"""Apply the bounded Astra findings without changing old accepted evidence."""
import hashlib
import json
import shutil
from pathlib import Path

BATCH = Path(__file__).resolve().parent
P = BATCH / "20260908_022627000"
saved = P / "before_astra_reference_repair"
assert not saved.exists()
saved.mkdir()
names = ["TURN_LEDGER.json", "REVIEW_SUPPLEMENT.md", "UNCERTAINTIES.json", "SUBMISSION.json"]
for name in names:
    shutil.copy2(P / name, saved / name)

ledger = json.loads((P / "TURN_LEDGER.json").read_text(encoding="utf-8-sig"))
rows = {row["turn_number"]: row for row in ledger["turns"]}
retreat = next(play for play in rows[15]["plays_in_order"] if play["kind"] == "retreat")
assert retreat["evidence_ids"] == ["F0591.00", "F0593.00"]
retreat["evidence_ids"] = ["F0591.00", "F0596.00"]
retreat["energy_retention_basis"] = "Direct nearby post-retreat Bench at F0596.00 shows 100 HP and both Psychic and Darkness retained. F0593.00 remains pre-switch/selection."
retreat["retreat_payment_basis"] = "Zero payment is endpoint-derived from the blank live Retreat cost at F0591.00 and unchanged typed Energy at F0596.00; no discard-selection input was observed."
retreat["limit_reason"] += " Requested596.0 seconds has producer-measured PTS596.0; exact retreat input remains uncertified."
retreat3 = next(play for play in rows[3]["plays_in_order"] if play["kind"] == "retreat")
retreat3["retreat_payment_basis"] = "One Psychic payment is inferred from the position switch, one-Psychic-to-zero endpoints F0126.00/F0137.00 and printed one-Colorless retreat cost. Exact discard-selection input was not inspected."
attachment12 = next(play for play in rows[12]["plays_in_order"] if play["kind"] == "energy_attachment")
attachment12["attachment_target_basis"] = "Endpoint-derived normal attachment: Drapion has one Darkness at F0467.00 and two at F0500.00; Mega Absol remains two. Generated Darkness is still available at467. The event is attributed to opponent turn12, bounded before the producer-observed owner13 banner near499."
attachment12["limit_reason"] += " F0500.00 is the owner-turn13 post-state. The467–500 endpoint interval crosses that turn boundary; neither endpoint pictures the attachment input."
ledger["astra_reference_repair"] = {
    "check": str(BATCH / "astra_checks" / P.name / "ACTION_CHECK.json"),
    "basis": "Bounded27-native Astra question check; whole-packet independent Sol acceptance still pending.",
    "preserved_questions": "ASTRA_QUESTIONS.json remains frozen as submitted; required reference/timing errata recorded here and in ASTRA_QUESTION_ERRATA.json.",
}
(P / "TURN_LEDGER.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")
note = "\nAstra reference check: Turn15 retained Psychic + Darkness is directly supported by F0596.00 after the switch, not F0593.00, which still shows Raticate Active. Zero retreat payment is derived from the blank live cost and unchanged Energy, not an observed discard input. Turn12 attachment target is endpoint-derived; F0500.00 is owner13 post-state, and the467–500 interval crosses the turn boundary. The attachment event is attributed to opponent12 using the producer-observed banner near499.\n"
with (P / "REVIEW_SUPPLEMENT.md").open("a", encoding="utf-8") as stream:
    stream.write(note)
uncertainties = json.loads((P / "UNCERTAINTIES.json").read_text(encoding="utf-8-sig"))
uncertainties["astra_reference_qualification"] = note.strip()
(P / "UNCERTAINTIES.json").write_text(json.dumps(uncertainties, ensure_ascii=False, indent=2), encoding="utf-8")
errata = {
    "frozen_question_file": "ASTRA_QUESTIONS.json",
    "source_sha256": "5689a2c45eda9b0629d7a2616852beef6fedb8396bdfe34c080b4c136e4e364e",
    "corrections": [
        {"question": "CAPE_RATICATE_FREE_RETREAT", "old_reference": "after593", "corrected_reference": "after596", "requested_seconds": 596.0, "producer_measured_pts": 596.0, "pre_switch_reference_preserved": "F0593.00"},
        {"question": "OPPONENT_ATTACHMENT_TARGETS_COUNTS", "correction": "467–500 endpoint interval crosses into owner13;500 is post-state, not opponent12. Only the attachment event is attributed to opponent12."},
    ],
    "new_video_reads": 0,
    "new_extraction": 0,
}
(P / "ASTRA_QUESTION_ERRATA.json").write_text(json.dumps(errata, indent=2), encoding="utf-8")
submission = json.loads((P / "SUBMISSION.json").read_text(encoding="utf-8-sig"))
submission["astra_reference_repair"] = {"errata": "ASTRA_QUESTION_ERRATA.json", "preserved_original_submission": str(saved / "SUBMISSION.json"), "modified_file_sha256": {name: hashlib.sha256((P / name).read_bytes()).hexdigest() for name in names[:-1]}}
(P / "SUBMISSION_AFTER_ASTRA_REPAIR.json").write_text(json.dumps(submission, indent=2), encoding="utf-8")
print(json.dumps({"repaired": P.name, "new_video_reads": 0, "original_packet_edited": False, "native_images_edited": False, "whole_packet_acceptance": "pending different Sol reviewer"}))
