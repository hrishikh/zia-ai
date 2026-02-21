"""
Email tool — send emails via Gmail API.
Migrated from the original executor.py compose_email().
"""

import os
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from tools.base_tool import BaseTool

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


class EmailTool(BaseTool):
    name = "send_email"
    description = (
        "Send an email using Gmail. Use this when the user wants to email someone."
    )
    parameters = {
        "type": "object",
        "properties": {
            "recipient": {
                "type": "string",
                "description": "Email address of the recipient.",
            },
            "subject": {
                "type": "string",
                "description": "Email subject line.",
            },
            "body": {
                "type": "string",
                "description": "Full email body text.",
            },
        },
        "required": ["recipient", "subject", "body"],
        "additionalProperties": False,
    }

    def execute(self, *, recipient: str, subject: str, body: str) -> dict:
        service = self._get_gmail_service()

        message = MIMEText(body)
        message["to"] = recipient
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()

        return {"status": "sent", "to": recipient, "subject": subject}

    # ── Gmail OAuth2 (reused from original executor.py) ──

    @staticmethod
    def _get_gmail_service():
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", GMAIL_SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None

            if not creds:
                if not os.path.exists("client_secret.json"):
                    raise FileNotFoundError(
                        "Missing 'client_secret.json'. "
                        "Download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    "client_secret.json", GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)
