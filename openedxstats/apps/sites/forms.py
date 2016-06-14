from django import forms
from .models import Site
from datetimewidget.widgets import DateWidget

default_url_errors = {
    'required': 'This field is required',
    'invalid': 'Enter a valid URL, i.e. https://example.com'
}

class SiteForm(forms.ModelForm):
    #site_type = forms.CharField(max_length=255, help_text="Type of site, enter 'General' if unsure.")
    #name = forms.CharField(max_length=255)
    url = forms.URLField(max_length=1000, required=True, error_messages=default_url_errors)
    #course_count = forms.IntegerField()
    #last_checked = forms.DateField()
    #org_type = forms.CharField(max_length=255, help_text="E.g. Industrial, Academic, etc.")
    #language = forms.SelectMultiple()
    #geography = forms.SelectMultiple()
    #github_fork = forms.URLField()
    #notes = forms.CharField(widget=forms.TextInput)
    #course_type = forms.ChoiceField(choices=COURSE_TYPE_CHOICES)
    #registered_user_count = forms.IntegerField()
    #active_learner_count = forms.IntegerField()

    class Meta:
        model = Site
        fields = '__all__'
        help_texts = {
            "language": "Select multiple languages with CMD+Click",
            "geography": "Select multiple geo-zones with CMD+Click",
            #'url': 'This text is not persistent on page, what gives!',
            #'last_checked': 'This text is persistent on the page, conflicts with error help text provided by bootstrap',
        }
        widgets = {
            'last_checked': DateWidget(attrs={'id': "last_checked"}, bootstrap_version=3)
        }
