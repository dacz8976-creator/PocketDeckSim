# Skip-attack comparison for the combined run (kx3_combined_v_frozen)

> **Oct 12: the exact measure now exists:** `SKIP_ATTACK_EXACT.md` in this folder (the cloud). It replays every game move for move
> on the program that played it and reads the legal moves at each decision. In short, the share of turns with a legal attack where no
> attack was made: candidate 5.0%, frozen kx3 3.7%, km3 2.3%; candidate − frozen +1.3 ± 1.1 points. The pre-registered measure (km3
> proposed an attack and none followed) is there too: candidate 8 turns, frozen kx3 8, km3 0; candidate − frozen +0.0 ± 0.4 points.
> The proxy counts below stand as what the records alone could show.

Sonnet "Opus agents progress", for the laptop and Fable; produced by `skip_attack.py` in this folder from the two `games.jsonl` files
(this run's and the development run's). Nothing was run: no engine, no cargo, no new games. The pre-registration (line 7) promised
a comparison of how often each bot skipped an attack it could have made; `PAIR_COMBINED.txt` does not contain it.

## 1. Short answer

**The traces cannot decide "an attack was available" at a decision point, so the pre-registered measure is not produced.** This is
said once here and the definitions are in section 2. What is below is what the files do show:

1. **Repeat-attacker turns (R)**, the closest proxy for "an attack was available": the candidate had 1061 such turns and did not attack on 85 (8.0 ± 1.7%); the frozen kx3 1032 and 71 (6.9 ± 1.6%); km3 973 and 58 (6.0 ± 1.5%), each over 560 games.
2. **Paired differences on R turns**, in points of did-not-attack share: candidate − frozen +1.1 ± 1.8; candidate − km3 +2.1 ± 1.8; frozen − km3 +0.9 ± 1.4.
3. Of the turns without an attack: the candidate retreated 41, chose EndTurn 27, was forced 17; frozen 22 / 28 / 21; km3 15 / 25 / 18. Paired, the candidate's share of R turns that ended in a Retreat without an attack is +1.7 ± 1.2 against the frozen kx3 and +2.3 ± 1.3 against km3.
4. **By group (Dustin's Oct 5 ask)**, did-not-attack share on R turns, candidate / frozen / km3: fast 7.1 / 7.3 / 4.7; setup 10.6 / 7.5 / 8.3; middle 4.5 / 5.0 / 3.6. Candidate − frozen: fast -0.2 ± 3.1, setup +3.2 ± 3.1, middle -0.5 ± 2.5 (points). The counts for every deck are in section 3, the paired differences in section 4.

## 2. What the log holds, what is used, and the definitions

**Files.** `games.jsonl` of this run (1120 games: 560 candidate arm X, 560 km3 arm ref) and of the development run
`rl/results/strength_2026-10-03_kx3_dev` (its arm X is the frozen kx3, on the same keys). The folder holds no `KX_TRACE` or other
decision record (besides `games.jsonl` it holds `errors.jsonl`, which is empty, `run_log.jsonl`, the manifest and configuration,
the reports and the two scripts). km3: this run's arm ref equals the development run's game for game and decision for decision
(560 of 560 reference games, `pair_combined.py`'s build check re-run on the fields it compares), so one set of km3 games serves
both runs. The pairing is `pair_combined.py`'s: the same (deck, opponent, deal, seat) key, 560 keys, the candidate against the
frozen kx3 against km3.

**Fields used.** Per game: `key`, `arm`, `deck`, `first` (which seat moved first: `deck` means the deck's turns are the odd game turns),
`turns`. Per logged decision of the deck's seat: `t` (game turn), `a` (the action, e.g. `Attack:Psychic`, `Retreat:2`, `EndTurn`), `act`
(the name of the deck's Active Pokémon before the action) and `n` (how many moves were offered). Not used: `ms`, `p`, `b`, `o`,
`moves_deck`, `moves_opp`, the outcomes. The log keeps only decisions with a real choice (`n` is never 1): a turn whose only legal
move was EndTurn leaves no entry for that move.

**Why "available" cannot be read off.** The log says how many moves were offered (`n`) but not which. When the bot chose EndTurn with
`n >= 2`, an attack may or may not have been among the other moves; the energy on the Active, its attack costs and the opponent's
effects are not logged. Rebuilding them from the log would mean replaying the engine, which is what the pre-registered
`trainer_habits scripted --attack-scan` does (I found no scan output for either arm in the repository, and the tool itself is not
under `rl/` or `engine/`). That replay is the way to get the exact measure.

**What can be shown, by turn.** The deck's *own turns* are the game turns of its parity, 1 up to the game's last turn. Each is exactly one of:
- **A**: the turn has an `Attack:` decision.
- **E**: no attack, and the last logged decision is the chosen `EndTurn` (with `n >= 2`): other moves were still legal. An attack may have been among them.
- **F**: no attack, and the last logged decision is not EndTurn (or none was logged): the final EndTurn was forced, nothing else was legal, so **no attack was available at the end of the turn**.

**Three sets of turns** (a game's turns are counted for each bot separately; a bot that plays differently has different sets):
- **after**: the own turns after the game's first attack turn. Context, not a skip measure: F turns (nothing to attack with, e.g. after a Knock Out) are in it.
- **R, repeat-attacker turns**: the Pokémon that is the Active at the start of the turn has the name of the Active that attacked on the previous own turn. This is the closest the log gets to "an attack was probably available": the same Pokémon, already charged for an attack, stayed in front. It is not certain: an attack that discards its own Energy, a Special Condition or an effect from the opponent's attack can leave nothing to use, and a different copy of the same name would be read as the same. Turns with no logged decision are not in R (the Active is not known).
- **R2**: R, and the same Pokémon (by name) also attacked two own turns back. Stricter, smaller.
On R turns, **did not attack** means not A, split into: a Retreat was played that turn (the attacker was moved out, whatever followed); the chosen EndTurn with other moves offered; a forced end.

**Intervals.** Shares are pooled over games (sum of the counts over the sum of the turns). The interval is ± 1.96 SE of the ratio estimator over
games: for each game the residual `(count - share * turns) / mean(turns)`, and for a difference between two bots on the same key the difference of the two
bots' residuals, SE = sqrt(sum of squares / (n (n - 1))). That is the pre-registration's mean ± 1.96 sd / sqrt(n) generalised to a rate whose
denominator differs by game. Group rows and deck rows are the same computation on their games (240, 240, 80; 80 per deck).

## 3. What the games show, per bot

Counts of the deck's own turns, summed over the games in each row (560 games per bot; 80 per deck). A = a turn with an attack; E = ended by the chosen EndTurn with other moves offered; F = ended with nothing else legal (the log shows no choice).

### candidate

| scope | games | own turns after the first attack: n | A | E | F | R turns | did not attack | share % | R2 turns | did not attack | share % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 560 | 1643 | 1394 | 120 | 129 | 1061 | 85 | 8.0 | 397 | 19 | 4.8 |
| fast | 240 | 614 | 549 | 39 | 26 | 368 | 26 | 7.1 | 96 | 5 | 5.2 |
| setup | 240 | 728 | 567 | 73 | 88 | 451 | 48 | 10.6 | 205 | 9 | 4.4 |
| middle | 80 | 301 | 278 | 8 | 15 | 242 | 11 | 4.5 | 96 | 5 | 5.2 |
| 06-mega-blaziken-tournament-list (fast) | 80 | 218 | 204 | 10 | 4 | 130 | 8 | 6.2 | 27 | 2 | 7.4 |
| 09-mega-manectric-heliolisk (fast) | 80 | 211 | 199 | 10 | 2 | 141 | 4 | 2.8 | 37 | 0 | 0.0 |
| 10-xatu-oricorio-tr-weezing (fast) | 80 | 185 | 146 | 19 | 20 | 97 | 14 | 14.4 | 32 | 3 | 9.4 |
| 01-muk-glimmora-kingambit-regigigas (setup) | 80 | 250 | 171 | 32 | 47 | 97 | 9 | 9.3 | 22 | 3 | 13.6 |
| 03-wailord-indeedee-wall (setup) | 80 | 226 | 193 | 16 | 17 | 178 | 12 | 6.7 | 99 | 2 | 2.0 |
| 05-indeedee-stoutland (setup) | 80 | 252 | 203 | 25 | 24 | 176 | 27 | 15.3 | 84 | 4 | 4.8 |
| draft-A-shark-tempo (middle) | 80 | 301 | 278 | 8 | 15 | 242 | 11 | 4.5 | 96 | 5 | 5.2 |

### frozen

| scope | games | own turns after the first attack: n | A | E | F | R turns | did not attack | share % | R2 turns | did not attack | share % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 560 | 1627 | 1370 | 116 | 141 | 1032 | 71 | 6.9 | 380 | 18 | 4.7 |
| fast | 240 | 651 | 572 | 44 | 35 | 383 | 28 | 7.3 | 100 | 9 | 9.0 |
| setup | 240 | 690 | 535 | 64 | 91 | 429 | 32 | 7.5 | 192 | 5 | 2.6 |
| middle | 80 | 286 | 263 | 8 | 15 | 220 | 11 | 5.0 | 88 | 4 | 4.5 |
| 06-mega-blaziken-tournament-list (fast) | 80 | 230 | 209 | 13 | 8 | 129 | 8 | 6.2 | 22 | 4 | 18.2 |
| 09-mega-manectric-heliolisk (fast) | 80 | 221 | 206 | 9 | 6 | 142 | 9 | 6.3 | 29 | 1 | 3.4 |
| 10-xatu-oricorio-tr-weezing (fast) | 80 | 200 | 157 | 22 | 21 | 112 | 11 | 9.8 | 49 | 4 | 8.2 |
| 01-muk-glimmora-kingambit-regigigas (setup) | 80 | 251 | 164 | 35 | 52 | 95 | 7 | 7.4 | 21 | 1 | 4.8 |
| 03-wailord-indeedee-wall (setup) | 80 | 214 | 182 | 9 | 23 | 170 | 7 | 4.1 | 94 | 2 | 2.1 |
| 05-indeedee-stoutland (setup) | 80 | 225 | 189 | 20 | 16 | 164 | 18 | 11.0 | 77 | 2 | 2.6 |
| draft-A-shark-tempo (middle) | 80 | 286 | 263 | 8 | 15 | 220 | 11 | 5.0 | 88 | 4 | 4.5 |

### km3

| scope | games | own turns after the first attack: n | A | E | F | R turns | did not attack | share % | R2 turns | did not attack | share % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 560 | 1617 | 1311 | 145 | 161 | 973 | 58 | 6.0 | 358 | 14 | 3.9 |
| fast | 240 | 630 | 565 | 39 | 26 | 380 | 18 | 4.7 | 114 | 6 | 5.3 |
| setup | 240 | 710 | 500 | 93 | 117 | 396 | 33 | 8.3 | 176 | 4 | 2.3 |
| middle | 80 | 277 | 246 | 13 | 18 | 197 | 7 | 3.6 | 68 | 4 | 5.9 |
| 06-mega-blaziken-tournament-list (fast) | 80 | 226 | 212 | 8 | 6 | 123 | 5 | 4.1 | 33 | 2 | 6.1 |
| 09-mega-manectric-heliolisk (fast) | 80 | 194 | 183 | 10 | 1 | 137 | 5 | 3.6 | 32 | 1 | 3.1 |
| 10-xatu-oricorio-tr-weezing (fast) | 80 | 210 | 170 | 21 | 19 | 120 | 8 | 6.7 | 49 | 3 | 6.1 |
| 01-muk-glimmora-kingambit-regigigas (setup) | 80 | 266 | 151 | 42 | 73 | 82 | 4 | 4.9 | 19 | 1 | 5.3 |
| 03-wailord-indeedee-wall (setup) | 80 | 236 | 183 | 27 | 26 | 167 | 5 | 3.0 | 94 | 1 | 1.1 |
| 05-indeedee-stoutland (setup) | 80 | 208 | 166 | 24 | 18 | 147 | 24 | 16.3 | 63 | 2 | 3.2 |
| draft-A-shark-tempo (middle) | 80 | 277 | 246 | 13 | 18 | 197 | 7 | 3.6 | 68 | 4 | 5.9 |

## 4. Paired differences (same deck, opponent, deal and seat in both arms)

Each cell: the first bot's pooled share minus the second's, in percentage points, ± 1.96 SE (the ratio estimator over games, paired on the key; see section 2). Positive in a *did-not-attack* column = the first bot skipped more.

### candidate − frozen

| scope | after: attack share | after: chose-to-end share | R: did-not-attack share | R: retreated-instead share | R: chose-EndTurn share | R2: did-not-attack share |
|---|---|---|---|---|---|---|
| all | +0.6 ± 2.1 | +0.2 ± 1.5 | +1.1 ± 1.8 | +1.7 ± 1.2 | -0.2 ± 1.2 | +0.0 ± 2.5 |
| fast | +1.5 ± 2.8 | -0.4 ± 2.3 | -0.2 ± 3.1 | +0.6 ± 1.7 | +0.9 ± 2.1 | -3.8 ± 6.1 |
| setup | +0.3 ± 3.7 | +0.8 ± 2.6 | +3.2 ± 3.1 | +3.4 ± 2.3 | -0.1 ± 1.8 | +1.8 ± 3.1 |
| middle | +0.4 ± 3.5 | -0.1 ± 2.3 | -0.5 ± 2.5 | +0.2 ± 1.9 | -1.9 ± 2.1 | +0.7 ± 5.0 |
| 06-mega-blaziken-tournament-list (fast) | +2.7 ± 4.7 | -1.1 ± 3.8 | -0.0 ± 5.5 | +0.8 ± 1.5 | +0.7 ± 3.9 | -10.8 ± 18.9 |
| 09-mega-manectric-heliolisk (fast) | +1.1 ± 4.4 | +0.7 ± 3.4 | -3.5 ± 4.0 | -0.7 ± 2.4 | -0.7 ± 2.4 | -3.4 ± 6.7 |
| 10-xatu-oricorio-tr-weezing (fast) | +0.4 ± 5.4 | -0.7 ± 4.9 | +4.6 ± 7.1 | +2.3 ± 4.7 | +3.6 ± 5.1 | +1.2 ± 9.2 |
| 01-muk-glimmora-kingambit-regigigas (setup) | +3.1 ± 5.6 | -1.1 ± 3.5 | +1.9 ± 5.8 | +6.2 ± 4.7 | -2.1 ± 2.8 | +8.9 ± 12.5 |
| 03-wailord-indeedee-wall (setup) | +0.4 ± 8.1 | +2.9 ± 5.4 | +2.6 ± 4.0 | -0.1 ± 2.3 | +1.6 ± 2.9 | -0.1 ± 4.0 |
| 05-indeedee-stoutland (setup) | -3.4 ± 5.5 | +1.0 ± 4.7 | +4.4 ± 6.1 | +5.3 ± 4.9 | -0.8 ± 3.2 | +2.2 ± 4.8 |
| draft-A-shark-tempo (middle) | +0.4 ± 3.5 | -0.1 ± 2.3 | -0.5 ± 2.5 | +0.2 ± 1.9 | -1.9 ± 2.1 | +0.7 ± 5.0 |

### candidate − km3

| scope | after: attack share | after: chose-to-end share | R: did-not-attack share | R: retreated-instead share | R: chose-EndTurn share | R2: did-not-attack share |
|---|---|---|---|---|---|---|
| all | +3.8 ± 2.7 | -1.7 ± 2.0 | +2.1 ± 1.8 | +2.3 ± 1.3 | -0.0 ± 1.2 | +0.9 ± 2.3 |
| fast | -0.3 ± 2.7 | +0.2 ± 2.4 | +2.3 ± 2.7 | +1.6 ± 1.6 | +1.4 ± 2.0 | -0.1 ± 4.3 |
| setup | +7.5 ± 5.1 | -3.1 ± 3.7 | +2.3 ± 3.3 | +3.4 ± 2.4 | -1.1 ± 2.2 | +2.1 ± 3.3 |
| middle | +3.6 ± 4.4 | -2.0 ± 3.5 | +1.0 ± 2.9 | +1.1 ± 2.3 | -0.1 ± 1.3 | -0.7 ± 5.2 |
| 06-mega-blaziken-tournament-list (fast) | -0.2 ± 4.7 | +1.0 ± 3.8 | +2.1 ± 5.0 | +1.5 ± 2.1 | +2.2 ± 3.4 | +1.3 ± 9.8 |
| 09-mega-manectric-heliolisk (fast) | -0.0 ± 4.3 | -0.4 ± 3.9 | -0.8 ± 3.1 | +1.4 ± 2.0 | -1.5 ± 2.8 | -3.1 ± 6.1 |
| 10-xatu-oricorio-tr-weezing (fast) | -2.0 ± 5.6 | +0.3 ± 5.0 | +7.8 ± 6.6 | +2.5 ± 4.6 | +4.7 ± 4.8 | +3.3 ± 8.7 |
| 01-muk-glimmora-kingambit-regigigas (setup) | +11.6 ± 8.0 | -3.0 ± 5.8 | +4.4 ± 6.8 | +5.0 ± 5.5 | +1.0 ± 2.0 | +8.4 ± 17.2 |
| 03-wailord-indeedee-wall (setup) | +7.9 ± 11.6 | -4.4 ± 7.7 | +3.7 ± 3.9 | +1.1 ± 1.5 | +1.0 ± 2.8 | +1.0 ± 3.5 |
| 05-indeedee-stoutland (setup) | +0.7 ± 6.8 | -1.6 ± 5.8 | -1.0 ± 7.1 | +4.6 ± 5.5 | -4.6 ± 5.1 | +1.6 ± 5.1 |
| draft-A-shark-tempo (middle) | +3.6 ± 4.4 | -2.0 ± 3.5 | +1.0 ± 2.9 | +1.1 ± 2.3 | -0.1 ± 1.3 | -0.7 ± 5.2 |

### frozen − km3

| scope | after: attack share | after: chose-to-end share | R: did-not-attack share | R: retreated-instead share | R: chose-EndTurn share | R2: did-not-attack share |
|---|---|---|---|---|---|---|
| all | +3.1 ± 2.5 | -1.8 ± 1.7 | +0.9 ± 1.4 | +0.6 ± 1.0 | +0.1 ± 0.9 | +0.8 ± 2.0 |
| fast | -1.8 ± 1.9 | +0.6 ± 1.7 | +2.6 ± 2.1 | +1.0 ± 1.2 | +0.5 ± 1.4 | +3.7 ± 4.3 |
| setup | +7.1 ± 4.6 | -3.8 ± 3.3 | -0.9 ± 2.5 | +0.0 ± 1.7 | -1.0 ± 1.6 | +0.3 ± 2.8 |
| middle | +3.1 ± 5.0 | -1.9 ± 3.4 | +1.4 ± 3.0 | +0.8 ± 2.3 | +1.8 ± 1.8 | -1.3 ± 4.1 |
| 06-mega-blaziken-tournament-list (fast) | -2.9 ± 4.0 | +2.1 ± 3.4 | +2.1 ± 3.9 | +0.8 ± 1.5 | +1.5 ± 3.1 | +12.1 ± 16.1 |
| 09-mega-manectric-heliolisk (fast) | -1.1 ± 2.0 | -1.1 ± 1.8 | +2.7 ± 3.3 | +2.1 ± 2.4 | -0.8 ± 2.4 | +0.3 ± 1.2 |
| 10-xatu-oricorio-tr-weezing (fast) | -2.5 ± 3.7 | +1.0 ± 3.6 | +3.2 ± 4.1 | +0.1 ± 2.5 | +1.1 ± 1.8 | +2.0 ± 4.2 |
| 01-muk-glimmora-kingambit-regigigas (setup) | +8.6 ± 6.4 | -1.8 ± 5.6 | +2.5 ± 4.8 | -1.2 ± 2.3 | +3.2 ± 3.4 | -0.5 ± 13.1 |
| 03-wailord-indeedee-wall (setup) | +7.5 ± 11.6 | -7.2 ± 6.9 | +1.1 ± 2.4 | +1.2 ± 1.6 | -0.6 ± 1.2 | +1.1 ± 2.1 |
| 05-indeedee-stoutland (setup) | +4.2 ± 5.2 | -2.6 ± 4.0 | -5.4 ± 5.8 | -0.7 ± 4.1 | -3.8 ± 3.7 | -0.6 ± 5.8 |
| draft-A-shark-tempo (middle) | +3.1 ± 5.0 | -1.9 ± 3.4 | +1.4 ± 3.0 | +0.8 ± 2.3 | +1.8 ± 1.8 | -1.3 ± 4.1 |

### Each bot's own pooled shares (± 1.96 SE), for reading the differences against

| bot | scope | after: attack share | after: chose-to-end share | R: did-not-attack share | R: retreated-instead share | R: chose-EndTurn share | R2: did-not-attack share |
|---|---|---|---|---|---|---|---|
| candidate | all | 84.8 ± 2.2 | 7.3 ± 1.5 | 8.0 ± 1.7 | 3.9 ± 1.2 | 2.5 ± 0.9 | 4.8 ± 2.1 |
| candidate | fast | 89.4 ± 2.7 | 6.4 ± 1.9 | 7.1 ± 2.7 | 2.2 ± 1.5 | 3.8 ± 1.9 | 5.2 ± 4.5 |
| candidate | setup | 77.9 ± 3.7 | 10.0 ± 2.7 | 10.6 ± 3.0 | 6.2 ± 2.3 | 2.7 ± 1.5 | 4.4 ± 2.8 |
| candidate | middle | 92.4 ± 4.1 | 2.7 ± 2.2 | 4.5 ± 2.6 | 2.1 ± 1.8 | 0.4 ± 0.8 | 5.2 ± 4.6 |
| frozen | all | 84.2 ± 2.2 | 7.1 ± 1.3 | 6.9 ± 1.6 | 2.1 ± 0.9 | 2.7 ± 1.0 | 4.7 ± 2.3 |
| frozen | fast | 87.9 ± 2.9 | 6.8 ± 2.0 | 7.3 ± 2.8 | 1.6 ± 1.2 | 2.9 ± 1.7 | 9.0 ± 6.2 |
| frozen | setup | 77.5 ± 3.9 | 9.3 ± 2.3 | 7.5 ± 2.6 | 2.8 ± 1.6 | 2.8 ± 1.6 | 2.6 ± 2.2 |
| frozen | middle | 92.0 ± 3.7 | 2.8 ± 1.8 | 5.0 ± 2.9 | 1.8 ± 1.8 | 2.3 ± 2.0 | 4.5 ± 4.4 |
| km3 | all | 81.1 ± 2.8 | 9.0 ± 1.8 | 6.0 ± 1.5 | 1.5 ± 0.8 | 2.6 ± 1.0 | 3.9 ± 2.0 |
| km3 | fast | 89.7 ± 2.5 | 6.2 ± 1.8 | 4.7 ± 2.1 | 0.5 ± 0.7 | 2.4 ± 1.5 | 5.3 ± 4.1 |
| km3 | setup | 70.4 ± 5.0 | 13.1 ± 3.3 | 8.3 ± 2.8 | 2.8 ± 1.6 | 3.8 ± 1.9 | 2.3 ± 2.2 |
| km3 | middle | 88.8 ± 5.1 | 4.7 ± 3.5 | 3.6 ± 2.5 | 1.0 ± 1.4 | 0.5 ± 1.0 | 5.9 ± 5.4 |

## 5. The repeat-attacker turns that did not end in an attack

Counts of the R turns, by what happened (a turn is in exactly one column): an attack; no attack and a Retreat was played that turn; no attack, no Retreat, and the turn ended by the chosen EndTurn with other moves offered; no attack, no Retreat, and the end was forced (nothing else legal).

| bot | scope | R turns | attacked | retreated, no attack | chose EndTurn | forced end |
|---|---|---|---|---|---|---|
| candidate | all | 1061 | 976 | 41 | 27 | 17 |
| candidate | fast | 368 | 342 | 8 | 14 | 4 |
| candidate | setup | 451 | 403 | 28 | 12 | 8 |
| candidate | middle | 242 | 231 | 5 | 1 | 5 |
| frozen | all | 1032 | 961 | 22 | 28 | 21 |
| frozen | fast | 383 | 355 | 6 | 11 | 11 |
| frozen | setup | 429 | 397 | 12 | 12 | 8 |
| frozen | middle | 220 | 209 | 4 | 5 | 2 |
| km3 | all | 973 | 915 | 15 | 25 | 18 |
| km3 | fast | 380 | 362 | 2 | 9 | 7 |
| km3 | setup | 396 | 363 | 11 | 15 | 7 |
| km3 | middle | 197 | 190 | 2 | 1 | 4 |

The attack the same Pokémon had used on the previous own turn, on the R turns without an attack (all 560 games per bot; the ten most common). An attack that discards its own Energy would explain a turn without an attack by itself; none of these names is looked up here.

| bot | previous attack (count) |
|---|---|
| candidate | Psychic 12; Tackle 11; Supernatural Feather 11; Whale Pump 7; Sharp Fang 6; Binding Snow 5; Wondrous Waves 4; Peck 4; Turbo Shark 4; Venomous Hit 3 |
| frozen | Tackle 8; Psychic 8; Supernatural Feather 8; Sharp Fang 6; Quick Attack 5; Venomous Hit 4; Wondrous Waves 4; Binding Snow 4; Tongue Whip 3; Sunny Scorching 3 |
| km3 | Psychic 15; Tackle 8; Supernatural Feather 6; Sharp Fang 4; Venomous Hit 3; Wave Splash 3; Peck 3; Wondrous Waves 2; Tongue Whip 2; Electrispark 2 |

## 6. Reading and limits

- On R turns the candidate does not skip measurably more than the frozen kx3 (candidate − frozen +1.1 ± 1.8), and is above km3 (candidate − km3 +2.1 ± 1.8; the interval just excludes zero). The one pattern that stands out is the Retreat: 41 R turns ended with a Retreat and no attack for the candidate, 22 for the frozen kx3, 15 for km3; as a share of R turns the candidate's is +1.7 ± 1.2 against the frozen kx3 and +2.3 ± 1.3 against km3 (both intervals exclude zero).
- By group, candidate − frozen on R turns: fast -0.2 ± 3.1 (includes zero); setup +3.2 ± 3.1 (excludes zero); middle -0.5 ± 2.5 (includes zero). Candidate − km3: fast +2.3 ± 2.7 (includes zero); setup +2.3 ± 3.3 (includes zero); middle +1.0 ± 2.9 (includes zero).
- The two decks with the highest did-not-attack share on R turns, per bot: candidate 05-indeedee-stoutland (15.3%) and 10-xatu-oricorio-tr-weezing (14.4%); frozen 05-indeedee-stoutland (11.0%) and 10-xatu-oricorio-tr-weezing (9.8%); km3 05-indeedee-stoutland (16.3%) and 10-xatu-oricorio-tr-weezing (6.7%). A deck's own pattern is in every bot's numbers.

- **Not the pre-registered measure.** "Km3 proposed an attack, kx3 played something else, and no attack followed that turn" needs km3's proposal at each of the candidate's decisions, which only a replay gives. R turns are a subset where an attack was probably available, chosen from the log alone; they are about 32% of the own turns, and they leave out the turns where the attacker changed (a new Pokémon was promoted or switched in), where skips may also happen.
- **The sets are each bot's own.** A bot's R turns exist because it attacked last turn, so a bot that skips more earlier has fewer R turns. The paired differences compare each bot's pooled share on its own R turns, not the same turns.
- **Deck effects are large** (the line above): the differences between bots within a deck are mostly inside their intervals, which are for the number of games shown (80 per deck, 240 per group, 560 pooled).
- **Many cells.** Sections 3 and 4 show 3 contrasts x 11 rows x 6 measures at 95%; some will exclude zero by chance. Nothing here was pre-registered as a test, and the retreat figures in section 1 are the ones picked out after looking.
- **A Retreat without an attack is not shown to be a mistake.** It can be a sound move (a damaged attacker moved out, its replacement not yet charged); the table only counts it.
- **Nothing is decided on this.** The pre-registered reading (the pooled interval for the score) is in `PAIR_COMBINED.txt` and is unchanged by it.
