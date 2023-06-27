from django import forms

from accounts.models import AerpawUser
from projects.models import Project
from reservations.models import Reservation
from .models import Resource,ResourceStageChoice,ResourceTypeChoice,ResourceLocationChoice

class ResourceCreateForm(forms.ModelForm):

    capabilities = [ ('gimbal','Gimbal and RGB/IR Camera'), ('lidar','LIDAR'), 
                 ('jetson', 'Jetson Nano'), ('sdr', 'Software Defined Radio'), 
                 ('5g', '5G module(s)'),
                 ('camera','Camera'), ('gps','GPS'),
                 ('t12','TEROS-12' ), ('t21','TEROS-21'), 
                 ('tts', 'Thermistor Temperature Sensor'), 
                 ('tsl259','TSL25911FN'),('bme', 'BME280'), 
                 ('icm', 'ICM20948'), ('ltr', 'LTR390-UV-1' ),
                 ('sgp', 'SGP40' ), ('cws', 'Compact Weather Sensor') ]
 
    name = forms.CharField(
        widget=forms.TextInput(attrs={'size': 60}),
        required=True,
        label='Resource Name',
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=False,
        label='Resource Description',
    )

    resourceType = forms.ChoiceField(
        choices=ResourceTypeChoice.choices(),
        widget=forms.Select(),
        required=False,
        label='Resource Type',
    )

    capabilities = forms.MultipleChoiceField(
        required = False,
        widget = forms.CheckboxSelectMultiple(),
        choices = capabilities,
    )

    units = forms.IntegerField(
        required=True,
        initial=0,
        widget=forms.NumberInput(),
        label='Resource Units',
    )

    location = forms.ChoiceField(
        choices=ResourceLocationChoice.choices(),
        widget=forms.Select(),
        required=False,
        label='Resource Location',
    )

    stage = forms.ChoiceField(
        choices=ResourceStageChoice.choices(),
        widget=forms.Select(),
        required=False,
        label='Resource Stage',
    )

    ip_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1, 'cols': 20}),
        required=False,
        label='IP Address',
    )

    hostname = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1, 'cols': 20}),
        required=False,
        label='Hostname',
    )

    class Meta:
        model = Resource
        fields = [
            'name',
            'description',
            'resourceType',
            'capabilities',
            'units',
            'availableUnits',
            'location',
            'stage',
            'created_date',
            'ip_address',
            'hostname'
        ]


class ResourceChangeForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'size': 60}),
        required=True,
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=False,
        label='Resource Description',
    )

    resourceType = forms.ChoiceField(
        choices=ResourceTypeChoice.choices(),
        widget=forms.Select(),
        required=True,
        label='Resource Type',
    )

    units = forms.IntegerField(
        required=True,
        initial=0,
        widget=forms.NumberInput(),
        label='Resource Units',
    )

    location = forms.ChoiceField(
        choices=ResourceLocationChoice.choices(),
        widget=forms.Select(),
        required=True,
        label='Resource Location',
    )

    stage = forms.ChoiceField(
        choices=ResourceStageChoice.choices(),
        widget=forms.Select(),
        required=True,
        label='Resource Stage',
    )

    class Meta:
        model = Resource
        fields = '__all__'
