from django.db.models import Sum
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from openedxstats.apps.slackdata.models import SlackUser, MessageCountByDay
from openedxstats.apps.slackdata.serializers import SlackUserSerializer, UserCountSerializer

# Create your views here.

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super().__init__(content, **kwargs)

def list_users(request):
    """
    List all users
    """
    if request.method == 'GET':
        users = SlackUser.objects.all()
        serializer = SlackUserSerializer(users, many=True)
        return JSONResponse(serializer.data)

def get_top_n(request, top_n):
    """
    List top N users
    """
    if request.method == 'GET':
        r = MessageCountByDay.objects.annotate(msg_count=Sum('count'))\
            .values('user__name', 'count')\
            .order_by('-count')[:top_n]
        serializer = UserCountSerializer(r, many=True)
        return JSONResponse(serializer.data)

def get_top_by_email(request, exclude, email_pattern, top_n):
    """
    List top N users
    """
    if request.method == 'GET':
        if(exclude == '-'):
            r = MessageCountByDay.objects.exclude(user__email__endswith=(email_pattern))\
                .annotate(msg_count=Sum('count')).values('user__name', 'count')\
                .order_by('-count')[:top_n]
        else:
            r = MessageCountByDay.objects.filter(user__email__endswith=(email_pattern))\
                .annotate(msg_count=Sum('count')).values('user__name', 'count')\
                .order_by('-count')[:top_n]
        serializer = UserCountSerializer(r, many=True)
        return JSONResponse(serializer.data)
