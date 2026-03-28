from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CreatorProfile, StudentProfile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "full_name", "role", "is_active", "email_verified", "created_at")
    list_filter = ("role", "is_active", "email_verified", "is_staff")
    search_fields = ("email", "full_name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name", "avatar", "bio", "phone")}),
        ("Role & Status", {"fields": ("role", "email_verified")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Dates", {"fields": ("created_at", "updated_at", "last_login")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "role", "password1", "password2"),
            },
        ),
    )


@admin.register(CreatorProfile)
class CreatorProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user", "headline", "is_verified", "total_earnings",
        "total_students", "commission_rate",
    )
    list_filter = ("is_verified", "stripe_onboarding_complete")
    search_fields = ("user__email", "user__full_name", "headline")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user",)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user", "completed_courses_count", "total_learning_hours",
        "streak_days", "last_active_at",
    )
    search_fields = ("user__email", "user__full_name")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user",)
