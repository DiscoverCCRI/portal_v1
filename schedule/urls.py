from django.conf.urls import include
from django.urls import path
from .views import schedule

#from experiments import views

#from .views import ()

urlpatterns = [
    path("", schedule, name="schedule"),
]
