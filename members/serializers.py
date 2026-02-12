from rest_framework import serializers
from .models import MemberProfile

class MemberProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = MemberProfile
        fields = ['id', 'full_name', 'email', 'bio', 'location', 'skills', 'photo']
