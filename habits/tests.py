from typing import Any, Dict, Optional
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from datetime import time

from .models import Habit

User = get_user_model()


class HabitAPITests(APITestCase):
    """
    Тестирование для проверки CRUD и поведения списка привычек.
    """
    def setUp(self):
        self.client: APIClient = APIClient()
        self.owner_password = "tgRe951"
        self.owner = User.objects.create_user(email="test_2@exampl.com", password=self.owner_password)
        self.other_password = "tgRe951"
        self.other = User.objects.create_user(email="test_3@exampl.com", password=self.other_password)

    def _get_token_for_user(self, email: str, password: str) -> str:
        url = reverse("users:token_obtain_pair")
        response = self.client.post(url, data={"email": email, "password": password}, format="json")
        self.assertEqual(response.status_code, 200)
        access = response.data.get("access")
        self.assertTrue(access)
        return access

    def test_create_habit_authenticated(self)  -> None:
        token = self._get_token_for_user(self.owner.email, self.owner_password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        payload: Dict[str, Any] = {
            "action": "Тестовое действие",
            "place": "Дом",
            "is_rewarding": False,
            "periodicity_days": 1,
            "time_to_day": time(hour=12, minute=0).isoformat(),
            "is_public": False,
        }
        response = self.client.post("/habits/", data=payload, format="json")
        self.assertEqual(response.status_code, 201)
        habit_id = response.data.get("id")
        habit = Habit.objects.get(pk=habit_id)
        self.assertEqual(habit.creator, self.owner)

    def test_public_habits_visible_to_anonymous(self) -> None:
        Habit.objects.create(creator=self.other,
                             action="Публичная привычка",
                             is_public=True,
                             periodicity_days=1,
                             time_of_day=time(hour=8, minute=0))
        Habit.objects.create(creator=self.other,
                             action="Приватная привычка",
                             is_public=False,
                             periodicity_days=1,
                             time_of_day=time(hour=9, minute=0))
        response = self.client.get("/habits/")
        self.assertEqual(response.status_code, 200)
        results = response.data.get("results", response.data)
        self.assertTrue(any(item.get("action") == "Публичная привычка" for item in results))
        self.assertFalse(any(item.get("action") == "Приватная привычка" for item in results))

    def test_only_owner_can_delete_private_habit(self) -> None:
        habit = Habit.objects.create(creator=self.owner,
                             action="Привычка владельца",
                             is_public=False,
                             periodicity_days=1,
                             time_of_day=time(hour=10, minute=0))
        token_other = self._get_token_for_user(self.other.email, self.other_password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_other}")
        delete_url = f"/habits/{habit.pk}/"
        response = self.client.delete(delete_url)
        self.assertIn(response.status_code, (403, 404))
        token_owner = self._get_token_for_user(self.owner.email, self.owner_password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_owner}")
        response_ok = self.client.delete(delete_url)
        self.assertEqual(response_ok.status_code, 204)
