from django.contrib import admin
from .models import Subscription, SubscriptionEvent

admin.site.register(Subscription)
admin.site.register(SubscriptionEvent)