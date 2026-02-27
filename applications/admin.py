from django.conf import settings
from django.contrib import admin
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from educate_us_rise_us.admin_mixins import RichTextAdminMixin

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


class AdminActionLinksMixin:
    @admin.display(description="Actions")
    def action_links(self, obj):
        opts = obj._meta
        change_url = reverse(f"admin:{opts.app_label}_{opts.model_name}_change", args=[obj.pk])
        delete_url = reverse(f"admin:{opts.app_label}_{opts.model_name}_delete", args=[obj.pk])
        return format_html(
            '<a class="button" href="{}">Edit</a>&nbsp;'
            '<a class="button" href="{}" style="background:#ba2121;color:#fff;">Delete</a>',
            change_url,
            delete_url,
        )


@admin.register(Application)
class ApplicationAdmin(AdminActionLinksMixin, RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ("message", "review_note")
    list_display = ["id", "type", "name", "email", "status", "created_at", "reviewed_at", "action_links"]
    search_fields = ["name", "email", "phone", "message", "role"]
    list_filter = ["type", "status", "created_at", "reviewed_at"]
    readonly_fields = ["created_at", "updated_at", "reviewed_at"]


@admin.register(Program)
class ProgramAdmin(AdminActionLinksMixin, RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ("description",)
    list_display = ["id", "title", "focus", "photo", "status", "display_order", "is_active", "action_links"]
    search_fields = ["title", "focus", "description", "beneficiaries"]
    list_filter = ["is_active", "status"]


@admin.register(Project)
class ProjectAdmin(AdminActionLinksMixin, RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ("copy",)
    list_display = ["id", "title", "tag", "photo", "display_order", "is_active", "action_links"]
    search_fields = ["title", "tag", "copy"]
    list_filter = ["is_active", "tag"]


@admin.register(Event)
class EventAdmin(AdminActionLinksMixin, RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ("description",)
    list_display = ["id", "title", "photo", "date", "location", "tag", "display_order", "is_active", "action_links"]
    search_fields = ["title", "location", "tag", "description"]
    list_filter = ["is_active", "tag", "date"]


@admin.register(TeamMember)
class TeamMemberAdmin(AdminActionLinksMixin, RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ("copy",)
    list_display = ["id", "name", "role", "photo", "display_order", "is_active", "action_links"]
    search_fields = ["name", "role", "copy"]
    list_filter = ["is_active", "role"]


@admin.register(Partner)
class PartnerAdmin(AdminActionLinksMixin, admin.ModelAdmin):
    list_display = ["id", "name", "link", "logo", "display_order", "is_active", "action_links"]
    search_fields = ["name", "link"]
    list_filter = ["is_active"]


@admin.register(Testimonial)
class TestimonialAdmin(AdminActionLinksMixin, RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ("quote",)
    list_display = ["id", "name", "role", "photo", "display_order", "is_active", "action_links"]
    search_fields = ["name", "role", "quote"]
    list_filter = ["is_active", "role"]


@admin.register(ContactMessage)
class ContactMessageAdmin(AdminActionLinksMixin, RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ("message",)
    list_display = ["id", "name", "email", "is_resolved", "created_at", "action_links"]
    search_fields = ["name", "email", "message"]
    list_filter = ["is_resolved", "created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(PartnerAppointment)
class PartnerAppointmentAdmin(AdminActionLinksMixin, RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ("message", "admin_response")
    list_display = [
        "id",
        "organization_name",
        "contact_name",
        "email",
        "preferred_date",
        "status",
        "response_sent_at",
        "created_at",
        "action_links",
    ]
    search_fields = ["organization_name", "contact_name", "email", "phone", "topic", "message", "admin_response"]
    list_filter = ["status", "preferred_date", "created_at", "response_sent_at"]
    readonly_fields = ["response_sent_at", "created_at", "updated_at"]
    actions = ["send_response_email"]

    @admin.action(description="Send response email to selected bookings")
    def send_response_email(self, request, queryset):
        sent_count = 0
        for booking in queryset:
            response_text = (booking.admin_response or "").strip()
            if not response_text:
                continue
            subject = f"Response to your partnership appointment: {booking.organization_name}"
            send_mail(
                subject,
                response_text,
                getattr(settings, "DEFAULT_FROM_EMAIL", ""),
                [booking.email],
                fail_silently=True,
            )
            booking.status = PartnerAppointment.STATUS_RESPONDED
            booking.response_sent_at = timezone.now()
            booking.save(update_fields=["status", "response_sent_at", "updated_at"])
            sent_count += 1

        self.message_user(request, f"Sent {sent_count} response email(s).")
