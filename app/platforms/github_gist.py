from app.config import env
from app.platforms.base import Platform, PostError


class GitHubGist(Platform):
    name = "GitHub Gist"
    required_env = ("GITHUB_TOKEN",)

    async def publish(self, message, client):
        resp = await client.post(
            "https://api.github.com/gists",
            headers={
                "Authorization": f"Bearer {env('GITHUB_TOKEN')}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={
                "description": message[:100],
                "public": True,
                "files": {"post.md": {"content": message}},
            },
        )
        data = self.check(resp, "GitHub gists API")
        if not data.get("html_url"):
            raise PostError("GitHub response had no gist URL")
        return data["html_url"]
