from django.conf.urls import url
from openedxstats.apps.slackdata import views

urlpatterns = [
    url(r'^slackdata/users$', views.list_users),
    url(r'^slackdata/top/(?P<top_n>[0-9]+)/$', views.get_top_n),
    url(r'^slackdata/top/(?P<exclude>-)?(?P<email_pattern>[^/]*)/(?P<top_n>[0-9]+)/$', views.get_top_by_email),
]
