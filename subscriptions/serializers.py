from rest_framework import serializers
from .models import Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
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
            'cancellation_date',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value

    def validate(self, data):
        if data.get('status') == 'CANCELED' and not data.get('cancellation_date'):
            raise serializers.ValidationError(
                "Cancellation date is required when status is canceled"
            )
        return data 