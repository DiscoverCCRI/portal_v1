from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import BadHeaderError
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.utils import timezone
from uuid import UUID

from accounts.models import AerpawUser
from experiments.models import Experiment
from profiles.models import Profile
from usercomms.usercomms import portal_mail, ack_mail
# from cicd.models import Cicd
from .forms import ProjectCreateForm, ProjectUpdateForm, ProjectUpdateMembersForm, ProjectUpdateOwnersForm, \
    ProjectJoinForm, JOIN_CHOICES
from .models import Project, ProjectMembershipRequest
from .projects import create_new_project, get_project_list, update_existing_project, delete_existing_project, \
    create_new_project_membership_request

PI_message = "Please email the admin to become a PI first!"


@login_required()
@user_passes_test(lambda u: u.is_aerpaw_user())
def projects(request):
    """

    :param request:
    :return:
    """
    my_projects, other_projects = get_project_list(request)
    return render(request, 'projects.html', {'my_projects': my_projects, 'other_projects': other_projects})


@login_required()
@user_passes_test(lambda u: u.is_project_manager() or u.is_site_admin())
def project_create(request):
    """

    :param request:
    :return:
    """
    if request.method == "POST":
        form = ProjectCreateForm(request.POST,
                                 initial={'project_members': request.user, 'project_owners': request.user})
        if form.is_valid():
            project_uuid = create_new_project(request, form)
            return redirect('project_detail', project_uuid=project_uuid)
    else:
        form = ProjectCreateForm()
    return render(request, 'project_create.html', {'form': form})


@login_required()
@user_passes_test(lambda u: u.is_aerpaw_user())
def project_detail(request, project_uuid):
    """

    :param request:
    :param project_uuid:
    :return:
    """
    # get project
    project = get_object_or_404(Project, uuid=UUID(str(project_uuid)))
    # check for project join request approval / denial
    if request.method == "POST":
        for key in request.POST.keys():
            if not key == 'csrfmiddlewaretoken':
                parse_key = key.rsplit('_', 1)
                if parse_key[0] != 'notes':
                    member_type = parse_key[0]
                    proj_mem_request = ProjectMembershipRequest.objects.get(id=int(parse_key[1]))
                    notes = request.POST.get('notes_' + str(parse_key[1]))
                    if request.POST.get(key) == 'Approve':
                        is_approved = True
                    else:
                        is_approved = False
        # get user_obj
        user_obj = AerpawUser.objects.get(id=int(proj_mem_request.requested_by_id))
        if str(is_approved) == 'True':
            if member_type == 'MEMBER':
                project.project_members.add(user_obj)
            elif member_type == 'OWNER':
                project.project_owners.add(user_obj)
        else:
            if member_type == 'MEMBER':
                project.project_members.remove(user_obj)
            elif member_type == 'OWNER':
                project.project_owners.remove(user_obj)
        project.save()
        proj_mem_request.notes = notes
        proj_mem_request.is_approved = is_approved
        proj_mem_request.is_completed = True
        proj_mem_request.save()
        if is_approved:
            subject = '[AERPAW] User: ' + user_obj.display_name + ' request to join project: ' + project.name + ' has been APPROVED'
            reference_url = 'https://' + str(request.get_host()) + '/projects/' + str(project_uuid)
        else:
            subject = '[AERPAW] User: ' + user_obj.display_name + ' request to join project: ' + project.name + ' has been DENIED'
            reference_url = None
        body_message = notes
        sender = AerpawUser.objects.get(id=request.user.id)
        receivers = [user_obj]
        reference_note = 'Join project ' + project.name + ' as ' + member_type
        try:
            portal_mail(subject=subject, body_message=body_message, sender=sender, receivers=receivers,
                        reference_note=reference_note, reference_url=reference_url)
            if is_approved:
                messages.info(request, 'Success! APPROVED: Request to join project: ' + project.name + ' has been sent')
            else:
                messages.info(request, 'Success! DENIED: Request to join project: ' + project.name + ' has been sent')
        except BadHeaderError:
            return HttpResponse('Invalid header found.')

    # set user permissions
    is_pc = (project.project_creator == request.user)
    is_po = (request.user in project.project_owners.all())
    is_pm = (request.user in project.project_members.all())
    # RM_CICD
    # try:
    #     cicd = Cicd.objects.get(aerpaw_uuid=str(project.uuid))
    # except Cicd.DoesNotExist as err:
    #     print(err)
    #     cicd = None
    # cicd = get_object_or_404(Cicd, aerpaw_uuid=str(project.uuid))
    request.session['project_id'] = project.id
    project_members = project.project_members.order_by('username')
    project_owners = project.project_owners.order_by('username')
    project_experiments = project.experiment_of_project
    project_profiles = Profile.objects.filter(project_id=project.id).order_by('name')
    project_requests = ProjectMembershipRequest.objects.filter(project_uuid=project_uuid, is_completed=False).order_by(
        '-created_date')
    return render(request, 'project_detail.html',
                  {'project': project, 'project_members': project_members, 'project_owners': project_owners,
                   'is_pc': is_pc, 'is_po': is_po, 'is_pm': is_pm, 'project_requests': project_requests,
                   'experiments': project_experiments.all(), 'profiles': project_profiles})


@login_required()
@user_passes_test(lambda u: u.is_aerpaw_user())
def project_join(request, project_uuid):
    """

    :param request:
    :param project_uuid:
    :return:
    """
    # get project
    project = get_object_or_404(Project, uuid=UUID(str(project_uuid)))
    if request.method == 'GET':
        form = ProjectJoinForm()
    else:
        form = ProjectJoinForm(request.POST)
        if form.is_valid():
            sender = get_object_or_404(AerpawUser, id=request.user.id)
            reference_url = 'https://' + str(request.get_host()) + '/projects/' + str(project_uuid)
            if str(dict(JOIN_CHOICES)[form.data['member_type']]) == 'Project Member':
                member_type = 'MEMBER'
            else:
                member_type = 'OWNER'
            body_message = form.cleaned_data['message']
            reference_note = 'Join project ' + str(project.name) + ' as ' + member_type
            subject = '[AERPAW] User: ' + sender.display_name + ' has requested to join project: ' + \
                      project.name + ' as ' + member_type
            receivers = [project.project_creator]
            project_owners = project.project_owners.order_by('username')
            for po in project_owners:
                receivers.append(po)
            receivers = list(set(receivers))
            try:
                create_new_project_membership_request(request, project_uuid, member_type, body_message)
                portal_mail(subject=subject, body_message=body_message, sender=sender, receivers=receivers,
                            reference_note=reference_note, reference_url=reference_url)
                kwargs = {'project_name': str(project.name), 'project_owner': str(project.created_by)}
                ack_mail(
                    template='project_join', user_name=request.user.display_name,
                    user_email=request.user.email, **kwargs
                )
                messages.info(request, 'Success! Request to join project: ' + str(project.name) + ' has been sent')
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('projects')

    return render(request, "project_join.html", {'form': form, 'project': project})


@login_required()
@user_passes_test(lambda u: u.is_aerpaw_user())
def project_update(request, project_uuid):
    """

    :param request:
    :param project_uuid:
    :return:
    """
    project = get_object_or_404(Project, uuid=UUID(str(project_uuid)))
    # set user permissions
    is_pc = (project.project_creator == request.user)
    is_po = (request.user in project.project_owners.all())
    is_pm = (request.user in project.project_members.all())
    if request.method == "POST":
        form = ProjectUpdateForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            project_uuid = update_existing_project(request, project, form)
            return redirect('project_detail', project_uuid=str(project.uuid))
    else:
        form = ProjectUpdateForm(instance=project)
    return render(request, 'project_update.html',
                  {'form': form, 'project_uuid': str(project_uuid), 'project_name': project.name,
                   'is_pc': is_pc, 'is_po': is_po, 'is_pm': is_pm}
                  )


@login_required()
@user_passes_test(lambda u: u.is_aerpaw_user())
def project_update_members(request, project_uuid):
    """

    :param request:
    :param project_uuid:
    :return:
    """
    project = get_object_or_404(Project, uuid=UUID(str(project_uuid)))
    # set user permissions
    is_pc = (project.project_creator == request.user)
    is_po = (request.user in project.project_owners.all())
    is_pm = (request.user in project.project_members.all())
    project_members_orig = list(project.project_members.all())
    if request.method == "POST":
        form = ProjectUpdateMembersForm(request.POST, instance=project)
        if form.is_valid():
            project_members = list(form.cleaned_data.get('project_members'))
            project_members_added = list(set(project_members).difference(set(project_members_orig)))
            project_members_removed = list(set(project_members_orig).difference(set(project_members)))
            # update members
            for member in project_members_added:
                project.project_members.add(member)
            for member in project_members_removed:
                project.project_members.remove(member)
            project.modified_by = request.user
            project.modified_date = timezone.now()
            project.save()
            # send usercomms
            sender = get_object_or_404(AerpawUser, id=request.user.id)
            reference_url = 'https://' + str(request.get_host()) + '/projects/' + str(project_uuid)
            try:
                if project_members_added:
                    reference_note = 'Added to project ' + str(project.name) + ' as MEMBER'
                    subject = '[AERPAW] User: ' + sender.display_name + ' has ADDED you to project: ' + \
                              project.name + ' as MEMBER'
                    body_message = 'A project owner has added you to ' + project.name + \
                                   '. If you believe this to be in error please contact the project owner direclty'
                    portal_mail(subject=subject, body_message=body_message, sender=sender,
                                receivers=project_members_added,
                                reference_note=reference_note, reference_url=reference_url)
                if project_members_removed:
                    reference_note = 'Removed from project ' + str(project.name) + ' as MEMBER'
                    subject = '[AERPAW] User: ' + sender.display_name + ' has REMOVED you from project: ' + \
                              project.name + ' as MEMBER'
                    body_message = 'A project owner has removed you from ' + project.name + \
                                   '. If you believe this to be in error please contact the project owner directly'
                    portal_mail(subject=subject, body_message=body_message, sender=sender,
                                receivers=project_members_removed,
                                reference_note=reference_note, reference_url=None)
                messages.info(request, 'Success! MEMBER changes for project: ' + str(project.name) + ' has been sent')
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('project_detail', project_uuid=str(project.uuid))
    else:
        form = ProjectUpdateMembersForm(instance=project)
    return render(request, 'project_update_members.html',
                  {
                      'form': form, 'project_uuid': str(project_uuid), 'project_name': project.name,
                      'is_pc': is_pc, 'is_po': is_po, 'is_pm': is_pm}
                  )


@login_required()
@user_passes_test(lambda u: u.is_aerpaw_user())
def project_update_owners(request, project_uuid):
    """

    :param request:
    :param project_uuid:
    :return:
    """
    project = get_object_or_404(Project, uuid=UUID(str(project_uuid)))
    # set user permissions
    is_pc = (project.project_creator == request.user)
    is_po = (request.user in project.project_owners.all())
    is_pm = (request.user in project.project_members.all())
    project_owners_orig = list(project.project_owners.all())
    if request.method == "POST":
        form = ProjectUpdateOwnersForm(request.POST, instance=project, project=project)
        if form.is_valid():
            project_owners = list(form.cleaned_data.get('project_owners'))
            project_owners_added = list(set(project_owners).difference(set(project_owners_orig)))
            project_owners_removed = list(set(project_owners_orig).difference(set(project_owners)))
            # update members
            for owner in project_owners_added:
                project.project_owners.add(owner)
            for owner in project_owners_removed:
                project.project_owners.remove(owner)
            project.modified_by = request.user
            project.modified_date = timezone.now()
            project.save()
            # send usercomms
            sender = get_object_or_404(AerpawUser, id=request.user.id)
            reference_url = 'https://' + str(request.get_host()) + '/projects/' + str(project_uuid)
            try:
                if project_owners_added:
                    reference_note = 'Added to project ' + str(project.name) + ' as OWNER'
                    subject = '[AERPAW] User: ' + sender.display_name + ' has ADDED you to project: ' + \
                              project.name + ' as OWNER'
                    body_message = 'A project owner has added you to ' + project.name + \
                                   '. If you believe this to be in error please contact the project owner direclty'
                    portal_mail(subject=subject, body_message=body_message, sender=sender,
                                receivers=project_owners_added,
                                reference_note=reference_note, reference_url=reference_url)
                if project_owners_removed:
                    reference_note = 'Removed from project ' + str(project.name) + ' as OWNER'
                    subject = '[AERPAW] User: ' + sender.display_name + ' has REMOVED you from project: ' + \
                              project.name + ' as OWNER'
                    body_message = 'A project owner has removed you from ' + project.name + \
                                   '. If you believe this to be in error please contact the project owner directly'
                    portal_mail(subject=subject, body_message=body_message, sender=sender,
                                receivers=project_owners_removed,
                                reference_note=reference_note, reference_url=None)
                messages.info(request, 'Success! OWNER changes for project: ' + str(project.name) + ' has been sent')
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('project_detail', project_uuid=str(project.uuid))
    else:
        form = ProjectUpdateOwnersForm(instance=project, project=project)
    return render(request, 'project_update_owners.html',
                  {
                      'form': form, 'project_uuid': str(project_uuid), 'project_name': project.name,
                      'is_pc': is_pc, 'is_po': is_po, 'is_pm': is_pm}
                  )


@login_required()
@user_passes_test(lambda u: u.is_aerpaw_user())
def project_delete(request, project_uuid):
    """

    :param request:
    :param project_uuid:
    :return:
    """
    project = get_object_or_404(Project, uuid=UUID(str(project_uuid)))
    project_owners = project.project_owners.order_by('display_name')
    project_members = project.project_members.order_by('display_name')
    profile_ids = Profile.objects.filter(project=project.id).values_list('pk', flat=True).distinct()
    profiles = Profile.objects.filter(pk__in=profile_ids).order_by('name')
    experiments = Experiment.objects.filter(Q(profile__project_id=project.id) |
                                            Q(profile__in=list(profiles)) |
                                            Q(project=project.id)).order_by('name').distinct()
    for exp in experiments:
        if not exp.can_initiate():
            messages.error(request, '[EXPERIMENT] {0} is not IDLE .. Unable to delete Project'.format(exp.name))
            return project_detail(request, project_uuid)
    # set user permissions
    is_pc = (project.project_creator == request.user)
    if request.method == "POST":
        is_removed = delete_existing_project(request, project, profiles, experiments)
        if is_removed:
            return redirect('projects')
    return render(request, 'project_delete.html',
                  {'project': project, 'project_owners': project_owners, 'project_members': project_members,
                   'profiles': profiles, 'experiments': experiments, 'is_pc': is_pc}
                  )
