from django.conf.urls import url, include
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth import views as auth_views

from openedxstats.views import HomePageView

urlpatterns = [
    url(r'^robots\.txt$', lambda r: HttpResponse("User-Agent: *\nDisallow: /", mimetype="text/plain"), name="robots_file"),
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.LoginView.as_view(
        redirect_authenticated_user=False, template_name='login.html', extra_context={'next': '/sites/current'}), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    url(r'^', include('slackdata.urls')),
    url(r'^', include('sites.urls', namespace="sites")),
]
