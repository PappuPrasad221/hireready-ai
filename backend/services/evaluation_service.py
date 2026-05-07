from typing import Dict, Any, List, Union
from datetime import datetime
import re
import statistics


class EvaluationService:
    """Strict, rubric-based answer and report evaluation."""

    async def evaluate_answer(
        self,
        question: Union[str, Dict[str, Any]],
        answer: str,
        question_type: str,
        behavior_data: Dict[str, Any],
        resume_context: Dict[str, Any] = None,
        job_insights: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        question_data = self._normalize_question(question, question_type)
        expected_points = question_data.get("expected_answer_points", [])
        answer = (answer or "").strip()

        text_scores = self._score_text_answer(answer, expected_points, question_data)
        behavior_scores = self._score_behavior(behavior_data or {})
        scores = self._combine_scores(text_scores, behavior_scores)
        feedback = self._build_feedback(answer, question_data, expected_points, text_scores, scores)

        return {
            "question": question_data,
            "answer": answer,
            "evaluated_at": datetime.now().isoformat(),
            "scores": scores,
            "feedback": feedback,
            "overall_score": scores["overall"],
        }

    def _normalize_question(self, question: Union[str, Dict[str, Any]], question_type: str) -> Dict[str, Any]:
        if isinstance(question, dict):
            return {
                "question": question.get("question") or question.get("text") or "",
                "round": question.get("round", question_type.title()),
                "type": question.get("type", question_type),
                "difficulty": question.get("difficulty", "Medium"),
                "source": question.get("source", "unknown"),
                "expected_answer_points": question.get("expected_answer_points", []),
            }
        return {
            "question": str(question),
            "round": question_type.title(),
            "type": question_type,
            "difficulty": "Medium",
            "source": "legacy",
            "expected_answer_points": [],
        }

    def _score_text_answer(self, answer: str, expected_points: List[str], question_data: Dict[str, Any]) -> Dict[str, Any]:
        words = re.findall(r"[A-Za-z0-9+#.]+", answer.lower())
        word_count = len(words)
        unique_words = len(set(words))

        if word_count == 0:
            length_score = 0
        elif word_count < 15:
            length_score = 25
        elif word_count < 35:
            length_score = 55
        elif word_count <= 180:
            length_score = 85
        else:
            length_score = 70

        question_words = set(re.findall(r"[A-Za-z0-9+#.]+", question_data.get("question", "").lower()))
        relevance = len(question_words & set(words)) / max(len(question_words), 1)
        relevance_score = min(100, relevance * 220)

        covered_points = []
        missing_points = []
        answer_set = set(words)
        for point in expected_points:
            point_terms = [
                term for term in re.findall(r"[A-Za-z0-9+#.]+", point.lower())
                if len(term) > 3
            ]
            if not point_terms:
                missing_points.append(point)
                continue
            overlap = len(set(point_terms) & answer_set) / len(set(point_terms))
            if overlap >= 0.25:
                covered_points.append(point)
            else:
                missing_points.append(point)

        completeness_score = 50 if not expected_points else (len(covered_points) / len(expected_points)) * 100

        structure_markers = ["first", "then", "because", "result", "impact", "for example", "finally", "therefore"]
        structure_score = min(100, 35 + sum(12 for marker in structure_markers if marker in answer.lower()))

        vague_terms = ["stuff", "things", "etc", "basically", "kind of", "maybe"]
        vague_penalty = min(30, sum(8 for term in vague_terms if term in answer.lower()))
        specificity_score = min(100, unique_words * 2.2 + self._count_numbers(answer) * 8) - vague_penalty
        specificity_score = max(0, specificity_score)

        technical_score = (completeness_score * 0.55) + (specificity_score * 0.25) + (relevance_score * 0.20)

        if word_count < 12:
            technical_score = min(technical_score, 35)
            completeness_score = min(completeness_score, 35)
            relevance_score = min(relevance_score, 45)

        return {
            "word_count": word_count,
            "relevance": round(relevance_score, 2),
            "technical_accuracy": round(technical_score, 2),
            "clarity": round((structure_score * 0.55) + (length_score * 0.45), 2),
            "completeness": round(completeness_score, 2),
            "structure": round(structure_score, 2),
            "covered_points": covered_points,
            "missing_points": missing_points,
        }

    def _score_behavior(self, behavior_data: Dict[str, Any]) -> Dict[str, float]:
        eye_contact = float(behavior_data.get("eye_contact", behavior_data.get("eyeContact", 0)) or 0)
        attention = float(behavior_data.get("attention", 0) or 0)
        distraction_count = float(behavior_data.get("distraction_count", behavior_data.get("distractionCount", 0)) or 0)
        face_detected = behavior_data.get("face_detected", behavior_data.get("faceDetected", True))

        behavior_score = (eye_contact * 0.35) + (attention * 0.45) + 20
        behavior_score -= min(35, distraction_count * 5)
        if face_detected is False:
            behavior_score -= 25

        confidence = behavior_data.get("confidence_indicators", {})
        voice_score = (
            float(confidence.get("clear_voice", 0.6)) * 40
            + float(confidence.get("steady_pace", 0.6)) * 30
            + float(confidence.get("minimal_fillers", 0.6)) * 30
        )

        return {
            "eye_contact": max(0, min(100, eye_contact)),
            "attention": max(0, min(100, attention)),
            "behavior": max(0, min(100, behavior_score)),
            "confidence": max(0, min(100, voice_score)),
        }

    def _combine_scores(self, text_scores: Dict[str, Any], behavior_scores: Dict[str, float]) -> Dict[str, float]:
        technical = text_scores["technical_accuracy"]
        communication = (text_scores["clarity"] * 0.65) + (text_scores["structure"] * 0.35)
        completeness = text_scores["completeness"]
        confidence = behavior_scores["confidence"]
        behavior = behavior_scores["behavior"]

        overall = (
            technical * 0.34
            + communication * 0.22
            + completeness * 0.20
            + confidence * 0.10
            + behavior * 0.14
        )

        return {
            "technical": round(technical, 2),
            "communication": round(communication, 2),
            "completeness": round(completeness, 2),
            "confidence": round(confidence, 2),
            "behavior": round(behavior, 2),
            "behavioral": round(behavior, 2),
            "problem_solving": round((technical + completeness) / 2, 2),
            "overall": round(max(0, min(100, overall)), 2),
        }

    def _build_feedback(
        self,
        answer: str,
        question_data: Dict[str, Any],
        expected_points: List[str],
        text_scores: Dict[str, Any],
        scores: Dict[str, float],
    ) -> Dict[str, Any]:
        strengths = []
        weaknesses = []

        if scores["technical"] >= 75:
            strengths.append("Answer addressed the technical intent of the question.")
        if scores["communication"] >= 75:
            strengths.append("Response was reasonably clear and structured.")
        if text_scores["covered_points"]:
            strengths.append(f"Covered {len(text_scores['covered_points'])} expected point(s).")

        if scores["overall"] < 60:
            weaknesses.append("Answer was too vague or incomplete for a strong interview response.")
        if text_scores["missing_points"]:
            weaknesses.append("Several expected answer points were missing.")
        if text_scores["word_count"] < 25:
            weaknesses.append("Answer was too short; add context, actions, and results.")

        improved_answer = self._improved_answer_template(question_data, expected_points)

        return {
            "strengths": strengths or ["You attempted the question and provided a usable response."],
            "weaknesses": weaknesses,
            "missing_points": text_scores["missing_points"],
            "covered_points": text_scores["covered_points"],
            "detailed_feedback": self._detailed_feedback(scores),
            "suggested_answer": improved_answer,
            "deep_explanation": {
                "what_user_answered": answer,
                "what_was_missing": text_scores["missing_points"],
                "what_interviewer_expected": expected_points,
                "ideal_answer_structure": [
                    "Brief context",
                    "Specific action or technical approach",
                    "Trade-offs or reasoning",
                    "Result, metric, or learning",
                ],
                "improved_answer": improved_answer,
            },
        }

    def _detailed_feedback(self, scores: Dict[str, float]) -> str:
        if scores["overall"] >= 80:
            return "Strong response with relevant substance. Add sharper metrics to make it excellent."
        if scores["overall"] >= 60:
            return "Decent response, but it needs more precise examples, expected points, and outcome detail."
        return "Weak response. Interviewers would need more concrete evidence, structure, and role-specific detail."

    def _improved_answer_template(self, question_data: Dict[str, Any], expected_points: List[str]) -> str:
        points = expected_points[:3] or ["the context", "your specific action", "the measurable result"]
        return (
            f"For this {question_data.get('round', 'interview')} question, structure the answer as: "
            f"brief context, then explain {points[0]}, connect it to {points[1] if len(points) > 1 else 'your role'}, "
            f"and close with {points[2] if len(points) > 2 else 'the result or learning'}."
        )

    async def generate_final_report(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        if hasattr(session_data, "model_dump"):
            session_data = session_data.model_dump()
        elif hasattr(session_data, "dict"):
            session_data = session_data.dict()

        answers = session_data.get("answers", [])
        scored_answers = [answer for answer in answers if answer.get("scores")]
        all_scores = [answer["scores"] for answer in scored_answers]

        report = {
            "session_id": session_data.get("session_id"),
            "company": session_data.get("company"),
            "role": session_data.get("role"),
            "overall_score": 0,
            "category_scores": {
                "technical": 0,
                "communication": 0,
                "confidence": 0,
                "behavior": 0,
                "completeness": 0,
            },
            "round_wise_scores": {},
            "strongest_answer": None,
            "weakest_answer": None,
            "missing_skills": [],
            "strengths": [],
            "improvements": [],
            "recommendations": [],
            "replay_timeline": [],
            "generated_at": datetime.now().isoformat(),
        }

        if not all_scores:
            report["recommendations"] = ["Complete at least one evaluated answer to generate a full report."]
            return report

        for category in report["category_scores"]:
            report["category_scores"][category] = round(statistics.mean(score.get(category, 0) for score in all_scores), 2)
        report["overall_score"] = round(statistics.mean(score.get("overall", 0) for score in all_scores), 2)

        by_round = {}
        for answer in scored_answers:
            question = answer.get("question", {})
            if isinstance(question, str):
                round_name = "General"
            else:
                round_name = question.get("round", "General")
            by_round.setdefault(round_name, []).append(answer["scores"].get("overall", 0))
        report["round_wise_scores"] = {
            round_name: round(statistics.mean(scores), 2)
            for round_name, scores in by_round.items()
        }

        strongest = max(scored_answers, key=lambda item: item["scores"].get("overall", 0))
        weakest = min(scored_answers, key=lambda item: item["scores"].get("overall", 0))
        report["strongest_answer"] = self._answer_summary(strongest)
        report["weakest_answer"] = self._answer_summary(weakest)

        missing_points = []
        for answer in scored_answers:
            missing_points.extend(answer.get("feedback", {}).get("missing_points", []))
            report["replay_timeline"].append({
                "question": answer.get("question"),
                "answer": answer.get("answer"),
                "score": answer.get("scores", {}).get("overall", 0),
                "feedback": answer.get("feedback", {}),
            })

        report["missing_skills"] = self._derive_missing_skills(missing_points)
        report["strengths"] = self._derive_strengths(report["category_scores"])
        report["improvements"] = self._derive_improvements(report["category_scores"], missing_points)
        report["recommendations"] = report["improvements"][:5]
        return report

    def _answer_summary(self, answer: Dict[str, Any]) -> Dict[str, Any]:
        question = answer.get("question", {})
        return {
            "question": question.get("question") if isinstance(question, dict) else question,
            "answer": answer.get("answer", ""),
            "score": answer.get("scores", {}).get("overall", 0),
            "feedback": answer.get("feedback", {}).get("detailed_feedback", ""),
        }

    def _derive_missing_skills(self, missing_points: List[str]) -> List[str]:
        candidates = []
        for point in missing_points:
            for token in re.findall(r"[A-Za-z][A-Za-z+#.]{2,}", point):
                if token.lower() not in {"specific", "clear", "result", "testing", "failure", "candidate"}:
                    candidates.append(token)
        return list(dict.fromkeys(candidates))[:8]

    def _derive_strengths(self, scores: Dict[str, float]) -> List[str]:
        labels = {
            "technical": "Technical reasoning",
            "communication": "Communication clarity",
            "confidence": "Voice confidence",
            "behavior": "Interview presence",
            "completeness": "Answer completeness",
        }
        return [label for key, label in labels.items() if scores.get(key, 0) >= 75] or ["Completed the interview flow"]

    def _derive_improvements(self, scores: Dict[str, float], missing_points: List[str]) -> List[str]:
        improvements = []
        if scores.get("technical", 0) < 70:
            improvements.append("Add more role-specific technical detail and trade-offs.")
        if scores.get("communication", 0) < 70:
            improvements.append("Use a tighter structure: context, action, result.")
        if scores.get("behavior", 0) < 70:
            improvements.append("Improve camera focus, eye contact, and reduce distractions.")
        if scores.get("confidence", 0) < 70:
            improvements.append("Practice speaking at a steady pace with fewer fillers.")
        if missing_points:
            improvements.append("Cover the expected answer points before adding extra details.")
        return improvements or ["Maintain current performance and add stronger metrics."]

    def _count_numbers(self, text: str) -> int:
        return len(re.findall(r"\b\d+[%x]?\b", text))
