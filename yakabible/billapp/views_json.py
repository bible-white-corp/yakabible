from django.http import JsonResponse
from django.urls import reverse
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from datetime import datetime

from .models import Event, Ticket

def get_color(obj):
    if obj.premium:
        return '#b23939'
    return ''

def EventsJSON(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    # Fetch events from BDD
    json = []
    events = Event.objects.all()
    if start and end:
        events = events.filter(end__gte=start, begin__lte=end)
    else:
        events = events.filter(end__gte=datetime.now())
    for obj in events:
        json.append({
            'id': obj.pk,
            'title': obj.title,
            'start': obj.begin,
            'end': obj.end,
            'url': reverse('event', args=[obj.pk]), # url of event/obj.pk
            'description': obj.association.name,
            'color': get_color(obj)
        })
    res = JsonResponse(json, safe=False)
    res["Access-Control-Allow-Origin"] = "*"
    return res

def TicketsJSON(request):
    event_id = request.GET.get('event')
    # Fetch tickets from BDD
    json = []
    tickets = Ticket.objects.all()
    if event_id:
        tickets = tickets.filter(event_id=event_id)
    else:
        tickets = tickets.filter(event__end__gte=datetime.now())
    for obj in tickets:
        json.append({
            'id': obj.pk,
            'event': obj.event.pk,
            'username': obj.user.username,
            'firstname': obj.user.first_name,
            'lastname': obj.user.last_name,
            'email': obj.user.email,
            'category': obj.category,
            'state': obj.state
        })
    res = JsonResponse(json, safe=False)
    res["Access-Control-Allow-Origin"] = "*"
    return res
