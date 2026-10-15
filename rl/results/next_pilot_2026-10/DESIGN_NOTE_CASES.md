# ky3 cases (appendix to DESIGN_NOTE.md, Oct 14)

Gate 0 (the baseline: km3, F, and ky3 with no switch, 12 seeds) decides each case's role. A case is a positive only if the
baseline meets its property in at most 8 of 12. Otherwise it is a keep check. "Known baseline" is what the records already
show; everything else is measured first. Combined-run cases are exported from `skip_replay.rs` (game key + decision), and each
is kept only if km3 makes its recorded move there.

## A. `_atk`: expected positives (F's own skips)

| case | what F did | property scored | known baseline | source |
|---|---|---|---|---|
| 01 v Hydreigon 0\|1 t9 | Copycat, then End Turn | Giga Turbo this turn | F skipped (1 recorded game) | hand check MISTAKE ×2; skip_scan 3.0 SE |
| 05 v Lucario 3\|0 t5 | End Turn | Indeedee ex's Psychic knocks out the 30-HP Bonsly | F skipped; `_zs3` lets it stand (3.4 SE) | MISTAKE ×2 |
| 06 v Lucario 4\|1 t3 | Retreat:2 | an attack this turn (Peck) | F skipped | MISTAKE ×2 |
| 09 v Hydreigon 4\|0 t2 | End Turn | Thunder Shock this turn | F skipped | MISTAKE ×2 |
| 09 v Suicune 4\|1 t4 | free retreat into an 80-HP Heliolisk | Lightning Accelerator, with Mega Manectric ex kept in front | F skipped | MISTAKE ×2. This is a skip case, not exposure (km3 proposed the attack). |
| 10 v Altaria 2\|0 t3 (lean) | End Turn | Supernatural Feather (discarding the 2nd Oricorio) | F skipped | MISTAKE + UNCLEAR: reported, not gating |
| 034953 t14 (pg_pos, Oct 12 set) | ended the turn at once in 7 of 12 | Metal Arms knocks out Happiny this turn | F 5 of 12 at most | pause_positions READING |

**Measure F first** (C's positions; each becomes a positive only if F fails it):
- 05 v Suicune 0|1 t12 (Sharp Fang)
- 06 v Hydreigon 1|0 t5 (Tongue Whip on the Benched Deino: tests the board copy's every-target read)
- 09 v Sceptile 4|0 t11 (Electrispark)
- 010837 t09 (C ended the turn in 11 of 12 with no Energy)
- B-210952 t14: an attack this turn that knocks out the 50-HP Wailmer, either Surf after benching Carvanha, or Binding Snow
  after the retreat. These are the game's Auto decisions, so the expected move comes from card text.

## B. Keep checks (the baseline should already pass; no switch may lower them)

- **213625 t07:** Sunny Wind knocks out Pinsir. F made his line in 11-12 of 12.
- **010837 t11:** property "doesn't end the turn with nothing". F took the knockout in 12 of 12. Which move is best is
  contested; this property is not.
- **The 13 same-position turns** where F attacked and C didn't. The property is "an attack this turn"; any attack counts,
  because in 5 of the 13 F's attack came by another route. A turn both readers judged MISTAKE becomes a positive if F fails it.
  - Judged MISTAKE: 03 v Blaziken 3|1 t8; 06 v Blaziken 0|0 t3; 06 v Hydreigon 1|1 t2; 06 v Lucario 4|0 t4; 09 v Altaria
    1|0 t4; 10 v Vespiquen 1|1 t4 and 4|0 t6; draft A v Blaziken 0|0 t6.
  - Split verdict, so either move is acceptable: 06 v Altaria 4|0 t5 and 4|1 t2.
  - Watch points: Castform holds Rocky Helmet at 03 v Blaziken t8, and Soothing Shore heals the 20, so the watch must not
    block that attack. The two Vespiquen turns use Supernatural Feather, whose discard is priced only by the watch.

## C. `_atk`: negatives (passing is right), with the exception expected to hold each

| case | right move | the rule looks? | exception expected to hold it | `_zs3` |
|---|---|---|---|---|
| 03 v Vespiquen 4\|0 t8 (F; DEFENSIBLE ×4) | retreat, no attack | yes | Watch: Chase Order with the optional Ogerpon discard does 140 and knocks out Wailord ex for 2 points. This holds only if the simulated km3 takes the discard. | keeps the attack: fails |
| draft A v Blaziken 0\|0 t2 (F and C; DEFENSIBLE ×4) | no Gnaw | yes | Watch: Rocky Helmet's 20 back plus Sunny Scorching and Burn put the Vulpix in knockout range next turn. The Helmet damage carried onto the future Ninetales ex is outside the window. | keeps the attack: fails |
| 10 v Suicune 4\|1 t3 (C; DEFENSIBLE ×2) | evolve Natu, no Peck | yes, if F evolves | Watch: with 2 more benched, Crystal Waltz does 60, exactly Natu's HP, and the empty Bench means the game is lost. | not reached |
| 10 v Altaria 1\|0 t7 (C; DEFENSIBLE ×2) | either move: nothing does damage | yes | "Does something" fails: Life Drain on a 10-HP Darkrai and Feather with an empty hand change nothing. F's own move there was a Life Drain that did nothing. | not reached |
| deck 12 game 3 T4 (Dustin: "delaying was my only chance") | keep the 40-HP Ariados in front (Pierce), no retreat into Whimsicott ex for the knockout | no: his line attacks, so the rule is "not exercised" | A keep check for every switch, and the `_expo` negative later. Built by hand, with the opponent's Miraidon ex given to F and ky3 through `KX_EXTRA_LISTS`. | n/a |

**Reported, not judged:**
- 010837 t03 and 203719 t17 (contested; Dustin's word first)
- 09 v Altaria 0|0 t3 (UNCLEAR ×2; km3 proposed no attack)
- draft A v Lucario 3|0 t2 (UNCLEAR ×2)

## D. Kangaskhan corrections (DECISION.md, Oct 14: separately testable)

**`_punch` unit tests.** The unfixed forecast gives 80, or 60 against a Heavy Helmet holder.
1. An unhelmeted 110-HP Alolan Muk: 1 attack (unfixed: 2).
2. A Heavy Helmet holder (Retreat Cost 3 or more) at 61-80 HP: knocked out by 60 + 20 (unfixed: survives).
3. A Helmet holder at 81-100 HP: survives (a flat +40 would say 100, a knockout).
4. The carry-over: the 40 lands on the promoted Pokémon, and there is no 40 after a game-ending knockout.
5. FINDINGS' clock totals: Kingambit + Glimmora + Muk 6 → 4, and the t09 board 3 → 2.
6. The threat pick (value_functions.rs:1762) uses 120.
7. The self-check digests are unchanged: neither self-check deck has Kangaskhan.

**`_queue` unit tests.**
1. A sibling of `depth_zero_prices_mandatory_queued_attack_damage` (expectiminimax_player.rs:1261) for the plain
   `ApplyDamage` form: the leaf is −200, not −240.
2. Tongue Whip with 1 and with 2 Benched targets (frames of 1 and 2 choices).
3. Diving Icicles (Chien-Pao ex, in t-suicune) is resolved. Re-run the self-check and report any digest change.
4. A frame that isn't from-attack damage stays unresolved.
5. FINDINGS' VK_110 root score: Place:Pawniard about 11781, not 1691.

**Positions:** the 8 recorded 010837 Kangaskhan turns are reported only. A +40 fix changed none of them; per-punch pricing
may move the Heavy Helmet at t11.

## E. Later switches: what each needs before it is built

**`_expo`** (when the opponent moves next and their ready attacker knocks out my Active in one hit, my clock leaves that
Pokémon out and its Energy earns nothing; the scope adds Dede-Circuit, `DamagePerOwnToolAttached`, to the damage estimator).
- **Positives, scored on the property "the turn's Energy is attached, and not on the doomed Active" (any Benched target):**
  - 015659 t05: F put it on Regigigas in 5 of 6 seeds.
  - 014423 t07: F put it on Regigigas in 6 of 12 and ended the turn in 6. Without the Dede-Circuit case the forecast reads 20,
    so `_expo` can't fire.
  - Both are confounded: Regigigas B3 134 can't attack under Seal of Antiquity with no Alolan Muk in play, so its Energy is
    wasted either way.
- **Still needed: one clean positive** where the doomed Active can attack. To find one, a reader pass over F's 32 skip turns
  whose retreat left an Active with no Energy (an unreviewed count that also holds correct sacrifices).
- **Negatives:**
  - 05 v Lucario 3|0 t5: the attach-then-attack line must survive the depth limit.
  - game 3 T4, the shield.
- **Keep check:** game 3 T1, the sacrifice.
- **Gate 2:** a differential test, with values bit-equal wherever the trigger is false.

**`_bench`** (the clock's attacker is the one fastest to win). There is no verified F failure.
- Measure F first on B-210952 t14 and t16 (Auto's decisions) and on deck 12 game 8 T2.
  - Game 8 T2 was Dustin's own slip. kx3 already arms the Benched Cottonee in 43 games against km3's 3.
- **Negative to add:** attaching to the Active for a knockout now beats arming the Bench.

**Deck 12, later:**
- game 4 (Safeguard: "does something" must read 0)
- game 5 T4 (Mirror Shot: both lines attack, so `_atk` isn't exercised; km3 doesn't price it)
- game 9 T4/T5 (either move acceptable)

**Still to find:**
- holding Energy against Indeedee ex's Psychic
- not benching against a Bench-counting attack (t-suicune's Crystal Waltz)
