from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from datetime import datetime

from .forms import *
from .models import Event, Ticket
from .insertions import insert_event, insert_user

class IndexView(generic.TemplateView):
    template_name = "billapp/index.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)

class CreateEvView(generic.FormView):
    template_name = "billapp/create_event.html"
    form_class = Event_Form
    success_url = "/?valid"

    def form_valid(self, form):
        insert_event(User.objects.get(username='Admin'), form)
        return super().form_valid(form)

class ConnectionView(generic.TemplateView):
    template_name = 'billapp/connection.html'

    def get(self, request):
        form = Connection_Form()
        return render(request, self.template_name, {'form': form,
                                                    'error': False})

    def post(self, request):
        form = Connection_Form(request.POST)
        if form.is_valid():
            user = authenticate(request,
                                username = form.cleaned_data['username'],
                                password = form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/?valid')
            else:
                return render(request, self.template_name, {'form': form,
                                                            'error': True})
        return render(request, self.template_name, {'form': form,
                                                    'error': True})

class InscriptionView(generic.TemplateView):
    template_name = 'billapp/inscription.html'

    def get(self, request):
        form = Inscription_Form(request.GET)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = Inscription_Form(request.POST)
        if form.is_valid():
            if form.cleaned_data['pwd'] != form.cleaned_data['pwd_conf']:
                return render(request, self.template_name, {'form': form,
                                                            'error': True})
            user = insert_user(form)
            login(request, user)
            return HttpResponseRedirect('/?valid')
        return render(request, self.template_name, {'form': form, 'error': True})

class EventView(generic.DetailView):
    template_name = 'billapp/event.html'
    model = Event

def LogOutView(request):
    logout(request)
    return HttpResponseRedirect('/?logout')

def RegEventView(request, pk):
    return HttpResponseRedirect('/?TODO')

def EventsJSON(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    # Fetch events from BDD
    json = []
    events = Event.objects.all()
    if start and end:
        events = events.filter(end__gte=start, begin__lte=end)
    else:
        events = events.filter(end__gte=datetime.now())
    for obj in events:
        json.append({
            'id': obj.pk,
            'title': obj.title,
            'start': obj.begin,
            'end': obj.end,
            'url': reverse('event', args=[obj.pk]), # url of event/obj.pk
        })
    res = JsonResponse(json, safe=False)
    res["Access-Control-Allow-Origin"] = "*"
    return res

def TicketsJSON(request):
    event_id = request.GET.get('event')
    # Fetch tickets from BDD
    json = []
    tickets = Ticket.objects.all()
    if event_id:
        tickets = tickets.filter(event_id=event_id)
    else:
        tickets = tickets.filter(event__end__gte=datetime.now())
    for obj in tickets:
        json.append({
            'id': obj.pk,
            'event': obj.event.pk,
            'username': obj.user.username,
            'firstname': obj.user.first_name,
            'lastname': obj.user.last_name,
            'email': obj.user.email,
            'category': obj.category,
        })
    res = JsonResponse(json, safe=False)
    res["Access-Control-Allow-Origin"] = "*"
    return res