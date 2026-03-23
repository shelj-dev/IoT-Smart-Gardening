from django.urls import path
from my_app import views 

urlpatterns=[
    path('update_schedule/',views.update_schedule, name='update_schedule'),
    path('manual_update/',views.manual_update, name='manual_update'),
    path('gardensensor/',views.receive_sensor_data, name='garden-sensor'),
    path('pump/',views.send_garden_data, name='pump'),
]