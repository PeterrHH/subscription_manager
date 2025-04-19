from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, URLValidator
from django.utils import timezone
from decimal import Decimal
SUBSCRIPTION_TYPES = [
    ('PAID', 'Paid'),
    ('FREE_TRIAL', 'Free Trial'),
]

class Subscription(models.Model):
    # SUBSCRIPTION_TYPES = [
    #     ('PAID', 'Paid'),
    #     ('FREE_TRIAL', 'Free Trial'),
    # ]
    
    BILLING_CYCLES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    ]
    
    CATEGORIES = [
        ('STREAMING', 'Streaming'),
        ('MUSIC', 'Music'),
        ('SOFTWARE', 'Software'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CANCELLED', 'Cancelled'),
        ('DELETED', 'Deleted'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    service_name = models.CharField(max_length=100)
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPES, default='PAID')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLES)
    start_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    category = models.CharField(max_length=20, choices=CATEGORIES)
    management_link = models.URLField(max_length=200, blank=True, null=True)
    cancellation_date = models.DateField(null=True, blank=True)
    
    # Reminder Settings
    send_reminder = models.BooleanField(default=False)
    reminder_days_ahead = models.IntegerField(default=1, null = True)  # Store number of days ahead
    reminder_hour = models.IntegerField(default=9, null = True)        # Store hour (1-12)
    reminder_minute = models.IntegerField(default=0, null = True)      # Store minute (0-59)
    reminder_ampm = models.CharField(                     # Store AM/PM
        max_length=2,
        choices=[('AM', 'AM'), ('PM', 'PM')],
        default='AM',
        null = True
    )
    
    # Free Trial specific fields
    free_trial_length = models.IntegerField(null=True, blank=True)
    free_trial_unit = models.CharField(
        max_length=10,
        choices=[('DAYS', 'Days'), ('MONTHS', 'Months')],
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service_name} - {self.user.username}"

    class Meta:
        ordering = ['-created_at']

    def get_next_charge_date(self):
        """Calculate the next charge date based on start date and billing cycle"""
        if not self.start_date:
            return None
            
        today = timezone.now().date()
        start = self.start_date
        
        if self.billing_cycle == 'WEEKLY':
            # Calculate days since start, then find next weekly date
            days_since_start = (today - start).days
            days_until_next = 7 - (days_since_start % 7)
            if days_until_next == 7:
                days_until_next = 0
            return today + timezone.timedelta(days=days_until_next)
            
        elif self.billing_cycle == 'MONTHLY':
            # Find the next occurrence of the same day of month
            next_month = today.replace(day=1)
            if today.day >= start.day:
                # Move to next month if we're past the day already
                next_month = (next_month.replace(day=28) + timezone.timedelta(days=4)).replace(day=1)
            
            # Handle month length differences
            try:
                next_date = next_month.replace(day=start.day)
            except ValueError:
                # If the month doesn't have this day (e.g., 31st), use last day
                last_day = 31 if next_month.month in [1, 3, 5, 7, 8, 10, 12] else 30
                if next_month.month == 2:
                    last_day = 29 if next_month.year % 4 == 0 else 28
                next_date = next_month.replace(day=last_day)
            
            return next_date
            
        elif self.billing_cycle == 'YEARLY':
            # Find the next yearly anniversary
            next_year = today.year
            if (today.month > start.month) or (today.month == start.month and today.day > start.day):
                next_year += 1
                
            try:
                return start.replace(year=next_year)
            except ValueError:
                # Handle Feb 29 in non-leap years
                if start.month == 2 and start.day == 29:
                    return start.replace(year=next_year, month=3, day=1)
                raise
        
        return None

    def create_event(self, event_type):
        """Create a new event for this subscription"""
        print(f"------ Creating event for {self.service_name} Event Type {event_type} ------- ")
        current_time = timezone.now();
        return SubscriptionEvent.objects.create(
            subscription=self,
            event_type=event_type,
            event_date=current_time,
            reminder_sent = self.send_reminder,
            reminder_date=current_time + timezone.timedelta(days=self.reminder_days_ahead),
        )

    def update_reminder_event(self):
        """Update or create reminder event based on send_reminder flag"""
        # Delete existing reminder event if send_reminder is False
        if not self.send_reminder:
            SubscriptionEvent.objects.filter(subscription=self).delete()
            return
            
        # If send_reminder is True, create or update the event
        event, created = SubscriptionEvent.objects.get_or_create(
            subscription=self,
            defaults={'reminder_date': None}  # Will be set below
        )
        
        # Calculate and set the reminder date
        reminder_date = event.calculate_reminder_date()
        if reminder_date:
            event.reminder_date = reminder_date
            event.reminder_sent = False
            event.save()
        else:
            event.delete()  # Delete if we can't calculate a valid reminder date

    def save(self, *args, **kwargs):
        # Get the old instance if this is an update
        old_instance = None
        if self.pk:
            old_instance = Subscription.objects.get(pk=self.pk)
            
        super().save(*args, **kwargs)
        
        # Check if send_reminder was changed
        if old_instance and old_instance.send_reminder != self.send_reminder:
            self.update_reminder_event()
        elif not old_instance and self.send_reminder:  # New subscription with reminders enabled
            self.update_reminder_event()

    def cancel(self):
        """Cancel the subscription and remove any reminder events"""
        self.is_active = False
        self.save()
        # Remove any reminder events
        SubscriptionEvent.objects.filter(subscription=self).delete()

class SubscriptionEvent(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='events')
    event_date = models.DateTimeField(auto_now_add=True)
    reminder_sent = models.BooleanField(default=False)
    reminder_date = models.DateTimeField(null=True, blank=True)
    event_type = models.CharField(choices=SUBSCRIPTION_TYPES,max_length=20,default='PAID')
    
    class Meta:
        ordering = ['-event_date']
    
    def __str__(self):
        return f"{self.subscription.service_name} - Reminder scheduled for {self.reminder_date}"

    def calculate_reminder_date(self):
        """Calculate the reminder date based on subscription settings"""
        next_charge = self.subscription.get_next_charge_date()
        if not next_charge:
            return None
            
        # Calculate the reminder date (next_charge_date - reminder_days_ahead)
        reminder_date = next_charge - timezone.timedelta(days=self.subscription.reminder_days_ahead)
        
        # Set the specific hour and minute
        hour = self.subscription.reminder_hour
        if self.subscription.reminder_ampm == 'PM' and hour != 12:
            hour += 12
        elif self.subscription.reminder_ampm == 'AM' and hour == 12:
            hour = 0
            
        return reminder_date.replace(
            hour=hour,
            minute=self.subscription.reminder_minute,
            second=0,
            microsecond=0
        )