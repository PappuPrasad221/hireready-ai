import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from services.question_bank_service import (  # noqa: E402
    ROUND_FILE_MAP,
    deduplicateQuestions,
    loadQuestionsByDataset,
    saveQuestionsByDataset,
)
from services.question_generation_service import QuestionGenerationService  # noqa: E402


TARGET_COUNTS = {
    "HR": 50,
    "Technical": 100,
    "Aptitude": 80,
    "Behavioral": 50,
    "Company": 50,
}

DEFAULT_CONTEXT = {
    "role": "Software Engineer",
    "company": "target company",
    "resume_skills": ["Python", "React", "FastAPI", "Firebase", "SQL", "API Integration"],
}


def _topics_from_questions(questions):
    topics = []
    for item in questions:
        topic = item.get("topic")
        if topic and topic not in topics:
            topics.append(topic)
    return topics or ["General"]


async def expand_round(round_name: str, filename: str, target_count: int) -> int:
    service = QuestionGenerationService()
    questions = deduplicateQuestions(loadQuestionsByDataset(filename))
    before = len(questions)
    topics = _topics_from_questions(questions)
    print(f"[expand] {round_name}: existing={before} target={target_count} topics={len(topics)}")

    topic_index = 0
    stalled_topics = 0
    while len(questions) < target_count:
        missing = target_count - len(questions)
        batch_size = min(10, missing)
        topic = topics[topic_index % len(topics)]
        examples = [item for item in questions if item.get("topic") == topic][:12] or questions[:12]
        generated = await service.generate_questions_from_pattern(
            existing_questions=questions,
            round_name=round_name,
            topic=topic,
            role=DEFAULT_CONTEXT["role"],
            company=DEFAULT_CONTEXT["company"],
            resume_skills=DEFAULT_CONTEXT["resume_skills"],
            count=batch_size,
        )
        if not generated:
            stalled_topics += 1
            print(f"[expand] {round_name}: no generated questions for topic={topic}; trying next topic")
            topic_index += 1
            if stalled_topics >= len(topics):
                print(f"[expand] {round_name}: all topics stalled; stopping early")
                break
            continue
        questions = deduplicateQuestions(questions + generated)
        print(f"[expand] {round_name}: topic={topic} added={len(generated)} total={len(questions)}")
        stalled_topics = 0
        topic_index += 1
        if topic_index > target_count * 2:
            print(f"[expand] {round_name}: safety stop reached")
            break

    saveQuestionsByDataset(filename, questions)
    final = len(loadQuestionsByDataset(filename))
    print(f"[expand] {round_name}: before={before} final={final} generated={final - before}")
    return final


async def main() -> int:
    results = {}
    for round_name, target_count in TARGET_COUNTS.items():
        filename = ROUND_FILE_MAP[round_name]
        results[round_name] = await expand_round(round_name, filename, target_count)

    clean_dir = ROOT / "clean_data"
    clean_dir.mkdir(exist_ok=True)
    for filename in ROUND_FILE_MAP.values():
        source = ROOT / "datasets" / filename
        target = clean_dir / filename
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    print("[expand] summary")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
