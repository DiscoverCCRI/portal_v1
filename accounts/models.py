# accounts/models.py

# import files
from enum import Enum
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

import uuid


# class AerpawUserRoleChoice(Enum):  # A subclass of Enum
#     ADMIN = 'Admin'
#     PI = 'PI'
#     LEADEXPERIMENTER = 'Lead Experimenter'
#     EXPERIMENTER = 'Experimenter'
#     OBSERVERS = 'Observers'
#
#     @classmethod
#     def choices(cls):
#         return [(key.value, key.name) for key in cls]

# DISCOVER User Roles
class AerpawUserRoleChoice(Enum):  # A subclass of Enum
    # Roles
    site_admin = 'Administrator'
    operator = 'Operator'
    project_manager = 'Principal Investigator (PI)'
    resource_manager = 'Resource Manager'
    user_manager = 'User Role Manager'
    aerpaw_user = 'Discover User'

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]


# Extends basic User model: https://docs.djangoproject.com/en/3.1/ref/contrib/auth/
class AerpawUser(AbstractUser):
    # universal unique identifier for user within infrastructure
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    display_name = models.CharField(max_length=255)

    # oidc scope openid
    oidc_claim_sub = models.CharField(max_length=255)
    oidc_claim_iss = models.CharField(max_length=255)
    oidc_claim_aud = models.CharField(max_length=255)
    oidc_claim_token_id = models.CharField(max_length=255)

    # oidc scope email
    oidc_claim_email = models.CharField(max_length=255)

    # oidc scope profile
    oidc_claim_given_name = models.CharField(max_length=255)
    oidc_claim_family_name = models.CharField(max_length=255)
    oidc_claim_name = models.CharField(max_length=255)

    # oidc scope org.cilogon.userinfo
    oidc_claim_idp = models.CharField(max_length=255)
    oidc_claim_idp_name = models.CharField(max_length=255)
    oidc_claim_eppn = models.CharField(max_length=255)
    oidc_claim_eptid = models.CharField(max_length=255)
    oidc_claim_affiliation = models.CharField(max_length=255)
    oidc_claim_ou = models.CharField(max_length=255)
    oidc_claim_oidc = models.CharField(max_length=255)
    oidc_claim_cert_subject_dn = models.CharField(max_length=255)

    # oidc other values
    oidc_claim_acr = models.CharField(max_length=255)
    oidc_claim_entitlement = models.CharField(max_length=255)

    def __str__(self):
        return str(self.display_name)

    def is_aerpaw_user(self):
        return self.groups.filter(name='aerpaw_user').exists()

    def is_operator(self):
        return self.groups.filter(name='operator').exists()

    def is_project_manager(self):
        return self.groups.filter(name='project_manager').exists()

    def is_resource_manager(self):
        return self.groups.filter(name='resource_manager').exists()

    def is_user_manager(self):
        return self.groups.filter(name='user_manager').exists()

    def is_site_admin(self):
        return self.groups.filter(name='site_admin').exists()


def is_PI(user):
    print(user)
    print(user.groups.all())
    return user.groups.filter(name='project_manager').exists()


def is_project_member(user, project_group):
    print(user)
    print(user.groups.all())
    return user.groups.filter(name=project_group).exists()

# DISCOVER User Signup (CILogon)
# Model stores user information from CILogon
class AerpawUserSignup(models.Model):
    # Attributes
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(AerpawUser, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    description = models.TextField()
    userRole = models.CharField(
        max_length=64,
        choices=AerpawUserRoleChoice.choices(),
    )

    # class method
    def __str__(self):
        return self.user.oidc_claim_email

# DISCOVER Role Request
# 
class AerpawRoleRequest(models.Model):
    # User = get_user_model()
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    requested_by = models.ForeignKey(
        AerpawUser, related_name='role_request_requested_by', on_delete=models.CASCADE, null=True, blank=True
    )
    purpose = models.TextField()
    is_approved = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    notes = models.TextField()
    requested_role = models.CharField(
        max_length=64,
        choices=AerpawUserRoleChoice.choices(),
    )
    created_by = models.ForeignKey(
        AerpawUser, related_name='role_request_created_by', on_delete=models.CASCADE, null=True, blank=True
    )
    created_date = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(
        AerpawUser, related_name='role_request_modified_by', on_delete=models.CASCADE, null=True, blank=True
    )
    modified_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.requested_by

# DISCOVER signup new user
def create_new_signup(request, form):
    """

    :param request:
    :param form:
    :return:
    """

    signup = AerpawUserSignup()
    signup.uuid = uuid.uuid4()
    signup.user = request.user
    signup.name = form.data.getlist('name')[0]
    signup.title = form.data.getlist('title')[0]
    signup.organization = form.data.getlist('organization')[0]
    try:
        signup.description = form.data.getlist('description')[0]
    except ValueError as e:
        print(e)
        signup.description = None

    signup.userRole = form.data.getlist('userRole')[0]
    request.user.save()
    signup.save()

    return str(signup.uuid)
