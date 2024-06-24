from django.conf.urls import include
from django.urls import path
from .views import schedule, schedule_experiment

#from experiments import views

#from .views import ()

urlpatterns = [
    path("", schedule, name="schedule"),
    path("schedule", schedule_experiment, name="schedule_experiment"),
]
