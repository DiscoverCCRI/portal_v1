from accounts.models import AerpawUser
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import Project, ProjectRequest

JOIN_CHOICES = (
    ("1", "Project Member"),
    ("2", "Project Owner"),
)


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "is_public"]


class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "is_public")


class ProjectJoinForm(forms.Form):
    member_type = forms.ChoiceField(choices=JOIN_CHOICES, label="Request to be a")
    message = forms.CharField(widget=forms.Textarea, required=True)


class ProjectUpdateMembersForm(forms.ModelForm):
    project_members = forms.ModelMultipleChoiceField(
        queryset=AerpawUser.objects.all()
        .exclude(username="admin")
        .order_by("display_name"),
        widget=FilteredSelectMultiple("Members", is_stacked=False),
        required=False,
    )

    class Media:
        extend = False
        css = {"all": ["admin/css/widgets.css"]}
        js = (
            "js/django_global.js",
            "admin/js/jquery.init.js",
            "admin/js/core.js",
            "admin/js/prepopulate_init.js",
            "admin/js/prepopulate.js",
            "admin/js/SelectBox.js",
            "admin/js/SelectFilter2.js",
            "admin/js/admin/RelatedObjectLookups.js",
        )

    class Meta:
        model = Project
        fields = ["project_members"]


class ProjectUpdateOwnersForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        super(ProjectUpdateOwnersForm, self).__init__(*args, **kwargs)
        self.pm = Project.objects.filter(uuid=self.project.uuid).values_list(
            "project_members", flat=True
        )
        self.fields["project_owners"] = forms.ModelMultipleChoiceField(
            queryset=AerpawUser.objects.filter(id__in=list(self.pm)).order_by(
                "display_name"
            ),
            widget=FilteredSelectMultiple("Owners", is_stacked=False),
            required=False,
        )

    class Media:
        extend = False
        css = {"all": ["admin/css/widgets.css"]}
        js = (
            "js/django_global.js",
            "admin/js/jquery.init.js",
            "admin/js/core.js",
            "admin/js/prepopulate_init.js",
            "admin/js/prepopulate.js",
            "admin/js/SelectBox.js",
            "admin/js/SelectFilter2.js",
            "admin/js/admin/RelatedObjectLookups.js",
        )

    class Meta:
        model = Project
        fields = ["project_owners"]


class ProjectRequestForm(forms.ModelForm):
    class Meta:
        model = ProjectRequest
        fields = ("name", "description", "is_public")
