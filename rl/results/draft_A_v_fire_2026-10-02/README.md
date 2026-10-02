# Draft A against the Fire list (registered Oct 2, 2026, before any game)

**Who wrote this and why.** A Claude Code subagent (Opus 5.5) on the laptop, on a job from the coordinator session, which
took the comparison from Astra's review. This README, `run.sh` and `analyze.py` were written before any game of this test.
Nothing here is committed by this job: Dustin or the coordinator commits it, or not. `run.sh` refuses to play until these
three files are committed, so the definitions below are fixed before the first game. Revised Oct 2, still before any game
of the test, after a design review (sections 4, 5, 6.5, 6.7, 11 and 12).

**Not a ranking and not a ladder forecast.** Two lists each play one saved opponent list, with the bot (km3) on both
sides. The result says how the bot does with each list against that one list. It does not say which deck is better on the
ladder, and no number here predicts Dustin's ladder results. The ladder is the only score of a brew (START_HERE).

## 1. What is compared, and why

Draft A (Shark Tempo, `decks/brews/drafts_2026-10-01/draft-A-shark-tempo.md`) says it is aimed at the Fire decks Dustin is
0-5 against on the ladder (Mega Charizard Y ex / Entei ex 0-3, Mega Blaziken ex 0-2). Its reasons: Water hits them for
Weakness, and Mega Sharpedo ex's Turbo Shark does 70 (90 into a Fire Active) for one Water Energy and puts a free Energy on
the Bench every turn. This test checks that premise in the simulator against one Fire list:

- draft A against the Charizard Y / Entei list, and
- deck 13 (Dustin's Alolan Ninetales / Raticate) against the same list,

on the same deals. Deck 13 is the yardstick. It is one of Dustin's own Water lists, it shares Alolan Ninetales ex with
draft A, and the drafts' README names it as draft A's cousin. "Aimed at Fire" should mean draft A does better against this
list than a Water list of his that was not built for it.

The opponent is the saved Charizard Y / Entei list that stands in for Charizard Y under Dustin's ruling P5 (Sept 28;
`decks/screen/panel_ladder_2026-09-26/README.md`, "P5, `h-charizardy_entei` stands in for Charizard Y"). It is one list.
Blaziken is not in this test.

The cards that matter (from `python3 lib/card.py`, Oct 2):
- **Mega Sharpedo ex** (B4 035): Water, Stage 1 from Carvanha (B4 034), HP 190, weak to Lightning, retreat 0.
  [W] **Turbo Shark** 70: "Take a [W] Energy from your Energy Zone and attach it to 1 of your Benched [W] Pokémon."
- **Alolan Ninetales ex** (B2 029): Water, Stage 1 from Alolan Vulpix (B2 028), HP 150. [WW] **Binding Snow** 80: during
  the opponent's next turn, they can't take Energy from their Energy Zone to attach to their Active Pokémon.
- The Fire list's Pokémon are all weak to Water: Charmander (B2b 007), Charmeleon (B2b 008), Mega Charizard Y ex
  (B1a 014), Entei ex (A4a 010).

## 2. The three lists

All three are committed on `main` (HEAD 7c1b62f when this was written). `run.sh` checks each file's sha256 and that it is
the committed blob.

| role | path | git blob | sha256 |
|---|---|---|---|
| draft A | `decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt` | `19331d7896e16728e6f727aad4a0941c6e7e94f8` | `3f39092ba6680cc5b8013b961e2f5a0f07bc779816ade7a6891983082b2e7417` |
| deck 13 | `decks/dustin/13-a-ninetales-raticate.txt` | `f6de36a84f7199d70b64551edf756cdd1330bd20` | `f79ad459a1188f10ba34be4606f3cbc60db21386e8ef91721c5506239653b6fa` |
| the Fire list | `rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt` | `ecb57120a4878d467303616a03f2eb703e0ff094` | `07b98258ec896664f27d4722db83a26041d23230d598d8216115ba7a77b43cef` |

Draft A's reasoning is in `draft-A-shark-tempo.md` (blob `79b7cbee7a850a95d77c6f9c8670a3719b874c65`) and the drafts'
`README.md` (blob `61895afc42c653a7269ef4e4d9c4ee9db18c8e6a`), both in `decks/brews/drafts_2026-10-01/`.

## 3. Engine and pilots

- **Engine:** `rl/engine-2026-10-02/deckgym`, main-8626a35, the manifest's available release (what `current_engine.py`
  resolves), sha256 `2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e`.
- **Coverage tool:** the same release's `rl/engine-2026-10-02/goldfish`, sha256
  `cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66` (it plays no game here).
- **`decks/screen/floor.py`**, sha256 `8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a` (blob
  `ec133dab0b061a06199ff268ada501999c8c2f7d`). `analyze.py` imports it so that the trace helpers, the went-first reading,
  the coverage flags and the flagged-card counts are read exactly as the floor reads them. `run.sh` refuses another hash.
- **Pilots:** km3 on both sides (`--players km3,km3`), the working pilot of the screen and the floor. Every result file
  must name `KM { max_depth: 3 }` for both players.

## 4. The deals: seed block, formula and size

- **Seed block: 23,200,000,000 – 23,200,999,999.** New. It is above the last block in START_HERE's table (23,100,000,000 –
  23,100,999,999, the rules switch), inside Claude Code's diagnostics range (20,000,000,000 and up). A search of the
  text files under `C:\Users\dacz8\Projects` (this repository and the others there) on Oct 2 found no seed between
  23,101,000,000 and 23,999,999,999.
- **Formula.** The list under test in seat 0: seed 23,200,000,000 + i. In seat 1 (the Fire list in seat 0):
  23,200,000,500 + i. i = 0 to 499. **The same seeds for draft A and deck 13.** This is the floor's pattern (seat 1 at
  +500), with `deckgym simulate --seed-stream`: game j of a call with `--seed S` plays seed S + j.
- **A deal** is one (seat, seed). There are 1,000 deals, and each list plays all of them: **500 deals per seat per list,
  1,000 games per list, 2,000 games in all.** Fixed now: no games are added or dropped after looking.
- **Calls.** Chunks of 50 games: chunk c (0 to 9) of seat s plays `--seed 23,200,000,000 + 500 × s + 50 × c --num 50`.
  Every game keeps the seed it would have in one 500-game call; each result file's `game_seed` is checked.
- **Smokes: 23,200,900,000 and up.** Used twice so far, both on Oct 2, both draft A in seat 0 against the Fire list: a
  2-game smoke (seeds 23,200,900,000 and 23,200,900,001) to confirm the command line and the trace format and to test
  `analyze.py`, replayed once (the same two seeds and command) because WSL's `/tmp` did not survive between two calls; and,
  after the design review's changes to `analyze.py`, a 2-game smoke of the revised extraction and page (seeds
  23,200,900,002 and 23,200,900,003). All their files were deleted. Those games are not part of this test.
- "Same deal" means the same seed and seat. The two lists are different cards, so their own draws differ even on one seed.
  The paired interval (section 7) is valid either way; it is only narrower when results on a deal move together.

## 5. How it runs (`run.sh`)

`bash rl/results/draft_A_v_fire_2026-10-02/run.sh` in WSL or the cloud, from a git checkout. `--plan` runs every check
except the commit check and prints the 40 planned calls, playing and writing nothing.

1. **Refuses** before any game unless: this README, `run.sh` and `analyze.py` are committed and unmodified (each file on
   disk equals its blob in HEAD); `current_engine.py` resolves `rl/engine-2026-10-02/deckgym`; the manifest's available
   release is main-8626a35 with the sha256 above, and the program on disk has it; goldfish and floor.py have the hashes
   above; the three lists have the sha256 and blob ids of section 2. It also refuses a second copy of itself running.
2. **Records** in `provenance.txt` (appended at each start): the date, git HEAD, and the sha256 of deckgym, goldfish,
   floor.py, analyze.py, run.sh, this README, current_engine.py, project_manifest.json, `lib/deckgym-database.json`,
   `engine/src/players/public_pricing_player.rs` (floor.py reads its audited texts) and the three lists; Python, machine.
3. **Coverage:** floor.py's own call, `goldfish --deck <list> --panel decks/screen/opponents --games 0 --coverage <file>`
   from `engine/`, for each of the three lists, into `coverage/{draftA,deck13,opponent}_coverage.json`.
4. **Games:** 40 calls (2 lists × 2 seats × 10 chunks), each
   `deckgym simulate --num 50 --players km3,km3 --seed S --seed-stream --data-output <tmp> --results-output <tmp> -p A B`,
   at `nice -n 10`. The per-decision traces (about 2.5 MB a game) and result files go to `/tmp`. `analyze.py extract`
   checks the call: 50 result files, every game "completed", the seeds exactly S to S + 49, the card ids in each seat equal
   to the registered lists, both pilots km depth 3, the printed wins equal to the result files, and one trace file per ply.
   It then writes one record per game to `games/<list>_s<seat>_c<NN>.jsonl`, and the traces are deleted.
5. **Page:** `analyze.py report` writes `RESULTS.md`. It refuses unless the games are exactly the 2,000 registered ones,
   with none repeated.

Resumable: a finished chunk file is never replayed. Every output is written as `.part` and renamed when complete.
Time: the floor's 1,920 games with traces took about 3 minutes (`../floor_drafts_2026-10-02/timing.txt`), so expect
roughly 5 to 10 minutes with the extraction, using every core.

**Per-game record** (one JSON line): list, seat, seed, game id, outcome, won, draw, final points, final turn, plies,
lifecycle errors, went first, the last own turn reached; `attacks` [own turn, game turn, attacker, attack]; `evolves`
[own turn, game turn, the Pokémon evolved into, its spot]; `sharks` (each Turbo Shark: own turn, game turn, Benched Water
Pokémon at the time, outcome, target, Energy); `arms` (each Bench arming: own turn, target, the armed Pokémon's first later
attack or none, `evolved`: its first evolution after the arming [own turn, the Pokémon it evolved into] or none, own turn
it left play, tracking lost); tracking mismatches; own turns with two attacks; floor.py's per-turn tags for the flagged
cards; chunk; smoke flag.

## 6. The metrics (exact definitions)

Words used below:
- **Game turn** t: the engine's `turn_count` (turn 1 is the first player's first turn; 0 is setup).
- **Went first**: the list is the current player at game turn 1 (floor.py's reading).
- **Own turn**: the list's own turn number, (t + 1) / 2 rounded down if it went first, t / 2 if it went second. Own turn 1
  is its first turn.
- **An attack**: a decision of the list whose chosen action is Attack. **Attacker** = the name of the list's Active
  Pokémon at that decision. **Attack name** = the action's title.
- **A win**: the result file's outcome is a win for the list's seat. A draw is not a win; draws are counted and shown.

**6.1 Win rate.** Wins / games for each list (1,000 games each), with its interval (section 7).

**6.2 Paired difference.** For each deal d: D(d) = (draft A won d: 1 or 0) − (deck 13 won d: 1 or 0), so D is −1, 0 or
+1. The mean of D over the 1,000 deals equals draft A's win rate minus deck 13's. Its interval is in section 7. Also
shown: the number of deals both won, only draft A won, only deck 13 won, neither won; the same mean for each seat alone
(descriptive); and the number of deals on which the two lists did not both go first or both go second.

**6.3 Went first / went second, and seat.** For each list, the win rate in its games going first and going second, and in
seat 0 and seat 1, each with its Wilson interval.

**6.4 Attacks by own turn (both lists).** For each (attacker, attack name) and own turn 1, 2, 3, 4, 5, 6 and 7 or later:
the number of the list's attacks. A turn has at most one attack, so this is also a number of games. Shown with the number
of games that reached each own turn (the list was the current player on that own turn).

**6.5 Sharpedo's line (draft A).** As I read draft A's `.md` ("The plan, by turn"):
- **Which Sharpedo:** Mega Sharpedo ex (B4 035), evolved from Carvanha (B4 034); two of each in the list.
- **Which attack, and when:** Turbo Shark, first on the list's **own turn 2**, going first or second. Going second: Carvanha
  Active and given an Energy on own turn 1, evolved and attacking on own turn 2. Going first (no Energy and no evolving on
  turn 1): Carvanha placed on own turn 1, then Energy, evolve and Turbo Shark on own turn 2. The `.md`'s going-first
  paragraph says "one turn later for the first attack", but its own steps there put Turbo Shark on own turn 2; the reading
  taken is own turn 2 going first and going second, and the first-Turbo-Shark table (going first and going second
  separately) also shows turn 3.
- **The arming:** Turbo Shark's Energy goes on a Benched Water Pokémon. The plan's target is the Benched Alolan Vulpix, so
  that on **own turn 3** it evolves into Alolan Ninetales ex already holding one or two [W] ("the second attacker is armed by
  turn 3 without spending the turn's attachment on it").
- **Own turn 3:** Binding Snow from Alolan Ninetales ex, or Turbo Shark again (Mega Sharpedo ex retreats for free).
- Own turn 4 on (the second Mega Sharpedo ex, Irida, Lucky Ice Pop, Cape, Cyrus) is not measured beyond the attack table.

Per game, each step is yes or no:
- **L1** an Evolve into Mega Sharpedo ex chosen on own turn 2 or earlier;
- **L2** the list's attack on own turn 2 is Turbo Shark by Mega Sharpedo ex;
- **L3** that Turbo Shark armed the Bench (below), on any Benched Water Pokémon;
- **L3v** that Turbo Shark armed a Benched **Alolan Vulpix**: an arm of own turn 2 whose target (below) is Alolan Vulpix;
- **L4** an Evolve into Alolan Ninetales ex chosen on own turn 3 or earlier, from any Vulpix;
- **L4v** that armed Alolan Vulpix itself (followed as below) evolved into Alolan Ninetales ex on own turn 3 or earlier:
  an arm of own turn 2 with target Alolan Vulpix whose `evolved` is [own turn 3 or earlier, Alolan Ninetales ex];
- **L5** the list's attack on own turn 3 is Binding Snow by Alolan Ninetales ex, or Turbo Shark by Mega Sharpedo ex;
- **the line through turn 2** = L2 and L3; **the line through turn 3** = L2, L3, L4 and L5. These are the loose lines:
  the Energy may have gone on any Benched Water Pokémon, and the Ninetales ex may have come from another Vulpix;
- **the plan's line** = L2, L4v and L5: own turn 2's Turbo Shark put its Energy on the Benched Alolan Vulpix, that Vulpix
  was Alolan Ninetales ex by own turn 3, and own turn 3's attack was Binding Snow or Turbo Shark. This is draft A's plan
  as written; the loose lines are shown beside it.

Each is shown as a count and a share of all 1,000 draft A games (a game that ended before that own turn counts as no),
for all games, going first and going second, with the number of games that reached own turns 2 and 3. Also, each for all
games, going first and going second: own turn 2's Turbo Shark by where its Energy went (each arm target, or the reason
there was no arm, below; and the games with no Turbo Shark on own turn 2); the own turn of the first Turbo Shark (2, 3,
4, 5, 6 or later, never). And the win rate in games where the line through turn 2 happened and where it did not
(descriptive only, not cause and effect: games where the bot can play the line are also games with good draws).

**The Bench-arming count.** After Turbo Shark's damage the engine offers one Attach per Benched Water Pokémon (not the
turn's Energy: `is_turn_energy` false). A Turbo Shark **armed the Bench** when, after the list's Turbo Shark decision and
before its turn ended, the list chose such an Attach. The **target** is the Pokémon on that Bench spot at that moment. Every
Turbo Shark is exactly one of: armed; "no Benched Water Pokémon" (nothing on the Bench to arm when it attacked); "game
ended before the attach" (its Knock Out ended the game first); "no attach (other)" (expected 0). Shown: Turbo Sharks
(total, per game, games with at least one); arms (total, per game, share of Turbo Sharks), by target and by own turn.

**What the arming led to.** For each arm: whether the armed Pokémon later attacked from the Active Spot in that game, and
its first such attack (attacker and attack name); otherwise whether it left play first or was still in play at the end.
Also its first evolution after the arming (`evolved`: the own turn and the Pokémon it evolved into, from an Evolve the
list chose on the followed spot), or none. The Pokémon is followed by its spot: a retreat (paid at once, or through the
Energy choice that follows it) swaps the Active Spot and that Bench spot; a promotion moves that Bench spot to the Active
Spot; a switch by a card effect (the engine's `Activate` on the list's side, whichever player chooses it) swaps the
Active Spot and that Bench spot, as the engine applies it; an evolution keeps it (the same Pokémon). At every decision the
followed spot must still hold a Pokémon with the same first card (the Basic under any evolution); otherwise the arm
counts as "tracking lost" (a move not listed here would show up this way). Expected 0; the page shows the count.

**6.6 Coverage flags.** The official goldfish's `--coverage` on each of the three lists, read by floor.py's
`flagged_cards` with pilot km3 (so a text km3 prices drops out, as on the floor page): each flagged card with its reasons.
For draft A and deck 13 also the flagged card's use in these games, counted as floor.py counts it, under floor.py's default
role (for a flagged attack: chosen on the turns it could be chosen with that Pokémon Active). A coverage check on Oct 2
(no game played) gave: Alolan Ninetales ex's Binding Snow ("pays off during the opponent's turn, which the search doesn't
play out") in draft A and in deck 13; nothing in the Fire list. The run's own coverage files are the ones the page uses.

**6.7 Did Mega Sharpedo ex, Alolan Ninetales ex and Lapras attack at all (both lists).** For each list and each of the
three, counted separately, one row each: the number of the list's games in which that Pokémon was the attacker (the
words above) of at least one of the list's attacks, any of its attacks, out of the list's games, with the share; and its
attacks in all, summed over the list's games. A game counts in every row whose Pokémon attacked in it. By name: an attack
by Carvanha or Alolan Vulpix does not count for its Stage 1. Lapras is A3 044, draft A's one Lapras. A Pokémon not in the
list (Mega Sharpedo ex and Lapras in deck 13) shows "not in the list". Descriptive, with no reading attached. Asked for by
the coordinator: in Dustin's five pause games with draft A, Mega Sharpedo ex attacked in three and not at all in the other
two, where Alolan Ninetales ex and Lapras did the attacking.

## 7. Intervals

- **Each win rate:** the 95% Wilson score interval, z = 1.96. With p = wins / n: centre = (p + z²/(2n)) / (1 + z²/n),
  half-width = z / (1 + z²/n) × √(p(1 − p)/n + z²/(4n²)).
- **The paired difference:** mean of D ± 1.96 × s / √n, with n = 1,000 deals and s the standard deviation of the 1,000
  values of D (divisor n − 1): a normal interval on the per-deal differences. For scale: if the two lists' results on a deal
  were unrelated and both near 50%, s would be about 0.7 and the half-width about 4.4 points.
- The per-seat paired differences, the went-first and seat rates and the Sharpedo-line win rates use the same formulas
  and are descriptive.

## 8. What would count as "the premise holds" or "doesn't"

Fixed now. Descriptive, with no adoption decision:
- **Holds in this test:** the paired interval lies entirely above zero, that is, draft A's win rate against this list is
  above deck 13's by more than the paired interval.
- **Doesn't hold, no difference seen:** the paired interval includes zero.
- **Doesn't hold, reversed:** the paired interval lies entirely below zero (deck 13 did better on the same deals).

Beside the reading, and not changing it:
- If the point difference is under 5 points, the page says so: START_HERE calls a difference that size noise for two
  versions of one shell.
- Secondary, descriptive: whether draft A's own Wilson interval lies above 50%, below it, or around it.
- The Sharpedo-line counts (section 6.5, the plan's line first) and the attacked-at-all counts (6.7) say whether the bot
  actually played the line the draft describes. If it rarely did, a "doesn't hold" may be about how the bot plays the
  list rather than the plan (draft A's `.md`: Turbo Shark's Bench Energy is valued only through the position at the end
  of the search, and Binding Snow is flagged). The page reports this; it does not decide it.

Nothing here adopts, drops or ranks a list. What to do with the result is Dustin's call.

## 9. What this is not

Not a ranking. Not a ladder forecast. One opponent list (not Blaziken, not the other Fire lists on the ladder), played by
the bot on both sides. A good number here would say the plan works against this list when km3 plays both decks, and
nothing more.

## 10. The "main attacker" label

Draft A's floor page (`../floor_drafts_2026-10-02/draft-A-shark-tempo.md`) measured its "main attacker" as Alolan
Ninetales ex: floor.py's fallback when a list has no entry in `lib/brew_pages.py`, the Pokémon with the highest printed
damage (Binding Snow 80 beats Turbo Shark 70). Draft A's plan is built on Mega Sharpedo ex. The coordinator says Sonnet is
correcting that label. This test uses no "main attacker" label: it names Mega Sharpedo ex, Turbo Shark and the steps of
section 6.5 directly, from the list and the `.md`'s plan.

## 11. Proposed START_HERE seed-table row (for the integrator to add)

| Seeds | Used by |
|---|---|
| 23,200,000,000 – 23,200,999,999 | Claude Code, draft A v the Fire list (registered Oct 2, `rl/results/draft_A_v_fire_2026-10-02/README.md`): draft A and deck 13 each against the Charizard Y / Entei list, km3 on both sides; 23,200,000,000 + 500 × seat + i, i < 500, the same seeds for both lists, `--seed-stream` in calls of 50; 23,200,900,000 and up for smokes (23,200,900,000 – 23,200,900,003 used, Oct 2) |

## 12. Files

- This registration: `README.md`, `run.sh`, `analyze.py` (`python3 analyze.py --self-test` checks the interval formulas
  and, on a made-up game (no engine game), the arm tracking through a switch and an evolution, the section 6.5 steps and
  the section 6.7 counts).
- After the run: `provenance.txt`, `run.log`, `coverage/*.json` (3), `games/*.jsonl` (40 files, about 1.5 KB a game),
  `RESULTS.md`. If `analyze.py` and this README ever disagree on a definition, this README is the registration and the page
  is the thing to fix.
