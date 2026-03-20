from django.db import models


class Gardening(models.Model):
    status = models.BooleanField(default=True)
    delay = models.IntegerField() # 5 hours


class manual(models.Model):
    pump_on = models.BooleanField(default=False)
    off_delay = models.IntegerField()
    threshold = models.IntegerField()


class sensor_data(models.Model):
    sensor_value=models.IntegerField()
    time_stamp=models.DateTimeField( auto_now_add = True)


class LastWater(models.Model):
    time = models.DateTimeField(auto_now_add=True)