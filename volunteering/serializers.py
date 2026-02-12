from rest_framework import serializers
from .models import Opportunity, Signup

class OpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = ['id', 'title', 'description', 'location', 'start_date', 'end_date', 'is_active']

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signup
        fields = ['id', 'opportunity', 'message', 'created_at']
        read_only_fields = ['created_at']
