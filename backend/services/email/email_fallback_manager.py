from datetime import datetime
import os
from typing import Dict

import requests

from firebase_config import get_firestore_db
from services.email.brevo_service import BrevoEmailService
from services.email.email_templates import report_email_body, report_email_subject
from services.email.resend_service import ResendEmailService


class EmailFallbackManager:
    def __init__(self):
        self.brevo = BrevoEmailService()
        self.resend = ResendEmailService()

    def send_report_email(self, profile: Dict, pdf_info: Dict, report_id: str = "", recording_info: Dict | None = None) -> Dict:
        email = profile.get("email", "")
        candidate_name = profile.get("fullName", "Candidate")
        subject = report_email_subject()
        recording_url = (recording_info or {}).get("recordingUrl", "")
        body = report_email_body(candidate_name, recording_url)
        extra_attachments, recording_attachment_mode = self._build_recording_attachment(recording_info or {})

        try:
            result = self.brevo.send_report(email, candidate_name, subject, body, pdf_info["pdfPath"], pdf_info["filename"], extra_attachments)
            self._log(profile, "brevo", result["status"], "")
            return {
                "emailStatus": result["status"],
                "emailProvider": "brevo",
                "emailError": "",
                "emailMessageId": result.get("messageId", ""),
                "recordingAttachmentMode": recording_attachment_mode,
            }
        except Exception as brevo_error:
            try:
                result = self.resend.send_report(email, candidate_name, subject, body, pdf_info["pdfPath"], pdf_info["filename"], extra_attachments)
                self._log(profile, "resend", result["status"], str(brevo_error))
                return {
                    "emailStatus": result["status"],
                    "emailProvider": "resend",
                    "emailError": f"Brevo fallback reason: {brevo_error}",
                    "emailMessageId": result.get("messageId", ""),
                    "recordingAttachmentMode": recording_attachment_mode,
                }
            except Exception as resend_error:
                error = f"Brevo: {brevo_error} Resend: {resend_error}"
                self._log(profile, "none", "failed", error)
                return {"emailStatus": "failed", "emailProvider": "", "emailError": error, "emailMessageId": "", "recordingAttachmentMode": "not_available"}

    def _build_recording_attachment(self, recording_info: Dict) -> tuple[list, str]:
        if recording_info.get("recordingStatus") != "uploaded" or not recording_info.get("recordingUrl"):
            return [], "not_available"

        max_bytes = int(os.getenv("EMAIL_VIDEO_ATTACHMENT_MAX_BYTES", str(10 * 1024 * 1024)))
        recording_size = int(recording_info.get("recordingSize") or 0)
        if not recording_size or recording_size > max_bytes:
            return [], "link"

        try:
            recording_url = recording_info["recordingUrl"]
            if recording_url.startswith("/uploads/"):
                local_path = recording_url.lstrip("/").replace("/", os.sep)
                with open(local_path, "rb") as handle:
                    content = handle.read()
            else:
                response = requests.get(recording_url, timeout=30)
                response.raise_for_status()
                content = response.content

            if len(content) > max_bytes:
                return [], "link"
            return [{
                "filename": recording_info.get("recordingFileName") or "HireReady_Interview_Recording.webm",
                "content": content,
            }], "attached"
        except Exception as error:
            print(f"Recording attachment download skipped: {error}")
            return [], "link"

    def _log(self, profile: Dict, provider: str, status: str, error: str) -> None:
        db = get_firestore_db()
        if not db:
            return
        try:
            db.collection("emailLogs").add({
                "userId": profile.get("userId", ""),
                "email": profile.get("email", ""),
                "provider": provider,
                "status": status,
                "sentAt": datetime.now().isoformat(),
                "error": error,
            })
        except Exception as firestore_error:
            print(f"Firestore email log skipped: {firestore_error}")
