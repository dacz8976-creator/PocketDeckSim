"""Metadata-only OneDrive release for two full reviews and two approved excerpts."""
import argparse
import csv
import importlib.util
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
VIDEOS = ["20261002_011527000_iOS.MP4", "20261002_012229000_iOS.MP4", "20260926_211809000_iOS.MP4", "20260926_212155000_iOS.MP4"]
EXCERPTS = VIDEOS[2:]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--wait-seconds", type=float, default=0)
    args = parser.parse_args()
    assert 0 <= args.wait_seconds <= 45
    spec = importlib.util.spec_from_file_location("existing_cloud_metadata", ROOT / "Recording_QA/free_reviewed_video_space.py")
    metadata_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(metadata_module)
    archive = (ROOT / "Reviewed").resolve()
    sync_roots = [Path(os.environ[key]).resolve() for key in ["OneDrive", "OneDriveConsumer", "OneDriveCommercial"] if os.environ.get(key)]
    assert any(archive.is_relative_to(path) for path in sync_roots)
    rows = list(csv.DictReader((ROOT / "BATTLE_REVIEW_INDEX.csv").open(encoding="utf-8-sig", newline="")))
    approval = read(BATCH / "OWNER_EXCERPT_ARCHIVE_APPROVAL.json")
    assert approval["approved"] is True and sorted(approval["source_basenames"]) == sorted(EXCERPTS)
    entries = []
    for video in VIDEOS:
        packet = BATCH / Path(video).stem
        lead = read(packet / "LEAD_ACCEPTANCE.json")
        move = read(packet / ("MOVE_RECEIPT." + video + ".json"))
        row = [row for row in rows if row["Video"] == video]
        assert len(row) == 1 and row[0]["Location"] == "Reviewed/" + video
        assert lead["accepted"] is True and move["identity_match"] is True
        assert move["sha256_before"] == move["sha256_after"] == lead["source_sha256"]
        if video in EXCERPTS:
            exception = read(packet / "LEAD_ARCHIVE_EXCEPTION.json")
            assert exception["approved"] is True and exception["source_sha256"] == approval["source_sha256"][video] == lead["source_sha256"]
            assert row[0]["Status"] == "Needs full battle review" and lead["battle_complete"] is False
        else:
            assert row[0]["Status"] == "Reviewed" and lead["battle_complete"] is True
        path = (archive / video).resolve()
        assert path.parent == archive and path.is_file()
        before = metadata_module.metadata(path)
        assert before["logical_bytes"] == move["bytes"]
        entry = {"video": video, "path": str(path), "source_sha256_from_verified_move": lead["source_sha256"],
                 "owner_excerpt_exception": video in EXCERPTS, "before": before, "requested_online_only": False}
        if args.apply and not before["online_only"]:
            if not before["cloud_placeholder"] or not before["in_sync"]:
                entry["pending_reason"] = "Waiting for OneDrive sync; original contents retained"
            else:
                attrib = str(Path(os.environ["SystemRoot"]) / "System32/attrib.exe")
                if before["unpinned"]:
                    subprocess.run([attrib, "-U", "-P", str(path)], check=True, capture_output=True, text=True)
                    time.sleep(1)
                subprocess.run([attrib, "+U", "-P", str(path)], check=True, capture_output=True, text=True)
                entry["requested_online_only"] = True
        entries.append(entry)
    deadline = time.monotonic() + (args.wait_seconds if args.apply else 0)
    while True:
        for entry in entries:
            entry["after"] = metadata_module.metadata(Path(entry["path"]))
            assert entry["after"]["logical_bytes"] == entry["before"]["logical_bytes"]
        if all(entry["after"]["online_only"] and entry["after"]["in_sync"] for entry in entries) or time.monotonic() >= deadline:
            break
        time.sleep(min(2, max(0, deadline - time.monotonic())))
    receipt = {"checked_utc": datetime.now(timezone.utc).isoformat(), "applied": args.apply,
               "videos": len(entries), "online_only": sum(entry["after"]["online_only"] and entry["after"]["in_sync"] for entry in entries),
               "allocated_bytes": sum(entry["after"]["allocated_bytes"] for entry in entries),
               "files_deleted": 0, "video_contents_read": False,
               "method": "Existing Cloud Files metadata query; documented attrib +U -P only for in-sync placeholders; explicit owner approval binds exactly two excerpt exceptions",
               "entries": entries}
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    (BATCH / ("STORAGE_CHECK." + stamp + ".json")).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    (BATCH / "FINAL_STORAGE_CHECK.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in receipt.items() if key != "entries"}))


if __name__ == "__main__":
    main()
