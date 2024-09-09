from django.conf.urls import include
from django.urls import path
from .views import schedule, site_filter, schedule_experiment, move_to_error, move_to_complete, move_to_not_scheduled

#from experiments import views

#from .views import ()

urlpatterns = [
    path("", schedule, name="schedule"),
    path("siteFilter", site_filter, name="site_filter"),
    path("schedule", schedule_experiment, name="schedule_experiment"),
    path("moveToError", move_to_error, name="move_to_error"),
    path("moveToComplete", move_to_complete, name="move_to_complete"),
    path("moveToNotScheduled", move_to_not_scheduled, name="move_to_not_scheduled"),
]
