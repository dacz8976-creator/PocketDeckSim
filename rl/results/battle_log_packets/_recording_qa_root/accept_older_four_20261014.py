"""Root-only acceptance and normal append-only registration of this named batch."""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / "Recording_QA/BATCH_2026-10-14_OLDER_FOUR"
CONFIG = {
    "20261002_011527000_iOS": {
        "full": True,
        "checks": [
            ("native/t0240.00.jpg", "Ordinary turn8 ends with Garchomp90HP, Water+Fighting, Combusken80HP, score2-0 and Auto OFF"),
            ("native/t0321.00.jpg", "Auto ON after knockout, during promotion; original Froakie60, second Froakie60, Garchomp110 Bench"),
            ("native/t0341.00.jpg", "Auto ON during Water Shuriken damage animation"),
            ("native/t0342.00.jpg", "First checked native Auto OFF after Water Shuriken; switch bounded341-342s"),
            ("native/t0393.00.jpg", "Three-point award after Mega Blaziken ex knockout"),
            ("native/t0401.60.jpg", "Named preset Victory;14turns, went second,3-2,490damage"),
        ],
        "scope": "Entire 404.598333-second recording; setup, all 14 turns and terminal victory; one computer battle",
        "notes": "Independent Sol acceptance after narrowly corrected Auto timing and root native-source checks. Computer battle, win3-2. Mixed AutoOFF-ON-OFF: OFF318s, ON321-341s, OFF342s. Frame338 hides control, so cannot establish OFF. Choice authorship remains limited. Excluded from Ladder Log and Pause Games. Rejected draft preserved; LEAD_ACCEPTANCE is authoritative after primary freeze.",
    },
    "20261002_012229000_iOS": {
        "full": True,
        "checks": [
            ("setup/t0002.00.jpg", "Setup explicitly labels opponent AI"),
            ("independent_sol/evidence/fresh_74.50.jpg", "Ordinary turn: Gabite80, two Froakie60, Water attached; Auto OFF"),
            ("independent_sol/evidence/fresh_206.00.jpg", "Garchomp0 HP after Burn20; Heads/recovery notice does not prevent knockout; Auto OFF"),
            ("independent_sol/evidence/fresh_309.00.jpg", "Named preset Defeat result"),
        ],
        "scope": "Entire 309.766667-second recording; AI setup, all 12 turns and terminal defeat; one computer battle",
        "notes": "Independent Sol acceptance and root native-source checks. Computer battle, Auto OFF observed, owner loss2-3. Excluded from Ladder Log and Pause Games. Original frozen primary independent_acceptance field remains historical; LEAD_ACCEPTANCE is authoritative.",
    },
    "20260926_211809000_iOS": {
        "full": False,
        "checks": [
            ("evidence/native_00p000s.jpg", "Already-developed board with owner first point present; opening and earlier turns missing"),
            ("evidence/native_38p000s.jpg", "Your opponent conceded; owner last score2-0 against XaBy8"),
            ("evidence/native_43p400s.jpg", "Dacz8976 Victory with Galarian Obstagoon"),
        ],
        "scope": "All 43.463333 seconds of late-battle excerpt reviewed; concession win established; setup, opening, earlier turns and first owner point unavailable",
        "notes": "Independent acceptance and root checks of complete available excerpt only. Win by XaBy8 concession, last visible score2-0. No Auto option observed; actual queue unknown. Missing original battle start prevents full-battle completion and ordinary archival. Ladder candidate awaiting fresh live filename duplicate check and save; no external entry made.",
    },
    "20260926_212155000_iOS": {
        "full": False,
        "checks": [
            ("../root_checks/StefaGo/t0000.00.jpg", "Source starts during initial owner turn with placed Basics; setup and earlier initial choices absent; no entirely missing completed turn established"),
            ("evidence/t0200.00.jpg", "Your opponent conceded; last score2-1 against StefaGo"),
            ("evidence/t0201.00.jpg", "Concession remains visible"),
            ("evidence/t0203.50.jpg", "Dacz8976 Victory with Hydreigon; corrects earlier no-result claim"),
        ],
        "scope": "All 205.771927 seconds reviewed through StefaGo concession and Victory; setup and beginning of initial owner turn unavailable",
        "notes": "Independent acceptance and root checks of complete available excerpt only. Win by StefaGo concession at199.5-201s; Victory at203.5-204s. Corrects earlier report that result was missing. Initial setup/choices remain missing; no whole previous turn established. No Auto observed; actual queue unknown. Full-battle completion and ordinary archival remain unavailable. Ladder candidate awaiting live duplicate check/save; no external entry made.",
    },
}


def digest(path):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def save(path, value):
    if path.exists():
        raise RuntimeError(f"Refusing to replace existing receipt: {path}")
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", choices=CONFIG)
    args = parser.parse_args()
    packet = BATCH / args.packet
    config = CONFIG[args.packet]
    source = json.loads((packet / "SOURCE.json").read_text(encoding="utf-8-sig"))
    summary = json.loads((packet / "SUMMARY.json").read_text(encoding="utf-8-sig"))
    correction = packet / "independent_sol/CORRECTION_RECHECK.json"
    check_path = correction if correction.is_file() else packet / "independent_sol/CHECK_RESULT.json"
    check = json.loads(check_path.read_text(encoding="utf-8-sig"))
    assert check.get("accepted") is True or check.get("decision") == "accepted_available_footage_packet"
    if "final_input_hashes" in check:
        hashes = check["final_input_hashes"]
        assert hashes == check["initial_input_hashes"]
        checked_source = check["source"]
    else:
        initial = json.loads((packet / "independent_sol/INTEGRITY_INITIAL.json").read_text(encoding="utf-8-sig"))
        final = json.loads((packet / "independent_sol/INTEGRITY_FINAL.json").read_text(encoding="utf-8-sig"))
        assert initial["files_checked"] == final["files_checked"]
        assert check["all_frozen_entries_match"] is True and check["primary_packet_unchanged_between_checks"] is True
        assert check["source_sha256_initial"] == check["source_sha256_final"]
        hashes = {row["path"]: row["sha256"] for row in final["files_checked"]}
        hashes["REVIEW_PACKET_HASHES.json"] = check["frozen_primary_manifest_sha256_final"]
        checked_source = {"filename": check["source_basename"], "sha256": check["source_sha256_final"]}
    for name, expected in hashes.items():
        assert digest(packet / name).lower() == expected.lower(), name
    video = args.packet + ".MP4"
    sha = source.get("sha256", source.get("source_sha256"))
    assert checked_source["sha256"].lower() == sha.lower()
    assert checked_source["filename"] == video
    assert summary["battle_complete"] is config["full"]
    observations = [
        {"path": name, "sha256": digest(packet / name), "directly_viewed_by_root": True, "finding": fact}
        for name, fact in config["checks"]
    ]
    now = datetime.now(timezone.utc).isoformat()
    save(packet / "SOURCE_CHECKS.json", {
        "lead": "/root", "checked_utc": now,
        "source_filename": video, "source_sha256": sha,
        "basis": "Direct original-resolution visual inspection, independent frozen packet and source identity reconciliation",
        "observations": observations,
    })
    save(packet / "LEAD_ACCEPTANCE.json", {
        "accepted": True,
        "decision": "accepted_full_battle_review" if config["full"] else "accepted_available_footage_review_only",
        "lead": "/root", "accepted_utc": now,
        "source_video": video, "source_sha256": sha,
        "source_game_count": 1, "all_source_games_accepted": config["full"],
        "battle_complete": config["full"], "archive_eligible": config["full"],
        "scope": config["scope"], "independent_acceptance": str(check_path),
        "independent_model_configuration": "gpt-6.1-sol/high, fresh compact independent task per applicable review cost instructions",
        "independent_acceptance_sha256": digest(check_path), "accepted_input_sha256": hashes,
        "root_checks": "SOURCE_CHECKS.json", "notes": config["notes"],
    })
    evidence = ["SOURCE.json", "REVIEW.md", "COVERAGE.md", "SUMMARY.json", "UNCERTAINTIES.json", "SOURCE_CHECKS.json", "LEAD_ACCEPTANCE.json", check_path.relative_to(packet).as_posix()]
    command = [sys.executable, str(ROOT / "Review_Log/review_log.py"), "record", "--video", video,
               "--reviewer", summary["reviewer"], "--status", "full_battle_review_complete" if config["full"] else "partial",
               "--scope", config["scope"], "--notes", config["notes"],
               "--recording-time", summary["source_creation_utc"]]
    for name in evidence:
        command.extend(["--evidence", str((packet / name).relative_to(ROOT))])
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    save(packet / "REGISTRATION_RESULT.json", {"registered_utc": datetime.now(timezone.utc).isoformat(), "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr, "command": command})
    print(json.dumps({"packet": args.packet, "status": command[command.index("--status") + 1], "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}))
    if result.returncode:
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
