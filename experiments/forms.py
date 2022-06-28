from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelChoiceField

from accounts.models import AerpawUser
from profiles.models import Profile
from projects.models import Project
from reservations.models import Reservation
from .models import Experiment, UserStageChoice, StageChoice
from django.db.models import Q


class ExperimentModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        erd_name = None
        erd_project = 'TEMPLATE'
        if obj.name:
            erd_name = obj.name
        if obj.project:
            erd_project = obj.project.name
        return '{0} ({1})'.format(erd_name, erd_project)


class ExperimentCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.project_id = kwargs.pop('project_id', None)
        super(ExperimentCreateForm, self).__init__(*args, **kwargs)
        # self.public_projects = list(Project.objects.filter(is_public=True).values_list('id', flat=True))
        # if self.project_id not in self.public_projects:
        #     self.public_projects.append(self.project_id)
        self.profiles = Profile.objects.filter(Q(project_id=int(self.project_id)) |
                                               Q(is_template=True)).order_by('name').distinct()
        self.fields['profile'] = ExperimentModelChoiceField(
            queryset=self.profiles,
            required=True,
            widget=forms.Select(),
            label='Experiment Resource Definition',
        )

    class Meta:
        model = Experiment
        fields = [
            'name',
            'description',
            'profile'
        ]


class ExperimentUpdateExperimentersForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # self.experimenter = kwargs.pop('experimenter')
        super(ExperimentUpdateExperimentersForm, self).__init__(*args, **kwargs)
        exp = kwargs.get('instance')
        project = Project.objects.get(id=int(exp.project_id))
        self.fields['experimenter'].queryset = (project.project_owners.all() | project.project_members.all()).distinct()

    class Media:
        extend = False
        css = {
            'all': [
                'admin/css/widgets.css'
            ]
        }
        js = (
            'js/django_global.js',
            'admin/js/jquery.init.js',
            'admin/js/core.js',
            'admin/js/prepopulate_init.js',
            'admin/js/prepopulate.js',
            'admin/js/SelectBox.js',
            'admin/js/SelectFilter2.js',
            'admin/js/admin/RelatedObjectLookups.js',
        )

    class Meta:
        model = Experiment
        fields = [
            'experimenter'
        ]

    experimenter = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=FilteredSelectMultiple("Experimenters", is_stacked=False),
        required=False
    )


# class ExperimentCreateForm(forms.ModelForm):
#     experimenter = forms.ModelChoiceField(
#         queryset=AerpawUser.objects.order_by('oidc_claim_name'),
#         required=True,
#         widget=forms.Select(),
#         label='Lead Experimenter',
#     )
#
#     project = forms.ModelChoiceField(
#         queryset=Project.objects.none(),
#         required=True,
#         widget=forms.Select(),
#         label='Project',
#     )
#
#     stage = forms.ChoiceField(
#         choices=ResourceStageRequestChoice.choices(),
#         required=True,
#         widget=forms.Select(),
#         label='Stage',
#     )
#
#     profile = forms.ModelChoiceField(
#         queryset=Profile.objects.order_by('name'),
#         required=False,
#         widget=forms.Select(),
#         label='Profile',
#     )
#
#     class Meta:
#         model = Experiment
#         fields = (
#             'name',
#             'description',
#             'experimenter',
#             'project',
#             'stage',
#         )
#
#     def __init__(self, *args, **kwargs):
#         project = kwargs.pop('project', None)
#         experimenter = kwargs.pop('experimenter', None)
#         super().__init__(*args, **kwargs)
#         if project and experimenter:
#             qs = Project.objects.filter(project_members__id=experimenter.id)
#             if qs:
#                 self.fields['project'].queryset = qs
#
#             qs = AerpawUser.objects.filter(projects__id=project.id)
#             #print(qs)
#             if qs:
#                 self.fields['experimenter'].queryset = qs
#
#     def clean_title(self):
#         data = self.cleaned_data.get('name')
#         if len(data) <4:
#             raise forms.ValidationError("The name is not long enough!")
#         return data
#
#     def clean(self, *args, **kwargs):
#         cleaned_data = super().clean(*args, **kwargs)
#
#         rs=cleaned_data.get("name")
#         qs=Experiment.objects.filter(name=rs)
#         if qs.exists():
#             raise forms.ValidationError("This experiment name has been used!")
#             return redirect("/create")
#
#         return cleaned_data


class ExperimentUpdateForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'size': 60}),
        required=True,
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=False,
        label='Experiment Description',
    )

    '''
    experimenter = forms.ModelChoiceField(
        queryset=AerpawUser.objects.order_by('oidc_claim_name'),
        required=True,
        initial=0,
        widget=forms.Select(),
        label='Lead Experimenter',
    )

    experiment_reservations = forms.ModelMultipleChoiceField(
        queryset=Reservation.objects.order_by('name'),
        required=False,
        widget=forms.SelectMultiple(),
        label='Experiment Reservations',
    )

    stage = forms.ChoiceField(
        choices=UserStageChoice.choices(),
        required=True,
        widget=forms.Select(),
        label='Stage',
    )

    profile = forms.ModelChoiceField(
        queryset=Profile.objects.order_by('name'),
        required=False,
        widget=forms.Select(),
        label='Experiment Resource Definition',
    )
    '''

    class Meta:
        model = Experiment
        fields = (
            'name',
            'description',
        )


class ExperimentUpdateByOpsForm(forms.ModelForm):
    stage = forms.ChoiceField(
        choices=StageChoice.choices(),
        required=True,
        widget=forms.Select(),
        label='Mode',
    )

    state = forms.ChoiceField(
        choices=Experiment.STATE_CHOICES,
        required=True,
        widget=forms.Select(),
        label='state',
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=False,
        label='Experiment Notification',
    )

    class Meta:
        model = Experiment
        fields = (
            'stage',
            'state',
            'message',
        )


class ExperimentSubmitForm(forms.ModelForm):
    stage = forms.ChoiceField(
        choices=UserStageChoice.choices(),
        required=True,
        widget=forms.Select(),
        label='Submit to',
    )

    submit_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=False,
        label='Testbed Experiment Description\n',
        # help_text='\nsuch as "The drone will take off at an altitude of 50m and then go west 300m, then return to launch and land."'
    )

    class Meta:
        model = Experiment
        fields = (
            'stage',
            'submit_notes'
        )


class ExperimentAdminForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'size': 60}),
        required=True,
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        required=False,
        label='Experiment Description',
    )

    experimenter = forms.ModelChoiceField(
        queryset=AerpawUser.objects.order_by('oidc_claim_name'),
        required=True,
        initial=0,
        widget=forms.Select(),
        label='Lead Experimenter',
    )

    experiment_reservations = forms.ModelMultipleChoiceField(
        queryset=Reservation.objects.order_by('name'),
        required=False,
        widget=forms.SelectMultiple(),
        label='Experiment Reservations',
    )

    stage = forms.ChoiceField(
        choices=StageChoice.choices(),
        required=True,
        widget=forms.Select(),
        label='Stage',
    )

    profile = forms.ModelChoiceField(
        queryset=Profile.objects.order_by('name'),
        required=False,
        widget=forms.Select(),
        label='Profile',
    )

    class Meta:
        model = Experiment
        fields = (
            'name',
            'description',
            'experimenter',
            'modified_by',
            'modified_date',
            'stage',
            'profile',
        )
