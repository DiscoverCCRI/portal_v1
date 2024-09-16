from django.shortcuts import render, redirect
from .forms import ScheduleForm
from experiments.experiments import get_experiment_list
from django.shortcuts import get_object_or_404
from uuid import UUID
from experiments.models import Experiment
from .schedule import update_scheduled_time, change_experiment_state

def schedule(request):
    experiments = get_experiment_list(request)
    form = ScheduleForm()  # Initialize form
    return render(
        request,
        "schedule.html", 
        {"experiments": experiments, "form": form})  # Pass form to template

def site_filter(request):
    if request.method == "POST":
        form = ScheduleForm(request.POST) 
        location = request.POST.get('location')
        site_experiments = Experiment.objects.filter(resources__location=location)
    else:
        form = ScheduleForm()  # If not POST, create a blank form
    return render(request,"schedule.html", {"experiments": site_experiments, "form": form})

def search_experiments(request):
    if request.method == "POST":
        form = ScheduleForm(request.POST) 
        name = request.POST.get('experiment_name')
        experiments = Experiment.objects.filter(name=name)
    else:
        form = ScheduleForm()  # If not POST, create a blank form
    return render(request,"schedule.html", {"experiments": experiments, "form": form})

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
        form = ScheduleForm(request.POST)  # Bind form with POST data
        if form.is_valid():
            scheduled_date = form.data['scheduled_time']
            experiment_uuid = form.data['experiment_uuid']
            experiment = get_object_or_404(Experiment, 
                                                uuid=UUID(str(experiment_uuid)))
            update_scheduled_time(experiment,scheduled_date)
            # Redirect to prevent re-submission
            return redirect('schedule')
    else:
        form = ScheduleForm()  # If not POST, create a blank form

    return render(request, "schedule.html", {"form": form})  # Pass form to template