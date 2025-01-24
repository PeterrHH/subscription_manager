from django import forms
from .models import Subscription
from django.forms.widgets import SelectDateWidget

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['service_name', 'price', 'billing_cycle', 
                  'description', 'status', 'category', 'start_date', 'management_link']
        widgets = {
            'charge_date': SelectDateWidget(
                empty_label=("Year", "Month", "Day"),
            ),
            'start_date': SelectDateWidget(
                empty_label=("Year", "Month", "Day"),
            ),
        }
