import json
import math
import re
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List


DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"
ROUND_FILE_MAP = {
    "HR": "hr_questions.json",
    "Technical": "technical_questions.json",
    "Aptitude": "aptitude_questions.json",
    "Behavioral": "behavioral_questions.json",
    "Company": "company_questions.json",
}
ROUND_ALIASES = {
    "hr": "HR",
    "resume": "Resume-Based",
    "resume based": "Resume-Based",
    "resume-based": "Resume-Based",
    "project": "Project-Based",
    "project based": "Project-Based",
    "project-based": "Project-Based",
    "technical": "Technical",
    "behavioral": "Behavioral",
    "aptitude": "Aptitude",
    "company": "Company",
}
REQUIRED_FIELDS = [
    "id",
    "company",
    "round",
    "topic",
    "difficulty",
    "question",
    "answerHint",
    "expectedAnswerPoints",
    "tags",
    "source",
]


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", normalize_text(value).lower()).strip()


def canonical_round(round_name: str) -> str:
    return ROUND_ALIASES.get(normalize_key(round_name), normalize_text(round_name) or "General")


def _token_set(value: str) -> set:
    return set(normalize_key(value).split())


def question_similarity(left: str, right: str) -> float:
    left_tokens = _token_set(left)
    right_tokens = _token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    return intersection / union if union else 0.0


def clean_question_item(item: Dict[str, Any], round_name: str = "", index: int = 1, prefix: str = "q") -> Dict[str, Any]:
    expected = item.get("expectedAnswerPoints") or item.get("expected_answer_points") or []
    if isinstance(expected, str):
        expected = [expected]
    tags = item.get("tags") or []
    if isinstance(tags, str):
        tags = [tags]
    resolved_round = canonical_round(item.get("round") or round_name)
    topic = normalize_text(item.get("topic")) or resolved_round
    difficulty = normalize_key(item.get("difficulty"))
    if difficulty not in {"easy", "medium", "hard"}:
        difficulty = "medium"
    return {
        "id": normalize_text(item.get("id")) or f"{prefix}_{index:03d}",
        "company": normalize_text(item.get("company", "")),
        "round": resolved_round,
        "topic": topic,
        "difficulty": difficulty,
        "question": normalize_text(item.get("question", "")),
        "answerHint": normalize_text(item.get("answerHint", "")),
        "expectedAnswerPoints": [normalize_text(point) for point in expected if normalize_text(point)][:6],
        "tags": list(dict.fromkeys([normalize_text(tag) for tag in tags if normalize_text(tag)]))[:8],
        "source": normalize_text(item.get("source", "AI-generated from curated dataset pattern")),
    }


def deduplicateQuestions(questions: List[Dict[str, Any]], threshold: float = 0.94) -> List[Dict[str, Any]]:
    unique: List[Dict[str, Any]] = []
    for item in questions:
        question = normalize_text(item.get("question", ""))
        if not question:
            continue
        question_key = normalize_key(question)
        duplicate = False
        for existing in unique:
            existing_question = existing.get("question", "")
            if question_key == normalize_key(existing_question) or question_similarity(question, existing_question) >= threshold:
                duplicate = True
                break
        if not duplicate:
            unique.append(item)
    return unique


def validate_question(item: Dict[str, Any]) -> List[str]:
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in item:
            errors.append(f"missing {field}")
    if not normalize_text(item.get("question")):
        errors.append("empty question")
    if item.get("difficulty") not in {"easy", "medium", "hard"}:
        errors.append("invalid difficulty")
    if not isinstance(item.get("expectedAnswerPoints"), list):
        errors.append("expectedAnswerPoints must be a list")
    if not isinstance(item.get("tags"), list):
        errors.append("tags must be a list")
    return errors


@lru_cache(maxsize=1)
def loadQuestionBank() -> List[Dict[str, Any]]:
    questions: List[Dict[str, Any]] = []
    if not DATASET_DIR.exists():
        print(f"Question bank directory missing: {DATASET_DIR}")
        return questions

    for path in sorted(DATASET_DIR.glob("*_questions.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                cleaned = [clean_question_item(item, index=index, prefix=path.stem.replace("_questions", "")) for index, item in enumerate(data, start=1) if isinstance(item, dict)]
                questions.extend(cleaned)
                print(f"Question bank loaded {len(cleaned)} questions from {path.name}")
        except Exception as error:
            print(f"Question bank load skipped for {path.name}: {error}")
    return deduplicateQuestions(questions)


def clearQuestionBankCache() -> None:
    loadQuestionBank.cache_clear()


def loadQuestionsByDataset(dataset_name: str) -> List[Dict[str, Any]]:
    path = DATASET_DIR / dataset_name
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    prefix = path.stem.replace("_questions", "")
    return [clean_question_item(item, index=index, prefix=prefix) for index, item in enumerate(data, start=1) if isinstance(item, dict)]


def saveQuestionsByDataset(dataset_name: str, questions: List[Dict[str, Any]]) -> None:
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    prefix = dataset_name.replace("_questions.json", "")
    cleaned = [
        clean_question_item(item, round_name=item.get("round", ""), index=index, prefix=prefix)
        for index, item in enumerate(deduplicateQuestions(questions), start=1)
    ]
    for index, item in enumerate(cleaned, start=1):
        item["id"] = f"{prefix}_{index:03d}"
    (DATASET_DIR / dataset_name).write_text(json.dumps(cleaned, indent=2, ensure_ascii=False), encoding="utf-8")
    clearQuestionBankCache()


def getQuestionsByRound(round_name: str, limit: int = None) -> List[Dict[str, Any]]:
    resolved = canonical_round(round_name)
    matches = [question for question in loadQuestionBank() if canonical_round(question.get("round")) == resolved]
    return matches[:limit] if limit else matches


def getQuestionsByCompany(company: str, limit: int = None) -> List[Dict[str, Any]]:
    company_key = normalize_key(company)
    if not company_key:
        return []
    matches = [
        question
        for question in loadQuestionBank()
        if company_key in normalize_key(question.get("company")) or company_key in normalize_key(question.get("question"))
    ]
    return matches[:limit] if limit else matches


def getQuestionsByDifficulty(difficulty: str, limit: int = None) -> List[Dict[str, Any]]:
    difficulty_key = normalize_key(difficulty)
    matches = [question for question in loadQuestionBank() if normalize_key(question.get("difficulty")) == difficulty_key]
    return matches[:limit] if limit else matches


def getMatchingQuestions(
    round_name: str,
    company: str = "",
    role: str = "",
    skills: List[str] = None,
    topics: List[str] = None,
    limit: int = 4,
) -> List[Dict[str, Any]]:
    skills = skills or []
    topics = topics or []
    resolved_round = canonical_round(round_name)
    company_matches = getQuestionsByCompany(company)
    round_matches = getQuestionsByRound(resolved_round)
    candidate_pool = deduplicateQuestions(company_matches + round_matches)
    search_terms = [normalize_key(term) for term in [role, company, *skills, *topics] if normalize_key(term)]

    def score(question: Dict[str, Any]) -> int:
        haystack = normalize_key(
            " ".join([
                question.get("question", ""),
                question.get("topic", ""),
                " ".join(question.get("tags", [])),
                question.get("company", ""),
            ])
        )
        exact = sum(3 for term in search_terms if term and term in haystack)
        round_bonus = 2 if canonical_round(question.get("round")) == resolved_round else 0
        company_bonus = 2 if company and normalize_key(company) in normalize_key(question.get("company")) else 0
        return exact + round_bonus + company_bonus

    ranked = sorted(candidate_pool, key=score, reverse=True)
    return ranked[:limit]


def dataset_status() -> Dict[str, Any]:
    status = {}
    for round_name, filename in ROUND_FILE_MAP.items():
        questions = loadQuestionsByDataset(filename)
        status[round_name] = {
            "file": filename,
            "count": len(questions),
            "updatedAt": datetime.utcnow().isoformat(),
        }
    total = sum(item["count"] for item in status.values())
    return {"total": total, "rounds": status}
