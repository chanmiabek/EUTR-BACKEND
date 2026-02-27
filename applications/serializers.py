from rest_framework import serializers

from .models import (
    Application,
    ContactMessage,
    Event,
    PartnerAppointment,
    Partner,
    Program,
    Project,
    TeamMember,
    Testimonial,
)


class VolunteerApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["id", "name", "email", "phone", "role", "availability", "message", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        validated_data["type"] = Application.TYPE_VOLUNTEER
        return super().create(validated_data)


class JoinApplicationCreateSerializer(serializers.ModelSerializer):
    startDate = serializers.DateField(source="preferred_start_date", required=False, allow_null=True)

    class Meta:
        model = Application
        fields = ["id", "name", "email", "phone", "role", "startDate", "message", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        validated_data["type"] = Application.TYPE_JOIN
        return super().create(validated_data)


class ApplicationAdminSerializer(serializers.ModelSerializer):
    reviewed_by_email = serializers.EmailField(source="reviewed_by.email", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "type",
            "name",
            "email",
            "phone",
            "role",
            "availability",
            "preferred_start_date",
            "message",
            "status",
            "review_note",
            "reviewed_by",
            "reviewed_by_email",
            "reviewed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "reviewed_by_email",
            "created_at",
            "updated_at",
        ]


class ApplicationReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["status", "review_note"]

    def validate_status(self, value):
        allowed = {Application.STATUS_APPROVED, Application.STATUS_REJECTED}
        if value not in allowed:
            raise serializers.ValidationError("Status must be either approved or rejected.")
        return value


class ProgramSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Program
        fields = [
            "id",
            "title",
            "focus",
            "description",
            "status",
            "beneficiaries",
            "highlights",
            "image",
            "photo",
            "image_url",
            "display_order",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_image_url(self, obj):
        if obj.photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return obj.image or ""


class ProjectSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "tag",
            "copy",
            "image",
            "photo",
            "image_url",
            "display_order",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_image_url(self, obj):
        if obj.photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return obj.image or ""


class EventSerializer(serializers.ModelSerializer):
    date = serializers.DateField(required=False, allow_null=True, format="%Y-%m-%d", input_formats=["%Y-%m-%d"])
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "date",
            "location",
            "tag",
            "description",
            "highlights",
            "image",
            "photo",
            "image_url",
            "display_order",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_image_url(self, obj):
        if obj.photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return obj.image or ""


class TeamMemberSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TeamMember
        fields = [
            "id",
            "name",
            "role",
            "copy",
            "image",
            "photo",
            "image_url",
            "display_order",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_image_url(self, obj):
        if obj.photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return obj.image or ""


class PartnerSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Partner
        fields = [
            "id",
            "name",
            "link",
            "logo",
            "logo_url",
            "display_order",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_logo_url(self, obj):
        if not obj.logo:
            return ""
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.logo.url)
        return obj.logo.url


class TestimonialSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Testimonial
        fields = [
            "id",
            "name",
            "role",
            "quote",
            "image",
            "photo",
            "image_url",
            "display_order",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_image_url(self, obj):
        if obj.photo:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return obj.image or ""


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["id", "name", "email", "message", "created_at"]
        read_only_fields = ["id", "created_at"]


class ContactMessageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["id", "name", "email", "message", "is_resolved", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PartnerAppointmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerAppointment
        fields = [
            "id",
            "organization_name",
            "contact_name",
            "email",
            "phone",
            "preferred_date",
            "preferred_time",
            "topic",
            "message",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PartnerAppointmentAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerAppointment
        fields = [
            "id",
            "organization_name",
            "contact_name",
            "email",
            "phone",
            "preferred_date",
            "preferred_time",
            "topic",
            "message",
            "status",
            "admin_response",
            "response_sent_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "response_sent_at", "created_at", "updated_at"]
