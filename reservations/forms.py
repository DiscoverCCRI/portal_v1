from accounts.models import AerpawUser
from django import forms
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from experiments.models import Experiment
from resources.models import Resource
from resources.resources import is_resource_available_time

from .models import Reservation, one_day_hence


class ReservationCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        experiment_id = kwargs.pop("experiment_id", None)
        qs = Experiment.objects.filter(id=experiment_id)
        if not qs.exists():
            raise forms.ValidationError("There is no active experiment!")
            return redirect("/")
        self.experiment = qs.first()
        self.stage = self.experiment.stage
        super(ReservationCreateForm, self).__init__(*args, **kwargs)
        # qs = Resource.objects.filter(stage=self.stage)
        qs = Resource.objects.order_by("name")
        if qs:
            self.fields["resource"].queryset = qs

    name = forms.CharField(
        widget=forms.TextInput(attrs={"size": 60}),
        required=True,
        label="Reservation Name",
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2, "cols": 60}),
        required=False,
        label="Description(Optional)",
    )

    resource = forms.ModelChoiceField(
        queryset=Resource.objects.none(),
        required=True,
        widget=forms.Select(),
        label="Resource",
    )

    units = forms.IntegerField(
        required=True,
        initial=0,
        widget=forms.NumberInput(),
        label="Resource Units",
    )

    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"class": "datetimepicker", "value": timezone.now()}
        ),
        initial=timezone.now,
        required=True,
    )

    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"class": "datetimepicker", "value": one_day_hence()}
        ),
        initial=one_day_hence,
        required=True,
    )

    class Meta:
        model = Reservation
        fields = (
            "name",
            "description",
            "resource",
            "units",
            "start_date",
            "end_date",
        )

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        rs = cleaned_data.get("resource")
        qs = Resource.objects.filter(name=rs)
        if not qs.exists():
            return redirect("/")
        resource = qs.first()

        if not resource.is_correct_stage(self.stage):
            raise forms.ValidationError(
                "This resource is not in your experiment's stage!"
            )

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        is_available = is_resource_available_time(resource, start_date, end_date)
        if not is_available:
            raise forms.ValidationError(
                "This resource has no units avaialble for reservation at this time!"
            )

        return cleaned_data


class ReservationChangeForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={"size": 60}),
        required=True,
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 6, "cols": 60}),
        required=False,
        label="Reservation Description",
    )

    resource = forms.ModelChoiceField(
        queryset=Resource.objects.order_by("name"),
        required=False,
        widget=forms.Select(),
        label="Resource",
    )

    units = forms.IntegerField(
        required=True,
        initial=0,
        widget=forms.NumberInput(),
        label="Resource Units",
    )

    start_date = forms.DateTimeField(
        input_formats=["%Y-%m-%d %H:%M:%S.%f%z"],
        widget=forms.DateTimeInput(
            attrs={"class": "datetimepicker", "value": timezone.now()}
        ),
        initial=timezone.now,
        required=True,
    )

    end_date = forms.DateTimeField(
        input_formats=["%Y-%m-%d %H:%M:%S.%f%z"],
        widget=forms.DateTimeInput(
            attrs={"class": "datetimepicker", "value": one_day_hence()}
        ),
        initial=one_day_hence,
        required=True,
    )

    class Meta:
        model = Reservation
        fields = (
            "name",
            "description",
            "resource",
            "units",
            "start_date",
            "end_date",
            "experiment",
        )

    def clean(self, *args, **kwargs):
        cleaned_data = super().clean(*args, **kwargs)

        rs = cleaned_data.get("resource")
        qs = Resource.objects.filter(name=rs)
        if not qs.exists():
            return redirect("/")
        resource = qs.first()

        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        is_available = is_resource_available_time(resource, start_date, end_date)
        if not is_available:
            raise forms.ValidationError(
                "This resource has no units avaialble for reservation at this time!"
            )

        return cleaned_data
