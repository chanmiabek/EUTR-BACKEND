from rest_framework import serializers

from .models import Opportunity, Signup


class OpportunitySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "title",
            "description",
            "location",
            "image",
            "image_url",
            "start_date",
            "end_date",
            "is_active",
        ]

    def get_image_url(self, obj):
        if not obj.image:
            return ""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signup
        fields = ["id", "opportunity", "message", "created_at"]
        read_only_fields = ["created_at"]
