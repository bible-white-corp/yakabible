from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

def promo_image_path(instance, filename):
    return 'promo/{0}_{1}'.format(get_random_string(length=32), filename)

def assos_image_path(instance, filename):
    return 'assos/{0}_{1}'.format(get_random_string(length=32), filename)

class Association(models.Model):
    name = models.CharField(max_length=64)
    logo_path = models.ImageField(upload_to=assos_image_path)
    email = models.CharField(max_length=64)
    description = models.TextField()

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    association = models.ForeignKey(Association, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, on_delete=models.CASCADE)
    premium = models.BooleanField()
    begin = models.DateTimeField()
    end = models.DateTimeField()
    begin_register = models.DateTimeField()
    end_register = models.DateTimeField()
    place = models.CharField(max_length=128)
    price_ionis = models.FloatField()
    price = models.FloatField()
    ext_capacity = models.IntegerField()
    int_capacity = models.IntegerField()
    staff_capacity = models.IntegerField()
    promotion_image_path = models.ImageField(upload_to=promo_image_path)
    validation_state = models.BooleanField()

    def __str__(self):
        return self.title

class AssociationUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    association = models.ForeignKey(Association, on_delete=models.CASCADE)
    role = models.IntegerField()

    def __str__(self):
        return self.user.username + ' : ' + self.association.name + ' (' + str(self.role) + ')'

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    category = models.BooleanField()
    state = models.IntegerField()

    def __str__(self):
        return self.user.username + ' (' + self.event.title + ')'

# Create your models here.
