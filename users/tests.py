from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class RegistrationAndAuthTests(APITestCase):
    """
    Тестирование регистрации и получения JWT токенов.
    """
    def setUp(self) -> None:
        self.client: APIClient = APIClient()

    def test_register_user_creates_user(self) -> None:
        payload: Dict[str, Any] = {
            "email": "test@example.com",
            "password": "tgRe951?",
            "password_confirm": "tgRe951?",
            "first_name": "Valio",
            "second_name": "Lavio",
        }
        url = reverse("users:register")
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email=payload["email"]).exists())

    def test_obtain_token_returns_access_and_refresh(self) -> None:
        password = "tgRe951"
        user = User.objects.create_user(email="test_1@example.com", password=password)
        payload: Dict[str, Any] = {"email": user.email, "password": password}
        url = reverse("users:token_obtain_pair")
        response = self.client.post(url, data=payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
