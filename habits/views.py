from typing import Any, Optional

from django.db import models
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Habit
from .pagination import HabitPagination
from .serializers import HabitSerializer
from .permissions import IsOwnerOrReadOnly


class HabitViewSet(viewsets.ModelViewSet):
    """
    Набор представлений для работы с привычками.
    """
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["action", "place", "reward"]
    ordering_fields = ["created_at", "updated_at", "periodicity_days"]
    pagination_class = HabitPagination

    def get_queryset(self):
        user: Optional[Any]  = getattr(self.request, "user", None)
        if user and getattr(user, "is_authenticated", False):
            return Habit.objects.filter(models.Q(is_public=True) | models.Q(creator=user))
        return Habit.objects.filter(is_public=True)

    def perform_create(self, serializer: Any) -> None:
        serializer.save(creator=self.request.user)

    def perform_update(self, serializer: HabitSerializer) -> None:
        instance: Habit = self.get_object()
        self.check_object_permissions(self.request, instance)
        serializer.save()

    @swagger_auto_schema(
        method="post",
        operation_summary="Отметить привычку как выполненную",
        operation_description="Пометка выполнения привычки",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "note": openapi.Schema(type=openapi.TYPE_STRING, description="Заметка о выполнении"),
            },
        ),
        responses={
            200: openapi.Response(description="Привычка отмечена как выполненная"),
            404: "не найдено",
        },
    )
    @action(detail=True, methods=["post"], url_path="mark_done")
    def mark_done(self, request: Any, pk: int) -> Response:
        habit: Habit = self.get_object()
        note: Optional[str] = request.data.get("note")
        return Response(
            {
                "detail": f"Привычка {habit.pk} отмечена как выполненная",
                "note": note,
            },
            status=status.HTTP_200_OK
        )

    def destroy(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
