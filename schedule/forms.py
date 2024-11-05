from django import forms
from resources.models import ResourceLocationChoice

class ScheduleForm(forms.Form):
    scheduled_time = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Schedule Time"
    )

    experiment_uuid = forms.UUIDField(
        widget=forms.HiddenInput()
    )

class LocationFilterForm(forms.Form):
    location = forms.ChoiceField(
        choices=ResourceLocationChoice.choices(),
        widget=forms.Select(attrs={'class': 'form-select w-70'}),
        required=False,
        label="Site",
    )

class ExperimentSearchForm(forms.Form):
    experiment_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "size": 50,
                "placeholder": "Searching..."
        }),
        required=False,
        label="Search",
    )
