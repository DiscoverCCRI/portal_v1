from django import forms

from .models import Cicd, CicdHostInfo


class CicdCreateHostInfoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CicdCreateHostInfoForm, self).__init__(*args, **kwargs)
        self.fields['fqdn_or_ip'].label = 'FQDN or IP'
        self.fields['nginx_http_port'].label = 'HTTP port'
        self.fields['nginx_https_port'].label = 'HTTPS port'
        self.fields['docker_subnet'].label = 'Docker Subnet'
        self.fields['jenkins_service_agent_port'].label = 'Jenkins Service Agent port'
        self.fields['jenkins_ssh_agent_port'].label = 'Jenkins SSH Agent port'
        self.fields['gitea_ssh_agent_port'].label = 'Gitea SSH Agent port'

    class Meta:
        model = CicdHostInfo
        fields = (
            'fqdn_or_ip',
            'nginx_http_port',
            'nginx_https_port',
            'docker_subnet',
            'jenkins_service_agent_port',
            'jenkins_ssh_agent_port',
            'gitea_ssh_agent_port',
        )


class CicdUpdateHostInfoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CicdUpdateHostInfoForm, self).__init__(*args, **kwargs)
        self.fields['fqdn_or_ip'].label = 'FQDN or IP'
        self.fields['nginx_http_port'].label = 'HTTP port'
        self.fields['nginx_https_port'].label = 'HTTPS port'
        self.fields['docker_subnet'].label = 'Docker Subnet'
        self.fields['jenkins_service_agent_port'].label = 'Jenkins Service Agent port'
        self.fields['jenkins_ssh_agent_port'].label = 'Jenkins SSH Agent port'
        self.fields['gitea_ssh_agent_port'].label = 'Gitea SSH Agent port'

    class Meta:
        model = CicdHostInfo
        fields = (
            'fqdn_or_ip',
            'nginx_http_port',
            'nginx_https_port',
            'docker_subnet',
            'jenkins_service_agent_port',
            'jenkins_ssh_agent_port',
            'gitea_ssh_agent_port',
        )


class CicdCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CicdCreateForm, self).__init__(*args, **kwargs)
        self.fields['jenkins_admin_password'].label = 'Admin Password'

    class Meta:
        model = Cicd
        fields = (
            'jenkins_admin_password',
        )
