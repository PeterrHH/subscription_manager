from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, URLValidator
from django.utils import timezone

class Subscription(models.Model):
    BILLING_CYCLE_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('CANCELED', 'Canceled'),
    ]
    
    CATEGORY_CHOICES = [
        ('STREAMING', 'Streaming'),
        ('MUSIC', 'Music'),
        ('SOFTWARE', 'Software'),
        ('OTHER', 'Other'),
    ]
    
    SUBSCRIPTION_TYPE_CHOICES = [
        ('FREE', 'Free'),
        ('PAID', 'Paid'),
    ]
    
    REMINDER_TIME_CHOICES = [
        ('SAME_DAY', 'On the morning of due date'),
        ('ONE_DAY', '1 day ahead'),
        ('TWO_DAYS', '2 days ahead'),
        ('THREE_DAYS', '3 days ahead'),
        ('ONE_WEEK', '1 week ahead'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    service_name = models.CharField(max_length=100)
    subscription_type = models.CharField(
        max_length=10,
        choices=SUBSCRIPTION_TYPE_CHOICES,
        default='PAID'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    billing_cycle = models.CharField(
        max_length=10,
        choices=BILLING_CYCLE_CHOICES,
        default='MONTHLY'
    )
    start_date = models.DateField(default=timezone.now)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE'
    )
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default='OTHER'
    )
    management_link = models.URLField(
        max_length=500,
        validators=[URLValidator()],
        null=True,
        blank=True
    )
    send_reminder = models.BooleanField(default=False)
    reminder_time = models.CharField(
        max_length=10,
        choices=REMINDER_TIME_CHOICES,
        default='SAME_DAY',
        null=True,
        blank=True
    )
    cancellation_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date', 'service_name']

    def __str__(self):
        return f"{self.service_name} - {self.user.username}"
        
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