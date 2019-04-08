from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .forms import *
from .models import Event
from .insertions import insert_event

class IndexView(generic.TemplateView):
    template_name = "billapp/index.html"

    def get(self, request):
        base = 'base_disconnected.html'
        if request.user.is_authenticated:
            base = 'base_connected.html'
        return render(request, self.template_name, {'base': base})

    def post(self, request):
        base = 'base_disconnected.html'
        if request.user.is_authenticated:
            base = 'base_connected.html'
        return render(request, self.template_name, {'base': base})

class CreateEvView(generic.TemplateView):
    template_name = "billapp/create_event.html"

    def get(self, request):
        form = Event_Form(request)
        base = 'base_disconnected.html'
        if request.user.is_authenticated:
            base = 'base_connected.html'
        return render(request, self.template_name, {'form': form,
                                                    'base': base})

    def post(self, request):
        form = Event_Form(request.POST)
        base = 'base_disconnected.html'
        if request.user.is_authenticated:
            base = 'base_connected.html'
        if form.is_valid():
            insert_event(User.objects.get(username='Admin'), form)
            return HttpResponseRedirect('/?valid')
        return render(request, self.template_name, {'form': form,
                                                    'base': base})

class ConnectionView(generic.TemplateView):
    template_name = 'billapp/connection.html'

    def get(self, request):
        form = Connection_Form(request.GET)
        base = 'base_disconnected.html'
        if request.user.is_authenticated:
            base = 'base_connected.html'
        return render(request, self.template_name, {'form': form,
                                                    'error': False,
                                                    'base': base})

    def post(self, request):
        form = Connection_Form(request.POST)
        base = 'base_disconnected.html'
        if request.user.is_authenticated:
            base = 'base_connected.html'
        if form.is_valid():
            print(request.user)
            user = authenticate(request,
                                username = form.cleaned_data['username'],
                                password = form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/?valid')
            else:
                return render(request, self.template_name, {'form': form,
                                                            'error': True,
                                                            'base': base})
            print(request.user)
        return render(request, self.template_name, {'form': form,
                                                    'error': False,
                                                    'base': base})

def LogOutView(request):
    logout(request)
    return HttpResponseRedirect('/?logout')

def EventsJSON(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    # Fetch events from BDD
    json = []
    events = Event.objects.all().filter(end__gte=start, begin__lte=end)
    for obj in events:
        json.append({
            'id': obj.pk,
            'title': obj.title,
            'start': obj.begin,
            'end': obj.end,
            'url': '/', # url of event/obj.pk
        })

    return JsonResponse(json, safe=False)
