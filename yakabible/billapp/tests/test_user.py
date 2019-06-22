from django.test import TestCase
from billapp.models import *
from django.contrib.auth import authenticate, login, logout
from billapp.insertions import *
from billapp.forms import *


# Create your tests here.

class UserTestCase(TestCase):
    fixtures = ['user.yaml', 'billapp.yaml']

    def test_user_form(self):
        form = Inscription_Form(data={
            'email': "invalidemail.fr",
            'firstname': 'toto',
            'lastname': 'titi',
            'pwd': 'password',
            'pwd_conf': 'password',
            'username': 'login'
        })
        self.assertEqual(form.is_valid(), False)
        form = Inscription_Form(data={
            'email': "valid@email.fr",
            'firstname': 'toto',
            'lastname': 'titi',
            'pwd': 'password',
            'pwd_conf': 'password',
            'username': 'login'
        })
        self.assertEqual(form.is_valid(), True)
        insert_user(form)

    def test_connection_user(self):
        self.test_user_form()
        user = authenticate(username="login", password="password")
        self.assertNotEqual(user, None)
