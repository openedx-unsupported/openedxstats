from django.shortcuts import render
from django.views import generic
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import Site
from .forms import SiteForm

class ListView(generic.ListView):
    model = Site

    template_name = 'sites/sites_list.html'
    context_object_name = 'sites_list'

    #def get_queryset(self):
    #    return Site.objects.all()


def add_site(request):
    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            form_to_post = form.save(commit=False) # In case we want to modify the object before saving to DB
            form_to_post.save()
            form_to_post.save_m2m()

            return HttpResponseRedirect(reverse('sites:sites_list'))

    else:
        form = SiteForm()

    return render(request, 'add_site.html', {'form':form})
