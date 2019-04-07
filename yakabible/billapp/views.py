from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.core.paginator import Paginator

from billapp.models import Event

class IndexView(generic.TemplateView):
    template_name = "billapp/index.html"

class CreateEvView(generic.TemplateView):
    template_name = "billapp/create_event.html"

def EventsJSON(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    # Fetch events from BDD
    json = []
    events = Event.objects.all().filter(end__gte=start, begin__lte=end)
    for obj in events:
        json.append({
            'id': obj.pk,
            'title': obj.title,
            'start': obj.begin,
            'end': obj.end,
            'url': '/', # url of event/obj.pk
        })

    return JsonResponse(json, safe=False)