from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.core.paginator import Paginator

from .models import *

class IndexView(generic.TemplateView):
    template_name = "billapp/index.html"

class CreateEvView(generic.TemplateView):
    template_name = "billapp/create_event.html"
