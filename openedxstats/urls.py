from django.conf.urls import url, include
from django.contrib import admin

from rest_framework import routers, serializers, viewsets

from .views import HomePageView

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('slackdata.urls')),
]
