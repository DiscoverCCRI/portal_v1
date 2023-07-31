# accounts/urls.py
from django.urls import path

from . import views
from .views import request_roles

urlpatterns = [
    path("profile", views.profile, name="profile"),
    path("signup", views.signup, name="signup"),
    path("request_roles", request_roles, name="request_roles"),
]
