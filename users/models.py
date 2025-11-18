from typing import Optional, Any

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Менеджер для модели User.
    """
    def create_user(self, email: str, password: Optional[str] = None, **extra_fields: Any) -> "User":
        if not email:
            raise ValueError("Email обязателен для заполнения.")
        email_normalized: str = self.normalize_email(email)
        user: "User" = self.model(email=email_normalized, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields: Any) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is-superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")
        return self.create_user(email, password, **extra_fields)


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
