def update_scheduled_time(experiment, scheduled_date, user_set_by):

    experiment.scheduled_date = scheduled_date
    #experiment.scheduled_by = user_set_by

    # Switch the state to scheduled


    experiment.save()