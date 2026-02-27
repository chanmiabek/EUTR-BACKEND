from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from educate_us_rise_us.admin_mixins import RichTextAdminMixin
from .models import MemberProfile


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


@admin.register(MemberProfile)
class MemberProfileAdmin(AdminActionLinksMixin, RichTextAdminMixin, admin.ModelAdmin):
    rich_text_fields = ("bio",)
    list_display = ["id", "user", "location", "skills", "photo", "action_links"]
    search_fields = ["user__email", "user__full_name", "location", "skills"]
