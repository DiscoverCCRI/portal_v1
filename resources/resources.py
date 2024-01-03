import logging
import os
import sys
import uuid
from datetime import datetime, timedelta

import aerpawgw_client
import pytz
from aerpawgw_client.rest import ApiException
from django.db.models import Q
from django.utils import timezone

from accounts.models import AerpawUser
from reservations.models import Reservation, ReservationStatusChoice

from .models import Resource

logger = logging.getLogger(__name__)


def create_new_resource(request, form):
    """

    :param request:
    :param form:
    :return:
    """
    resource = Resource()
    resource.uuid = uuid.uuid4()
    resource.name = form.data.getlist("name")[0]
    try:
        resource.description = form.data.getlist("description")[0]
    except ValueError as e:
        print(e)
        resource.description = None

    resource.resourceType = form.data.getlist("resourceType")[0]

    resource.capabilities = form.data.getlist("capabilities")

    resource.units = form.data.getlist("units")[0]

    resource.location = form.data.getlist("location")[0]

    try:
        resource.ip_address = form.data.getlist("ip_address")[0]
    except ValueError as e:
        print(e)
        resource.ip_address = None

    try:
        resource.hostname = form.data.getlist("hostname")[0]
    except ValueError as e:
        print(e)
        resource.hostname = None

    resource.save()
    return str(resource.uuid)


def update_existing_resource(request, resource, form):
    """
    Create new AERPAW resource

    :param request:
    :param form:
    :return:
    """
    resource.name = form.data.getlist("name")[0]
    try:
        resource.description = form.data.getlist("description")[0]
    except ValueError as e:
        print(e)
        resource.description = None

    resource.resourceType = form.data.getlist("resourceType")[0]

    resource.units = form.data.getlist("units")[0]

    resource.location = form.data.getlist("location")[0]
    resource.modified_by = request.user
    resource.modified_date = timezone.now()

    try:
        resource.ip_address = form.data.getlist("ip_address")[0]
    except ValueError as e:
        print(e)
        resource.ip_address = None

    try:
        resource.hostname = form.data.getlist("hostname")[0]
    except ValueError as e:
        print(e)
        resource.hostname = None

    resource.save()
    return str(resource.uuid)


def get_filtered_resource(capabilities):
    """
    param - request: A map with filtering information
    request fields: capabilities( Array of strings )

    return - Resources matching the filtered request
    """
    matchedResources = []

    resources = Resource.objects

    if len(capabilities) > 0:
        for resource in resources:
            if resource.capabilities == capabilities:
                matchedResources.append(resource)
        return matchedResources
    else:
        return resources


def delete_existing_resource(request, resource):
    """

    :param request:
    :param resource:
    :return:
    """
    try:
        resource.delete()
        return True
    except Exception as e:
        print(e)
    return False


def get_resource_list(request):
    """

    :param request:
    :return:
    """
    if request.user.is_superuser:
        resources = Resource.objects.order_by("name")
    else:
        resources = Resource.objects.order_by("name")
    return resources


def get_reserved_resource(start_time, end_time):
    resources = Resource.objects.order_by("name")
    resource_units = {}
    for resource in resources:
        reserved_units = get_reserved_units(resource, start_time, end_time)
        available_units = resource.units - reserved_units
        units = []
        units.append(reserved_units)
        units.append(available_units)
        resource_units[resource.uuid] = units
    return resource_units


def get_all_reserved_units(term, delta):
    start_time = datetime.today()
    all_units = {}
    for i in range(term):
        end_time = start_time + timedelta(hours=delta)
        reserved_units = get_reserved_resource(start_time, end_time)
        start_time = end_time
        all_units[i] = reserved_units
    return all_units


def is_resource_available_time(resource, start_time, end_time):
    if not resource.is_units_available():
        return False

    reserved_units = get_reserved_units(resource, start_time, end_time)
    return resource.is_units_available_reservation(reserved_units)


def get_reserved_units(resource, start, end):
    qs0 = Reservation.objects.filter(state=ReservationStatusChoice.SUCCESS.value)
    qs1 = qs0.filter(start_date__lte=end)
    qs2 = qs1.filter(end_date__gte=end)
    qs3 = qs2.filter(resource=resource)
    units = 0
    for rs in qs3:
        units += rs.units
    return units


def update_units(
    resource, updated_units, original_units, start_time, end_time, save=True
):
    count = updated_units - original_units
    return remove_units(resource, count, start_time, end_time)


def remove_units(resource, count, start_time, end_time, save=True):
    is_resource_available = is_resource_available_time(resource, start_time, end_time)
    if is_resource_available or count < 0:
        # start_date = datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S.%f%z')
        # end_date = datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S.%f%z')
        # utc=pytz.UTC
        count_date = timezone.now() + timezone.timedelta(hours=2)
        # count_date = count_date.replace(tzinfo=utc)

        if start_time <= count_date:
            reserved_units = get_reserved_units(resource, start_time, end_time)
            resource.availableUnits = resource.units - reserved_units - count
        if save == True:
            resource.save()
    return True


def import_cloud_resources(request):
    """
    Import cloud resources to portal

    :param request:
    :param form:
    :return:
    """
    if (
        not os.getenv("AERPAWGW_HOST")
        or not os.getenv("AERPAWGW_PORT")
        or not os.getenv("AERPAWGW_VERSION")
    ):
        return

    total_cloud_resources = {}
    avail_cloud_resources = {}
    try:
        emulab_resources = get_emulab_resource_list(request)
        logger.info("parsing emulab resources:")
        for emulab_node in emulab_resources:
            end_index = emulab_node.component_id.find(
                "node"
            )  # "urn:publicid:IDN+exogeni.net+node+pc1"
            location_urn = emulab_node.component_id[: end_index - 1]
            location = emulab_urn_to_location(location_urn)
            key = location + "," + emulab_node.type
            logger.warning(
                "component_name = {}, location_urn = {}, key = {}, available = {}".format(
                    emulab_node.component_name, location_urn, key, emulab_node.available
                )
            )

            if key in total_cloud_resources:
                total_cloud_resources[key] += 1
                if emulab_node.available is True:
                    avail_cloud_resources[key] += 1
            else:
                total_cloud_resources[key] = 1
                if emulab_node.available is True:
                    avail_cloud_resources[key] = 1
                else:
                    avail_cloud_resources[key] = 0

        logger.warning("total_cloud_resources:{}".format(total_cloud_resources))
        logger.warning("avail_cloud_resources:{}".format(avail_cloud_resources))
        logger.warning(
            "portal should calculate the available counts by reservation, "
            + "the avail_cloud_resources returned by emulab should just be reference \n"
        )

        # create or update resources in database
        for key in total_cloud_resources.keys():
            create_or_update_cloud_resource(
                request,
                key.split(",")[0],
                key.split(",")[1],
                total_cloud_resources[key],
                avail_cloud_resources[key],
            )
    except:
        logger.error("Import Emulab resource error", sys.exc_info()[0])

    # delete resources if they are no longer on emulab
    existing_resources = get_resource_list(request)
    for resource in existing_resources:
        key = resource.location + "," + resource.name
        if (
            resource.description == "Emulab nodes"
            and resource.resourceType.upper() == "CLOUD"
            and key not in total_cloud_resources.keys()
        ):
            logger.warning(
                "Emulab resource '{}' no longer exists, deleting it".format(
                    resource.name
                )
            )
            delete_existing_resource(request, resource)


def create_or_update_cloud_resource(request, location, name, units, avail_units):
    """

    :param request:
    :param location:
    :param name:
    :param units:
    :param avail_units:
    :return:
    """

    existing_resources = get_resource_list(request)
    for resource in existing_resources:
        if resource.name == name and resource.location == location:
            if resource.units != units:
                # resource.availableUnits = avail_units # portal calculates its own avail_units
                resource.units = units
                resource.modified_date = timezone.now()
                resource.save()
                logger.warning("Emulab resource '{}' is updated".format(resource.name))
            return
    # there was no such resource, let's create a new one
    newresource = Resource()
    newresource.uuid = uuid.uuid4()
    newresource.name = name
    newresource.description = "Emulab nodes"
    newresource.units = units
    newresource.availableUnits = avail_units
    newresource.resourceType = "Cloud"
    newresource.stage = "Development"
    newresource.location = location
    newresource.save()
    logger.warning("Emulab resource '{}' is created".format(newresource.name))
    return


def get_emulab_resource_list(request):
    """
    Query emulab resource

    :param request: in case we need user info later
    :return emulab_resources:
    """
    api_instance = aerpawgw_client.ResourcesApi()
    try:
        # list resources
        api_response = api_instance.list_resources()
        logger.info(api_response)
        return api_response.nodes
    except ApiException as e:
        logger.error("Exception when calling ResourcesApi->list_resources: %s\n" % e)
        raise Exception(e)


def emulab_location_to_urn(location):
    if location == "RENCIEmulab":
        return os.getenv("URN_RENCIEMULAB")
    else:
        raise Exception("unknown location")


def emulab_urn_to_location(urn):
    if urn == os.getenv("URN_RENCIEMULAB"):
        return "RENCIEmulab"
    else:
        raise Exception("unknown urn")
