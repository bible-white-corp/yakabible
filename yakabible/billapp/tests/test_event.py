import datetime
import json

from django.test import TestCase, Client
from billapp.models import *
from django.contrib.auth import authenticate, login, logout
from billapp.insertions import *
from billapp.forms import *
from billapp.templatetags.tools import *
from django.urls import reverse


# Create your tests here.


class IndexTestCase(TestCase):
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
        self.get_request(reverse('event', args=[2]))

    def test_unlogged(self):
        for event in Event.objects.all().filter(end__gte=datetime.now(), validation_state=4):
            pk = event.pk
            response = self.get_request(reverse('event', args=[pk]))
            if event.premium:
                assert 'Événement premium' in response
            else:
                assert 'Événement premium' not in response
            assert event.association.name in response
            assert 'href="/event/{}/register?ionis=true"'.format(pk) in response
            assert event.description[:10] in response
            assert event.title in response
            assert event.manager.username in response

    def test_logged_admin(self):
        self.login("Admin", "admin")
        for event in Event.objects.all().filter(end__gte=datetime.now(), validation_state=4):
            pk = event.pk
            response = self.get_request(reverse('event', args=[pk]))
            if event.premium:
                assert 'Événement premium' in response
            else:
                assert 'Événement premium' not in response
            assert event.association.name in response
            assert 'href="/event/{}/register?ionis=true"'.format(pk) in response
            assert event.description[:10] in response
            assert event.title in response
            assert event.manager.username in response
            assert 'href="/event/{}/staff"'.format(pk) in response

    def test_logged_membre(self):
        self.login("Membre_Antre", 'membre_antre')
        pk = 2
        response = self.get_request(reverse('event', args=[pk]))
        event = Event.objects.get(pk=pk)
        if event.premium:
            assert 'Événement premium' in response
        else:
            assert 'Événement premium' not in response
        assert event.association.name in response
        assert 'href="/event/{}/register?ionis=true"'.format(pk) in response
        assert event.description[:10] in response
        assert event.title in response
        assert event.manager.username in response
