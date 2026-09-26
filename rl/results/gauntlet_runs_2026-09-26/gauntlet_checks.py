#!/usr/bin/env python3
"""Mechanical checks for the gauntlet runs (no games are played here). WSL python3, from anywhere.

    gauntlet_checks.py tsvs
        Every TSV in tsv/ against its references: new_decks.tsv is the 25-pairing layout of make_tsvs.py (seed base
        21,108,000,000); each table-deck file (var_v-lucario_*, var_v-suicune_*, var_v-weezing_*, id_<deck>_main)
        has exactly that deck's 7 table pairings, with each pairing's two decks in the table's order (the pairing ->
        (a, b) map read from the official scan's own per-game file, ../engine_identity_2026-09-25/kp3_500.jsonl),
        the version on the deck's own side, the other side the table's decks/research file, seed_first = 72,000,000
        + 10,000 x pairing; each Charizard Y file (var_l-charizardy, var_v-charizardy_*, id_charizardy_main) equals
        ../b2e_card_check_2026-09-26/b2e_pairings.tsv rows 40-47 in pairing, opponent, panel_file and seed_first,
        with the version as the held deck (id_charizardy_main: B2e's rows exactly). new_decks_run.tsv is exactly
        new_decks.tsv without the decks named in tsv/not_run.json. Every deck file named exists.

    gauntlet_checks.py rows <tsv> <seed base> <games> <pilot> <jsonl> [<tsv> <base> <games> <pilot> <jsonl> ...]
        Each run file against its TSV: exactly one game per (pairing, i), every TSV row and i < games, nothing else;
        every field (b2e_checks.FIELDS) present, moves a 16-hex-digit hash; seed = base + 10,000 x pairing + i =
        seed_first + i; first_seat = i % 2 (even i: the held deck in seat 0); a, b, a_file, b_file as the TSV row;
        bot_a = bot_b = pilot; first_deck_score consistent with winner_seat; findings and finding_examples
        consistent; the per-game findings summed equal the run's own .txt log's findings section. Prints RULE and
        CHECK findings per pairing and a last line "ROWS PASS ..." or "ROWS FAIL ...". Exit 1 on FAIL.
"""
import csv
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(RES, "..", ".."))
sys.path.insert(0, os.path.join(RES, "b2e_rows_2026-09-26"))
sys.dont_write_bytecode = True
import b2e_checks as B  # noqa: E402

TSV_DIR = os.path.join(HERE, "tsv")
OFFICIAL_KP3 = os.path.join(RES, "engine_identity_2026-09-25", "kp3_500.jsonl")
B2E_TSV = os.path.join(RES, "b2e_card_check_2026-09-26", "b2e_pairings.tsv")
PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
NEW_KEYS = ["scizor", "rayquaza", "altaria_greninja"]


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def table_map():
    m = {}
    with open(OFFICIAL_KP3, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                g = json.loads(line)
                if m.setdefault(g["pairing"], (g["a"], g["b"])) != (g["a"], g["b"]):
                    raise SystemExit(f"{OFFICIAL_KP3}: pairing {g['pairing']} names two deck pairs")
    if sorted(m) != list(range(28)):
        raise SystemExit(f"{OFFICIAL_KP3}: pairings {sorted(m)}")
    return m


def check_tsvs():
    bad = []
    names = sorted(n for n in os.listdir(TSV_DIR) if n.endswith(".tsv"))
    tm = table_map()
    b2e = {int(r["pairing"]): r for r in read_tsv(B2E_TSV)}
    with open(os.path.join(TSV_DIR, "not_run.json"), encoding="utf-8") as f:
        not_run = json.load(f)
    for name in names:
        rows = read_tsv(os.path.join(TSV_DIR, name))
        if name == "new_decks_run.tsv":
            full = {r["pairing"]: r for r in read_tsv(os.path.join(TSV_DIR, "new_decks.tsv"))}
            want = [p for p, r in full.items() if r["held_key"] not in not_run]
            if [r["pairing"] for r in rows] != want or any(r != full[r["pairing"]] for r in rows):
                bad.append(f"{name}: not new_decks.tsv without the decks in not_run.json ({sorted(not_run)})")
            continue
        for r in rows:
            for col in ("held_file", "panel_file"):
                if not os.path.isfile(os.path.join(REPO, r[col])):
                    bad.append(f"{name} pairing {r['pairing']}: {r[col]} does not exist")
            if int(r["seed_last"]) != int(r["seed_first"]) + 499 or int(r["sub_block_end"]) != int(r["seed_first"]) + 9_999:
                bad.append(f"{name} pairing {r['pairing']}: seed columns")
        if name == "new_decks.tsv":
            if [int(r["pairing"]) for r in rows] != list(range(25)):
                bad.append(f"{name}: pairings {[r['pairing'] for r in rows]}")
            for r in rows:
                p = int(r["pairing"])
                want = (NEW_KEYS[p // 8], PANEL[p % 8]) if p < 24 else ("rayquaza", "altaria_greninja")
                if (r["held_key"], r["opponent"]) != want or int(r["seed_first"]) != 21_108_000_000 + 10_000 * p:
                    bad.append(f"{name} pairing {p}: {r['held_key']} v {r['opponent']} seed {r['seed_first']}; want {want}")
                if r["block"] != ("coverage" if r["held_key"] == "scizor" else "scoreboard"):
                    bad.append(f"{name} pairing {p}: block {r['block']}")
            continue
        deck = rows[0]["deck"]
        version = rows[0]["version"]
        if deck == "charizardy":
            if [int(r["pairing"]) for r in rows] != list(range(40, 48)):
                bad.append(f"{name}: pairings {[r['pairing'] for r in rows]}")
            for r in rows:
                ref = b2e[int(r["pairing"])]
                for col in ("opponent", "panel_file", "seed_first", "seed_last", "sub_block_end"):
                    if r[col] != ref[col]:
                        bad.append(f"{name} pairing {r['pairing']}: {col} {r[col]!r}, B2e has {ref[col]!r}")
                if name == "id_charizardy_main.tsv":
                    for col in ("block", "held_key", "held_file"):
                        if r[col] != ref[col]:
                            bad.append(f"{name} pairing {r['pairing']}: {col} {r[col]!r}, B2e has {ref[col]!r}")
                elif r["held_key"] != version or r["variant_side"] != "a":
                    bad.append(f"{name} pairing {r['pairing']}: held {r['held_key']}, want {version}")
            continue
        want_ps = [p for p, (a, b) in sorted(tm.items()) if deck in (a, b)]
        if [int(r["pairing"]) for r in rows] != want_ps:
            bad.append(f"{name}: pairings {[r['pairing'] for r in rows]}, the table's {deck} pairings are {want_ps}")
        for r in rows:
            p = int(r["pairing"])
            a, b = tm[p]
            side = "a" if a == deck else "b"
            if r["variant_side"] != side:
                bad.append(f"{name} pairing {p}: variant_side {r['variant_side']}, want {side}")
            other_key, other_file = (r["opponent"], r["panel_file"]) if side == "a" else (r["held_key"], r["held_file"])
            own_key = r["held_key"] if side == "a" else r["opponent"]
            if other_key != (b if side == "a" else a):
                bad.append(f"{name} pairing {p}: the other deck is {other_key}, the table has {(a, b)}")
            if other_file != f"decks/research/{other_key}.txt":
                bad.append(f"{name} pairing {p}: other file {other_file}")
            if own_key != version:
                bad.append(f"{name} pairing {p}: version side key {own_key}, want {version}")
            if int(r["seed_first"]) != 72_000_000 + 10_000 * p:
                bad.append(f"{name} pairing {p}: seed_first {r['seed_first']}")
    for b in bad[:20]:
        print("  ", b)
    print(f"TSVS {'PASS' if not bad else 'FAIL'}: {len(names)} files checked ({', '.join(names)}); problems {len(bad)}")
    return not bad


def check_rows(specs, out=print):
    """specs: [(tsv path, base, games, pilot, jsonl path)]. Returns ok, findings {name: {pairing: Counter}}."""
    problems, findings = [], {}
    for tsv, base, games, pilot, path in specs:
        rows = {int(r["pairing"]): r for r in read_tsv(tsv)}
        bad, seen = [], set()
        per_pairing, first = defaultdict(Counter), defaultdict(dict)
        occ_total, games_total = Counter(), Counter()
        try:
            gs = B.load_games(path)
        except OSError as e:
            gs = []
            bad.append(f"cannot read: {e}")
        for g in gs:
            key = (g.get("pairing"), g.get("i"))
            absent = [x for x in B.FIELDS if x not in g]
            if absent:
                bad.append(f"pairing {key[0]} deal {key[1]}: no {', '.join(absent)}")
                continue
            if not (isinstance(g["moves"], str) and B.MOVES.fullmatch(g["moves"])):
                bad.append(f"pairing {key[0]} deal {key[1]}: moves {g['moves']!r}")
            if key in seen:
                bad.append(f"pairing {key[0]} deal {key[1]} twice")
                continue
            seen.add(key)
            p, i = key
            r = rows.get(p)
            if r is None:
                bad.append(f"pairing {p} not in {os.path.basename(tsv)}")
                continue
            if not (isinstance(i, int) and 0 <= i < games):
                bad.append(f"pairing {p}: deal {i!r} outside 0..{games - 1}")
                continue
            if g["seed"] != int(r["seed_first"]) + i or g["seed"] != base + 10_000 * p + i:
                bad.append(f"pairing {p} deal {i}: seed {g['seed']}")
            if g["first_seat"] != i % 2:
                bad.append(f"pairing {p} deal {i}: first_seat {g['first_seat']}")
            for field, want in (("a", r["held_key"]), ("b", r["opponent"]), ("a_file", r["held_file"]),
                                ("b_file", r["panel_file"]), ("bot_a", pilot), ("bot_b", pilot)):
                if g.get(field) != want:
                    bad.append(f"pairing {p} deal {i}: {field} {g.get(field)!r}, want {want!r}")
            w = g["winner_seat"]
            want_score = 0.5 if w == -1 else (1.0 if w == g["first_seat"] else 0.0)
            if w not in (-1, 0, 1) or g["first_deck_score"] != want_score:
                bad.append(f"pairing {p} deal {i}: winner_seat {w}, first_deck_score {g['first_deck_score']}")
            fs, fx = g.get("findings"), g.get("finding_examples")
            if fs is None:
                if fx is not None:
                    bad.append(f"pairing {p} deal {i}: finding_examples without findings")
                continue
            if not (isinstance(fs, dict) and fs and all(isinstance(n, int) and n > 0 for n in fs.values())):
                bad.append(f"pairing {p} deal {i}: findings {fs!r}")
                continue
            if not (isinstance(fx, dict) and set(fx) == set(fs)):
                bad.append(f"pairing {p} deal {i}: finding_examples does not match the finding codes")
                fx = {}
            for code, n in fs.items():
                per_pairing[p][code] += 1
                occ_total[code] += n
                games_total[code] += 1
                if code in fx and (code not in first[p] or i < first[p][code][0]):
                    first[p][code] = (i, g["seed"], fx[code])
        missing = [(p, i) for p in sorted(rows) for i in range(games) if (p, i) not in seen]
        if missing or len(gs) != len(rows) * games:
            bad.append(f"{len(gs):,} lines, {len(seen):,} distinct; want {len(rows) * games:,}; missing {len(missing)} "
                       f"(first {missing[:3]})")
        log = path[:-len(".jsonl")] + ".txt" if path.endswith(".jsonl") else None
        if log and os.path.exists(log):
            try:
                logged = B.log_findings(log)
                summed = {c: (occ_total[c], games_total[c]) for c in occ_total}
                if summed != logged:
                    bad.append(f"per-game findings {summed} differ from the log's {logged}")
            except ValueError as e:
                bad.append(f"log: {e}")
        else:
            bad.append(f"no log {log}")
        name = os.path.basename(path)
        out(f"{name} ({pilot}, {os.path.basename(tsv)}, base {base:,}, {games} deals): {len(gs):,} lines; problems {len(bad)}")
        for b in bad[:8]:
            out(f"   {b}")
        for p in sorted(per_pairing):
            for code, n in sorted(per_pairing[p].items()):
                ex = first[p].get(code)
                out(f"   {'RULE ' if code.startswith('RULE') else 'CHECK'} pairing {p} ({rows[p]['held_key']} v "
                    f"{rows[p]['opponent']}): {code}: {n} games" + (f" (e.g. deal {ex[0]}: {ex[2][:200]})" if ex else ""))
        problems += [f"{name}: {b}" for b in bad]
        findings[name] = per_pairing
    n_rule = sum(1 for f in findings.values() for c in f.values() if any(k.startswith("RULE") for k in c))
    if problems:
        out(f"ROWS FAIL: {len(problems)} problems, first: {problems[0]}")
    else:
        out(f"ROWS PASS: {len(specs)} run files hold exactly their TSVs' pairings x deals (seeds, seats, decks, "
            f"pilots); RULE findings in {n_rule} file-pairings")
    return not problems, findings


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "tsvs":
        sys.exit(0 if check_tsvs() else 1)
    if len(sys.argv) >= 7 and sys.argv[1] == "rows" and (len(sys.argv) - 2) % 5 == 0:
        a = sys.argv[2:]
        specs = [(a[k], int(a[k + 1]), int(a[k + 2]), a[k + 3], a[k + 4]) for k in range(0, len(a), 5)]
        ok, _ = check_rows(specs)
        sys.exit(0 if ok else 1)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
