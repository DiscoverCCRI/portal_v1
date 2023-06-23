from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from enum import Enum
import uuid, os

from accounts.models import AerpawUser

User = get_user_model()

class ResourceStageChoice(Enum):   # A subclass of Enum
    IDLE = 'Idle'
    DEVELOPMENT = 'Development'
    SANDBOX = 'Sandbox'
    EMULATION = 'Emulation'
    TESTBED = 'Testbed'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class ResourceTypeChoice(Enum):   # A subclass of Enum
    CLOUD = 'Cloud'
    SANDBOX = 'Sandbox'
    DRONE = 'Drone'
    ROVER = 'Rover'
    STATIONARY = 'Stationary'
    OTHERS = 'Others'
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class ResourceLocationChoice(Enum):   # A subclass of Enum
    NAUCORE = "NAU Core"
    HATRANCH = "Hat Ranch"
    NAVAJO_TECH = "Navajo Tech"
    CLEMSON = "Clemson"
    #RENCIEMULAB = 'RENCIEmulab'   # need correspondent entry in .env for the urn
    OTHERS = 'Others'
    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

# Create your models here.
class Resource(models.Model):
    admin=models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)

    capabilities = ArrayField( models.CharField( max_length = 50, blank = True ),
                                                 size = 10, default = list )

    name=models.CharField(max_length=32)
    description = models.TextField()
    resourceType=models.CharField(
      max_length=64,
      choices=ResourceTypeChoice.choices(),
    )

    units=models.PositiveSmallIntegerField(default=1) #total units in inventory.
    availableUnits=models.PositiveSmallIntegerField(default=1) #current available units.
    location=models.CharField(
      max_length=64,
      choices=ResourceLocationChoice.choices(),
    )
    locationURL = models.URLField(max_length = 300, default="https://www.google.com/maps/d/u/0/viewer?mid=1kgubHXowj8c08ZAUqjlIMpbmugo&hl=en&ll=35.18135920444196%2C-111.64538796598629&z=16")

    stage=models.CharField(
      max_length=64,
      choices=ResourceStageChoice.choices(),
    )

    created_date=models.DateTimeField(default=timezone.now)
    ip_address = models.TextField(null=True)
    hostname = models.TextField(null=True)

    @property
    def reservation_btn_title(self):
      if self.is_available():
        return "Reserve"
      else:
        return "Can not reserve"


    def __str__(self):
      return self.name

    def is_units_available(self):
      return (self.units > 0)

    def is_units_available_reservation(self, count):
      return (self.units - count > 0)

    def is_correct_stage(self,stage):
      return (stage == self.stage)

    def get_resource_stage(self):
      return self.stage
    
    def save( self, *args, **kwargs ):
      resource_map = {
        "NAU Core" : os.getenv('DISCOVER_NAU_CORE_MAP'),
        "Hat Ranch" : os.getenv('DISCOVER_HAT_RANCH_MAP'),
        "Navajo Tech" : os.getenv('DISCOVER_NAVAJO_TECH_MAP'),
        "Clemson" : os.getenv('DISCOVER_CLEMSON_MAP'),
        "Others" : os.getenv('DISCOVER_OTHERS_MAP'),
      }

      self.locationURL = resource_map[ self.location ]
      
      super().save(*args, **kwargs )
