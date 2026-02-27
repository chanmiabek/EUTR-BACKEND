from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from educate_us_rise_us.admin_mixins import RichTextAdminMixin
from .models import Donation


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


@admin.register(Donation)
class DonationAdmin(AdminActionLinksMixin, RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ("message", "failed_reason")
    list_display = [
        "id",
        "donor_name",
        "amount",
        "currency",
        "payment_method",
        "provider",
        "status",
        "created_at",
        "action_links",
    ]
    list_filter = ["payment_method", "provider", "status", "currency"]
    search_fields = ["donor_name", "email"]
