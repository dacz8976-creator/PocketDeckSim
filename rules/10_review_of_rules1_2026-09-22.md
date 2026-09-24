# 10 — Review of Astra's rules repairs (`0.1.0-pdl.rules1`), 2026-09-22

Historical snapshot of the rules1 review. The R1 attack-reduction target bug and R2/M7 Energy-choice gaps described
below were later repaired in active rules3. See the [rules3 repair record](../Boss%20Folder/rules3-repairs-2026-09-22/README.md).

Reviewer: Claude, at Dustin's request. Scope: the repairs listed in `09_engine_repairs_2026-09-22.md`, checked against
this folder and against Dustin's in-game tests. I did not change any engine code.

## Verdict

**Historical rules1 review:** the repairs listed for that release behaved correctly in the independent checks below.
The review also found R1 and recorded R2 before their later rules3 implementation.

## How I checked

1. **Rebuilt from Astra's archive** (`Boss Folder/rules-repair-2026-09-22/source-after.tar.gz`) in the cloud, not from
   Astra's binary. `cargo test`: **1,811 passed, 0 failed**, the same count as Astra's log.
2. **Read every source change**: `git diff` equivalent against the unified1 working tree, about 1,800 changed lines in
   26 files. Test-only files were skimmed.
3. **Ran my own probe tests.** These are black-box checks written from the rules, not from Astra's code; files in
   `_research_notes/audit_2026-09-22/probes/`:

| Check | Real game | rules1 result |
|---|---|---|
| Opening hand, 2-Basic deck, 40,000 deals | both Basics ~5.3% (Dustin's T1: 3/50) | **5.31%**, never a hand without a Basic |
| 60 Fire into Skarmory ex + Metal Core Barrier, Bounded Field | 70 (seen in Dustin's game) | **70** (30 without Bounded Field, also right) |
| Heavy Helmet holder, one Poison tick | 10 damage | **10** (unified1: 0) |
| Clemont's Backpack + Electrispark, Bench hit | 30 | **30** (unified1: 10) |
| Poisoned Pokémon on 10 HP, Garganacl in play | survives on 10, no point | **survives, 0–0** (unified1: KO'd, point given) |
| Glimmora KO'd by Poison, 60 runs | coin flips, ~half denied | **30 scored, 30 denied** (unified1: 40/40 scored) |
| Budew's Prickly Powder into Druddigon | no Rough Skin damage (official JP FAQ) | **no damage** (unified1: 20) |
| Same, with Alolan Muk in play | no Rough Skin (Druddigon is Basic) | **no damage** (unified1: 20) |
| Iron Jugulis hit by an attack | attacker takes 20 | **20** (unified1: 0) |
| Mesagoza then Arcade in one turn | second Stadium refused (Dustin's T10) | **Arcade not offered** |
| Mythical Slab, Psychic Stage 1 on top / Colorless Basic on top | Kirlia to hand / Eevee to bottom | **both right** (unified1: reversed) |

From reading the code, also right: status replacement (Asleep/Paralyzed/Confused), Eevee's exception limited to that
Eevee, Quick-Grow Extract and Wallace let the player choose the target (Wallace reads maximum HP), Checkup order
(player whose turn ended first, Poison → Burn → Sleep → Paralysis, then Checkup Abilities, then one Knock Out wave),
Lum Berry vs Bad Dreams by turn owner, Caterpie before the Checkup, Protective Poncho, Pichu, Politoed/Weavile's "from
X", the visible-information playability rule (Gladion, Grunt, Cabbie, Pokémon Communication, Mesagoza, Kid's Room,
Fragrant Forest, search Abilities), empty-deck blocks, heal targets, and Piers's random Energy. The attack-reaction
sequencing (attack effects → retaliation → point-denial coins → Knock Outs, holding the right Pokémon through switches)
is intricate. It reads correctly, and the tests cover the cases I'd worry about.

## Findings

**R1 [Medium, pre-existing; my audit missed it; fixed in rules3]** — "During your opponent's next turn, attacks used by the Defending
Pokémon do −20/−30 damage" is modelled as *the attacker's own Pokémon taking* −20/−30. Cards: Cubone's Growl
(A1 151 and reprints), Clefable's Moonblast (A2a 030), **Bonsly (B3 078, in the Mega Lucario tournament list)**. The map
entry is `DamageAndCardEffect { opponent: false, effect: ReducedDamage }` (`effect_mechanic_map.rs` ~499 and ~508). The
card puts the effect on the **Defending Pokémon**. Where that goes wrong:
- The opponent retreats the debuffed Pokémon and attacks with a different one. Real: no debuff. Engine: Bonsly is
  still protected.
- The opponent **evolves** the debuffed Pokémon. Real: the −30 is cleared. **Seen twice in Dustin's games** (224540 T4:
  Rattata→Raticate, then Bite did its full 40 and KO'd Bonsly; 235356 T3: Exeggcute→Exeggutor ex, then an 80 KO). In
  224540 the old engine would still take 30 off Bite (40−30 = 10 damage to a 30-HP Bonsly, leaving 20 HP), so Bonsly
  survives and the opponent's first point never happens [INFERRED from the code, not run].
- The debuffed Pokémon attacks something other than Bonsly (after a Sabrina/switch, or Bench damage). Real: −X
  applies. Engine: no reduction.
- Official damage order puts effects on the Attacking Pokémon **before** Weakness. Now that rules1 applies
  defender-side reductions after Weakness, this debuff lands in the wrong step. It only shows with Bounded Field or
  when the attack is small.

Rules3 implementation: put a `CardEffect` on the opponent's Active (cleared when it goes to the Bench or evolves, like
other effects of attacks) and subtract it at step 2 of the damage order. Rules3 is validated and active.

**R2 [Medium; rule settled 2026-09-22 by Dustin; implemented in rules3]** — the player chooses which
Energy to discard for retreat and Gouging Fire / Walking Wake ("discard X Energy" without "random"). The rules1
behavior described above this finding is historical; rules3 now offers a player choice between distinct Energy
combinations.

**R3 [Low]** — End-of-turn order across owners isn't strict. The turn player's Bad Dreams and Berries now go first and
the other player's go last (the official Darkrai/Lum Berry case is right). But the other player's delayed effects that
fire at the end of this turn (e.g. Mismagius's Cursed Prose, 90 damage) still resolve *before* the turn player's
Deceptive Needle and Soothing Shore. It only matters when both kinds are in play at once.

**R4 [Low, fragile code]** — Clemont's Backpack's Bench reach is recognised by its numbers (+20 for Magneton/Heliolisk)
inside a shared boost type (`hooks/core.rs` ~1064). It works today. A future card that uses the same boost type with
the same numbers would inherit Bench reach, and the check doesn't confirm the Bench target is the opponent's. A small
"reaches Bench" flag on the effect would be sturdier.

**R5 [Note]** — Quick-Grow Extract and Wallace offer any Grass (Water ≤50 HP) Pokémon as a target, including ones with
no evolution at all (a Stage 2). In 150630 both highlighted Pokémon had evolutions, so we don't know whether the game
would also offer one with none. Low value; it would only waste a card.

**R6 [Note]** — As Astra says, the Run 4 RL environment still pins the old unified1 wheel. A new training run needs a
rebuilt environment on rules1, and old results shouldn't be mixed with rules1 results.

## A new official source Astra found

Astra cites a Japanese Pokémon Support article (Grapploct's Knock Back, `app-ptcgp.pokemon-support.com/hc/ja/articles/41083304332057`)
from the **Gameplay** section of the support site, not the Detailed Battle FAQ we swept. It says a Pokémon knocked to
the Bench by the attack is Knocked Out **on the Bench** (so it isn't "your Active Pokémon" when it's KO'd). That's
official support for "attack effects resolve before Knock Outs", and it hints the Japanese Gameplay section may hold
more rulings. It hasn't been swept yet.
