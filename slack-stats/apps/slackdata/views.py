from django.shortcuts import render
from .models import SlackUser
from .serializers import SlackUserSerializer
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

# Create your views here.
class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def list_users(request):
    """
    List all users
    """
    if request.method == 'GET':
        users = SlackUser.objects.all()
        serializer = SlackUserSerializer(users, many=True)
        return JSONResponse(serializer.data)
