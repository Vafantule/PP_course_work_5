from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# Установка переменной окружения для настроек проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Создание экземпляра объекта Celery
app = Celery("config")

# Загрузка настроек из файла Django
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение и регистрация задач из файлов tasks.py в приложениях Django
app.autodiscover_tasks()


# Пример расписания. Включаем задачу, которая каждые 60 секунд проверяет просроченные напоминания и отправляет уведомления.
# Вы можете изменить интервал или добавить дополнительные задачи.
app.conf.beat_schedule: Dict[str, Any] = {  # пояснение: определяем расписание Celery Beat, аннотируем тип словаря
    "send-due-habit-reminders-every-minute": {  # пояснение: уникальное имя для задачи в расписании
        "task": "reminders.tasks.send_due_habit_reminders",  # пояснение: точное имя задачи для вызова
        "schedule": 60.0,  # пояснение: интервал в секундах (60 секунд)
        "args": (),  # пояснение: аргументы задачи (пустой кортеж)
    },
}