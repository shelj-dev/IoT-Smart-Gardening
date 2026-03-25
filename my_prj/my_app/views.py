from django.shortcuts import render, redirect, get_object_or_404
from my_app.models import Gardening, sensor_data, manual, LastWater
from my_app.forms import GardeningForm, ManualForm
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def update_schedule(request):
    data = get_object_or_404(Gardening, id=1)

    if request.method == "POST":
        form = GardeningForm(request.POST, instance=data)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = GardeningForm(instance=data)

    return render(request, "update.html", {'form': form})


def manual_update(request):
    data = manual.objects.first()

    if request.method == "POST":
        form = ManualForm(request.POST, instance=data)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
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


def index_page(request):
    auth_logout(request)
    return render(request, 'index.html')

def login_page(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            auth_login(request, user)
            return redirect('welcome')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'login.html')

@login_required(login_url='login')
def welcome_page(request):
    return render(request, 'welcome.html')

@login_required(login_url='login')
def help_page(request):
    return render(request, 'help.html')

def logout_view(request):
    auth_logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')


@login_required(login_url='login')
def dashboard_api_status(request):
    try:
        latest_sensor = sensor_data.objects.last()
        moisture = latest_sensor.sensor_value if latest_sensor else "N/A"
        
        pump = manual.objects.first()
        pump_on = pump.pump_on if pump else False
        threshold = pump.threshold if pump else 500
        
        last_water_obj = LastWater.objects.order_by("-time").first()
        last_water_time = last_water_obj.time.strftime('%Y-%m-%d %H:%M:%S') if last_water_obj else "Never"
        
        garden = Gardening.objects.first()
        delay_active = False
        
        # Calculate if delay condition is active
        if last_water_obj and garden:
            now_dt = timezone.now() if timezone.is_aware(last_water_obj.time) else datetime.now()
            delay_duration = timedelta(hours=garden.delay)
            if now_dt < last_water_obj.time + delay_duration:
                delay_active = True

        return JsonResponse({
            'moisture': moisture,
            'pump_on': pump_on,
            'threshold': threshold,
            'last_watered': last_water_time,
            'delay_active': delay_active,
            'status': 'online'
        })
    except Exception as e:
        return JsonResponse({'status': 'offline', 'error': str(e)})


@csrf_exempt
@login_required(login_url='login')
def toggle_pump(request):
    if request.method == 'POST':
        pump = manual.objects.first()
        if pump:
            pump.pump_on = not pump.pump_on
            pump.save()
            return JsonResponse({'status': 'success', 'pump_on': pump.pump_on})
        return JsonResponse({'status': 'error', 'message': 'Pump record not found.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})