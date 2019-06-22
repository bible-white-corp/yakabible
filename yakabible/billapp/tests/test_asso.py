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
        for asso in Association.objects.all():
            pk = asso.pk
            response = self.get_request(reverse('association', args=[pk]))
            assert 'href="mailto:{}"'.format(asso.email) in response
            assert 'src="/media/{}"'.format(asso.logo_path) in response
            assert asso.name in response
            assert asso.description[:10] in response
            assert 'href="/assos/{}/dashboard"'.format(pk) not in response


    def test_logged_admin(self):
        self.login("Admin", "admin")
        for asso in Association.objects.all():
            pk = asso.pk
            response = self.get_request(reverse('association', args=[pk]))
            assert 'href="mailto:{}"'.format(asso.email) in response
            assert 'src="/media/{}"'.format(asso.logo_path) in response
            assert asso.name in response
            assert asso.description[:10] in response
            assert 'href="/assos/{}/dashboard"'.format(pk) in response


    def test_logged_membre(self):
        self.login("Bureau_Antre", 'bureau_antre')
        pk = 1
        asso = Association.objects.get(pk=pk)
        response = self.get_request(reverse('association', args=[pk]))
        assert 'href="mailto:{}"'.format(asso.email) in response
        assert 'src="/media/{}"'.format(asso.logo_path) in response
        assert asso.name in response
        assert asso.description[:10] in response
        assert 'href="/assos/{}/dashboard"'.format(pk) in response

