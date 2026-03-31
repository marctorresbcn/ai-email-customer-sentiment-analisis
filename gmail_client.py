import base64
import html2text
import os
import re
from typing import Any

from domain import Email
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailEmailSource:
    def __init__(self, credentials_path: str, token_path: str, user_id: str = "me", labels: list[str] | None = None, query: str = ""):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.user_id = user_id
        self.labels = labels or ["INBOX"]
        self.query = query
        self.service = None

    def _ensure_service(self):
        if self.service is None:
            self.service = get_service(self.credentials_path, self.token_path)

    def list_email_ids(self, max_results: int = 100) -> list[str]:
        self._ensure_service()
        request = self.service.users().messages().list(
            userId=self.user_id,
            labelIds=self.labels,
            q=self.query,
            maxResults=max_results,
        )
        response = request.execute()
        return [item["id"] for item in response.get("messages", [])]

    def fetch_email(self, email_id: str):
        self._ensure_service()
        message = self.service.users().messages().get(userId=self.user_id, id=email_id, format="full").execute()
        headers = parse_headers(message)
        body_text = clean_text(extract_message_body(message), max_chars=4000)
        return Email(
            id=email_id,
            thread_id=message.get("threadId", ""),
            sender=headers.get("from", ""),
            subject=headers.get("subject", ""),
            date=headers.get("date", ""),
            body=body_text,
        )


def get_service(credentials_path: str, token_path: str):
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def fetch_message_ids(service, user_id: str = "me", labels: list[str] = None, query: str = "", max_results: int = 100):
    labels = labels or ["INBOX"]
    request = service.users().messages().list(userId=user_id, labelIds=labels, q=query, maxResults=max_results)
    response = request.execute()
    return [item["id"] for item in response.get("messages", [])]


def get_message(service, user_id: str, message_id: str) -> dict[str, Any]:
    return service.users().messages().get(userId=user_id, id=message_id, format="full").execute()


def _decode_part(part) -> str:
    data = part.get("body", {}).get("data")
    if not data:
        return ""
    text_data = base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="ignore")
    return text_data


def _extract_text_from_parts(parts: list) -> str:
    collected = []
    for part in parts:
        mime_type = part.get("mimeType", "")
        if mime_type == "text/plain":
            collected.append(_decode_part(part))
        elif mime_type == "text/html":
            html = _decode_part(part)
            collected.append(html2text.html2text(html))
        elif part.get("parts"):
            collected.append(_extract_text_from_parts(part.get("parts")))
    return "\n".join(p for p in collected if p)


def extract_message_body(message: dict[str, Any]) -> str:
    payload = message.get("payload", {})
    mime_type = payload.get("mimeType", "")

    if mime_type == "text/plain":
        return _decode_part(payload)
    if mime_type == "text/html":
        raw_html = _decode_part(payload)
        return html2text.html2text(raw_html)

    if payload.get("parts"):
        return _extract_text_from_parts(payload.get("parts"))

    return ""


def parse_headers(message: dict[str, Any]) -> dict[str, str]:
    headers = {item.get("name", "").lower(): item.get("value", "") for item in message.get("payload", {}).get("headers", [])}
    return {
        "from": headers.get("from", ""),
        "subject": headers.get("subject", ""),
        "date": headers.get("date", ""),
    }


def clean_text(text: str, max_chars: int = 2500) -> str:
    if not text:
        return ""

    txt = re.sub(r"\s+", " ", text).strip()
    return txt[:max_chars]
