from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone


class User(AbstractBaseUser, PermissionsMixin):
    """
    Модель пользователя.
    """
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="Имя")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="Фамилия")
    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь сотрудником")
    is_active = models.BooleanField(default=True, verbose_name="Активность учётной записи")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Даты и времени регистрации")

    USERNAME_FIELD: str = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self) -> str:
        return self.email or ""
