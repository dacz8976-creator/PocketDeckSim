# Pocket Deck Lab — Independent Audit (2026-09-10)

**Scope.** Read-only. Nothing in your folders was edited or moved. Audited: `C:\Users\dacz8\Projects\Pocket Deck Lab` (live checkout, 1,170 files in the root, plus `Boss Folder` with ~1,500 files), `Projects\Pocket Deck Lab Backups`, `Desktop\Battle Logs`, and the retired OneDrive checkout. The Desktop path you gave is now an empty shell (empty `.git`/`.codex`/`.agents` and one stray 46-byte error file).

**Method.** Five cheap scouts (2× Haiku on the 1.3 MB ledgers, 3× Sonnet on governance, engine, evidence/Codex era) wrote reports; I then re-verified every load-bearing claim myself against the files, and for the engine I compiled the fork as it sits on disk and ran a probe against it and against upstream `bcollazo/deckgym-core` (HEAD 2026-08-30). Two scout claims were wrong and are excluded (details in file 01 and 02). Epistemic tags used throughout: **[V]** verified against a file or by execution, **[I]** inferred, **[U]** uncertain.

Companion files: `01_ENGINE_FIDELITY.md`, `02_PROCESS_AND_HISTORY.md`, `03_RECOMMENDATIONS_AND_ALTERNATIVE_PATH.md`.

---

## The plain answer to your question

**Your goal is achievable. This project, on its current route, will not get you there — and that is not a budget or model-choice problem.** It is the route. Three facts, each verified:

1. **Every deck ranking the project has ever produced (meta4 through meta9, all ~244 Claude sessions and the Codex era's eval18 panel) was run on an engine in which Sleep and Paralysis do nothing.** An Asleep or Paralyzed Active Pokémon is offered its attacks and its retreat, and Paralysis is wiped at the very next Checkup — before the victim's turn begins. I reproduced this by compiling the fork on disk and by compiling upstream; both behave identically [V]. The bug is inherited from upstream's first commits (2025-03) and has been present the entire life of the project [V, from Codex's own `STATUS_BUG_PROVENANCE.md` plus my probe]. Codex found it on Sept 8 and fixed it in an *isolated candidate* (`status1`, `paralysis1`) — but the shared development checkout still has the bug, which is why my compile of it failed the probe [V]. meta4–meta6 additionally used the `e`-family bot that reads the opponent's hidden hand and deck [V: `tests/value_function_hidden_info_test.rs`]; whether meta7–8's `p3` pilot was leak-free is [U].

2. **The simulator has been measured against real play three separate times and never came close to ranking decks the way real results do.** Claude era §44: correlation +0.14 across 27 archetypes / ~5,700 real games, wrong favored side 59%, sim too high by +16.5 points on average [V, ledger]. Claude era 93-cell check: r ≈ 0.11, wrong winner 48% [V, ledger]. Codex era Sept 8, 8 top archetypes vs. 900 real Limitless BO1 games: matchup-level r ≈ 0.50, mean absolute error 15.5 points, wrong favored side in 8 of 28 cells, and **deck-level rank correlation ≈ 0.2 (0.21 buggy, 0.23 after the Sleep fix)** — the sim has Suicune at 60% (real 41%), Lucario at 59% (real 49%), Hydreigon at 37% (real 51%) [V, recomputed by me from Codex's table]. Fixing Sleep moved Altaria from 34% to 45% (real 50.5%) but left the overall correlation essentially unchanged. The sim cannot currently tell you which of two real decks is better, and the remaining gap is mostly the bot (one-ply search, no opponent modeling), not rules.

3. **Effort has gone to process and infrastructure in both eras, and the project already knows it.** 79% of the 34 automated gates check the project's own bookkeeping, not decks or rules [V, `gates.sh:57-92`]. Five gates protect a tournament-census scraper that never harvested a decklist [V]. Sixty Claude sessions (s181–s244) on the Battle Log pipeline yielded five approved OCR rows from one 60-second clip, with OCR identifying zero cards [V]. `Boss Folder` has 94 top-level directories, ~90 of them dated work packages; of the ~74 its own docs name, about 40 are bot/engine infrastructure, ~21 video/OCR, 5 deck research [I, classified by name]. The project's own review s243 (2026-08-26) wrote: "the project has concentrated on proof machinery and invented inputs rather than producing a reviewed transcript from a real clip." Codex's `PROCESS_AND_SETUP.md` (2026-09-05) wrote: "effort being diverted into process." Then both eras continued the same shape. **Another document will not change this — a different workflow will** (file 03).

Net product after ~2 months: four narrow engine fixes from video (Soothing Wind ×2, Magmar, Xatu), one inherited-bug fix sitting unmerged, two hand transcriptions of one game, and no deck that is simultaneously (a) yours, (b) backed by a real win/loss record, and (c) backed by a simulator result that survived its own replication [V, Codex `CURRENT_FINDINGS.md`, `deck-question-refresh/RESULTS_BRIEF.md`].

---

## What is sound (say this first, because it matters for what to keep)

- **The hidden-information architecture Codex built is real engineering** [V]: `PlayerObservation` hides opponent hand/deck, search RNG is decoupled from game RNG, and the `k3` default bot uses a non-leaking value function. Two of the three most serious bot defects from the Sept 5 `ENGINE_AUDIT.md` are closed.
- **Poison, Burn, status clearing on bench/evolve, and checkup order are correct** [V]; turn-1 energy and evolution restrictions look structurally correct [V for evolution, I for energy — traced by initialization comment, not by executing `rotate_energy_zone`].
- **Codex's Sept 8 competitive-deck-study is the single most useful artifact in the project** — not because of the sim, but because it pulled the real Limitless field (55 tournaments, 5,029 registrations, 13,313 matches) and a real archetype matchup matrix. That data answers "what is competitive" directly, for free, without a simulator.
- **Codex's rule scanner** (`audit_status_restrictions.py`) found 13 illegal decision rows in 56 games in minutes — source reading plus invariant checks found in one day what 60 OCR sessions and dozens of video reviews did not. That is the fidelity tool to keep.
- The current `AGENTS.md` (Sept 9) is lean and explicitly says a routine fix needs no station, prereg, or design review. The problem is no longer the written rules; it is the package-per-question habit in `Boss Folder`.

## What is not

- **Two special conditions inert in every ranking ever produced**; fix exists but is unmerged; no rule-level test exists that would have caught it (tests assert the flag is set, never that the effect happens) [V].
- **No single source of truth for the engine**: installed runtime = s120k (Aug 19); "available" = eval18; dev checkout on disk = eval19-adjacent (Sept 8); fixes = isolated `status1`/`paralysis1` binaries; fork git log ends Aug 22 with ~461 of 465 tracked files modified and uncommitted [V]. Meanwhile a 46-part hash-verified cloud ZIP regime exists for backups.
- **1,170 files in the project root; `HANDOFF.md` 648 KB and `CURRENT.md` 633 KB**; `STATIONS.md:83` measured boot cost at 139k tokens and named root clutter as the cause; never fixed [V].
- **~28 documented retractions** across the two ledgers (11 in HANDOFF, 17 in CURRENT) — findings published before replication, then reversed [V, scout counts].
- **Zoroark**: 37 root files and ~17 stations; sim called zoroark-absol the 65% champion while your own ladder showed it losing 0-7 to magnezone-oricorio; the ledger still lists `zoroark-absol-dustin-2ex` as "best deck" [V].
- **Evidence pipeline cost per battle was never measured** in either era, by the project's own repeated admission [V].

---

## Where the audit disagrees with the scouts (so you know the checks ran)

- A Sonnet scout flagged "Confusion deals no self-damage on tails" as a bug. **That is the physical-TCG rule; in Pocket the attack simply fails.** The engine is correct here. Dropped.
- A Sonnet scout flagged `AGENTS.md`'s reference to `Boss Folder/before_changes/AGENTS.md` as a dead link. **The file exists (22,743 bytes)**; it simply wasn't in the subset I staged. Dropped.
- Scouts reported the fork tree "does not compile." It compiles fine once the missing modules are present; the probe ran.

---

## The recommendation in one paragraph (full version in file 03)

Stop using the simulator as a deck *ranker*. Use the real Limitless matchup matrix (already pulled, refreshable monthly) to define "competitive," use it to find off-meta archetypes with favorable matchups against the top-share decks ("creative within competitive"), and make **your own ladder games the arbiter** with a one-line-per-game log (25–30 games per candidate). Keep the simulator for exactly two narrow jobs where bot weakness cancels out: same-shell card-swap A/Bs with paired seeds (≥1,000 games, treat <5 points as noise), and "does this list function at all" sanity checks — and only after `status1` + `paralysis1` are merged into one canonical, committed fork guarded by a ~12-test rules-conformance suite (spec in file 03). Archive the station system, the 34 gates, both ledgers, and `Boss Folder` into one `archive/` folder; a new session should need to read under 5,000 words. Upstream the Sleep/Paralysis fix to `bcollazo/deckgym-core` — it is the one thing this project has produced that the outside world would value, and it's about four files.

If you instead want to keep pushing the simulator toward "trustworthy ranker," say so knowing the price: it requires a much stronger bot (opponent modeling, multi-ply search with hidden information) — a research problem the upstream project and its Discord have not solved either — and even then bot-vs-bot results will differ from a human ladder with mixed skill. That path is open-ended; the Limitless-plus-playtest path has a bounded cost and produces decks you can play next week.
