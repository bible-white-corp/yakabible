from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse, HttpResponseNotFound, \
    HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import authenticate, login, logout
from braces.views import GroupRequiredMixin
from datetime import datetime
from django.contrib import messages
from django.contrib.messages import get_messages
from django.core.paginator import Paginator
from django.db import IntegrityError
from .forms import *
from .models import Event, Ticket
from .insertions import *
from .tools import *
from .decorators import *
from django.contrib.auth.models import Group

from decimal import Decimal
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm


class IndexView(generic.ListView):
    """
    View for the index page.
    """
    template_name = "billapp/index.html"
    model = Event

    def get_queryset(self):
        return super().get_queryset().filter(premium=True) \
            .filter(validation_state=4) \
            .filter(end__gte=datetime.now())


class CreateEvView(generic.View):
    """
    View of the creation page of events.
    """
    template_name = "billapp/create_event.html"
    success_url = "/?valid"

    def get(self, request, pk):
        asso = get_object_or_404(Association, pk=pk)
        if (not user_in_assos(request.user, asso)):
            return HttpResponseRedirect('connection')
        event_form = Event_Form()
        staff_form = Staff_Form_Set()
        return render(request, self.template_name, {'asso': asso,
                                                    'event_form': event_form,
                                                    'staff_form': staff_form})

    def post(self, request, pk):
        asso = get_object_or_404(Association, pk=pk)

        event_form = Event_Form(request.POST, request.FILES)
        if (not user_in_assos(request.user, asso)):
            return HttpResponseRedirect('connection')

        staff_form = Staff_Form_Set(request.POST)
        if 'additems' in request.POST and request.POST["additems"] == 'true':
            formset_dictionary_copy = request.POST.copy()
            formset_dictionary_copy['form-TOTAL_FORMS'] = int(formset_dictionary_copy['form-TOTAL_FORMS']) + 1
            staff_form = Staff_Form_Set(formset_dictionary_copy)
        elif event_form.is_valid() and staff_form.is_valid():
            asso = Association.objects.get(pk=pk)
            e = insert_event(request.user, event_form, asso)
            if (insert_staff_capacity(staff_form, e)):
                return HttpResponseRedirect('/?valid')
            e.delete()
        return render(request, self.template_name, {'asso': asso,
                                                    'event_form': event_form,
                                                    'staff_form': staff_form})


class EventEdit(generic.View):
    """
    View of the modification of an event.
    """
    template_name = "billapp/create_event.html"

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if request.user != event.manager:
            return HttpResponseForbidden()
        event_form = get_form_from_event(event)
        staff_form = get_staff_form_from_event(event)
        return render(request, self.template_name, {'event': event,
                                                    "modif": True,
                                                    "event_form": event_form,
                                                    'staff_form': staff_form})

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if request.user != event.manager:
            return HttpResponseForbidden()
        event_form = Event_Form(request.POST, request.FILES)
        staff_form = Staff_Form_Set(request.POST)

        if 'additems' in request.POST and request.POST["additems"] == 'true':
            formset_dictionary_copy = request.POST.copy()
            formset_dictionary_copy['form-TOTAL_FORMS'] = int(formset_dictionary_copy['form-TOTAL_FORMS']) + 1
            staff_form = Staff_Form_Set(formset_dictionary_copy)
        elif event_form.is_valid() and staff_form.is_valid():
            if update_event(request, event_form, staff_form, event):
                return HttpResponseRedirect(reverse('event', args=[pk]))
        return render(request, self.template_name, {'modif': True,
                                                    'event': event,
                                                    'event_form': event_form,
                                                    'staff_form': staff_form})


class ConnectionView(generic.TemplateView):
    """
    View of the login page.
    """
    template_name = 'billapp/connection.html'

    def get(self, request):
        form = Connection_Form()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = Connection_Form(request.POST)
        if form.is_valid():
            user = authenticate(request,
                                username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                if user.groups.filter(name="Locked").exists():
                    return render(request, self.template_name, {'form': form,
                                                                'error2': True})
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                if request.GET.get('next'):
                    return HttpResponseRedirect(request.GET.get('next'))
                return HttpResponseRedirect('/?valid')
        return render(request, self.template_name, {'form': form,
                                                    'error': True})


class AfterReg(generic.DetailView):
    """
    View of the modification of an event.
    """
    model = User
    template_name = "billapp/after_reg.html"


class RegistrationView(UserPassesTestMixin, generic.TemplateView):
    """
    View of the registration page for new users.
    """
    template_name = 'billapp/registration.html'

    def test_func(self):
        return self.request.user.is_anonymous

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

            group_locked = Group.objects.get(name='Locked')
            group_locked.user_set.add(user)
            #  login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            link = request.build_absolute_uri().split('/registration')[0]
            link += reverse('unlock_user', args=[user.pk])
            send_registration(user.first_name + ' ' + user.last_name, user.email, link)
            return HttpResponseRedirect(reverse('after_reg', args=[user.pk]))

        return render(request, self.template_name, {'form': form, 'error': True})


class EventView(generic.DetailView):
    """
    View of an event.
    """
    template_name = 'billapp/event.html'
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_refus'] = Refusing_Form()
        return context


class EventStaffView(generic.DetailView):
    """
    Sub-view of events to manage staff.
    """
    template_name = 'billapp/event_staff_link.html'
    model = Event

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_refus'] = Refusing_Form()
        return context


class AssociationView(generic.DetailView):
    """
    View of the association page.
    """
    model = Association
    template_name = 'billapp/association.html'


class DashboardAssociationView(UserPassesTestMixin, generic.DetailView):
    """
    View of the dashboard of the association.
    """
    model = Association
    template_name = 'billapp/dashboard_association.html'

    def test_func(self):
        return user_in_assos(self.request.user, Association.objects.get(pk=self.kwargs['pk']))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_adduser'] = AddUserAssosFrom()
        context['users'] = User.objects.all()
        context['form_website'] = WebsiteUpdateForm(
            initial={"input": Association.objects.get(pk=self.kwargs['pk']).url})
        return context


@in_asso_super_required
def AddUserAssosView(request, pk):
    """
    Sub-view of the dashboard association to add users to the association.
    """
    assos = get_object_or_404(Association, pk=pk)
    adduser = AddUserAssosFrom(request.POST)
    if not adduser.is_valid():
        return HttpResponseNotFound("Invalid request")
    user = get_object_or_404(User, username=adduser.cleaned_data['input'])
    insert_user_assos(assos, user)
    return HttpResponseRedirect(reverse('dashboard_association', args=[pk]) + "#listuser")


def AddStaffEventView(request, pk, user_pk, asso_pk):
    """
    Sub-view of events to add staff to the event.
    """
    event = get_object_or_404(Event, pk=pk)
    user = get_object_or_404(User, pk=user_pk)
    asso = get_object_or_404(Association, pk=asso_pk)
    esc = EventStaffCapacity.objects.get(event=event, association=asso)
    tickets = Ticket.objects.filter(event=event, association=asso)
    if len(tickets) < esc.capacity:
        insert_staff(user, event, asso)
    return HttpResponseRedirect(reverse('event_staff', args=[pk]) + "#" + asso.name)


def DelStaffEventView(request, pk):
    """
    Sub-view of events to remove staff from the event.
    """
    ticket = get_object_or_404(Ticket, pk=pk)
    asso = ticket.association
    event = ticket.event
    ticket.delete()
    return HttpResponseRedirect(reverse('event_staff', args=[event.pk]) + "#" + asso.name)


@in_asso_super_required
def UpdateUserAssosView(request, pk):
    """
    Sub-view of the association dashboard to manage users in the association.
    """
    assos = get_object_or_404(Association, pk=pk)
    user_assos = get_object_or_404(AssociationUser, pk=request.GET.get('user'))
    new_role = request.GET.get('new_role')
    if not user_is_manager_or_admin(request.user):
        if assos.pk is not user_assos.association.pk \
                or (can_delete(request.user, assos, user_assos) is False and new_role == "delete") \
                or (new_role != "2" and asso_is_president(request.user, assos)):
            raise Http404("Invalid request")
    if new_role == "delete":
        user_assos.delete()
    else:
        user_assos.role = int(new_role)
        user_assos.save()
    return HttpResponseRedirect(reverse('dashboard_association', args=[pk]) + "#listuser")


class DashboardRespoView(GroupRequiredMixin, generic.TemplateView):
    """
    View of the admin manager dashboard.
    """
    group_required = [u'Manager', u'Admin']
    template_name = 'billapp/dashboard_respo.html'

    def get(self, request):
        storage = get_messages(request)
        asso_form = Asso_Form()
        all_events = Event.objects.all()
        all_assos = Association.objects.all()
        for m in storage:
            if 'deleted' == str(m):
                return HttpResponseRedirect(reverse('dashboard_respo') + "#listassos")
        return render(request, self.template_name, {'Form': asso_form,
                                                    'Events': all_events,
                                                    'Assos': all_assos})

    def post(self, request):
        asso_form = Asso_Form(request.POST, request.FILES)
        all_events = Event.objects.all()
        all_assos = Association.objects.all()
        if 'delete_asso' in request.POST:
            pass
        if (asso_form.is_valid()):
            try:
                insert_association(asso_form)
            except:
                return HttpResponseRedirect(reverse('dashboard_respo') + "#createasso?uniqueViolated")
            return self.get(request)
        return HttpResponseRedirect(reverse('dashboard_respo') + "#createasso")


@login_required
def Profile_redir(request):
    return HttpResponseRedirect(reverse('profile', args=[request.user.pk]))


class ProfileView(generic.DetailView):
    """
    View of the user profile.
    """
    model = User
    context_object_name = 'obj'
    template_name = 'billapp/profile.html'


@login_required
def TicketDownload(request, pk):
    """
    Return the ticket of the user
    """
    ticket = get_object_or_404(Ticket, pk=pk)
    if ticket.user != request.user:
        return HttpResponseNotFound("Ticket not found")
    return make_pdf_response(ticket)


@login_required
def RegEventSuccessView(request, pk):
    """
    Generate the ticket et send the mails after the user registered to an event
    """
    ticket = get_object_or_404(Ticket, pk=pk)
    pdf = make_pdf(ticket)
    send_pdf_mail(ticket, pdf)
    return make_pdf_response(ticket, pdf)


def LogOutView(request):
    logout(request)
    return HttpResponseRedirect('/?logout')


@login_required
def ask_approval(request, pk):
    """
    Try to send email to resp and president + set boolean request at true if success
    """
    e = get_object_or_404(Event, pk=pk)
    adm = User.objects.filter(groups__name="Manager")

    if not adm:
        adm = User.objects.filter(groups__name="Admin")
    if not adm:
        return HttpResponseRedirect('/?failure')

    path = request.build_absolute_uri().split('/ask_for_approval')[0]
    res = send_approval_mail(e, adm[0], path)
    if res:
        e.request_for_approval = True
        e.save()
        return redirect(path + '?Rapproval=success')
    else:
        return redirect(path + '?Rapproval=failure')


@login_required
def RegEventView(request, pk):
    """
    View to register to an event
    Handles when the user is already register0
    """
    e = get_object_or_404(Event, pk=pk)
    try:
        tmp_t = Ticket.objects.get(user=request.user, event=e)
    except Ticket.DoesNotExist:
        tmp_t = None
    if tmp_t is None:

        price = e.price
        ionis_query = request.GET.get('ionis', '')
        if ionis_query != '':
            ionis_query = "?ionis=true"
            price = e.price_ionis

        if price > 0.00:
            return redirect(reverse('paymentProcess', args=[pk]) + ionis_query)  # payment

        t = insert_ticket(request.user, e, ionis_query != '')
    else:
        t = get_object_or_404(Ticket, user=request.user, event=e)
    return HttpResponseRedirect(reverse('reg_event_success', args=[t.pk]))


@group_required('Manager', 'Admin')
def DeleteAssociation(request, pk):
    """
    View to delete an association
    You should access it from respo dashboard.
    """
    association = Association.objects.get(pk=pk)
    association.delete()
    messages.success(request, 'deleted')
    return HttpResponseRedirect(reverse('dashboard_respo'))


class AssociationListView(generic.ListView):
    """
    View of the list of associations.
    """
    template_name = "billapp/association_list.html"
    model = Association

    def get_queryset(self):
        qset = super().get_queryset()
        paginator = Paginator(qset, 10)
        page = self.request.GET.get("page")
        return paginator.get_page(page)


class EventsListView(generic.ListView):
    """
    View of the list of scheduled events.
    """
    template_name = "billapp/events_list.html"
    model = Event

    def get_queryset(self):
        res = super().get_queryset() \
            .filter(end__gte=datetime.now()) \
            .order_by('begin') \
            .filter(validation_state=4)
        paginator = Paginator(res, 10)
        page = self.request.GET.get("page")
        return paginator.get_page(page)


class ApprovingListView(generic.ListView):
    """
    View of the list of events needing approval.
    """
    template_name = "billapp/approving_events_list.html"
    model = Event

    def get_queryset(self):
        return super().get_queryset() \
            .filter(begin__gte=datetime.now()) \
            .order_by('begin') \
            .filter(validation_state__lte=3) \
            .filter(request_for_approval=True)


class EventRealtime(generic.DetailView):
    template_name = "billapp/event_realtime.html"
    model = Event


@csrf_exempt
def payment_done(request):
    """
    Redirection view when paypal succeeded.
    """
    return render(request, 'payment/done.html')


@csrf_exempt
def payment_canceled(request):
    """
    Redirection view when paypal failed.
    """
    return render(request, 'payment/canceled.html')


def payment_process(request, pk):
    """
    View for the generation of the "Buy Now" paypal button.
    Also provides all of the data required by paypal.
    """

    e = get_object_or_404(Event, pk=pk)
    price = e.price
    category = 'extern'

    ionis = request.GET.get('ionis', '')

    if ionis != '':
        ionis = '?ionis=true'
        category = 'ionis'
        price = e.price_ionis

    user = request.user.first_name + " " + request.user.last_name
    user_id = str(request.user.id)
    eventname = e.title
    eventpk = e.pk

    paypal_dict = {
        "business": "yakabible@gmail.com",
        "amount": str(price),
        "item_name": user + " : " + eventname,
        "invoice": user_id + "/" + str(eventpk) + "/" + category,
        "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
        "return": request.build_absolute_uri(reverse('paymentDone')),
        "cancel_return": request.build_absolute_uri(reverse('paymentCanceled')),
        "currency_code": "EUR",
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, "payment/process.html", {'form': form})


@login_required
def ask_validation(request, pk):
    """
    Procedure for the validation of an event. Checks if the user has the rights.
    Updates the event to the corresponding state.
    If both association and admin validated the event, upgrades it and send mails.
    """
    e = get_object_or_404(Event, pk=pk)
    status = e.association.associationuser_set.filter(user=request.user).filter(association=e.association)
    is_prez = status and status[0].role == 2
    is_adm = user_is_manager_or_admin(request.user)

    if not is_prez and not is_adm:
        return HttpResponseRedirect('/?unauthorized')
    if is_adm and e.validation_state == 3:
        return HttpResponseRedirect('/?authorizationAlreadyGiven')
    if is_prez and e.validation_state == 2:
        return HttpResponseRedirect('/?authorizationAlreadyGiven')

    if e.validation_state == 4:
        return HttpResponseRedirect('/?eventAlreadyValidated')

    adm = User.objects.filter(groups__name="Manager")
    if not adm:
        adm = User.objects.filter(groups__name="Admin")

    if e.validation_state == 1:
        if status:
            e.validation_state = 2
        else:
            e.validation_state = 3
    else:
        e.validation_state = 4
    e.save()

    path = request.build_absolute_uri().split('/validating')[0]

    if e.validation_state == 4:
        if not send_validation_mail(e, adm, path):
            return redirect(path + '?Mailing=failure')
        return redirect(path + '?Mailing=success')

    return redirect(path + '?Validation=success')


@login_required
def ask_refusing(request, pk):
    """
    Procedure to refuse the event. Checks if the circumstances allow the refusal.
    Changes the status of the event and sends the mails.
    """
    e = get_object_or_404(Event, pk=pk)

    if request.method != "POST":
        return HttpResponseRedirect('/?illegalmethod')

    if e.validation_state == 4:
        return HttpResponseRedirect('/?eventAlreadyValidated')
    status = e.association.associationuser_set.filter(user=request.user).filter(association=e.association)
    if not (status and status[0].role == 2) and not user_is_manager_or_admin(request.user):
        return HttpResponseRedirect('/?unauthorized')

    adm = User.objects.filter(groups__name="Manager")
    if not adm:
        adm = User.objects.filter(groups__name="Admin")

    refus_form = Refusing_Form(request.POST)
    if not refus_form.is_valid():
        return redirect('/?form_error')

    description = refus_form.cleaned_data['description']

    e.validation_state = 1
    e.request_for_approval = False
    e.save()
    path = request.build_absolute_uri().split('/refusing')[0]

    if not send_refusing_mail(e, adm, status.count() != 0, description, path):
        return redirect(path + '?deny=failure')
    return redirect(path + '?deny=success')


def NotifyOff(request):
    """
    Disables notification indicating that the user should inspect events for the whole session.
    """
    request.session["noNotify1"] = True
    return HttpResponse('ok')


def switch_premium(request, pk):
    if not user_is_manager_or_admin(request.user):
        return HttpResponseForbidden
    e = get_object_or_404(Event, pk=pk)
    e.premium = not e.premium
    e.save()
    return HttpResponseRedirect(reverse('event', args=[pk]))


def update_website(request, pk):
    a = get_object_or_404(Association, pk=pk)
    if "input" in request.POST:
        a.url = request.POST["input"]
        a.save()
    return HttpResponseRedirect(reverse('dashboard_association', args=[pk]) + "#listuser")


def unlock_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    group_locked = Group.objects.get(name='Locked')
    group_locked.user_set.remove(user)
    return HttpResponseRedirect(reverse("connection"))


def search_view(request):
    if "q" not in request.GET:
        return HttpResponseRedirect(reverse("index"))
    query = request.GET.get("q")
    print(query)
    q_events = Event.objects.all().filter(title__icontains=query)
    q_assos = Association.objects.all().filter(name__icontains=query)
    q_users = User.objects.all().filter(
       Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(username__icontains=query))
    return render(request, "billapp/search.html", {"q_assos": q_assos,
                                                   "q_events": q_events,
                                                   "q_users": q_users})
