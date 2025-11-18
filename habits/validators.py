from typing import Dict, Any, Optional

from rest_framework import serializers
from .models import Habit


class HabitValidator:
    """
    Валидатор объекта для модели/сериализатора Habit.
    """
    def __call__(self, attrs: Dict[str, Any]) -> None:
        is_rewarding: Optional[bool] = attrs.get("is_rewarding")
        related_habit: Optional[Any] = attrs.get("related_habit")
        reward: Optional[str] = attrs.get("reward")
        duration_seconds = Optional[int] = attrs.get("duration_seconds")
        periodicity_days = Optional[int] = attrs.get("periodicity_days")

        if (related_habit is not None) and (reward not in (None, "", b"", False)):
            raise serializers.ValidationError({
                "non_field_errors": ["Нельзя одновременно указывать и related_habit, и reward."],
                "related_habit": ["Нельзя указать связную привычку при одновременном указании вознаграждения."],
                "reward": ["Нельзя указать вознаграждение при наличии связной привычки."],
            })

        if is_rewarding is True:
            if (related_habit is not None) and (reward not in (None, "", b"", False)):
                raise serializers.ValidationError({
                    "is_rewarding": ["Приятная привычка не должна иметь related_habit или reward."],
                    "related_habit": ["Приятная привычка не должна иметь связную привычку."],
                    "reward": ["Приятная привычка не должна иметь текст вознаграждения."],
                })

        if duration_seconds is not None:
            if duration_seconds > 120:
                raise serializers.ValidationError({
                    "duration_seconds": ["Время выполнения не может превышать 120 секунд."]
                })
            if duration_seconds < 0:
                raise serializers.ValidationError({
                    "duration_seconds": ["Время выполнения не может быть отрицательным."]
                })

        if periodicity_days is not None:
            if periodicity_days < 1 or periodicity_days > 7:
                raise serializers.ValidationError({
                    "periodicity_days": ["Периодичность должна быть от 1 до 7 дней (включительно)."]
                })

        if isinstance(related_habit, Habit):
            if not related_habit.is_rewarding:
                raise serializers.ValidationError({
                    "related_habit": ["Связанная привычка должна быть помечена как приятная."]
                })

    def validate_with_instance(self, attrs: Dict[str, Any], instance: Optional[Habit]) -> None:
        merged_is_rewarding: bool = attrs.get(
            "is_rewarding",
            getattr(instance, "is_rewarding", False) if instance is not None else False
        )
        merged_related: Optional[Habit] = attrs.get(
            "related_habit",
            getattr(instance, "related_habit", None) if instance is not None else None
        )
        merged_reward: str = attrs.get(
            "reward",
            getattr(instance, "reward", "") if instance is not None else ""
        )
        merged_duration: Optional[int] = attrs.get(
            "duration_seconds",
            getattr(instance, "duration_seconds", None) if instance is not None else None
        )
        merged_periodicity: int = attrs.get(
            "periodicity_days",
            getattr(instance, "periodicity_days", 1) if instance is not None else 1
        )

        merged_attrs: Dict[str, Any] = {
            "is_rewarding": merged_is_rewarding,
            "related_habit": merged_related,
            "reward": merged_reward,
            "duration_seconds": merged_duration,
            "periodicity_days": merged_periodicity,
        }

        self.__call__(merged_attrs)
