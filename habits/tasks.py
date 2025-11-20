import logging
from datetime import timedelta
from typing import Any, Dict, List

from celery import shared_task
from django.utils import timezone
from django.db import models

from .services import TelegramClient


logger = logging.getLogger(__name__)


def _get_models() -> Any:
    """
    Функция импорта моделей Habit & User.
    """
    from habits.models import Habit
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return Habit, User


@shared_task(bind=True, name="habits.tasks.send_due_habit_reminders")
def send_due_habit_reminders(self) -> Dict[str, Any]:
    """
    Функция периодической отправки уведомлений пользователям о необходимости выполнения привычки в данной время.
    """
    Habit, User = _get_models()
    time_now = timezone.localtime()
    logger.debug("Запуск send_due_habit_reminders в %s", time_now)

    window_start = (time_now - timedelta(seconds=30)).time()
    window_end =  (time_now + timedelta(seconds=30)).time()

    due_queryset = (models.Q(time_of_day__isnull=False) &
                    models.Q(time_of_day__gte=window_start) &
                    models.Q(time_of_day__lte=window_end))
    due_habits = Habit.objects.filter(due_queryset)

    client = TelegramClient()
    sent: List[Dict[str, Any]] = []
    for habit in due_habits:
        try:
            user = habit.creator
            chat_id = getattr(user, "telegram_chat_id", None)
            if not chat_id:
                logger.info("У пользователя %s не доступен telegram_chat_id, пропущенная привычка %s",
                            user,
                            habit.id)
                continue
            text = (f"Напоминание: время выполнить привычку - {habit.action}.\n"
                    f"Место: {habit.place or 'не указано'}.\n"
                    f"Вознаграждение: {habit.reward or 'не указано'}")
            result = client.send_message(chat_id=str(chat_id), message=text, parse_mode="Markdown")
            sent.append(
                {
                    "habit_id": habit.id,
                    "user_id": getattr(user, "pk", None),
                    "result": result
                }
            )
            logger.info("Отправлено напоминание о привычке %s пользователю %s: %s",
                        habit.id,
                        user,
                        result)
        except Exception as exception:
            logger.exception("Ошибка при отправке напоминания о привычке %s: %s",
                             getattr(habit, "id", None),
                             exception)
            sent.append(
                {
                    "habit_id": getattr(habit, "id", None),
                    "error": str(exception)
                }
            )
    return {
        "timestamp": time_now.isoformat(),
        "count_due": due_habits.count(),
        "sent": sent
    }
