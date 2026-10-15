"""Correct supplemental action fields from the independent Sol source check."""
import copy
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

BATCH = Path(__file__).resolve().parent
P = BATCH / "20260908_190933000"
SAVE = P / "before_independent_action_repair"
assert not SAVE.exists()
SAVE.mkdir()
names = ["TURN_LEDGER.json", "TURN_EVIDENCE.json", "REVIEW_SUPPLEMENT.md", "UNCERTAINTIES.json", "METRICS.json"]
for name in names:
    shutil.copy2(P / name, SAVE / name)

def read(name):
    return json.loads((P / name).read_text(encoding="utf-8-sig"))

def write(name, data):
    (P / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

new_paths = list((P / "independent_added_evidence").glob("*.jpg"))
new_paths += list((BATCH / "independent_ladder" / P.name / "added_t8").glob("*.jpg"))
assert len(new_paths) == 9, "All nine independently inspected native captures are required."
evidence = read("TURN_EVIDENCE.json")
lookup = {}
crop_bytes = 0
for path in sorted(new_paths):
    time = float(path.stem.removeprefix("t"))
    tag = "repair_" + f"{time:07.2f}"
    lookup[time] = tag
    with Image.open(path) as image:
        assert image.size == (1170, 2532)
        bottom = P / "hand_crops" / (tag + "_bottom.jpg")
        top = P / "hand_crops" / (tag + "_top.jpg")
        image.crop((0, 2025, 1170, 2532)).save(bottom, quality=95)
        image.crop((0, 0, 1170, 582)).save(top, quality=95)
    crop_bytes += bottom.stat().st_size + top.stat().st_size
    evidence["frames"].append({
        "evidence_id": tag, "role": "independent check action-order repair anchor",
        "turn_number": 2 if time < 200 else 8, "who_played": "opponent",
        "source_video": "20260908_190933000_iOS.MP4",
        "source_sha256": "5c49e55a0b3153581904ffcefd747d941d5a729412a90708ec1f2783649610c5",
        "requested_source_seconds": time, "actual_frame_seconds_if_measured": None,
        "full_frame_path": str(path), "full_frame_sha256": sha(path),
        "native_dimensions": {"width": 1170, "height": 2532},
        "bottom_crop": {"path": str(bottom), "pixel_bounds_x0_y0_x1_y1": [0,2025,1170,2532]},
        "top_crop": {"path": str(top), "pixel_bounds_x0_y0_x1_y1": [0,0,1170,582]},
        "selected_for_start_hand": False, "before_first_play": False,
        "suitability_or_limit": "Native action evidence, not an owner turn-start substitute. Requested source time; actual PTS not measured. Independently inspected by Sol before this field repair.",
    })
write("TURN_EVIDENCE.json", evidence)
ledger = read("TURN_LEDGER.json")
rows = {row["turn_number"]: row for row in ledger["turns"]}

def qualify(play, order, refs, interval=None):
    play = copy.deepcopy(play)
    play["inherited_action_fields_preserved"] = {"order": play.get("order"), "timestamp_seconds": play.get("timestamp_seconds"), "timestamp_basis": play.get("timestamp_basis"), "basis": play.get("basis")}
    play.update(order=order, evidence_ids=refs,
                basis="Independent Sol native observations plus approximate source-local locator order; old accepted prose retained separately.",
                timestamp_seconds=None,
                timestamp_basis="Requested native anchors and one-frame-per-second source cues; exact input time and actual PTS are unmeasured.",
                source_event_interval_seconds=interval)
    return play

old2 = rows[2]["plays_in_order"]
assert len(old2) == 4
research = qualify(old2[0],1,["t0114.50"],[92.5,93.5])
left = qualify(old2[1],2,[lookup[102.5]],[98.5,99.5])
ball = qualify(old2[0],3,[lookup[100.5],lookup[102.5],lookup[108.5]],[100.5,108.5])
ball.update(kind="item", card_name="Poké Ball", target="opponent deck search", result="Search resolves with concealed card identity; Poké Ball becomes the opposing discard-pile top.", accepted_provenance=None, limit_reason="Search result is face down. The later regular Electrike bench does not directly identify the searched card. The transaction/animation is located about100.5–103.5;108.5 is a subsequent pile/board anchor.")
right = qualify(old2[2],4,[lookup[108.5]],[103.5,108.5])
energy = qualify(old2[3],5,[lookup[108.5],"t0114.50"],[108.5,111.5])
energy["attachment_target_basis"] = "The left Electrike endpoint has one Lightning; attachment follows the second bench in the inspected source cues. Exact input not captured by the selected stills."
rows[2]["plays_in_order"] = [research,left,ball,right,energy]
rows[2]["draws_and_searches"] += [
    {"kind":"Professor's Research", "cards_in_reveal_order":None, "count":2, "basis":"Opponent resolves Research, but both draw identities remain concealed.", "evidence_ids":["t0114.50"], "limit_reason":"Hidden opponent draw identities; Research play/order inherited and corroborated by source cues."},
    {"kind":"Poké Ball", "cards_in_reveal_order":None, "count":1, "basis":"Independent native/locator search transaction and pile transition.", "evidence_ids":[lookup[100.5],lookup[102.5],lookup[108.5]], "limit_reason":"Concealed search result; regular Electrike as the searched card would only be an inference and is not adopted."},
]
rows[2]["turn_evidence_ids"] += [lookup[t] for t in [100.5,102.5,108.5]]
rows[2]["fresh_observation_conflicts_with_inherited"].append("Older accepted turn2 prose omits the opponent Poké Ball. New source order is Research, first left Electrike, Poké Ball search, second regular Electrike, then Lightning; inherited99.5/102.5/108.5 action times were not exact input observations.")

old8 = rows[8]["plays_in_order"]
assert len(old8) == 7
# Native343.5 proves retreat happened while Electrode still had zero Energy.
sequence = [
    (2,[lookup[314.5],lookup[317.5]],[314.5,315.5]),
    (0,[lookup[317.5],lookup[333.5]],[317.5,319.5]),
    (3,[lookup[333.5]],[332.5,333.5]),
    (4,[lookup[335.5],lookup[339.5]],[334.5,336.5]),
    (5,[lookup[339.5],lookup[343.5]],[339.5,343.5]),
    (1,[lookup[343.5],"t0354.00"],[343.5,350.5]),
    (6,["t0354.00"],[350.5,353.5]),
]
rows[8]["plays_in_order"] = [qualify(old8[idx], order, refs, interval) for order,(idx,refs,interval) in enumerate(sequence,1)]
rows[8]["plays_in_order"][4]["retreat_payment_basis"] = "Typed Energy retention and the source-supported free retreat are distinct from the attack-cost icons; no discard input asserted. Native343.5 shows damaged Mega on Bench with two Lightning and Electrode Active with none."
rows[8]["plays_in_order"][5]["attachment_target_basis"] = "Endpoint-derived: Electrode Active has no attached Energy at343.5, then one Lightning at354; current Lightning is still available at339.5. Locator attack begins about350.5, placing attachment after retreat and before attack."
rows[8]["plays_in_order"][5]["limit_reason"] = "Exact Energy input is not pictured by these selected stills; the attachment interval is source-cue/endpoint-derived."
rows[8]["turn_evidence_ids"] += [lookup[t] for t in [314.5,317.5,333.5,335.5,339.5,343.5]]
rows[8]["fresh_observation_conflicts_with_inherited"].append("Fresh order is Protective Poncho, Electrode evolution, second Voltorb bench, second Mega evolution, damaged Mega retreat, Lightning to promoted Active Electrode, Random Spark. Older evolution/Energy-before-Poncho and Energy-before-retreat order is contradicted. A preliminary reduced-grid reading of the339.5 Energy Zone was incorrect and not adopted; the native still shows current Lightning available and Electrode Energy0.")
def nested_refs(value):
    result=[]
    if isinstance(value, dict):
        for key,item in value.items():
            if key == 'evidence_ids' and isinstance(item, list):
                result.extend(item)
            else:
                result.extend(nested_refs(item))
    elif isinstance(value, list):
        for item in value:
            result.extend(nested_refs(item))
    return result
declared={frame['evidence_id'] for frame in evidence['frames']}
for row in ledger['turns']:
    row['turn_evidence_ids']=list(dict.fromkeys((row.get('turn_evidence_ids') or [])+nested_refs(row)))
    assert set(row['turn_evidence_ids']).issubset(declared), 'Unresolved row evidence references'
ledger["independent_action_repair"] = {"check_folder":str(BATCH/"independent_ladder"/P.name), "required_native_additions":9, "whole_packet_repair_acceptance":"pending", "old_accepted_prose_modified":False}
write("TURN_LEDGER.json", ledger)
text=(P/"REVIEW_SUPPLEMENT.md").read_text(encoding="utf-8-sig")
for turn in [2,8]:
    start=text.index("## Turn"+str(turn)+" (opponent)")
    end=text.index("## Turn"+str(turn+1)+" (owner)", start)
    row=rows[turn]
    section="## Turn"+str(turn)+" (opponent)\n\nOwner start hand: "+str(row['owner_hand_start'].get('cards_left_to_right'))+"\n\nOwner ending hand is unchanged in the recorded row. Fresh source action order:\n\n"
    for action in row['plays_in_order']:
        section+=str(action['order'])+". "+action['kind']+": "+str(action.get('card_name') or '')+"; "+action['result']+" Evidence: "+", ".join(action['evidence_ids'])+". Approximate source interval: "+str(action.get('source_event_interval_seconds'))+".\n"
    section+="\n"+row['fresh_observation_conflicts_with_inherited'][-1]+" Exact old prose remains unchanged in INHERITED_TURNS.json and its accepted packet. Input times are approximate; native seek times are not measured PTS.\n\n"
    text=text[:start]+section+text[end:]
(P/"REVIEW_SUPPLEMENT.md").write_text(text,encoding="utf-8")
uncertain=read("UNCERTAINTIES.json")
uncertain['independent_action_order_repairs']={"turn2":rows[2]['fresh_observation_conflicts_with_inherited'][-1],"turn8":rows[8]['fresh_observation_conflicts_with_inherited'][-1],"concealed_opponent_search":"Poké Ball result stays null; next bench is not proof of searched identity."}
write("UNCERTAINTIES.json",uncertain)
metrics=read("METRICS.json")
metrics['approved_native_cap']=59
metrics['new_native_full_frames']+=9
metrics['bottom_crops']+=9
metrics['top_crops']+=9
metrics['new_native_full_frame_bytes']+=sum(path.stat().st_size for path in new_paths)
metrics['native_crop_bytes']+=crop_bytes
metrics['independent_action_repair']={"native_additions":9,"additional_sha_reads":0,"cached_decoder_captures":9,"source_old_files_modified":False,"purpose":"Resolve omitted opponent search and exact action order, with source limits retained."}
write("METRICS.json",metrics)
print(json.dumps({"repaired":P.name,"additional_native_frames":9,"new_total_native_frames":metrics['new_native_full_frames'],"old_packet_modified":False,"independent_repair_acceptance":"pending"}))
