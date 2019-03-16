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
    logo_path = models.CharField(max_length=64)
    email = models.CharField(max_length=64)
    description = models.TextField()

# Create your models here.
