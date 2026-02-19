from telegram import Bot
from src.config import settings

_bot: Bot | None = None


def get_bot() -> Bot:
    global _bot
    if _bot is None:
        _bot = Bot(token=settings.telegram_bot_token)
    return _bot


async def send_message(chat_id: int, text: str) -> None:
    bot = get_bot()
    await bot.send_message(chat_id=chat_id, text=text)
