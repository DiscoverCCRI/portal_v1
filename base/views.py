import os

from django.shortcuts import render


def home(request):
    """

    :param request:
    :return:
    """
    if request.user.is_authenticated:
        operator_cicd = {
            "url": os.getenv("OPERATOR_CICD_URL"),
            "port": os.getenv("OPERATOR_CICD_PORT"),
        }
        return render(request, "home.html", {"operator_cicd": operator_cicd})
    else:
        return render(request, "home.html")
