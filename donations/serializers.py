from rest_framework import serializers
from .models import Donation

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = [
            'id', 'donor_name', 'email', 'phone', 'amount', 'currency',
            'payment_method', 'anonymous', 'message', 'status', 'created_at'
        ]
        read_only_fields = ['status', 'created_at']
