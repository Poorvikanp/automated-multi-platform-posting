# Automated Multi-Platform Posting System

A Python FastAPI service that accepts a short message containing exactly one CTA link and publishes it to multiple platforms using their official APIs.

Each platform is processed independently and concurrently. If one platform fails, the remaining platforms continue publishing.

## Features

- Publishes one message to five platforms.
- Validates message length (maximum 200 characters).
- Requires exactly one valid HTTP/HTTPS CTA link.
- Executes platform publishing concurrently.
- Handles individual platform failures without interrupting other platforms.
- Returns publishing status, post URL, date, time, and public-access information.
- Loads credentials securely through environment variables.

## Supported Platforms

| Platform | API used | Authentication | Published content |
|---|---|---|---|
| Mastodon | `POST /api/v1/statuses` | Bearer token | Status |
| Bluesky | AT Protocol `createSession` and `createRecord` | App password | Post |
| DEV Community | `POST /api/articles` | API key | Article |
| GitHub Gist | `POST /gists` | Personal access token with Gist permission | Public Gist |
| Telegram | Bot API `sendMessage` | Bot token | Channel message |

**Note:** DEV Community publishes content as an article, while GitHub Gist publishes a public text snippet. These are publishing destinations with different content formats.

### Adding a Platform

To add another platform:
1. Create a new class in `app/platforms/`.
2. Subclass the existing `Platform` base class.
3. Implement the `publish()` method.
4. Register the platform in `app/platforms/__init__.py`.

## Technology Stack

- Python 3
- FastAPI
- Uvicorn
- Pydantic
- HTTPX
- Python environment variables

## Project Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd automated-posting
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file:

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**Linux/macOS:**

```bash
cp .env.example .env
```

Add the required platform credentials to `.env`.

Never commit your `.env` file or expose API tokens publicly.

### 5. Start the application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

The API documentation is available at:

`http://localhost:4000/docs`

## API Usage

### Endpoint

`POST http://localhost:4000/posting`

### Request Body

```json
{
  "message": "Check out our latest platform and grow your online visibility. https://example.com"
}
```

### Validation Rules

- Maximum message length: 200 characters.
- Exactly one CTA link is required.
- The link must be a valid HTTP or HTTPS URL.
- Invalid requests return HTTP `422`.

Example validation error:

```json
{
  "success": false,
  "errors": [
    {
      "field": "message",
      "message": "Message must contain exactly one CTA link (found 2)."
    }
  ]
}
```

### Sample Response

```json
{
  "success": true,
  "results": [
    {
      "platform": "Mastodon",
      "status": "success",
      "posted_url": "https://mastodon.social/@thoju/117654668784216655",
      "public_access": true,
      "date": "2026-11-21",
      "time": "18:59:33",
      "error": null
    },
    {
      "platform": "Bluesky",
      "status": "success",
      "posted_url": "https://bsky.app/profile/did:plc:ii4rjslavxglhkcaler4ss5i/post/3n2t7gzdkhp2a",
      "public_access": true,
      "date": "2026-11-21",
      "time": "18:59:34",
      "error": null
    },
    {
      "platform": "DEV Community",
      "status": "success",
      "posted_url": "https://dev.to/poorvika_np_d13d0e132d81/testing-my-python-multi-platform-posting-system-on-bluesk-o7n",
      "public_access": true,
      "date": "2026-11-21",
      "time": "18:59:33",
      "error": null
    },
    {
      "platform": "GitHub Gist",
      "status": "success",
      "posted_url": "https://gist.github.com/Poorvikanp/859af52140faf4feb67e647c08421c70",
      "public_access": true,
      "date": "2026-11-21",
      "time": "18:59:34",
      "error": null
    },
    {
      "platform": "Telegram Channel",
      "status": "success",
      "posted_url": "https://t.me/poorvika_posting_demo/5",
      "public_access": false,
      "date": "2026-11-21",
      "time": "18:59:34",
      "error": null
    }
  ]
}
```

**Response interpretation:**

- `success`: Overall operation succeeds when at least one platform publishes successfully.
- `status`: Individual platform publishing status (`success` or `failed`).
- `posted_url`: URL returned for the published content.
- `public_access`: Result of the application's anonymous URL accessibility check.
- `date` and `time`: Publishing timestamp.
- `error`: Error details when publishing fails.

A successful API publishing operation and a successful anonymous URL accessibility check are separate outcomes. Therefore, `public_access: false` does not automatically mean publishing failed.

## Running Tests

Run the automated test suite:

```bash
pytest -v
```

Tests cover:

- Message validation.
- Invalid and multiple CTA links.
- Partial platform failures.
- Platform exceptions.
- Missing credentials.

Platform API calls are mocked during tests, so no real posts are created.

## Project Structure

```text
automated-posting/
│
├── app/
│   ├── main.py
│   ├── schemas.py
│   ├── config.py
│   │
│   ├── platforms/
│   │   ├── base.py
│   │   ├── mastodon.py
│   │   ├── bluesky.py
│   │   ├── devto.py
│   │   ├── github_gist.py
│   │   └── telegram.py
│   │
│   └── services/
│       └── posting_service.py
│
├── tests/
│   └── test_posting.py
│
├── docs/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Security

- API credentials are loaded from environment variables.
- The `.env` file is excluded from Git using `.gitignore`.
- No API tokens or private credentials should be committed to the repository.
- Use platform-specific tokens and permissions with only the required access.

## Live Deployment

- Live API: https://automated-multi-platform-posting.onrender.com/
- Swagger Documentation: https://automated-multi-platform-posting.onrender.com/docs

Deployed using Render.

## Author

**Poorvika N P**

