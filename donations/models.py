from django.db import models
from django.conf import settings

class Donation(models.Model):
    PAYMENT_METHODS = (
        ('mpesa', 'MPESA'),
        ('paypal', 'PayPal'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
    )
    STATUSES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    donor_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='KES')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='mpesa')
    anonymous = models.BooleanField(default=False)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor_name} - {self.amount} {self.currency}"

# Create your models here.
