# Create your views here.


import logging
from uuid import UUID

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from projects.models import Project
from usercomms.usercomms import portal_mail
from .experiments import get_experiment_list, generate_experiment_session_request, create_new_experiment, \
    get_emulab_manifest, experiment_state_change, query_emulab_instance_status, \
    delete_existing_experiment, is_emulab_stage, initiate_emulab_instance, update_existing_experiment
from .forms import ExperimentCreateForm, ExperimentLinkUpdateForm, ExperimentUpdateExperimentersForm, ExperimentUpdateForm, ExperimentSubmitForm, \
    ExperimentUpdateByOpsForm
from .models import Experiment

logger = logging.getLogger(__name__)


@login_required()
def experiments(request):
    """

    :param request:
    :return:
    """
    experiments = get_experiment_list(request)
    return render(request, 'experiments.html', {'experiments': experiments})


@login_required()
def experiment_create(request):
    """

    :param request:
    :return:
    """
    project_id = request.session.get('project_id', '')
    project = get_object_or_404(Project, id=int(project_id))
    if request.method == "POST":
        form = ExperimentCreateForm(request.POST, project_id=project_id)
        if form.is_valid():
            experiment_uuid = create_new_experiment(request, form, project_id)
            return redirect('experiment_detail', experiment_uuid=experiment_uuid)
    elif request.user.is_anonymous:
        form = None
    else:
        form = ExperimentCreateForm(project_id=project_id)
    return render(request, 'experiment_create.html',
                  {'form': form, 'project_uuid': str(project.uuid), 'project_id': str(project.id)})


@login_required()
def experiment_update_experimenters(request, experiment_uuid):
    """

    :param request:
    :param experiment_uuid:
    :return:
    """
    experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))

    if request.method == "POST":
        form = ExperimentUpdateExperimentersForm(request.POST, instance=experiment)
        if form.is_valid():
            exps = form.cleaned_data.get('experimenter')
            experiment.experimenter.through.objects.filter(experiment_id=experiment.id).delete()
            for exp in exps:
                experiment.experimenter.add(exp)
            experiment.modified_by = request.user
            experiment.modified_date = timezone.now()
            experiment.save()
            return redirect('experiment_detail', experiment_uuid=str(experiment.uuid))
    else:
        form = ExperimentUpdateExperimentersForm(instance=experiment)
    return render(request, 'experiment_update_experimenters.html',
                  {
                      'form': form, 'experiment_uuid': str(experiment_uuid),
                      'experiment_name': experiment.name}
                  )


# def experiment_create(request):
#     """
#
#     :param request:
#     :return:
#     """
#     experimenter = request.user
#     print(request.session.values())
#     print(request.session.get('project_id'))
#     project_id = request.session.get('project_id', None)
#     try:
#         # project_id = request.session['project_id']
#         project = get_object_or_404(Project, id=project_id)
#     except KeyError:
#         project_qs=Project.objects.filter(project_members=experimenter)
#         if project_qs:
#             project=project_qs[0]
#         else:
#             return redirect('/')
#
#     form = ExperimentCreateForm()
#     # form = ExperimentCreateForm(request.POST, project=project, experimenter=experimenter)
#
#     if form.is_valid():
#         experiment_uuid = create_new_experiment(request, form)
#         return redirect('experiment_detail', experiment_uuid=experiment_uuid)
#
#     return render(request, 'experiment_create.html', {'form': form})

@login_required()
def experiment_detail(request, experiment_uuid):
    """

    :param request:
    :param experiment_uuid:
    :return:
    """
    experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))
    is_creator = (experiment.created_by == request.user)
    is_exp = (request.user in experiment.experimenter.all())
    is_po = (request.user in experiment.project.project_owners.all())
    is_pm = (request.user in experiment.project.project_members.all())
    is_not_testbed = (experiment.stage != 'Testbed')
    experiment_reservations = experiment.reservation_of_experiment
    request.session['experiment_id'] = experiment.id

    status = ''

    if is_emulab_stage(experiment.stage):
        status = query_emulab_instance_status(request, experiment)
        # the status can be any of following:
        # 'created', 'provisioning', 'provisioned', 'ready', 'failed', 'teriminating', 'not_started'
        if status == 'provisioned':
            status = 'booting'  # for better user understanding
    # elif experiment.state is Experiment.STATE_SUBMIT and 'Req' not in experiment.stage:
    #    # The operator approved and changed the state, set state to READY
    #    experiment.ready()
    #    experiment.save()
    else:
        status = 'idle'  # temporary, might want to change it

    return render(request, 'experiment_detail.html',
                  {'experiment': experiment,
                   'experimenter': experiment.experimenter.all(),
                   'experiment_status': Experiment.STATE_CHOICES[experiment.state][1],
                   'reservations': experiment_reservations.all(),
                   'is_creator': is_creator, 'is_exp': is_exp,
                   'is_po': is_po, 'is_pm': is_pm,
                   'is_not_testbed': is_not_testbed,}
                  )


@login_required()
def experiment_update(request, experiment_uuid):
    """

    :param request:
    :param experiment_uuid:
    :return:
    """
    experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))
    prev_stage = experiment.stage
    prev_state = experiment.state
    if request.method == "POST":
        form = ExperimentUpdateForm(request.POST, instance=experiment)
        if form.is_valid():
            experiment = form.save(commit=False)
            experiment_uuid = update_existing_experiment(request, experiment, form, prev_stage,
                                                         prev_state)
            return redirect('experiment_detail', experiment_uuid=str(experiment.uuid))

    form = ExperimentUpdateForm(instance=experiment)
    return render(request, 'experiment_update.html',
                  {
                      'form': form, 'experiment_uuid': str(experiment_uuid),
                      'experiment_name': experiment.name}
                  )


@login_required()
def experiment_update_by_ops(request, experiment_uuid):
    """
    This temporary code will need some update after GA
    :param request:
    :param experiment_uuid:
    :return:
    """
    experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))
    prev_stage = experiment.stage
    prev_state = experiment.state
    if request.method == "POST":
        form = ExperimentUpdateByOpsForm(request.POST, instance=experiment)
        if form.is_valid():
            experimenter = experiment.created_by  # save first, otherwise soon overwritten
            experiment = form.save(commit=False)
            experiment_uuid = update_existing_experiment(request, experiment, form, prev_stage,
                                                         prev_state)
            if experiment.message is not None and experiment.message != "":
                subject = 'DISCOVER Experiment Notification: {}'.format(experiment.uuid)
                email_message = "[{}]\n\n".format(subject) \
                                + "Experiment Name: {}\n".format(str(experiment)) \
                                + "Project: {}\n\n".format(experiment.project) \
                                + "Operator Comments:\n{}\n".format(experiment.message)
                receivers = [experimenter]
                logger.warning("send_email:\n" + subject)
                logger.warning(email_message)
                logger.warning("receivers = {}\n".format(receivers))
                portal_mail(subject=subject, body_message=email_message, sender=request.user,
                            receivers=receivers,
                            reference_note=None, reference_url=None)

            return redirect('experiment_detail', experiment_uuid=str(experiment.uuid))

    form = ExperimentUpdateByOpsForm(instance=experiment)
    return render(request, 'experiment_update.html',
                  {
                      'form': form, 'experiment_uuid': str(experiment_uuid),
                      'experiment_name': experiment.name}
                  )


@login_required()
def experiment_submit(request, experiment_uuid):
    """
    Submit = update experiment stage from development to Testbed/(Sandbox?)

    :param request:
    :param experiment_uuid:
    :return:
    """
    experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))
    prev_stage = experiment.stage
    prev_state = experiment.state
    if request.method == "POST":
        form = ExperimentSubmitForm(request.POST, instance=experiment)
        if form.is_valid():
            experiment = form.save(commit=False)
            update_existing_experiment(request, experiment, form, prev_stage, prev_state)
            return redirect('experiment_detail', experiment_uuid=str(experiment.uuid))

    form = ExperimentSubmitForm(instance=experiment)
    return render(request, 'experiment_update.html',
                  {
                      'form': form, 'experiment_uuid': str(experiment_uuid),
                      'experiment_name': experiment.name}
                  )


@login_required()
def experiment_delete(request, experiment_uuid):
    """

    :param request:
    :param experiment_uuid:
    :return:
    """
    experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))
    experiment_reservations = experiment.reservation_of_experiment
    if request.method == "POST":
        is_removed = delete_existing_experiment(request, experiment)
        if is_removed:
            return redirect('experiments')
    return render(request, 'experiment_delete.html',
                  {'experiment': experiment, 'experimenter': experiment.experimenter.all(),
                   'experiment_reservations': experiment_reservations})


@login_required()
def experiment_initiate(request, experiment_uuid):
    """
    handles experiment initiate OR terminate depending on its state

    :param request:
    :param experiment_uuid:
    :return:
    """
    experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))
    experiment_reservations = experiment.reservation_of_experiment

    if request.method == "POST":
        if experiment.can_initiate():
            # we are going to initiate the development
            experiment.stage = 'Development'
            experiment.save()
        elif experiment.can_terminate():
            # we are going to terminate the development
            experiment_state_change(request, experiment, "terminating")
            experiment.stage = 'Idle'
            experiment.save()
            return redirect('experiment_detail', experiment_uuid=experiment_uuid)
        else:
            logger.error("wrong state!")
            return redirect('experiment_detail', experiment_uuid=experiment_uuid)

        if not is_emulab_stage(experiment.stage):
            # should check reservation
            session_req = generate_experiment_session_request(request, experiment)
            if session_req is None:
                return render(request, 'experiment_initiate.html', {'experiment': experiment,
                                                                    'experimenter': experiment.experimenter.all(),
                                                                    'experiment_reservations': experiment_reservations,
                                                                    'msg': '* [ERROR] Invalid entry for "Definition".'})

            if experiment.state < Experiment.STATE_DEPLOYING:  # and if reservation is_valid
                experiment_state_change(request, experiment, "ready")
            else:
                # should do something to tell node agent to terminate experiment
                # ...
                experiment_state_change(request, experiment, "not_started")
            return redirect('experiment_detail', experiment_uuid=experiment_uuid)

        else:
            is_success = initiate_emulab_instance(request, experiment)
            if is_success:
                status = query_emulab_instance_status(request, experiment)
                # add a thread here
                # t = threading.Thread(target=bg_deploy_emulab,args=(request, experiment), daemon=True)
                # t.setDaemon(True)
                # t.start()
                return redirect('experiment_detail', experiment_uuid=experiment_uuid)
            else:
                logger.error('Need to pop up something to indicate "Retry later"')
    return render(request, 'experiment_initiate.html',
                  {'experiment': experiment, 'experimenter': experiment.experimenter.all(),
                   'experiment_reservations': experiment_reservations})


@login_required()
def experiment_manifest(request, experiment_uuid):
    """
    render manifest information for the experiment

    :param request:
    :param experiment_uuid:
    :return:
    """
    experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))

    manifest = None
    user_manifest = ''
    if is_emulab_stage(experiment.stage):
        manifest = get_emulab_manifest(request, experiment)
    else:
        manifest = generate_experiment_session_request(request, experiment)

    if (experiment.stage == "Development" and experiment.state == Experiment.STATE_DEPLOYED) \
            or (experiment.stage == "Idle" and experiment.state == Experiment.STATE_IDLE):
        user_manifest = experiment.message

    if manifest is not None:
        return render(request, 'experiment_manifest.html',
                      {'experiment': experiment,
                       'manifest': manifest,
                       'profile': experiment.profile.profile,
                       'user_manifest': user_manifest})
    else:
        return render(request, 'experiment_manifest.html',
                      {'experiment': experiment,
                       'manifest': "",
                       'profile': experiment.profile.profile,
                       'user_manifest': user_manifest})

@login_required()
def experiment_link_update(request, experiment_uuid):
    """
    render manifest information for the experiment

    :param request:
    :param experiment_uuid:
    :return:
    """
    experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))

    if request.method == "POST":
        form = ExperimentLinkUpdateForm(request.POST, instance=experiment)

        if form.is_valid():
            link = form.cleaned_data.get("cloudstorage_link")
            experiment.cloudstorage_link = link
            experiment.save()
            return redirect('experiment_detail', experiment_uuid=str(experiment.uuid))
    
    form = ExperimentLinkUpdateForm(instance=experiment)
    return render(request, 'experiment_link_update.html',
                      {'experiment': experiment,
                       'experiment_uuid': str(experiment_uuid),
                       'form' : form,})