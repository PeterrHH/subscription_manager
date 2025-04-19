from abc import ABC, abstractmethod
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class NotificationService(ABC):
    @abstractmethod
    def send_notification(self, user, subscription_name, days_ahead):
        pass

class EmailNotificationService(NotificationService):
    def send_notification(self, user, subscription_name, days_ahead):
        subject = f'Subscription Reminder: {subscription_name}'
        
        # You can create HTML templates for emails in the future
        message = f'Your subscription "{subscription_name}" is up in {days_ahead} days.'
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Failed to send email notification: {str(e)}")
            return False

# Factory to get the appropriate notification service
class NotificationServiceFactory:
    @staticmethod
    def get_service(service_type='email'):
        if service_type == 'email':
            return EmailNotificationService()
        # Add more notification services here in the future
        # elif service_type == 'sms':
        #     return SMSNotificationService()
        # elif service_type == 'push':
        #     return PushNotificationService()
        raise ValueError(f"Unknown notification service type: {service_type}") 