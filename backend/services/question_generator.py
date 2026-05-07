from typing import Dict, Any, List
from datetime import datetime


class QuestionGenerator:
    """Generate structured, resume/job-aware interview rounds."""

    ROUND_ORDER = [
        "HR",
        "Resume-Based",
        "Project-Based",
        "Technical",
        "Behavioral",
    ]

    async def generate_questions(
        self,
        resume_data: Dict[str, Any],
        job_insights: Dict[str, Any],
        role: str,
        company: str,
    ) -> List[Dict[str, Any]]:
        skills = self._normalize_skills(resume_data.get("skills", []))
        projects = self._normalize_items(resume_data.get("projects", []), ["title", "description"])
        experience = self._normalize_items(resume_data.get("experience", []), ["role", "company", "duration"])
        job_skills = self._normalize_skills(
            job_insights.get("skills")
            or job_insights.get("requiredSkills")
            or job_insights.get("preferredSkills")
            or []
        )
        responsibilities = self._normalize_items(job_insights.get("responsibilities", []))
        topics = self._normalize_items(job_insights.get("interviewTopics", []))
        expectations = self._normalize_items(job_insights.get("companySpecificExpectations", []))

        primary_skill = self._pick_first(job_skills, skills, ["problem solving"])
        primary_project = self._pick_first(projects, ["a project from your resume"])
        primary_experience = self._pick_first(experience, ["your recent experience"])
        primary_topic = self._pick_first(topics, job_skills, [primary_skill])
        primary_responsibility = self._pick_first(responsibilities, [f"working as a {role}"])
        company_expectation = self._pick_first(expectations, ["professionalism and ownership"])

        questions = [
            self._question(
                "HR",
                "Medium",
                f"Why are you interested in the {role} role at {company}, and how does it fit your career direction?",
                "company_role",
                [
                    f"Specific reason for choosing {company}",
                    f"Connection between background and {role}",
                    "Clear career motivation",
                    f"Awareness of company expectation: {company_expectation}",
                ],
            ),
            self._question(
                "Resume-Based",
                "Medium",
                f"Walk me through {primary_experience} and explain the impact you personally created.",
                "resume_experience",
                [
                    "Concrete responsibility owned by the candidate",
                    "Measurable or observable impact",
                    "Technical or collaboration decisions made",
                    "What was learned or improved",
                ],
            ),
            self._question(
                "Project-Based",
                "Hard",
                f"Pick {primary_project}. What was the hardest technical decision, and how would you improve it today?",
                "resume_project",
                [
                    "Clear project context and candidate role",
                    "Trade-off behind the technical decision",
                    "Outcome of the decision",
                    "Specific improvement with reasoning",
                ],
            ),
            self._question(
                "Technical",
                "Hard",
                f"How would you apply {primary_skill} to solve a production problem related to {primary_responsibility}?",
                "job_required_skill",
                [
                    f"Correct use of {primary_skill}",
                    "Production constraints such as scale, security, reliability, or monitoring",
                    "Step-by-step implementation approach",
                    "Testing and failure handling",
                ],
            ),
            self._question(
                "Behavioral",
                "Medium",
                f"Tell me about a time you had to learn or apply {primary_topic} under pressure. What did you do and what was the result?",
                "job_interview_topic",
                [
                    "Situation and pressure clearly explained",
                    "Candidate's specific actions",
                    "Result or measurable outcome",
                    "Reflection on what could be improved",
                ],
            ),
        ]

        return questions

    def _question(
        self,
        round_name: str,
        difficulty: str,
        text: str,
        source: str,
        expected_points: List[str],
    ) -> Dict[str, Any]:
        return {
            "id": f"{round_name.lower().replace(' ', '_')}_{datetime.now().strftime('%H%M%S%f')}",
            "round": round_name,
            "type": round_name.lower().replace("-", "_").replace(" ", "_"),
            "difficulty": difficulty,
            "question": text,
            "source": source,
            "expected_answer_points": expected_points,
        }

    def _normalize_skills(self, skills: Any) -> List[str]:
        if isinstance(skills, dict):
            normalized = []
            for value in skills.values():
                if isinstance(value, list):
                    normalized.extend(str(item).strip() for item in value if item)
            return self._unique(normalized)
        if isinstance(skills, list):
            return self._unique([str(item).strip() for item in skills if item])
        return []

    def _normalize_items(self, items: Any, fields: List[str] = None) -> List[str]:
        if not isinstance(items, list):
            return []
        normalized = []
        for item in items:
            if isinstance(item, str):
                value = item.strip()
            elif isinstance(item, dict) and fields:
                value = " - ".join(str(item.get(field, "")).strip() for field in fields if item.get(field))
            elif isinstance(item, dict):
                value = " - ".join(str(value).strip() for value in item.values() if value)
            else:
                value = str(item).strip()
            if value:
                normalized.append(value)
        return self._unique(normalized)

    def _pick_first(self, *groups: List[str]) -> str:
        for group in groups:
            if group:
                return group[0]
        return ""

    def _unique(self, values: List[str]) -> List[str]:
        seen = set()
        unique = []
        for value in values:
            key = value.lower()
            if key not in seen:
                seen.add(key)
                unique.append(value)
        return unique
