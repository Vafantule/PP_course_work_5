from rest_framework import serializers

from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Привычки.
    """
    creator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ["id", "creator", "created_at", "updated_at"]

    def validate(self, attrs: dict) -> dict:
        is_rewarding = attrs.get("is_rewarding", getattr(self.instance, "is_rewarding", False))
        related = attrs.get("related_habit", getattr(self.instance, "related_habit", None))
        duration = attrs.get("duration_minutes", getattr(self.instance, "duration_minutes", None))

        if is_rewarding and related is not None:
            raise serializers.ValidationError({"related_habit": "Приятная привычка не должна иметь связанной привычки."})
        if duration is not None and duration > 2:
            raise serializers.ValidationError({"duration_minutes": "Время выполнения не может превышать 2 минуты."})

        return attrs

    def create(self, validated_data: dict) -> dict:
        request = self.context.get("request")
        if request is not None and hasattr(request, "user"):
            validated_data["creator"] = request.user
        return super().create(validated_data)
