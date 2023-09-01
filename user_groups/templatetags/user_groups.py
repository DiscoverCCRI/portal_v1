from django import template
from django.template.defaultfilters import stringfilter
from accounts.models import AerpawUser, AerpawUserRoleChoice

register = template.Library()

@register.filter
@stringfilter
def role_name(role):
    choices = AerpawUserRoleChoice.choices()
    return dict(choices).get(role)


@register.filter
def sort_by(queryset, order):
    return queryset.order_by(order)


@register.filter
def displayname_by_id(user_id):
    return AerpawUser.objects.get(id=int(user_id)).display_name
