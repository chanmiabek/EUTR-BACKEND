from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from members.models import MemberProfile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        MemberProfile.objects.get_or_create(user=user)
        return user

class UserSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(source='profile.bio', required=False, allow_blank=True)
    location = serializers.CharField(source='profile.location', required=False, allow_blank=True)
    skills = serializers.CharField(source='profile.skills', required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'bio', 'location', 'skills']

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token
