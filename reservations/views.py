# Create your views here.

from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from experiments.models import Experiment

from .forms import ReservationChangeForm, ReservationCreateForm
from .models import Reservation
from .reservations import (create_new_reservation, delete_existing_reservation,
                           get_reservation_list, update_existing_reservation)


@login_required()
def reservations(request):
    """

    :param request:
    :return:
    """
    reservations = get_reservation_list(request)
    return render(request, "reservations.html", {"reservations": reservations})


@login_required()
def reservation_create(request, experiment_uuid):
    """

    :param request:
    :return:
    """
    experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))
    if request.method == "POST":
        form = ReservationCreateForm(request.POST, experiment_id=experiment.id)
        if form.is_valid():
            reservation_uuid = create_new_reservation(request, form, experiment_uuid)
            return redirect(
                "reservation_detail",
                reservation_uuid=reservation_uuid,
                experiment_uuid=experiment_uuid,
            )
    else:
        form = ReservationCreateForm(experiment_id=experiment.id)

    return render(
        request,
        "reservation_create.html",
        {
            "form": form,
            "experiment": experiment,
            "experimenter": experiment.experimenter.all(),
        },
    )


@login_required()
def reservation_detail(request, reservation_uuid, experiment_uuid):
    """

    :param request:
    :param project_uuid:
    :return:
    """
    reservation = get_object_or_404(Reservation, uuid=UUID(str(reservation_uuid)))
    experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))
    reservation_resource = reservation.resource
    return render(
        request,
        "reservation_detail.html",
        {
            "reservation": reservation,
            "experiment": experiment,
            "reservation_resource": reservation_resource,
        },
    )


@login_required()
def reservation_detail_own(request, reservation_uuid):
    """

    :param request:
    :param project_uuid:
    :return:
    """
    reservation = get_object_or_404(Reservation, uuid=UUID(str(reservation_uuid)))
    reservation_resource = reservation.resource
    return render(
        request,
        "reservation_detail.html",
        {"reservation": reservation, "reservation_resource": reservation_resource},
    )


@login_required()
def reservation_update(request, reservation_uuid):
    """

    :param request:
    :param reservation_uuid:
    :return:
    """
    reservation = get_object_or_404(Reservation, uuid=UUID(str(reservation_uuid)))
    original_units = reservation.units
    if request.method == "POST":
        form = ReservationChangeForm(request.POST, instance=reservation)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation_uuid = update_existing_reservation(
                request, original_units, reservation, form
            )
            return redirect(
                "reservation_detail_own", reservation_uuid=str(reservation.uuid)
            )
    else:
        form = ReservationChangeForm(instance=reservation)
    return render(
        request,
        "reservation_update.html",
        {
            "form": form,
            "reservation_uuid": str(reservation_uuid),
            "reservation_name": reservation.name,
        },
    )


@login_required()
def reservation_delete(request, reservation_uuid):
    """

    :param request:
    :param reservation_uuid:
    :return:
    """
    reservation = get_object_or_404(Reservation, uuid=UUID(str(reservation_uuid)))
    if request.method == "POST":
        is_removed = delete_existing_reservation(request, reservation)
        if is_removed:
            return redirect("reservations")
    return render(request, "reservation_delete.html", {"reservation": reservation})
