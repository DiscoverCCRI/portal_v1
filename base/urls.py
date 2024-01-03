"""base URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

from .views import home

urlpatterns = [
    # path('', TemplateView.as_view(template_name='base/home.html'), name='home'),
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("oidc/", include("mozilla_django_oidc.urls")),
    path("projects/", include("projects.urls")),
    path("experiments/", include("experiments.urls")),
    path("reservations/", include("reservations.urls")),
    path("resources/", include("resources.urls")),
    path("profile/", include("profiles.urls")),
    # path('cicd/', include('cicd.urls')), # RM_CICD
    path("manage/", include("user_groups.urls")),
    path("messages/", include("usercomms.urls")),
]
