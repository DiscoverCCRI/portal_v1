from django.urls import path
from django.conf.urls import include

from reservations import views

from .views import(
    experiments,
    experiment_create,
    experiment_detail,
    experiment_update,
    experiment_update_by_ops,
    experiment_update_experimenters,
    experiment_delete,
    experiment_initiate,
    experiment_manifest,
    experiment_submit,
    experiment_link_update,
    get_filtered_resource
)

urlpatterns = [
    path('', experiments, name='experiments'),
    path('create', experiment_create, name='experiment_create'),
    path('<uuid:experiment_uuid>', experiment_detail, name='experiment_detail'),
    path('<uuid:experiment_uuid>/update', experiment_update, name='experiment_update'),
    path('<uuid:experiment_uuid>/update_by_ops', experiment_update_by_ops, name='experiment_update_by_ops'),
    path('<uuid:experiment_uuid>/update_experimenters', experiment_update_experimenters, name='experiment_update_experimenters'),
    path('<uuid:experiment_uuid>/delete', experiment_delete, name='experiment_delete'),
    path('<uuid:experiment_uuid>/initiate', experiment_initiate, name='experiment_initiate'),
    path('<uuid:experiment_uuid>/manifest', experiment_manifest, name='experiment_manifest'),
    path('', include(('reservations.urls', 'reservations'), namespace='reservations')),
    path('<uuid:experiment_uuid>/submit', experiment_submit, name='experiment_submit'),
    path('<uuid:experiment_uuid>/update_link', experiment_link_update, name='experiment_link_update'),
    path('filter', get_filtered_resource, name='get_filtered_resource'),
]