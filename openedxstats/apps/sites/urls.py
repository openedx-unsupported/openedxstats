from django.conf.urls import url
from . import views

urlpatterns = [
               url(r'^sites/all$', views.ListView.as_view(), name='sites_list'),
               url(r'^sites/add_site/$', views.add_site, name='add_site'),
]