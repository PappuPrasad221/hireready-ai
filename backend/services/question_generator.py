from typing import Dict, Any, List
import re


class QuestionGenerator:
    """Generate structured, resume/job-aware interview rounds and follow-ups."""

    ROUND_CONFIG = [
        ("HR", "hr", 4),
        ("Resume-Based", "resume", 3),
        ("Project-Based", "project", 4),
        ("Technical", "technical", 4),
        ("Behavioral", "behavioral", 3),
    ]

    async def generate_interview_plan(
        self,
        resume_data: Dict[str, Any],
        job_insights: Dict[str, Any],
        role: str,
        company: str,
    ) -> List[Dict[str, Any]]:
        context = self._build_context(resume_data, job_insights, role, company)
        return [
            {"round": "HR", "questions": self._hr_questions(context)},
            {"round": "Resume-Based", "questions": self._resume_questions(context)},
            {"round": "Project-Based", "questions": self._project_questions(context)},
            {"round": "Technical", "questions": self._technical_questions(context)},
            {"round": "Behavioral", "questions": self._behavioral_questions(context)},
        ]

    async def generate_questions(
        self,
        resume_data: Dict[str, Any],
        job_insights: Dict[str, Any],
        role: str,
        company: str,
    ) -> List[Dict[str, Any]]:
        plan = await self.generate_interview_plan(resume_data, job_insights, role, company)
        return [question for round_plan in plan for question in round_plan["questions"]]

    async def generate_followup_question(
        self,
        question: Any,
        answer: str,
        evaluation: Dict[str, Any],
        previous_answers: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        question_data = question if isinstance(question, dict) else {"question": str(question), "round": "General"}
        answer = (answer or "").strip()
        scores = evaluation.get("scores", {}) if isinstance(evaluation, dict) else {}
        feedback = evaluation.get("feedback", {}) if isinstance(evaluation, dict) else {}
        score = self._as_number(scores.get("overall") or evaluation.get("overall_score") or 0)
        missing_points = self._normalize_items(feedback.get("missing_points", []))
        triggers = self._followup_triggers(question_data, answer, score, missing_points)

        if not triggers:
            return {"required": False, "followup_question": None, "reason": "answer_sufficient"}

        mentioned_topics = self._extract_topics(answer)
        topic = self._pick_first(mentioned_topics, self._normalize_items(question_data.get("expected_answer_points", [])), ["the key decision"])
        round_name = question_data.get("round", "Follow-Up")

        if score >= 80:
            prompt = f"What trade-offs, edge cases, or architecture constraints would you consider if you had to scale {topic} in a production {round_name.lower()} scenario?"
            difficulty = "hard"
            reason = "high_score_deeper_probe"
        elif score < 55:
            prompt = f"Can you explain the fundamentals of {topic} step by step and connect it directly to your previous answer?"
            difficulty = "easy"
            reason = "low_score_foundation_probe"
        elif mentioned_topics:
            prompt = f"You mentioned {topic}. Why did you choose it, what alternatives did you consider, and what measurable result did it create?"
            difficulty = "medium"
            reason = "mentioned_tool_or_project"
        elif missing_points:
            prompt = f"Your answer missed {missing_points[0]}. Can you expand on that with a concrete example, action, and result?"
            difficulty = "medium"
            reason = "missing_expected_point"
        else:
            prompt = "Can you add a specific example with the context, your exact action, and the final outcome?"
            difficulty = "medium"
            reason = "vague_or_short_answer"

        return {
            "required": True,
            "followup_question": self._question(
                round_name,
                f"{question_data.get('id', 'followup')}_fu",
                prompt,
                "adaptive_previous_answer",
                [
                    "Directly addresses the previous answer",
                    "Adds specific reasoning or technical depth",
                    "Provides concrete example, metric, or trade-off",
                ],
                triggers,
                difficulty=difficulty,
                is_followup=True,
            ),
            "reason": reason,
        }

    def _build_context(self, resume_data: Dict[str, Any], job_insights: Dict[str, Any], role: str, company: str) -> Dict[str, Any]:
        skills = self._normalize_skills(resume_data.get("skills", []))
        projects = self._normalize_items(resume_data.get("projects", []), ["title", "description", "technologies", "impact"])
        education = self._normalize_items(resume_data.get("education", []), ["degree", "institution", "year"])
        experience = self._normalize_items(resume_data.get("experience", []), ["role", "company", "duration", "description"])
        certifications = self._normalize_items(resume_data.get("certifications", []))
        achievements = self._normalize_items(resume_data.get("achievements", []))
        job_skills = self._normalize_skills(
            job_insights.get("skills")
            or job_insights.get("requiredSkills")
            or job_insights.get("preferredSkills")
            or []
        )
        responsibilities = self._normalize_items(job_insights.get("responsibilities", []))
        tools = self._normalize_items(job_insights.get("tools", []))
        topics = self._normalize_items(job_insights.get("interviewTopics", []))
        expectations = self._normalize_items(job_insights.get("companySpecificExpectations", []))

        return {
            "role": role or "this role",
            "company": company or "the company",
            "skills": skills,
            "projects": projects,
            "education": education,
            "experience": experience,
            "certifications": certifications,
            "achievements": achievements,
            "job_skills": job_skills,
            "responsibilities": responsibilities,
            "tools": tools,
            "topics": topics,
            "expectations": expectations,
        }

    def _hr_questions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        role = context["role"]
        company = context["company"]
        expectation = self._pick_first(context["expectations"], ["ownership and communication"])
        responsibility = self._pick_first(context["responsibilities"], [f"working as a {role}"])
        return [
            self._question("HR", "hr_1", f"Give me a concise introduction and connect your background to the {role} role at {company}.", "role/company/resume", ["Brief introduction", f"Relevant fit for {role}", "Clear career direction"], ["too_short", "vague_motivation"]),
            self._question("HR", "hr_2", f"Why are you interested in {company}, and what part of this {role} opportunity is most aligned with your goals?", "company/job_insight", [f"Specific interest in {company}", "Role motivation", "Evidence of company research"], ["generic_company_answer", "too_short"]),
            self._question("HR", "hr_3", f"What strengths from your resume make you ready for {responsibility}?", "resume/job_insight", ["Relevant strength", "Concrete evidence", "Connection to responsibility"], ["missing_evidence", "vague_strength"]),
            self._question("HR", "hr_4", f"How do you show {expectation} in a professional team environment?", "company_expectation", ["Professional behavior", "Example from past work", "Outcome or learning"], ["no_example", "low_confidence"]),
        ]

    def _resume_questions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        skill_a = self._pick_first(context["skills"], context["job_skills"], ["your strongest technical skill"])
        skill_b = self._pick_first(context["skills"][1:], context["job_skills"], ["another relevant skill"])
        education = self._pick_first(context["education"], ["your education"])
        achievement = self._pick_first(context["achievements"], context["certifications"], ["an achievement or certification"])
        return [
            self._question("Resume-Based", "resume_1", f"Your resume mentions {skill_a}. Where did you use it most meaningfully, and what was the outcome?", "resume_skill", [f"Specific use of {skill_a}", "Candidate ownership", "Outcome or measurable result"], ["mentions_tool", "missing_outcome"]),
            self._question("Resume-Based", "resume_2", f"How does {education} support your readiness for this role?", "resume_education", ["Relevant coursework or foundation", "Connection to role", "Practical application"], ["vague_education_link"]),
            self._question("Resume-Based", "resume_3", f"Tell me about {achievement}. Why is it relevant for a {context['role']} interview?", "resume_achievement", ["Context of achievement", "Skill demonstrated", "Relevance to role"], ["missing_relevance", "too_short"]),
            self._question("Resume-Based", "resume_4", f"Compare your comfort level with {skill_a} and {skill_b}. Where do you still need to improve?", "resume_skill_depth", ["Honest skill comparison", "Example for each skill", "Specific improvement plan"], ["low_confidence", "missing_examples"]),
        ][:3 if not achievement or achievement == "an achievement or certification" else 4]

    def _project_questions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        projects = context["projects"] or ["your strongest project"]
        project_a = self._pick_first(projects, ["your strongest project"])
        project_b = self._pick_first(projects[1:], [project_a])
        skill = self._pick_first(context["skills"], context["job_skills"], ["the main technology"])
        tool = self._pick_first(context["tools"], context["job_skills"], [skill])
        return [
            self._question("Project-Based", "project_1", f"Walk me through {project_a}. What problem did it solve, and what was your exact contribution?", "resume_project", ["Problem statement", "Candidate contribution", "Impact or result"], ["mentions_project", "missing_impact"]),
            self._question("Project-Based", "project_2", f"Which technologies did you use in {project_a}, and why were they the right choices?", "resume_project/skills", ["Technology choices", "Reasoning and alternatives", "Trade-offs"], ["mentions_tool", "missing_tradeoff"]),
            self._question("Project-Based", "project_3", f"What was the hardest challenge in {project_b}, and how did you debug or resolve it?", "resume_project", ["Challenge", "Debugging approach", "Resolution and learning"], ["vague_challenge", "missing_resolution"]),
            self._question("Project-Based", "project_4", f"If you rebuilt that project for a production use case involving {tool}, what would you change?", "resume_project/job_tool", ["Production improvement", f"Use of {tool}", "Scalability, security, or reliability"], ["high_score_deeper_probe", "technical_incomplete"]),
        ]

    def _technical_questions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        role = context["role"]
        skill = self._pick_first(context["job_skills"], context["skills"], ["core role skill"])
        tool = self._pick_first(context["tools"], context["job_skills"], [skill])
        topic = self._pick_first(context["topics"], context["job_skills"], [skill])
        responsibility = self._pick_first(context["responsibilities"], [f"building reliable solutions as a {role}"])
        return [
            self._question("Technical", "technical_1", f"Explain the core concepts behind {skill} and how you would apply them in this {role} role.", "job_required_skill", [f"Correct fundamentals of {skill}", "Role-specific application", "Limitations or trade-offs"], ["technical_incomplete", "mentions_tool"]),
            self._question("Technical", "technical_2", f"Design a practical solution for {responsibility}. What components, data flow, and failure handling would you include?", "job_responsibility", ["Architecture/components", "Data flow", "Failure handling and testing"], ["high_score_deeper_probe", "missing_architecture"]),
            self._question("Technical", "technical_3", f"How would you use {tool} in a production project, and what risks would you monitor?", "job_tool", [f"Correct use of {tool}", "Risks and monitoring", "Security or reliability considerations"], ["mentions_tool", "missing_risks"]),
            self._question("Technical", "technical_4", f"What interview topics around {topic} should a strong {role} candidate be ready to explain deeply?", "job_interview_topic", ["Topic breakdown", "Depth of explanation", "Practical example"], ["too_generic", "technical_incomplete"]),
        ]

    def _behavioral_questions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        role = context["role"]
        topic = self._pick_first(context["topics"], context["skills"], ["a technical concept"])
        return [
            self._question("Behavioral", "behavioral_1", f"Tell me about a time you worked with a team to solve a difficult problem related to {topic}.", "behavioral/resume", ["Situation", "Team role", "Action", "Result"], ["missing_star_structure", "too_short"]),
            self._question("Behavioral", "behavioral_2", f"Describe a conflict or disagreement during a project. How did you handle it?", "behavioral_project", ["Conflict context", "Communication approach", "Resolution", "Learning"], ["vague_conflict", "missing_resolution"]),
            self._question("Behavioral", "behavioral_3", f"When working under pressure as a {role}, how do you prioritize quality, speed, and communication?", "role_behavioral", ["Prioritization method", "Quality control", "Communication under pressure"], ["low_confidence", "missing_example"]),
        ]

    def _question(
        self,
        round_name: str,
        question_id: str,
        text: str,
        source: str,
        expected_points: List[str],
        followup_triggers: List[str],
        difficulty: str = "medium",
        is_followup: bool = False,
    ) -> Dict[str, Any]:
        return {
            "id": question_id,
            "round": round_name,
            "type": round_name.lower().replace("-", "_").replace(" ", "_"),
            "difficulty": difficulty,
            "question": text,
            "source": source,
            "expected_answer_points": expected_points,
            "expectedAnswerPoints": expected_points,
            "followUpTriggers": followup_triggers,
            "is_followup": is_followup,
        }

    def _followup_triggers(self, question_data: Dict[str, Any], answer: str, score: float, missing_points: List[str]) -> List[str]:
        words = re.findall(r"[A-Za-z0-9+#.]+", answer)
        triggers = []
        if len(words) < 35:
            triggers.append("too_short")
        if score < 65:
            triggers.append("low_score")
        if missing_points:
            triggers.append("missing_expected_points")
        if self._extract_topics(answer):
            triggers.append("mentioned_tool_or_project")
        if any(term in answer.lower() for term in ["maybe", "stuff", "things", "etc", "basically"]):
            triggers.append("vague_answer")
        if question_data.get("round") == "Technical" and score < 80:
            triggers.append("technical_incomplete")
        return triggers[:4]

    def _extract_topics(self, answer: str) -> List[str]:
        known = [
            "TensorFlow", "Firebase", "React", "FastAPI", "CNN", "MongoDB", "API", "Python",
            "JavaScript", "Firestore", "Azure", "Docker", "SQL", "Node", "Machine Learning",
        ]
        found = [topic for topic in known if re.search(rf"\b{re.escape(topic)}\b", answer, re.IGNORECASE)]
        capitalized = re.findall(r"\b[A-Z][A-Za-z0-9+#.]{2,}\b", answer or "")
        return self._unique(found + capitalized)[:4]

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
        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list):
            return []
        normalized = []
        for item in items:
            if isinstance(item, str):
                value = item.strip()
            elif isinstance(item, dict) and fields:
                parts = []
                for field in fields:
                    raw = item.get(field)
                    if isinstance(raw, list):
                        parts.extend(str(value).strip() for value in raw if value)
                    elif raw:
                        parts.append(str(raw).strip())
                value = " - ".join(parts)
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

    def _as_number(self, value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
