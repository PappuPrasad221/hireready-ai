import argparse
import sys
from pathlib import Path

from dataset_common import DATASET_DIR, load_json

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload structured question datasets to Firestore.")
    parser.add_argument("--dry-run", action="store_true", help="Print upload count without writing.")
    args = parser.parse_args()

    from firebase_config import get_firestore_db

    db = get_firestore_db()
    if not db:
        print("[firestore] skipped: Firestore is not configured")
        return 0

    total = 0
    for path in sorted(DATASET_DIR.glob("*_questions.json")):
        questions = load_json(path)
        print(f"[firestore] {path.name}: questions={len(questions)} dry_run={args.dry_run}")
        if args.dry_run:
            total += len(questions)
            continue
        for item in questions:
            doc_id = f"{path.stem}_{item['id']}"
            db.collection("questionBank").document(doc_id).set(item)
            total += 1
    print(f"[firestore] upload_result total={total} status={'dry_run' if args.dry_run else 'uploaded'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
