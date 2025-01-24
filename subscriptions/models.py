from django.db import models
from django.contrib.auth.models import User

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    billing_cycle = models.CharField(
        max_length=10,
        choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')]
    )
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=[('active', 'Active'), ('paused', 'Paused'), ('canceled', 'Canceled')],
        default='active'
    )
    category = models.CharField(
        max_length=50,
        choices=[('streaming', 'Streaming'), ('music', 'Music'), ('software', 'Software'), ('utility', 'Utility'),('other', 'Other')],
        default='other'
    )
    start_date = models.DateField()
    contract_duration = models.CharField(
        max_length=10,
        choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')],
        default='monthly'
    )
    management_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.service_name} - {self.subscription_type}"