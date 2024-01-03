from django.conf.urls import include
from django.urls import path

from reservations import views

from .views import (resource_create, resource_delete, resource_detail,
                    resource_update, resources)

urlpatterns = [
    path("", resources, name="resources"),
    path("create", resource_create, name="resource_create"),
    path("<uuid:resource_uuid>", resource_detail, name="resource_detail"),
    path("<uuid:resource_uuid>/update", resource_update, name="resource_update"),
    path("<uuid:resource_uuid>/delete", resource_delete, name="resource_delete"),
]
