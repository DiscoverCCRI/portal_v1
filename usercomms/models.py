import uuid

from accounts.models import AerpawUser
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Usercomms(models.Model):
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    reference_url = models.URLField(null=True, blank=True)
    reference_note = models.TextField(null=True, blank=True)
    reference_user = models.ForeignKey(
        User, related_name='usercomms_reference_user', on_delete=models.CASCADE, null=True, blank=True
    )
    sender = models.ForeignKey(
        User, related_name='usercomms_sender', on_delete=models.CASCADE, null=True, blank=True
    )
    receivers = models.ManyToManyField(
        User, related_name='usercoms_receivers'
    )
    is_hidden = models.BooleanField(default=False)
    is_removed = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, related_name='usercomms_created_by', on_delete=models.CASCADE, null=True, blank=True
    )
    created_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'AERPAW User Communications'

    def __str__(self):
        return u'{0}'.format(self.subject)
