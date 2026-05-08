import os
import re
from datetime import datetime
from typing import Any, Dict, List


class PDFReportService:
    """Generate local PDF reports for interview results."""

    def __init__(self):
        self.output_dir = os.path.join("uploads", "reports")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, report_data: Dict[str, Any], candidate_profile: Dict[str, Any]) -> Dict[str, str]:
        candidate_name = candidate_profile.get("fullName") or report_data.get("candidate_name") or "Candidate"
        filename = f"HireReady_Report_{self._safe_filename(candidate_name)}.pdf"
        file_path = os.path.join(self.output_dir, filename)
        sections = self._build_lines(report_data, candidate_profile)

        try:
            self._generate_with_reportlab(file_path, sections)
        except Exception as error:
            print(f"ReportLab PDF generation failed, using fallback PDF writer: {error}")
            self._generate_basic_pdf(file_path, sections)

        return {
            "pdfPath": file_path,
            "pdfUrl": f"/uploads/reports/{filename}",
            "filename": filename,
        }

    def _build_lines(self, report: Dict[str, Any], profile: Dict[str, Any]) -> List[str]:
        category_scores = report.get("category_scores", {})
        lines = [
            "HireReady AI Interview Report",
            f"Candidate Name: {profile.get('fullName', 'Candidate')}",
            f"Email: {profile.get('email', '')}",
            f"Interview Date: {report.get('generated_at') or datetime.now().isoformat()}",
            f"Company: {report.get('company', 'Not captured')}",
            f"Role: {report.get('role', profile.get('targetRole', 'Not captured'))}",
            "",
            f"Overall Score: {report.get('overall_score', 0)}",
            f"Technical Score: {category_scores.get('technical', 0)}",
            f"Communication Score: {category_scores.get('communication', 0)}",
            f"Confidence Score: {category_scores.get('confidence', 0)}",
            f"Behavior Score: {category_scores.get('behavior', category_scores.get('behavioral', 0))}",
            "",
            "Strengths:",
            *self._list_lines(report.get("strengths", [])),
            "",
            "Weaknesses / Improvements:",
            *self._list_lines(report.get("improvements", report.get("recommendations", []))),
            "",
            "AI Suggestions:",
            *self._list_lines(report.get("recommendations", [])),
            "",
            "Question-wise Feedback:",
        ]

        for index, item in enumerate(report.get("replay_timeline", []), 1):
            question = item.get("question", "")
            question_text = question.get("question", "") if isinstance(question, dict) else str(question)
            feedback = item.get("feedback", {})
            lines.extend([
                f"Q{index}: {question_text}",
                f"Answer: {item.get('answer', '')}",
                f"Score: {item.get('score', 0)}",
                f"Feedback: {feedback.get('detailed_feedback', '')}",
                "",
            ])

        return lines

    def _generate_with_reportlab(self, file_path: str, lines: List[str]) -> None:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        pdf = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter
        y = height - 54
        pdf.setTitle("HireReady AI Interview Report")

        for index, line in enumerate(lines):
            if y < 54:
                pdf.showPage()
                y = height - 54
            if index == 0:
                pdf.setFont("Helvetica-Bold", 18)
            elif line.endswith(":"):
                pdf.setFont("Helvetica-Bold", 12)
            else:
                pdf.setFont("Helvetica", 10)
            for wrapped in self._wrap(line, 92):
                pdf.drawString(54, y, wrapped)
                y -= 15
            if not line:
                y -= 4
        pdf.save()

    def _generate_basic_pdf(self, file_path: str, lines: List[str]) -> None:
        escaped = []
        for line in lines:
            escaped.append(line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")[:115])
        stream_lines = ["BT", "/F1 10 Tf", "50 760 Td", "14 TL"]
        for line in escaped:
            stream_lines.append(f"({line}) Tj")
            stream_lines.append("T*")
        stream_lines.append("ET")
        stream = "\n".join(stream_lines)
        objects = [
            "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
            "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
            "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj",
            "4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
            f"5 0 obj << /Length {len(stream)} >> stream\n{stream}\nendstream endobj",
        ]
        pdf = "%PDF-1.4\n"
        offsets = []
        for obj in objects:
            offsets.append(len(pdf.encode("utf-8")))
            pdf += obj + "\n"
        xref = len(pdf.encode("utf-8"))
        pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n"
        for offset in offsets:
            pdf += f"{offset:010d} 00000 n \n"
        pdf += f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF"
        with open(file_path, "wb") as handle:
            handle.write(pdf.encode("utf-8"))

    def _list_lines(self, values: List[Any]) -> List[str]:
        if not values:
            return ["- Not captured"]
        return [f"- {str(value)}" for value in values[:8]]

    def _wrap(self, line: str, width: int) -> List[str]:
        if not line:
            return [""]
        return [line[i:i + width] for i in range(0, len(line), width)]

    def _safe_filename(self, value: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
        return cleaned or "Candidate"
