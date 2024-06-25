def update_scheduled_time(experiment, scheduled_date):
    experiment.scheduled_date = scheduled_date
    if experiment.state_temp == 0:
        experiment.state_temp = 1
    experiment.save()

def change_experiment_state(experiment, state):
    experiment.state_temp = state
    experiment.save()
