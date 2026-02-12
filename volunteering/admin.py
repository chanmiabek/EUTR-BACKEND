from django.contrib import admin
from .models import Opportunity, Signup

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'location', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description', 'location']

@admin.register(Signup)
class SignupAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'opportunity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'opportunity__title']
