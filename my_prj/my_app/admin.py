from django.contrib import admin
from my_app.models import Gardening, manual, sensor_data, LastWater


admin.site.register(Gardening)
admin.site.register(manual)
admin.site.register(sensor_data)
admin.site.register(LastWater)
