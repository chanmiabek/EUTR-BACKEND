from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import EventOverviewVideoAdminViewSet, EventOverviewVideoListView, EventOverviewVideoView

router = DefaultRouter()
router.include_format_suffixes = False
router.register(r"admin/event-overview-videos", EventOverviewVideoAdminViewSet, basename="admin-event-overview-video")

urlpatterns = [
    path("event-overview-video/", EventOverviewVideoView.as_view(), name="event-overview-video"),
    path("event-overview-videos/", EventOverviewVideoListView.as_view(), name="event-overview-videos"),
]

urlpatterns += router.urls
