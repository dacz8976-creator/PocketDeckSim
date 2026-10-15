"""Lead integrity check; does not read cloud movie content or accept source facts."""
import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parents[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(path):
    path = path.strip()
    if path.startswith("/mnt/c/"):
        path = "C:/" + path[7:]
    return str(Path(path).resolve()).casefold()


parser = argparse.ArgumentParser()
parser.add_argument("--partial", action="store_true")
args = parser.parse_args()
inventory = read(BATCH / "INVENTORY.json")
baseline = read(BATCH / "PRESERVATION_BASELINE.json")
old_files = []
errors = []
for old in baseline:
    path = Path(old["path"])
    exists = path.is_file()
    intact = exists and path.stat().st_size == old["bytes"] and sha(path) == old["sha256"]
    old_files.append({"path": str(path), "unchanged": intact})
    if not intact:
        errors.append("Old accepted file changed or missing: " + str(path))

with (ROOT / "BATTLE_REVIEW_INDEX.csv").open(encoding="utf-8-sig", newline="") as stream:
    index = list(csv.DictReader(stream))
packets = []
for entry in inventory["recordings"]:
    source = entry["source"]
    folder = BATCH / source.split("_iOS")[0]
    matches = [row for row in index if row["Video"] == source]
    if len(matches) != 1:
        errors.append("Index uniqueness failed: " + source)
        continue
    row = matches[0]
    refs = {normalized(item) for item in row["Review evidence"].split("|") if item.strip()}
    old_refs_preserved = all(normalized(item["path"]) in refs for item in entry["accepted_evidence"] if item["exists"])
    full_status_preserved = row["Status"] == "Reviewed" and row["Location"].replace("\\", "/") == "Reviewed/" + source
    if not old_refs_preserved or not full_status_preserved:
        errors.append("Prior status or evidence references not preserved: " + source)
    acceptance_path = folder / "LEAD_ACCEPTANCE.json"
    if not acceptance_path.is_file() or read(acceptance_path).get("shared_registration") != "complete":
        if not args.partial:
            errors.append("Supplement is not independently accepted and registered: " + source)
        packets.append({"source": source, "accepted": False, "prior_full_status_preserved": full_status_preserved, "prior_evidence_references_preserved": old_refs_preserved})
        continue
    lead = read(acceptance_path)
    hashes = {name: (folder / name).is_file() and sha(folder / name) == expected for name, expected in lead["accepted_packet_hashes"].items()}
    if not all(hashes.values()):
        errors.append("Accepted packet hash drift: " + source)
    check_path = Path(lead["independent_check"])
    check = read(check_path)
    check_verdict = check.get("verdict", check.get("final_verdict"))
    if check_verdict is None and check.get("independent_acceptance") is True:
        check_verdict = check.get("status")
    check_accepted = check_verdict in ["accepted", "accepted_with_recording_limits"]
    event_path = Path(lead["shared_event"])
    event = read(event_path)
    event_registered = event.get("status") == "full_battle_review_complete"
    if not check_accepted or not event_registered:
        errors.append("Independent acceptance or registration receipt failed: " + source)
    table_verified = None
    if entry["group"] in ["ladder", "wailord"]:
        table_path = folder / "TURN_TABLE.json"
        if table_path.is_file():
            table = read(table_path)
            ledger = read(folder / "TURN_LEDGER.json")
            table_verified = table["recorded_turns_lossless"] == ledger["turns"] and len(table["rows"]) == len(ledger["turns"]) + 1 and all(sha(folder / name) == expected for name, expected in table["input_sha256"].items())
        else:
            table_verified = False
        if not table_verified:
            errors.append("Standard turn table is missing or stale: " + source)
    packets.append({"source": source, "accepted": True, "prior_full_status_preserved": full_status_preserved, "prior_evidence_references_preserved": old_refs_preserved, "accepted_packet_hashes_unchanged": all(hashes.values()), "independent_source_acceptance": check_accepted, "registration_event_verified": event_registered, "standard_table_verified": table_verified, "source_sha256": lead["source_sha256"], "excluded_from_ladder": lead.get("excluded_from_ladder"), "packet": str(folder)})

receipt = {"schema": "retrospective-batch-integrity-verification-v1", "checked_utc": datetime.now(timezone.utc).isoformat(), "partial_check": args.partial, "approved_limit": inventory["approved_limit"], "selected_recordings": len(inventory["recordings"]), "accepted_registered": sum(row["accepted"] for row in packets), "original_accepted_files_checked": len(old_files), "original_accepted_files_unchanged": sum(row["unchanged"] for row in old_files), "movie_content_reads": 0, "check_basis": "Saved independent acceptance, frozen packet hashes, additive registration, original packet preservation, lossless table exports. This integrity check does not replace visual source acceptance.", "packets": packets, "original_files": old_files, "errors": errors, "passed": not errors}
target = BATCH / ("BATCH_INTEGRITY_INTERIM.json" if args.partial else "BATCH_COMPLETION_VERIFICATION.json")
target.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
print(json.dumps({key: receipt[key] for key in ["partial_check", "selected_recordings", "accepted_registered", "original_accepted_files_checked", "original_accepted_files_unchanged", "passed", "errors"]}))
if errors:
    raise SystemExit(1)
