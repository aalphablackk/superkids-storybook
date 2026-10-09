from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import (
    User,
    ParentProfile,
    ChildProfile,
    CampaignerProfile,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "is_staff",
        "is_active",
    )
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    fieldsets = UserAdmin.fieldsets + (
        ("Superkids Role", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Superkids Details", {"fields": ("email", "role")}),
    )


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "created_at")
    search_fields = ("user__username", "user__email", "phone")


@admin.register(ChildProfile)
class ChildProfileAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "parent", "school")
    search_fields = ("first_name", "last_name", "parent__email", "school")


@admin.register(CampaignerProfile)
class CampaignerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "occupation", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email", "occupation")