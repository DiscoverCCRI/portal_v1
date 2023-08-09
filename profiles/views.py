# Create your views here.

from uuid import UUID

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from experiments.models import Experiment

from .forms import ProfileCreateForm, ProfileUpdateForm
from .profiles import *


@login_required()
def profiles(request):
    """

    :param request:
    :return:
    """
    profiles = get_profile_list(request)
    return render(request, "profiles.html", {"profiles": profiles})


@login_required()
def profile_create(request):
    """

    :param request:
    :return:
    """
    try:
        is_template = request.GET["is_template"]
        project = None
        project_uuid = "None"
    except Exception as exc:
        project = get_object_or_404(
            Project, id=int(request.session.get("project_id", ""))
        )
        project_uuid = str(project.uuid)
    if request.method == "POST":
        form = ProfileCreateForm(request.POST, user=request.user, project=project)
        if form.is_valid():
            profile_uuid = create_new_profile(request, form)
            if profile_uuid is None:
                return render(
                    request,
                    "profile_create.html",
                    {
                        "form": form,
                        "project_uuid": project_uuid,
                        "msg": '* [ERROR] Invalid entry for "Definition".',
                    },
                )
            return redirect("profile_detail", profile_uuid=profile_uuid)
    else:
        form = ProfileCreateForm(user=request.user, project=project)
    return render(
        request, "profile_create.html", {"form": form, "project_uuid": project_uuid}
    )


@login_required()
def profile_detail(request, profile_uuid):
    """

    :param request:
    :param profile_uuid:
    :return:
    """
    profile = get_object_or_404(Profile, uuid=UUID(str(profile_uuid)))
    experiments = profile.experiment_profile.all()
    is_creator = profile.created_by == request.user
    return render(
        request,
        "profile_detail.html",
        {"profile": profile, "is_creator": is_creator, "experiments": experiments},
    )


@login_required()
def profile_update(request, profile_uuid):
    """

    :param request:
    :param profile_uuid:
    :return:
    """
    profile = get_object_or_404(Profile, uuid=UUID(str(profile_uuid)))
    if profile.project:
        project = get_object_or_404(Project, id=profile.project.id)
    else:
        project = None
    if request.method == "POST":
        old_profile_name = profile.name
        form = ProfileUpdateForm(request.POST, instance=profile, project=project)
        if form.is_valid():
            # if is_emulab_profile(profile):
            #    delete_emulab_profile(request, profile, old_profile_name)
            profile = form.save(commit=False)
            temporary_uuid = update_existing_profile(request, profile, form)
            if temporary_uuid is None:
                return render(
                    request,
                    "profile_update.html",
                    {
                        "form": form,
                        "profile_uuid": str(profile_uuid),
                        "profile_name": profile.name,
                        "msg": '* [ERROR] Invalid entry for "Definition".',
                    },
                )
            else:
                return redirect("profile_detail", profile_uuid=str(profile.uuid))
    else:
        form = ProfileUpdateForm(instance=profile, project=project)
    return render(
        request,
        "profile_update.html",
        {"form": form, "profile_uuid": str(profile_uuid), "profile_name": profile.name},
    )


@login_required()
def profile_delete(request, profile_uuid):
    """

    :param request:
    :param profile_uuid:
    :return:
    """
    profile = get_object_or_404(Profile, uuid=UUID(str(profile_uuid)))
    experiments = Experiment.objects.filter(profile_id=profile.id).order_by("name")
    for exp in experiments:
        if not exp.can_initiate():
            messages.error(
                request,
                "[EXPERIMENT] {0} is not IDLE .. Unable to delete Resource Description".format(
                    exp.name
                ),
            )
            return profile_detail(request, profile_uuid)
    if request.method == "POST":
        is_removed = delete_existing_profile(request, profile, experiments)
        if is_removed:
            return redirect("profiles")
    return render(
        request, "profile_delete.html", {"profile": profile, "experiments": experiments}
    )
