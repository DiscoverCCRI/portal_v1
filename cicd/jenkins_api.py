import logging
from datetime import datetime
from pprint import pprint
from uuid import UUID

import aerpawgw_client
import jenkins
from aerpawgw_client.rest import ApiException
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from jenkins import JenkinsException

from accounts.models import AerpawUser
from profiles.models import Profile
from profiles.profiles import *
from projects.models import Project
from reservations.models import Reservation
from resources.resources import *

from . import jenkins_server as js
from .models import Cicd

# logger = logging.getLogger(__name__)
#
# # TODO: pull username/password from admin config for operator ci/cd deployment
# jenkins_server = jenkins.Jenkins(
#     'https://aerpaw-ci.renci.org/jenkins',
#     username='admin',
#     password='xxxxxxx'
# )
# jenkins_server._session.verify = False

# params = { \
#     'AERPAW_UUID': 'a355f97e-2ccf-4d53-9821-6c3099193e97', \
#     'FQDN_OR_IP': 'aerpaw-dev.renci.org', \
#     'JENKINS_ADMIN_ID': 'admin', \
#     'JENKINS_ADMIN_NAME': 'TEST Admin', \
#     'JENKINS_ADMIN_PASSWORD': 'password123!', \
#     'jenkins_service_agent_port': '50001', \
#     'JENKINS_SSH_AGENT_PORT': '50023', \
#     'NGINX_HTTP_PORT': '9090', \
#     'NGINX_HTTPS_PORT': '9443' \
#  \
#     }


def deploy_cicd_environment(cicd_uuid):
    cicd = get_object_or_404(Cicd, uuid=UUID(str(cicd_uuid)))
    print(cicd.aerpaw_uuid)
    if not cicd.aerpaw_uuid == "00000000-0000-0000-0000-000000000000":
        params = {
            "AERPAW_UUID": str(cicd.aerpaw_uuid),
            "AERPAW_COMMAND": "DEPLOY",
            "FQDN_OR_IP": str(cicd.cicd_host_info.fqdn_or_ip),
            "DOCKER_SUBNET": str(cicd.cicd_host_info.docker_subnet),
            "JENKINS_ADMIN_ID": str(cicd.jenkins_admin_id),
            "JENKINS_ADMIN_NAME": str(cicd.jenkins_admin_name),
            "JENKINS_ADMIN_PASSWORD": str(cicd.jenkins_admin_password),
            "JENKINS_SERVICE_AGENT_PORT": str(
                cicd.cicd_host_info.jenkins_service_agent_port
            ),
            "JENKINS_SSH_AGENT_PORT": str(cicd.cicd_host_info.jenkins_ssh_agent_port),
            "NGINX_HTTP_PORT": str(cicd.cicd_host_info.nginx_http_port),
            "NGINX_HTTPS_PORT": str(cicd.cicd_host_info.nginx_https_port),
            "GITEA_SERVICE_AGENT_PORT": str(cicd.cicd_host_info.gitea_ssh_agent_port),
        }
        next_bn = js.get_job_info("manage-aerpaw-cicd")["nextBuildNumber"]
        output = js.build_job("manage-aerpaw-cicd", parameters=params)
        # print(output)
    else:
        next_bn = -1

    return next_bn


def start_cicd_environment(cicd_uuid):
    cicd = get_object_or_404(Cicd, uuid=UUID(str(cicd_uuid)))
    params = {"AERPAW_UUID": str(cicd.aerpaw_uuid), "AERPAW_COMMAND": "START"}
    print(params)
    next_bn = js.get_job_info("manage-aerpaw-cicd")["nextBuildNumber"]
    output = js.build_job("manage-aerpaw-cicd", parameters=params)
    # print(output)
    # info = js.get_build_console_output('aerpaw-cicd-control', next_bn)
    # pprint(info)
    return next_bn


def stop_cicd_environment(cicd_uuid):
    cicd = get_object_or_404(Cicd, uuid=UUID(str(cicd_uuid)))
    params = {"AERPAW_UUID": str(cicd.aerpaw_uuid), "AERPAW_COMMAND": "STOP"}
    print(params)
    next_bn = js.get_job_info("manage-aerpaw-cicd")["nextBuildNumber"]
    output = js.build_job("manage-aerpaw-cicd", parameters=params)
    # print(output)
    # info = js.get_build_console_output('aerpaw-cicd-control', next_bn)
    # pprint(info)
    return next_bn


def purge_cicd_environment(cicd_uuid):
    cicd = get_object_or_404(Cicd, uuid=UUID(str(cicd_uuid)))
    if not cicd.aerpaw_uuid == "00000000-0000-0000-0000-000000000000":
        params = {"AERPAW_UUID": str(cicd.aerpaw_uuid), "AERPAW_COMMAND": "PURGE"}
        print(params)
        next_bn = js.get_job_info("manage-aerpaw-cicd")["nextBuildNumber"]
        output = js.build_job("manage-aerpaw-cicd", parameters=params)
        # print(output)
        # info = js.get_build_console_output('aerpaw-cicd-control', next_bn)
        # pprint(info)
    else:
        next_bn = -1
    return next_bn


def info_cicd_environment(cicd_uuid):
    # next_bn = js.get_job_info('manage-aerpaw-cicd')['nextBuildNumber']
    # output = js.build_job('manage-aerpaw-cicd', parameters=params)
    try:
        next_bn = js.get_job_info("manage-aerpaw-cicd")["nextBuildNumber"]
        info = js.get_build_console_output("manage-aerpaw-cicd", int(next_bn - 1))
        response = "[job #{0}]: ".format(str(next_bn - 1)) + "<br />".join(
            info.split("\n")
        )
    except JenkinsException as err:
        print(err)
        response = "[job #?]: Unable to locate job"
    # pprint(info)

    # print(response)
    return response
