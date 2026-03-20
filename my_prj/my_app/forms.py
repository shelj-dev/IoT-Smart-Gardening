from django import forms
from my_app.models import Gardening, manual

class GardeningForm(forms.ModelForm):
    class Meta:
        model = Gardening
        fields = ['status','delay']

class ManualForm(forms.ModelForm):
    class Meta:
        model = manual
        fields = [
            "pump_on",
            "off_delay",
            "threshold",
        ]
