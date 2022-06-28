import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone

from .models import Project, AerpawUser, ProjectMembershipRequest


def create_new_project(request, form):
    """

    :param request:
    :param form:
    :return:
    """
    project = Project()
    project.uuid = uuid.uuid4()
    project.name = form.data.getlist('name')[0]
    try:
        project.description = form.data.getlist('description')[0]
    except IndexError as e:
        print(e)
        project.description = None
    try:
        if form.data.getlist('is_public')[0]:
            project.is_public = True
    except IndexError as e:
        print(e)
        project.is_public = False

    project.project_creator = request.user
    project.created_by = request.user
    project.created_date = timezone.now()
    project.modified_by = project.created_by
    project.modified_date = project.created_date
    project.save()

    return str(project.uuid)


def update_project_members(project, project_member_email_list):
    """

    :param project:
    :param project_member_id_list:
    :return:
    """
    # clear current project membership
    # project.project_members.clear()
    # add members from project_member_id_update_list
    project.project_pending_member_emails = ''
    project.save()
    updated_pending_email_list = []
    for member_email in project_member_email_list:
        try:
            project_member = AerpawUser.objects.get(oidc_claim_email=member_email)
            project.project_members.add(project_member)
        except AerpawUser.DoesNotExist:
            updated_pending_email_list.append(member_email)

    seen = set()
    unique_list = []
    for email in updated_pending_email_list:
        if email not in seen:
            unique_list.append(email)
            seen.add(email)
    project.project_pending_member_emails = ",".join(str(x) for x in unique_list)
    if project.project_pending_member_emails != '':
        send_pending_memeber_emails(unique_list)


def send_pending_memeber_emails(pending_member_emails_list):
    subject = 'AERPAW project sign up'
    message = 'You received this email because a project PI has added you to the project. Please go to aerpaw.org to login and signup.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = pending_member_emails_list
    send_mail(subject, message, email_from, recipient_list)


def delete_project_members(project, project_member_id_list):
    """

    :param project:
    :param project_member_id_list:
    :return:
    """
    # clear current project membership
    # project.project_members.clear()
    # add members from project_member_id_update_list
    for member_id in project_member_id_list:
        project_member = AerpawUser.objects.get(id=int(member_id))
        project.project_members.remove(project_member)
    project.save()


def update_existing_project(request, project, form):
    """
    Create new AERPAW Project

    :param request:
    :param form:
    :return:
    """
    project.modified_by = request.user
    project.modified_date = timezone.now()
    project.name = form.data.getlist('name')[0]
    try:
        project.description = form.data.getlist('description')[0]
    except IndexError as e:
        print(e)
        project.description = None
    try:
        if form.data.getlist('is_public')[0]:
            project.is_public = True
    except IndexError as e:
        print(e)
        project.is_public = False

    project.save()

    return str(project.uuid)


def delete_existing_project(request, project, profiles, experiments):
    """

    :param request:
    :param project:
    :param profiles:
    :param experiments:
    :return:
    """
    try:
        for experiment in experiments:
            experiment.delete()
        for profile in profiles:
            profile.delete()
        project.delete()
        return True
    except Exception as e:
        print(e)
    return False


def get_project_list(request):
    """

    :param request:
    :return:
    """
    my_projects = Project.objects.filter(
        Q(project_creator=request.user) |
        Q(project_owners__in=[request.user]) |
        Q(project_members__in=[request.user])
    ).order_by('name').distinct()
    other_projects = Project.objects.all().difference(my_projects).order_by('name')
    return my_projects, other_projects


def create_new_project_membership_request(request, project_uuid, member_type, message):
    pm_request = ProjectMembershipRequest()
    pm_request.project_uuid = project_uuid
    pm_request.requested_by = request.user
    pm_request.member_type = member_type
    pm_request.message = message
    pm_request.created_by = request.user
    pm_request.created_date = timezone.now()
    pm_request.is_approved = False
    pm_request.is_completed = False
    pm_request.modified_by = pm_request.created_by
    pm_request.modified_date = pm_request.created_date
    pm_request.save()

    return True
