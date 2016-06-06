from django.conf.urls import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from sites import views

urlpatterns = [
               url(r'^sites/all$', views.ListView.as_view()),
]

# urlpatterns = ('',
#                url(r'^sites/all$', views.ListView.as_view()),
# )+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
#
# urlpatterns += staticfiles_urlpatterns()
