from rest_framework import serializers

from .models import MemberProfile


class MemberProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    photo_url = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = MemberProfile
        fields = ["id", "user_id", "full_name", "email", "bio", "location", "skills", "photo", "photo_url"]

    def get_photo_url(self, obj):
        if not obj.photo:
            return ""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.photo.url)
        return obj.photo.url
