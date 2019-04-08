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
            print(request.user)
            user = authenticate(request,
                                username = form.cleaned_data['username'],
                                password = form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/?valid')
            else:
                return render(request, self.template_name, {'form': form,
                                                            'error': True})
            print(request.user)
        return render(request, self.template_name, {'form': form,
                                                    'error': False})

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
