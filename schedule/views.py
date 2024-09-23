from django.shortcuts import render, redirect
from .forms import ScheduleForm, LocationFilterForm, ExperimentSearchForm
from experiments.experiments import get_experiment_list
from django.shortcuts import get_object_or_404
from uuid import UUID
from experiments.models import Experiment
from .schedule import update_scheduled_time, change_experiment_state


def schedule(request):
    experiments = get_experiment_list(request)
    schedule_form = ScheduleForm()
    location_form = LocationFilterForm()
    search_form = ExperimentSearchForm()
    
    return render(request, "schedule.html", {
        "experiments": experiments,
        "schedule_form": schedule_form,
        "location_form": location_form,
        "search_form": search_form
    })

def schedule_experiment(request):
    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            scheduled_date = form.cleaned_data['scheduled_time']
            experiment_uuid = form.cleaned_data['experiment_uuid']
            experiment = get_object_or_404(Experiment, uuid=UUID(str(experiment_uuid)))
            update_scheduled_time(experiment, scheduled_date)
            change_experiment_state(experiment, 1)
            return redirect('schedule')
    return redirect('schedule')

def site_filter(request):
    experiments = Experiment.objects.all()
    location_form = LocationFilterForm(request.POST or None)
    search_form = ExperimentSearchForm()
    
    if location_form.is_valid():
        location = location_form.cleaned_data['location']
        experiments = experiments.filter(resources__location=location)

    return render(request, "schedule.html", {
        "experiments": experiments,
        "schedule_form": ScheduleForm(),
        "location_form": location_form,
        "search_form": search_form
    })

def search_experiments(request):
    experiments = Experiment.objects.all()
    location_form = LocationFilterForm()
    search_form = ExperimentSearchForm(request.POST or None)
    
    if search_form.is_valid():
        name = search_form.cleaned_data['experiment_name']
        experiments = experiments.filter(name__icontains=name)

    return render(request, "schedule.html", {
        "experiments": experiments,
        "schedule_form": ScheduleForm(),
        "location_form": location_form,
        "search_form": search_form
    })


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
