# ky3 phase 1: what each case is expected to show (written Oct 15, before any gate run)

Source: `DESIGN_NOTE.md` and `DESIGN_NOTE_CASES.md` (read from origin/main). Nothing here is measured. "Baseline" is what the
records already show; "to measure" means gate 0 (km3, F and ky3 with no switch, the same 12 seeds) fills it in. Gate 0 decides each
case's role: a case is a **positive** only if the baseline meets its property in at most 8 of 12; otherwise it is a **keep check**.

Skip rule (confirmed by the coordinator, Oct 15): a skip stands when the mean is at least the threshold AND the mean is more than 2 SE above 0 (not mean minus 2 SE at least the threshold). Kept.

Pass rules (gate 1). Positive: 10 or more of 12 and at least 4 above the baseline. Negative or keep check: no seed loses what the
baseline had. A negative counts only if `_atk` looked in at least 6 of its 12 replays; otherwise it is "not exercised". Since the M2 fix `_atk` writes "_atk looked: ..." or "_atk: ... played instead" on every look, including "no attack does anything", "effects failed" and "play-outs failed", so 10 v Altaria 1|0 t7 reads as looked.
`_punch` and `_queue` are judged by their unit tests. The all-switches run must meet every switch's rules, and a failing negative
stops its switch. A failing right-to-pass case blocks adoption even when it is reported as a known limit.

## A. `_atk` expected positives (F's own skips)

| case | property (any seed meeting it counts) | baseline |
|---|---|---|
| 01 v Hydreigon 0\|1 t9 | Giga Turbo this turn | F skipped in its 1 recorded game; rest to measure |
| 05 v Lucario 3\|0 t5 | Indeedee ex's Psychic knocks out the 30-HP Bonsly | F skipped; `_zs3` lets it stand (3.4 SE); to measure |
| 06 v Lucario 4\|1 t3 | an attack this turn (Peck) | F skipped; to measure |
| 09 v Hydreigon 4\|0 t2 | Thunder Shock this turn | F skipped; to measure |
| 09 v Suicune 4\|1 t4 | Lightning Accelerator, Mega Manectric ex kept in front (a skip case, not exposure) | F skipped; to measure |
| 034953 t14 (pg_pos) | Metal Arms knocks out Happiny this turn | F 5 of 12 at most (ended the turn at once in 7) |
| 10 v Altaria 2\|0 t3 | Supernatural Feather (discarding the 2nd Oricorio) | F skipped; **report only, not gating** |

**Measure F first** (each becomes a positive only if F fails it, else a keep check): 05 v Suicune 0|1 t12 (Sharp Fang);
06 v Hydreigon 1|0 t5 (Tongue Whip on the Benched Deino, which tests the board copy's every-target read); 09 v Sceptile 4|0 t11
(Electrispark); B-210952 t14 (an attack that knocks out the 50-HP Wailmer: Surf after benching Carvanha, or Binding Snow after the
retreat; the Auto decisions, so the expected move comes from card text). Baseline: all to measure.

## B. Keep checks (the baseline should already pass)

- **213625 t07:** Sunny Wind knocks out Pinsir. Baseline: F in 11-12 of 12.
- **The 13 same-position turns** where F attacked and C didn't; property "an attack this turn", any attack counts. Baseline: to
  measure; expected near 12 for F. A turn both readers judged MISTAKE becomes a positive if F fails it.
  - Judged MISTAKE: 03 v Blaziken 3|1 t8; 06 v Blaziken 0|0 t3; 06 v Hydreigon 1|1 t2; 06 v Lucario 4|0 t4; 09 v Altaria 1|0 t4;
    10 v Vespiquen 1|1 t4 and 4|0 t6; draft A v Blaziken 0|0 t6.
  - Split verdict, either move acceptable: 06 v Altaria 4|0 t5 and 4|1 t2.
  - Watch points: Castform's Rocky Helmet at 03 v Blaziken t8 (Soothing Shore heals the 20, so the watch must not block that
    attack); the two Vespiquen turns use Supernatural Feather, priced only by the watch.
  - 06 v Lucario 4|0 t4 needs an attack that becomes legal only after an attach, which `_atk` does not cover: a miss there is
    expected, not a failure of the rule.

## C. `_atk` negatives (passing is right), the exception expected to hold each

Baseline for every row: to measure (what km3, F and ky3 with no switch do at each seed). The exception is the one-turn watch
(opponent points through the checkup after their next turn; the skip stands if attacking gives up at least 0.25 more, over 2 SE).
It is swept at 0.15, 0.25 and 0.5.

| case | right move | looks? | exception expected to hold it | `_zs3` |
|---|---|---|---|---|
| 03 v Vespiquen 4\|0 t8 | retreat, no attack | yes | Watch: Chase Order with the optional Ogerpon discard does 140 and knocks out Wailord ex (2 points). Holds only if the simulated km3 takes the discard. | keeps the attack: fails |
| draft A v Blaziken 0\|0 t2 | no Gnaw | yes | Watch: Rocky Helmet's 20 back plus Sunny Scorching and Burn put the Vulpix in knockout range next turn. Helmet damage carried onto the future Ninetales ex is outside the window. | keeps the attack: fails |
| 10 v Suicune 4\|1 t3 | evolve Natu, no Peck | yes, if F evolves | Watch: with 2 more benched, Crystal Waltz does 60 = Natu's HP, and an empty Bench loses the game. | not reached |
| 10 v Altaria 1\|0 t7 | either move | yes | "Does something" fails: Life Drain on a 10-HP Darkrai and Feather with an empty hand change nothing. | not reached |
| deck 12 game 3 T4 (hand-built, `skip_export/game3_t4_*`) | keep the 40-HP Ariados in front (Pierce), no retreat into Whimsicott ex | no: his line attacks, so "not exercised" | None needed for `_atk`. A keep check for every switch, and the `_expo` negative later. Miraidon ex goes to F and ky3 through `KX_EXTRA_LISTS`: checked Oct 15, the 14-card list loads and a sampled world fills his hand 2 and deck 2 from it (test `a_14_card_extra_list_loads_and_fills_the_hidden_zones`). **Approximate world** (his real deck held 6 more unseen cards): a keep check only when labelled so, never `_expo`'s negative as it stands. | n/a |
| deck 13-A G5 T4 (video 20261014_230328; built by hand, `skip_export/deck13A_g5_t4_position.json`, **approximate world**: no opponent list, his hand 4 and deck 5 counted; `pg_pos` loads it with no problems) | no attack: keep the 60-HP Ninetales ex back from the Binding Snow knock-out on Entei-B | yes | Watch: the knock-out makes it 2-1, then their benched Entei-A (3 Fire already) knocks out the 60-HP Ninetales ex for the third point. | not measured |
| 012303 t09 | evolve to Gurdurr and attach, no Strength | no: F's line attacks (all three bots) | None needed: "not exercised", a keep check for every switch. A later positive for the watch used the other way (Mega Absol ex's Poison Barb, the check-up and Darkness Claw knock out Gurdurr for the third point). | keeps the attack, which loses on the spot |

**010837 t09 and t11 (correct passes after the cloud's diagnosis):**
- t11: C passes the Pichu knockout on its play-out scores alone (knockout line 33%, passing wins at count 3 with the Blade at 180).
  Expect `_atk` to leave the pass alone: the play-outs carry the plan. Baseline: C passes; F's play-outs score almost every move
  94-100%; to measure for km3, F, ky3.
- t09: `_m64` tips a close call (C passes in 2 of 12 seeds without it, 11 of 12 with it). Baseline for F: expected near the
  without-`_m64` figure, to measure.
- Open doubt: C's 100% for passing assumes the opponent walks Kangaskhan into the count-3 Blade; the real opponent did not. The
  separate paired play-out gate (km3, km4, Blade-aware opponent; R = 128) settles it. It is not part of phase 1.

## D. Reported, with a known limit (Dustin's plan passes)

- **010837 t03:** retreating Pawniard instead of taking the Slash knockout on the 30-HP Pichu keeps the future Kingambit safe.
- **203719 t17:** passing up the exact-100 Blade knockout, letting Glimmora fall to raise Overlord's Blade.
- Both are negatives for `_atk` (correct passes by a sacrifice or a delay), but each is about the deck's plan, not the opponent's
  next turn, so **the one-turn points exception may not hold them.** Expected: `_atk` takes the knockout in both. That is a
  known limit of the one-turn watch, not a pass; it blocks adoption. If it happens, the next iteration tries a longer watch
  (through two opponent turns) or a plan-value term, never a special case for one card. If `_atk` instead passes, the report says
  what the watch saw (unexpected). Baseline: to measure.
- Reported, not judged: 09 v Altaria 0|0 t3, draft A v Lucario 3|0 t2.

## E. `_punch` and `_queue`: unit tests, not positions

- `_punch` (unfixed gives 80, or 60 against a Heavy Helmet holder): an unhelmeted 110-HP Alolan Muk takes 1 attack (unfixed 2);
  a Helmet holder (Retreat Cost 3+) at 61-80 HP is knocked out by 60 + 20; at 81-100 HP it survives; the 40 lands on the promoted
  Pokémon and there is no 40 after a game-ending knockout; clock totals Kingambit + Glimmora + Muk 6 -> 4 and the t09 board
  3 -> 2; the threat pick (value_functions.rs:1762) uses 120; digests unchanged (neither self-check deck has Kangaskhan).
- `_queue`: the plain `ApplyDamage` sibling of `depth_zero_prices_mandatory_queued_attack_damage` gives -200, not -240; Tongue
  Whip with 1 and with 2 Benched targets; Diving Icicles resolved (re-run the self-check, report any digest change); a frame that
  isn't from-attack damage stays unresolved; VK_110 root score Place:Pawniard about 11781, not 1691.
- The 8 recorded 010837 Kangaskhan turns are reported only (a +40 fix moved none; per-punch pricing may move the Heavy Helmet
  at t11).

## F. Identity (gate 2), expected

ky3 with no switch prints F's `31d638dbc818b0fa` and plays F's move at every seed; km3 stays `81b572198c04d5d1`. With `_atk`, games
where it never looked match. `_punch` is bit-equal wherever no Kangaskhan is in play. `_queue` may change the digest through
Diving Icicles (t-suicune); games with no firing must match, and firings are counted.

## G. Not in phase 1 (what each later switch needs)

`_expo` (positives 015659 t05 and 014423 t07 are confounded; it needs one clean positive where the doomed Active can attack;
negatives 05 v Lucario 3|0 t5 and game 3 T4; keep check game 3 T1), `_bench` (no verified F failure; measure F on B-210952 t14,
t16 and deck 12 game 8 T2), `_spread`, and the Kingambit pilot (item 7). Deck 12 later: games 4, 5 T4, 9 T4/T5.

## H. Positions that did not export

Any position the export drops (km3 on the current engine does not make its recorded `km3_move` in most of 12 seeds) is listed by
the tool and is not a case. Deck 13-A G5 T4 is built (see its row in C). Its world is approximate, and every result for it carries that label.
