from datetime import datetime
from typing import Dict

from firebase_config import get_firestore_db
from services.email.brevo_service import BrevoEmailService
from services.email.email_templates import report_email_body, report_email_subject
from services.email.resend_service import ResendEmailService


class EmailFallbackManager:
    def __init__(self):
        self.brevo = BrevoEmailService()
        self.resend = ResendEmailService()

    def send_report_email(self, profile: Dict, pdf_info: Dict, report_id: str = "") -> Dict:
        email = profile.get("email", "")
        candidate_name = profile.get("fullName", "Candidate")
        subject = report_email_subject()
        body = report_email_body(candidate_name)

        try:
            result = self.brevo.send_report(email, candidate_name, subject, body, pdf_info["pdfPath"], pdf_info["filename"])
            self._log(profile, "brevo", result["status"], "")
            return {
                "emailStatus": result["status"],
                "emailProvider": "brevo",
                "emailError": "",
                "emailMessageId": result.get("messageId", ""),
            }
        except Exception as brevo_error:
            try:
                result = self.resend.send_report(email, candidate_name, subject, body, pdf_info["pdfPath"], pdf_info["filename"])
                self._log(profile, "resend", result["status"], str(brevo_error))
                return {
                    "emailStatus": result["status"],
                    "emailProvider": "resend",
                    "emailError": f"Brevo fallback reason: {brevo_error}",
                    "emailMessageId": result.get("messageId", ""),
                }
            except Exception as resend_error:
                error = f"Brevo: {brevo_error} Resend: {resend_error}"
                self._log(profile, "none", "failed", error)
                return {"emailStatus": "failed", "emailProvider": "", "emailError": error, "emailMessageId": ""}

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
