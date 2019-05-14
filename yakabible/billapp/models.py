from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from enum import Enum

def promo_image_path(instance, filename):
    return 'promo/{0}_{1}'.format(get_random_string(length=32), filename)

def assos_image_path(instance, filename):
    return 'assos/{0}_{1}'.format(get_random_string(length=32), filename)

class Association(models.Model):
    """
    Model représentant une association
    """
    name = models.CharField(max_length=64, unique=True)
    logo_path = models.ImageField(upload_to=assos_image_path)
    email = models.CharField(max_length=64, unique=True)
    description = models.TextField(max_length=2000)

    def __str__(self):
        return self.name

class Event(models.Model):
    """
    Model représentant un événement00
    """

    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2000)
    association = models.ForeignKey(Association, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    premium = models.BooleanField()
    begin = models.DateTimeField()
    end = models.DateTimeField()
    begin_register = models.DateTimeField()
    end_register = models.DateTimeField()
    place = models.CharField(max_length=128)
    price_ionis = models.DecimalField(decimal_places=2, max_digits=5)
    price = models.DecimalField(decimal_places=2, max_digits=5)
    ext_capacity = models.PositiveSmallIntegerField()
    int_capacity = models.PositiveSmallIntegerField()
    staff_capacity = models.PositiveSmallIntegerField()
    promotion_image_path = models.ImageField(upload_to=promo_image_path, blank=True)
    validation_state = models.SmallIntegerField(choices=(
        (1, 'Need authorization'),
        (2, 'Approved by the association'),
        (3, 'Approved by EPITA'),
        (4, 'Authorized')
    ), default=1)
    request_for_approval = models.BooleanField(default=False)

    show_capacity = models.BooleanField()

    def __str__(self):
        return self.title

class AssociationUser(models.Model):
    """
    Model qui associe une :model:`billapp.Association` à un :model:`django.contrib.auth.models.User`.
    Il est utilisé pour inscrire un membre à une association.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    association = models.ForeignKey(Association, on_delete=models.CASCADE)
    role = models.IntegerField()

    def __str__(self):
        return self.user.username + ' : ' + self.association.name + ' (' + str(self.role) + ')'

class Ticket(models.Model):
    """
    Model représentant un ticket.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    category = models.BooleanField()
    state = models.IntegerField()

    def __str__(self):
        return self.user.username + ' (' + self.event.title + ')'

class EventStaffCapacity(models.Model):
    """
    Model pour stocker les places de staff disponibles pour une asso
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    association = models.ForeignKey(Association, on_delete=models.CASCADE)
    capacity = models.IntegerField()

# Create your models here.
