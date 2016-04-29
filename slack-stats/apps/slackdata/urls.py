from django.conf.urls import url
from slackdata import views

urlpatterns = [
    url(r'^slackdata/users$', views.list_users),
    url(r'^slackdata/top/(?P<top_n>[0-9]+)/$', views.get_top_n),
]
