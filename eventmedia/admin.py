from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import EventOverviewVideo


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


@admin.register(EventOverviewVideo)
class EventOverviewVideoAdmin(AdminActionLinksMixin, admin.ModelAdmin):
    list_display = ["id", "title", "is_active", "created_at", "updated_at", "action_links"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["title", "youtube_url", "image_url"]
