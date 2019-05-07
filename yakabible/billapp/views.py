from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.core.paginator import Paginator

from .forms import *
from .models import Event, Ticket
from .insertions import *
from .tools import *

class IndexView(generic.ListView):
    """
    View de la page d'accueil
    """
    template_name = "billapp/index.html"
    model=Event

    def get_queryset(self):
        return super().get_queryset().filter(premium=True) # TODO : Filter only future events
    

class CreateEvView(generic.FormView):
    """
    View pour créer un événement
    """
    template_name = "billapp/create_event.html"
    form_class = Event_Form
    success_url = "/?valid"

    def form_valid(self, form):
        insert_event(User.objects.get(username='Admin'), form)
        return super().form_valid(form)

class ConnectionView(generic.TemplateView):
    """
    View de la page de login
    """
    template_name = 'billapp/connection.html'

    def get(self, request):
        form = Connection_Form()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = Connection_Form(request.POST)
        if form.is_valid():
            user = authenticate(request,
                                username = form.cleaned_data['username'],
                                password = form.cleaned_data['password'])
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                if (request.GET.get('next')):
                    return HttpResponseRedirect(request.GET.get('next'))
                return HttpResponseRedirect('/?valid')
        return render(request, self.template_name, {'form': form,
                                                    'error': True})

class RegistrationView(generic.TemplateView):
    """
    View de la page d'inscription au site avec formulaire
    """
    template_name = 'billapp/registration.html'

    def get(self, request):
        form = Inscription_Form(request.GET)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = Inscription_Form(request.POST)
        if form.is_valid() and form.cleaned_data['pwd'] == form.cleaned_data['pwd_conf']:
            user = insert_user(form)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return HttpResponseRedirect('/?valid')
        return render(request, self.template_name, {'form': form, 'error': True})

class EventView(generic.DetailView):
    """
    View de la description d'un événement
    """
    template_name = 'billapp/event.html'
    model = Event

class AssociationView(generic.DetailView):
    """
    View de la description d'une association
    """
    model = Association
    template_name = 'billapp/association.html'

@login_required
def Profile_redir(request):
    return HttpResponseRedirect(reverse('profile', args=[request.user.pk]))

class ProfileView(generic.DetailView):
    """
    View d'une page utilisateur
    """
    model = User
    context_object_name = 'obj'
    template_name = 'billapp/profile.html'

def RegEventSuccessView(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    event = ticket.event
    association = event.association
    return make_pdf_response(ticket, association)

def LogOutView(request):
    logout(request)
    return HttpResponseRedirect('/?logout')

@login_required
def RegEventView(request, pk):
    # Need to check payement TODO
    # Maybe confirmation mail before payement
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

class AssociationListView(generic.ListView):
    """
    View de la liste des associaitons
    """
    template_name = "billapp/association_list.html"
    model = Association

    def get_queryset(self):
        set = super().get_queryset();
        paginator = Paginator(set, 10)
        page = self.request.GET.get("page")
        return paginator.get_page(page)

class EventsListView(generic.ListView):
    """
    View de la liste des événements
    """
    template_name = "billapp/events_list.html"
    model = Event
    def get_queryset(self):
        return super().get_queryset().filter(end__gte=datetime.now()).order_by('begin')
