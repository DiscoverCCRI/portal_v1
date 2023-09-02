import uuid
from json import JSONEncoder
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from accounts.models import AerpawUser

JSONEncoder_olddefault = JSONEncoder.default


def JSONEncoder_newdefault(self, o):
    if isinstance(o, UUID): return str(o)
    return JSONEncoder_olddefault(self, o)


JSONEncoder.default = JSONEncoder_newdefault

User = get_user_model()


class Project(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField()
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    is_public = models.BooleanField(default=False)
    project_creator = models.ForeignKey(
        AerpawUser, related_name='project_creator', on_delete=models.CASCADE
    )
    project_owners = models.ManyToManyField(
        AerpawUser, related_name='project_owners'
    )
    project_members = models.ManyToManyField(
        AerpawUser, related_name='project_members'
    )
    created_by = models.ForeignKey(
        User, related_name='project_created_by', on_delete=models.CASCADE, null=True, blank=True
    )
    created_date = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(
        User, related_name='project_modified_by', on_delete=models.CASCADE, null=True, blank=True
    )
    modified_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'AERPAW Project'

    # def __str__(self):
    #     return self.name

    def __str__(self):
        return u'{0}'.format(self.name)


class ProjectMembershipRequest(models.Model):
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    project_uuid = models.CharField(max_length=255)
    requested_by = models.ForeignKey(
        AerpawUser, related_name='project_membership_requested_by', on_delete=models.CASCADE, null=True, blank=True
    )
    message = models.TextField()
    is_approved = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    notes = models.TextField()
    member_type = models.CharField(
        max_length=64,
    )
    created_by = models.ForeignKey(
        AerpawUser, related_name='project_membership_request_created_by', on_delete=models.CASCADE, null=True, blank=True
    )
    created_date = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(
        AerpawUser, related_name='project_membership_request_modified_by', on_delete=models.CASCADE, null=True, blank=True
    )
    modified_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.requested_by


class ProjectRequest(models.Model):
    # User = get_user_model()
    name = models.CharField(max_length=255, blank=False, null=False)
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    requested_by = models.ForeignKey(
        AerpawUser, related_name='project_request_requested_by', on_delete=models.CASCADE, null=True, blank=True
    )
    description = models.TextField()
    is_public = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    notes = models.TextField()
    created_by = models.ForeignKey(
        AerpawUser, related_name='project_request_created_by', on_delete=models.CASCADE, null=True, blank=True
    )
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.requested_by