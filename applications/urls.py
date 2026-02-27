from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ApplicationAdminViewSet,
    ApplicationReviewView,
    ContactCreateView,
    ContactMessageAdminViewSet,
    EventAdminViewSet,
    EventsListView,
    JoinApplicationCreateView,
    PartnerAppointmentAdminViewSet,
    PartnerAppointmentCreateView,
    PartnerAdminViewSet,
    PartnersListView,
    ProgramAdminViewSet,
    ProgramsListView,
    ProjectAdminViewSet,
    ProjectsListView,
    TeamAdminViewSet,
    TeamListView,
    TestimonialAdminViewSet,
    TestimonialsListView,
    VolunteerApplicationCreateView,
)

router = DefaultRouter()
router.include_format_suffixes = False
router.register(r"admin/applications", ApplicationAdminViewSet, basename="admin-applications")
router.register(r"admin/programs", ProgramAdminViewSet, basename="admin-programs")
router.register(r"admin/projects", ProjectAdminViewSet, basename="admin-projects")
router.register(r"admin/events", EventAdminViewSet, basename="admin-events")
router.register(r"admin/team", TeamAdminViewSet, basename="admin-team")
router.register(r"admin/partners", PartnerAdminViewSet, basename="admin-partners")
router.register(r"admin/testimonials", TestimonialAdminViewSet, basename="admin-testimonials")
router.register(r"admin/contact-messages", ContactMessageAdminViewSet, basename="admin-contact-messages")
router.register(r"admin/partner-appointments", PartnerAppointmentAdminViewSet, basename="admin-partner-appointments")

urlpatterns = [
    path("volunteer/", VolunteerApplicationCreateView.as_view(), name="volunteer-apply"),
    path("join-us/", JoinApplicationCreateView.as_view(), name="join-us-apply"),
    path("programs/", ProgramsListView.as_view(), name="programs-list"),
    path("projects/", ProjectsListView.as_view(), name="projects-list"),
    path("events/", EventsListView.as_view(), name="events-list"),
    path("team/", TeamListView.as_view(), name="team-list"),
    path("partners/", PartnersListView.as_view(), name="partners-list"),
    path("testimonials/", TestimonialsListView.as_view(), name="testimonials-list"),
    path("contact/", ContactCreateView.as_view(), name="contact-create"),
    path("partner-appointments/", PartnerAppointmentCreateView.as_view(), name="partner-appointment-create"),
    path("admin/applications/<int:pk>/review/", ApplicationReviewView.as_view(), name="application-review"),
]

urlpatterns += router.urls
