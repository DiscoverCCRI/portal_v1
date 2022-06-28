from django.urls import path
from django.conf.urls import include

from .views import(
    profiles,
    profile_create,
    profile_detail,
    profile_update,
    profile_delete
)

urlpatterns = [
    path('', profiles, name='profiles'),
    path('create', profile_create, name='profile_create'),
    path('<uuid:profile_uuid>', profile_detail, name='profile_detail'),
    path('<uuid:profile_uuid>/update', profile_update, name='profile_update'),
    path('<uuid:profile_uuid>/delete', profile_delete, name='profile_delete'),
]