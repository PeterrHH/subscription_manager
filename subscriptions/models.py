from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, URLValidator

class Subscription(models.Model):
    BILLING_CYCLE_CHOICES = [
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
    next_charge_date = models.DateField()
    start_date = models.DateField(null=True, blank=True)
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
    cancellation_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['next_charge_date', 'service_name']

    def __str__(self):
        return f"{self.service_name} - {self.user.username}"