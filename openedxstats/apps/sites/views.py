from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum, Q
from openedxstats.apps.sites.models import Site, SiteLanguage, SiteGeoZone, Language, GeoZone, SiteSummarySnapshot
from openedxstats.apps.sites.forms import SiteForm, LanguageForm, GeoZoneForm
import re
from datetime import datetime, timedelta


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


# To allow for JSON response for OTChartView
class JSONResponseMixin(object):
    def render_to_json_response(self, context, **response_kwargs):
        return HttpResponse(self.get_data(context), content_type='application/json', **response_kwargs)

    def get_data(self, context):
        return context


class OTChartView(JSONResponseMixin, generic.list.MultipleObjectTemplateResponseMixin, generic.list.BaseListView):
    model = SiteSummarySnapshot
    template_name = 'sites/ot_chart.html'
    context_object_name = 'snapshot_list'

    def daterange(self, start_date, end_date):
        """
        This function is used to generate a date range, with one day increments. Notice the +1 adjustment on day, and -1
        adjustment on seconds. This is used to ensure each day is actually a datetime of the last second of that day, to
        allow for correct aggregation when querying the database with these dates.
        """
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(days=n+1, seconds=-1)

    def generate_summary_data(self, start_datetime):
        """
        Generate site total and course totals by day since ending of site summary snapshots were recorded
        """
        daily_summary_obj_list = []
        # Generate a summary of total sites and courses active for each day in a range of dates
        for day in self.daterange(start_datetime, datetime.now() + timedelta(days=1)):
            # Query to get all site versions that are active within the specified date period
            day_stats = Site.objects.filter(
                Q(course_count__gt=0) & Q(active_start_date__lte=day) &
                (Q(active_end_date__gte=day) | Q(active_end_date=None))
            ).values('active_start_date').aggregate(sites=Count('active_start_date'), courses=Sum('course_count'))

            # Generate summary object for day
            daily_summary_obj = SiteSummarySnapshot(
                timestamp=day,
                num_sites=day_stats['sites'],
                num_courses=day_stats['courses'],
                notes="Auto-generated day summary"
            )
            daily_summary_obj_list.append(daily_summary_obj)

        return daily_summary_obj_list

    def post(self, request, *args, **kwargs):
        old_ot_data = []
        new_ot_data = []
        if SiteSummarySnapshot.objects.count() > 0 or Site.objects.count() > 0:
            # Get old data (pre-historical tracking implementation)
            old_ot_data = list(SiteSummarySnapshot.objects.all())
            # Gets oldest site summary snapshot from db, after this point we will generate statistics from site versions
            start_datetime = SiteSummarySnapshot.objects.all().order_by('-timestamp').first().timestamp + timedelta(days=1)
            # Generate new data
            new_ot_data = self.generate_summary_data(start_datetime)

        serialized_data = serializers.serialize('json', old_ot_data+new_ot_data)
        return self.render_to_json_response(serialized_data)

    def render_to_response(self, context):
        return super(OTChartView, self).render_to_response(context)


def add_site(request, pk=None):
    if pk:
        s = get_object_or_404(Site, pk=pk)
        # Do not allow edits of old versions
        # TODO: clean this up to be more user friendly
        if s.active_end_date is not None:
            response = HttpResponse()
            response.status_code = 403
            return response
    else:
        s = Site()

    if request.method == 'POST':
        form = SiteForm(request.POST, instance=s)
        if form.is_valid():
            new_site = form.save(commit=False)
            new_form_created_time = new_site.active_start_date
            # We must check for uniqueness explicitly, as SiteForm has trouble raising unique key errors for duplicate
            # site entries when trying to update a site
            try:
                new_site.pk = None
                new_site.validate_unique()
            except ValidationError as err:
                messages.error(request, ",".join(err.messages))
                return render_site_form(request, form, pk)

            if pk: # If updating
                # We must grab the same object from the DB again, as s is linked to the form and using it here will
                # cause duplicate key errors
                old_version = Site.objects.get(pk=pk)
                old_version.active_end_date = new_form_created_time
                old_version.save()
            else:
                # Check if there are other versions of site
                if Site.objects.filter(url=new_site.url).count() > 0:
                    next_most_recent_version_of_site = None
                    # Check if any existing sites were created with a more recent start date
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

            new_site.save(force_insert=True)

            if pk: # Delete existing languages and geographies if updating to prevent duplicates
                new_site.language.clear()
                new_site.geography.clear()

            for l in languages:
                site_language = SiteLanguage.objects.create(language=l, site=new_site)
                site_language.save()

            for g in geozones:
                site_geozone = SiteGeoZone.objects.create(geo_zone=g, site=new_site)
                site_geozone.save()

            messages.success(request, 'Success! A new site version has been added!')
            return HttpResponseRedirect(reverse('sites:sites_list'))

        else:
            # Display errors
            form_errors_string = generate_form_errors_string(form.errors)
            messages.error(request, 'Oops! Something went wrong! Details: %s' % form_errors_string)

    else:
        if pk:
            form = SiteForm(initial={'active_start_date':datetime.now()}, instance=s)
        else:
            form = SiteForm()

    return render_site_form(request, form, pk)


def add_language(request):
    l = Language()

    if request.method == 'POST':
        form = LanguageForm(request.POST, instance=l)
        if form.is_valid():
            form.save()
            messages.success(request, 'Success! A new language has been added!')
            return HttpResponseRedirect(reverse('sites:sites_list'))
        else:
            # Display errors
            form_errors_string = generate_form_errors_string(form.errors)
            messages.error(request, 'Oops! Something went wrong! Details: %s' % form_errors_string)
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
            return HttpResponseRedirect(reverse('sites:sites_list'))
        else:
            # Display errors
            form_errors_string = generate_form_errors_string(form.errors)
            messages.error(request, 'Oops! Something went wrong! Details: %s' % form_errors_string)
    else:
        form = GeoZoneForm()

    return render(request, 'add_geozone.html', {'form': form})


# Helper function for generating form errors
def generate_form_errors_string(form_errors):
    form_errors_string = ""
    for i, err in enumerate(form_errors):
        err_description = re.search(r'<li>(.*?)</li>', str(form_errors[err]), re.I).group(1)
        form_errors_string += err + ": " + err_description + ", "
        if i == len(form_errors) - 1:
            form_errors_string = form_errors_string[:-2]

    return form_errors_string

# Helper function for add_site
def render_site_form(request, form, pk):
    if pk:
        return render(request, 'add_site.html',
                      {'form': form, 'post_url': reverse('sites:update_site', args=[pk]), 'page_title': 'Update Site'})
    else:
        return render(request, 'add_site.html',
                      {'form': form, 'post_url': reverse('sites:add_site'), 'page_title': 'Add Site'})