from typing import Any

from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters, status
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
        user = getattr(self.request, "use", None)
        if user and user.is_authenticated:
            return Habit.objects.filter(models.Q(is_public=True) | models.Q(creator=user))
        return Habit.objects.filter(is_public=True)

    def perform_create(self, serializer: Any) -> None:
        serializer.save(creator=self.request.user)

    def destroy(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
