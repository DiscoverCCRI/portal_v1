import unicodedata

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.core.mail import BadHeaderError
from django.http import HttpResponse
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from usercomms.usercomms import portal_mail


def generate_username(oidc_claim_email):
    # Using Python 3 and Django 1.11+, usernames can contain alphanumeric
    # (ascii and unicode), _, @, +, . and - characters. So we normalize
    # it and slice at 150 characters.
    return unicodedata.normalize('NFKC', oidc_claim_email)[:150]


def provider_logout(request):
    # See your provider's documentation for details on if and how this is
    # supported
    redirect_url = 'https://cilogon.org/logout'
    return redirect_url


class MyOIDCAB(OIDCAuthenticationBackend):

    # Extend default user model to include OIDC claims
    def create_user(self, claims):
        user = super(MyOIDCAB, self).create_user(claims)

        # scope openid
        user.oidc_claim_sub = claims.get('sub', '')
        user.oidc_claim_iss = claims.get('iss', '')
        user.oidc_claim_aud = claims.get('aud', '')
        user.oidc_claim_token_id = claims.get('token_id', '')

        # scope email
        user.oidc_claim_email = claims.get('email', '')

        # scope profile
        user.oidc_claim_given_name = claims.get('given_name', '')
        user.oidc_claim_family_name = claims.get('family_name', '')
        user.oidc_claim_name = claims.get('name', '')

        # scope org.cilogon.userinfo
        user.oidc_claim_idp = claims.get('idp', '')
        user.oidc_claim_idp_name = claims.get('idp_name', '')
        user.oidc_claim_eppn = claims.get('eppn', '')
        user.oidc_claim_eptid = claims.get('eptid', '')
        user.oidc_claim_affiliation = claims.get('affiliation', '')
        user.oidc_claim_ou = claims.get('ou', '')
        user.oidc_claim_oidc = claims.get('oidc', '')
        user.oidc_claim_cert_subject_dn = claims.get('cert_subject_dn', '')

        # other values
        user.oidc_claim_acr = claims.get('acr', '')
        user.oidc_claim_entitlement = claims.get('entitlement', '')

        # set default user fields
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.email = claims.get('email', '')

        user.save()
        # set display name
        user.display_name = user.oidc_claim_name + ' (' + user.username + ')'
        # add user to aerpaw_user group
        aug = Group.objects.get(name='aerpaw_user')
        user.groups.add(aug)
        user.save()

        # send welcome email and set initial usercomm message
        sender = settings.EMAIL_HOST_USER
        reference_url = 'https://' + str(self.request.get_host()) + '/accounts/profile'
        body_message = """
Welcome to the AERPAW Portal
        
User manuals, tutorials, and other relevant documentation can be found at the following links; 
please refer to relevant instructions before attempting to use this Portal.
- AERPAW main website: https://www.aerpaw.org
- AERPAW wiki: https://sites.google.com/ncsu.edu/aerpaw-wiki
- AERPAW Acceptable Use Policy: https://sites.google.com/ncsu.edu/aerpaw-wiki/aerpaw-user-manual/2-experiment-web-portal/acceptable-use-policy-aup
"""
        reference_note = 'New user signup for: ' + user.display_name
        subject = '[DISCOVER] Welcome ' + user.display_name + ' to the AERPAW portal!'
        receivers = [user]
        try:
            portal_mail(subject=subject, body_message=body_message, sender=sender, receivers=receivers,
                        reference_note=reference_note, reference_url=reference_url)
            messages.info(self.request, 'Success! Welcome email to user: ' + user.display_name + ' has been sent')
        except BadHeaderError:
            return HttpResponse('Invalid header found.')

        return user

    def update_user(self, user, claims):
        # scope openid
        user.oidc_claim_sub = claims.get('sub', '')
        user.oidc_claim_iss = claims.get('iss', '')
        user.oidc_claim_aud = claims.get('aud', '')
        user.oidc_claim_token_id = claims.get('token_id', '')

        # scope email
        user.oidc_claim_email = claims.get('email', '')

        # scope profile
        user.oidc_claim_given_name = claims.get('given_name', '')
        user.oidc_claim_family_name = claims.get('family_name', '')
        user.oidc_claim_name = claims.get('name', '')

        # scope org.cilogon.userinfo
        user.oidc_claim_idp = claims.get('idp', '')
        user.oidc_claim_idp_name = claims.get('idp_name', '')
        user.oidc_claim_eppn = claims.get('eppn', '')
        user.oidc_claim_eptid = claims.get('eptid', '')
        user.oidc_claim_affiliation = claims.get('affiliation', '')
        user.oidc_claim_ou = claims.get('ou', '')
        user.oidc_claim_oidc = claims.get('oidc', '')
        user.oidc_claim_cert_subject_dn = claims.get('cert_subject_dn', '')

        # other values
        user.oidc_claim_acr = claims.get('acr', '')
        user.oidc_claim_entitlement = claims.get('entitlement', '')

        # set default user fields
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.email = claims.get('email', '')

        user.save()

        return user
