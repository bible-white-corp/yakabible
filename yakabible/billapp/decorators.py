from .models import *
from .tools import *
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, FileResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from .templatetags.tools import *
from django.contrib.auth.decorators import user_passes_test


def in_asso_required(function):
    """
    Decorator for view that 403 if users not in association
    """

    def wrap(obj, *args, **kwargs):
        asso = Association.objects.get(pk=kwargs['pk'])
        if user_in_assos(obj.user, asso):
            return function(obj, *args, **kwargs)
        else:
            raise Http404("Not in asso")

    return wrap


def in_asso_super_required(function):
    """
    Decorator for view that 403 if users not bureau's member at least
    """

    def wrap(obj, *args, **kwargs):
        asso = Association.objects.get(pk=kwargs['pk'])
        if user_in_assos_super(obj.user, asso):
            return function(obj, *args, **kwargs)
        else:
            raise Http404("Not in asso")

    return wrap


def group_required(*group_names):
    """
    Decorator to check is users at least in groups
    """

    def in_groups(u):
        print(u)
        if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
            return True
        return False

    return user_passes_test(in_groups)
