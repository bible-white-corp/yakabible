import sys

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from paypal.standard.models import ST_PP_COMPLETED
from django.dispatch import receiver
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received

from billapp.insertions import insert_ticket
from billapp.models import Event, Ticket
from billapp.tools import is_ionis


@receiver(valid_ipn_received)
def valid_ipn_handler(sender, **kwargs):
    ipn = sender
    payment_key = ipn.invoice.split('/')

    if len(payment_key) != 2:
        raise ValueError

    event_id = "".join(payment_key[1])
    user_id = payment_key[0]
    print("event_id: " + str(event_id))
    print("user_id: " + str(user_id))

    try:
        tmp_t = Ticket.objects.get(user=user_id, event=event_id)
    except Ticket.DoesNotExist as e:
        tmp_t = None

    if tmp_t is not None:
        raise ValueError

    event = get_object_or_404(Event, pk=event_id)
    user = get_object_or_404(User, id=user_id)
    #  TODO ajouter sécurité, genre clé random dans le invoice qu'on stocke, puis compare
    t = insert_ticket(user, event)
    print("ARGENT RECU de " + user.username + " pour l'événement " + event.title)  # debug

    return HttpResponseRedirect(reverse('reg_event_success', args=[t.pk]))


@receiver(invalid_ipn_received)
def do_not_show_me_the_money(sender, **kwargs):
    print("\nERROR: IPN signal was treated as invalid by django-paypal:" +
          "\ninvoice;" + sender.invoice +
          "\ntxn_id: " + sender.txn_id + "\n", file=sys.stderr)

