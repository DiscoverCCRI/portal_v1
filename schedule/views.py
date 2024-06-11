from django.shortcuts import render

from experiments.experiments import get_experiment_list

def schedule(request):
    experiments = get_experiment_list(request)
    return render(
        request,
        "schedule.html", 
        {"experiments": experiments})