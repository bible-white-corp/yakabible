from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from datetime import datetime

from .forms import *
from .models import Event, Ticket
from .insertions import *

from reportlab.pdfgen import canvas

import qrcode
import io

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

class RegistrationView(generic.TemplateView):
    template_name = 'billapp/registration.html'

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

def RegEventSuccessView(request, pk):
    t = get_object_or_404(Ticket, pk=pk)
    e = t.event
    user = request.user
    full_name = user.first_name + ' ' + user.last_name

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}_{}.pdf"'.format(request.user, e.title.replace(' ', '_'))

    #QRCODE -> SHA1 ?
    q = qrcode.QRCode()
    q.add_data(user.username + '\n')
    q.add_data(str(e.pk) + '\n')
    q.add_data(str(pk) + '\n')
    q.add_data(user.email + '\n')
    img = q.make_image()

    p = canvas.Canvas(response)
    p.drawString(100, 700, 'Nom d\'utilisateur: ' + user.username)
    p.drawString(100, 680, 'Nom: ' + full_name)
    p.drawString(100, 660, 'Nom de l\'événement: ' + e.title)
    p.drawString(100, 640, 'ID: ' + str(pk))
    p.drawInlineImage(img, 100, 160)
    p.showPage()
    p.save()
    return response

def LogOutView(request):
    logout(request)
    return HttpResponseRedirect('/?logout')

def RegEventView(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/connection')
    # Need to check payement TODO
    e = get_object_or_404(Event, pk=pk)
    try:
        tmp_t = Ticket.objects.get(user=request.user,event=e)
    except Ticket.DoesNotExist:
        tmp_t = None
    if tmp_t is None:
        t = insert_ticket(request, e)
    else:
        t = get_object_or_404(Ticket, user=request.user, event=e)
    return HttpResponseRedirect(reverse('reg_event_success', args=[t.pk]))

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
