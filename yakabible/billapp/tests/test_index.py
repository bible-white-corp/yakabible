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
        self.get_request(reverse('index'))

    def test_unlogged(self):
        response = self.get_request(reverse('index'))
        assert 'href="/profile/' in response
        assert 'href="/assos/' in response
        assert 'href="/connection/' in response
        assert 'href="/login/epita/' in response
        assert 'href="/registration/' in response
        assert get_admin_email() in response
        assert 'Heure du server' in response
        assert 'Développeurs' in response
        assert 'Thomas Lupin' in response

    def test_logged_admin(self):
        self.login("Admin", "admin")
        response = self.get_request(reverse('index'))
        assert 'href="/profile/' in response
        assert 'href="/assos/' in response
        assert 'href="/logout/' in response
        assert 'href="/respos/dashboard' in response
        assert 'href="/event/to_approve/' in response
        assert get_admin_email() in response
        assert 'admin fake' in response

    def test_logged_random(self):
        self.login("Membre_Antre", "membre_antre")
        response = self.get_request(reverse('index'))
        assert 'href="/profile/' in response
        assert 'href="/assos/' in response
        assert 'href="/logout/' in response
        assert 'href="/respos/dashboard' not in response
        assert 'href="/event/to_approve/' not in response
        assert get_admin_email() in response
        assert 'Pas Thomas' in response
