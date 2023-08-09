import json
import logging
import os
import uuid

import aerpawgw_client
from aerpawgw_client.rest import ApiException
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from projects.models import Project
from resources.models import Resource

from .models import Profile

logger = logging.getLogger(__name__)


@login_required()
def create_new_profile(request, form):
    """

    :param request:
    :param form:
    :return:
    """
    profile = Profile()
    profile.uuid = uuid.uuid4()
    request.session["profile_uuid"] = profile.uuid
    profile.name = form.data.getlist("name")[0]

    try:
        profile.description = form.data.getlist("description")[0]
    except ValueError as e:
        print(e)
        profile.description = None

    try:
        profile.profile = form.data.getlist("profile")[0]
    except ValueError as e:
        print(e)
        profile.profile = None

    if parse_profile(request, profile.profile) is None:
        logger.warning("definition format not correct")
        return None

    profile.created_by = request.user
    profile.created_date = timezone.now()
    try:
        project_id = request.GET.get("project_id", None)
        profile.project = Project.objects.get(id=int(project_id))
    except Exception as exc:
        profile.project = None
        profile.is_template = True
    # profile.stage = form.data.getlist('stage')[0]

    """
    # user doesn't care about emulab profile.
    # we change design to always use the default 1 node profie in emulab
    # not every profile need to be sent to emulab,
    # now in is_emulab_profile(), using Stage 'DEVELOPMENT' to see if it's for emulab
    if is_emulab_profile(profile):
        create_new_emulab_profile(request, profile)
    """

    profile.save()
    try:
        profile.project.profile_of_project.add(profile)
        profile.save()
    except Exception as e:
        print(e)
        profile.project = None

    # try:
    #    reservation_id_list=form.data.getlist('reservation')
    #    if not reservation_id_list:
    #        reservation_id = reservation_id_list[0]
    #        profile.reservations = Reservation.objects.get(id=int(reservation_id))
    # except ValueError as e:
    #    print(e)
    #    profile.reservations= None
    profile.save()

    return str(profile.uuid)


@login_required()
def update_existing_profile(request, profile, form):
    """
    Create new AERPAW Profile

    :param request:
    :param form:
    :return:
    """
    try:
        profile.description = form.data.getlist("description")[0]
    except ValueError as e:
        profile.description = None
    profile.modified_by = request.user
    profile.modified_date = timezone.now()

    if parse_profile(request, profile.profile) is None:
        logger.warning("definition format not correct")
        return None

    # if is_emulab_profile(profile):
    #    delete_emulab_profile(request, profile)
    #    create_new_emulab_profile(request, profile)

    profile.save()
    return str(profile.uuid)


@login_required()
def delete_existing_profile(request, profile, experiments):
    """

    :param request:
    :param profile:
    :param experiments:
    :return:
    """
    try:
        # if is_emulab_profile(profile):
        #    delete_emulab_profile(request, profile)
        for experiment in experiments:
            experiment.delete()
        profile.delete()
        return True
    except Exception as e:
        print(e)
    return False


@login_required()
def get_profile_list(request):
    """

    :param request:
    :return:
    """
    if request.user.is_site_admin() or request.user.is_operator():
        profiles = Profile.objects.order_by("name")
    else:
        # public_projects = list(Project.objects.filter(is_public=True).values_list('id', flat=True))
        my_projects = Project.objects.filter(
            Q(project_creator=request.user)
            | Q(project_members__in=[request.user])
            | Q(project_owners__in=[request.user])
        ).values_list("id", flat=True)
        # projects = set(list(public_projects) + list(my_projects))
        profiles = (
            Profile.objects.filter(
                Q(project__in=list(my_projects)) | Q(is_template=True)
            )
            .order_by("name")
            .distinct()
        )
    return profiles


@login_required()
def parse_profile(request, experiment_definition):
    """
    Verify if resource definition is valid and return the resources as dictionary
    Currently the resource definition is provided by user with raw json file.

    :param request:
    :param experiment_definition:
    """
    try:
        logger.info(experiment_definition)
        resources = json.loads(experiment_definition)

        if len(resources) < 1:
            raise Exception("Empty definition")
        for reqnode in resources:
            if (
                "idx" not in reqnode.keys()
                or "name" not in reqnode.keys()
                or "hardware_type" not in reqnode.keys()
                or (
                    "component_id" not in reqnode.keys()
                    and "vehicle" not in reqnode.keys()
                )
            ):
                raise Exception("lacking necessary attribute(s)")

            if "component_id" in reqnode.keys():
                resource = Resource.objects.get(
                    resourceType=reqnode["hardware_type"], name=reqnode["component_id"]
                )
            elif "vehicle" in reqnode.keys():
                resource = Resource.objects.get(
                    resourceType=reqnode["hardware_type"], name=reqnode["vehicle"]
                )
            else:
                raise Exception("lacking component_id or vehicle in definition")
    except Resource.DoesNotExist:
        logger.error("!Not able to find {}".format(reqnode))
        return None
    except Exception as e:
        logger.error(e)
        return None
    return resources


def is_emulab_stage(stage):
    return False
    # not every profile need to be sent to emulab,
    # first check if we have AERPAWGW env setup,
    # and check the Stage 'DEVELOPMENT' to see if it's for emulab
    if (
        not os.getenv("AERPAWGW_HOST")
        or not os.getenv("AERPAWGW_PORT")
        or not os.getenv("AERPAWGW_VERSION")
    ):
        return False
    elif stage.upper() == "DEVELOPMENT" or stage.upper() == "EMULATION":
        return True
    else:
        return False


def is_emulab_profile(profile):
    if not profile.profile.startswith("[{") and is_emulab_stage(profile.stage):
        return True
    else:
        return False


def query_emulab_profile(request, emulab_profile_name):
    """
    Query emulab profile

    :param request: in case we need user info later
    :param emulab_profile_name:
    :return emulab_profile:
    """
    api_instance = aerpawgw_client.ProfileApi()
    logger.info(emulab_profile_name)
    try:
        # query specific profile
        emulab_profile = api_instance.query_profile(profile=emulab_profile_name)
        logger.info(emulab_profile)
        return emulab_profile
    except ApiException as e:
        logger.error("Exception when calling ProfileApi->query_profile: %s\n" % e)
        return None


def create_new_emulab_profile(request, profile):
    """
    Create new Profile on Emulab

    :param request: in case we need user info later
    :param profile:
    :return:
    """
    emulab_profile_name = get_emulab_profile_name(profile.project.name, profile.name)

    # create on emulab
    api_instance = aerpawgw_client.ProfileApi()
    body = aerpawgw_client.Profile(name=emulab_profile_name, script=profile.profile)
    logger.debug(body)
    try:
        api_response = api_instance.create_profile(body)
    except ApiException as e:
        raise Exception("Exception when calling Gateway->create_profile: %s\n" % e)

    # verify created profile on emulab by querying it
    try:
        profile_created = query_emulab_profile(request, emulab_profile_name)
        if profile_created is None:
            raise Exception("failed to query the created emulab profile")
    except Exception as e:
        raise Exception("failed to query the created emulab profile")


def delete_emulab_profile(request, profile, name_to_delete=None):
    """
    Delte profile in emulab cloud

    :param request: in case we need user info later
    :param profile:
    :param name_to_delete: in case of user updates the name in profile,
                            we will need to use the oldnname to delete
    :return
    """
    if name_to_delete is None:
        emulab_profile_name = get_emulab_profile_name(
            profile.project.name, profile.name
        )
    else:
        emulab_profile_name = get_emulab_profile_name(
            profile.project.name, name_to_delete
        )
    api_instance = aerpawgw_client.ProfileApi()
    try:
        # delete profile
        api_instance.delete_profile(emulab_profile_name)
    except ApiException as e:
        logger.error("Exception when calling ProfileApi->delete_profile: %s\n" % e)


def get_emulab_profile_name(projectname, profilename):
    return "{}-{}".format(projectname, profilename)
