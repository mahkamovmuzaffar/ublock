from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('bio', 'phone_number', 'is_kyc_verified')}),
    )
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_kyc_verified', 'is_active', 'date_joined']
    list_filter = BaseUserAdmin.list_filter + ('is_kyc_verified',)
    search_fields = ['username', 'email', 'first_name', 'last_name']
