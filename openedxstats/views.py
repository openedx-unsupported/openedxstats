from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse

class HomePageView(TemplateView):
    template_name = 'home.html'

    # TODO: Remove this method once a home page is created
    def dispatch(self, request, *args, **kwargs):
        # Redirect to sites list
        return HttpResponseRedirect(reverse('sites:sites_list'))
