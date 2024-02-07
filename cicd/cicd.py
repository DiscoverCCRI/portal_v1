from django.contrib import messages

from resources.resources import *

from .models import Cicd, CicdHostInfo

logger = logging.getLogger(__name__)


def get_cicd_list(request):
    """

    :param request:
    :return:
    """
    cicds = Cicd.objects.order_by("name")
    return cicds


def get_cicd_host_info_list(request):
    """

    :param request:
    :return:
    """
    cicd_his = CicdHostInfo.objects.order_by("name")
    return cicd_his


def create_new_cicd(request, form, project_uuid):
    """

    :param request:
    :param form:
    :param project_uuid:
    :return:
    """
    cicd = Cicd()
    # base information
    cicd.uuid = uuid.uuid4()
    cicd.aerpaw_uuid = project_uuid
    # domain and port information
    cicd.cicd_host_info = CicdHostInfo.objects.filter(is_allocated=False).first()
    # TODO: handle case of no available allocation
    if not cicd.cicd_host_info:
        messages.error(
            request,
            "ERROR: All available CI/CD resource connections have already been allocated, \
        contact an Administrator for further information",
        )
        return None
    # update cicd_host_info object as allocated
    cicd.cicd_host_info.is_allocated = True
    cicd.cicd_host_info.project_uuid = cicd.aerpaw_uuid
    cicd.cicd_host_info.save()
    # name and description
    cicd.name = cicd.cicd_host_info.name
    cicd.description = cicd.cicd_host_info.description
    # admin information
    cicd.jenkins_admin_id = "aerpaw"
    cicd.jenkins_admin_name = request.user.username
    cicd.jenkins_admin_password = form.data.getlist("jenkins_admin_password")[0]
    # user information
    cicd.created_by = request.user
    cicd.modified_by = cicd.created_by
    # date information
    cicd.created_date = timezone.now()
    cicd.modified_date = cicd.created_date
    cicd.save()

    return str(cicd.uuid)


def create_new_cicd_host_info(request, form):
    """

    :param request:
    :param form:
    :return:
    """
    cicd_hi = CicdHostInfo()
    cicd_hi.uuid = uuid.uuid4()
    cicd_hi.fqdn_or_ip = form.data.getlist("fqdn_or_ip")[0]
    cicd_hi.nginx_http_port = form.data.getlist("nginx_http_port")[0]
    cicd_hi.nginx_https_port = form.data.getlist("nginx_https_port")[0]
    cicd_hi.name = (
        str(cicd_hi.fqdn_or_ip)
        + " ("
        + str(cicd_hi.nginx_http_port)
        + " / "
        + str(cicd_hi.nginx_https_port)
        + ")"
    )
    cicd_hi.docker_subnet = form.data.getlist("docker_subnet")[0]
    cicd_hi.jenkins_service_agent_port = form.data.getlist(
        "jenkins_service_agent_port"
    )[0]
    cicd_hi.jenkins_ssh_agent_port = form.data.getlist("jenkins_ssh_agent_port")[0]
    cicd_hi.gitea_ssh_agent_port = form.data.getlist("gitea_ssh_agent_port")[0]
    cicd_hi.description = """{3}: 
    fqdn_or_ip = {0}, 
    nginx_http_port = {1}, 
    nginx_https_port = {2}, 
    name = {3}, 
    docker_subnet = {4}, 
    jenkins_service_agent_port = {5}, 
    jenkins_ssh_agent_port = {6}, 
    gitea_ssh_agent_port = {7}
    """.format(
        cicd_hi.fqdn_or_ip,
        cicd_hi.nginx_http_port,
        cicd_hi.nginx_https_port,
        cicd_hi.name,
        cicd_hi.docker_subnet,
        cicd_hi.jenkins_service_agent_port,
        cicd_hi.jenkins_ssh_agent_port,
        cicd_hi.gitea_ssh_agent_port,
    )
    # user information
    cicd_hi.created_by = request.user
    cicd_hi.modified_by = cicd_hi.created_by
    # date information
    cicd_hi.created_date = timezone.now()
    cicd_hi.modified_date = cicd_hi.created_date
    cicd_hi.save()

    return str(cicd_hi.uuid)


def update_existing_cicd_host_info(request, form, cicd_hi):
    """

    :param request:
    :param form:
    :param cicd_hi:
    :return:
    """
    cicd_hi.fqdn_or_ip = form.data.getlist("fqdn_or_ip")[0]
    cicd_hi.nginx_http_port = form.data.getlist("nginx_http_port")[0]
    cicd_hi.nginx_https_port = form.data.getlist("nginx_https_port")[0]
    cicd_hi.name = (
        str(cicd_hi.fqdn_or_ip)
        + " ("
        + str(cicd_hi.nginx_http_port)
        + " / "
        + str(cicd_hi.nginx_https_port)
        + ")"
    )
    cicd_hi.docker_subnet = form.data.getlist("docker_subnet")[0]
    cicd_hi.jenkins_service_agent_port = form.data.getlist(
        "jenkins_service_agent_port"
    )[0]
    cicd_hi.jenkins_ssh_agent_port = form.data.getlist("jenkins_ssh_agent_port")[0]
    cicd_hi.gitea_ssh_agent_port = form.data.getlist("gitea_ssh_agent_port")[0]
    cicd_hi.description = """{3}: 
    fqdn_or_ip = {0}, 
    nginx_http_port = {1}, 
    nginx_https_port = {2}, 
    name = {3}, 
    docker_subnet = {4}, 
    jenkins_service_agent_port = {5}, 
    jenkins_ssh_agent_port = {6}, 
    gitea_ssh_agent_port = {7}
    """.format(
        cicd_hi.fqdn_or_ip,
        cicd_hi.nginx_http_port,
        cicd_hi.nginx_https_port,
        cicd_hi.name,
        cicd_hi.docker_subnet,
        cicd_hi.jenkins_service_agent_port,
        cicd_hi.jenkins_ssh_agent_port,
        cicd_hi.gitea_ssh_agent_port,
    )
    # user information
    cicd_hi.modified_by = request.user
    # date information
    cicd_hi.modified_date = timezone.now()
    cicd_hi.save()

    return str(cicd_hi.uuid)
