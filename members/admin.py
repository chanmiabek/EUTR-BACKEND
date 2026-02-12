from django.contrib import admin
from .models import MemberProfile

@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'location', 'skills']
    search_fields = ['user__email', 'user__full_name', 'location', 'skills']
