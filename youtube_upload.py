"""
Uploads a finished video to YouTube. Same one-time setup as the news bot —
see README.md for the full walkthrough (Google Cloud OAuth client, Codespace
login, saving the token as a GitHub Secret).
"""
import json
from pathlib import Path

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.http
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import config

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def _get_authenticated_service():
    creds = None

    if config.YOUTUBE_TOKEN_JSON_ENV:
        creds = Credentials.from_authorized_user_info(
            json.loads(config.YOUTUBE_TOKEN_JSON_ENV), SCOPES
        )
    else:
        token_path = Path(config.YOUTUBE_TOKEN_FILE)
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path(config.YOUTUBE_CLIENT_SECRET_FILE).exists():
                raise RuntimeError(
                    f"Missing {config.YOUTUBE_CLIENT_SECRET_FILE}. This one-time auth step "
                    "must be run interactively (e.g. in a GitHub Codespace), not in CI."
                )
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                config.YOUTUBE_CLIENT_SECRET_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        Path(config.YOUTUBE_TOKEN_FILE).write_text(creds.to_json())

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)


def upload_video(video_path: Path, title: str, description: str,
                  tags: list[str] | None = None, privacy: str = "public") -> str:
    youtube = _get_authenticated_service()

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags or config.YOUTUBE_DEFAULT_TAGS,
            "categoryId": config.YOUTUBE_CATEGORY_ID,
        },
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }

    media = googleapiclient.http.MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading... {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"[OK] Uploaded: https://youtu.be/{video_id}")
    return video_id
