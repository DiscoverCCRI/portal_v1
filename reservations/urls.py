from django.urls import path

from .views import(
    reservations,
    reservation_create,
    reservation_detail,
    reservation_detail_own,
    reservation_update,
    reservation_delete
)

urlpatterns = [
    path('', reservations, name='reservations'),
    path('<uuid:experiment_uuid>/create', reservation_create, name='reservation_create'),
    path('<uuid:reservation_uuid>/<uuid:experiment_uuid>', reservation_detail, name='reservation_detail'),
    path('<uuid:reservation_uuid>', reservation_detail_own, name='reservation_detail_own'),
    path('<uuid:reservation_uuid>/update', reservation_update, name='reservation_update'),
    path('<uuid:reservation_uuid>/delete', reservation_delete, name='reservation_delete'),
]