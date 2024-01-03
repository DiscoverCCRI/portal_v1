import os
import subprocess
import tempfile
from zipfile import ZipFile

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import BadHeaderError
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect, render

from usercomms.usercomms import portal_mail

from .accounts import create_new_role_request
from .forms import AerpawRoleRequestForm, AerpawUser, AerpawUserSignupForm
from .models import create_new_signup


@login_required
def profile(request):
    """

    :param request:
    :return:
    """
    user = request.user
    if request.method == "POST":
        for key in request.POST.keys():
            if not key == "csrfmiddlewaretoken":
                display_name = request.POST.get(key)
                if len(display_name) < 5:
                    messages.error(
                        request,
                        "ERROR: Display Name must be at least 5 characters long...",
                    )
                    return render(request, "profile.html", {"user": user})
                user_obj = AerpawUser.objects.get(id=user.id)
                if user_obj.display_name != display_name:
                    user_obj.display_name = display_name
                    user_obj.save()
                    user = user_obj

    return render(request, "profile.html", {"user": user})


@login_required
def request_roles(request):
    """

    :param request:
    :return:
    """
    if request.user.is_aerpaw_user() and request.user.is_project_manager():
        has_role_options = False
    else:
        has_role_options = True
    if request.method == "GET":
        form = AerpawRoleRequestForm(user=request.user)
    else:
        form = AerpawRoleRequestForm(request.POST, user=request.user)
        if form.is_valid():
            role_request = create_new_role_request(request, form)
            subject = (
                "[DISCOVER] User: "
                + request.user.display_name
                + " has requested role: "
                + role_request
            )
            body_message = form.cleaned_data["purpose"]
            sender = request.user
            receivers = []
            if role_request == "is Administrator":
                user_managers = AerpawUser.objects.filter(is_superuser=True).distinct()
            elif role_request in [
                "is Operator",
                "can Manage Resources",
                "can Manage User Roles",
            ]:
                user_managers = AerpawUser.objects.filter(
                    groups__name__in=["site_admin"]
                ).distinct()
            else:
                user_managers = AerpawUser.objects.filter(
                    groups__name__in=["site_admin", "user_manager"]
                ).distinct()
            for um in user_managers:
                receivers.append(um)
            reference_note = "Add role " + str(role_request)
            reference_url = (
                "https://" + str(request.get_host()) + "/manage/user_requests"
            )
            try:
                portal_mail(
                    subject=subject,
                    body_message=body_message,
                    sender=sender,
                    receivers=receivers,
                    reference_note=reference_note,
                    reference_url=reference_url,
                )
                messages.info(
                    request,
                    "Success! Request to add role: " + role_request + " has been sent",
                )
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            return redirect("profile")

    return render(
        request,
        "request_roles.html",
        {"form": form, "has_role_options": has_role_options},
    )


@login_required
def signup(request):
    """

    :param request:
    :return:
    """

    if request.method == "POST":
        form = AerpawUserSignupForm(request.POST)
        if form.is_valid():
            signup_uuid = create_new_signup(request, form)
            return redirect("home")
    else:
        form = AerpawUserSignupForm()
    return render(request, "signup.html", {"form": form})
