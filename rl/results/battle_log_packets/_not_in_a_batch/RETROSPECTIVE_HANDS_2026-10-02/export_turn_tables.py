"""Present accepted full-turn supplements in one consistent, lossless turn table.

This exports existing observations. It performs no video review or fact inference.
"""
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
FIELDS = [
    "Row", "Player", "Mode and setup", "Opening or starting hand",
    "Named draws and searches", "Numbered plays and visible declines",
    "Both boards before", "Both boards after", "Points",
    "Opponent fan", "Owner ending hand", "Discard observations",
    "Source times and evidence", "Limits and provenance",
]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cell(value):
    """Keep every original nested field and null visible without rewording facts."""
    if value is None:
        return "null (not established in this field)"
    if isinstance(value, dict):
        return "<br>".join(
            "<b>" + html.escape(str(key)).replace("|", "&#124;") + "</b>: " + cell(item)
            for key, item in value.items()
        ) or "{}"
    if isinstance(value, list):
        return "<br>".join("[" + str(i + 1) + "] " + cell(item) for i, item in enumerate(value)) or "[]"
    return html.escape(str(value)).replace("|", "&#124;").replace("\r\n", "<br>").replace("\n", "<br>")


def selected(record, keys):
    return {key: record[key] for key in keys if key in record}


def names(cards):
    if cards is None:
        return "not established"
    values=[]
    for card in cards:
        if isinstance(card, dict):
            label=str(card.get('name') or card.get('card_name') or 'unreadable slot')
            if card.get('variant'):
                label+=' ('+str(card['variant'])+')'
            if card.get('limit_reason'):
                label+=' [qualified: '+str(card['limit_reason'])+']'
        else:
            label=str(card)
        values.append(label)
    return cell(values)


def hand(value):
    if not isinstance(value, dict):
        return cell(value)
    if 'cards_left_to_right' not in value:
        return cell(value)
    result=names(value['cards_left_to_right'])
    if 'count' in value:
        result+='; count '+cell(value['count'])
    if value.get('limit_reason'):
        result+='<br>Qualification: '+cell(value['limit_reason'])
    return result


def board(value):
    if not isinstance(value, dict) or 'owner' not in value or 'opponent' not in value:
        return cell(value)
    lines=[]
    if value.get('phase'):
        lines.append(cell(value['phase']))
    for side in ['owner','opponent']:
        subset=value[side]
        lines.append('<b>'+side+'</b>')
        pokemon=[('Active',subset.get('active'))]+[('Bench '+str(i+1),card) for i,card in enumerate(subset.get('bench_in_position_order') or [])]
        for position,card in pokemon:
            if not isinstance(card,dict):
                lines.append(position+': '+cell(card))
                continue
            energy=card.get('attached_energy')
            typed=energy.get('by_type') if isinstance(energy,dict) else None
            typed_text=', '.join(str(kind)+' '+str(count) for kind,count in typed.items() if count) if isinstance(typed,dict) else 'not established'
            if isinstance(typed,dict) and not typed_text:
                typed_text='0'
            line=position+': '+str(card.get('name'))+'; HP '+str(card.get('hp_now'))+'/'+str(card.get('hp_max'))+'; damage '+str(card.get('damage'))+'; Energy '+typed_text+'; Tool '+str(card.get('tool'))
            lines.append(cell(line))
            for key in ['special_conditions','active_effects']:
                if card.get(key):
                    lines.append(key+': '+cell(card[key]))
            if card.get('status')=='inferred':
                lines.append('Attributes qualified as a source-derived boundary; full basis in structured table.')
        lines.append('Energy Zone: '+cell(subset.get('energy_zone')))
        if subset.get('board_effects'):
            lines.append('Side effects: '+cell(subset['board_effects']))
    lines.append('Stadium: '+cell(value.get('stadium')))
    if value.get('shared_effects'):
        lines.append('Shared effects: '+cell(value['shared_effects']))
    if value.get('specific_boundary_derivations'):
        lines.append('Boundary qualifications: '+cell(value['specific_boundary_derivations']))
    return '<br>'.join(lines)


def readable(field,value):
    """Readable presentation; the JSON below remains the exact full export."""
    if field=='Opening or starting hand' and isinstance(value,dict):
        if 'owner_hand_start' in value:
            result='Owner: '+hand(value['owner_hand_start'])
            if value.get('hand_at_start')!=value['owner_hand_start']:
                result+='<br>Acting player: '+hand(value.get('hand_at_start'))
            return result
        return hand(value)
    if field=='Owner ending hand':
        return hand(value)
    if field in ['Both boards before','Both boards after']:
        return board(value)
    if field=='Named draws and searches' and isinstance(value,list):
        result=[]
        for event in value:
            result.append(cell(event.get('kind'))+': '+names(event.get('cards_in_reveal_order')))
            if event.get('limit_reason'):
                result.append('Qualification: '+cell(event['limit_reason']))
        return '<br>'.join(result) or '[]'
    if field=='Numbered plays and visible declines' and isinstance(value,dict):
        result=[]
        for key in ['plays_in_order','automatic_events_in_order','declines_and_no_effect_actions']:
            for event in value.get(key) or []:
                if not isinstance(event,dict):
                    result.append(cell(event));continue
                label=str(event.get('order',''))+'. '+str(event.get('kind') or key)+': '+str(event.get('card_name') or '')
                if event.get('target'):
                    label+='; target '+str(event['target'])
                if event.get('result'):
                    label+='; '+str(event['result'])
                result.append(cell(label))
                if event.get('energy'):
                    result.append('Energy/payment: '+cell(event['energy']))
                if event.get('prompt_text') or event.get('response'):
                    result.append('Prompt/response: '+cell(selected(event,['prompt_text','response'])))
                if event.get('limit_reason'):
                    result.append('Qualification: '+cell(event['limit_reason']))
        return '<br>'.join(result) or '[]'
    if field=='Limits and provenance' and isinstance(value,dict):
        limits=selected(value,['limits','game_limits','capture_status','discard_snapshot_limit','fresh_observation_conflicts_with_inherited','supplement_conflicts'])
        return cell(limits)+'<br>Full per-field basis and preserved accepted prose: TURN_TABLE.json.'
    if field=='Mode and setup' and isinstance(value,dict) and 'deck_log_snapshot' in value:
        deck=value['deck_log_snapshot']
        summary=selected(value,['mode_as_recorded','first_recorded_turn','deck_name','outcome_inherited_from_accepted_review'])
        summary['deck_log_version_and_limits']=selected(deck,['deck_name_in_log','log_list_version','exact_list_status','actual_card_count','game_version_binding_basis','limits'])
        summary['exact_deck_cards_as_recorded']=deck.get('cards_in_log_order')
        return cell(summary)
    return cell(value)


def export(folder):
    filenames = ["PAUSE_GAME.json", "TURN_LEDGER.json", "TURN_EVIDENCE.json", "DECK_USED.json", "LEAD_ACCEPTANCE.json"]
    inputs = {name: read(folder / name) for name in filenames}
    if inputs["LEAD_ACCEPTANCE.json"].get("shared_registration") != "complete":
        return None
    game, ledger, evidence, deck = [inputs[name] for name in filenames[:4]]
    turns = ledger["turns"]
    if not isinstance(turns, list) or len({row["turn_number"] for row in turns}) != len(turns):
        raise ValueError("Turn rows are missing or duplicate in " + folder.name)
    modes = selected(game, ["classification", "excluded_from_ladder", "classification_basis", "mode_observation", "mode_evidence", "mode_flag", "mode", "mode_classification"])
    setup = {
        "Row": "Setup",
        "Player": selected(game, ["who_went_first", "turn_order"]),
        "Mode and setup": {
            "mode_as_recorded": modes,
            "first_recorded_turn": selected(turns[0], ["turn_number", "who_played"]),
            "deck_name": game.get("deck_name"),
            "deck_log_snapshot": deck,
            "outcome_inherited_from_accepted_review": game.get("outcome"),
        },
        "Opening or starting hand": game.get("opening"),
        "Named draws and searches": None,
        "Numbered plays and visible declines": None,
        "Both boards before": game.get("setup_board"),
        "Both boards after": None,
        "Points": None,
        "Opponent fan": None,
        "Owner ending hand": None,
        "Discard observations": None,
        "Source times and evidence": game.get("sources"),
        "Limits and provenance": {
            "game_limits": game.get("limits"),
            "presentation_basis": "Direct export of independently accepted supplement fields. Nulls and observation qualifiers retained. No new source review or reconstruction.",
        },
    }
    snapshots = evidence.get("discard_snapshots") or []
    table = [setup]
    for row in turns:
        ids = row.get("discard_snapshot_ids") or []
        before, after = row.get("board_at_start"), row.get("board_after")
        scores = {
            "before": selected(before, ["points", "score", "owner_points", "opponent_points"]) if isinstance(before, dict) else None,
            "after": selected(after, ["points", "score", "owner_points", "opponent_points"]) if isinstance(after, dict) else None,
            "before_player_fields": {side: selected(before.get(side, {}), ["points", "score"]) for side in ["owner", "opponent"]} if isinstance(before, dict) else None,
            "after_player_fields": {side: selected(after.get(side, {}), ["points", "score"]) for side in ["owner", "opponent"]} if isinstance(after, dict) else None,
            "row_fields": selected(row, ["points", "points_after", "score_after"]),
            "inherited_accepted_context": selected(row.get("accepted_context", {}), ["points_after", "basis", "accepted_review"]),
            "basis": "Score fields are exported where recorded; nested player points remain in the board columns.",
        }
        used = {"turn_number", "who_played", "timing", "source_interval_seconds", "source_video", "hand_at_start", "owner_hand_start", "opponent_hand_at_owner_turn_start", "draws_and_searches", "plays_in_order", "automatic_events_in_order", "board_at_start", "board_after", "owner_hand_end", "discard_snapshot_ids", "turn_evidence_ids", "declines_and_no_effect_actions"}
        table.append({
            "Row": row["turn_number"],
            "Player": row["who_played"],
            "Mode and setup": "Same source and recorded mode as setup.",
            "Opening or starting hand": selected(row, ["hand_at_start", "owner_hand_start"]),
            "Named draws and searches": row.get("draws_and_searches"),
            "Numbered plays and visible declines": selected(row, ["plays_in_order", "automatic_events_in_order", "declines_and_no_effect_actions"]),
            "Both boards before": before,
            "Both boards after": after,
            "Points": scores,
            "Opponent fan": row.get("opponent_hand_at_owner_turn_start"),
            "Owner ending hand": row.get("owner_hand_end"),
            "Discard observations": {
                "snapshot_ids": ids,
                "packet_discard_snapshots_is_null": evidence.get("discard_snapshots") is None,
                "bound_snapshots": [s for s in snapshots if s.get("snapshot_id") in ids],
                "additional_same_turn_snapshots": [s for s in snapshots if s.get("turn_number") == row["turn_number"] and s.get("snapshot_id") not in ids],
            },
            "Source times and evidence": selected(row, ["timing", "source_interval_seconds", "source_video", "turn_evidence_ids"]),
            "Limits and provenance": {key: value for key, value in row.items() if key not in used},
        })
    payload = {
        "schema": "retrospective-standard-turn-table-v1",
        "game_id": folder.name,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input_sha256": {name: digest(folder / name) for name in filenames},
        "columns": FIELDS,
        "row_count_including_setup": len(table),
        "rows": table,
        "recorded_turns_lossless": turns,
        "ledger_level_qualifications": {key: value for key, value in ledger.items() if key != "turns"},
        "evidence_frames_reference": "TURN_EVIDENCE.json",
    }
    (folder / "TURN_TABLE.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    text = "# " + folder.name + " turn table\n\n"
    text += "One setup row followed by one row for each recorded turn, including both players. This readable presentation keeps recorded values and material qualifications. [The structured table](TURN_TABLE.json) retains the complete original wording, nulls, per-field provenance and every original turn row for scripts. [The evidence manifest](TURN_EVIDENCE.json) gives native image paths. Board columns include both Energy Zones, HP, typed Energy, Tools, conditions and effects where recorded. Completion is established by [lead acceptance](LEAD_ACCEPTANCE.json); worker submission-time pending labels are preserved in the original data.\n\n"
    text += "| " + " | ".join(FIELDS) + " |\n| " + " | ".join(["---"] * len(FIELDS)) + " |\n"
    for row in table:
        text += "| " + " | ".join(readable(field,row[field]) for field in FIELDS) + " |\n"
    text += "\nOriginal accepted reviews and source movies were not edited for this export. TURN_TABLE.json retains every original turn row verbatim in recorded_turns_lossless and records the input file hashes.\n"
    (folder / "TURN_TABLE.md").write_text(text, encoding="utf-8")
    # Compare the presentation against its source rather than asserting new evidence.
    saved = read(folder / "TURN_TABLE.json")
    assert saved["recorded_turns_lossless"] == turns
    assert len(saved["rows"]) == len(turns) + 1
    assert all(saved["input_sha256"][name] == digest(folder / name) for name in filenames)
    return {"game_id": folder.name, "turns": len(turns), "setup_rows": 1, "lossless_turns_verified": True, "input_hashes_verified": True, "table_json_sha256": digest(folder / "TURN_TABLE.json"), "table_markdown_sha256": digest(folder / "TURN_TABLE.md")}


if __name__ == "__main__":
    inventory = read(BATCH / "INVENTORY.json")
    receipts = []
    for record in inventory["recordings"]:
        if record["group"] not in ["ladder", "wailord"]:
            continue
        folder = BATCH / record["source"].split("_iOS")[0]
        if not (folder / "LEAD_ACCEPTANCE.json").exists():
            continue
        receipt = export(folder)
        if receipt:
            receipts.append(receipt)
    (BATCH / "TURN_TABLE_EXPORT_VERIFICATION.json").write_text(json.dumps({"schema": "presentation-export-verification-v1", "created_utc": datetime.now(timezone.utc).isoformat(), "exports": receipts}, indent=2), encoding="utf-8")
    print(json.dumps({"accepted_full_turn_tables_exported": len(receipts), "turn_rows": sum(r["turns"] for r in receipts)}))
