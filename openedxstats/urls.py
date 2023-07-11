from django.urls import include, path, re_path
from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth import views as auth_views

from openedxstats.views import HomePageView

urlpatterns = [
    re_path(r'^robots\.txt$', lambda r: HttpResponse("User-Agent: *\nDisallow: /", mimetype="text/plain"), name="robots_file"),
    path('', HomePageView.as_view(), name='home'),
    re_path(r'^admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(
        redirect_authenticated_user=False, template_name='login.html', extra_context={'next': '/sites/current'}), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('', include('slackdata.urls')),
    path('', include('sites.urls', namespace="sites")),
]
