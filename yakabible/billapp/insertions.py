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
            validation_state = 'Need authorization',
            request_for_approuval=False,
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

def insert_ticket(request, e):
    t = Ticket(
                user = request.user,
                event = e,
                category = False,
                state = 0
                )
    t.save()
    return t

def update_ticket(ticket, new_state):
    ticket.state = new_state
    ticket.save()
    return ticket

def insert_staff_capacity(formset, event):
    for form in formset:
        if form.cleaned_data['association_name'] == "" or form.cleaned_data['capacity'] <= 0:
           continue
        ev_staff_cap = EventStaffCapacity(
                    event = event,
                    association = Association.objects.get(name=form.cleaned_data['association_name']),
                    capacity = form.cleaned_data['capacity']
                    )
        ev_staff_cap.save()
