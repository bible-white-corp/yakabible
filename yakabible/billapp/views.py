from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.core.paginator import Paginator
from django.db import IntegrityError
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
        return super().get_queryset().filter(premium=True)\
            .filter(validation_state=4)\
            .filter(end__gte=datetime.now())
    

class CreateEvView(generic.View):
    """
    View pour créer un événement
    """
    template_name = "billapp/create_event.html"
    success_url = "/?valid"

    def get(self, request, pk):
        asso = get_object_or_404(Association, pk=pk)
        event_form = Event_Form()
        staff_form = Staff_Form_Set()
        return render(request, self.template_name, {'asso': asso,
                                                    'event_form': event_form,
                                                    'staff_form': staff_form})

    def post(self, request, pk):
        asso = get_object_or_404(Association, pk=pk)
        event_form = Event_Form(request.POST, request.FILES)

        staff_form = Staff_Form_Set(request.POST)
        if 'additems' in request.POST and  request.POST["additems"] == 'true':
            formset_dictionary_copy = request.POST.copy()
            formset_dictionary_copy['form-TOTAL_FORMS'] = int(formset_dictionary_copy['form-TOTAL_FORMS']) + 1
            staff_form = Staff_Form_Set(formset_dictionary_copy)
        elif event_form.is_valid() and staff_form.is_valid():
            asso = Association.objects.get(pk=pk)
            e = insert_event(request.user, event_form, asso)
            insert_staff_capacity(staff_form, e)
            return HttpResponseRedirect('/?valid')
        return render(request, self.template_name, {'asso': asso,
                                                    'event_form': event_form,
                                                    'staff_form': staff_form})

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
            try:
                user = insert_user(form)
            except IntegrityError:
                return render(request, self.template_name, {'form': form, 'errorAlreadyUsed': True})

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

class DashboardAssociationView(generic.DetailView):
    """
    View du dashboard d'association
    """
    model = Association
    template_name = 'billapp/dashboard_association.html'

class DashboardRespoView(generic.TemplateView):
    """
    View du dashboard du responsable des associations
    """
    template_name = 'billapp/dashboard_respo.html'

    def get(self, request):
        asso_form = Asso_Form()
        all_events = Event.objects.all()
        all_assos = Association.objects.all()
        return render(request, self.template_name, {'Form': asso_form,
                                                    'Events': all_events,
                                                    'Assos': all_assos,
                                                    'f_active': "active",
                                                    'show_f_active': "show active"})

    def post(self, request):
        asso_form = Asso_Form(request.POST, request.FILES)
        all_events = Event.objects.all()
        all_assos = Association.objects.all()
        if 'delete_asso' in request.POST:
            pass
        if (asso_form.is_valid()):
            insert_association(asso_form)
            return self.get(request)
        return render(request, self.template_name, {'Form': asso_form,
                                                    'Events': all_events,
                                                    'Assos': all_assos,
                                                    't_active': "active",
                                                    'show_t_active': "show active"})

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

@login_required
def TicketDownload(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if ticket.user != request.user:
        return HttpResponseNotFound("Ticket not found")
    return make_pdf_response(ticket)

@login_required
def RegEventSuccessView(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    pdf = make_pdf(ticket)
    send_pdf_mail(ticket, pdf)
    return make_pdf_response(ticket, pdf)

def LogOutView(request):
    logout(request)
    return HttpResponseRedirect('/?logout')

###
#   Try to send email to resp and president + set boolean request at true if success
###
@login_required
def ask_approval(request, pk):
    e = get_object_or_404(Event, pk=pk)
    adm = User.objects.filter(groups__name="Manager")
    if not adm:
        adm = User.objects.filter(groups__name="Admin")
    if not adm:
        return HttpResponseRedirect('/?failure')
    res = send_approval_mail(e, adm[0])
    if res:
        e.request_for_approuval = True
        e.save()
        return redirect(request.path_info.split('/ask_for_approval')[0] + '?Rapproval=success')
    else:
        return redirect(request.path_info.split('/ask_for_approval')[0] + '?Rapproval=failure')

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

def DeleteAssociation(request, pk):
    """
    View to delete an association
    You should acces it from respo dashboard
    """
    association = Association.objects.get(pk=pk)
    association.delete()
    return HttpResponseRedirect(reverse('dashboard_respo'))

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
        return super().get_queryset()\
            .filter(end__gte=datetime.now())\
            .order_by('begin')\
            .filter(validation_state=4)

class ApprovingListView(generic.ListView):
    """
    View de la liste des événements en attente d'approbation
    """
    template_name = "billapp/approving_events_list.html"
    model = Event
    def get_queryset(self):
        return super().get_queryset()\
            .filter(end__gte=datetime.now())\
            .order_by('begin')\
            .filter(validation_state__lte=4)\
            .filter(request_for_approuval=True)

class EventRealtime(generic.DetailView):
    template_name = "billapp/event_realtime.html"
    model = Event
