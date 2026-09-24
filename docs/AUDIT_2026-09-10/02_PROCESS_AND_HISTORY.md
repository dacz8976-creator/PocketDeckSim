# 02 — Process, history, and the pitfalls that repeat

Tags: **[V]** verified against the cited file; **[I]** inferred; **[U]** uncertain. Paths relative to `C:\Users\dacz8\Projects\Pocket Deck Lab\`.

## 1. Shape of the project today [V]

| Location | Contents | Notes |
|---|---|---|
| project root | **1,170 files, 30 dirs, flat** — 357 .txt, 318 .md, 129 .jsonl, 105 .py, 64 .sh, 16 git bundles, 13 engine tarballs | 772 files carry an `s<NNN>_` session prefix; `STATIONS.md:83` says root clutter drove boot cost to 139k tokens; `s243` re-measured 1,158 files two weeks later and said the same |
| `HANDOFF.md` / `CURRENT.md` | 648 KB / 633 KB; 520 + 465 headers; ~185,000 words combined | "grep only" by rule, yet they are the only place most findings live |
| `deckgym-fork-s193/` | the Rust engine, 472 .rs files; git log ends 2026-08-22; 461/465 tracked files modified since | see file 01 §4 |
| `Boss Folder/` | Codex era (Sept 5–9): ≥1,500 files (listing truncated), 1.48 GB, 94 top-level dirs (~90 dated packages) — counts from the on-device directory listing; only ~11 of those dirs were staged for reading | each package: README, candidate, validation, harness, fixtures, before/after copies |
| `Pocket Deck Lab Backups/` | 87 entries incl. a 717 MB and a 432 MB recovery ZIP plus per-eval checkpoints | |
| `Desktop\Battle Logs\` | 11 MP4s at top level (6.35 GB) plus subfolders; `BATTLE_REVIEW_INDEX.csv`: 39 videos, 28 "Reviewed", 9 "Needs full battle review", 2 "Partial" (reviews are narratives, not transcripts) | |
| `Desktop\Pocket Deck Lab\` | empty shell: empty `.git`, `.codex`, `.agents`; `_UL` (46 bytes: a captured "cmd.exe: command not found" error) | the path you gave me |
| `.pdl-retired\DO-NOT-USE-s241-...` | full copy of the Aug 26 checkout (1,155 files) | |

Mandatory bootstrap reading named by the docs themselves (both eras): ~15,000 words / 129 KB before touching either ledger [V, scout `wc -w`].

## 2. Governance burden — measured, not felt [V]

- `gates.sh:57-92` registers **34 gates**. By subject: 7 touch deck legality / card resolution / evaluation regression; **27 (79%) verify the project's own paperwork** — runner self-test, boot status, claim/close integrity, station IDs, lock etiquette, prereg schema, runbook artifacts, evidence portability, driver authority, render guard, taxonomy crosswalk.
- **Five gates** (`m2_source`, `s127_gate0`, `s128_userscript`, `s128_prereg`, `s128_verify`) exist to keep a tournament-census scraper honest. `CURRENT-CORE.md:200,234,248`: "the census harvester does not exist yet," "HOLDOUT stays unread." It never harvested a decklist. 15% of the gate board guards data that was never collected.
- Eighteen standalone `*_selftest.*` scripts plus ~12 embedded `selftest` subcommands: nearly every gate tests itself. `gates_selftest.sh` has 10 cases proving `gates.sh` fails correctly.
- `PREREG_TEMPLATE.txt:22-70` requires ESTIMAND, SIGN-CONVENTION, per-arm player bindings, EXPECT-IDS-SHA256, sealed PILOT-PLAN, BAR/NULL-CALIBRATION pairs with thousands of null replicates, SCOPE-ON-PASS/FAIL. Clinical-trial rigor for a card-game hobby sim, enforced by a gate, consuming a full station (`claims/done/analysis-layer-gates.claim`, 9 versions).
- `CURRENT-CORE.md` (the "digest") carries 25 ⛔ and 54 ⚠ markers in 352 lines — one prohibition or warning every ~4.5 lines.
- The current `AGENTS.md` (Sept 9) is the sanest governance document in the tree. It explicitly retires station/prereg/review requirements for routine fixes. The burden now lives in *behavior* (`Boss Folder` packaging), not in written rules.

## 3. Claude era, by the ledgers [V via Haiku digests, spot-checked]

- `HANDOFF.md`: ~70 deck-research stations, ~25 engine/card, ~20 infrastructure/process, ~10 audit. **11 retractions/corrections**, including: Solgaleo "#2" disputed then retracted (§12→§22→§25); "goodra 58.5%" withdrawn (mixed bot tiers); seat-bias finding retracted (engine does randomize); `mcts_finals_driver.sh` silently ran `m,e2` for three weeks across 8 result files (§23); the "MCTS" bot was flat Monte Carlo (§25); Vaporeon cost explanation retracted (ablation error, §47); Zoroark family order reversed vs. real ladder (§45).
- `CURRENT.md`: **17 retracted findings**; 38 standing rules (23 measurement, 8 compute, 11 deckbuilding, 3 bookkeeping); the "largest open defect" is `sim-spread-calibration` — every arm's calibration slope 0.22–0.47 against a target of 1.00 (§156–§163). The ledger's "best deck" remains `zoroark-absol-dustin-2ex` (meta9 4th of 33; real 53.6% on ~200 Limitless matches) with `chandelure-oricorio` secondary (your own ladder 7-2-1 in 10).
- Zoroark: 37 root files match `zoro*`; mkdecks wave1/2/3 scripts; the sim crowned zoroark-absol at 65.36% (§28) while your ladder observation was 0-7 vs magnezone-oricorio (§44). This is the fixation you named, and it is visible in the file system.
- Sessions s137–s244 (Aug 21–27): reading the `claims/done/` names in order — driver authority, F007 selftests, equiv exit codes, portable evidence, fixture containment, node gates, gate board fail-closed, transactional station close, resumable authoritative gate board, gate trust anchor design, trust boundary decomposition, clean-commit board semantic equivalence, authority host eligibility, trusted admin WSL handoff, WSL keepalive, WSL on-demand bridge, then s201–s244 battle-log: architecture design, contract validator, schema rebuild, boundaries design, extractor/oracle separation design, MVP charter, MVP v1, foundation rebuild, card resolution simplification, foundation v3, output transaction foundation, implementation conformance, simplification decision, minimal vertical slice, manual-assisted prototype design, synthetic feasibility design, feasibility execution, synthetic retry design, discrete retry execution, synthetic two-turn design, OCR goal realignment, editable OCR prototype. **About 100 consecutive sessions, roughly one deck-research result among them.** `s199` alone went v1.0.0→v1.0.5 in 17 hours (Aug 22 23:47Z → Aug 23 17:03Z), each version rejected by "lead" for 7–12 new defects, the validator reaching 122 self-test cases plus a 52-case acceptance suite and a 63-mutant kill sweep, with each version retracting some of the previous version's own claims ("I counted by eye"; v1.0.4's acceptance command "COULD NOT ACCEPT ANYTHING in production") — all under the scope line "NO recording, image, frame, crop or video inspected" [V, `claims/done/s199-*.claim:5-10`].
- `archive/` (on-device listing) holds nine `s###-rejected-*` directories — rejected pre-capture series, rejected resumable gate v1, rejected battle-log MVP v1, two rejected contract v2s, rejected ordered-evidence v3, rejected transaction candidate, rejected implementation candidate, rejected minimal vertical slice. The project generated more rejected architectures than accepted transcripts.

## 4. Evidence pipeline yield [V]

| Effort | Output |
|---|---|
| ~60 Claude sessions (s181–s244) on Battle Log OCR/extraction | 5 approved rows from one 60-second slice of one clip; OCR identified 0 cards (all 3 IDs typed by you); `READ_ME_TOMORROW...:40`: "Card IDs were generally blank" |
| Hand transcription | 1 real game, transcribed twice (`7.23battle1_log.md`, `battle1_log.md`) |
| Codex video review (Sept 5–9), 39 videos indexed, 28 "Reviewed" | 4 narrow engine/evaluator fixes (Soothing Wind arrival, Soothing Wind restoration, Magmar conditional damage, Xatu forced-Checkup boundary); several "engine already agrees" confirmations; several still `RulesUnverified`; 9 reviews later demoted under a stricter full-battle bar |
| Cost per battle | never measured, in either era (`direct-video-benchmark/README.md:24`, `ROADMAP.md:43`, `CURRENT_WORK.md:13`) |
| Owner priority reversals | Sept 5 "OCR primary, video too costly" → Sept 6 "video primary, OCR deferred" → Sept 9 video paused |

The screenshot of the in-game Battle Log (`Screenshot 2026-08-27 100033.png`) shows why OCR failed: legible event text next to ~90×115 px stylized card thumbnails. The text was never the problem; card identity was, and it is not in the image.

By contrast, Codex's rule-invariant scanner over saved game traces (`tools/audit_status_restrictions.py`) found 13 illegal decision rows in 56 games and exposed the Sleep bug in one day. **Reading the engine against the rulebook beat reading pixels.**

## 5. Codex era — same shape, new vocabulary [V/I]

Codex diagnosed the Claude era correctly in writing (`Boss Folder/PROCESS_AND_SETUP.md:31`: "effort being diverted into process") and then:
- produced eval1…eval19 packets, each with README/candidate/validation/harness/fixtures/before-after copies and a multi-paragraph scope disclaimer — station numbers renamed;
- built a Meowscarada matchup study (protocol, capability review, tactical guide) before checking you play the deck; you didn't (`matchup-meowscarada-study/OWNER_CORRECTION.md`);
- froze a "broader fresh evaluation" protocol, reviewed it, and paused it before a single fresh game ("no fresh protocol game… exists in this checkpoint", `broader-fresh-evaluation-paused/CHECKPOINT.md`);
- engineered a 2.26 GB, 46-part, per-part SHA-256'd, upload-then-readback-verified cloud archive plus a verified "completion receipt" (`full-project-recovery-2026-09-08/README.md`) while the fork had no commit in three weeks;
- introduced a new governance layer ("Sol"/"Astra" cost pilots, per-unit budgets) on top of the old one.

Of ~74 named packages: ~40 bot/engine/evaluation infrastructure, ~21 video/OCR, **5 deck research**, ~2 backup [I, by name]. Net deck product: `competitive-deck-study-2026-09-08` — which is good work (see file 01 §7 and file 03) but whose sim half invalidated itself by discovering the Sleep bug mid-study.

Owner direction *was* followed where it was specific (Potion pilot repeated on a frozen bot; Comfey weights untouched; recovery checkpoint made). The Meowscarada premise was not checked first. `CURRENT_WORK.md` today reads as bot micro-tactics ("Mega0→1 funding merely starts setup; Mega1→2 enables an attack…") — less legible than the Claude-era station logs it replaced.

## 6. Version control and "which engine?" [V]

Root repo: 238 reflog entries, last commit 2026-08-27 ("Close Battle Log OCR prototype station"); no remote. Fork: 4 reflog entries, last commit 2026-08-22; `RECOVERY_ASSESSMENT_2026-09-07.md:21-27`: "Of 465 tracked files, 461 have unstaged changes… Neither Git history currently serves as a recoverable remote for the live work." `project_manifest.json`: installed runtime s120k (Aug 19) vs. "available" eval18 — neither is the dev checkout, and neither has the Sept 8 status fixes. Backups have triple checksums; the code has no commits.

## 7. Audits that changed nothing (the meta-pattern)

Independent reviews that reached essentially this audit's conclusion before it: `archive_S125_DIRECTION_v5.md` (Aug), `s227-external-audit-actionability-handoff` (Aug 25), `s243` (Aug 26: "proof machinery and invented inputs"), Codex `COMPREHENSIVE_REVIEW.md` / `ENGINE_AUDIT.md` / `EVALUATION_AUDIT.md` (Sept 5), `CLAUDE_IDEAS_bot_and_deck_research_2026-09-07.md` (my own prior session). Each produced a correct diagnosis and a document. None changed the workflow. **That is the strongest argument that the next step must be structural, not another note** — your own "gates, not notes" rule, applied to the project itself.

## 8. KNOWN_FAILURES — repeat pitfalls with a gate column

Per your standing instruction: anything at NONE after a second occurrence is a task, not a note. Occurrences are from the ledgers and Boss Folder; gates are what would refuse the failure mechanically (file 03 specifies them).

| # | Failure | Occurrences (≥2) | Current gate | Proposed gate |
|---|---|---|---|---|
| F1 | Rankings published on an engine whose basic rules were never conformance-tested (Sleep/Paralysis inert in every ranking) | meta4…meta9, eval18 | NONE | Rules-conformance suite (~12 behavioral tests) must be green at the binary's hash before any ranking is written; ranking files must carry the engine hash |
| F2 | Tests assert the flag, not the effect | status tests across fork + upstream; confusion test accepts either rule | NONE | Conformance suite written against rule text, not card text; a reviewer check: "does this test fail if the mechanic is removed?" |
| F3 | Process/infrastructure substitutes for product | s137–s244; eval1–eval19; Sol/Astra budget layer; 46-part backups | NONE (AGENTS.md says stop; nothing enforces) | Session exit gate: a session must append to one of three product artifacts (`DECKS.md`, `ENGINE_BUGS.md`, `PLAYTEST_LOG.tsv`) or be logged as overhead; overhead cap per week |
| F4 | New file in root instead of replacing one | 1,170 root files; 139k-token boot measured and re-measured | NONE | Pre-commit hook: root file count ≤ N (e.g., 25); new session-prefixed files refused |
| F5 | Finding published before replication, later retracted | ~28 retractions across both ledgers; Potion A/B sign flip | partial (prereg gate, but it gates paperwork) | No number enters `DECKS.md` without a second independent-seed run and a ≥5 pp threshold; otherwise it goes in a scratch file |
| F6 | Engine drift: uncommitted fork, multiple "engines," fix in an isolated binary | eval12→eval19, status1, paralysis1 | NONE | Commit-per-change in the fork; one `CANONICAL_ENGINE.sha256`; `cargo test` + conformance suite in a pre-commit hook; any run output must include the binary hash and must match the canonical hash |
| F7 | Building a study on an unchecked premise | Meowscarada (not your deck); Zoroark as "best" vs your ladder | NONE | Study charter must name the deck *you* will play and the real-game validation plan before any sim run |
| F8 | Evidence pipeline whose cost and accuracy were never measured | OCR (Claude), video (Codex), both eras | NONE | One-pilot rule: measure tokens and minutes on one battle before a second; write the number down or don't scale |
| F9 | Hidden-information leak in the bot used for rankings | meta4–meta8 | FIXED for `k3` (`value_function_hidden_info_test.rs`) | Keep; add: rankings may only cite `k`/public-family bots |
| F10 | Same failing approach retried under a new name | OCR gates v1.0.0–v1.0.5; station→eval; gauntlet meta4→meta9 re-rankings | NONE | Before a v(N+1) of anything, a one-line statement of what real-game fact v(N) produced; none → stop |

## 9. Two scout claims rejected during verification (for the record)

- "Confusion should deal 30 self-damage" — physical-TCG rule, not Pocket; engine is correct. Rejected.
- "`Boss Folder/before_changes/AGENTS.md` does not exist" — it exists (22,743 bytes); artifact of partial staging. Rejected.
