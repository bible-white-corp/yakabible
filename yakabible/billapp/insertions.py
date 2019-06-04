from .models import *
from .forms import Event_Form, Staff_Form, Staff_Form_Set

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

def insert_ticket(user, e):
    t = Ticket(
                user = user,
                event = e,
                category = False,
                state = 0
                )
    t.save()
    return t

def insert_staff(user, e):
    t = Ticket (
                user = user,
                event = e,
                category = True,
                state = 0
                )
    t.save()
    return t

def update_ticket(ticket, new_state):
    ticket.state = new_state
    ticket.save()
    return ticket

def update_event(user, form, staff_form, event):
    EventStaffCapacity.objects.filter(event=event).delete()
    if not insert_staff_capacity(staff_form, event):
        return False
    notify_president = False
    notify_adm = False
    Event.objects.filter(pk=event.pk).update(
            title = form.cleaned_data['title'],
            description = form.cleaned_data['description'],
            association = event.association,
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
    """
    if event.title != event_form.cleaned_data['title']:
        notify_president = True, etc
    """
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
