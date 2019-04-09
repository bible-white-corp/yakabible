from django import template
from billapp.models import Ticket
from datetime import datetime
import pytz

utc = pytz.UTC
register = template.Library()

@register.filter
def get_ext(event):
    return event.ticket_set.count() - get_int(event)

@register.filter
def get_int(event):
    return event.ticket_set.filter(user__email__iregex=r'.*epita.*').count()
    
@register.filter
def in_the_bound(e):
    begin = e.begin_register.replace(tzinfo=utc)
    end = e.end_register.replace(tzinfo=utc)
    now = datetime.now().replace(tzinfo=utc)
    return now >= begin and now < end
