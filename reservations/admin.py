import functools

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import ReservationChangeForm, ReservationCreateForm
from .models import Reservation

# Register your models here.


# Register your models here.




class AerpawReservationAdmin(admin.ModelAdmin):
    add_form = ReservationCreateForm
    form = ReservationChangeForm
    model = Reservation
    list_display = [
        "name",
        "description",
        "state",
        "start_date",
        "end_date",
        "experiment",
        "resource",
    ]


""" 
    def get_form(self, request, obj=None, **kwargs):
        try:
            kwargs['form'] = ReservationCreateForm
            Form = super().get_form(request, obj=None, **kwargs)
            return functools.partial(Form,experiment_id = request.session['experiment_id'])
        except KeyError as e:
            print(e) """


admin.site.register(Reservation, AerpawReservationAdmin)
