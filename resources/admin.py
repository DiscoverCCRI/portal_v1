
# Register your models here.

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import ResourceCreateForm, ResourceChangeForm
from .models import Resource,ResourceTypeChoice,ResourceStageChoice


class AerpawResourceAdmin(admin.ModelAdmin):
    add_form = ResourceCreateForm
    form = ResourceCreateForm
    model = Resource
    list_display = ['name', 'description', 'resourceType', 'units', 'availableUnits','location', 'stage','admin']


admin.site.register(Resource, AerpawResourceAdmin)