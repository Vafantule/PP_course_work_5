from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .apps import UsersConfig

app_name = UsersConfig.name

router = DefaultRouter()
# router.register(r"habits", HabitViewSet, basename="habit")

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),  # маршрут для получения access и refresh токенов  # пояснение: POST username+password -> получает пару токенов
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
] + router.urls
