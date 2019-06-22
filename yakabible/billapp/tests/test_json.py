import datetime
import json

from django.test import TestCase, Client
from billapp.models import *
from django.contrib.auth import authenticate, login, logout
from billapp.insertions import *
from billapp.forms import *
from django.urls import reverse

# Create your tests here.

class JsonTestCase(TestCase):
    fixtures = ['user.yaml', 'billapp.yaml']

    def setUp(self):
        self.client = Client()

    def get_request(self, page):
        response = self.client.get(page)
        assert response.status_code == 200
        return json.loads(response.content)

    def test_tickets(self):
        response = self.get_request(reverse('tickets_json'))
        assert 'id' in response[0]
        assert 'ionis' in response[0]
        assert 'event' in response[0]
        assert 'username' in response[0]
        assert 'firstname' in response[0]
        assert 'lastname' in response[0]
        assert 'email' in response[0]
        assert 'category' in response[0]
        assert 'state' in response[0]
        assert len(response) == len(Ticket.objects.all().filter(event__validation_state=4))

    def test_events(self):
        response = self.get_request(reverse('events_json'))
        assert 'id' in response[0]
        assert 'title' in response[0]
        assert 'start' in response[0]
        assert 'end' in response[0]
        assert 'url' in response[0]
        assert 'description' in response[0]
        assert 'color' in response[0]
        assert len(response) == len(Event.objects.all().filter(validation_state=4, end__gte=datetime.datetime.now()))
