import os
from pathlib import Path

import jenkins
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# load environment variables
env_path = Path('.') / '.env'
load_dotenv(verbose=True, dotenv_path=env_path)

# TODO: pull username/password from admin config for operator ci/cd deployment
jenkins_server = jenkins.Jenkins(
    str(os.getenv('JENKINS_API_URL')),
    username=str(os.getenv('JENKINS_API_USER')),
    password=str(os.getenv('JENKINS_API_PASS'))
)
jenkins_server._session.verify = False
