import logging
from typing import Optional, Dict, Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramClient:
    """
    Отправка сообщений через Telegram Bot API.
    """
    def __init__(self, token: Optional[str] = None) -> None:
        self.token: str = token or getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        self.base_url: str = f"{settings.TELEGRAM_URL}{self.token}"

    def send_message(self, chat_id: str, message: str, parse_mode: Optional[str] = "Markdown") -> Dict[str, Any]:
        url: str = f"{self.base_url}/sendMessage"
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": message,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            if not data.get("ok", False):
                logger.error("Telegram API возвращает ошибку: %s", data)
            return data
        except Exception as exception:
            logger.exception("Ошибка отправки сообщения в Telegram: $s", exception)
            return {"ok": False, "error": str(exception)}
