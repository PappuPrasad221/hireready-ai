def report_email_subject() -> str:
    return "Your HireReady AI Interview Report"


def report_email_body(candidate_name: str) -> str:
    return f"""Hello {candidate_name},

Your AI interview report has been generated successfully.

Attached is your detailed interview performance report including:
- technical analysis
- communication feedback
- behavioral insights
- strengths & weaknesses
- AI improvement suggestions

Regards,
HireReady AI Team
"""
