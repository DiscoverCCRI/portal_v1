# comanage/management/commands/comanage_sync_on_startup.py

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from experiments.models import Experiment
from profiles.models import Profile


class Command(BaseCommand):
    help = "Remove orphaned Experiments and Experiment Resource Definitions"

    def handle(self, *args, **kwargs):
        try:
            print(
                "### Remove orphaned Experiments and Experiment Resource Definitions ###"
            )
            experiments = Experiment.objects.filter(
                Q(project_id=None) | Q(profile_id=None)
            )
            profiles = Profile.objects.filter(Q(project_id=None))
            for exp in experiments:
                print("[DELETE]: ", exp.name, exp.project, exp.profile, exp.created_by)
                exp.delete()
            for pro in profiles:
                print("[DELETE]: ", pro.name, pro.project, pro.created_by)
                pro.delete()

        except Exception as e:
            print(e)
            raise CommandError("Initalization failed.")
