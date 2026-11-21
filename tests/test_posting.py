import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.platforms import Mastodon, default_platforms
from app.platforms.base import Platform, PostError
from app.services import posting_service

VALID = "Check out our latest business platform and grow your online visibility. https://example.com"


class OkPlatform(Platform):
    name = "OkPlatform"

    async def publish(self, message, client):
        return "https://example.com/post/1"


class FailPlatform(Platform):
    name = "FailPlatform"

    async def publish(self, message, client):
        raise PostError("Authentication failed")


class CrashPlatform(Platform):
    name = "CrashPlatform"

    async def publish(self, message, client):
        raise RuntimeError("boom")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    async def fake_check(client, url):
        return True

    monkeypatch.setattr(posting_service, "check_public_access", fake_check)


@pytest.fixture
def client():
    return TestClient(app)


def use(platforms):
    app.dependency_overrides[default_platforms] = lambda: platforms


@pytest.fixture(autouse=True)
def reset_overrides():
    yield
    app.dependency_overrides.clear()


def test_partial_failure_continues(client):
    use([FailPlatform(), OkPlatform(), CrashPlatform()])
    r = client.post("/posting", json={"message": VALID})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    by_name = {x["platform"]: x for x in body["results"]}
    assert by_name["OkPlatform"]["status"] == "success"
    assert by_name["OkPlatform"]["posted_url"] == "https://example.com/post/1"
    assert by_name["OkPlatform"]["public_access"] is True
    assert by_name["FailPlatform"]["error"] == "Authentication failed"
    assert by_name["FailPlatform"]["date"] is None
    assert "boom" in by_name["CrashPlatform"]["error"]


def test_all_fail_means_success_false(client):
    use([FailPlatform()])
    assert client.post("/posting", json={"message": VALID}).json()["success"] is False


def test_missing_credentials_reported(client, monkeypatch):
    monkeypatch.delenv("MASTODON_INSTANCE", raising=False)
    monkeypatch.delenv("MASTODON_ACCESS_TOKEN", raising=False)
    use([Mastodon()])
    res = client.post("/posting", json={"message": VALID}).json()["results"][0]
    assert res["status"] == "failed"
    assert "Missing credentials" in res["error"]


@pytest.mark.parametrize(
    "message",
    [
        "x" * 201,                                    # too long
        "No link in this message at all",             # zero links
        "Two links https://a.com and https://b.com",  # two links
        "Bad link https://nodot",                     # invalid URL
        "Missing scheme www.example.com",             # no http(s)
        "   ",                                        # empty
    ],
)
def test_invalid_messages_rejected(client, message):
    use([OkPlatform()])
    r = client.post("/posting", json={"message": message})
    assert r.status_code == 422
    assert r.json()["success"] is False
    assert r.json()["errors"][0]["message"]


def test_missing_body_field(client):
    r = client.post("/posting", json={})
    assert r.status_code == 422


def test_exactly_200_chars_ok(client):
    use([OkPlatform()])
    url = "https://example.com"
    msg = "a" * (200 - len(url) - 1) + " " + url
    assert len(msg) == 200
    assert client.post("/posting", json={"message": msg}).status_code == 200
