from typing import Dict, Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Habit
from .validators import HabitValidator

User = get_user_model()


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Привычки.
    """
    creator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ["id", "creator", "created_at", "updated_at"]
        validators = [HabitValidator()]

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        validator = HabitValidator()
        validator.validate_with_instance(attrs, getattr(self, "instance", None))
        return attrs

    def create(self, validated_data: dict) -> dict:
        request = self.context.get("request")
        if request is not None and hasattr(request, "user"):
            validated_data["creator"] = request.user
        return super().create(validated_data)
