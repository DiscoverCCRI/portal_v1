import logging
import uuid
from datetime import datetime
from uuid import UUID

import aerpawgw_client
from aerpawgw_client.rest import ApiException
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accounts.models import AerpawUser
from experiments.models import Experiment
from resources.models import Resource
from resources.resources import remove_units, update_units

from .models import Reservation, ReservationStatusChoice

logger = logging.getLogger(__name__)


def create_new_reservation(request, form, experiment_uuid):
    """

    :param request:
    :param form:
    :return:
    """
    reservation = Reservation()
    reservation.uuid = uuid.uuid4()
    reservation.name = form.cleaned_data.get("name")
    try:
        reservation.description = form.cleaned_data.get("description")
    except ValueError as e:
        print(e)
        reservation.description = None

    reservation.experiment = get_object_or_404(
        Experiment, uuid=UUID(str(experiment_uuid))
    )

    reservation.resource = form.cleaned_data.get("resource")
    reservation.units = form.cleaned_data.get("units")

    reservation.start_date = form.cleaned_data.get("start_date")
    reservation.end_date = form.cleaned_data.get("end_date")

    is_available = remove_units(
        reservation.resource,
        int(reservation.units),
        reservation.start_date,
        reservation.end_date,
    )
    if not is_available:
        reservation.state = ReservationStatusChoice.FAILURE.value
        print("The resource is not available at this time")
    else:
        reservation.state = ReservationStatusChoice.SUCCESS.value

    reservation.save()
    reservation.experiment.reservation_of_experiment.add(reservation)
    reservation.save()

    return str(reservation.uuid)


def update_existing_reservation(request, original_units, reservation, form):
    """
    Create new AERPAW reservation

    :param request:
    :param form:
    :return:
    """
    reservation.start_date = form.cleaned_data.get("start_date")
    reservation.end_date = form.cleaned_data.get("end_date")
    is_available = update_units(
        reservation.resource,
        int(reservation.units),
        original_units,
        reservation.start_date,
        reservation.end_date,
    )

    if not is_available:
        reservation.state = ReservationStatusChoice.FAILURE.value
        print("The resource is not available at this time")
    else:
        reservation.state = ReservationStatusChoice.SUCCESS.value

    reservation.modified_by = request.user
    reservation.modified_date = timezone.now()

    reservation.save()
    return str(reservation.uuid)


def delete_existing_reservation(request, reservation):
    """

    :param request:
    :param reservation:
    :return:
    """
    try:
        update_units(
            reservation.resource,
            0,
            int(reservation.units),
            reservation.start_date,
            reservation.end_date,
        )
        reservation.delete()
        return True
    except Exception as e:
        print(e)
        raise RuntimeError("Failed in update_units") from e
    return False


def get_reservation_list(request):
    """

    :param request:
    :return:
    """
    if request.user.is_superuser:
        reservations = Reservation.objects.order_by("name")
    else:
        experiment_id = request.session["experiment_id"]
        ex = Experiment.objects.get(id=experiment_id)
        reservations = Reservation.objects.filter(experiment=ex).order_by("name")
    return reservations


def create_new_emulab_reservation(request, reservation):
    """
    Create new reservation on Emulab

    :param request: in case we need user info later
    :param reservation:
    :return:
    """
    # create on emulab
    api_instance = aerpawgw_client.ReservationApi()
    start_timestamp = str(
        int(datetime.fromisoformat(reservation.start_date).timestamp())
    )
    end_timestamp = str(int(datetime.fromisoformat(reservation.end_date).timestamp()))
    body = aerpawgw_client.Reservation(
        type=reservation.resource.name,
        nodes=int(reservation.units),
        experiment=reservation.experiment.name,
        start=start_timestamp,
        end=end_timestamp,
    )
    logger.warning(body)
    try:
        api_response = api_instance.create_reservation(body)
        print(api_response)
    except ApiException as e:
        raise Exception("Exception when calling Gateway->create_reservation: %s\n" % e)

    # verify created reservation on emulab by querying it
    try:
        reservation_cloud_uuid = query_emulab_reservation(
            request, reservation.experiment.name, reservation.resource.name
        )
        if reservation_cloud_uuid is None:
            raise Exception("failed to query the created emulab reservation")
    except Exception as e:
        raise Exception("failed to query the created emulab reservation")


def query_emulab_reservation(request, experiment, resourcetype):
    """
    Query emulab reservation

    :param request: in case we need user info later
    :param resourcetype:
    :param experiment:
    :return emulab_reservation:
    """
    api_instance = aerpawgw_client.ReservationApi()
    try:
        # check if there is reserveration matches the experiment and resourcetype
        emulab_reservations = api_instance.get_reservation()
        for reservation in emulab_reservations:
            if (
                reservation.experiment == experiment
                and reservation.type == resourcetype
            ):
                return reservation.uuid
    except ApiException as e:
        print("Exception when calling ProfileApi->query_profile: %s\n" % e)
        raise Exception(e)

    return None


def delete_emulab_reservation(request, experiment, resourcetype):
    """
    Query emulab reservation

    :param request: in case we need user info later
    :param resourcetype:
    :param experiment:
    :return emulab_reservation:
    """
    # find the reservation and get the uuid
    try:
        reservation_cloud_uuid = query_emulab_reservation(
            request, experiment, resourcetype
        )
        if reservation_cloud_uuid is None:
            return
    except Exception as e:
        raise Exception("failed to query the created emulab reservation")
    api_instance = aerpawgw_client.ReservationApi()
    try:
        # delete reservation
        api_instance.delete_reservation(reservation_cloud_uuid)
    except ApiException as e:
        print("Exception when calling ReservationApi->delete_reservation: %s\n" % e)
    return
