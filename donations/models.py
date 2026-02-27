from django.db import models
from django.conf import settings
from django.utils import timezone

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
    provider = models.CharField(max_length=20, blank=True)
    external_reference = models.CharField(max_length=120, blank=True)
    gateway_event_id = models.CharField(max_length=120, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor_name} - {self.amount} {self.currency}"

    def mark_completed(self):
        self.status = "completed"
        if not self.completed_at:
            self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at"])

    def mark_failed(self, reason=""):
        self.status = "failed"
        self.failed_reason = reason[:1000]
        self.save(update_fields=["status", "failed_reason"])

# Create your models here.
