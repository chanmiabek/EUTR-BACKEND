from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import filters, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import (
    Application,
    ContactMessage,
    Event,
    Partner,
    PartnerAppointment,
    Program,
    Project,
    TeamMember,
    Testimonial,
)
from .pagination import AdminResultsSetPagination
from .serializers import (
    ApplicationAdminSerializer,
    ApplicationReviewSerializer,
    ContactMessageAdminSerializer,
    ContactMessageCreateSerializer,
    EventSerializer,
    JoinApplicationCreateSerializer,
    PartnerAppointmentAdminSerializer,
    PartnerAppointmentCreateSerializer,
    PartnerSerializer,
    ProgramSerializer,
    ProjectSerializer,
    TeamMemberSerializer,
    TestimonialSerializer,
    VolunteerApplicationCreateSerializer,
)


def parse_bool(value):
    if value is None:
        return None
    lowered = str(value).strip().lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    return None


class JWTAdminMixin:
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    pagination_class = AdminResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


class VolunteerApplicationCreateView(generics.CreateAPIView):
    serializer_class = VolunteerApplicationCreateSerializer
    permission_classes = [AllowAny]


class JoinApplicationCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        payload = request.data.copy()
        if payload.get("interest") and not payload.get("role"):
            payload["role"] = payload.get("interest")

        serializer = JoinApplicationCreateSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        out = JoinApplicationCreateSerializer(application)
        return Response(out.data, status=status.HTTP_201_CREATED)


class ApplicationAdminViewSet(JWTAdminMixin, viewsets.ModelViewSet):
    queryset = Application.objects.select_related("reviewed_by").all()
    serializer_class = ApplicationAdminSerializer
    search_fields = ["name", "email", "phone", "role", "message", "review_note"]
    ordering_fields = ["created_at", "updated_at", "reviewed_at", "status", "type", "name", "email"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        app_type = self.request.query_params.get("type")
        app_status = self.request.query_params.get("status")
        reviewed_by = self.request.query_params.get("reviewed_by")
        date_from = self.request.query_params.get("created_from")
        date_to = self.request.query_params.get("created_to")

        if app_type in {Application.TYPE_VOLUNTEER, Application.TYPE_JOIN}:
            queryset = queryset.filter(type=app_type)
        if app_status in {
            Application.STATUS_PENDING,
            Application.STATUS_APPROVED,
            Application.STATUS_REJECTED,
        }:
            queryset = queryset.filter(status=app_status)
        if reviewed_by:
            queryset = queryset.filter(reviewed_by_id=reviewed_by)
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        return queryset


class ApplicationReviewView(generics.UpdateAPIView):
    queryset = Application.objects.select_related("reviewed_by").all()
    serializer_class = ApplicationReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        instance.status = serializer.validated_data["status"]
        instance.review_note = serializer.validated_data.get("review_note", "")
        instance.reviewed_by = request.user
        instance.reviewed_at = timezone.now()
        instance.save(update_fields=["status", "review_note", "reviewed_by", "reviewed_at", "updated_at"])

        output = ApplicationAdminSerializer(instance)
        return Response(output.data)


class ProgramsListView(generics.ListAPIView):
    serializer_class = ProgramSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Program.objects.filter(is_active=True).order_by("display_order", "id")


class ProjectsListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Project.objects.filter(is_active=True).order_by("display_order", "id")


class EventsListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Event.objects.filter(is_active=True).order_by("display_order", "date", "id")


class TeamListView(generics.ListAPIView):
    serializer_class = TeamMemberSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return TeamMember.objects.filter(is_active=True).order_by("display_order", "id")


class PartnersListView(generics.ListAPIView):
    serializer_class = PartnerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Partner.objects.filter(is_active=True).order_by("display_order", "id")


class TestimonialsListView(generics.ListAPIView):
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Testimonial.objects.filter(is_active=True).order_by("display_order", "id")


class ContactCreateView(generics.CreateAPIView):
    serializer_class = ContactMessageCreateSerializer
    permission_classes = [AllowAny]


class PartnerAppointmentCreateView(generics.CreateAPIView):
    serializer_class = PartnerAppointmentCreateSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        appointment = serializer.save(status=PartnerAppointment.STATUS_PENDING)

        team_email = getattr(settings, "PARTNER_BOOKING_NOTIFICATION_EMAIL", "")
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "")

        admin_subject = f"New Partner Appointment Request: {appointment.organization_name}"
        admin_message = (
            f"Organization: {appointment.organization_name}\n"
            f"Contact: {appointment.contact_name}\n"
            f"Email: {appointment.email}\n"
            f"Phone: {appointment.phone or '-'}\n"
            f"Preferred Date: {appointment.preferred_date or '-'}\n"
            f"Preferred Time: {appointment.preferred_time or '-'}\n"
            f"Topic: {appointment.topic or '-'}\n"
            f"Message:\n{appointment.message or '-'}"
        )
        if team_email:
            send_mail(admin_subject, admin_message, from_email, [team_email], fail_silently=True)

        user_subject = "We received your partner appointment request"
        user_message = (
            f"Hello {appointment.contact_name},\n\n"
            "Thank you for booking a partnership appointment with EUTR.\n"
            "Our team has received your request and will respond by email soon.\n\n"
            "Best regards,\nEUTR Partnerships Team"
        )
        send_mail(user_subject, user_message, from_email, [appointment.email], fail_silently=True)


class ProgramAdminViewSet(JWTAdminMixin, viewsets.ModelViewSet):
    queryset = Program.objects.all().order_by("display_order", "id")
    serializer_class = ProgramSerializer
    search_fields = ["title", "focus", "description", "beneficiaries", "status"]
    ordering_fields = ["display_order", "title", "status", "created_at", "updated_at", "is_active"]
    ordering = ["display_order", "id"]

    def get_queryset(self):
        queryset = super().get_queryset()
        focus = self.request.query_params.get("focus")
        status_value = self.request.query_params.get("status")
        is_active = parse_bool(self.request.query_params.get("is_active"))

        if focus:
            queryset = queryset.filter(focus__icontains=focus)
        if status_value:
            queryset = queryset.filter(status__icontains=status_value)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset


class ProjectAdminViewSet(JWTAdminMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by("display_order", "id")
    serializer_class = ProjectSerializer
    search_fields = ["title", "tag", "copy"]
    ordering_fields = ["display_order", "title", "tag", "created_at", "updated_at", "is_active"]
    ordering = ["display_order", "id"]

    def get_queryset(self):
        queryset = super().get_queryset()
        tag = self.request.query_params.get("tag")
        is_active = parse_bool(self.request.query_params.get("is_active"))

        if tag:
            queryset = queryset.filter(tag__icontains=tag)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset


class EventAdminViewSet(JWTAdminMixin, viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by("display_order", "date", "id")
    serializer_class = EventSerializer
    search_fields = ["title", "location", "tag", "description"]
    ordering_fields = ["display_order", "date", "title", "location", "tag", "created_at", "updated_at", "is_active"]
    ordering = ["display_order", "date", "id"]

    def get_queryset(self):
        queryset = super().get_queryset()
        tag = self.request.query_params.get("tag")
        location = self.request.query_params.get("location")
        is_active = parse_bool(self.request.query_params.get("is_active"))
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if tag:
            queryset = queryset.filter(tag__icontains=tag)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        return queryset


class TeamAdminViewSet(JWTAdminMixin, viewsets.ModelViewSet):
    queryset = TeamMember.objects.all().order_by("display_order", "id")
    serializer_class = TeamMemberSerializer
    search_fields = ["name", "role", "copy"]
    ordering_fields = ["display_order", "name", "role", "created_at", "updated_at", "is_active"]
    ordering = ["display_order", "id"]

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get("role")
        is_active = parse_bool(self.request.query_params.get("is_active"))

        if role:
            queryset = queryset.filter(role__icontains=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset


class PartnerAdminViewSet(JWTAdminMixin, viewsets.ModelViewSet):
    queryset = Partner.objects.all().order_by("display_order", "id")
    serializer_class = PartnerSerializer
    search_fields = ["name", "link"]
    ordering_fields = ["display_order", "name", "link", "created_at", "updated_at", "is_active"]
    ordering = ["display_order", "id"]

    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = parse_bool(self.request.query_params.get("is_active"))

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset


class TestimonialAdminViewSet(JWTAdminMixin, viewsets.ModelViewSet):
    queryset = Testimonial.objects.all().order_by("display_order", "id")
    serializer_class = TestimonialSerializer
    search_fields = ["name", "role", "quote"]
    ordering_fields = ["display_order", "name", "role", "created_at", "updated_at", "is_active"]
    ordering = ["display_order", "id"]

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get("role")
        is_active = parse_bool(self.request.query_params.get("is_active"))

        if role:
            queryset = queryset.filter(role__icontains=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset


class ContactMessageAdminViewSet(JWTAdminMixin, viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all().order_by("-created_at")
    serializer_class = ContactMessageAdminSerializer
    search_fields = ["name", "email", "message"]
    ordering_fields = ["created_at", "updated_at", "name", "email", "is_resolved"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        is_resolved = parse_bool(self.request.query_params.get("is_resolved"))
        email = self.request.query_params.get("email")
        created_from = self.request.query_params.get("created_from")
        created_to = self.request.query_params.get("created_to")

        if is_resolved is not None:
            queryset = queryset.filter(is_resolved=is_resolved)
        if email:
            queryset = queryset.filter(email__icontains=email)
        if created_from:
            queryset = queryset.filter(created_at__date__gte=created_from)
        if created_to:
            queryset = queryset.filter(created_at__date__lte=created_to)
        return queryset


class PartnerAppointmentAdminViewSet(JWTAdminMixin, viewsets.ModelViewSet):
    queryset = PartnerAppointment.objects.all().order_by("-created_at")
    serializer_class = PartnerAppointmentAdminSerializer
    search_fields = ["organization_name", "contact_name", "email", "phone", "topic", "message", "admin_response"]
    ordering_fields = ["created_at", "updated_at", "preferred_date", "status", "organization_name", "contact_name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        status_value = self.request.query_params.get("status")
        email = self.request.query_params.get("email")
        created_from = self.request.query_params.get("created_from")
        created_to = self.request.query_params.get("created_to")

        if status_value in {
            PartnerAppointment.STATUS_PENDING,
            PartnerAppointment.STATUS_RESPONDED,
            PartnerAppointment.STATUS_CLOSED,
        }:
            queryset = queryset.filter(status=status_value)
        if email:
            queryset = queryset.filter(email__icontains=email)
        if created_from:
            queryset = queryset.filter(created_at__date__gte=created_from)
        if created_to:
            queryset = queryset.filter(created_at__date__lte=created_to)
        return queryset

    @action(detail=True, methods=["post"])
    def send_response(self, request, pk=None):
        appointment = self.get_object()
        response_text = (request.data.get("response") or "").strip()
        if not response_text:
            return Response({"detail": "Response text is required."}, status=status.HTTP_400_BAD_REQUEST)

        subject = f"Response to your partnership appointment: {appointment.organization_name}"
        send_mail(
            subject,
            response_text,
            getattr(settings, "DEFAULT_FROM_EMAIL", ""),
            [appointment.email],
            fail_silently=True,
        )

        appointment.admin_response = response_text
        appointment.status = PartnerAppointment.STATUS_RESPONDED
        appointment.response_sent_at = timezone.now()
        appointment.save(update_fields=["admin_response", "status", "response_sent_at", "updated_at"])

        return Response(self.get_serializer(appointment).data)


