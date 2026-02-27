from django.db import transaction
from rest_framework import filters, generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from applications.pagination import AdminResultsSetPagination

from .models import EventOverviewVideo
from .serializers import EventOverviewVideoSerializer


def parse_bool(value):
    if value is None:
        return None
    lowered = str(value).strip().lower()
    if lowered in {"1", "true", "yes", "y", "on"}:
        return True
    if lowered in {"0", "false", "no", "n", "off"}:
        return False
    return None


class EventOverviewVideoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        video = EventOverviewVideo.objects.filter(is_active=True).first() or EventOverviewVideo.objects.first()
        if not video:
            return Response({"detail": "No event overview video found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = EventOverviewVideoSerializer(video)
        return Response(serializer.data)


class EventOverviewVideoListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = EventOverviewVideoSerializer

    def get_queryset(self):
        return EventOverviewVideo.objects.filter(is_active=True).order_by("-created_at")


class EventOverviewVideoAdminViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    pagination_class = AdminResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    queryset = EventOverviewVideo.objects.all().order_by("-created_at")
    serializer_class = EventOverviewVideoSerializer
    search_fields = ["title", "youtube_url"]
    ordering_fields = ["created_at", "updated_at", "title", "is_active"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        is_active = parse_bool(self.request.query_params.get("is_active"))
        title = self.request.query_params.get("title")

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.is_active:
            EventOverviewVideo.objects.exclude(pk=instance.pk).update(is_active=False)

    @transaction.atomic
    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.is_active:
            EventOverviewVideo.objects.exclude(pk=instance.pk).update(is_active=False)
