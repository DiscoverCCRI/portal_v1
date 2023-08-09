from accounts.models import AerpawRoleRequest, AerpawUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.core.mail import BadHeaderError
from django.http import HttpResponse
from django.shortcuts import render
from usercomms.usercomms import portal_mail

from .templatetags.user_groups import role_name


@login_required
@user_passes_test(lambda u: u.is_user_manager() or u.is_site_admin())
def user_groups(request):
    """

    :param request:
    :return:
    """
    if request.method == 'POST':
        for key in request.POST.keys():
            if not key == 'csrfmiddlewaretoken':
                cur_value = request.POST.get(key)
                parse_key = key.rsplit('_', 1)
                user_obj = AerpawUser.objects.get(id=int(parse_key[1]))
                group_obj = Group.objects.get(name=parse_key[0])
                if str(cur_value) == 'True':
                    user_obj.groups.remove(group_obj)
                else:
                    user_obj.groups.add(group_obj)
                user_obj.save()
    user = request.user
    all_users = AerpawUser.objects.all().exclude(username='admin').order_by('display_name')
    return render(request, 'user_groups.html', {'user': user, 'all_users': all_users})


@login_required
@user_passes_test(lambda u: u.is_user_manager() or u.is_site_admin())
def user_requests(request):
    """

    :param request:
    :return:
    """
    user_manager = AerpawUser.objects.get(id=request.user.id)
    if request.method == "POST":
        for key in request.POST.keys():
            if not key == 'csrfmiddlewaretoken':
                parse_key = key.rsplit('_', 1)
                if parse_key[0] != 'notes':
                    role = parse_key[0]
                    role_request = AerpawRoleRequest.objects.get(id=int(parse_key[1]))
                    notes = request.POST.get('notes_' + str(parse_key[1]))
                    if request.POST.get(key) == 'Approve':
                        is_approved = True
                    else:
                        is_approved = False
        # get user_obj
        user_obj = AerpawUser.objects.get(id=int(role_request.requested_by_id))
        group_obj = Group.objects.get(name=str(role))
        r_name = role_name(group_obj.name)
        if str(is_approved) == 'True':
            user_obj.groups.add(group_obj)
        else:
            user_obj.groups.remove(group_obj)
        user_obj.save()
        role_request.notes = notes
        role_request.is_approved = is_approved
        role_request.is_completed = True
        role_request.save()
        # TODO: email
        if is_approved:
            subject = '[DISCOVER] User: ' + user_obj.display_name + ' requested role: ' + r_name + ' has been APPROVED'
        else:
            subject = '[DISCOVER] User: ' + user_obj.display_name + ' requested role: ' + r_name + ' has been DENIED'
        body_message = notes
        sender = user_manager
        receivers = [user_obj]
        user_managers = AerpawUser.objects.filter(groups__name='user_manager')
        for um in user_managers:
            receivers.append(um)
        receivers.remove(sender)
        reference_note = 'Add role ' + r_name
        reference_url = None
        try:
            portal_mail(subject=subject, body_message=body_message, sender=sender, receivers=receivers,
                        reference_note=reference_note, reference_url=reference_url)
            if is_approved:
                messages.info(request, 'Success! APPROVED: Request to add role: ' + r_name + ' has been sent')
            else:
                messages.info(request, 'Success! DENIED: Request to add role: ' + r_name + ' has been sent')
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
    sa_set = ['site_admin']
    um_set = ['site_admin', 'operator', 'user_manager', 'resource_manager']
    if user_manager.is_superuser:
        print('IS SUPERUSER')
        open_u_reqs = AerpawRoleRequest.objects.filter(is_completed=False).order_by('-created_date')
        closed_u_reqs = AerpawRoleRequest.objects.filter(is_completed=True).order_by('-created_date')
    elif user_manager.is_site_admin():
        print('IS SITE ADMIN')
        open_u_reqs = AerpawRoleRequest.objects.filter(is_completed=False).exclude(requested_role__in=sa_set).order_by(
            '-created_date')
        closed_u_reqs = AerpawRoleRequest.objects.filter(is_completed=True).exclude(requested_role__in=sa_set).order_by(
            '-created_date')
    else:
        print('IS USER MANAGER')
        open_u_reqs = AerpawRoleRequest.objects.filter(is_completed=False).exclude(requested_role__in=um_set).order_by(
            '-created_date')
        closed_u_reqs = AerpawRoleRequest.objects.filter(is_completed=True).exclude(requested_role__in=um_set).order_by(
            '-created_date')
    return render(request, 'user_requests.html', {'ou_reqs': open_u_reqs, 'cu_reqs': closed_u_reqs})
