from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
    """
    Админ-класс для модели User.
    """
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "is_superuser")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),  # пояснение: базовые поля (логин и пароль)
        ("Личная информация", {"fields": ("first_name", "last_name", "telegram_chat_id")}),
        ("Права и роли", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Временные метки", {"fields": ("date_joined",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2", "is_active", "is_staff"),
        }),
    )

admin.site.register(User, UserAdmin)
