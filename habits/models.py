from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Habit(models.Model):
    """
    Модель привычки.
    """
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Привычка",
        help_text="Пользователь: создатель привычки",
    )
    place = models.CharField(max_length=255, blank=True, verbose_name="Место", default="")
    time_of_day = models.TimeField(blank=True, null=True, verbose_name="Время суток")
    action = models.TextField(verbose_name="Действие для привычки")
    is_rewarding = models.BooleanField(default=False, verbose_name="Приятная привычка")
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Связанная привычка",
        related_name="related_by",
    )
    periodicity_days = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Периодичность выполнения привычки"
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Описание вознаграждения",
        default=""
    )
    duration_minutes = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(2)],
        verbose_name="Время выполнения",
        default=1
    )
    is_public = models.BooleanField(verbose_name="Публикация привычки в доступ", default=False)
    created_at = models.DateTimeField(editable=False, verbose_name="Время создания записи", default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время обновления записи")

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.creator} - {self.action[:50]}"
