from rest_framework import serializers

from .models import EventOverviewVideo


class EventOverviewVideoSerializer(serializers.ModelSerializer):
    image_file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EventOverviewVideo
        fields = [
            "id",
            "title",
            "youtube_url",
            "image",
            "image_url",
            "image_file_url",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_image_file_url(self, obj):
        if not obj.image:
            return ""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url
