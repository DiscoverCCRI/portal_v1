import json
import logging
import os
import time
import uuid
from datetime import datetime

import aerpawgw_client
from aerpawgw_client.rest import ApiException
from django.utils import timezone

from accounts.models import AerpawUser
from profiles.models import Profile
from profiles.profiles import is_emulab_stage, parse_profile
from projects.models import Project
from reservations.models import Reservation
from resources.models import Resource
from resources.resources import emulab_location_to_urn
from usercomms.usercomms import portal_mail, ack_mail
from .jenkins_api import deploy_experiment, info_deployment
from .models import Experiment

logger = logging.getLogger(__name__)


def create_new_experiment(request, form, project_id):
    """

    :param request:
    :param form:
    :return:
    """
    experiment = Experiment()
    experiment.uuid = uuid.uuid4()
    # request.session['experiment_uuid'] = experiment.uuid
    experiment.name = form.data.getlist('name')[0]
    experiment.github_link = form.data.getlist('github_link')[0]
    try:
        experiment.description = form.data.getlist('description')[0]
        profile = Profile.objects.get(id=int(form.data.getlist('profile')[0]))
        if profile.is_template:
            profile.pk = None
            profile.id = None
            profile.save()
            profile.uuid = uuid.uuid4()
            profile.is_template = False
            profile.name = profile.name + ' (copy)'
            profile.created_by = request.user
            profile.modified_by = request.user
            profile.created_date = timezone.now()
            profile.modified_date = timezone.now()
            profile.project = Project.objects.get(id=str(project_id))
            profile.save()
        experiment.profile = profile
    except ValueError as e:
        print(e)
        experiment.profile = None
    experiment.created_by = request.user
    experiment.created_date = timezone.now()
    experiment.save()

    experiment.project = Project.objects.get(id=str(project_id))
    experiment.experimenter.add(request.user)
    experiment.modified_by = experiment.created_by
    experiment.modified_date = experiment.created_date
    experiment.stage = 'Idle'
    experiment.save()

    # experimenter_id_list = form.data.getlist('experimenter')
    # update_experimenter(experiment, experimenter_id_list)
    # experiment.save()

    # try:
    #     experiment.project = Project.objects.get(id=int(form.data.getlist('project')[0]))
    #     experiment.project.experiment_of_project.add(experiment)
    #     experiment.profile = Profile.objects.get(id=int(form.data.getlist('profile')[0]))
    #     experiment.save()
    # except ValueError as e:
    #     print(e)
    #     experiment.project = None

    # try:
    #    reservation_id_list=form.data.getlist('reservation')
    #    if not reservation_id_list:
    #        reservation_id = reservation_id_list[0]
    #        experiment.reservations = Reservation.objects.get(id=int(reservation_id))
    # except ValueError as e:
    #    print(e)
    #    experiment.reservations= None
    # experiment.save()

    return str(experiment.uuid)


def update_experimenter(experiment, experimenter_id_list):
    """

    :param experiment:
    :param experimenter_id_list:
    :return:
    """
    # clear current experimenter
    experiment.experimenter.clear()
    # add members from experimenter_id_update_list
    for experimenter_id in experimenter_id_list:
        experiment_experimenter = AerpawUser.objects.get(id=int(experimenter_id))
        experiment.experimenter.add(experiment_experimenter)


def update_existing_experiment(request, experiment, form, prev_stage, prev_state):
    """
    Update AERPAW Experiment Stage and/or State

    :param request:
    :param form:
    :return:
    """
    try:
        logger.warning("stage prev {}, new {}".format(prev_stage, experiment.stage))
        logger.warning("state prev {}, new {}".format(prev_state, experiment.state))
        experiment.modified_by = request.user
        experiment.modified_date = timezone.now()
        experiment.save()

        if prev_stage != experiment.stage:
            if experiment.stage == 'Testbed':
                # User click submit button in 2 scenarios:
                # - Development -> Testbed
                # - Idle -> Testbed
                if experiment.state == Experiment.STATE_DEPLOYED \
                        and prev_stage == 'Development':
                    # do some trick, roll back to previous stage temporarily to
                    # exit with save first (request msg send inside the experiment_state_change())
                    current_new_stage = experiment.stage
                    experiment.stage = prev_stage
                    experiment_state_change(request, experiment, 'terminating')
                    experiment.stage = current_new_stage
                    experiment.save()

                # submit to testbed
                session_req = generate_experiment_session_request(request, experiment)
                if session_req is None:
                    raise Exception
                experiment.submit()
                experiment.save()
                send_request_to_testbed(request, experiment)
                kwargs = {'experiment_name': str(experiment)}
                ack_mail(
                    template='experiment_submit', user_name=request.user.display_name,
                    user_email=request.user.email, **kwargs
                )
            elif experiment.stage == 'Idle':
                # Operator finished testbed testing, change the experiment back to Idle
                experiment.idle()
                experiment.save()

            if not request.user.is_operator() and experiment.state != Experiment.STATE_SUBMIT:
                # temporary, currently not handling anything besides TESTBED
                logger.warning("Currently not handling anything besides TESTBED!")
                experiment.stage = prev_stage
                experiment.save()

    except ValueError as e:
        print(e)
    return str(experiment.uuid)


def send_request_to_testbed(request, experiment):
    action = None
    if is_emulab_stage(experiment.stage):
        return  # do nothing, this function is not for emulab
    if experiment.state == Experiment.STATE_DEPLOYING:
        action = 'START'
    elif experiment.state == Experiment.STATE_IDLE:
        action = 'SAVE and EXIT'
    elif experiment.state == Experiment.STATE_SUBMIT:
        action = 'SUBMIT'

    if action:
        subject = 'Aerpaw Experiment Action Session Request: {} {}:{}'.format(action,
                                                                              str(experiment.uuid),
                                                                              experiment.stage)
        message = "[{}]\n\n".format(subject) \
                  + "Experiment Name: {}\n".format(str(experiment)) \
                  + "Project: {}\n".format(experiment.project) \
                  + "User: {}\n\n".format(request.user.username)
        if action == 'SUBMIT':
            message += "Testbed Experiment Description: {}\n\n".format(experiment.submit_notes)
        if action == 'START' or action == 'SUBMIT':
            try:
                session_req = generate_experiment_session_request(request, experiment)
                session_req_json=json.dumps(session_req) #dict to json str
            except TypeError:
                session_req_json=json.dumps({"experiment_resource_definition":"Unable to serialize the object"})
            message += "Experiment {} Session Request:\n{}\n".format(experiment.stage, session_req_json)

        receivers = []
        operators = list(AerpawUser.objects.filter(groups__name='operator'))
        for operator in operators:
            receivers.append(operator)
        logger.warning("send_email:\n" + subject)
        logger.warning(message)
        portal_mail(subject=subject, body_message=message, sender=request.user,
                    receivers=receivers,
                    reference_note=None, reference_url=None)
        if action == 'START':
            kwargs = {'experiment_name': str(experiment)}
            ack_mail(
                template='experiment_init', user_name=request.user.display_name,
                user_email=request.user.email, **kwargs
            )


def update_experiment_reservations(experiment, experiment_reservation_id_list):
    """

    :param experiment:
    :param experiment_reservation_id_list:
    :return:
    """
    # clear current reservations
    # experiment.reservations.clear()
    # add reservations from experimenter_id_update_list
    for res_id in experiment_reservation_id_list:
        experiment_reservation = Reservation.objects.get(id=int(res_id))
        experiment.reservations.add(experiment_reservation)


def delete_existing_experiment(request, experiment):
    """

    :param request:
    :param experiment:
    :return:
    """
    try:
        if is_emulab_stage(experiment.stage):
            # instance on emulab should be terminated first
            emulab_deleted = terminate_emulab_instance(request, experiment)
            if emulab_deleted is False:
                return False
        experiment.delete()
        return True
    except Exception as e:
        print(e)
    return False


def get_experiment_list(request):
    """

    :param request:
    :return:
    """
    if request.user.is_operator() or request.user.is_site_admin():
        experiments = Experiment.objects.order_by('created_date')
    else:
        experiments = Experiment.objects.filter(experimenter__uuid=request.user.uuid).order_by('created_date').distinct()
    return experiments


def experiment_state_change(request, experiment, backend_status):
    automated = False

    logger.warning(
        '[{}] current state={}, backend_status={}'.format(experiment.name, experiment.state,
                                                          backend_status))

    if backend_status == 'unknown':
        return

    elif backend_status == 'not_started' or backend_status == 'terminating':
        # the emulab is not doing anything or soon be idle
        if experiment.state != Experiment.STATE_IDLE:
            if experiment.can_snapshot():
                experiment.is_snapshotted = True
            experiment.idle()
            experiment.save()
            send_request_to_testbed(request, experiment)
        return

    elif backend_status != 'ready':
        # possible status: created, provisioning, provisioned ...
        # the emulab is provisioning the node or booting
        if experiment.state < Experiment.STATE_PROVISIONING:
            experiment.provision()
            experiment.save()
        return

    elif backend_status == 'ready':
        if experiment.state < Experiment.STATE_DEPLOYING:
            prev_state = experiment.state
            experiment.deploy()  # change state first so get_emulab_manifest can function properly
            experiment.save()

            if is_emulab_stage(experiment.stage):
                manifest = get_emulab_manifest(request, experiment)
            else:
                manifest = generate_experiment_session_request(request, experiment)

            if manifest != None:
                send_request_to_testbed(request, experiment)
                # since new run is started, reset is_snapshotted flag and message
                experiment.is_snapshotted = False
                experiment.message = ""
                experiment.save()
            else:
                logger.error('!! Error - Manifest is not available')
                experiment.state = prev_state  # revert state
                experiment.save()
                return

            if automated and is_emulab_stage(experiment.stage):
                # currently just test for emulab development node
                hostname = manifest['nodes'][0]['hostname']
                logger.warning('[{}] deployment host: {}'.format(experiment.name, hostname))
                jenkins_bn = deploy_experiment(experiment, hostname)  # for testing jenkins_bn = 19
                logger.warning(
                    '[{}] deployment build number: {}'.format(experiment.name, jenkins_bn))
                experiment.deployment_bn = jenkins_bn
            return

        if experiment.state == Experiment.STATE_DEPLOYING:
            if automated:
                console_output = info_deployment(experiment)
                output_ending = console_output[len(console_output) - 40:]  # last 40 chars
                logger.warning("[{}] deployment output: {}".format(experiment.name, output_ending))
                # check "Finished: SUCCESS"
                if "Finished: SUCCESS" in output_ending:
                    experiment.ready()
                    experiment.save()


def generate_experiment_session_request(request, experiment):
    """
    Generate experiment session request from resource definition and database or emulab resource
    This should be rewritten and update via some defined openapi

    :param request:
    :param experiment:
    """
    session_req = {}
    if experiment.stage != "Idle":
        session_req['ap_msg_type'] = 'experiment_{}_session_request'.format(
            experiment.stage).lower()

    resources = parse_profile(request, experiment.profile.profile)
    if resources is None:
        return None
    resource_def = {'experiment_uuid': str(experiment.uuid), 'experiment_idx': experiment.id,
                    'nodes': resources}
    session_req['experiment_resource_definition'] = resource_def

    user = {'username': experiment.created_by.username.split('@')[0],
            'publickey': experiment.created_by.publickey}
    session_req['user'] = user

    return session_req


##################################################################################
# Following functions are for emulab only !
def initiate_emulab_instance(request, experiment):
    """
    Initiate experiment instance on Emulab

    :param request:
    :param experiment:
    :return: True - success, False - otherwise
    """
    status = query_emulab_instance_status(request, experiment)

    if status == '':
        logger.error('Do nothing since we cannot get the status from emulab')
        return False
    elif status != 'not_started':
        logger.warning('emulab experiment already started')
        logger.error(
            '[testing code] Stopping emulab instance now, but we might want to move this stop to another button')
        return terminate_emulab_instance(request, experiment)

    '''
    # user doesn't care about emulab profile.
    # changing design to always use the default 1 node profie in emulab
    # the status is 'not_started': create an instance of the API class
    # before that, make sure profile existed in emulab
    emulab_profile_name = get_emulab_profile_name(experiment.profile.project.name,
                                                  experiment.profile.name)
    if query_emulab_profile(request, emulab_profile_name) is None:
        create_new_emulab_profile(request, experiment.profile)
    '''

    api_instance = aerpawgw_client.ExperimentApi()
    location = 'RENCIEmulab'
    # location = experiment.reservation.location
    logger.error(
        '[IMPORTANT] We should check if Reservation exists, and use that Reservation.location')
    logger.error('[IMPORTANT] now just hard-coded default: {}'.format(location))
    experiment_body = aerpawgw_client.Experiment(name=experiment.name,
                                                 profile='aerpaw-default',
                                                 # profile=emulab_profile_name,
                                                 cluster=emulab_location_to_urn(location))
    experiment.save()
    try:
        # create a experiment
        api_response = api_instance.create_experiment(experiment_body)
    except ApiException as e:
        logger.error("Exception when calling ExperimentApi->create_experiment: %s\n" % e)
        return False

    return True


def bg_deploy_emulab(request, experiment):
    while True:
        time.sleep(10)
        logger.warning('{} bg_deploy_emulab()'.format(datetime.now()))
        query_emulab_instance_status(request, experiment)
        # if experiment.state >= Experiment.STATE_DEPLOYED or experiment.state == Experiment.STATE_IDLE:
        if experiment.state >= Experiment.STATE_DEPLOYING or experiment.state == Experiment.STATE_IDLE:
            break


def query_emulab_instance_status(request, experiment):
    """
    Query the experiment instance status on Emulab

    :param request:
    :param experiment:
    :return status of emulab experiment: str, including 'not_started', 'provisioning',
                                             'provisioned', 'ready', 'failed'
    """
    if not os.getenv('AERPAWGW_HOST') \
            or not os.getenv('AERPAWGW_PORT') \
            or not os.getenv('AERPAWGW_VERSION'):
        return ''
    if not is_emulab_stage(experiment.stage):
        return ''

    api_instance = aerpawgw_client.ExperimentApi()
    backend_status = 'not_started'
    try:
        # get status of specific experiment
        emulab_exp = api_instance.query_experiment(experiment.name)
        backend_status = emulab_exp.status
        logger.info(emulab_exp)

    except ApiException as e:
        logger.warning("Exception e: {}".format(e.body))
        if e.status == 404:
            # no such experiment, means that the experiment is idle.
            logger.warning("backend_status is 'not_started' since e.status = {}".format(e.status))
        elif e.status == 500:
            if 'No available physical nodes' in e.body:
                backend_status = 'terminating'
                logger.warning("backend_status is 'not_started' because no available resource(s)")
            else:
                backend_status = 'unknown'

    # call function to change state accordingly
    experiment_state_change(request, experiment, backend_status)

    return backend_status


def terminate_emulab_instance(request, experiment):
    """
    terminate the experiment instance on Emulab, the status has to be ready or failed.

    :param request:
    :param experiment:
    :return : True - success, False - try later
    """
    status = query_emulab_instance_status(request, experiment)

    if status == '':
        logger.error('Do nothing since we cannot get the status from emulab')
        return False
    elif status == 'not_started':
        return True
    elif status != 'ready' and status != 'failed':
        logger.error('The instance operation is in progress. Please try later.')
        return False
    api_instance = aerpawgw_client.ExperimentApi()
    try:
        # delete experiment
        api_instance.delete_experiment(experiment.name)
        experiment.save()
    except ApiException as e:
        logger.error("Exception when calling ExperimentApi->delete_experiment: %s\n" % e)
    return True


def generate_emulab_manifest(request, experiment, emulab_resource):
    """
    Generate manifest from user profile and database or emulab resource

    :param request:
    :param experiment:
    :param emulab_resource : class Resource of aerpawgw_client. vnodes are what we need
    """
    if experiment.profile is None:
        return None
    json_profile = experiment.profile.profile
    if not json_profile.startswith('[{'):
        logger.error('profile should be json consists of nodes')
        logger.error(json_profile)
        return None
    logger.info(json_profile)
    nodes = json.loads(json_profile)

    if emulab_resource is not None:
        logger.warning("emulab resource hostname:{}, ip:{}".format(
            emulab_resource.vnodes[0].hostname, emulab_resource.vnodes[0].ipv4))
    for reqnode in nodes:
        try:
            if 'idx' not in reqnode.keys() \
                    or 'name' not in reqnode.keys() \
                    or 'hardware_type' not in reqnode.keys() \
                    or 'component_id' not in reqnode.keys():
                logger.error("Json is not valid")
                raise Exception
            if emulab_resource is None:
                resource = Resource.objects.get(resourceType=reqnode['hardware_type'],
                                                name=reqnode['component_id'])
                reqnode['ipv4'] = resource.ip_address
                reqnode['hostname'] = resource.hostname
            else:
                reqnode['ipv4'] = emulab_resource.vnodes[0].ipv4
                reqnode['hostname'] = emulab_resource.vnodes[0].hostname
        except Resource.DoesNotExist:
            logger.error("we are not able to find {}/{}".format(reqnode['hardware_type'],
                                                                reqnode['component_id']))
            return None
        except:
            logger.error("json format is not expected")
            return None
    if len(nodes) < 1:
        logger.error("return manifest as None")
        return None
    else:
        logger.warning(nodes)
        manifest = {}
        manifest['experiment_id'] = str(experiment.uuid)
        manifest['idx'] = experiment.id
        manifest['mode'] = experiment.stage
        manifest['nodes'] = nodes
        user = {}
        user['username'] = request.user.username.split('@')[0]
        user['publickey'] = request.user.publickey
        manifest['user'] = user
        return manifest


def get_emulab_manifest(request, experiment):
    """
    Get manifest from Emulab, the status has to be ready.

    :param request:
    :param experiment:
    :return : class Resource of aerpawgw_client. rspec and vnodes are what we need
    """
    if experiment.state < Experiment.STATE_DEPLOYING:
        return None
    api_instance = aerpawgw_client.ResourcesApi()
    try:
        emulab_resource = api_instance.list_resources(experiment=experiment.name)
        logger.info(emulab_resource)
        return generate_emulab_manifest(request, experiment, emulab_resource)
    except ApiException as e:
        logger.error("Exception when calling ResourcesApi->list_resources: %s\n" % e)
    return None


def insert_user_to_emulab(request, user, pubkey, experiment):
    """
    Insert user and pubkey to emulab instance.

    :param request:
    :param user: str
    :param pubkey: str
    :param experiment:
    :return: None
    """
    api_instance = aerpawgw_client.UserApi()
    body = aerpawgw_client.Userkey(user, pubkey)
    try:
        # add/update user and sshkey on experiment nodes
        logger.warning("insert user %s and public key to the instance\n" % user)
        api_instance.adduser(body, experiment.name)

    except ApiException as e:
        logger.error("Exception when calling UserApi->adduser: %s\n" % e)


'''
def get_emulab_instances(request):
    api_instance = aerpawgw_client.ExperimentApi()

    try:
        # get experiment(s) under user
        api_response = api_instance.get_experiments()
    except ApiException as e:
        logger.error("Exception when calling ExperimentApi->get_experiments: %s\n" % e)

    emulab_experiments = []
    for emulab_e in api_response:  # aerpawgw_client.models.experiment.Experiment
        e = Experiment()
        e.name = emulab_e.name
        e.created_date = datetime.fromtimestamp(int(emulab_e.start))
        e.created_by = request.user
        e.uuid = emulab_e.uuid

        # we need a field to store emulab eid (project+name)
        # borrow description field first.
        emulab_eid = '{},{}'.format(emulab_e.project, emulab_e.name)
        e.description = emulab_eid
        # e.emulab_eid = emulab_eid

        # e.project =
        # e.stage =
        emulab_experiments.append(e)

    return emulab_experiments
'''
