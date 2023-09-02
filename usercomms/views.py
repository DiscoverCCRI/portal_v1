from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404

from uuid import UUID

from .models import Usercomms
from projects.models import AerpawUser


@login_required
def usercomms(request):
    """

    :param request:
    :return:
    """
    sent = Usercomms.objects.filter(
        Q(reference_user_id=request.user.id) &
        Q(sender_id=request.user.id)
    ).order_by('-created_date').distinct()
    received = Usercomms.objects.filter(reference_user_id=request.user.id).difference(sent).order_by('-created_date')
    return render(request, 'usercomms.html', {'sent': sent, 'received': received})


@login_required
def usercomm_detail(request, usercomm_uuid):
    """

    :param request:
    :param usercomm_uuid:
    :return:
    """
    uc = get_object_or_404(Usercomms, uuid=UUID(str(usercomm_uuid)), reference_user_id=request.user.id)
    return render(request, 'usercomm_detail.html', {'uc': uc})