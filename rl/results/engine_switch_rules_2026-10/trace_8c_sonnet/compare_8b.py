#!/usr/bin/env python3
"""Row-for-row comparison of this run's step 8b rows (verdicts.tsv) against the cloud's classify_output.txt
(early_warning_8b, commit 3a107f4). Compared per game (bot, pairing, i): the first-difference tick, its kind, its turn and the verdict.
Any disagreement, or a game one side lacks, is a STOP (exit 1).
Usage: compare_8b.py <verdicts.tsv> <cloud classify_output.txt> [out file]"""
import csv, re, sys

verdicts, cloud_txt = sys.argv[1], sys.argv[2]
out = open(sys.argv[3], "w", encoding="utf-8") if len(sys.argv) > 3 else None


def say(s):
    print(s)
    if out:
        out.write(s + "\n")


cloud, bot, pairing = {}, None, None
for ln in open(cloud_txt, encoding="utf-8"):
    m = re.match(r"=== (\S+)", ln)
    if m:
        bot = m.group(1)
        continue
    m = re.match(r"pairing (\d+),", ln)
    if m:
        pairing = m.group(1)
        continue
    m = re.match(r"\s+i =\s*(\d+): first difference at tick (\d+) \(turn (\d+); (\w+):.*=> (.+?)\s*$", ln)
    if m:
        cloud[(bot, pairing, m.group(1))] = {"k": m.group(2), "turn": m.group(3), "kind": m.group(4), "verdict": m.group(5)}

mine = {}
for r in csv.DictReader(open(verdicts, encoding="utf-8"), delimiter="\t"):
    if r["step"] == "8b":
        mine[(r["bot"], r["pairing"], r["i"])] = {"k": r["k"], "turn": r["turn"], "kind": r["kind"], "verdict": r["verdict"]}

bad = []
for key in sorted(set(cloud) | set(mine), key=lambda t: (t[0], int(t[1]), int(t[2]))):
    c, m = cloud.get(key), mine.get(key)
    if c is None or m is None:
        bad.append(f"{key}: only in {'mine' if c is None else 'the cloud'}'s run")
    elif c != m:
        bad.append(f"{key}: cloud {c} v mine {m}")
say(f"cloud's 8b games: {len(cloud)}; this run's 8b rows: {len(mine)}; compared on tick, kind, turn and verdict")
if bad:
    say(f"STOP: {len(bad)} disagreement(s)")
    for b in bad:
        say("  " + b)
    sys.exit(1)
say(f"AGREE row for row: all {len(mine)} games match on tick, kind, turn and verdict")
