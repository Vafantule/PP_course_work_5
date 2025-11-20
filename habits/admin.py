from django.contrib import admin

from .models import Habit


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ("id", "creator", "action", "is_public", "is_rewarding", "periodicity_days", "duration_minutes")
    search_fields = ("action", "place", "reward", "creator__username")
    list_filter = ("is_public", "is_rewarding", "periodicity_days")
