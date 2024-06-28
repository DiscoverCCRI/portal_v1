import logging
import uuid
from enum import Enum

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django_fsm import FSMIntegerField, transition

from accounts.models import AerpawUser
from profiles.models import Profile
from projects.models import Project
from resources.models import Resource, ResourceStageChoice
from django.core.validators import MaxValueValidator, MinValueValidator

logger = logging.getLogger(__name__)


"""
class StageChoice(Enum):   # A subclass of Enum
    IDLE = 'Idle'
    DEVELOPMENT = 'Development'
    SANDBOX = 'Sandbox'
    SANDBOXRequest = 'SandboxRequest'
    EMULATION = 'Emulation'
    EMULATIONRequest = 'EmulationRequest'
    TESTBED = 'Testbed'
    TESTBEDRequest = 'TestbedRequest'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class ResourceStageRequestChoice(Enum):   # A subclass of Enum
    IDLE = 'Idle'
    DEVELOPMENT = 'Development'
    SANDBOXRequest = 'SandboxRequest'
    EMULATIONRequest = 'EmulationRequest'
    TESTBEDRequest = 'TestbedRequest'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]
"""


class UserStageChoice(Enum):  # A subclass of Enum
    TESTBED = "Testbed"
    SANDBOX = "Sandbox"
    # EMULATION = 'Emulation'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class StageChoice(Enum):  # A subclass of Enum
    IDLE = "Idle"
    DEVELOPMENT = "Development"
    SANDBOX = "Sandbox"
    EMULATION = "Emulation"
    TESTBED = "Testbed"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class ReservationStatusChoice(Enum):  # A subclass of Enum
    IDLE = "Idle"
    SUCCESS = "Success"
    FAILURE = "Failure"
    RETRY = "Retry"
    EXPIRATION = "Expiration"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


# Create your models here.


class Experiment(models.Model):
    STATE_IDLE = 0
    STATE_PROVISIONING = 1
    STATE_DEPLOYING = 2
    STATE_DEPLOYED = 3
    STATE_SUBMIT = 4
    STATE_CHOICES = (
        (STATE_IDLE, "idle"),
        (STATE_PROVISIONING, "provisioning"),
        (STATE_DEPLOYING, "deploying"),
        (STATE_DEPLOYED, "ready"),
        (STATE_SUBMIT, "submitted"),
    )

    PENDING_STATUS = 0
    SCHEDULED_STATUS = 1
    COMPLETED_STATUS = 2
    ERROR_STATUS = 3
    CANCELLED_STATUS = 4
    CHOICES_STATUS = (
        (PENDING_STATUS, "Pending"),
        (SCHEDULED_STATUS, "Scheduled"),
        (COMPLETED_STATUS, "Completed"),
        (ERROR_STATUS, "Error"),
        (CANCELLED_STATUS, "Cancelled"),
    )
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    resources = models.ManyToManyField(Resource)
    dependencies = ArrayField(
        models.CharField(max_length=100, blank=True), size=20, default=list
    )
    name = models.CharField(max_length=255)
    github_link = models.CharField(max_length=255, blank=False, null=False, default="")
    cloudstorage_link = models.CharField(
        max_length=255, blank=False, null=False, default=""
    )
    execution_duration = models.IntegerField(
        default=1,
        validators=[MaxValueValidator(12), MinValueValidator(1)],
        blank=False
    )
    description = models.TextField()
    execution_condition = models.TextField(default="Weather, Time,...", blank=False)
    experimenter = models.ManyToManyField(
        AerpawUser, related_name="experiment_of_experimenter"
    )
    project = models.ForeignKey(
        Project,
        related_name="experiment_of_project",
        null=True,
        on_delete=models.SET_NULL,
    )
    created_by = models.ForeignKey(
        AerpawUser,
        related_name="experiment_created_by",
        null=True,
        on_delete=models.SET_NULL,
    )
    created_date = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(
        AerpawUser,
        related_name="experiment_modified_by",
        null=True,
        on_delete=models.SET_NULL,
    )
    modified_date = models.DateTimeField(blank=True, null=True)
    # reservations = models.ForeignKey(
    #    'reservations.Reservation', related_name='experiment_of_reservation', null=True, on_delete=models.SET_NULL
    # )
    stage = models.CharField(max_length=64, choices=StageChoice.choices())
    profile = models.ForeignKey(
        Profile,
        related_name="experiment_profile",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    is_snapshotted = models.BooleanField(default=False, blank=True, null=True)

    state = FSMIntegerField(default=0, blank=True, null=True, choices=CHOICES_STATUS)

    state_temp = FSMIntegerField(default=0, blank=True, null=True, choices=CHOICES_STATUS)

    @transition(field=state, source=STATE_IDLE, target=STATE_PROVISIONING)
    def provision(self):
        logger.warning(
            "[{}] Experiment.state : {} -> {}".format(
                self.name, self.state, Experiment.STATE_PROVISIONING
            )
        )

    @transition(
        field=state, source=[STATE_IDLE, STATE_PROVISIONING], target=STATE_DEPLOYING
    )
    def deploy(self):
        logger.warning(
            "[{}] Experiment.state : {} -> {}".format(
                self.name, self.state, Experiment.STATE_DEPLOYING
            )
        )

    @transition(
        field=state, source=[STATE_DEPLOYING, STATE_SUBMIT], target=STATE_DEPLOYED
    )
    def ready(self):
        logger.warning(
            "[{}] Experiment.state : {} -> {}".format(
                self.name, self.state, Experiment.STATE_DEPLOYED
            )
        )

    @transition(field=state, source=[STATE_IDLE, STATE_DEPLOYED], target=STATE_SUBMIT)
    def submit(self):
        logger.warning(
            "[{}] Experiment.state : {} -> {}".format(
                self.name, self.state, Experiment.STATE_SUBMIT
            )
        )

    @transition(
        field=state,
        source=[
            STATE_IDLE,
            STATE_PROVISIONING,
            STATE_DEPLOYING,
            STATE_DEPLOYED,
            STATE_SUBMIT,
        ],
        target=STATE_IDLE,
    )
    def idle(self):
        logger.warning(
            "[{}] Experiment.state : {} -> {}".format(
                self.name, self.state, Experiment.STATE_IDLE
            )
        )

    deployment_bn = models.IntegerField(blank=True, null=True)  # not being used
    message = models.TextField(blank=True, null=True)  # message from system/ops
    submit_notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "AERPAW Experiment"

    def __str__(self):
        return self.name

    def status(self):
        if self.state == Experiment.STATE_PROVISIONING:
            return "provisioning"
        elif self.state == Experiment.STATE_DEPLOYING:
            return "deploying"
        elif self.state == Experiment.STATE_DEPLOYED:
            return "ready"
        elif self.state == Experiment.STATE_SUBMIT:
            return "submitted"
        else:  # Experiment.STATE_IDLE:
            return "Idle"

    def can_initiate(self):
        if self.state == Experiment.STATE_IDLE:
            return True
        else:
            return False

    def can_terminate(self):
        if self.state != Experiment.STATE_IDLE and self.stage == "Development":
            return True
        else:
            return False

    def can_snapshot(self):
        if self.state == Experiment.STATE_DEPLOYED and self.stage == "Development":
            return True
        else:
            return False

    def can_submit(self):
        if (
            (self.stage == "Idle" or self.stage == "Development")
            and self.state != Experiment.STATE_SUBMIT
            and (
                self.is_snapshotted
                or (
                    self.state == Experiment.STATE_DEPLOYED
                    and self.stage == "Development"
                )
            )
        ):
            return True
        else:
            return False
