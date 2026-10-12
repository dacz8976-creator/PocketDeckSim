# The exact attack-skip measure for the combined run (the cloud, Oct 12)

The pre-registration (line 7) promised a measure of how often each bot skipped an attack it could have made. `SKIP_ATTACK.md`
could not produce it from the game records: the log says how many moves were offered, not which, so it can't tell whether an
attack was among them. This file gives the exact measure. It comes from replaying every recorded game move for move on the
program that played it, and reading the legal moves at each of the bot's decisions. No game was played again and no bot or engine
changed. How it was done is in `skip_exact/README.md`.

## Oct 12 update: the pre-registered measure, the boards, and the laptop's review

**The pre-registered measure now exists, and it shows no difference.** The pre-registration counts a turn where km3, asked at the
same decision, proposed an attack, the bot played something else, and no attack followed that turn. km3 was asked at every decision
with a legal attack, from the same position and the same search randomness the engine gave the bot there in play.

| Bot | Turns where km3 proposed an attack | No attack that turn | Share |
|---|---:|---:|---:|
| candidate | 1,892 | 8 | 0.4 ± 0.3% |
| frozen kx3 | 1,896 | 8 | 0.4 ± 0.3% |
| km3 | 1,849 | 0 | 0 (by construction) |

- **Candidate − frozen: +0.0 ± 0.4 points.** By group: fast +0.2 ± 0.7, setup −0.1 ± 0.6, middle 0.0.
- **The frozen kx3's 8 is the development run's own count:** its attack scan (`playout_attack_skip_2026-10-07/` on
  claude/playout-pilot) found 8.
- **What this means:** almost all of the skip turns below (101, 73, 43) are turns where km3 would not have attacked either. The
  candidate does not leave km3's attack more often than the frozen kx3. The skip bar `_zs3` acts only on those few turns, so this
  measure can't show it working: 8 against 8.
- **Where the columns are:** `km3_move` and `km3_attacked` are on every decision line (`skip_exact/decisions_*.jsonl.gz`) and in
  `skip_exact/skip_turns.tsv`. The full table is `skip_exact/exact_summary.txt`.

**The turn-level measure below is not the pre-registered one.** It counts any turn with a legal attack and none made. The
pre-registered turns are a strict subset of these (8 of the frozen kx3's 73).

**About 23% of games were matched by trial in the first run (cf2f27ca).** Some move labels fit more than one legal move:
- DiscardOwnCards after Supernatural Feather (deck 10);
- ApplyDamage after Tongue Whip (deck 06);
- DiscardToolFromPokemon after Field Blower;
- MoveRandomOpponentEnergyToActive.

The first replay tried options until one fit the log.
- That happened in 130 candidate, 134 frozen and 131 km3 games, and needed retries in 68, 71 and 75.
- **The laptop's sensitivity** (REVIEW_SKIP_EXACT_laptop.md on main). Candidate − frozen is:
  - +1.3 ± 1.1 on all games;
  - +0.8 ± 1.2 without the ambiguous games;
  - +0.7 ± 1.1 without the retried games;
  - +1.0 ± 1.1 when each game is cut at its first ambiguous choice.
- Deck 10's +3.0 ± 2.7 becomes −0.1 ± 3.8 under that cut.
- **Now:** at such a label, the replay asks the pilot that played (km3, or that arm's kx3) for its move, from the same observation
  and search randomness. Neither bot keeps memory between decisions, so that is the move it made in play.
  - Every ambiguous label in every game was resolved this way; none is matched by trial any more.
  - In km3's own games the proof is direct: km3's answer equals its recorded move at all 15,355 decisions. Before this change,
    18 decisions in 10 trial-matched games differed.
  - The 217 skip turns came out the same, row for row. So no number in this file changed, but the trial-matched games no longer
    carry the doubt.

**The identity check is stricter.**
- Besides each decision's move, turn and number of legal moves, it now compares the points, the Active and the Bench count logged at
  each decision, and each game's plies and the opponent's number of decisions. Every game passes.
- **Negative controls**, 2 records for every deck and arm (42 records), each changed one way:
  - a wrong seed: 42 of 42 caught;
  - one logged move replaced by another label from the same game: 42 of 42 caught;
  - a wrong opponent pilot (km2 for km3): 39 of 42 caught. In the other 3 (05 v Lucario 2|1, 10 v Weezing 1|0, draft A v Blaziken
    3|0), the record holds only how many decisions the opponent made, not which moves. km2 evidently made moves that left every
    recorded field the same, so no check against these records can see it (`skip_exact/negative_control.txt`).

**Boards for every skip turn: `skip_exact/skip_boards.jsonl`.** It has one record for each of the bot's decisions in the 217 skip
turns, 1,139 in all. Each record has:
- both Actives and Benches: HP and max HP, Energy, Tools, Special Conditions;
- our hand and deck count, the points and the turn;
- the legal moves, the one taken and km3's proposal;
- each legal attack's expected damage to their Active and its chance to Knock it Out;
- their Active's attacks with cost, expected damage and Knock Out chance against ours.

The laptop's 13 hand-check turns are among these. How the forecast is made, and its limits, are in `skip_exact/README.md`.

## Short answer

**The candidate kx3 skips a little more often than the frozen kx3, and both skip more often than km3.** A "skip turn" is one of the
deck's turns where an attack was legal at some point and the bot attacked at no point that turn.

| Bot | Turns with a legal attack | Skip turns | Share | Games with one or more |
|---|---:|---:|---:|---:|
| candidate (kx3 `_tools _zs3 _m64`) | 2,034 | 101 | 5.0 ± 1.0% | 83 of 560 |
| frozen kx3 (the development run) | 1,981 | 73 | 3.7 ± 0.8% | 67 of 560 |
| km3 (the reference arm) | 1,892 | 43 | 2.3 ± 0.7% | 42 of 560 |

Paired on the same 560 deals (the same deck, opponent, deal and seat), in percentage points of the share:
- **candidate − frozen: +1.3 ± 1.1.** The interval is just above zero.
- candidate − km3: +2.7 ± 1.1.
- frozen − km3: +1.4 ± 0.8.

**By group (Dustin's Oct 5 ask), skip-turn share, candidate / frozen / km3:**
- fast (09, 06, 10): 4.6 / 2.7 / 1.6%; candidate − frozen +2.0 ± 1.5, entirely above zero.
- setup (03, 01, 05): 6.5 / 4.9 / 3.5%; candidate − frozen +1.6 ± 1.9.
- middle (draft A): 2.2 / 3.4 / 1.2%; candidate − frozen −1.2 ± 1.9.

By deck, one candidate − frozen interval is entirely above zero: 10 (Xatu), +3.0 ± 2.7 (15 skip turns against 8). None is
entirely below. Deck 05 (Indeedee Stoutland) skips the most for every bot: 10.6 / 8.9 / 7.6%. Every row is in
`skip_exact/exact_summary.txt`.

**What a skip turn usually is.** Most skip turns include a Retreat: the candidate 68 of 101, the frozen kx3 50 of 73, km3 35 of 43.
The bot moved its attacker out instead of attacking. The most common legal attack on a skip turn is Tackle, then Supernatural
Feather. Whether a skip was a good idea isn't decided here: the measure says an attack was legal and none was made, not that the
attack was worth making (a 10-damage Tackle can be the right one to pass up). The laptop's hand check of a sample answers that.

## The list for a hand check

`skip_exact/skip_turns.tsv` has one row per skip turn (217 rows: 101 candidate, 73 frozen, 43 km3). Each row has:
- the bot;
- the game key (deck | opponent | deal | seat | arm), which finds the game in this folder's `games.jsonl` (the frozen kx3's in
  `../strength_2026-10-03_kx3_dev/games.jsonl`);
- the game turn;
- the deck side's decision numbers that turn (counting from 0, as in the game's log);
- the attacks that were legal;
- every move the bot made that turn.

## The decision-level count (as asked, with a caution)

At the decision level, an attack was legal at 5,523 of the candidate's decisions, and the move taken was not an attack at 65.0 ± 1.0%
of them. The frozen kx3 is at 63.6 ± 1.0% of 5,241, km3 at 63.4 ± 1.0% of 5,049. Paired: candidate − frozen +1.4 ± 0.8, candidate −
km3 +1.6 ± 1.0.

**Read the turn level, not this.** Most of these "not an attack" decisions are the normal moves made before attacking in the same turn:
attach an Energy, evolve, play a Trainer, then attack. A turn with five setup moves and then an attack counts five here. The turn level
counts a turn only when no attack followed. The per-decision list is `skip_exact/skip_decisions.tsv.gz`; its last column says whether
an attack came later that turn.

## How sure this is

- **Every game replayed exactly:** 560 of 560 for each bot.
  - Every logged decision was found among the legal moves, with the logged turn, number of legal moves, points, Active and Bench
    count.
  - The points, turns, winner, plies and the opponent's number of decisions are the recorded ones.
  - Since Oct 12, every ambiguous label is resolved by the pilot that played.
- **The right program for each set:**
  - the candidate's and km3's games on the combined run's program source (172cbe9c, engine tree 69a5a441);
  - the frozen kx3's on the development run's (d513e37b, engine tree 31dbd2e6).
  - The engine outside `players/` is the same in both. km3's games give byte-for-byte the same decisions on both builds.
- **Deck files:** both runs' manifests match the deck files used, by sha256.
- **The replay check catches a wrong record:** a wrong seed and a changed label, 42 of 42 each; a wrong opponent pilot, 39 of 42
  (see the Oct 12 update above).
- **Why the replay is exact without the bots thinking:**
  - the engine gives each decision its own search randomness, separate from the shuffles and coin flips;
  - km3 plays its own side as it did;
  - the deck side plays the logged moves.
  - So the game is the same one. kx3's play-outs run only where kx3 is asked to resolve an ambiguous label.
- **What this measure is, against the pre-registration's wording.** The pre-registration defined a skip turn relative to km3's
  proposal ("where km3 proposed an attack, kx3 played something else and no attack followed that turn"). This file uses what Fable
  asked for: an attack was legal, and none followed that turn. That counts every legal attack, not only the ones km3 would have made,
  and it applies to km3 itself.
- **One small blind spot:** a turn whose only legal move was an attack isn't a decision, so it isn't counted. In practice EndTurn is
  always legal in the main part of a turn.
