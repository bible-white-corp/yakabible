from django.db import models
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string

def promo_image_path(instance, filename):
    return 'promo/{0}_{1}'.format(get_random_string(length=32), filename)

def assos_image_path(instance, filename):
    return 'assos/{0}_{1}'.format(get_random_string(length=32), filename)

class Association(models.Model):
    """
    Model of the associations
    """
    # Name of the association, unique string
    name = models.CharField(max_length=64, unique=True)

    # Logo of the association, path to image, uploads it
    logo_path = models.ImageField(upload_to=assos_image_path)

    # Email of the association, unique email field
    email = models.CharField(max_length=64, unique=True)

    # Description of the association, string
    description = models.TextField(max_length=2000)

    # Url to the association website, optionnal.
    url = models.TextField(max_length=64, default=None, blank=True, null=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    """
    Model of the events
    """

    # Title of the event, string
    title = models.CharField(max_length=128)

    # Description of the event, string
    description = models.TextField(max_length=2000)

    # Foreign key to the hosting association.
    association = models.ForeignKey(Association, on_delete=models.CASCADE)

    # Foreign key to the user managing the event.
    manager = models.ForeignKey(User, on_delete=models.CASCADE)

    # Boolean indicating if the event has been set as Premium
    premium = models.BooleanField()

    # Date of the beginning of the event.
    begin = models.DateTimeField()

    # Date of the ending of the event.
    end = models.DateTimeField()

    # Date of the beginning of visitor's registration
    begin_register = models.DateTimeField()

    # Date of the ending og visitor's registration
    end_register = models.DateTimeField()

    # Location of the event, string
    place = models.CharField(max_length=128)

    # Price of the event for IONIS members, decimal xxx,xx
    price_ionis = models.DecimalField(decimal_places=2, max_digits=5)

    # Price of the event for externals, decimal xx,xxx
    price = models.DecimalField(decimal_places=2, max_digits=5)

    # Capacity for external visitors, positive integer
    ext_capacity = models.PositiveSmallIntegerField()

    # Capacity for IONIS visitors, positve integer
    int_capacity = models.PositiveSmallIntegerField()

    # Capacity for staff at the event, positive integer
    staff_capacity = models.PositiveSmallIntegerField()

    # Path to the promotional image of the event, uploads it, optional
    promotion_image_path = models.ImageField(upload_to=promo_image_path, blank=True, null=True)

    # Enumeration of the state of the event
    validation_state = models.SmallIntegerField(choices=(
        (1, 'Need authorization'),
        (2, 'Approved by the association'),
        (3, 'Approved by EPITA'),
        (4, 'Authorized')
    ), default=1)

    # Boolean indicating if the event has been asked for approval
    request_for_approval = models.BooleanField(default=False)

    # Boolean indicating of the capacity of the event should be shown to visitors
    show_capacity = models.BooleanField()

    def __str__(self):
        return self.title

class AssociationUser(models.Model):
    """
    Model associating :model:`billapp.Association` à un :model:`django.contrib.auth.models.User`.
    Used to register users to associations.
    """
    # Foreign key of the user
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Foreign key of the association
    association = models.ForeignKey(Association, on_delete=models.CASCADE)

    # Integer for the role of the user in the association
    role = models.IntegerField()
        # 0 = Member
        # 1 = Bureau's member
        # 2 = President

    def __str__(self):
        return self.user.username + ' : ' + self.association.name + ' (' + str(self.role) + ')'

class Ticket(models.Model):
    """
    Model of tickets.
    """

    # Foreign key to the user
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Foreign key to the event
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    # Boolean indicating if the ticket is a staff one
    category = models.BooleanField()

    # Boolean indicating if the tickets is a IONIS one or not
    ionis = models.BooleanField()
    association = models.ForeignKey(Association, on_delete=models.CASCADE, blank=True, null=True)
    state = models.IntegerField()

    def __str__(self):
        return self.user.username + ' (' + self.event.title + ')'

class EventStaffCapacity(models.Model):
    """
    Model to save staff capacity for each association for each event
    """

    # Foreign key of the event
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    # Foreign key to the association
    association = models.ForeignKey(Association, on_delete=models.CASCADE)

    # Number of staff allowed for the event
    capacity = models.IntegerField()
