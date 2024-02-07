# accounts/urls.py
from django.urls import path

from .views import user_groups, user_requests

urlpatterns = [
    path("user_groups", user_groups, name="user_groups"),
    path("user_requests", user_requests, name="user_requests"),
]
