from django.conf.urls import include
from django.urls import path

from .views import usercomm_detail, usercomms

urlpatterns = [
    path("", usercomms, name="usercomms"),
    path("<uuid:usercomm_uuid>", usercomm_detail, name="usercomm_detail"),
]
