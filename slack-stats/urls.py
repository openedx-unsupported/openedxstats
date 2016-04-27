from django.conf.urls import url
from django.contrib import admin

from .views import HomePageView

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^admin/', admin.site.urls),
]
