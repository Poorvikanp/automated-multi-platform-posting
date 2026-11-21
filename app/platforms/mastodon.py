from app.config import env
from app.platforms.base import Platform, PostError


class Mastodon(Platform):
    name = "Mastodon"
    required_env = ("MASTODON_INSTANCE", "MASTODON_ACCESS_TOKEN")

    async def publish(self, message, client):
        instance = env("MASTODON_INSTANCE").rstrip("/")
        resp = await client.post(
            f"{instance}/api/v1/statuses",
            headers={"Authorization": f"Bearer {env('MASTODON_ACCESS_TOKEN')}"},
            json={"status": message, "visibility": "public"},
        )
        data = self.check(resp, "Mastodon statuses API")
        if not data.get("url"):
            raise PostError("Mastodon response had no post URL")
        return data["url"]
