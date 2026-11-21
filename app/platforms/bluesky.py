from datetime import datetime, timezone

from app.config import env
from app.platforms.base import Platform, PostError
from app.schemas import find_urls


class Bluesky(Platform):
    name = "Bluesky"
    required_env = ("BLUESKY_HANDLE", "BLUESKY_APP_PASSWORD")

    async def publish(self, message, client):
        base = env("BLUESKY_SERVICE", "https://bsky.social").rstrip("/")

        session = self.check(
            await client.post(
                f"{base}/xrpc/com.atproto.server.createSession",
                json={"identifier": env("BLUESKY_HANDLE"), "password": env("BLUESKY_APP_PASSWORD")},
            ),
            "Bluesky createSession",
        )
        did, jwt = session["did"], session["accessJwt"]

        record = {
            "$type": "app.bsky.feed.post",
            "text": message,
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        # Make the CTA link clickable (facets use UTF-8 byte offsets).
        urls = find_urls(message)
        if urls:
            raw = message.encode("utf-8")
            start = raw.find(urls[0].encode("utf-8"))
            if start >= 0:
                record["facets"] = [{
                    "index": {"byteStart": start, "byteEnd": start + len(urls[0].encode("utf-8"))},
                    "features": [{"$type": "app.bsky.richtext.facet#link", "uri": urls[0]}],
                }]

        created = self.check(
            await client.post(
                f"{base}/xrpc/com.atproto.repo.createRecord",
                headers={"Authorization": f"Bearer {jwt}"},
                json={"repo": did, "collection": "app.bsky.feed.post", "record": record},
            ),
            "Bluesky createRecord",
        )
        uri = created.get("uri", "")  # at://did:plc:xxx/app.bsky.feed.post/<rkey>
        if not uri:
            raise PostError("Bluesky response had no record URI")
        rkey = uri.rsplit("/", 1)[-1]
        return f"https://bsky.app/profile/{did}/post/{rkey}"
