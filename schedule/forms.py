from django import forms
from resources.models import ResourceLocationChoice

class ScheduleForm(forms.Form):
    scheduled_time = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    location = forms.ChoiceField(
        choices=ResourceLocationChoice.choices(),
        widget=forms.Select(),
        required=False,
        label="Site",
    )

    experiment_name = forms.CharField(
        widget=forms.TextInput(attrs={"size": 60}),
        required=True,
        label="Search",
    )