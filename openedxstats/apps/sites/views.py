from __future__ import unicode_literals

from django.shortcuts import render
from django.views import generic
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from .models import Site, SiteLanguage, SiteGeoZone, Language, GeoZone
from .forms import SiteForm, LanguageForm, GeoZoneForm


class ListView(generic.ListView):
    model = Site

    template_name = 'sites/sites_list.html'
    context_object_name = 'sites_list'


class SiteDetailView(generic.DetailView):
    model = Site

    template_name = 'sites/site_detail.html'
    context_object_name = 'site'


class SiteDelete(generic.DeleteView):
    model = Site
    template_name = 'sites/delete_site.html'
    success_url = reverse_lazy('sites:sites_list')


# TODO: Implement updating sites, not just adding. Refer to http://www.ianrolfe.com/page/django-many-to-many-tables-and-forms/ for help
def add_site(request):
    # This is where I will add an if statement to check if we are passing in an existing id or making a new object
    # For now, we will just make a new object
    s = Site()

    if request.method == 'POST':
        form = SiteForm(request.POST, instance=s)
        if form.is_valid():
            #try:
            new_site = form.save(commit=False)
            new_form_created_time = new_site.active_start_date #form.cleaned_data.pop('active_start_date')

            if Site.objects.filter(url=new_site.url).count() > 0:
                next_most_recent_version_of_site = None
                for site in Site.objects.filter(url=new_site.url).order_by('active_start_date'):
                    if site.active_start_date > new_form_created_time:
                        next_most_recent_version_of_site = site
                        break

                if next_most_recent_version_of_site is not None:
                    # The version being submitted is older than current version
                    new_site.active_end_date = next_most_recent_version_of_site.active_start_date
                else:
                    # The version being submitted is newer than current version
                    next_most_recent_version_of_site = Site.objects.filter(url=new_site.url).order_by(
                        '-active_start_date').first()
                    next_most_recent_version_of_site.active_end_date = new_form_created_time
                    next_most_recent_version_of_site.save()

            languages = form.cleaned_data.pop('language')
            geozones = form.cleaned_data.pop('geography')
            new_site.save()

            # site.language.clear()    # delete existing languages (for if/when I implement update)
            for l in languages:
                site_language = SiteLanguage.objects.create(language=l, site=s)
                site_language.save()

            for g in geozones:
                site_geozone = SiteGeoZone.objects.create(geo_zone=g, site=s)
                site_geozone.save()

            messages.success(request, 'Success! A new site has been added!')
            #except Exception as e:
            #    messages.error(request, 'Oops! Something went wrong! Details: %s' % e.message)
            #    print("ERROR in add_site, should making error toast notification")
        else:
            messages.error(request, 'Oops! Something went wrong! Details: %s' % form.errors)

        return HttpResponseRedirect(reverse('sites:sites_list'))
    else:
        form = SiteForm()

    return render(request, 'add_site.html', {'form':form})


def add_language(request):
    l = Language()

    if request.method == 'POST':
        form = LanguageForm(request.POST, instance=l)
        if form.is_valid():
            form.save()
            messages.success(request, 'Success! A new language has been added!')
        else:
            messages.error(request, 'Oops! Something went wrong! Details: %s' % form.errors)

        return HttpResponseRedirect(reverse('sites:sites_list'))
    else:
        form = LanguageForm()

    return render(request, 'add_language.html', {'form':form})


def add_geozone(request):
    g = GeoZone()

    if request.method == 'POST':
        form = GeoZoneForm(request.POST, instance=g)
        if form.is_valid():
            form.save()
            messages.success(request, 'Success! A new geozone has been added!')
        else:
            messages.error(request, 'Oops! Something went wrong! Details: %s' % form.errors)

        return HttpResponseRedirect(reverse('sites:sites_list'))
    else:
        form = GeoZoneForm()

    return render(request, 'add_geozone.html', {'form': form})

