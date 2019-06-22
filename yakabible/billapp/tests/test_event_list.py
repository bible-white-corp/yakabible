from datetime import datetime
import json

from django.test import TestCase, Client
from billapp.models import *
from django.contrib.auth import authenticate, login, logout
from billapp.insertions import *
from billapp.forms import *
from billapp.templatetags.tools import *
from django.urls import reverse


# Create your tests here.


class EventListTestCase(TestCase):
    fixtures = ['user.yaml', 'billapp.yaml']

    def setUp(self):
        self.client = Client()

    def get_request(self, page):
        response = self.client.get(page)
        assert response.status_code == 200
        return response.content.decode("utf-8")

    def login(self, u, p):
        self.client.login(username=u, password=p)

    def test_available(self):
        self.get_request(reverse('events_list'))

    def test_list(self):
        response = self.get_request(reverse('events_list'))
        for e in Event.objects.all().filter(end__gte=datetime.now(), validation_state=4):
            assert 'href="/event/{}"'.format(e.pk) in response
            assert 'href="/assos/{}"'.format(e.association.pk) in response
        assert 'href="?page=1"' in response
