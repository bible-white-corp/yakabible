from django import template
from billapp.models import Ticket

register = template.Library()

@register.filter
def get_ext(event):
    return event.ticket_set.count() - get_int(event)

@register.filter
def get_int(event):
    return event.ticket_set.filter(user__email__iregex=r'.*epita.*').count()
