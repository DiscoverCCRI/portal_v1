# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import AerpawUser, AerpawUserSignup, AerpawRoleRequest, AerpawUserRoleChoice


class AerpawUserCreationForm(UserCreationForm):
    class Meta:
        model = AerpawUser
        fields = ('username', 'email', 'first_name', 'last_name', 'oidc_claim_sub')


class AerpawUserChangeForm(UserChangeForm):
    class Meta:
        model = AerpawUser
        fields = ('username', 'email', 'first_name', 'last_name', 'oidc_claim_sub')


class AerpawUserSignupForm(forms.ModelForm):
    class Meta:
        model = AerpawUserSignup
        fields = ('user', 'name', 'title', 'organization', 'description', 'userRole')

class AerpawRoleRequestForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AerpawRoleRequestForm, self).__init__(*args, **kwargs)
        self.fields['purpose'].label = "Purpose of request?"
        all_choices = AerpawUserRoleChoice.choices()
        cur_roles = self.user.groups.all()
        # per GH issue #85 - hide administrative roles from dropdown list
        cur_role_list = ['site_admin', 'operator', 'resource_manager', 'user_manager']
        for role in cur_roles:
            cur_role_list.append(str(role))
        display_choices = [('', '--------')]
        for ch in all_choices:
            if str(ch[0]) not in cur_role_list:
                display_choices.append(ch)
        display_choices.sort()
        self.fields['requested_role'].choices = display_choices

    class Meta:
        model = AerpawRoleRequest
        fields = (
            'requested_role',
            'purpose'
        )

    requested_role = forms.ChoiceField(
        widget=forms.Select,
        label='Requested Role'
    )
