# `lib/` — run these, don't remember rules

## Why this directory exists

The same defect shipped **three times in two sessions**, each time followed by a new prose
"standing rule" in `CURRENT.md` / `HANDOFF.md`. By 2026-08-16 those two files contained **43**
such warnings and the bug happened anyway:

| § | the bug | what it did |
|---|---|---|
| §37-R | accented card name never matched | a card silently vanished |
| §101 | filtered card lines by the name prefix `Pok` | every `Poké Ball` / `Pokémon Center Lady` vanished |
| §102 | keyed a decklist by NAME, not `(name, id)` | one copy of a split-print line vanished |

**One shared signature: a card silently disappeared during parsing.** And none was caught, because
every check validated the **output** ("does my deck have 20 cards?") — which greedy-fill guaranteed
regardless. Nothing validated the **input** or the **shape**.

Prose rules require the next session to read them, recall them, and generalise them to a novel
variant. That has now failed three times. **An assertion fires on its own.**

## The two checks

**1. INPUT — every published decklist is exactly 20 cards.**
If your parser reads a real list and it does not sum to 20, *your parser dropped something.* This
one line catches all three historical bugs at parse time, on the first list, before any sim runs.

```
python3 lib/deck_check.py lists parsed_source.jsonl
```

**2. SHAPE — a deck must be a deck.**
20 cards · positive integer quantities · at least one resolved Basic Pokémon · maximum two copies
per canonical printed name across IDs · every ID resolvable. Name/ID disagreement is reported because
the engine resolves by ID and ignores names. Thin evolution lines receive a source/playability
warning, not a legality error: extra evolution copies are legal. The September 5 audit verified that
the former rule wrongly rejected the existing beautifly-dustox and venusaur lists.

```
python3 lib/deck_check.py pool pool_meta8      # -> "✅ pool clean" or "❌ N deck(s) FAILED — DO NOT SIM"
```

## Non-negotiables baked in

- **`selftest` encodes the three historical bugs as fixtures.** Any change to this file must keep
  failing them. `python3 lib/deck_check.py selftest`
- **The validator REFUSES to run without `deckgym-database.json`.** It silently no-opped and passed
  the §102 fixture once during its own construction — a check that skips quietly is the exact
  failure mode this file exists to prevent.

## When to run it

- After reconstructing ANY decklist from a source, before writing it to a pool.
- **Before any sweep.** `deck_check.py pool <dir>` exits non-zero; gate the driver on it.
- Before believing a surprising result that would be explained by a crippled deck.

## The check no tool can do for you

A legal 20-card deck can still be a bad reconstruction of its source. Compare parsed quantities
and IDs to the published input before adding filler. A thin evolution line warrants checking the
source; it does not establish that the deck is illegal.
