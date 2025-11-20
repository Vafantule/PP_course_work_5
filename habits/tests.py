from typing import Any, Dict, List
from unittest.mock import patch, Mock

import requests

import config.celery as celery_module
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.test import APITestCase, APIClient
from datetime import datetime, time
from celery import Celery

from .models import Habit
from .services import TelegramClient
from .tasks import send_due_habit_reminders

User = get_user_model()


class HabitAPITests(APITestCase):
    """
    Тестирование для проверки CRUD и поведения списка привычек.
    """
    def setUp(self):
        self.client: APIClient = APIClient()
        self.owner_password = "tgRe951"
        self.owner = User.objects.create_user(email="test_2@example.com", password=self.owner_password)
        self.other_password = "tgRe951"
        self.other = User.objects.create_user(email="test_3@example.com", password=self.other_password)

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


class TelegramClientTests(TestCase):
    """
    Тестирование TelegramClient.
    """
    def setUp(self) -> None:
        self.client = TelegramClient(token="TEST_TOKEN")

    @patch("habits.services.requests.post")
    def test_send_message_success(self, mock_post: Mock) -> None:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"ok": True, "result": {"message_id": 1}}
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        result: Dict[str, Any] = self.client.send_message(chat_id="12345", message="Test")
        self.assertTrue(result.get("ok", False))
        self.assertIn("result", result)

    @patch("habits.services.requests.post")
    def test_send_message_chat_not_fount(self, mock_post: Mock) -> None:
        mock_response = Mock()
        http_error = requests.HTTPError("400 Ошибка клиента: неверный запрос URL")
        http_error.response = mock_response
        mock_response.json.return_value = {
            "ok": False,
            "error_code": 400,
            "description": "Bad Request: chat not found"
        }
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = http_error
        mock_post.return_value = mock_response
        result = self.client.send_message(chat_id="1722262177", message="Test")
        self.assertFalse(result.get("ok", True))
        http_description = result.get("http_description") or result.get("error") or ""
        self.assertIsNotNone(http_description)
        self.assertTrue(
            ("chat not found" in str(http_description).lower())
            or ("bad request" in str(http_description).lower())
            or ("400" in str(http_description).lower()),
            msg=f"Неожиданное описание ошибки: {http_description}"
        )


class CeleryConfigTests(SimpleTestCase):
    """
    Тесты конфигурации Celery.
    """
    def test_app_object_exists(self) -> None:
        self.assertTrue(hasattr(celery_module, "app"),
                        msg="Модуль config.celery должен предоставлять атрибут `app`")

    def test_app_is_celery_instance(self) -> None:
        app: Any = getattr(celery_module, "app", None)
        self.assertIsInstance(app, Celery, msg="config.celery.app должен быть экземпляром celery.Celery")

    def test_autodiscover_tasks_in_callable(self):
        app: Any = getattr(celery_module, "app", None)
        self.assertTrue(hasattr(app, "autodiscover_tasks"),
                        msg="Приложение Celery должно иметь метод autodiscover_tasks")
        self.assertTrue(callable(getattr(app, "autodiscover_tasks")),
                        msg="autodiscover_tasks должен быть доступен для вызова")



class SendDueHabitRemindersTests(TestCase):
    """
    Тесты конфигурации tasks (периодические задания).
    """
    def setUp(self) -> None:
        self.user_with_chat: User = User.objects.create_user(email="test_4@example.com", password="pass1234")
        self.user_with_chat.telegram_chat_id = "12345678"
        self.user_with_chat.save()
        self.user_without_chat: User = User.objects.create_user(email="test_5@example.com", password="pass1234")
        now: datetime = timezone.localtime()
        self.fixed_now: datetime = timezone.make_aware(
            datetime(year=now.year, month=now.month, day=now.day,
                     hour=now.hour, minute=now.minute, second=now.second),
            timezone.get_current_timezone()
        )

    @patch("habits.tasks.TelegramClient.send_message")
    @patch("habits.tasks.timezone.localtime")
    def test_send_message_for_due_habit(self, mock_localtime: Mock, mock_send: Mock) -> None:
        mock_localtime.return_value = self.fixed_now
        due_habit: Habit = Habit.objects.create(
            creator=self.user_with_chat,
            action="Тестовое действие",
            is_public=False,
            periodicity_days=1,
            time_of_day=self.fixed_now.time(),
        )
        mock_send.return_value = {"ok": True, "result": {"message_id": 1}}
        result: Dict[str, Any] = send_due_habit_reminders.run()
        self.assertEqual(result.get("count_due"), 1, msg=f"Ожидается одна привычка, на выходе: {result}")
        self.assertTrue(mock_send.called,
                        msg=f"Ожидается, что TelegramClient.send_message будет вызван по привычке. Результат={result}")
        called_args, called_kwargs = mock_send.call_args
        combined = " ".join([str(called_args), str(called_kwargs)])
        self.assertIn(str(self.user_with_chat.telegram_chat_id), combined,
                      msg=f"Ожидаемый chat_id {self.user_with_chat.telegram_chat_id} "
                          f"в send_message аргументы вызова: {combined}")

    @patch("habits.tasks.TelegramClient.send_message")
    @patch("habits.tasks.timezone.localtime")
    def test_skip_id_no_chat_id(self, mock_localtime: Mock, mock_send: Mock) -> None:
        mock_localtime.return_value = self.fixed_now
        due_habit: Habit = Habit.objects.create(
            creator=self.user_without_chat,
            action="Другое тестовое действие",
            is_public=False,
            periodicity_days=1,
            time_of_day=self.fixed_now.time(),
        )
        result: Dict[str, Any] = send_due_habit_reminders.run()
        mock_send.assert_not_called()
        self.assertEqual(result.get("sent"), [])
        self.assertEqual(result.get("count_due"), 1)
