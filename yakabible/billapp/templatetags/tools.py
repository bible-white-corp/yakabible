from django import template
from billapp.models import Ticket
from datetime import datetime
from django.templatetags.static import static
from django.contrib.auth.models import User
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

@register.filter
def get_photo(user):
    try :
        user.social_auth.get(provider="epita")
        return "https://photos.cri.epita.fr/" + user.username
    except:
        return static('billapp/img/profile-placeholder.jpg')

@register.filter
def get_role(index):
    switcher = {
        0: "Membre",
        1: "Membre du bureau",
        2: "Président"
    }
    return switcher.get(index)

@register.filter
def get_president(assos):
    user = assos.associationuser_set.filter(role=2)
    if not user:
        return None
    return user[0].user

@register.simple_tag
def get_admin_email():
    user = User.objects.filter(groups__name="Admin")
    if not user:
        return "NO ADMIN"
    return user[0].email
