from uuid import UUID

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from projects.models import Project
from .cicd import get_cicd_list, get_cicd_host_info_list, create_new_cicd, create_new_cicd_host_info, \
    update_existing_cicd_host_info
from .forms import CicdCreateForm, CicdCreateHostInfoForm, CicdUpdateHostInfoForm
from .jenkins_api import deploy_cicd_environment
from .jenkins_api import start_cicd_environment, stop_cicd_environment, purge_cicd_environment, info_cicd_environment
from .models import Cicd, CicdHostInfo


@login_required
def cicd(request):
    """

    :param request:
    :return:
    """
    cicds = get_cicd_list(request)
    return render(request, 'cicd.html', {'cicds': cicds})


def cicd_host_info(request):
    """

    :param request:
    :return:
    """
    cicd_his = get_cicd_host_info_list(request)
    return render(request, 'cicd_host_info.html', {'cicd_his': cicd_his})


def cicd_create(request):
    """

    :param request:
    :return:
    """
    # get project
    if request.GET.get('project_uuid'):
        project_uuid = request.GET.get('project_uuid')
    else:
        project_uuid = '00000000-0000-0000-0000-000000000000'
    project = get_object_or_404(Project, uuid=UUID(str(project_uuid)))
    # set user permissions
    is_pc = (project.project_creator == request.user)
    is_po = (request.user in project.project_owners.all())
    is_pm = (request.user in project.project_members.all())
    initial_data = {
        'aerpaw_uuid': project_uuid,
    }
    if request.method == 'POST':
        form = CicdCreateForm(request.POST, initial=initial_data)
        if form.is_valid():
            cicd_uuid = create_new_cicd(request, form, project_uuid)
            if cicd_uuid:
                return redirect('cicd_detail', cicd_uuid=cicd_uuid)
            else:
                return redirect('project_detail', project_uuid=project_uuid)
        else:
            messages.error(request, "Error")
    else:
        form = CicdCreateForm(initial=initial_data)

    return render(request, 'cicd_create.html', {'form': form, 'is_pc': is_pc, 'is_po': is_po, 'is_pm': is_pm})


def cicd_host_info_create(request):
    """

    :param request:
    :return:
    """
    # TODO: handle case of duplicate configuration (all ports must be globally unique)
    if request.method == 'POST':
        form = CicdCreateHostInfoForm(request.POST)
        if form.is_valid():
            cicd_hi_uuid = create_new_cicd_host_info(request, form)
            return redirect('cicd_host_info_detail', cicd_host_info_uuid=cicd_hi_uuid)
        else:
            messages.error(request, "Error")
    else:
        form = CicdCreateHostInfoForm()

    return render(request, 'cicd_host_info_create.html', {'form': form})


def cicd_detail(request, cicd_uuid):
    """

    :param request:
    :param experiment_uuid:
    :return:
    """
    cicd = get_object_or_404(Cicd, uuid=UUID(str(cicd_uuid)))
    # get project
    project_uuid = cicd.aerpaw_uuid
    project = get_object_or_404(Project, uuid=UUID(str(project_uuid)))
    # set user permissions
    is_pc = (project.project_creator == request.user)
    is_po = (request.user in project.project_owners.all())
    is_pm = (request.user in project.project_members.all())
    try:
        project = Project.objects.get(uuid=UUID(str(cicd.aerpaw_uuid)))
    except Project.DoesNotExist:
        project = {
            'name': 'UNDEFINED',
            'uuid': cicd.aerpaw_uuid
        }
    if request.GET.get('deploy_cicd'):
        info = deploy_cicd_environment(cicd.uuid)
        if info == -1:
            status = {
                'message': 'ERROR: CI/CD deployment requires a valid project link',
                'timestamp': timezone.now()
            }
        else:
            status = {
                'message': 'Deploying CI/CD as job #{0}'.format(info),
                'timestamp': timezone.now()
            }
    elif request.GET.get('restart_cicd'):
        info = start_cicd_environment(cicd.uuid)
        status = {
            'message': 'Starting CI/CD as job #{0}'.format(info),
            'timestamp': timezone.now()
        }
    elif request.GET.get('stop_cicd'):
        info = stop_cicd_environment(cicd.uuid)
        status = {
            'message': 'Stopping CI/CD as job #{0}'.format(info),
            'timestamp': timezone.now()
        }
    elif request.GET.get('purge_cicd'):
        info = purge_cicd_environment(cicd.uuid)
        status = {
            'message': 'Purging CI/CD as job #{0}'.format(info),
            'timestamp': timezone.now()
        }
        cicd_hi = CicdHostInfo.objects.get(id=cicd.cicd_host_info_id)
        cicd_hi.is_allocated = False
        cicd_hi.project_uuid = ''
        cicd.delete()
        cicd_hi.save()
        return redirect('cicd')
    else:
        info = info_cicd_environment(cicd.uuid)
        status = {
            'message': info,
            'timestamp': timezone.now()
        }

    return render(request, 'cicd_detail.html',
                  {'cicd': cicd, 'project': project, 'status': status, 'is_pc': is_pc, 'is_po': is_po, 'is_pm': is_pm})


def cicd_host_info_detail(request, cicd_host_info_uuid):
    """

    :param request:
    :param cicd_host_info_uuid:
    :return:
    """
    cicd_hi = get_object_or_404(CicdHostInfo, uuid=UUID(str(cicd_host_info_uuid)))

    if request.GET.get('purge_cicd_host_info'):
        if not cicd_hi.is_allocated:
            cicd_hi.delete()
            return redirect('cicd_host_info')
        else:
            messages.error(request, 'ERROR: Unable to delete an allocated CI/CD resource connection')
            return redirect('cicd_host_info_detail', cicd_host_info_uuid=str(cicd_hi.uuid))

    return render(request, 'cicd_host_info_detail.html',
                  {
                      'cicd_hi': cicd_hi
                  })


def cicd_host_info_update(request, cicd_host_info_uuid):
    """

    :param request:
    :return:
    """
    user = request.user
    cicd_hi = get_object_or_404(CicdHostInfo, uuid=UUID(str(cicd_host_info_uuid)))
    if cicd_hi.is_allocated:
        messages.info(request, 'INFO: Unable to edit because CI/CD resource is already allocated')
        return render(request, 'cicd_host_info_detail.html', {'cicd_hi': cicd_hi})
    if request.method == 'POST':
        form = CicdUpdateHostInfoForm(request.POST)
        if form.is_valid():
            cicd_host_info_uuid = update_existing_cicd_host_info(request, form, cicd_hi)
            return redirect('cicd_host_info_detail', cicd_host_info_uuid=str(cicd_host_info_uuid))
        else:
            messages.error(request, "Error")
    else:
        form = CicdUpdateHostInfoForm(instance=cicd_hi)

    return render(request, 'cicd_host_info_update.html', {'form': form, 'cicd_hi_uuid': str(cicd_hi.uuid)})
