



# ---------------------------------------Module Visibility --------------------------------------------------------------------------------------

from django import forms
from .models import ModuleVisibility, CoreModule

class ModuleVisibilityForm(forms.ModelForm):
    class Meta:
        model = ModuleVisibility
        fields = [ 'enabled_modules']

    enabled_modules = forms.ModelMultipleChoiceField(
        queryset=CoreModule.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )


