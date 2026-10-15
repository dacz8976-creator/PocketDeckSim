"""Verify the named four-source batch and optionally mirror retained evidence."""
import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
FULL = ["20261002_011527000_iOS.MP4", "20261002_012229000_iOS.MP4"]
PARTIAL = ["20260926_211809000_iOS.MP4", "20260926_212155000_iOS.MP4"]


def sha(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def reconcile():
    rows = list(csv.DictReader((ROOT / "BATTLE_REVIEW_INDEX.csv").open(encoding="utf-8-sig", newline="")))
    prior = {row["Video"]: row for row in read(BATCH / "INDEX_BEFORE.json")}
    current = {row["Video"]: row for row in rows}
    assert len(current) == len(rows)
    unrelated = {key: row for key, row in prior.items() if key not in FULL + PARTIAL}
    assert all(current[key] == row for key, row in unrelated.items()), "Unrelated review index rows changed"
    events = [read(path) for path in (ROOT / "Review_Log/events").glob("*.json")]
    location_map = read(ROOT / "MEDIA_LOCATIONS.json")
    entries = []
    for video in FULL + PARTIAL:
        packet = BATCH / Path(video).stem
        lead = read(packet / "LEAD_ACCEPTANCE.json")
        registration = read(packet / "REGISTRATION_RESULT.json")
        assert lead["accepted"] is True and registration["exit_code"] == 0
        latest = sorted((event for event in events if event.get("video_basename") == video), key=lambda event: (event.get("logged_at_utc", ""), event.get("event_id", "")))[-1]
        assert latest["video_sha256"].lower() == lead["source_sha256"].lower()
        full = video in FULL
        expected = "full_battle_review_complete" if full else "partial"
        assert latest["status"] == expected
        assert lead["battle_complete"] is full
        row = current[video]
        assert row["Status"] == ("Reviewed" if full else "Needs full battle review")
        assert row["Location"] == "Reviewed/" + video
        assert (ROOT / row["Location"]).is_file()
        assert not (ROOT / video).exists()
        move = read(packet / ("MOVE_RECEIPT." + video + ".json"))
        assert move["identity_match"] is True and move["sha256_before"] == move["sha256_after"] == lead["source_sha256"]
        mapped = [entry for entry in location_map["moved"] if entry["filename"] == video]
        assert len(mapped) == 1 and Path(mapped[0]["current_path"]) == ROOT / "Reviewed" / video
        assert mapped[0]["sha256"] == lead["source_sha256"]
        if not full:
            approval = read(BATCH / "OWNER_EXCERPT_ARCHIVE_APPROVAL.json")
            exception = read(packet / "LEAD_ARCHIVE_EXCEPTION.json")
            assert approval["approved"] is True and video in approval["source_basenames"]
            assert exception["approved"] is True and exception["source_sha256"] == lead["source_sha256"]
            assert move["battle_complete"] is False
            assert lead["archive_eligible"] is False
        entries.append({"video": video, "source_sha256": lead["source_sha256"], "battle_complete": full,
                        "available_footage_review_accepted": True, "latest_event_id": latest["event_id"],
                        "review_status": expected, "index_status": row["Status"], "location": row["Location"],
                        "source_archive_verified": True, "owner_excerpt_archive_exception": not full})
    result = {"checked_utc": datetime.now(timezone.utc).isoformat(), "requested_sources": 4,
              "all_available_footage_reviews_accepted": True, "full_battle_reviews_complete": 2,
              "recording_limited_excerpt_reviews": 2, "full_sources_archived_with_identity_match": 2,
              "approved_excerpt_sources_archived_with_identity_match": 2, "all_four_source_archives_verified": True,
              "all_requested_full_battles_complete": False, "unrelated_index_rows_unchanged": True,
              "external_results_saved": 0, "external_status": "Two prepared Ladder candidates; owner-approved retry reached browser inventory but state capture failed after bounded recovery; no live duplicate check/save",
              "storage_status": "Consult FINAL_STORAGE_CHECK.json; no metadata check reads archived video contents",
              "entries": entries}
    write(BATCH / "BATCH_COMPLETION_CHECK.json", result)
    print(json.dumps({key: value for key, value in result.items() if key != "entries"}))


def mirror():
    check = read(BATCH / "BATCH_COMPLETION_CHECK.json")
    assert check["all_available_footage_reviews_accepted"] is True
    boss = Path("C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder").resolve()
    destination = boss / BATCH.name
    assert destination.parent == boss and not destination.exists(), "Refusing destination collision"
    files = sorted(path for path in BATCH.rglob("*") if path.is_file() and "__pycache__" not in path.parts)
    assert not any(path.suffix.lower() in [".mp4", ".mov", ".mkv", ".avi", ".m4v"] for path in files)
    shutil.copytree(BATCH, destination, ignore=shutil.ignore_patterns("__pycache__"))
    copies = []
    for path in files:
        relative = path.relative_to(BATCH)
        digest = sha(path)
        assert sha(destination / relative) == digest
        copies.append({"path": relative.as_posix(), "bytes": path.stat().st_size, "sha256": digest})
    receipt = {"copied_utc": datetime.now(timezone.utc).isoformat(), "source": str(BATCH),
               "destination": str(destination), "file_count": len(files), "all_copy_hashes_match": True,
               "videos_copied": 0, "files": copies}
    receipt_path = BATCH / "MIRROR_RECEIPT.json"
    write(receipt_path, receipt)
    shutil.copy2(receipt_path, destination / receipt_path.name)
    assert sha(receipt_path) == sha(destination / receipt_path.name)
    print(json.dumps({"mirrored_files": len(files), "copy_hashes_match": True, "videos_copied": 0}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mirror", action="store_true")
    args = parser.parse_args()
    reconcile()
    if args.mirror:
        mirror()
