
from django.test import TestCase, Client
from billapp.models import Ticket
from billapp.tools import *
from django.contrib.auth import authenticate
from django.urls import reverse

class TicketTestCase(TestCase):
    fixtures = ['user.yaml', 'billapp.yaml']

    def setUp(self):
        self.client = Client()

    def test_type(self):
        [ticket] = Ticket.objects.all()[:1]
        assert get_ticket_type(ticket) == "Externe"


    def test_pdf_response(self):
        [ticket] = Ticket.objects.all()[:1]
        response = make_pdf_response(ticket)
        assert response.status_code == 200

    def test_hide_tickets(self):
        self.client.login(username="President_Antre", password="president_antre")
        for ticket in Ticket.objects.all():
            pk = ticket.pk
            response = self.client.get(reverse('ticket', args=[pk]))
            assert response.status_code == 404

    def test_get_tickets(self):
        self.client.login(username="Admin", password="admin")
        for ticket in Ticket.objects.all().filter(user_id=2):
            pk = ticket.pk
            response = self.client.get(reverse('ticket', args=[pk]))
            assert response.status_code == 200