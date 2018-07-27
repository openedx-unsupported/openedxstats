from django.conf.urls import url
from openedxstats.apps.sites import views

app_name = 'sites'
urlpatterns = [
    url(r'^sites/all/$', views.ListView.as_view(), name='sites_list'),
    url(r'^sites/all/json$', views.SiteView_JSON, name='sites_list_json'),
    url(r'^sites/map/$', views.MapView.as_view(), name='sites_map'),
    url(r'^sites/hawthorn_map/$', views.HawthornMapView.as_view(), name='sites_hawthorn_map'),
    url(r'^sites/add_site/$', views.add_site, name='add_site'),
    url(r'^sites/update_site/(?P<pk>[0-9]+)/$', views.add_site, name='update_site'),
    url(r'^sites/add_language/$', views.add_language, name='add_language'),
    url(r'^sites/add_geozone/$', views.add_geozone, name='add_geozone'),
    url(r'^sites/site_detail/(?P<pk>[0-9]+)/$', views.SiteDetailView.as_view(), name='site_detail'),
    url(r'^sites/delete_site/(?P<pk>[0-9]+)/$', views.SiteDelete.as_view(), name='delete_site'),
    url(r'^sites/ot_chart/$', views.OTChartView.as_view(), name='ot_chart'),
    url(r'^sites/site_discovery/$', views.SiteDiscoveryListView.as_view(), name='site_discovery'),
    url(r'^sites/csv/$', views.sites_csv_view, name='sites_csv'),
    url(r'^sites/bulk/$', views.bulk_update, name='bulk_update'),
]
