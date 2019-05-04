from django import template
from billapp.models import Ticket
from datetime import datetime
import pytz

utc = pytz.UTC
register = template.Library()

@register.filter
def get_ext(event):
    """
    Filtre qui récupère le nombre d'externes inscrit à un événement
    """
    return event.ticket_set.count() - get_int(event)

@register.filter
def get_int(event):
    """
    Filtre qui récupère le nombre d'interne inscrit à un événement
    """
    return event.ticket_set.filter(user__email__iregex=r'.*epita.*').count()
    
@register.filter
def in_the_bound(e):
    """
    Filtre qui retourne un boolean si l':model:`billapp.Event` est ouvert au inscription actuellement
    """
    begin = e.begin_register.replace(tzinfo=utc)
    end = e.end_register.replace(tzinfo=utc)
    now = datetime.now().replace(tzinfo=utc)
    return now >= begin and now < end
