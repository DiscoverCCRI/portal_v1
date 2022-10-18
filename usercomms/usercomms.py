from uuid import uuid4

from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.utils import timezone

from usercomms.models import Usercomms
from accounts.models import AerpawUser


def ack_mail(template: str, user_name: str, user_email: str, **kwargs) -> None:
    """
    Acknowledgement email sent to User making request

    :param template: ['project_join', 'experiment_init', 'experiment_submit']
    :param user_name:
    :param user_email:
    :param kwargs: Additional fields passed as keyword args
        project_join      -> project_name, project_owner
        experiment_init   -> experiment_name
        experiment_submit -> experiment_name
    :return:
    """
    subject = None
    body = None
    if template == 'project_join':
        project_name = kwargs.pop('project_name')
        project_owner = kwargs.pop('project_owner')
        subject = '[DISCOVER] Request to join Project: {0}'.format(project_name)
        body = "Hi {0},\r\n\r\nYour request to join the Project \"{1}\" has been forwarded to \"{2}\", " \
               "the owner of this project.\r\nYou will receive an email confirmation once the Project Owner " \
               "has approved /rejected this request.".format(user_name, project_name, project_owner)
    elif template == 'experiment_init':
        experiment_name = kwargs.pop('experiment_name')
        subject = '[DISCOVER] Request to initiate development for Experiment: {0}'.format(experiment_name)
        body = "Hi {0},\r\n\r\nYour request to initiate a development session for the experiment \"{1}\" has been " \
               "forwarded to DISCOVER Ops.\r\nWhen the Development Session is ready for you, you will receive another " \
               "email with access info.\r\nAs noted in the DISCOVER User Manual, this can take a variable amount of " \
               "time, from minutes to hours.".format(user_name, experiment_name)
    elif template == 'experiment_submit':
        experiment_name = kwargs.pop('experiment_name')
        subject = '[DISCOVER] Request to submit to testbed for Experiment: {0}'.format(experiment_name)
        body = "Hi {0},\r\n\r\nYour request to submit your experiment \"{1}\" for testbed execution has been forwarded " \
               "to DISCOVER Ops, for opportunistic scheduling and subsequent execution.\r\nWhen the Testbed Execution " \
               "is complete, you will receive another email.\r\nAs noted in the DISCOVER User Manual, this can take a " \
               "variable amount of time, typically several days.".format(user_name, experiment_name)
    if subject and body:
        sender = settings.EMAIL_HOST_USER
        send_mail(subject, body, sender, [user_email])


def portal_mail(subject, body_message, sender, receivers, reference_note='', reference_url=''):
    if receivers is None:
        receivers = []
    email_sender = settings.EMAIL_HOST_USER
    if sender == email_sender:
        sender = AerpawUser.objects.filter(is_superuser=True).first()
    email_uuid = uuid4()
    email_body = 'FROM: ' + str(sender.display_name) + \
                 '\r\nREQUEST: ' + str(reference_note) + \
                 '\r\n\r\nURL: ' + str(reference_url) + \
                 '\r\n\r\nMESSAGE: ' + body_message
    body = 'FROM: ' + str(sender.display_name) + \
           '\r\nREQUEST: ' + str(reference_note) + \
           '\r\nMESSAGE: ' + str(body_message)
    receivers_email = []
    for rc in receivers:
        receivers_email.append(rc.email)
    receivers = list(set(receivers))
    receivers_email = list(set(receivers_email))
    try:
        send_mail(subject, email_body, email_sender, receivers_email)
        created_by = sender
        created_date = timezone.now()
        # Sender
        uc = Usercomms(uuid=email_uuid, subject=subject, body=body, sender=created_by,
                       reference_url=None, reference_note=reference_note, reference_user=sender,
                       created_by=created_by, created_date=created_date)
        uc.save()
        for rc in receivers:
            uc.receivers.add(rc)
        uc.save()
        # Receivers
        for rc in receivers:
            uc = Usercomms(uuid=email_uuid, subject=subject, body=email_body, sender=created_by,
                           reference_url=reference_url, reference_note=reference_note, reference_user=rc,
                           created_by=created_by, created_date=created_date)
            uc.save()
            for inner_rc in receivers:
                uc.receivers.add(inner_rc)
            uc.save()
    except BadHeaderError:
        return HttpResponse('Invalid header found.')
