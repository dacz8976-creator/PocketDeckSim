#!/usr/bin/env python3
"""Post-freeze Limitless pull (Dustin, Sept 27: "Now is fine"), by the skill-model folder's method, for confirmations
on events after the freeze (RUN5 "Rules"; kpg REGISTRATION section 5; the reserve-route no-harm re-check).

The rule, fixed here before any outcome is fetched:
- Events: the Limitless API tournament list (game=POCKET, limit=1000), format null or STANDARD, scheduled start date
  (UTC) on or after 2026-09-25, and at least 24 hours before this pull's frozen time (the API has no completion
  timestamp). The skill model's collection ended with start dates through 2026-09-24 UTC, so no event overlaps it,
  and nothing from the spent Sept 25 holdout is read.
- Membership is frozen from event metadata only (events.json, with the pull time), before any standings or pairings.
- Outcomes: details, standings and pairings per event, cached raw with the same fetch code (honours RateLimit and
  Retry-After). An event with any "unresolved" pairing is unfinished: it is dropped whole and listed.
- Matches: the skill model's serialize_matches, unchanged (one row per API pairing entry; exact deck ids).
Stages: python3 collect.py freeze | fetch | matches
"""
import csv, datetime, gzip, json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
SKILL = HERE.parent / "limitless_skill_model_2026-09-25"
sys.path.insert(0, str(SKILL))
sys.dont_write_bytecode = True
import fetch as F  # noqa: E402  (the skill model's cached, rate-limited fetch)
F.RAW = HERE / "raw"; F.RAW.mkdir(exist_ok=True); F.STATE = F.RAW / "rate_state.json"
START = "2026-09-25"
MAPPING = json.loads((SKILL / "deck_mapping.json").read_text(encoding="utf-8"))["deck_ids"]
REV = {v: k for k, vs in MAPPING.items() for v in vs}


def freeze():
    out = HERE / "events.json"
    if out.exists():
        raise SystemExit("events.json exists: membership is already frozen")
    now = datetime.datetime.now(datetime.timezone.utc)
    lst = F.get_json("https://play.limitlesstcg.com/api/tournaments?game=POCKET&limit=1000",
                     f"tournaments_limit1000_{now:%Y%m%dT%H%M%SZ}")
    cutoff = (now - datetime.timedelta(hours=24)).isoformat().replace("+00:00", "Z")
    assert min(x["date"][:10] for x in lst) < START, "need further pagination"
    chosen = sorted([x for x in lst if x["format"] in (None, "STANDARD") and x["date"][:10] >= START
                     and x["date"] <= cutoff], key=lambda x: x["id"])
    skipped_recent = sorted(x["id"] for x in lst if x["format"] in (None, "STANDARD") and x["date"] > cutoff)
    for e in chosen:
        e["split"] = "postfreeze"
    out.write_text(json.dumps({"frozen_at": now.isoformat(), "rule": __doc__.split("The rule")[1].split("Stages")[0].strip(),
                               "start_date_utc": START, "latest_start_utc": cutoff, "events": chosen,
                               "too_recent_not_taken": skipped_recent}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"frozen {len(chosen)} events (start {START} to {cutoff}); {len(skipped_recent)} too recent; no outcomes read")


def fetch_all():
    ev = json.loads((HERE / "events.json").read_text(encoding="utf-8"))["events"]
    for i, e in enumerate(sorted(ev, key=lambda e: (e["date"], e["id"]))):
        print(f"event {i + 1}/{len(ev)} {e['id']}", flush=True)
        for endpoint in ("details", "standings", "pairings"):
            F.fetch(f"https://play.limitlesstcg.com/api/tournaments/{e['id']}/{endpoint}", f"{e['id']}_{endpoint}")
    print("FETCH COMPLETE")


def readraw(eid, kind):
    return json.loads(gzip.decompress((F.RAW / f"{eid}_{kind}.json.gz").read_bytes()))


def serialize_matches(events):
    """The skill model's analyze.py serialize_matches, unchanged apart from its output path and REV's source."""
    rows = []; seen = set()
    for e in events:
        eid = e['id']; det = readraw(eid, 'details'); sts = readraw(eid, 'standings'); ps = readraw(eid, 'pairings')
        assert det['format'] in (None, 'STANDARD')
        players = {r['player']: r for r in sts}; assert len(players) == len(sts)
        phases = {p['phase']: p for p in det['phases']}
        for i, p in enumerate(ps):
            p1 = p.get('player1', ''); p2 = p.get('player2', ''); winner = p.get('winner')
            key = (eid, p.get('phase'), p.get('round'), p.get('table'), p.get('match'), p1, p2)
            assert key not in seen, ('duplicate match identity', key); seen.add(key)
            if not p1 or not p2: status = 'bye_or_automatic_loss'
            elif winner == 0: status = 'tie'
            elif winner == -1: status = 'double_loss'
            elif winner in (p1, p2): status = 'decisive'
            else: status = 'unresolved'
            row = {'event_id': eid, 'date': e['date'], 'event_name': e['name'], 'split': e['split'], 'phase': p.get('phase'),
                   'phase_type': phases.get(p.get('phase'), {}).get('type', ''), 'round': p.get('round'),
                   'mode': phases.get(p.get('phase'), {}).get('mode', ''), 'table': p.get('table', ''),
                   'bracket_match': p.get('match', ''), 'source_row': i, 'player1': p1, 'player2': p2, 'winner': winner,
                   'result_status': status}
            for seat, pid in [(1, p1), (2, p2)]:
                pl = players.get(pid, {}) or {}; deck = pl.get('deck') or {}; rec = pl.get('record') or {}
                row.update({f'player{seat}_name': pl.get('name', ''), f'deck{seat}_id': deck.get('id', ''),
                            f'deck{seat}_name': deck.get('name', ''), f'archetype{seat}': REV.get(deck.get('id'), ''),
                            f'player{seat}_final_wins': rec.get('wins', ''), f'player{seat}_final_losses': rec.get('losses', ''),
                            f'player{seat}_final_ties': rec.get('ties', ''), f'player{seat}_placing': pl.get('placing', '')})
            rows.append(row)
    return rows


def matches():
    ev = json.loads((HERE / "events.json").read_text(encoding="utf-8"))["events"]
    rows = serialize_matches(ev)
    unfinished = sorted({r["event_id"] for r in rows if r["result_status"] == "unresolved"})
    empty = sorted({e["id"] for e in ev} - {r["event_id"] for r in rows})
    rows = [r for r in rows if r["event_id"] not in unfinished]
    with open(HERE / "matches.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (HERE / "completeness.json").write_text(json.dumps({"events_frozen": len(ev), "unfinished_dropped": unfinished,
                                                        "no_pairings": empty, "rows": len(rows)}, indent=2) + "\n")
    print(f"{len(rows)} pairing rows from {len(ev) - len(unfinished) - len(empty)} events; "
          f"{len(unfinished)} unfinished dropped, {len(empty)} with no pairings")


if __name__ == "__main__":
    {"freeze": freeze, "fetch": fetch_all, "matches": matches}[sys.argv[1]]()
