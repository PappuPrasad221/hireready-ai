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
    normalize_key,
    question_similarity,
    validate_question,
)


TARGET_COUNTS = {
    "HR": 50,
    "Technical": 100,
    "Aptitude": 80,
    "Behavioral": 50,
    "Company": 50,
}


def main() -> int:
    errors = []
    summary = {}
    for round_name, filename in ROUND_FILE_MAP.items():
        questions = loadQuestionsByDataset(filename)
        unique = deduplicateQuestions(questions)
        count = len(questions)
        summary[round_name] = count
        if count < TARGET_COUNTS[round_name]:
            errors.append(f"{round_name} has {count}, expected at least {TARGET_COUNTS[round_name]}")
        if len(unique) != count:
            errors.append(f"{round_name} has {count - len(unique)} duplicate or near-duplicate questions")

        ids = set()
        for index, question in enumerate(questions, start=1):
            for error in validate_question(question):
                errors.append(f"{filename}#{index}: {error}")
            if question["id"] in ids:
                errors.append(f"{filename}: duplicate id {question['id']}")
            ids.add(question["id"])
            if question.get("source") == "AI-generated from curated dataset pattern":
                text = normalize_key(question.get("question"))
                if len(text.split()) < 6:
                    errors.append(f"{filename}#{index}: generated question is too short")

        for left_index, left in enumerate(questions):
            for right in questions[left_index + 1:]:
                if question_similarity(left.get("question", ""), right.get("question", "")) >= 0.94:
                    errors.append(f"{filename}: near duplicate detected between {left.get('id')} and {right.get('id')}")
                    break

        print(f"[validate-generated] {round_name}: count={count} unique={len(unique)}")

    print("[validate-generated] summary")
    print(json.dumps(summary, indent=2))

    if errors:
        print("[validate-generated] failed")
        for error in errors[:80]:
            print(f"  - {error}")
        return 1
    print("[validate-generated] passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
