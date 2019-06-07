from .models import *
from .tools import send_modification_mail
from .tools import send_modification_notification_mail
from .forms import Event_Form, Staff_Form, Staff_Form_Set
from threading import Thread

def insert_event(user, form, asso):
    e = Event(
            title = form.cleaned_data['title'],
            description = form.cleaned_data['description'],
            association = asso,
            manager = user,
            premium = False,
            begin = form.cleaned_data['begin'],
            end = form.cleaned_data['end'],
            begin_register = form.cleaned_data['begin_register'],
            end_register = form.cleaned_data['end_register'],
            place = form.cleaned_data['place'],
            price_ionis = form.cleaned_data['price_ionis'],
            price = form.cleaned_data['price'],
            ext_capacity = form.cleaned_data['ext_capacity'],
            int_capacity = form.cleaned_data['int_capacity'],
            staff_capacity = 0,
            promotion_image_path = form.cleaned_data['promotion_image_path'],
            validation_state = 1,
            request_for_approval=False,
            show_capacity = form.cleaned_data['show_capacity']
            )
    e.save()
    return e

def insert_user(form):
    u = User.objects.create_user(
            username = form.cleaned_data['username'],
            password = form.cleaned_data['pwd'],
            email = form.cleaned_data['email'],
            first_name = form.cleaned_data['firstname'],
            last_name = form.cleaned_data['lastname']
            )
    u.save()
    return u

def insert_association(form):
    a = Association(
            name = form.cleaned_data['name'],
            logo_path = form.cleaned_data['logo_path'],
            email = form.cleaned_data['email'],
            description = form.cleaned_data['description']
        )
    a.save()

def insert_ticket(user, e, ionis=False):
    t = Ticket(
                user = user,
                event = e,
                category = False,
                ionis = ionis,
                state = 0
                )
    t.save()
    return t

def insert_staff(user, e, asso):
    t = Ticket (
                user = user,
                event = e,
                association = asso,
                category = True,
                ionis = False,
                state = 0
                )
    t.save()
    return t

def update_ticket(ticket, new_state):
    ticket.state = new_state
    ticket.save()
    return ticket

def update_event(request, form, staff_form, event):
    EventStaffCapacity.objects.filter(event=event).delete()
    if not insert_staff_capacity(staff_form, event):
        return False
    notify_president = False
    notify_adm = False

    if event.price != form.cleaned_data['price'] or event.price_ionis != form.cleaned_data['price_ionis']:
        notify_president = True
    if event.title != form.cleaned_data['title']\
            or event.begin != form.cleaned_data['begin']\
            or event.end != form.cleaned_data['end']\
            or event.begin_register != form.cleaned_data['price_ionis']\
            or event.end_register != form.cleaned_data['end_register']\
            or event.place != form.cleaned_data['place']\
            or event.int_capacity != form.cleaned_data['int_capacity']\
            or event.ext_capacity != form.cleaned_data['ext_capacity']:
        notify_president = True
        notify_adm = True

    Event.objects.filter(pk=event.pk).update(
            title = form.cleaned_data['title'],
            description = form.cleaned_data['description'],
            association = event.association,
            manager = event.manager,
            premium = event.premium,
            begin = form.cleaned_data['begin'],
            end = form.cleaned_data['end'],
            begin_register = form.cleaned_data['begin_register'],
            end_register = form.cleaned_data['end_register'],
            place = form.cleaned_data['place'],
            price_ionis = form.cleaned_data['price_ionis'],
            price = form.cleaned_data['price'],
            ext_capacity = form.cleaned_data['ext_capacity'],
            int_capacity = form.cleaned_data['int_capacity'],
            staff_capacity = 0, # Unused
            promotion_image_path = form.cleaned_data['promotion_image_path'],
            validation_state = event.validation_state,
            request_for_approval=event.request_for_approval,
            show_capacity = form.cleaned_data['show_capacity']
            )


    # Notify all sub users
    # users = event.ticket_set.user
    users = Ticket.objects\
        .filter(event=event)\
        .values('user')

    if (users):
        link = request.build_absolute_uri().split('/edit')[0]
        u_thread = NotifyVisitors(users, event, link)
        u_thread.start()

    # Notify ADM & president
    if notify_adm or notify_president:
        president = None
        adm = None
        if notify_president:
            president = AssociationUser.objects\
                .filter(role=2)\
                .filter(association=event.association)[0]\
                .user.email
            print(president)
            if event.validation_state == 4:
                event.validation_state = 3
            else:
                event.validation_state = 1
        if notify_adm:
            adm = User.objects.filter(groups__name="Manager")
            if not adm:
                adm = User.objects.filter(groups_name="Admin")
            adm = adm[0].email
            event.validation_state = 1
        event.save()
        link = request.build_absolute_uri().split('/edit')[0]
        return send_modification_mail(event, president, adm, link)

    return True


def insert_staff_capacity(formset, event):
    asso_list = []
    for form in formset:
        try:
            asso = form.cleaned_data['association_name']
            cap = form.cleaned_data['capacity']
            if (asso in asso_list):
                form.add_error('association_name', 'Une association ne peut apparaître qu\'une seule fois')
                return False
            asso_list.append(asso)
            if asso == None or cap <= 0:
                continue
            ev_staff_cap = EventStaffCapacity(
                    event = event,
                    association = asso,
                    capacity = cap
                    )
            ev_staff_cap.save()
        except:
            pass
    return True


def insert_user_assos(assos, user):
    new = AssociationUser(user=user, association=assos, role=0)
    new.save()
    return new

class NotifyVisitors(Thread):
    """
    Thread in charge of sending to all visitors the event modification notification
    """

    def __index__(self, users, event, link):
        Thread.__init__(self)
        self.users = users
        self.event = event
        self.link = link

    def run(self):
        for u in self.users:
            send_modification_notification_mail(self.event, u.email, self.link)