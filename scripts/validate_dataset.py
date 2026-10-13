import sys

from dataset_common import DATASET_DIR, REQUIRED_FIELDS, load_json


def main() -> int:
    errors = []
    total = 0
    for path in sorted(DATASET_DIR.glob("*_questions.json")):
        questions = load_json(path)
        ids = set()
        for index, item in enumerate(questions, start=1):
            total += 1
            for field in REQUIRED_FIELDS:
                if field not in item:
                    errors.append(f"{path.name}#{index} missing field {field}")
            if not str(item.get("question", "")).strip():
                errors.append(f"{path.name}#{index} has empty question")
            if item.get("id") in ids:
                errors.append(f"{path.name} duplicate id {item.get('id')}")
            ids.add(item.get("id"))
        print(f"[validate] {path.name}: questions={len(questions)} duplicate_ids={len(questions) - len(ids)}")
    if errors:
        print("[validate] failed")
        for error in errors[:50]:
            print(f"  - {error}")
        return 1
    print(f"[validate] passed total_questions={total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
