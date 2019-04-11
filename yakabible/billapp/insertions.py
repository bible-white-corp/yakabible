from .models import *
from .forms import Event_Form

def insert_event(user, form):
    e = Event(
            title = form.cleaned_data['title'],
            description = form.cleaned_data['description'],
            association = Association.objects.get(name='Antre'),
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
            validation_state = False
            )
    e.save()

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
