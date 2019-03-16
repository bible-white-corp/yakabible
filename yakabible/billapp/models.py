from django.db import models

class User(models.Model):
    firstname = models.CharField(max_length=64)
    lastname = models.CharField(max_length=64)
    email = models.CharField(max_length=128)
    pseudo = models.CharField(max_length=64)
    password = models.BinaryField(max_length=20)
    role = models.IntegerField()

class Association(models.Model):
    name = models.CharField(max_length=64)
    logo_path = models.CharField(max_length=128)
    email = models.CharField(max_length=64)
    description = models.TextField()

class AssociationUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    association = models.ForeignKey(Association, on_delete=models.CASCADE)
    role = models.IntegerField()

class Event(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    association = models.ForeignKey(Association, on_delete=models.CASCADE)
    manager = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    premium = models.BooleanField()
    begin = models.DateTimeField()
    end = models.DateTimeField()
    begin_register = models.DateTimeField()
    end_register = models.DateTimeField()
    place = models.CharField(max_length=128)
    price_ionis = models.IntegerField()
    price = models.IntegerField()
    ext_capacity = models.IntegerField()
    int_capacity = models.IntegerField()
    staff_capacity = models.IntegerField()
    promotion_image_path = models.CharField(max_length=128)
    validation_state = models.BooleanField()

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    category = models.BooleanField()
    state = models.IntegerField()
# Create your models here.
