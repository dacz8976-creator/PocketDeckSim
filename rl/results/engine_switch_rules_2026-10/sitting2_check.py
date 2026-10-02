#!/usr/bin/env python3
"""The checks sitting2.sh makes beside switch_check.py and sitting1_check.py (the rules switch, PLAN.md steps 8, 8b and
8c's hand-off). Standard library only; it imports sitting1_check.py's counter definitions and switch_check.py's readers
from its own folder (sitting2.sh runs private copies of the three side by side).

  pairs8 --repo R --out PAIRS.tsv [--seeds-out SEEDS.txt]
      Writes steps 8's and 8b's pairs file, in legality_scan's --pairs format with pairs_7c.tsv's columns (pairing block
      held_key held_file opponent panel_file seed_first seed_last sub_block_end; paths relative to the repository, as
      --root R reads them): pairings 0-31 are the four carrier lists (carriers/garchomp_meowth.txt, then the alternates
      togekiss_meowth, hisuian_goodra, houndoom_victini) each against the 8 panel lists decks/screen/opponents/t-*.txt in
      sorted order; 32-35 are 8b's scratch rows (fire_victini v psychic_confuse, fire_heatmor v meowth_carefree,
      t-vespiquen v meowth_carefree, l-sharpedo v meowth_carefree). seed_first = 23,100,000,000 + 10,000 x pairing;
      seed_last covers the most deals the step plays there (km3's 500 in step 8, 40 in 8b). --seeds-out writes the seed
      record: the block, each pairing's seed range per bot, and every deck file with the git blob id of its bytes.
      Prints a one-line summary. Exit 0, or 2 when a deck file or the panel is missing.
  touched --old F --new F --watch F --expect N --label L --step 8|8b --bot B --repo R --out-handoff F
      One bot's scan set of step 8 or 8b: the pinned old legality_scan, the new one and the watch build on the same deals.
      Each file must hold exactly N games, once each, keyed by (pairing, i), and the three the same deals. Every watch
      game's counters must have sitting1_check.py's shapes (as_exact). A game is CHANGED when the new game differs from
      the old one on any field the old file records (the union of its keys; "moves" differing is reported apart). A
      game whose watch row has every REPAIR counter at 0 (sitting1_check.py's 11, and vs_confused_choice_first null;
      the two off-gate counters do not count) must equal the old game, new and watch alike: one that differs is the
      halt "a changed game with every repair counter 0". Prints this set's lines for touched_<step>.txt (per pairing:
      games, identical, changed; the reach of each exact counter: games, ticks and changed games where it fired; one
      reach verdict per mechanic; the off-gate and superset counters and vs_confused_choice under its own name; the
      changed games no reach counter explains; the CONDITION 3 count: changed games where coin_full_prevention fired
      and no reach counter did, which PLAN.md:95 says must be identical, a pin-gate item reported, never a stop) and
      writes the changed games to --out-handoff (handoff_8c.tsv's columns, header first). Exit 0 pass; 1 a
      halt-worthy finding (a changed all-zero game, a count mismatch, a duplicate, different deals, a malformed
      counter); 2 a malformed or missing input.
  stepsum --step 8|8b --watch F [F ...] --rows F [F ...]
      A step's lines over both bots, from the watch scans and the hand-off rows: one reach verdict per mechanic (A,
      B(a), B(b)/Chase Order: "reached in N games (M ticks)" or "UNREACHED", a report: an unreached mechanic rests on
      its tests); for 8b, the off-gate discard counter in pairings 34 (t-vespiquen v meowth_carefree, Chase Order's
      discard) and 35 (l-sharpedo v meowth_carefree, the Wild Swing control): "met (N games)" or "NOT met" each, the
      refactor rule's condition 3 for the equivalence rows 13 and 22 that sitting 1's 7c carried here; the changed
      games and those with no reach counter; the CONDITION 3 count. Its last line starts "SUMMARY: " (the step's finish
      line carries it). Exit 0, or 2 on a malformed input.
  handoff --tsv OUT --md OUT --candidate C [--rows F ...] [--files F ...]
      Rebuilds handoff_8c.tsv (one header, then every --rows file's rows in the order given) and handoff_8c.md (what the
      cloud and Sonnet need to trace them: totals per step and per mechanic, the CONDITION 3 count, the engines, the
      tracer and probes, the classifier, the --files with their sha256, the rule). No timestamps, so a rebuild of the
      same inputs is the same bytes.
  trace-gate FILE
      Step 8c's gate before step 8: FILE (trace_load.txt; read as utf-8-sig) holds exactly one line "TRACE LOAD <n> <free
      text naming the cloud commit>" (the text must hold a commit id, 7-40 hex characters) and, when n > 50, a line
      starting "DUSTIN " (his words). Other lines (CLOUD8B <commit> <bot> <path>, read by sitting2.sh) are left alone.
      Prints the reading on its first line, then the marked lines "LOAD <n>" and "COMMIT <id>" once each when parsed
      (sitting2.sh reads exactly those, and checks the commit with git cat-file -e). Exit 0 when step 8 may run, 3 when
      it waits (missing, unparseable, or n > 50 with no DUSTIN line).
  cloud8b --new F --cloud F --bot km3|k3 --label L [--expect 160]
      The cloud's early-warning rows for 8b v this run's NEW-build rows (F = <S>_8b_new_<bot>.jsonl). The cloud's rows
      are first filtered to bot_a = the bot, pairings 32-35, i < 40 (a file of both bots, or of more deals, is fine);
      they must then be exactly this run's 160 deals, once each, else "not compared (owed)" with the reason. They are
      compared on the fields both files record, a_file and b_file left out (the cloud's own paths), and so every field
      this run's new file lacks (a watch file's counters): exit 0 equal; 1 a matched deal differs on a remaining field
      (a halt); 3 not compared (owed: unreadable, other deals, or the cloud's rows lack a core field).
"""
import argparse, glob, hashlib, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitting1_check import (EXACT_DICT, SUPERSET_INT, HEADS_INT, HEADS_FIRST, OFFGATE, REPAIR, BY_MECHANIC,  # noqa: E402
                            Malformed, as_exact, as_int, check_by_mechanic, short)

REL = "rl/results/engine_switch_rules_2026-10"
BASE_8 = 23_100_000_000
PANEL_DIR = "decks/screen/opponents"
CARRIERS = (f"{REL}/carriers/garchomp_meowth.txt", f"{REL}/carriers/alternates/togekiss_meowth.txt",
            f"{REL}/carriers/alternates/hisuian_goodra.txt", f"{REL}/carriers/alternates/houndoom_victini.txt")
SCR = f"{REL}/scratch_8b"
SHARPEDO = "decks/screen/panel_ladder_2026-09-26/l-sharpedo.txt"
ROWS_8B = ((f"{SCR}/fire_victini.txt", f"{SCR}/psychic_confuse.txt"),
           (f"{SCR}/fire_heatmor.txt", f"{SCR}/meowth_carefree.txt"),
           (f"{PANEL_DIR}/t-vespiquen.txt", f"{SCR}/meowth_carefree.txt"),
           (SHARPEDO, f"{SCR}/meowth_carefree.txt"))
DEALS = {"8": {"km3": 500, "k3": 250}, "8b": {"km3": 40, "k3": 40}}
FIRST_8B = 32
PAIRINGS_8B = (32, 33, 34, 35)
PATH_FIELDS = {"a_file", "b_file"}   # the cloud's paths differ by design (its own checkout's lists)
CLOUD_CORE = ("pairing", "i", "seed", "first_seat", "bot_a", "bot_b", "moves", "decisions", "winner_seat", "points")

# The reach counters (tightened_rule.py's; PLAN.md's mechanic check: only these explain a changed game on the board).
REACH_A = ("vs_confusion_first_built", "vs_confused_choice_offered", "vs_confused_choice_chosen")
REACH_BA = ("coin_cut_recorded",)
REACH_BB = ("coin_queued_offered", "coin_queued_offered_any")
REACH = REACH_A + REACH_BA + REACH_BB
FULL_PREV = "coin_full_prevention"   # exact, but the retain check's (PLAN.md step 2), not reach
GROUPS = (("A (Victory Star with a Confused attacker)", REACH_A),
          ("B(a) (the heads finite cut; coin_full_prevention is the retain check, not reach)", REACH_BA + (FULL_PREV,)),
          ("B(b) and Chase Order (the queued coin-path choice offered)", REACH_BB))
VERDICTS = (("A", "Victory Star with a Confused attacker", REACH_A),
            ("B(a)", "the heads finite cut on Bastiodon or Hisuian Goodra", REACH_BA),
            ("B(b)/Chase Order", "the queued coin-path choice offered", REACH_BB))
SUPER3 = SUPERSET_INT   # vs_confused_attack, coin_defender_attack, coin_queued_attack_damage: the superset counters
assert set(REACH + (FULL_PREV,)) == set(EXACT_DICT), "sitting1_check.py's exact counters changed"
assert HEADS_INT not in SUPER3
COND3 = "CONDITION 3 (PLAN.md:95: such games must be identical)"
RULING = "a ruling is needed before the pin"
DISCARD = OFFGATE[1]   # offgate_discard_then_damage
ROWS13_22 = ((34, "t-vespiquen v meowth_carefree, Chase Order's discard"),
             (35, "l-sharpedo v meowth_carefree, the Wild Swing control"))
MISSING = object()
HEADER = ("step", "bot", "pairing", "i", "seed", "held_file", "held_blob", "panel_file", "panel_blob", "old_moves",
          "new_moves", "moves_differ", "differing_fields", "old_winner", "new_winner", "old_points", "new_points",
          "exact_counters", "superset_counters", "vs_confused_choice", "offgate_counters", "no_reach_counter",
          "full_prevention_only")


def cond3_line(n, first=None):
    if not n:
        return f"{COND3}: 0 games"
    return (f"{COND3}: {n} games (changed, coin_full_prevention fired, no reach counter fired"
            + (f"; the first {first}" if first is not None else "") + f"); {RULING}")


def verdict(games, ticks):
    return f"reached in {games} games ({ticks} ticks)" if games else "UNREACHED"


def blob_id(path):
    """git's blob id of the file's bytes (git hash-object --no-filters; the repository's .gitattributes say * -text)."""
    data = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def cj(x):
    return json.dumps(x, separators=(",", ":"), sort_keys=True)


def panel(repo):
    opps = sorted(glob.glob(os.path.join(repo, PANEL_DIR, "*.txt")))
    names = [os.path.basename(o) for o in opps]
    if len(opps) != 8 or not all(n.startswith("t-") for n in names):
        raise Malformed(f"{PANEL_DIR} holds {names}, not the 8 panel lists t-*.txt")
    return [f"{PANEL_DIR}/{n}" for n in names]


def key_of(path):
    return os.path.splitext(os.path.basename(path))[0]


def rows8(repo):
    """(pairing, block, held_file, panel_file, deals) for pairings 0-35."""
    out, p = [], 0
    for c in CARRIERS:
        for o in panel(repo):
            out.append((p, "rules8", c, o, DEALS["8"]["km3"]))
            p += 1
    for held, opp in ROWS_8B:
        out.append((p, "rules8b", held, opp, DEALS["8b"]["km3"]))
        p += 1
    return out


def pairs8(a):
    rows = rows8(a.repo)
    files = sorted({x for r in rows for x in (r[2], r[3])})
    missing = [f for f in files if not os.path.isfile(os.path.join(a.repo, f))]
    if missing:
        raise Malformed(f"deck files missing: {', '.join(missing)}")
    head = ["pairing", "block", "held_key", "held_file", "opponent", "panel_file", "seed_first", "seed_last",
            "sub_block_end"]
    lines = ["\t".join(head)]
    for p, block, held, opp, deals in rows:
        s = BASE_8 + 10_000 * p
        lines.append("\t".join(str(x) for x in (p, block, key_of(held), held, key_of(opp).removeprefix("t-"), opp, s,
                                                 s + deals - 1, s + 9_999)))
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    last = rows[-1][0]
    if a.seeds_out:
        sl = ["The rules switch's step 8 and 8b seeds (sitting2.sh, step 8-seeds), recorded and committed before any step 8 "
              "or 8b game.",
              "Block: 23,100,000,000 + pairing x 10,000 + i (PLAN.md step 8; START_HERE's seed table). Step 8: pairings "
              "0-31; step 8b: 32-35; sitting 1's step 7c: 40-71 (pairs_7c.tsv). Same bot in both seats.",
              "Pairings (pairs_8.tsv; held list v opponent; seed ranges by bot):"]
        for p, block, held, opp, deals in rows:
            s = BASE_8 + 10_000 * p
            st = "8" if block == "rules8" else "8b"
            rng = "; ".join(f"{b} i < {n}: {s:,} - {s + n - 1:,}" for b, n in DEALS[st].items())
            sl.append(f"  {p} (step {st}): {held} v {opp}: {rng}")
        sl.append("Deck files (repository path, git blob id of the bytes on disk):")
        sl += [f"  {f} {blob_id(os.path.join(a.repo, f))}" for f in files]
        with open(a.seeds_out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(sl) + "\n")
    print(f"pairs8: pairings 0-{last} ({len(rows)} rows: the 4 carrier lists x the 8 panel lists, 0-31; 8b's 4 scratch "
          f"rows, {FIRST_8B}-{last}); seeds 23,100,000,000 + pairing x 10,000 + i: step 8 {BASE_8:,} - "
          f"{BASE_8 + 10_000 * 31 + 499:,} (km3 i < 500, k3 i < 250), 8b {BASE_8 + 10_000 * FIRST_8B:,} - "
          f"{BASE_8 + 10_000 * last + 39:,} (i < 40); {len(files)} deck files")
    return 0


def read_set(path):
    """{(pairing, i): game}, the deals seen twice, and the number of games."""
    out, dup, n = {}, [], 0
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.strip():
                continue
            g = json.loads(ln)
            k = (g["pairing"], g["i"])
            if k in out:
                dup.append(k)
            out[k] = g
            n += 1
    return out, dup, n


def counters_of(w):
    """The watch game's counters, shape-checked as sitting1_check.py checks them (Malformed otherwise)."""
    ex = {k: as_exact(w, k)[0] for k in EXACT_DICT}
    og = {k: as_exact(w, k)[0] for k in OFFGATE}
    check_by_mechanic(w)
    si = {k: as_int(w, k) for k in SUPERSET_INT + (HEADS_INT,)}
    if HEADS_FIRST not in w:
        raise Malformed(f"game {(w.get('pairing'), w.get('i'))}: no {HEADS_FIRST}")
    hf = w[HEADS_FIRST]
    if hf is not None and (not isinstance(hf, int) or isinstance(hf, bool)):
        raise Malformed(f"game {(w.get('pairing'), w.get('i'))}: {HEADS_FIRST} is {hf!r}, not null or a tick")
    return ex, og, si, hf


def touched(a):
    sets = {}
    for nm, path in (("old", a.old), ("new", a.new), ("watch", a.watch)):
        sets[nm] = read_set(path)
    old, new, watch = (sets[x][0] for x in ("old", "new", "watch"))
    issues = []
    for nm, (games, dup, n) in sets.items():
        if dup:
            issues.append(f"the {nm} file holds {len(dup)} deals twice (first {dup[0]})")
        if n != a.expect or len(games) != a.expect:
            issues.append(f"the {nm} file holds {n} games ({len(games)} deals), expected {a.expect}")
    if not set(old) == set(new) == set(watch):
        issues.append("the three files do not hold the same deals (old-only "
                      f"{len(set(old) - set(new) - set(watch))}, new-only {len(set(new) - set(old))}, "
                      f"watch-only {len(set(watch) - set(old))})")
    fields = sorted(set().union(*(g.keys() for g in old.values()))) if old else []
    keys = sorted(set(old) & set(new) & set(watch))
    per, reach, sup, zero_bad, bad_shape, out_rows, cond3 = {}, {}, {}, [], [], [], []
    for k in EXACT_DICT + OFFGATE:
        reach[k] = [0, 0, 0]   # games where it fired, ticks, changed games where it fired
    for k in SUPER3 + (HEADS_INT, HEADS_FIRST):
        sup[k] = [0, 0]        # games above 0 (non-null), sum
    groups = {g: [0, 0] for g, _, _ in VERDICTS}   # games where any of the group's reach counters fired, their ticks
    blobs = {}

    def blob(p):
        if p not in blobs:
            q = os.path.join(a.repo, p) if p else ""
            blobs[p] = blob_id(q) if p and os.path.isfile(q) else "missing"
        return blobs[p]

    changed_n = moves_n = no_reach = fp_only = 0
    for k in keys:
        o, n_, w = old[k], new[k], watch[k]
        try:
            ex, og, si, hf = counters_of(w)
        except Malformed as e:
            bad_shape.append(str(e))
            continue
        all_zero = not any(ex.values()) and not any(si.values()) and hf is None
        d_new = [f for f in fields if n_.get(f, MISSING) != o.get(f, MISSING)]
        d_watch = [f for f in fields if w.get(f, MISSING) != o.get(f, MISSING)]
        changed = bool(d_new)
        mv = n_.get("moves") != o.get("moves")
        if all_zero and (d_new or d_watch):
            zero_bad.append((k, d_new or d_watch))
        row = per.setdefault(k[0], {"a": n_.get("a"), "b": n_.get("b"), "games": 0, "identical": 0, "changed": 0,
                                    "moves": 0})
        row["games"] += 1
        row["changed" if changed else "identical"] += 1
        row["moves"] += mv
        for c, v in list(ex.items()) + list(og.items()):
            if v:
                reach[c][0] += 1
                reach[c][1] += v
                reach[c][2] += changed
        for c, v in si.items():
            if v:
                sup[c][0] += 1
                sup[c][1] += v
        if hf is not None:
            sup[HEADS_FIRST][0] += 1
        for g, _, names in VERDICTS:
            t = sum(ex[c] for c in names)
            if t:
                groups[g][0] += 1
                groups[g][1] += t
        if not changed:
            continue
        changed_n += 1
        moves_n += mv
        fired = [c for c in REACH if ex[c]]
        no_reach += not fired
        if not fired and ex[FULL_PREV]:
            cond3.append(k)
        out_rows.append((a.step, a.bot, k[0], k[1], n_.get("seed"), n_.get("a_file") or "", blob(n_.get("a_file")),
                         n_.get("b_file") or "", blob(n_.get("b_file")), o.get("moves"), n_.get("moves"),
                         "yes" if mv else "no", ",".join(d_new), o.get("winner_seat"), n_.get("winner_seat"),
                         cj(o.get("points")), cj(n_.get("points")),
                         cj({c: w[c]["ticks"] for c in EXACT_DICT if ex[c]}),
                         cj({c: si[c] for c in SUPER3 if si[c]}),
                         cj({"n": si[HEADS_INT], "first": hf} if si[HEADS_INT] or hf is not None else {}),
                         cj({**{c: w[c]["ticks"] for c in OFFGATE if og[c]},
                             **({BY_MECHANIC: w[BY_MECHANIC]} if w.get(BY_MECHANIC) else {})}),
                         "no" if fired else "yes", "yes" if (not fired and ex[FULL_PREV]) else "no"))
    with open(a.out_handoff, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(HEADER) + "\n")
        for r in out_rows:
            f.write("\t".join("" if x is None else str(x) for x in r) + "\n")
    lab = a.label
    ident = sum(r["identical"] for r in per.values())
    lines = [f"{lab}: {short(a.old)} / {short(a.new)} / {short(a.watch)}: {len(keys)} deals in all three"
             f" (expected {a.expect} each); {ident} identical to the old game on every field the old file records "
             f"({len(fields)} fields: {', '.join(fields)}), {changed_n} changed ({moves_n} with different moves)"]
    for p in sorted(per):
        r = per[p]
        lines.append(f"  pairing {p} {r['a']} v {r['b']}: {r['games']} games, {r['identical']} identical, "
                     f"{r['changed']} changed ({r['moves']} with different moves)")
    for title, names in GROUPS:
        lines.append(f"  reach {title}: " + "; ".join(
            f"{c} in {reach[c][0]} games ({reach[c][1]} ticks; {reach[c][2]} of them changed)" for c in names))
    for g, what, names in VERDICTS:
        lines.append(f"  reach verdict {g} ({what}; {', '.join(names)}): {verdict(*groups[g])}"
                     + ("" if groups[g][0] else " (a report, not a stop: an unreached mechanic rests on its tests)"))
    lines.append("  off-gate (evidence for B's rewritten lines, never reach): " + "; ".join(
        f"{c} in {reach[c][0]} games ({reach[c][1]} ticks)" for c in OFFGATE))
    lines.append("  superset (never reach; they back 'all counters 0 means identical'): " + "; ".join(
        f"{c} above 0 in {sup[c][0]} games (sum {sup[c][1]})" for c in SUPER3))
    lines.append(f"  {HEADS_INT} (a Confusion heads that led to a Victory Star choice; a plain count, not reach): above 0 "
                 f"in {sup[HEADS_INT][0]} games (sum {sup[HEADS_INT][1]}); {HEADS_FIRST} set in {sup[HEADS_FIRST][0]} games")
    lines.append(f"  changed games with no reach counter anywhere: {no_reach} of {changed_n} (8c places every changed "
                 f"game's first difference, these included; on the board without a counter is UNEXPLAINED). Rows: "
                 f"{short(a.out_handoff)}")
    lines.append("  " + cond3_line(len(cond3), cond3[0] if cond3 else None))
    if zero_bad:
        k, d = zero_bad[0]
        issues.append(f"{len(zero_bad)} changed games with every repair counter 0 ({len(REPAIR)} counters and "
                      f"{HEADS_FIRST} null), the first {k} on {', '.join(d)}")
    if bad_shape:
        issues.append(f"{len(bad_shape)} watch games with a malformed counter, the first: {bad_shape[0]}")
    ok = not issues
    lines.append(f"{lab}: {'PASS' if ok else 'does not pass'}: {len(keys)} deals; {changed_n} changed "
                 f"({no_reach} with no reach counter); changed games with every repair counter 0: {len(zero_bad)}; "
                 f"{COND3}: {len(cond3)} games" + ("" if ok else "; " + "; ".join(issues)))
    print("\n".join(lines))
    return 0 if ok else 1


def read_rows(paths):
    rows = []
    for path in paths or []:
        with open(path, encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f if ln.strip()]
        if not lines or tuple(lines[0].split("\t")) != HEADER:
            raise Malformed(f"{short(path)} does not start with the hand-off header")
        for ln in lines[1:]:
            r = ln.split("\t")
            if len(r) != len(HEADER):
                raise Malformed(f"{short(path)}: a row with {len(r)} fields, not {len(HEADER)}")
            rows.append(dict(zip(HEADER, r)))
    return rows


def stepsum(a):
    groups = {g: [0, 0] for g, _, _ in VERDICTS}
    disc = {p: {} for p, _ in ROWS13_22}   # pairing: {bot: [unchanged games where the discard fired, unchanged games]}
    rows = read_rows(a.rows)
    changed_keys = {(r["bot"], int(r["pairing"]), int(r["i"])) for r in rows}
    deals = 0
    for path in a.watch:
        bot = None
        with open(path, encoding="utf-8") as f:
            for ln in f:
                if not ln.strip():
                    continue
                w = json.loads(ln)
                deals += 1
                bot = w.get("bot_a")
                ex = {k: as_exact(w, k)[0] for k in EXACT_DICT}
                for g, _, names in VERDICTS:
                    t = sum(ex[c] for c in names)
                    if t:
                        groups[g][0] += 1
                        groups[g][1] += t
                if a.step == "8b" and w["pairing"] in disc:
                    d = disc[w["pairing"]].setdefault(bot, [0, 0])
                    fired = bool(as_exact(w, DISCARD)[0])
                    if (bot, w["pairing"], w["i"]) not in changed_keys:   # only identical games prove the rewritten lines
                        d[1] += 1
                        d[0] += fired
    changed = len(rows)
    no_reach = sum(r["no_reach_counter"] == "yes" for r in rows)
    c3 = [r for r in rows if r["full_prevention_only"] == "yes"]
    lines, summ = [], []
    for g, what, names in VERDICTS:
        v = verdict(*groups[g])
        lines.append(f"{a.step} (all bots): reach verdict {g} ({what}): {v}"
                     + ("" if groups[g][0] else " (a report, not a stop: an unreached mechanic rests on its tests)"))
        summ.append(f"{g} {v}")
    if a.step == "8b":
        parts = []
        for p, what in ROWS13_22:
            by = disc[p]
            n = sum(x[0] for x in by.values())
            seen = sum(x[1] for x in by.values())
            v = f"met ({n} games)" if n else "NOT met"
            parts.append(f"pairing {p} ({what}): {v}")
            lines.append(f"8b: the refactor rule's condition 3 for rows 13 and 22 ({DISCARD} in identical games only; "
                         f"sitting 1's 7c carried it here): pairing {p} ({what}): {v}, of {seen} unchanged games ("
                         + ", ".join(f"{b} {x[0]} of {x[1]}" for b, x in sorted(by.items())) + "; changed games excluded)")
        summ.append("rows 13 and 22: " + "; ".join(parts))
    lines.append(f"{a.step}: changed games: {changed} of {deals} deals, {no_reach} with no reach counter anywhere (8c "
                 f"places every changed game's first difference)")
    first = f"({c3[0]['pairing']}, {c3[0]['i']}) {c3[0]['bot']}" if c3 else None
    lines.append(f"{a.step}: {cond3_line(len(c3), first)}")
    summ.append(f"changed {changed} of {deals} deals ({no_reach} with no reach counter)")
    summ.append(cond3_line(len(c3)))
    lines.append("SUMMARY: " + "; ".join(summ))
    print("\n".join(lines))
    return 0


ENGINES = """- **old**: the official engine, main-d363ba8 (engine/ tree 9c84fef), the pinned programs `rl/engine-2026-09-30/`
  (legality_scan sha256 fe244ecd92e159706c1ee0fc9933037e87d885c4a1cb9b4f37ee7adf96067be1).
- **new**: the candidate {c} (main c9f4224 + R f8cfa9c; engine/ = R's tree 38af8b0), built by sitting 1:
  `programs.sha256` (the plain legality_scan) and `watch.sha256` (the watch build, both F5 instrument scripts)."""
TRACER = """`vs_trace.rs` at the candidate, `{c7}:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_trace.rs`,
built as an example in a scratch copy of each engine. It sets a game up as legality_scan's `--pairs` row does
(seed = seed base + pairing x 10,000 + i; even i puts the first-named deck in seat 0), with the same bot in both seats:
`vs_trace --a <held_file> --b <panel_file> --seed-base 23100000000 --pairing <P> --bot <bot> --deals <i>,<i>,...`
- **Pass each row's own bot** (its `bot` column: km3 or k3). vs_trace defaults to kog3, and so do `coin_probe.rs`
  and `coin_lookahead.py`: a trace or probe under the default bot is another game.
- **Check each trace's last line** (legality_scan's move fingerprint) against the row's old_moves (the old engine's
  trace) and new_moves (the candidate's) before reading anything else from it: a trace that does not reproduce its
  game explains nothing.
- **The probes:** `vs_probe.rs` for A, at the candidate,
  `{c7}:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_probe.rs`; `coin_probe.rs` and `coin_lookahead.py`
  for B, in `rl/results/engine_switch_rules_2026-10/` at the candidate (again with the row's bot).
- **Rows with moves_differ = no** (the games differ only in points, winner or another field, with the same moves):
  their two traces can agree tick for tick, and then `first_difference` returns kind "length" (no tick to look at),
  which the rule reads as UNEXPLAINED. Look at those rows' state hashes and final boards by hand."""
CLASSIFIER = """`tightened_rule.py` at the candidate, `{c7}:rl/results/engine_switch_rules_2026-10/tightened_rule.py`
(first_difference, counter_hits; the coordinator accepted its reading, Oct 1). Its loaders key games by i alone
(`load_trace`: one game per i), so trace one pairing per folder, or adapt the loader to (pairing, i)."""
RULE = """PLAN.md's mechanic check, as `tightened_rule.py` applies it: a changed game is explained on the board only when an
exact reach counter (A: vs_confusion_first_built, vs_confused_choice_offered, vs_confused_choice_chosen; B(a):
coin_cut_recorded; B(b) and Chase Order: coin_queued_offered, coin_queued_offered_any) fired at a tick at or before the
first differing tick k, in k's turn or at the cause tick. A firing after k, or in an earlier turn other than the cause
tick, explains nothing. A board difference (offered moves, a forced move, the state after identical moves, a prefix)
with no such counter is UNEXPLAINED and stops the switch. A lookahead difference (the same state and offered moves, a
different choice) needs both halves: the code gate, and a probe (vs_probe.rs for A; coin_probe.rs and coin_lookahead.py
for B) showing the gate's condition within the mover's search depth at k. A trace that needs a judgment call goes to
Dustin, and the pin waits for his word. coin_full_prevention, vs_confused_choice and the superset counters never explain
a game. The refactor rule's condition 3 (PLAN.md:95) says a game where coin_full_prevention fired and no reach counter
did must be identical: every such changed game is counted as CONDITION 3 above, and a ruling is needed before the pin.
The runner already stopped on any changed game whose repair counters all read 0."""


def handoff(a):
    rows = read_rows(a.rows)
    with open(a.tsv, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(HEADER) + "\n")
        for r in rows:
            f.write("\t".join(r[h] for h in HEADER) + "\n")
    tot = {}
    for r in rows:
        t = tot.setdefault((r["step"], r["bot"]), {"changed": 0, "moves": 0, "no_reach": 0, "fp_only": 0,
                                                    "mech": {c: 0 for c in EXACT_DICT}})
        t["changed"] += 1
        t["moves"] += r["moves_differ"] == "yes"
        t["no_reach"] += r["no_reach_counter"] == "yes"
        t["fp_only"] += r["full_prevention_only"] == "yes"
        for c in json.loads(r["exact_counters"]):
            t["mech"][c] += 1
    c7 = a.candidate[:7]
    c3 = sum(t["fp_only"] for t in tot.values())
    md = ["# The hand-off for step 8c: the changed games of steps 8b and 8",
          "",
          "Rebuilt by sitting2.sh (`sitting2_check.py handoff`) at every checkpoint from the per-scan-set rows "
          "(`handoff_<step>_<bot>.tsv`); every changed game is a row of `handoff_8c.tsv`. Nothing here is a verdict: "
          "8c (the cloud's traces, Sonnet reading every hand trace) decides each row by the rule below.",
          "",
          f"**{cond3_line(c3)}.**" if c3 else f"{cond3_line(0)}.",
          "",
          "## Totals",
          "",
          "Every changed game needs its first difference placed (tick k, its turn, the cause tick), not only the rows "
          "with no reach counter: a counter that fired after k, or in an earlier turn other than the cause tick, "
          "explains nothing.",
          "",
          "| step | bot | changed games (each traced to its first difference) | with different moves | no reach counter "
          "anywhere | CONDITION 3: coin_full_prevention fired, no reach counter |",
          "|---|---|---:|---:|---:|---:|"]
    for (st, bot), t in sorted(tot.items(), key=lambda kv: (kv[0][0] != "8b", kv[0][1] != "km3")):
        md.append(f"| {st} | {bot} | {t['changed']} | {t['moves']} | {t['no_reach']} | {t['fp_only']} |")
    if not tot:
        md.append("| - | - | 0 | 0 | 0 | 0 |")
    md += ["", "Changed games in which each exact counter fired (anywhere in the game; 8c places it against the first "
           "difference):", "", "| step | bot | " + " | ".join(EXACT_DICT) + " |",
           "|---|---|" + "---:|" * len(EXACT_DICT)]
    for (st, bot), t in sorted(tot.items(), key=lambda kv: (kv[0][0] != "8b", kv[0][1] != "km3")):
        md.append(f"| {st} | {bot} | " + " | ".join(str(t["mech"][c]) for c in EXACT_DICT) + " |")
    md += ["", "## The engines", "", ENGINES.format(c=a.candidate), "",
           "## The tracer and the probes", "", TRACER.format(c7=c7), "",
           "## The classifier", "", CLASSIFIER.format(c7=c7), "",
           "## The files", "",
           "The rows: `handoff_8c.tsv` (columns: " + ", ".join(HEADER) + "). exact_counters and offgate_counters are "
           "compact JSON with every firing tick of each counter that fired; superset_counters holds the three superset "
           "counts; vs_confused_choice holds that count and vs_confused_choice_first (its own name: not a superset "
           "counter, not reach). no_reach_counter is yes when none of the six reach counters fired; "
           "full_prevention_only is yes for a CONDITION 3 row. The games (legality_scan --games-out, sha256):", ""]
    for p in a.files or []:
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        n = sum(1 for ln in open(p, encoding="utf-8") if ln.strip())
        md.append(f"- `{short(p)}`: {n} games, sha256 {h}")
    md += ["", "Seeds: 23,100,000,000 + pairing x 10,000 + i (`pairs_8.tsv`, `seeds_8.txt`); held list in seat 0 for "
           "even i.", "", "## The rule", "", RULE, ""]
    with open(a.md, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md))
    print(f"handoff: {len(rows)} changed games from {len(a.rows or [])} row files; "
          + "; ".join(f"{st} {bot}: {t['changed']} changed, {t['no_reach']} with no reach counter"
                      for (st, bot), t in sorted(tot.items())) + f"; {cond3_line(c3)}")
    return 0


def trace_gate(a):
    marks = []   # the marked lines the shell reads: "LOAD <n>" and "COMMIT <id>", each once, after the reading

    def wait(why):
        print("\n".join([f"trace load: step 8 waits: {why}"] + marks))
        return 3
    if not os.path.isfile(a.file):
        return wait(f"{os.path.basename(a.file)} is not here")
    try:
        with open(a.file, encoding="utf-8-sig") as f:
            lines = [ln.rstrip("\r\n") for ln in f]
    except (OSError, UnicodeDecodeError) as e:
        return wait(f"{os.path.basename(a.file)} cannot be read ({e!r})")
    tl = [ln for ln in lines if ln.startswith("TRACE LOAD")]
    if len(tl) != 1:
        return wait(f"{len(tl)} lines start with 'TRACE LOAD', not 1")
    m = re.fullmatch(r"TRACE LOAD (\d+) (.*\S.*)", tl[0])
    if not m:
        return wait(f"the line {tl[0]!r} is not 'TRACE LOAD <n> <free text naming the cloud commit>'")
    n, text = int(m.group(1)), m.group(2).strip()
    marks.append(f"LOAD {n}")
    cm = re.search(r"(?<![0-9a-fA-F])([0-9a-f]{7,40})(?![0-9a-fA-F])", text)
    if not cm:
        return wait(f"its free text names no commit (7-40 hex characters): {text!r}")
    marks.append(f"COMMIT {cm.group(1)}")
    dustin = [ln for ln in lines if ln.startswith("DUSTIN ") and ln[7:].strip()]
    if n > 50 and not dustin:
        return wait(f"the trace load is {n} (more than about 50 hand traces), and no DUSTIN line gives his word")
    print("\n".join([f"trace load: {n} ({text})" + (f"; Dustin: {dustin[0][7:].strip()}" if dustin else "")
                     + "; step 8 may run"] + marks))
    return 0


def cloud8b(a):
    """The cloud's 8b rows v this run's NEW-build rows for one bot. Exit 0 equal; 1 a matched deal differs (a halt); 3
    not compared (owed), with the reason."""
    def owed(why):
        print(f"{a.label}: not compared (owed): {why}")
        return 3
    new, ndup, nn = read_set(a.new)
    if ndup or nn != a.expect or len(new) != a.expect:
        return owed(f"this run's file holds {nn} games ({len(new)} deals, {len(ndup)} twice), not {a.expect}")
    want = set(new)
    cloud, kept_rows, other = {}, 0, 0
    try:
        with open(a.cloud, encoding="utf-8-sig") as f:
            for ln in f:
                if not ln.strip():
                    continue
                g = json.loads(ln)
                if not isinstance(g, dict) or "pairing" not in g or "i" not in g:
                    return owed("a row with no pairing or i")
                if g.get("bot_a") != a.bot or g["pairing"] not in PAIRINGS_8B or not (0 <= g["i"] < DEALS["8b"][a.bot]):
                    other += 1
                    continue
                k = (g["pairing"], g["i"])
                if k in cloud:
                    return owed(f"the cloud's rows hold deal {k} twice for {a.bot}")
                cloud[k] = g
                kept_rows += 1
    except (OSError, ValueError, TypeError) as e:
        return owed(f"the cloud's file cannot be read ({e!r})")
    if set(cloud) != want:
        return owed(f"after the filter (bot_a {a.bot}, pairings 32-35, i < 40) the cloud's rows hold {len(cloud)} deals, "
                    f"{len(want - set(cloud))} of this run's missing and {len(set(cloud) - want)} others "
                    f"({other} rows of other bots or deals left out)")
    nf = set().union(*(g.keys() for g in new.values()))
    cf = set().union(*(g.keys() for g in cloud.values()))
    fields = sorted((nf & cf) - PATH_FIELDS)
    lacking = sorted(nf - cf - PATH_FIELDS)
    if not set(CLOUD_CORE) <= set(fields):
        return owed(f"the cloud's rows lack {', '.join(sorted(set(CLOUD_CORE) - set(fields)))}")
    bad = [(k, [f for f in fields if new[k].get(f, MISSING) != cloud[k].get(f, MISSING)]) for k in sorted(want)]
    bad = [(k, d) for k, d in bad if d]
    head = (f"{a.label}: {len(want) - len(bad)} of {len(want)} deals equal on the {len(fields)} fields both record "
            f"({', '.join(fields)}; a_file and b_file left out"
            + (f"; the cloud's rows lack {', '.join(lacking)}" if lacking else "")
            + (f"; {len(cf - nf)} fields only the cloud records, left out" if cf - nf else "")
            + f"; {other} cloud rows of other bots or deals left out)")
    if bad:
        print(head + f"; DIFFERS: {len(bad)} deals, first {bad[0][0]} on {', '.join(bad[0][1])}")
        return 1
    print(head)
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pairs8"); p.add_argument("--repo", required=True); p.add_argument("--out", required=True)
    p.add_argument("--seeds-out")
    t = sub.add_parser("touched")
    for x in ("--old", "--new", "--watch", "--label", "--bot", "--repo", "--out-handoff"):
        t.add_argument(x, required=True)
    t.add_argument("--expect", type=int, required=True); t.add_argument("--step", choices=("8", "8b"), required=True)
    h = sub.add_parser("handoff"); h.add_argument("--tsv", required=True); h.add_argument("--md", required=True)
    h.add_argument("--candidate", required=True); h.add_argument("--rows", nargs="*"); h.add_argument("--files", nargs="*")
    g = sub.add_parser("trace-gate"); g.add_argument("file")
    s = sub.add_parser("stepsum"); s.add_argument("--step", choices=("8", "8b"), required=True)
    s.add_argument("--watch", nargs="+", required=True); s.add_argument("--rows", nargs="+", required=True)
    c = sub.add_parser("cloud8b")
    for x in ("--new", "--cloud", "--label"):
        c.add_argument(x, required=True)
    c.add_argument("--bot", choices=("km3", "k3"), required=True); c.add_argument("--expect", type=int, default=160)
    a = ap.parse_args()
    fn = {"pairs8": pairs8, "touched": touched, "handoff": handoff, "trace-gate": trace_gate, "stepsum": stepsum,
          "cloud8b": cloud8b}[a.cmd]
    try:
        rc = fn(a)
    except (OSError, ValueError, KeyError, TypeError, Malformed) as e:
        print(f"{a.cmd}: malformed or missing input: {e!r}")
        sys.exit(3 if a.cmd in ("trace-gate", "cloud8b") else 2)
    sys.exit(rc)


if __name__ == "__main__":
    main()
