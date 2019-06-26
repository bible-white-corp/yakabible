from django.test import TestCase
from billapp.models import Event as MyEvent
from billapp.models import Ticket
from django.contrib.auth import authenticate, login, logout
from billapp.insertions import *
from billapp.forms import *
from billapp.tools import *

# Create your tests here.


class MailTestCase(TestCase):
    fixtures = ['user.yaml', 'billapp.yaml']

    def test_pdf(self):
        [ticket] = Ticket.objects.all()[:1]
        assert make_pdf(ticket) is not None

    def test_mail(self):
        [ticket] = Ticket.objects.all()[:1]
        assert send_pdf_mail(ticket)

    def test_approv_mail(self):
        [event] = MyEvent.objects.all()[:1]
        [adm] = User.objects.filter(groups__name="Admin")[:1]
        assert send_approval_mail(event, adm, "Test")

    def test_send_registration(self):
        assert send_registration("TestCase", "yakabible+test@gmail.com", "")

    def test_send_validation_mail(self):
        [event] = MyEvent.objects.all()[:1]
        adm = User.objects.filter(groups__name="Admin")[:1]
        assert send_validation_mail(event, adm, "Test")

    def test_send_refusing_mail(self):
        [event] = MyEvent.objects.all()[:1]
        adm = User.objects.filter(groups__name="Admin")[:1]
        assert send_refusing_mail(event, adm, True, "Test description", "Test")

    def test_send_modification_mail(self):
        [event] = MyEvent.objects.all()[:1]
        [adm] = User.objects.filter(groups__name="Admin")[:1]
        assert send_modification_mail(event, None, adm, "Test")

    def test_send_modification_notification_mail(self):
        [event] = MyEvent.objects.all()[:1]
        [user] = User.objects.filter(groups__name="Admin")[:1]
        assert send_modification_notification_mail(event, user, "Test")
