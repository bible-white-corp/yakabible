from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from billapp.insertions import *
from django.shortcuts import get_object_or_404, render, redirect
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
    events = Event.objects.all().filter(validation_state=4)
    if start and end:
        print(start)
        start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S+02:00').strftime('%Y-%m-%dT%H:%M:%S')
        end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S+02:00').strftime('%Y-%m-%dT%H:%M:%S')
        events = events.filter(end__gte=start, begin__lte=end)
    else:
        events = events.filter(end__gte=datetime.now())
    for obj in events:
        json.append({
            'id': obj.pk,
            'title': obj.title,
            'start': obj.begin,
            'end': obj.end,
            'url': reverse('event', args=[obj.pk]),  # url of event/obj.pk
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
    tickets = Ticket.objects.all().filter(event__validation_state=4)
    if event_id:
        tickets = tickets.filter(event_id=event_id)
    else:
        tickets = tickets.filter(event__end__gte=datetime.now())
    for obj in tickets:
        json.append({
            'id': obj.pk,
            'ionis': obj.ionis,
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


def UpdateTicket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    new_state = request.GET.get('new_state')
    update_ticket(ticket, new_state)
    return HttpResponseRedirect(reverse('event_realtime', args=[ticket.event.pk]))
