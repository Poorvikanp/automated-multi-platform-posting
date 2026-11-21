from app.config import env
from app.platforms.base import Platform, PostError


class Telegram(Platform):
    name = "Telegram Channel"
    required_env = ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")

    async def publish(self, message, client):
        token = env("TELEGRAM_BOT_TOKEN")
        resp = await client.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": env("TELEGRAM_CHAT_ID"), "text": message},
        )
        data = self.check(resp, "Telegram sendMessage")
        result = data.get("result") or {}
        username = (result.get("chat") or {}).get("username")
        message_id = result.get("message_id")
        if not (username and message_id):
            raise PostError("Posted, but channel is not public (no username), so no public URL exists")
        return f"https://t.me/{username}/{message_id}"
