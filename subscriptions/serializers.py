from rest_framework import serializers
from .models import Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
    next_charge_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = [
            'id',
            'service_name',
            'subscription_type',
            'price',
            'billing_cycle',
            'next_charge_date',
            'start_date',
            'status',
            'category',
            'management_link',
            'send_reminder',
            'reminder_days_ahead',
            'reminder_hour',
            'reminder_minute',
            'reminder_ampm',
            'free_trial_length',
            'free_trial_unit',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'next_charge_date']

    def get_next_charge_date(self, obj):
        """Get the calculated next charge date"""
        next_date = obj.get_next_charge_date()
        if next_date:
            return next_date.isoformat()
        return None

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value

    def validate(self, data):
        # if data.get('status') == 'CANCELED' and not data.get('cancellation_date'):
        #     data['cancellation_date'] = serializers.DateField().to_internal_value(
        #         serializers.DateField().to_representation(
        #             serializers.DateField().get_default()
        #         )
        #     )
        
        # If send_reminder is False, set reminder_time to None
        if 'send_reminder' in data and not data.get('send_reminder'):
            data['reminder_days_ahead'] = None
            data['reminder_hour'] = None
            data['reminder_minute'] = None
            data['reminder_ampm'] = None
            
        return data 