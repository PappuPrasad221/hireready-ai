from pathlib import Path

from dataset_common import CLEAN_DIR, DATASET_DIR, clean_questions, load_json, save_json


def main() -> None:
    total_before = 0
    total_after = 0
    for path in sorted(DATASET_DIR.glob("*_questions.json")):
        questions = load_json(path)
        cleaned = clean_questions(questions, path.stem.replace("_questions", ""))
        total_before += len(questions)
        total_after += len(cleaned)
        save_json(path, cleaned)
        save_json(CLEAN_DIR / path.name, cleaned)
        print(f"[clean] {path.name}: before={len(questions)} after={len(cleaned)} duplicates_removed={len(questions) - len(cleaned)}")
    print(f"[clean] total_before={total_before} total_after={total_after} duplicates_removed={total_before - total_after}")


if __name__ == "__main__":
    main()
