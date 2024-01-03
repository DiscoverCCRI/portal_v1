# Register your models here.

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from accounts.models import AerpawUser

from .forms import ExperimentAdminForm, ExperimentCreateForm
from .models import Experiment


class AerpawExperimentAdmin(admin.ModelAdmin):
    # fields = ('description', 'stage', 'created_by', 'created_date','project')
    # add_form = ExperimentAdminForm
    # form = ExperimentAdminForm
    model = Experiment
    # list_display = ['name', 'description', 'stage', 'created_by', 'created_date','project']


admin.site.register(Experiment, AerpawExperimentAdmin)
