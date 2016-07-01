from django import forms
from django.contrib.auth.models import User
from openedxstats.apps.sites.models import Site, Language, GeoZone
from datetimewidget.widgets import DateTimeWidget

default_url_errors = {
    'required': 'This field is required',
    'invalid': 'Enter a valid URL, i.e. https://example.com'
}

class SiteForm(forms.ModelForm):
    #site_type = forms.CharField(max_length=255, help_text="Type of site, enter 'General' if unsure.")
    #name = forms.CharField(max_length=255)
    url = forms.URLField(max_length=1000, required=True, error_messages=default_url_errors)
    course_count = forms.IntegerField(min_value=0, required=False)
    #last_checked = forms.DateField()
    #org_type = forms.CharField(max_length=255, help_text="E.g. Industrial, Academic, etc.")
    #language = forms.ModelMultipleChoiceField(Language.objects.all())   # Does the same thing as the one below
    #geography = forms.SelectMultiple()
    #github_fork = forms.URLField()
    #notes = forms.CharField(widget=forms.TextInput)
    #course_type = forms.ChoiceField(choices=COURSE_TYPE_CHOICES)
    registered_user_count = forms.IntegerField(min_value=0, required=False)
    active_learner_count = forms.IntegerField(min_value=0, required=False)

    class Meta:
        model = Site
        exclude = ['active_end_date']
        # If the corresponding attribute in site form is uncommented above, these help messages won't show
        help_texts = {
            "language": "Select multiple languages with CMD+Click",
            "geography": "Select multiple geo-zones with CMD+Click",
            #'url': 'This text is not persistent on page, what gives!',
            #'last_checked': 'This text is persistent on the page, conflicts with error help text provided by bootstrap',
        }
        widgets = {
            'active_start_date': DateTimeWidget(attrs={'id': 'active_start_date'}, bootstrap_version=3),
        }


class LanguageForm(forms.ModelForm):

    class Meta:
        model = Language
        fields = '__all__'


class GeoZoneForm(forms.ModelForm):

    class Meta:
        model = GeoZone
        fields = '__all__'


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = '__all__'
