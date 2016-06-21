from django import forms
from .models import Site, COURSE_TYPE_CHOICES

class SiteForm(forms.ModelForm):
    #site_type = forms.CharField(max_length=255, help_text="Type of site, enter 'General' if unsure.")
    #name = forms.CharField(max_length=255)
    #url = forms.URLField(max_length=255, required=True)
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
        #fields = ['site_type','name','url','course_count','last_checked','org_type','language','geography',
        #          'github_fork','notes','course_type','registered_user_count','active_learner_count']
