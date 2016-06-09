from django.shortcuts import render
from django.views import generic
from .models import *

class ListView(generic.ListView):
    model = Site

    template_name = 'sites/sites_list.html'
    context_object_name = 'sites_list'

    #def get_queryset(self):
    #    return Site.objects.all()
