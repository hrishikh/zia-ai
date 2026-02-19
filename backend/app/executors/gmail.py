"""
Zia AI — Gmail Executor
Send and read emails via Gmail API with OAuth2.
"""

import base64
import os
from email.mime.text import MIMEText
from typing import Any, Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.executors.base import BaseExecutor

SCOPES = ["https://www.googleapis.com/auth/gmail.send",
           "https://www.googleapis.com/auth/gmail.readonly"]


class GmailExecutor(BaseExecutor):
    """Gmail send/read executor using Google API."""

    def get_supported_actions(self) -> List[str]:
        return ["gmail.send_email", "gmail.read_inbox"]

    async def execute(
        self, action_type: str, params: Dict[str, Any], user_id: str
    ) -> Dict[str, Any]:
        if action_type == "gmail.send_email":
            self.validate_params(action_type, params, ["recipient", "subject", "body"])
            return await self._send_email(params, user_id)
        elif action_type == "gmail.read_inbox":
            return await self._read_inbox(params, user_id)
        raise ValueError(f"Unsupported action: {action_type}")

    async def _send_email(self, params: Dict, user_id: str) -> Dict:
        service = self._get_service(user_id)
        message = MIMEText(params["body"])
        message["to"] = params["recipient"]
        message["subject"] = params["subject"]

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return {"status": "email_sent", "to": params["recipient"]}

    async def _read_inbox(self, params: Dict, user_id: str) -> Dict:
        service = self._get_service(user_id)
        limit = params.get("limit", 10)
        query = params.get("query", "")

        results = (
            service.users()
            .messages()
            .list(userId="me", maxResults=limit, q=query)
            .execute()
        )
        messages = results.get("messages", [])

        emails = []
        for msg in messages[:limit]:
            detail = (
                service.users().messages().get(userId="me", id=msg["id"]).execute()
            )
            headers = {
                h["name"]: h["value"]
                for h in detail["payload"]["headers"]
                if h["name"] in ("From", "Subject", "Date")
            }
            emails.append(headers)

        return {"status": "inbox_read", "count": len(emails), "emails": emails}

    def _get_service(self, user_id: str):
        """Get authenticated Gmail service.
        In production, tokens are loaded from encrypted DB per user.
        This fallback uses token.json for local development.
        """
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists("client_secret.json"):
                    raise FileNotFoundError("Missing client_secret.json")
                flow = InstalledAppFlow.from_client_secrets_file(
                    "client_secret.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as f:
                f.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)
