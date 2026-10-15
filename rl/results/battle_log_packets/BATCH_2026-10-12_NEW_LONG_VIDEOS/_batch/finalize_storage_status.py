import datetime
import hashlib
import json
from pathlib import Path
import shutil

batch = Path(__file__).resolve().parent
mirror = Path(r"C:\Users\dacz8\Projects\Pocket Deck Lab\Boss Folder\BATCH_2026-10-12_NEW_LONG_VIDEOS")
storage_source = batch.parent / "CLOUD_STORAGE" / "20261013T002408284304Z.apply.json"
storage = json.loads(storage_source.read_text(encoding="utf-8-sig"))
expected_sizes = {
    "20261012_010706000_iOS.MP4": 1531356838,
    "20261012_203719000_iOS.MP4": 1496457121,
    "20261012_210041000_iOS.MP4": 820910252,
    "20261012_210823000_iOS.MP4": 817334249,
}
assert storage["videos"] == storage["online_only"] == 4
assert storage["allocated_bytes_after"] == storage["files_deleted"] == 0
assert {entry["video"] for entry in storage["entries"]} == set(expected_sizes)
for entry in storage["entries"]:
    after = entry["after"]
    assert after["in_sync"] and after["online_only"] and after["cloud_placeholder"]
    assert after["allocated_bytes"] == 0
    assert after["logical_bytes"] == expected_sizes[entry["video"]]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

stamp = "20261013T002408Z"
receipt_name = "FINAL_STORAGE_RELEASE_RECEIPT.json"
assert not (batch / "MIRROR_FINAL_STATUS_RECEIPT.json").exists(), "Already finalized"
shutil.copy2(storage_source, batch / receipt_name)
changed = []
for name in ["README.md", "BATCH_COMPLETION_CHECK.json"]:
    path = batch / name
    assert digest(path) == digest(mirror / name), "Mirror baseline mismatch"
    history_name = f"{path.stem}.before_storage_release_{stamp}{path.suffix}"
    assert not (batch / history_name).exists()
    shutil.copy2(path, batch / history_name)
    old_hash = digest(path)
    if name == "README.md":
        text = path.read_text(encoding="utf-8-sig")
        old_line = "Storage release is verified for 1 of four archived originals. See FINAL_STORAGE_CHECK.json for in-sync flags, online-only state and allocated bytes. No video was deleted. Written packets and retained evidence are mirrored into Pocket Deck Lab/Boss Folder/BATCH_2026-10-12_NEW_LONG_VIDEOS."
        assert old_line in text
        text = text.replace(old_line, "Storage release is verified for all four archived originals as of 2026-10-13 00:24 UTC. All are in sync, online-only and allocate zero local bytes. See FINAL_STORAGE_RELEASE_RECEIPT.json. No video was deleted. Written packets and retained evidence are retained locally and mirrored into Pocket Deck Lab/Boss Folder/BATCH_2026-10-12_NEW_LONG_VIDEOS. The earlier storage snapshot is preserved in FINAL_STORAGE_CHECK.json.")
        path.write_text(text, encoding="utf-8")
    else:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        assert data["all_requested_local_reviews_complete"] and not data["external_saved"]
        data.update({
            "storage_state": "All four archived sources verified in sync, online-only, and zero allocated local bytes by metadata-only check.",
            "storage_online_only_count": 4,
            "storage_allocated_bytes": 0,
            "storage_receipt": receipt_name,
            "storage_updated_utc": storage["created_at_utc"],
            "prior_completion_snapshot": history_name,
        })
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    changed.append({"path": name, "prior_sha256": old_hash, "current_sha256": digest(path), "preserved_prior_path": history_name})

additions = [receipt_name, Path(__file__).name] + [entry["preserved_prior_path"] for entry in changed]
copied = []
for name in [entry["path"] for entry in changed] + additions:
    shutil.copy2(batch / name, mirror / name)
    assert digest(batch / name) == digest(mirror / name)
    copied.append({"path": name, "sha256": digest(batch / name), "bytes": (batch / name).stat().st_size})
receipt = {
    "updated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "purpose": "Complete local storage status after OneDrive synchronization finished; preserve historical snapshots.",
    "all_four_sources_in_sync_online_only_zero_allocated": True,
    "accepted_review_packets_changed": False,
    "video_contents_read": False,
    "external_saved": False,
    "external_message_sent": False,
    "current_owner_authorization_pending": True,
    "source": str(batch),
    "destination": str(mirror),
    "changed_admin_files": changed,
    "all_copy_hashes_match": True,
    "copied_files": copied,
    "prior_mirror_receipt_preserved": "MIRROR_RECEIPT.json",
}
out = batch / "MIRROR_FINAL_STATUS_RECEIPT.json"
out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
shutil.copy2(out, mirror / out.name)
assert digest(out) == digest(mirror / out.name)
print(json.dumps({"storage_online_only": 4, "allocated_bytes": 0, "mirror_hashes_match": True, "external_saved": False, "receipt": str(out)}, indent=2))
