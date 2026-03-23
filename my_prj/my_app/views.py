from django.shortcuts import render, redirect, get_object_or_404
from my_app.models import Gardening, sensor_data, manual, LastWater
from my_app.forms import GardeningForm, ManualForm
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from datetime import datetime


def update_schedule(request):
    data = get_object_or_404(Gardening, id=1)

    if request.method == "POST":
        form = GardeningForm(request.POST, instance=data)
        if form.is_valid():
            form.save()
            return redirect("update_schedule")
    else:
        form = GardeningForm(instance=data)

    return render(request, "update.html", {'form': form})


def manual_update(request):
    data = manual.objects.first()

    if request.method == "POST":
        form = ManualForm(request.POST, instance=data)
        if form.is_valid():
            form.save()
            return redirect("relay_update")
    else:
        form = ManualForm(instance=data)

    return render(request, "relay.html", {'form': form})


# Receive sensor data from ESP / IoT
@csrf_exempt
def receive_sensor_data(request):
    print("qq")
    if request.method == "POST":
        print("q")
        data = json.loads(request.body)
        print(data)

        moisture = data.get("moisture")

        sensor_data.objects.create(sensor_value=moisture)

        return JsonResponse({
            "status": "received",
            "moisture": moisture
        })

    return JsonResponse({"error": "POST required"})


# Send config to IoT device
@require_GET
def send_garden_data(request):
    garden = Gardening.objects.first()
    pump = manual.objects.first()
    last_water = LastWater.objects.order_by("-time").first()

    now = datetime.now()

    # 🛑 Check if delay time is active
    if last_water:
        if last_water.time + garden.delay < now:
            is_delay_hour = True
            last_water.objects.create()
        else:
            is_delay_hour = False
    else:
        is_delay_hour = False   # no previous watering

    data = {
        "status": garden.status,
        "is_delay_hour": is_delay_hour,
        "pump_on": pump.pump_on,
        "off_delay": pump.off_delay,
        "threshold": pump.threshold,
    }

    return JsonResponse(data)