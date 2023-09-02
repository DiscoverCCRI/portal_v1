from django.urls import path
from django.conf.urls import include

from .views import(
    usercomms,
    usercomm_detail,
)

urlpatterns = [
    path('', usercomms, name='usercomms'),
    path('<uuid:usercomm_uuid>', usercomm_detail, name='usercomm_detail'),
]
