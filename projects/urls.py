from django.urls import path
from django.conf.urls import include
from experiments import views

from .views import(
    projects,
    project_create,
    project_detail,
    project_update,
    project_delete,
    project_update_members,
    project_update_owners,
    project_join
)

urlpatterns = [
    path('', projects, name='projects'),
    path('create', project_create, name='project_create'),
    path('<uuid:project_uuid>', project_detail, name='project_detail'),
    path('<uuid:project_uuid>/join', project_join, name='project_join'),
    path('<uuid:project_uuid>/update', project_update, name='project_update'),
    path('<uuid:project_uuid>/update_members', project_update_members, name='project_update_members'),
    path('<uuid:project_uuid>/update_owners', project_update_owners, name='project_update_owners'),
    path('<uuid:project_uuid>/delete', project_delete, name='project_delete'),
    path('', include(('experiments.urls', 'experiments'), namespace='experiments')),
]
