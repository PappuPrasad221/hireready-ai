import base64
import json
import os
from typing import Dict

import requests


class ResendEmailService:
    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY", "")
        self.from_email = os.getenv("RESEND_FROM_EMAIL") or "onboarding@resend.dev"
        self.from_name = os.getenv("RESEND_FROM_NAME") or os.getenv("FROM_NAME", "HireReady AI")

    def send_report(self, to_email: str, candidate_name: str, subject: str, body: str, pdf_path: str, filename: str) -> Dict[str, str]:
        if not self.api_key:
            raise RuntimeError("RESEND_API_KEY is not configured")

        with open(pdf_path, "rb") as handle:
            attachment = base64.b64encode(handle.read()).decode("utf-8")

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "text": body,
                "attachments": [{"filename": filename, "content": attachment}],
            },
            timeout=20,
        )
        if response.status_code >= 300:
            raise RuntimeError(self._format_error(response))
        payload = response.json() if response.content else {}
        return {
            "provider": "resend",
            "status": "sent_via_resend",
            "messageId": payload.get("id", ""),
        }

    def _format_error(self, response: requests.Response) -> str:
        message = response.text[:300]
        try:
            payload = response.json()
            message = payload.get("message") or payload.get("name") or message
        except json.JSONDecodeError:
            pass

        if response.status_code == 403 and "domain is not verified" in message.lower():
            return (
                "Resend rejected the sender domain. Verify the domain in Resend, "
                "or set RESEND_FROM_EMAIL to a verified sender address."
            )
        if response.status_code in (401, 403):
            return "Resend authentication or sender verification failed. Check RESEND_API_KEY and RESEND_FROM_EMAIL."
        return f"Resend failed with HTTP {response.status_code}: {message}"
