from django.urls import path
from openedxstats.apps.sites import views

app_name = 'sites'
urlpatterns = [
    path('sites/all/', views.ListAllView.as_view(), name='sites_all_list'),
    path('sites/all/json', views.SiteView_JSON, name='sites_list_json'),
    path('sites/current/', views.ListView.as_view(), name='sites_list'),
    path('sites/map/', views.MapView.as_view(), name='sites_map'),
    path('sites/stats/', views.stats_view, name='sites_stats'),
    path('sites/add_site/', views.add_site, name='add_site'),
    path('sites/update_site/<int:pk>/', views.add_site, name='update_site'),
    path('sites/add_language/', views.add_language, name='add_language'),
    path('sites/add_geozone/', views.add_geozone, name='add_geozone'),
    path('sites/site_detail/<int:pk>/', views.SiteDetailView.as_view(), name='site_detail'),
    path('sites/delete_site/<int:pk>/', views.SiteDelete.as_view(), name='delete_site'),
    path('sites/ot_chart/', views.OTChartView.as_view(), name='ot_chart'),
    path('sites/site_discovery/', views.SiteDiscoveryListView.as_view(), name='site_discovery'),
    path('sites/csv/', views.sites_csv_view, name='sites_csv'),
    path('sites/bulk_update/', views.bulk_update),
    path('sites/bulk_create/', views.bulk_create),
]
