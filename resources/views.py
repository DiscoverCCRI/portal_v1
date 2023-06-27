# Create your views here.

# Create your views here.

import json
from uuid import UUID

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms.models import model_to_dict
from django.shortcuts import render, redirect, get_object_or_404
from urllib3.exceptions import MaxRetryError

from .forms import ResourceCreateForm, ResourceChangeForm
from .resources import *

capabilityMap = {
        'gimbal': 'Gimbal and RGB/IR Camera',
        'lidar': 'LIDAR',
        'jetson': 'Jetson Nano',
        'sdr': 'Software Defined Radio',
        '5g': '5G module(s)',
        'camera': 'Camera',
        'gps': 'GPS',
        't12': 'TEROS-12',
        't21': 'TEROS-21',
        'tts': 'Thermistor Temperature Sensor',
        'tsl259': 'TSL25911FN',
        'bme': 'BME280',
        'icm': 'ICM20948',
        'ltr': 'LTR390-UV-1',
        'sgp': 'SGP40',
        'cws': 'Compact Weather Sensor'
    }


def get_resources_json(resources):
    refactored_rescources_dict = {}

    for res in resources:
        res_dict = model_to_dict(res)
        res_dict["created_date"] = str(res_dict["created_date"])
        refactored_rescources_dict[str(res.uuid)] = res_dict

    return json.dumps(refactored_rescources_dict)


def get_reservations_json(reservations):
    # OUTPUT:
    # json format
    # uuid (string) as keys
    # available units in array as values
    result = {}

    for res in reservations.values():
        for key, units in res.items():
            if str(key) not in result.keys():
                result[str(key)] = []
            available_units = units[1]
            result[str(key)].append(available_units)

    return json.dumps(result)


@login_required()
@user_passes_test(lambda u: u.is_aerpaw_user())
def resources(request):
    """

    :param request:
    :return:
    """
    try:
        import_cloud_resources(request)
    except MaxRetryError as err:
        messages.info(request, 'ERROR: ' + str(err))

    resources = get_resource_list(request)
    resources_json = get_resources_json(resources)
    reserved_resource = get_all_reserved_units(24, 2)
    reservations_json = get_reservations_json(reserved_resource)
    resource_map = {
        "NAU Core" : os.getenv('DISCOVER_NAU_CORE_MAP'),
        "Hat Ranch" : os.getenv('DISCOVER_HAT_RANCH_MAP'),
        "Navajo Tech" : os.getenv('DISCOVER_NAVAJO_TECH_MAP'),
        "Clemson" : os.getenv('DISCOVER_CLEMSON_MAP'),
        "Others" : os.getenv('DISCOVER_OTHERS_MAP'),
    }

    # resource type list
    resource_list = []
    for res in resources.values():
        type = res.get('resourceType')
        if type not in resource_list:
            resource_list.append(type)

    return render(request, 'resources.html',
                  {
                      'resources': resources,
                      'resources_json': resources_json,
                      'reservations': reserved_resource,
                      'reservations_json': reservations_json,
                      'resource_list': resource_list,
                      'resource_map': resource_map,
                  })


@login_required()
@user_passes_test(lambda u: u.is_site_admin() or u.is_resource_manager())
def resource_create(request):
    """

    :param request:
    :return:
    """
    if request.method == "POST":
        form = ResourceCreateForm(request.POST)
        if form.is_valid():
            resource_uuid = create_new_resource(request, form)
            return redirect('resource_detail', resource_uuid=resource_uuid)
    else:
        form = ResourceCreateForm()

    return render(request, 'resource_create.html', {'form': form})


@login_required()
def resource_detail(request, resource_uuid):
    """

    :param request:
    :param resource_uuid:
    :return:
    """
    resource = get_object_or_404(Resource, uuid=UUID(str(resource_uuid)))
    resource_reservations = resource.reservation_of_resource
    resource_map = os.getenv('AERPAW_MAP_URL')
    return render(request, 'resource_detail.html',
                  {'resource': resource, 'reservations': resource_reservations.all(), 'resource_map': resource_map, 'capabilityMap': capabilityMap })


@login_required()
@user_passes_test(lambda u: u.is_superuser or u.is_resource_manager())
def resource_update(request, resource_uuid):
    """

    :param request:
    :param resource_uuid:
    :return:
    """
    resource = get_object_or_404(Resource, uuid=UUID(str(resource_uuid)))
    if request.method == "POST":
        form = ResourceChangeForm(request.POST, instance=resource)
        if form.is_valid():
            resource = form.save(commit=False)
            resource_uuid = update_existing_resource(request, resource, form)
            return redirect('resource_detail', resource_uuid=str(resource.uuid))
    else:
        form = ResourceChangeForm(instance=resource)
    return render(request, 'resource_update.html',
                  {
                      'form': form, 'resource_uuid': str(resource_uuid), 'resource_name': resource.name}
                  )


@login_required()
@user_passes_test(lambda u: u.is_superuser or u.is_resource_manager())
def resource_delete(request, resource_uuid):
    """

    :param request:
    :param resource_uuid:
    :return:
    """
    resource = get_object_or_404(Resource, uuid=UUID(str(resource_uuid)))
    if request.method == "POST":
        is_removed = delete_existing_resource(request, resource)
        if is_removed:
            return redirect('resources')
    return render(request, 'resource_delete.html', {'resource': resource, 'capabilityMap': capabilityMap})
