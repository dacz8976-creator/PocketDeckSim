# 03 — Recommendations: a route that actually ends in decks you play

Tags: **[V]** verified; **[I]** inferred / methodological judgment; **[U]** uncertain — verify before relying on it. These are proposals; nothing here has been applied to your files.

## 1. The verdict, stated plainly

**Goal:** creative and competitive 20-card decks for real Pocket play.

**Route A — the current route (simulator as ranking oracle):** not viable on any budget you have described. Three prerequisites would all have to be met: rules fidelity (fixable — the Sleep/Paralysis fix already exists), bot strength sufficient to pilot non-trivial decks (not fixed; `k3` searches its own turn only; the ledger shows ~20-point under-rating of decks the bot cannot pilot), and a bot-vs-bot → human-ladder transfer that has measured at r≈0.1–0.5 three times with the sim 2.1× more decisive than reality. The second and third are research problems, not bug fixes. The only engine change ever measured against real data — the Sleep fix — moved the deck-level rank correlation from 0.21 to 0.23; the nineteen eval packets were never measured against real results at all [V, file 01 §7]. Continuing this route buys more engine microscopy and no decks.

**Route B — real data decides what is competitive; you decide what is creative; your ladder decides if it works; the simulator is a small tool, not the judge.** Bounded cost, produces a playable list in weeks, uses the project's two genuinely valuable assets (the Limitless pull and a corrected engine) and your genuine edge (you read card text correctly and catch mechanics errors agents miss). This is what file 03 describes.

If you want Route A anyway, §7 gives the one number that would make it honest.

## 2. What "creative and competitive" means operationally [I]

"Competitive" is an empirical property of a deck against the field people are actually playing. The project already has the right data source: Limitless (`play.limitlesstcg.com/decks/?game=pocket`) — 55 tournaments, 5,029 registrations, 13,313 matches, archetype-level matchup matrix, exact lists from top finishes, refreshable on demand. Codex's `competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/` already contains the capture method, the parsed `OPPONENT_DISTRIBUTION.json` (523 archetypes, reconciled to the header), and 28 real matchup cells [V].

"Creative" then has a precise meaning: an archetype **outside** the top-share tier (say <3% of registrations) whose real matchups against the top-3-by-share decks are favorable, or a non-standard build of a known archetype. Real players find rogue decks exactly this way — by reading the matchup matrix for holes, not by simulating 50,000 games.

## 3. The loop (replaces stations, evals, and packets)

**Monthly, ~1 hour, cheap agent (Haiku/Sonnet) or a script you already have:**
1. Snapshot Limitless: archetype shares, W-L-D, matchup matrix for the top ~12 archetypes. Save raw HTML + a parsed JSON. (Method exists: `research/README.md`, `OPPONENT_DISTRIBUTION.md`.)
2. Compute each archetype's *field-weighted* real win rate (weights = registration share) and list the five archetypes under 3% share with the best weighted rate or the best record against the top 3. These are the "creative-competitive" candidates. Pull one top-finishing exact list for each as a skeleton.

**Per candidate, you + one cheap agent:**
3. Build the 20-card list from the skeleton plus your modifications. The agent's job is card-text lookup and legality (`lib/deck_check.py` already does this); yours is the idea.
4. Optional simulator pass — only the two jobs it is fit for (§4).
5. **Playtest: 25–30 ladder games**, one line per game in `PLAYTEST_LOG.tsv`: `date, deck, opponent archetype, first/second, W/L, one note`. Opponent archetype comes from glancing at the in-game Battle Log (a 30-second manual entry; no OCR, no video). Stop-loss: at 25 games, below 10 wins → drop; 16+ → keep and extend to 50; in between → your call or extend.
6. Promote anything that holds ≥55% at 50 games to `DECKS.md` with its record, the Limitless snapshot date, and the list.

Statistics, so expectations are honest [I]: at n=30 a win rate has a 95% interval of roughly ±18 points; at n=50, ±14. That cannot distinguish 52% from 48%; it can distinguish a 65% deck from a 45% one, which is the decision you actually need. It is coarse, but it is *real*, and it is more predictive evidence than the simulator has produced in two months. You can sharpen it with the Limitless matchup priors for the opponents you face.

**Three product artifacts are the whole project state**: `DECKS.md` (candidate and promoted lists with evidence), `PLAYTEST_LOG.tsv`, `ENGINE_BUGS.md` (rule defects with status and the test that pins them). A session that changes none of them is overhead.

## 4. What the simulator is still good for — two jobs, with conditions [I, conditions V]

Preconditions before any sim number is used for anything: `status1` + `paralysis1` merged into the dev checkout, committed, tagged, built once, hash recorded in `CANONICAL_ENGINE.sha256`; conformance suite (§5) green on that hash; bot = `k3` or another public-information bot only.

- **Job 1 — same-shell card swaps.** Same 20-card shell, 1–2 cards changed, same pilot both sides, paired initial seeds, ≥1,000 games per arm, against 3–4 fixed opponents from the Limitless top tier. Read only differences ≥5 points, and only after a second seed block agrees on the sign (the project's own best A/B flipped sign between 576 and 2,112 games [V]). Never use it if either arm or any opponent depends on Sleep/Paralysis until the fix is merged.
- **Job 2 — "does this list function."** Does it set up by turn 3? Energy type conflicts? Dead cards? A few hundred games vs. a random or weak bot answers this; it is a sanity check, not a rating.

Never again: cross-archetype rankings, "best deck" tables, gauntlet re-ranks, meta10. Until §7's criterion is met, any such number is noise with a decimal point.

## 5. Rules-conformance suite — the gate that would have caught this six months ago [I; rule text V via Pocket-specific guide]

Behavioral tests at the `Game` API level, written against the rulebook, not against a card. Each must fail if the mechanic is removed. Roughly a day of agent work; the probe in file 01 Appendix A is tests 1–3.

1. Asleep Active: zero Attack actions and zero Retreat actions offered; abilities, Trainers, evolution still offered.
2. Paralyzed Active: same as 1.
3. Paralysis lifecycle: inflicted on A's turn → still present at the start of victim's turn → cleared at the Checkup after the victim's turn.
4. Sleep lifecycle: flip at every Checkup including the first; heads restores Attack/Retreat on the next turn; tails keeps them blocked.
5. Confusion: tails → no damage to either side, turn ends; heads → normal; Retreat unaffected.
6. Exclusivity: applying Paralyzed to an Asleep Active clears Asleep (and each other pairing); Poison/Burn stack with all.
7. Poison 10 / Burn 20 at every Checkup for both actives, Burn heads cures (exists — keep).
8. Status clears on retreat/bench and on evolution (exists — keep).
9. Turn 1: first player cannot attach Energy-Zone energy; no evolution on either player's first turn; one Supporter per turn; one Retreat per turn.
10. KO points: 1 for a non-ex, 2 for an ex, 3 for a Mega ex [U — confirm current in-game text]; game ends at 3 points; promotion forced when Active is KO'd with Bench available.
11. Empty deck: no draw, no loss (Pocket has no deck-out loss) [U — confirm]; turn cap / draw behavior matches the in-game rule [U — confirm the exact cap].
12. Energy Zone: exactly one attach per turn from the zone; zone types restricted to the deck's declared energy.

Mechanical gate: `cargo test --test conformance` in a pre-commit hook on the fork; any ranking or A/B file must begin with the engine hash and the conformance pass timestamp.

## 6. Engine actions, in order

1. Merge `status1` and `paralysis1` into `deckgym-fork-s193`, run the full suite, **commit**, tag `v-pdl-canonical-1`, record the hash. (Codex reports both pass 1,748 / 1,760 tests [V].)
2. Add the conformance suite (§5). Commit.
3. Open an upstream PR to `bcollazo/deckgym-core` with the Sleep/Paralysis attack-retreat restriction and Paralysis lifecycle fix plus tests 1–4. It is four source files [V]. This is the one output of the project with external value; it also means future upstream card updates come to you with the fix in place rather than being re-patched.
4. Retire the `e`-family bots from anything that produces a number (they read the opponent's hidden hand [V]).
5. Stop the eval-packet series unless a specific deck question from §3 requires a specific engine fix. Nineteen packets produced four narrow fixes and were never scored against real results; the §7 metric is how any future bot work earns its keep.

## 7. The one number that would justify Route A [I]

If you want to keep trying to make the simulator a ranker, track exactly one metric and make it a gate: **deck-level Spearman correlation between simulator win rates and the Limitless matchup matrix for the top-8 archetypes, using the current canonical engine and `k3`.** Today it is 0.23 [V, recomputed with tie correction]. Set the bar at ≥0.7 and matchup MAE ≤8 points before any cross-archetype ranking may be cited. Every engine or bot change reports the delta. If five engine changes in a row fail to move it, Route A is dead by its own measure. This converts an open-ended research program into a falsifiable one, which is the only honest way to keep it.

## 8. Project hygiene — archive, don't delete [I]

Move (do not delete) into `archive/2026-09-claude-era/` and `archive/2026-09-codex-era/`: `HANDOFF.md`, `CURRENT.md`, `CURRENT-CORE.md`, `STATIONS.md`, `SKILL.md`, `station.sh`, `gates.sh` + all `*_selftest.*`, `prereg_gate.py` + template, `claims/`, all `s###_*` files, all `meta*`, `zoro*`, deck `.txt` files (index them in `DECKS.md` first), bundles and tarballs, `OPEN_FIXES.tsv`, `NEXT_ACTIONS.tsv`, `lab_*`, `jobs_*`, `Boss Folder/` in its entirety except `competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/` (the Limitless capture — keep that at top level as `field/2026-09-08/`).

Target root after cleanup: ≤25 entries — `README.md` (≤600 words), `AGENTS.md` (current one, minus the Sol/Astra budget section, plus §9 below), `DECKS.md`, `PLAYTEST_LOG.tsv`, `ENGINE_BUGS.md`, `CANONICAL_ENGINE.sha256`, `field/`, `deckgym-fork/` (renamed, committed), `lib/` (deck_check, card_canon), `archive/`, `.git/`. A fresh session should be able to read everything it needs in under 5,000 words.

Fix the one remaining path confusion: the Desktop `Pocket Deck Lab` shell and `.pdl-retired` can go to `archive/` too; `LOCAL_DECKGYM_WSL_RUNBOOK.md` still points at the OneDrive path [V].

## 9. Gates for the agents, not notes (one paragraph for `AGENTS.md`) [I]

"Every session ends by appending to `DECKS.md`, `PLAYTEST_LOG.tsv`, or `ENGINE_BUGS.md`, or by logging itself as overhead in `OVERHEAD.tsv`; the owner reviews that file weekly. No new top-level file without removing one (pre-commit hook: root entries ≤25). No new `.md` that describes a plan, design, protocol, charter, checkpoint, review, or independent review — plans go in the chat. No gate, selftest, validator, hash manifest, or backup procedure may be added without a one-line statement of the real-game fact it protects. Engine changes: commit per change, conformance suite green, hash recorded; no number is reported from a binary whose hash is not `CANONICAL_ENGINE.sha256`. Sim numbers are only same-shell A/B deltas or function checks; cross-archetype rankings are forbidden until the §7 gate passes. No video review, OCR, or evidence pipeline work without a measured one-battle pilot (minutes and tokens) written in `OVERHEAD.tsv` first." Implement the hook and the root-count check as scripts that exit non-zero; the prose is just their documentation.

## 10. On agents and cost [I]

- The heavy lifting in Route B is human (you playing) and clerical (Haiku-class: Limitless parsing, deck legality, log tallying). Reserve an expensive model for the merge/commit/conformance work once, and for reading engine code when a real-game observation disagrees with the sim.
- Never again task an agent with reviewing raw video at scale or OCR on the Battle Log. The information you need from the Battle Log (opponent archetype, who went first) is a 30-second human glance.
- When you do want an engine check from a real game, write the *disagreement* in one sentence ("my Sleeping Castform couldn't attack; the sim's could") and have the agent write the failing test first. That is how Codex found the Sleep bug; it is cheaper than every pipeline built before it.

## 11. What would change this verdict

- If someone shows a bot (yours or upstream's) with deck-level Spearman ≥0.7 against Limitless, Route A becomes viable and §4's restrictions can loosen.
- If Limitless stops publishing matchup data, Route B loses its "competitive" anchor and your playtest log becomes the only real signal — still better than the sim, but slower.
- If you find you don't enjoy 25-game playtests, the honest answer is that the project's goal requires them; no amount of engineering substitutes for the real game being played by a real person.

## 12. Decisions only you can make

1. Route B, Route A with the §7 gate, or stop — I recommend B, with §6 steps 1–3 done once because they are cheap and the fix has external value.
2. Whether to archive the Claude- and Codex-era material as described in §8 (I recommend yes; nothing is deleted).
3. Which three or four archetypes to start with. From the Sept 8 real data, the top-3-by-share were Lucario, Altaria/Espeon, Suicune/Baxcalibur [V]; your two real records on file are chandelure-oricorio 7-2-1 (10 games) and zoroark-absol-dustin-2ex 53.6% (~200 Limitless matches) [V] — both are reasonable first entries in `PLAYTEST_LOG.tsv`, and Mega Blaziken (52.4% overall on Limitless; 60.5% mean across its seven top-8 matchups; a 9-2-1 first-place exact list on file) is the obvious competitive baseline to measure your creative decks against.
