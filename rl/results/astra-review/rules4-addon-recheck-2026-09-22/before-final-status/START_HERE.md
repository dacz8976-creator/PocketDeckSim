# START HERE — Pocket Deck Lab (updated 2026-09-22)

Read this before anything else in the folder. It is the only summary that is current. If another
file disagrees with it, the other file is history.

## What this project is for

Find 20-card Pokémon TCG Pocket decks that are creative **and** win — off-meta, catch people off
guard, built around what Dustin enjoys playing (Arceus/Crobat, Xatu, poison, weird pairings). Not
"the optimized deck that wins 0.1% more often." The output that counts is a deck Dustin plays on
the ladder and wins with.

## What is true right now

- **The engine is `0.1.0-pdl.rules4`** (September 22). It retains the earlier rules repairs,
  player-selected Energy discards and corrected Cubone/Clefable/Bonsly effects, and fixes the
  T2 last-Pokemon/third-point result to a tie. `project_manifest.json` names the verified executable.
  Verification: 1,826 engine tests, 44 accepted-review segments and four k3 smoke games.
  See the [rules4 repair and evidence limits](Boss%20Folder/rules4-t2-repair-2026-09-22/README.md)
  and [earlier rules3 repairs](Boss%20Folder/rules3-repairs-2026-09-22/README.md).
  The RL add-on is now **0.7.2** on rules4. Its chosen-pair replay, hidden-card, forecast and
  choice-encoding checks passed; the full benchmark refresh is running. See the
  [current add-on recheck](Boss%20Folder/rl-feasibility-2026-09-18/results/astra-review/rules4-addon-recheck-2026-09-22/README.md).
  Historical binaries, results and training environments are preserved. Run 5 has not started;
  any new run must identify the new add-on explicitly and have a fresh result identity.
- **Every deck ranking produced before 2026-09-10 is void.** All of them (meta4–meta9, the
  Zoroark work, the Sept 8 eval18 panel) ran on an engine where Asleep/Paralyzed Pokémon could
  still attack and retreat. Don't re-run them; don't cite them.
- **The simulator cannot rank decks**, even now. Against real Limitless results it gets the
  favored side wrong about a third of the time and its deck-level rank correlation is ~0.2. The
  September 22 rules fixes do not establish playing strength or deck-ranking accuracy. Use it only for: (1) does this list function at all,
  (2) card A vs card B in the same shell with paired seeds, ≥1,000 games, differences under 5
  points are noise.
- **What "competitive" means is read off Limitless**, not simulated. Snapshot and top-30 table:
  `decks/classifier/limitless_2026-09-10.json`. Refresh roughly monthly or when a set drops.

## The loop

1. New set or new idea → run the classifier for complements (`lib/deck_classifier.py`, usage
   in `decks/brews/BREW_NOTES_2026-09-10.md`) and write a draft list into `decks/brews/`.
2. Dustin plays it 10–15 ladder games and reports in a sentence.
3. Adjust the list or move on. A brew that wins on the ladder gets promoted to `decks/dustin/`.
4. Sim is optional and narrow (see above). Astra runs it; results are "does the combo fire,"
   not "is the deck good."

## Before you do anything

Read `RULES_FOR_AGENTS.md` (one page: Pocket's rules, where they differ from the physical TCG).
Never state a card's text from memory — `python lib/card.py "<name or id>"` prints it.
When your session ends, add one dated line to `LOG.md` in plain words: who you are, what changed.

## Where things are

- `RULES_FOR_AGENTS.md` — the rules. `lib/card.py` — card lookup. `LOG.md` — one line per session.
- `decks/dustin/` — Dustin's 15 real decks, decoded from in-game QR codes.
- `decks/brews/` — draft lists to playtest + `BREW_NOTES_2026-09-10.md` (the ideas and why).
- `decks/classifier/` — classifier inputs, Limitless snapshot, full classifier report.
- `decks/history/` — what the Sept 5–9 battle recordings were (mostly AI games; don't re-mine).
- Ladder results this season: the **Ladder Log** artifact (Claude-hosted page); read it back before adjusting a list.
- `lib/deck_classifier.py` (what a deck is built to do, what pairs with a card),
  `lib/decode_qr.py` (QR screenshot → decklist), `lib/deck_check.py` (20-card legality).
- `AUDIT_2026-09-10/` — the independent audit: engine findings, project history, known failures
  (`02_PROCESS_AND_HISTORY.md` has the KNOWN_FAILURES table), recommendations.
- `deckgym-fork-s193/UPSTREAM.md` — how the fork differs from upstream and what to do at the
  next set merge. Five B4a cards are still `RulesUnverified` (listed there).

## What NOT to treat as current

`HANDOFF.md`, `CURRENT.md`, `CURRENT-CORE.md`, `current_best_decklists.txt`, the historical
entries in `decks/index.json`, `STATIONS.md`, `station.sh`, `gates.sh`, the `claims/` folder,
`meta9_SPEC.md` and every `meta*`/`zoroark*`/`s1NN_*` file in the root. `Boss Folder/` is
Astra's working area; its dated packages are records of runs, not instructions.

## Who does what

Dustin owns it and decides. Astra (Codex) owns the engine, builds, and sim runs. Claude does deck
discovery (classifier, brews, Limitless reading) and reviews. Both agents: report in plain
language; no new files, gates, stations, or process documents unless Dustin asks; keep it cheap.

## The mistakes this project has already made (don't repeat them)

Ranking decks on an engine nobody had checked against the rules. Publishing findings before
replicating them (~28 retractions in the old ledgers). Building process — 34 gates, stations,
claim files, 1,100+ root files — instead of decks. Four different "current" engines at once.
Sixty sessions on video/OCR that never read a single card. Fixating on one deck (Zoroark) that
the sim liked and the ladder didn't. Full list with what catches each: `AUDIT_2026-09-10/`.
