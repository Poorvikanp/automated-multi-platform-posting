from app.config import env
from app.platforms.base import Platform, PostError


class DevTo(Platform):
    name = "DEV Community"
    required_env = ("DEVTO_API_KEY",)

    async def publish(self, message, client):
        title = message if len(message) <= 60 else message[:57].rstrip() + "..."
        resp = await client.post(
            "https://dev.to/api/articles",
            headers={"api-key": env("DEVTO_API_KEY")},
            json={"article": {"title": title, "body_markdown": message, "published": True}},
        )
        data = self.check(resp, "DEV articles API")
        if not data.get("url"):
            raise PostError("DEV response had no article URL")
        return data["url"]
