from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DonationStatusStreamView, DonationViewSet, MpesaWebhookView, PayPalWebhookView, StripeWebhookView

router = DefaultRouter()
router.include_format_suffixes = False
router.register(r"donations", DonationViewSet, basename="donations")

payment_section = DonationViewSet.as_view({"get": "payment_section"})
payment_stats = DonationViewSet.as_view({"get": "payment_stats"})

urlpatterns = [
    path("payment-section/", payment_section, name="payment-section"),
    path("payment-stats/", payment_stats, name="payment-stats"),
    path("donations/<int:pk>/status-stream/", DonationStatusStreamView.as_view(), name="donation-status-stream"),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("webhooks/paypal/", PayPalWebhookView.as_view(), name="paypal-webhook"),
    path("webhooks/mpesa/", MpesaWebhookView.as_view(), name="mpesa-webhook"),
]

urlpatterns += router.urls
