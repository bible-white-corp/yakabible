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

    def get_request_error(self, page):
        response = self.client.get(page)
        assert response.status_code != 200
        return response.content.decode("utf-8")

    def get_request(self, page):
        response = self.client.get(page)
        assert response.status_code == 200
        return response.content.decode("utf-8")

    def login(self, u, p):
        self.client.login(username=u, password=p)

    def test_unlogged_respo_dashboard(self):
        response = self.get_request_error(reverse('dashboard_respo'))

    def test_logged_admin_respo_dashboard(self):
        self.login("Admin", "admin")
        response = self.get_request(reverse('dashboard_respo'))

    def test_logged_membre_respo_dashboard(self):
        self.login("Bureau_Antre", 'bureau_antre')
        response = self.get_request_error(reverse('dashboard_respo'))
