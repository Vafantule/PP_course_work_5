from typing import Any

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import RegistrationSerializer


class RegistrationView(generics.CreateAPIView):
    """
    Контроллер регистрации нового пользователя.
    """
    serializer_class = RegistrationSerializer

    @swagger_auto_schema(
        operation_summary="Регистрация Пользователя",
        operation_description="Создает нового пользователя по email и паролю.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password", "password_confirm"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email пользователя"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="Пароль"),
                "password_confirm": openapi.Schema(type=openapi.TYPE_STRING, description="Подтверждение пароля"),
                "first_name": openapi.Schema(type=openapi.TYPE_STRING, description="Имя пользователя"),
                "last_name": openapi.Schema(type=openapi.TYPE_STRING, description="Фамилия пользователя"),
            },
        ),
        responses={
            201: openapi.Response(
                description="Пользователь создан",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "email": openapi.Schema(type=openapi.TYPE_STRING),
                        "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                        "second_name": openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: "Validation error (пароли не совпадают или неверный формат)",
        }
    )
    def create(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
