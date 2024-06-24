from django.shortcuts import render, redirect
from .forms import DateTimeForm
from experiments.experiments import get_experiment_list
from django.shortcuts import get_object_or_404
from uuid import UUID
from experiments.models import Experiment
from .schedule import update_scheduled_time

def schedule(request):
    experiments = get_experiment_list(request)
    form = DateTimeForm()  # Initialize form
    return render(
        request,
        "schedule.html", 
        {"experiments": experiments, "form": form})  # Pass form to template

def schedule_experiment(request):
    if request.method == "POST":
        form = DateTimeForm(request.POST)  # Bind form with POST data
        if form.is_valid():
            scheduled_date = form.data['scheduled_time']
            experiment_uuid = form.data['experiment_uuid']
            experiment = get_object_or_404(Experiment, 
                                                uuid=UUID(str(experiment_uuid)))
            update_scheduled_time(experiment,scheduled_date,request.user)
            # Redirect to prevent re-submission
            return redirect('schedule')
    else:
        form = DateTimeForm()  # If not POST, create a blank form

    return render(request, "schedule.html", {"form": form})  # Pass form to template