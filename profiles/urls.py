from django.conf.urls import include
from django.urls import path

from .views import (profile_create, profile_delete, profile_detail,
                    profile_update, profiles)

urlpatterns = [
    path("", profiles, name="profiles"),
    path("create", profile_create, name="profile_create"),
    path("<uuid:profile_uuid>", profile_detail, name="profile_detail"),
    path("<uuid:profile_uuid>/update", profile_update, name="profile_update"),
    path("<uuid:profile_uuid>/delete", profile_delete, name="profile_delete"),
]
