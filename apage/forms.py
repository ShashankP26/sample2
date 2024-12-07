from django import forms
from .models import GeneralReport

class GeneralReportForm(forms.ModelForm):
    class Meta:
        model = GeneralReport
        fields = ['site', 'date_of_visit', 'point1', 'point2', 'point3', 'point4', 'notes', 'attachment']
        widgets = {
            'date_of_visit': forms.DateInput(attrs={'type': 'date'}),
        }
