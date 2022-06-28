import uuid

from django.db import models
from django.utils import timezone

from accounts.models import AerpawUser
from projects.models import Project
from resources.models import ResourceStageChoice


class Profile(models.Model):
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_template = models.BooleanField(default=False)

    project = models.ForeignKey(
        Project, related_name='profile_of_project', default=None, null=True, on_delete=models.SET_NULL
    )

    profile = models.TextField()

    created_by = models.ForeignKey(
        AerpawUser, related_name='profile_created_by', null=True, on_delete=models.SET_NULL
    )
    created_date = models.DateTimeField(default=timezone.now)

    modified_by = models.ForeignKey(
        AerpawUser, related_name='profile_modified_by', null=True, on_delete=models.SET_NULL
    )
    modified_date = models.DateTimeField(blank=True, null=True)

    # reservations = models.ForeignKey(
    #    'reservations.Reservation', related_name='experiment_of_reservation', null=True, on_delete=models.SET_NULL
    # )

    stage = models.CharField(
        max_length=64,
        choices=ResourceStageChoice.choices(),
    )

    class Meta:
        verbose_name = 'AERPAW Profile'

    def __str__(self):
        return self.name
