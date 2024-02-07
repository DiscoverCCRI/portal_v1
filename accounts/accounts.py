import logging

from django.utils import timezone

from .models import AerpawRoleRequest, AerpawUserRoleChoice

logger = logging.getLogger(__name__)


def create_new_role_request(request, form):
    role_request = AerpawRoleRequest()
    requested_role = form.data.getlist("requested_role")[0]
    purpose = form.data.getlist("purpose")[0]

    role_request.requested_by = request.user
    role_request.purpose = purpose
    role_request.created_by = request.user
    role_request.created_date = timezone.now()
    role_request.requested_role = requested_role
    role_request.is_approved = False
    role_request.is_completed = False
    role_request.modified_by = role_request.created_by
    role_request.modified_date = role_request.created_date
    role_request.save()

    return AerpawUserRoleChoice[requested_role].value
