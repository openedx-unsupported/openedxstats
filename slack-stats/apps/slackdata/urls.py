from django.conf.urls import url
from slackdata import views

urlpatterns = [
    url(r'^slackdata/users$', views.list_users),
]
