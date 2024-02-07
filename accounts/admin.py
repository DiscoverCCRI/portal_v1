# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import (AerpawUserChangeForm, AerpawUserCreationForm,
                    AerpawUserSignupForm)
from .models import AerpawUser, AerpawUserSignup


class AerpawUserAdmin(UserAdmin):
    add_form = AerpawUserCreationForm
    form = AerpawUserChangeForm
    model = AerpawUser
    list_display = ["username", "email", "first_name", "last_name", "oidc_claim_sub"]


admin.site.register(AerpawUser, AerpawUserAdmin)


class AerpawUserSignupAdmin(admin.ModelAdmin):
    add_form = AerpawUserSignupForm
    form = AerpawUserSignupForm
    model = AerpawUserSignup
    list_display = ["user", "name", "title", "organization", "description", "userRole"]


admin.site.register(AerpawUserSignup, AerpawUserSignupAdmin)
