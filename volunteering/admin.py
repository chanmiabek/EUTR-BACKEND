from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from educate_us_rise_us.admin_mixins import RichTextAdminMixin
from .models import Opportunity, Signup


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


@admin.register(Opportunity)
class OpportunityAdmin(AdminActionLinksMixin, RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ("description",)
    list_display = ["id", "title", "location", "start_date", "end_date", "is_active", "action_links"]
    list_filter = ["is_active"]
    search_fields = ["title", "description", "location"]


@admin.register(Signup)
class SignupAdmin(AdminActionLinksMixin, RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ("message",)
    list_display = ["id", "user", "opportunity", "created_at", "action_links"]
    list_filter = ["created_at"]
    search_fields = ["user__email", "opportunity__title"]
