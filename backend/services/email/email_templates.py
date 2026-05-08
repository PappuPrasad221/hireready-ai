def report_email_subject() -> str:
    return "Your HireReady AI Interview Report"


def report_email_body(candidate_name: str, recording_url: str = "") -> str:
    recording_section = ""
    if recording_url:
        recording_section = f"""
Your interview recording is available here:
{recording_url}
"""

    return f"""Hello {candidate_name},

Your AI interview report has been generated successfully.

Attached is your detailed interview performance report including:
- technical analysis
- communication feedback
- behavioral insights
- strengths & weaknesses
- AI improvement suggestions
{recording_section}

Regards,
HireReady AI Team
"""
