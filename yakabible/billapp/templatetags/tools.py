from django import template
from billapp.models import *
from datetime import datetime
from django.templatetags.static import static
from django.contrib.auth.models import User
import pytz

utc = pytz.UTC
register = template.Library()


@register.filter
def get_ext(event):
    """
    Filter that returns the number of external visitors registered to the event
    """
    return event.ticket_set.count() - get_int(event)


@register.filter
def get_int(event):
    """
    Filter that returns the number of IONIS visitors registered to the event
    """
    return event.ticket_set.filter(user__email__iregex=r'.*epita.*').count()


@register.filter
def in_the_bound(e):
    """
    Filters that returns if the :model:`billapp.Event` is currently open to registration
    """
    begin = e.begin_register.replace(tzinfo=utc)
    end = e.end_register.replace(tzinfo=utc)
    now = datetime.now().replace(tzinfo=utc)
    return now >= begin and now < end


@register.filter
def get_photo(user):
    """
    Return the ID of the user in CRI DB if exists
    """
    try:
        user.social_auth.get(provider="epita")
        return "https://photos.cri.epita.fr/" + user.username
    except:
        return static('billapp/img/profile-placeholder.jpg')


@register.filter
def get_role(index):
    """
    Convert the index of role to string
    :param index: integer role of the user in the database
    :return: string role
    """
    switcher = {
        0: "Membre",
        1: "Membre du bureau",
        2: "Président"
    }
    return switcher.get(index)


@register.filter
def get_ticket_state(index):
    """
    Convert the index of the status of a ticket to string
    :param index: integer status of the event
    :return: string status
    """
    switcher = {
        0: "Expiré",
        1: "Pas utilisé",
        2: "Utilisé",
        3: "En pause"
    }
    return switcher.get(index)


@register.filter
def true_false_to_fr(b):
    """
    Convert boolean to french string
    :param b: boolean yes/false
    :return: string boolean in French
    """
    if b:
        return "Oui"
    return "Non"


@register.filter
@register.simple_tag
def get_president(assos):
    """
    Get the president of the association
    :param assos: Association object from DB
    :return: User president of the association
    """
    user = assos.associationuser_set.filter(role=2)
    if not user:
        return None
    return user[0].user


@register.simple_tag
def get_admin_email():
    """
    Get the email of the first administrator of the system.
    :return: email
    """
    user = User.objects.filter(groups__name="Admin")
    if not user:
        return "NO ADMIN"
    return user[0].email


@register.simple_tag(takes_context=True)
def event_started(context):
    """
    Indicates if the event is happening currently.
    :param context: context transmitted to the HTML calling the tag
    :return: boolean, true if the event is taking place
    """
    return context['object'].begin < datetime.now() < context['object'].end


@register.filter
def visible_events(e):
    """
    Filters events validated and not started yet
    :param e: List of all events
    :return: List of visible events
    """
    return e.filter(validation_state=4).filter(end__gte=datetime.now())


@register.filter
def user_is_manager_or_admin(user):
    """
    Indicates if the user if manager or admin.
    :param user: the prospected user
    :return: boolean, true if administration user
    """
    return User.objects.filter(groups__name="Admin", pk=user.pk) \
           or User.objects.filter(groups__name="Manager", pk=user.pk)


@register.simple_tag
def user_in_assos(user, assos):
    """
    Filters if the user is in the association or administration
    """
    return assos.associationuser_set.filter(user__pk=user.pk) or user_is_manager_or_admin(user)


@register.simple_tag
def get_http_url(url):
    """
    Convert a url(?) to a proper url
    :param url: url to inspect
    :return: url
    """
    if url.find('http:', 0, 6) != -1 or url.find('https:') != -1:
        return url
    return 'http://' + url


@register.simple_tag
def user_in_assos_super(user, assos):
    """
    Filters if the users is at least bureau's member of the association(or admin).
    """
    return assos.associationuser_set.filter(user__pk=user.pk, role__gt=0) or user_is_manager_or_admin(user)


@register.simple_tag
def asso_is_president(user, asso):
    """
    Indicates if the user if president of the association
    :param user: the user to inspect
    :param asso: the associated association
    :return: boolean, true if president
    """
    return asso.associationuser_set.filter(user__pk=user.pk, role=2)


@register.simple_tag
def can_delete(user, asso, dest_user):
    """
    Return True if user can delete dest_user in asso
    """
    if user_is_manager_or_admin(user):
        return True
    asso_user = asso.associationuser_set.get(user__pk=user.pk)
    if asso_user.role == 2:
        return True
    return asso_user.role > 0 and dest_user.role <= 0


@register.simple_tag
def unprepared(e, u):
    """
    Used in event.html to know if the user is authorized to see the unapproved event
    """
    if e.validation_state == 4:
        return False
    if u.is_anonymous:
        return True
    if u == e.manager or user_is_manager_or_admin(u):
        return False
    status = e.association.associationuser_set.filter(user=u).filter(association=e.association)
    if not status:
        return True
    if status[0].role == 1 or status[0].role == 2:
        return False
    return True


@register.simple_tag
def can_add_staff(e, u):
    """
    Used in event_staff_link.html to know if the user is authorized to link staff
    """
    if e.validation_state != 4:
        return True
    if u.is_anonymous:
        return True
    if u == e.manager or user_is_manager_or_admin(u):
        return False
    status = AssociationUser.objects.filter(user=u)
    if not status:
        return True
    tmp_assos = EventStaffCapacity.objects.filter(event=e).values('association')
    assos = [a['association'] for a in tmp_assos]
    for link in status:
        if link.association.pk not in assos:
            continue
        if link.role == 1 or link.role == 2:
            return False
    return True


@register.simple_tag
def can_rfa(e, u):
    """
    used in event.html to know if the user can ask for the approval of the event
    """
    if u == e.manager:
        return True
    status = e.association.associationuser_set.filter(user=u).filter(association=e.association)
    if not status:
        return False
    if status[0].role == 1 or status[0].role == 2:
        return True
    return False


@register.filter
def is_Rapproval_success(query):
    """
    used in event.html after a request to check if success
    """
    if query.get('Rapproval') == 'success':
        return True
    return False


@register.filter
def is_Rapproval_failure(query):
    """
    used in event.html after a request to check if failure
    """
    if query.get('Rapproval') == 'failure':
        return True
    return False


@register.filter
def is_Mailing_success(query):
    """
    used in event.html after a validation to check if mailing succeeded
    """
    if query.get('Mailing') == 'success':
        return True
    return False


@register.filter
def is_Validation_success(query):
    """
    used in event.html after a validation to check if success
    """
    if query.get('Validation') == 'success':
        return True
    return False


@register.filter
def is_Mailing_failure(query):
    """
    used in event.html after a validation to check if mailing failed
    """
    if query.get('Mailing') == 'failure':
        return True
    return False


@register.filter
def is_refusing_success(query):
    """
    used in event.html after a refusing to check if mailing succeeded
    """
    if query.get('deny') == 'success':
        return True
    return False


@register.filter
def is_refusing_failure(query):
    """
    used in event.html after a refusing to check if mailing failed
    """
    if query.get('deny') == 'failure':
        return True
    return False


@register.filter
def get_number_of_member(asso):
    return asso.associationuser_set.count()


@register.simple_tag
def events_to_approve(u, e):
    """
    used in approving_events_list.html to know if an unvalidated event is visible by the user
    """
    if u.is_anonymous:
        return False
    if user_is_manager_or_admin(u):
        return True
    status = e.association.associationuser_set.filter(user=u).filter(association=e.association)
    if not status:
        return False
    if status[0].role == 2:
        return True
    return False


@register.filter
def validation_step(event):
    """
    used in approving_events_list.html to return the current validation status
    """
    status = event.validation_state
    if status == 2:
        return 'ADM'
    if status == 3:
        return 'ASSOS'
    if status == 4:
        return 'AUTHORIZED'
    return 'AUCUNE APPROBATION'


@register.simple_tag
def has_taff(u):
    """
    used in base.html to know if the event ninspection is available
    """
    if not u.is_authenticated:
        return False
    events = Event.objects \
        .filter(begin__gte=datetime.now()) \
        .filter(validation_state__lte=3) \
        .filter(request_for_approval=True)

    if not events or events.count() == 0:
        return False

    if user_is_manager_or_admin(u):
        return True

    for ev in events:
        status = ev.association.associationuser_set.filter(user=u).filter(association=ev.association)
        if status:
            if status[0].role == 2:
                return True

    return False


@register.simple_tag
def has_to_validate(u):
    """
    used in base.html to know if the alert on validation is needed
    """
    events = Event.objects \
        .filter(begin__gte=datetime.now()) \
        .filter(validation_state__lte=3) \
        .filter(request_for_approval=True)
    is_adm = user_is_manager_or_admin(u)

    for ev in events:
        if is_adm and ev.validation_state != 3:
            return True
        status = ev.association.associationuser_set.filter(user=u).filter(association=ev.association)
        if status:
            if status[0].role == 2 and ev.validation_state != 2:
                return True

    return False


@register.simple_tag
def can_approve(u, ev):
    """
    used in event.html to know if user can validate or refuse an event
    """
    if not u.is_authenticated or not ev.request_for_approval:
        return False
    if user_is_manager_or_admin(u):
        return True
    status = ev.association.associationuser_set.filter(user=u).filter(association=ev.association)
    if status and status[0].role == 2:
        return True
    return False


@register.simple_tag
def can_validate(u, ev):
    """
    used in event.html to know if user has already validate an event
    """
    if user_is_manager_or_admin(u):
        if ev.validation_state != 3:
            return True
    else:
        if ev.validation_state != 2:
            return True
    return False


@register.simple_tag
def is_staff_in_event(user, event, asso):
    """
    Filters if the user is staff at the event
    """
    t = Ticket.objects.filter(user__pk=user.pk, category=True)
    if t == None or len(t) == 0:
        return -1
    if t[0].association != asso:
        return -2
    return t[0].pk


@register.simple_tag
def has_staff_place_in_event(event, asso):
    """
    Filters if the association has staff tickets to the event
    """
    esc = EventStaffCapacity.objects.get(event=event, association=asso)
    tickets = Ticket.objects.filter(event=event, association=asso)
    return len(tickets) < esc.capacity


@register.simple_tag
def user_event_staff_cap_where_ranked(u, e):
    """
    Gets a list of EventStaffCapacity for a user
    """
    escs = EventStaffCapacity.objects.filter(event=e)
    l = []
    for esc in escs:
        if user_in_assos_super(u, esc.association):
            l.append(esc)
    return l
