#!/usr/bin/env python3
"""Scans lib/deckgym-database.json (origin/main) for the card texts the round-2 package turns on, to check the audit's card lists are complete.
Run from the repository root."""
import json, re, subprocess
raw = subprocess.run(["git", "show", "origin/main:lib/deckgym-database.json"], capture_output=True, text=True, encoding="utf-8").stdout
db = json.loads(raw)
cards = db if isinstance(db, list) else db.get("cards", db)
rows = list(cards.values()) if isinstance(cards, dict) else cards
PATS = {
    "block coin (attack text)": r"tries to use an attack, your opponent flips a coin",
    "coin Ability on damage": r"If any damage is done to this Pok.mon by attacks, flip a coin",
    "Guts": r"would be Knocked Out by damage from an attack, flip a coin",
    "Perish Body": r"Knocked Out by damage from an attack from your opponent.s Pok.mon, flip a coin",
    "Trap Territory": r"Retreat Cost is 1 more",
    "Luxury Coin": r"coins for an effect of your Trainer cards",
    "Will": r"first coin flip will definitely be heads",
    "copies an attack (Ditto-like)": r"use it as this attack",
}
hits = {k: {} for k in PATS}
for c in rows:
    f = c.get("Pokemon") or c.get("Trainer") or c
    texts = []
    if f.get("ability"):
        texts.append(f["ability"].get("effect") or "")
    for a in f.get("attacks", []) or []:
        texts.append(a.get("effect") or "")
    texts.append(f.get("effect") or "")
    for k, pat in PATS.items():
        if any(re.search(pat, t or "", re.I) for t in texts):
            hits[k].setdefault(f.get("name"), []).append(f.get("id"))
for k, v in hits.items():
    print(f"== {k}: {sum(len(x) for x in v.values())} printings of {len(v)} cards")
    for name, ids in sorted(v.items()):
        print(f"   {name}: {', '.join(sorted(ids))}")
