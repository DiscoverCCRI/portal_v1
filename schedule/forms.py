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