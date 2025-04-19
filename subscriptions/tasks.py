from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Subscription, SubscriptionEvent
from .notifications import NotificationServiceFactory

@shared_task
def check_upcoming_subscriptions():
    # Get all active subscriptions
    active_subscriptions = Subscription.objects.filter(is_active=True)
    
    for subscription in active_subscriptions:
        # Calculate days until renewal
        days_until_renewal = (subscription.next_renewal_date - timezone.now().date()).days
        
        # Check if we need to send a reminder
        if days_until_renewal == subscription.reminder_days_ahead:
            # Get the notification service (email by default)
            notification_service = NotificationServiceFactory.get_service('email')
            
            # Send the notification
            notification_service.send_notification(
                user=subscription.user,
                subscription_name=subscription.name,
                days_ahead=days_until_renewal
            )

@shared_task
def check_pending_reminders():
    """Check for events that need reminders and send them"""
    now = timezone.now()
    pending_events = SubscriptionEvent.objects.filter(
        reminder_sent=False,
        reminder_date__lte=now
    )
    
    for event in pending_events:
        # Only send if subscription is still active and has reminders enabled
        if event.subscription.is_active and event.subscription.send_reminder:
            notification_service = NotificationServiceFactory.get_service('email')
            notification_service.send_notification(
                user=event.subscription.user,
                subscription_name=event.subscription.service_name,
                days_ahead=event.subscription.reminder_days_ahead
            )
            
            # Mark the event as reminder sent
            event.reminder_sent = True
            event.save()
            
            # Create a new event for the next reminder
            event.subscription.update_reminder_event() 