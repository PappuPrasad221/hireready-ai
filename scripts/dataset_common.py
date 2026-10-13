import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List

import pandas as pd
import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "datasets"
RAW_DIR = ROOT / "raw_data"
CLEAN_DIR = ROOT / "clean_data"

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

TOPIC_TAGS = {
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "react": "React",
    "api": "API",
    "dbms": "DBMS",
    "sql": "SQL",
    "oop": "OOP",
    "network": "Networking",
    "operating system": "OS",
    "machine learning": "Machine Learning",
    "firebase": "Firebase",
    "fastapi": "FastAPI",
    "leadership": "Leadership",
    "team": "Teamwork",
    "conflict": "Conflict",
    "aptitude": "Aptitude",
}


def ensure_dirs() -> None:
    for directory in (DATASET_DIR, RAW_DIR, CLEAN_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def normalize_text(value: Any) -> str:
    text = BeautifulSoup(str(value or ""), "html.parser").get_text(" ")
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -|•\t\r\n")


def question_key(question: Any) -> str:
    if isinstance(question, dict):
        question = question.get("question", "")
    text = normalize_text(question).lower()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def infer_tags(text: str, round_name: str, topic: str = "") -> List[str]:
    haystack = f"{text} {round_name} {topic}".lower()
    tags = [tag for keyword, tag in TOPIC_TAGS.items() if keyword in haystack]
    if round_name and round_name not in tags:
        tags.insert(0, round_name)
    return list(dict.fromkeys(tags))[:6]


def infer_difficulty(text: str, default: str = "medium") -> str:
    lowered = text.lower()
    if any(term in lowered for term in ["design", "architecture", "optimize", "scale", "trade-off", "complexity"]):
        return "hard"
    if any(term in lowered for term in ["define", "what is", "introduce", "basic", "why"]):
        return "easy"
    return default


def make_question(
    prefix: str,
    index: int,
    round_name: str,
    topic: str,
    question: str,
    answer_hint: str,
    expected_points: Iterable[str],
    company: str = "",
    difficulty: str = "",
    source: str = "IndiaBIX-style curated",
) -> Dict[str, Any]:
    clean_question = normalize_text(question)
    clean_topic = normalize_text(topic)
    clean_expected = [normalize_text(point) for point in expected_points if normalize_text(point)]
    return {
        "id": f"{prefix}_{index:03d}",
        "company": normalize_text(company),
        "round": round_name,
        "topic": clean_topic,
        "difficulty": difficulty or infer_difficulty(clean_question),
        "question": clean_question,
        "answerHint": normalize_text(answer_hint),
        "expectedAnswerPoints": clean_expected,
        "tags": infer_tags(clean_question, round_name, clean_topic),
        "source": source,
    }


def fetch_candidate_questions(urls: Iterable[str], round_name: str, topic: str) -> List[str]:
    if os.getenv("ALLOW_LIVE_EXTRACTION", "").lower() not in {"1", "true", "yes"}:
        print(f"[extract] live extraction disabled for {round_name}; using curated seed data")
        return []

    extracted: List[str] = []
    headers = {"User-Agent": "HireReadyAI-DatasetBuilder/1.0"}
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=12)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")
            for node in soup.select("h1,h2,h3,h4,p,li,td"):
                text = normalize_text(node.get_text(" "))
                if 18 <= len(text) <= 240 and text.endswith("?"):
                    extracted.append(text)
            print(f"[extract] fetched {len(extracted)} candidate questions from {url}")
        except Exception as error:
            print(f"[extract] fetch skipped for {url}: {error}")
    return list(dict.fromkeys(extracted))


def deduplicate_questions(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not questions:
        return []
    frame = pd.DataFrame(questions)
    frame["_key"] = frame["question"].map(question_key)
    frame = frame[frame["_key"].astype(bool)]
    frame = frame.drop_duplicates(subset=["_key"], keep="first")
    return frame.drop(columns=["_key"]).to_dict("records")


def clean_questions(questions: List[Dict[str, Any]], prefix: str = "q") -> List[Dict[str, Any]]:
    cleaned: List[Dict[str, Any]] = []
    for index, item in enumerate(questions, start=1):
        question = normalize_text(item.get("question", ""))
        if not question:
            continue
        round_name = normalize_text(item.get("round", "General")) or "General"
        topic = normalize_text(item.get("topic", round_name)) or round_name
        expected = item.get("expectedAnswerPoints") or []
        if isinstance(expected, str):
            expected = [expected]
        cleaned.append(
            {
                "id": normalize_text(item.get("id")) or f"{prefix}_{index:03d}",
                "company": normalize_text(item.get("company", "")),
                "round": round_name,
                "topic": topic,
                "difficulty": normalize_text(item.get("difficulty")) or infer_difficulty(question),
                "question": question,
                "answerHint": normalize_text(item.get("answerHint", "")),
                "expectedAnswerPoints": [normalize_text(point) for point in expected if normalize_text(point)],
                "tags": list(dict.fromkeys([normalize_text(tag) for tag in item.get("tags", []) if normalize_text(tag)]))
                or infer_tags(question, round_name, topic),
                "source": normalize_text(item.get("source", "IndiaBIX-style curated")) or "IndiaBIX-style curated",
            }
        )
    unique = deduplicate_questions(cleaned)
    for index, item in enumerate(unique, start=1):
        item["id"] = f"{prefix}_{index:03d}"
    return unique


def save_json(path: Path, data: Any) -> None:
    ensure_dirs()
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_dataset(name: str, questions: List[Dict[str, Any]]) -> None:
    ensure_dirs()
    raw_path = RAW_DIR / f"{name}_raw.json"
    dataset_path = DATASET_DIR / f"{name}_questions.json"
    save_json(raw_path, questions)
    cleaned = clean_questions(questions, name)
    duplicate_count = max(0, len(questions) - len(cleaned))
    save_json(dataset_path, cleaned)
    print(f"[extract] {name}: extracted={len(questions)} cleaned={len(cleaned)} duplicates_removed={duplicate_count}")
