from django.conf.urls import url
from . import views

app_name = 'sites'
urlpatterns = [
    url(r'^sites/all$', views.ListView.as_view(), name='sites_list'),
    url(r'^sites/add_site/$', views.add_site, name='add_site'),
    url(r'^sites/add_language/$', views.add_language, name='add_language'),
    url(r'^sites/add_geozone/$', views.add_geozone, name='add_geozone'),
    url(r'^sites/site_detail/(?P<pk>[0-9]+)/$', views.SiteDetailView.as_view(), name='site_detail'),
]
