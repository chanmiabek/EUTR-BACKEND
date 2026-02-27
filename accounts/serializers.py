from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from members.models import MemberProfile

from .models import User


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
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'is_staff', 'is_team_member', 'role', 'bio', 'location', 'skills']

    def get_role(self, obj):
        if obj.is_staff:
            return 'admin'
        if obj.is_team_member:
            return 'team_member'
        return 'member'


class TeamMemberCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'password', 'is_active']
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['is_team_member'] = True
        user = User.objects.create_user(password=password, **validated_data)
        MemberProfile.objects.get_or_create(user=user)
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['is_team_member'] = user.is_team_member
        token['role'] = 'admin' if user.is_staff else ('team_member' if user.is_team_member else 'member')
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'full_name': self.user.full_name,
            'is_staff': self.user.is_staff,
            'is_team_member': self.user.is_team_member,
            'role': 'admin' if self.user.is_staff else ('team_member' if self.user.is_team_member else 'member'),
        }
        return data
