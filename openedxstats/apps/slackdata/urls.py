from django.urls import path, re_path
from openedxstats.apps.slackdata import views

urlpatterns = [
    path('slackdata/users', views.list_users),
    path('slackdata/top/<int:top_n>/', views.get_top_n),
    re_path(r'^slackdata/top/(?P<exclude>-)?(?P<email_pattern>[^/]*)/(?P<top_n>[0-9]+)/$', views.get_top_by_email),
]
