import json
import os
import re
from typing import Any, Dict, List

from services.gemini_service import GeminiService
from services.question_bank_service import clean_question_item, deduplicateQuestions, normalize_key


class QuestionGenerationService:
    """Expand interview questions from dataset style using Gemini with a local fallback."""

    SOURCE = "AI-generated from curated dataset pattern"

    async def generate_questions_from_pattern(
        self,
        existing_questions: List[Dict[str, Any]],
        round_name: str,
        topic: str,
        role: str = "",
        company: str = "",
        resume_skills: List[str] = None,
        count: int = 5,
    ) -> List[Dict[str, Any]]:
        resume_skills = resume_skills or []
        if count <= 0:
            return []

        prompt = self._build_prompt(existing_questions, round_name, topic, role, company, resume_skills, count)
        generated: List[Dict[str, Any]] = []
        if os.getenv("USE_GEMINI_QUESTION_EXPANSION", "").lower() in {"1", "true", "yes"}:
            try:
                gemini = GeminiService()
                if gemini.model:
                    content = await gemini.generate_content_text(prompt)
                    generated = self._parse_questions(content)
                    print(f"AI question generation round={round_name} topic={topic} requested={count} received={len(generated)}")
            except Exception as error:
                print(f"AI question generation fallback round={round_name} topic={topic}: {error}")
        else:
            print(f"AI question generation disabled by default for bulk expansion; using pattern generator for {round_name}/{topic}")

        if len(generated) < count:
            generated.extend(
                self._fallback_questions(
                    existing_questions=existing_questions,
                    round_name=round_name,
                    topic=topic,
                    role=role,
                    company=company,
                    resume_skills=resume_skills,
                    count=count - len(generated),
                    offset=len(generated),
                )
            )

        cleaned = [
            clean_question_item(
                {
                    **item,
                    "round": item.get("round") or round_name,
                    "topic": item.get("topic") or topic,
                    "company": item.get("company") or company,
                    "source": self.SOURCE,
                },
                round_name=round_name,
                index=index,
                prefix=normalize_key(round_name).replace(" ", "_") or "generated",
            )
            for index, item in enumerate(generated, start=1)
        ]
        existing_and_generated = deduplicateQuestions(existing_questions + cleaned)
        existing_keys = {normalize_key(item.get("question")) for item in existing_questions}
        unique_generated = [item for item in existing_and_generated if normalize_key(item.get("question")) not in existing_keys]
        return unique_generated[:count]

    def _build_prompt(
        self,
        existing_questions: List[Dict[str, Any]],
        round_name: str,
        topic: str,
        role: str,
        company: str,
        resume_skills: List[str],
        count: int,
    ) -> str:
        examples = json.dumps(existing_questions[:12], indent=2, ensure_ascii=False)
        return f"""
You are an expert interview question designer.

You are given a small curated interview question dataset.

Your task:
Generate new original interview questions that follow the same style, difficulty, topic, and round.

Rules:
- Do not copy existing questions exactly.
- Generate original variations.
- Keep questions interview-focused.
- Match round type.
- Match difficulty.
- Add expectedAnswerPoints.
- Add answerHint.
- Add tags.
- Return only valid JSON.

Existing Questions:
{examples}

Round:
{round_name}

Topic:
{topic}

Role:
{role}

Company:
{company}

Resume Skills:
{", ".join(resume_skills)}

Generate {count} new questions.

Return:
{{
  "questions": [
    {{
      "id": "",
      "company": "",
      "round": "",
      "topic": "",
      "difficulty": "",
      "question": "",
      "answerHint": "",
      "expectedAnswerPoints": [],
      "tags": [],
      "source": "AI-generated from curated dataset pattern"
    }}
  ]
}}
""".strip()

    def _parse_questions(self, content: str) -> List[Dict[str, Any]]:
        if not content:
            return []
        match = re.search(r"\{.*\}", content, re.DOTALL)
        payload = match.group(0) if match else content
        parsed = json.loads(payload)
        questions = parsed.get("questions", []) if isinstance(parsed, dict) else []
        return [item for item in questions if isinstance(item, dict)]

    def _fallback_questions(
        self,
        existing_questions: List[Dict[str, Any]],
        round_name: str,
        topic: str,
        role: str,
        company: str,
        resume_skills: List[str],
        count: int,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        skill = resume_skills[0] if resume_skills else "the required skill"
        role_text = role or "this role"
        company_text = company or "the company"
        templates = {
            "HR": [
                "How would you explain your fit for {role} at {company} using one recent achievement?",
                "What motivates you to pursue {role}, and how does this opportunity match your long-term plan?",
                "Describe a professional habit that would help you succeed at {company}.",
                "Tell me about a time you accepted feedback and changed how you worked.",
            ],
            "Technical": [
                "How would you apply {skill} to solve a production problem in a {role} role?",
                "What trade-offs would you consider while designing a system that uses {skill}?",
                "Explain a failure scenario involving {skill} and how you would detect and recover from it.",
                "How would you test, monitor, and improve a feature built with {skill}?",
            ],
            "Aptitude": [
                "A project metric improves from 48 to 60. What is the percentage improvement?",
                "If 5 developers finish a module in 18 days, how many days would 9 developers take at the same rate?",
                "A candidate solves 70 percent of 40 problems. How many problems are unsolved?",
                "If three interview rounds have scores 65, 75, and 85, what is the average score?",
            ],
            "Behavioral": [
                "Tell me about a time you handled ambiguity while working on {topic}.",
                "Describe a situation where you helped a team recover from a setback.",
                "Give an example of how you balanced quality and speed under pressure.",
                "Tell me about a time you disagreed with a teammate and still delivered the outcome.",
            ],
            "Company": [
                "How would you adapt your working style to succeed in {company}'s interview and delivery environment?",
                "What part of {company}'s business or engineering culture connects with your strengths?",
                "How would you communicate technical risk to stakeholders at {company}?",
                "Why does your background make sense for {role} at {company}?",
            ],
        }
        selected = templates.get(round_name, templates["Technical"])
        angles = [
            "during a production deadline",
            "while collaborating with a cross-functional team",
            "when requirements are incomplete",
            "after receiving critical feedback",
            "while improving reliability",
            "when explaining the work to a non-technical stakeholder",
            "while balancing speed and quality",
            "when measuring impact with clear evidence",
            "while debugging an unexpected issue",
            "when choosing between two possible approaches",
        ]
        questions = []
        for index in range(count):
            base = selected[(index + offset) % len(selected)].format(
                role=role_text,
                company=company_text,
                skill=skill,
                topic=topic or "a project",
            )
            angle = angles[(index + offset) % len(angles)]
            text = f"{base} Frame your answer around {angle}, with specific focus on {topic or round_name}."
            questions.append(
                {
                    "id": "",
                    "company": company,
                    "round": round_name,
                    "topic": topic or round_name,
                    "difficulty": "medium",
                    "question": text,
                    "answerHint": "Answer with a structured explanation and a concrete example.",
                    "expectedAnswerPoints": ["Direct answer", "Relevant example", "Clear reasoning", "Outcome or trade-off"],
                    "tags": [round_name, topic or round_name, role_text],
                    "source": self.SOURCE,
                }
            )
        return questions
