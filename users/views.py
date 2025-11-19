from typing import Any

from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import RegistrationSerializer


class RegistrationView(generics.CreateAPIView):
    """
    Контроллер регистрации нового пользователя.
    """
    serializer_class = RegistrationSerializer

    def create(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
