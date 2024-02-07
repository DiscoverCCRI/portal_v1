import logging
from pprint import pprint

from jenkins import JenkinsException

from cicd import jenkins_server as js

JENKINS_DEPLOY_DEV_JOB = "deploy-experiment-development"
JENKINS_EXAMPLE_REPO = (
    "https://gitlab.flux.utah.edu/powder-profiles/srslte-docker-sim.git"
)

logger = logging.getLogger(__name__)


def deploy_experiment(experiment, host):
    if (
        experiment.stage.upper() == "DEVELOPMENT"
    ):  # experiment.state == Experiment.STATE_PROVISIONING and
        params = {"host": host, "repo": JENKINS_EXAMPLE_REPO}
        next_bn = js.get_job_info(JENKINS_DEPLOY_DEV_JOB)["nextBuildNumber"]
        output = js.build_job(JENKINS_DEPLOY_DEV_JOB, parameters=params)
        logger.info(output)
    else:
        next_bn = -1

    return next_bn


def info_deployment(experiment):
    try:
        buildnumber = experiment.deployment_bn
        logger.warning("[{}] buildnumber = {}".format(experiment.name, buildnumber))
        info = js.get_build_console_output(JENKINS_DEPLOY_DEV_JOB, buildnumber)
        response = "[job #{0}]: ".format(buildnumber) + "<br />".join(info.split("\n"))
    except JenkinsException as err:
        logger.error(err)
        response = "[job #?]: Unable to locate job"
    # pprint(response)
    return response
