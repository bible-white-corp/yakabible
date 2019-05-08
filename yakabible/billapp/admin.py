from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Association)
admin.site.register(Event)
admin.site.register(Ticket)
admin.site.register(AssociationUser)
admin.site.register(EventStaffCapacity)
