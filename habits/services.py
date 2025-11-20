import logging
from typing import Optional, Dict, Any

import requests
from requests.exceptions import RequestException
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramClient:
    """
    Отправка сообщений через Telegram Bot API.
    """
    def __init__(self, token: Optional[str] = None) -> None:
        self.token: str = token or getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        self.base_url: str = f"{getattr(settings, 'TELEGRAM_URL')}{self.token}"

    def send_message(self, chat_id: str, message: str, parse_mode: Optional[str] = "Markdown") -> Dict[str, Any]:
        url: str = f"{self.base_url}/sendMessage"
        if not message or not message.strip():
            logger.warning("Попытка отправить пустое сообщение в Telegram для chat_id=%s — пропущено",
                           chat_id)
            return {"ok": False, "error": "текст сообщения пуст (local check)"}

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
                logger.error("Telegram API возвращает ошибку для chat_id=%s: %s",
                             chat_id,
                             data)
            return data
        except RequestException as exception:
            logger.exception("Ошибка отправки сообщения в Telegram для chat_id=%s: %s",
                             chat_id,
                             str(exception))
            return {"ok": False, "error": str(exception)}
