import base64
import json
import os
from typing import Dict

import requests


class BrevoEmailService:
    def __init__(self):
        self.api_key = os.getenv("BREVO_API_KEY", "")
        self.from_email = os.getenv("BREVO_FROM_EMAIL") or os.getenv("FROM_EMAIL", "noreply@hireready.ai")
        self.from_name = os.getenv("BREVO_FROM_NAME") or os.getenv("FROM_NAME", "HireReady AI")

    def send_report(self, to_email: str, candidate_name: str, subject: str, body: str, pdf_path: str, filename: str) -> Dict[str, str]:
        if not self.api_key:
            raise RuntimeError("BREVO_API_KEY is not configured")

        with open(pdf_path, "rb") as handle:
            attachment = base64.b64encode(handle.read()).decode("utf-8")

        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "sender": {"name": self.from_name, "email": self.from_email},
                "to": [{"email": to_email, "name": candidate_name}],
                "subject": subject,
                "textContent": body,
                "attachment": [{"content": attachment, "name": filename}],
            },
            timeout=20,
        )
        if response.status_code >= 300:
            raise RuntimeError(self._format_error(response))
        payload = response.json() if response.content else {}
        return {
            "provider": "brevo",
            "status": "sent_via_brevo",
            "messageId": payload.get("messageId", ""),
        }

    def _format_error(self, response: requests.Response) -> str:
        message = response.text[:300]
        try:
            payload = response.json()
            message = payload.get("message") or payload.get("code") or message
        except json.JSONDecodeError:
            pass

        if response.status_code in (401, 403) and "unrecognised IP address" in message:
            return (
                "Brevo rejected this backend IP address. Add the current backend/server IP "
                "to Brevo authorized IPs, or disable Brevo IP restriction for this API key."
            )
        if response.status_code in (401, 403):
            return "Brevo authentication failed. Check BREVO_API_KEY and the sender configured in BREVO_FROM_EMAIL or FROM_EMAIL."
        return f"Brevo failed with HTTP {response.status_code}: {message}"
