from django import forms

class DateTimeForm(forms.Form):
    scheduled_time = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )