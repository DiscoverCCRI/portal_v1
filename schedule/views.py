from django.shortcuts import render, redirect
from .forms import DateTimeForm
from experiments.experiments import get_experiment_list
from django.shortcuts import get_object_or_404
from uuid import UUID
from experiments.models import Experiment
from .schedule import update_scheduled_time, change_experiment_state

def schedule(request):
    experiments = get_experiment_list(request)
    form = DateTimeForm()  # Initialize form
    return render(
        request,
        "schedule.html", 
        {"experiments": experiments, "form": form})  # Pass form to template

def move_to_error(request):
    if request.method == 'POST':
        experiment_uuid = request.POST.get('experiment_uuid')
        experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))
        change_experiment_state( experiment, 3 )
    
    return redirect('schedule')

def move_to_complete(request):
    if request.method == 'POST':
        experiment_uuid = request.POST.get('experiment_uuid')
        experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))
        change_experiment_state( experiment, 2 )
    
    return redirect('schedule')

def move_to_not_scheduled(request):
    if request.method == 'POST':
        experiment_uuid = request.POST.get('experiment_uuid')
        experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))
        change_experiment_state( experiment, 0 )
    
    return redirect('schedule')

def schedule_experiment(request):
    if request.method == "POST":
        form = DateTimeForm(request.POST)  # Bind form with POST data
        if form.is_valid():
            scheduled_date = form.data['scheduled_time']
            experiment_uuid = form.data['experiment_uuid']
            experiment = get_object_or_404(Experiment, 
                                                uuid=UUID(str(experiment_uuid)))
            update_scheduled_time(experiment,scheduled_date)
            # Redirect to prevent re-submission
            return redirect('schedule')
    else:
        form = DateTimeForm()  # If not POST, create a blank form

    return render(request, "schedule.html", {"form": form})  # Pass form to template