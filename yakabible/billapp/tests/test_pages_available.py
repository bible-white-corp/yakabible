from django.test import TestCase, Client
from django.urls import reverse
from billapp.models import *
from django.contrib.auth import authenticate, login, logout
from billapp.insertions import *
from billapp.forms import *
from billapp.urls import *
from billapp.views import *
# Create your tests here.


class AvailableTestCase(TestCase):
    # fixtures = ['user.yaml', 'billapp.yaml'] Pas nécessaire

    def setUp(self):
        self.client = Client()

    def get_request(self, page):
        response = self.client.get(page)
        assert response.status_code == 200

    def test_index(self):
        self.get_request(reverse('index'))

    def test_connection(self):
        self.get_request(reverse('connection'))

    def test_registration(self):
        self.get_request(reverse('registration'))

    def test_event_list(self):
        self.get_request(reverse('events_list'))

    def test_assos_list(self):
        self.get_request(reverse('assos_list'))
