# Card check: the gauntlet's new cards (Sept 26, 2026)

**Pre-repair: checked against the official engine's source (7fc6ccb). Check again at the repaired engine.**

## In plain words

- **17 cards in the new lists had never been checked.** 16 of them do nothing in the engine that their text doesn't
  allow, in any game the gauntlet will play.
- **One card is wrong in a way that changes games: Mega Scizor ex.** Its attack, Bullet Slugger, does 50 more damage
  "if this Pokémon moved from your Bench to the Active Spot this turn".
  - The engine also gives the 50 when Mega Scizor ex comes in to replace a Pokémon Knocked Out at the end of the
    opponent's turn (by Burn, Poison, Deceptive Needle or Bad Dreams). Pocket's ruling gives no bonus there.
  - The cause is the known promotion-timing bug. The engine asks for the new Active only after the next turn has
    begun, so the replacement counts as "moved this turn".
  - Five of the eight panel decks can cause it.
  - All three skeptics upheld it. Two of them add that the gain is smaller than it sounds: in Pocket a player can
    often still earn the 50 by switching Mega Scizor ex in with Revavroom's ability. It still changes games.
  - **So the Scizor list is not run** (the task's rule), and it was only a coverage row anyway.
- **The Rayquaza and Altaria/Greninja lists and all 12 variation lists run.** Their cards all check out.
- **Answered from footage, Sept 26 (laptop session plus an independent re-check):** Rainbow Cave's discarded Energy goes to the discard pile in Pocket, as it does in the engine. So the question below does not flatter Rayquaza.
  - Evidence: Dragon's Blessing's picker counts on turns 16 and 18 of battle 015702 (`rl/results/recordings_check_2026-09-25/video_frame_checks.md` §6).
  - R4 (using Rainbow Cave after the turn's attachment) is not shown there. The review note that suggested it misread the Blessing Metal as that attachment.
- **The open question as first written (now answered above):**
  - In the engine, the Energy that Rainbow Cave throws away goes to the discard pile, and Dragonair's ability can
    then put it on Mega Rayquaza ex the same turn: about one extra Energy per turn, which is +50 on Mega Burst.
  - Nobody has checked where that Energy goes in Pocket. One look in the game settles it: use Rainbow Cave, then
    check your discard pile.
  - The same question touches Flame Patch in the Charizard Y lists and in Blaziken.
- **Nothing here is a rules change.** The engine deviations found go to the cloud's repair list via Dustin (the last
  section).

## Scope

The cards in `decks/gauntlet_2026-09-26/*.txt` and `decks/screen/panel_ladder_2026-09-26/l-charizardy.txt` that are
in none of the following:
- the Altaria check (`rl/results/altaria_card_check_2026-09-26/`);
- the Raticate and Manectric check (`rl/results/raticate_manectric_card_check_2026-09-26/`);
- B2e's 12 checked lists (`rl/results/b2e_card_check_2026-09-26/card_check_*.md`);
- the eight table decks.

The comparison is by printing id. No unchecked card shares its text with a checked printing. Riolu A2 091 is a
different printing from the checked Riolu B3 079.

| List | Cards not checked before |
|---|---|
| `g-mega_scizor_revavroom.txt` | Varoom A2b 055, Orthworm B2a 077, Scyther B2b 001, Mega Scizor ex B2b 047, Revavroom B2b 050, Red A2b 071, Metal Core Barrier B2 148 |
| `g-dragonair_mega_rayquaza.txt` | Dratini B2b 051, Gouging Fire B3a 054, Dragonair B4 117, Mega Rayquaza ex B4 120, Ancient Booster Energy Capsule B3a 069, Professor Sada B3a 072 |
| `g-mega_altaria_greninja.txt` | Froakie A1 087, Greninja A1 089, Oricorio B4 078 |
| `v-lucario_2.txt` | Riolu A2 091 |
| The other 11 variation lists and `l-charizardy.txt` | none (every card was checked before) |

## How

- **Method.** The Altaria and Raticate/Manectric checks' method, code reading only:
  - every clause of each card's `lib/card.py` text: identity, HP, Weakness, Retreat, evolution, ex and Mega ex
    points, cost, damage, every effect clause, who chooses, targets, timing, first-turn rules and once-per-turn
    limits;
  - each clause traced through its code path (database entry, effect mapping, apply code, damage hooks, move
    generation), with file:line, existing tests, the rules docs and Dustin's recordings where they apply.
- **Source.** `engine/src` equals 7fc6ccb (`git diff 7fc6ccb HEAD -- engine/src` is empty) and the scan's own tree,
  byte for byte.
- **Checkers.** Three, one per list (Riolu with the Greninja list).
- **Skeptics.** Three independent skeptics then tried to refute every finding that wasn't clean (13 findings, plus a
  late one). Each also spot-checked the "matches" verdicts most likely to change play: Mega Burst's damage count,
  Dragon's Blessing's gating, Gouging Fire's discard and −30, Metal Transport, and Water Shuriken's targets and
  Weakness. 43 skeptic entries in all.
- **Full output:** `card_check.json` (17 card rows with every clause, and the 43 skeptic entries).
- **Coverage.** `goldfish --coverage` at 0 games on every list (`coverage/`): all cards "Fully implemented" (README).

## Per card

| Card | Verdict | Notes |
|---|---|---|
| Varoom A2b 055 | matches | Headbutt 10. |
| Orthworm B2a 077 | matches | Iron Supply puts a [M] from the Zone on a Benched Pokémon of the player's choice. It does not use the turn's attachment. With an empty Bench it still does 10. |
| Scyther B2b 001 | matches | U-turn's switch is part of the attack. With an empty Bench it does 10 and doesn't switch. Rocky Helmet then hits Scyther on the Bench, which is the right order. |
| **Mega Scizor ex B2b 047** | **deviates, changes play** | S1 below. Also settled: a Scyther that moved and then Mega Evolved gets no bonus, as the ruling says. Own retreat, Metal Transport and switch cards count; the opponent's switches don't. |
| Revavroom B2b 050 | matches | Metal Transport needs a [M] Active and works once per turn per Revavroom, from the Active or the Bench. It clears Special Conditions and is not a retreat. It correctly sets Bullet Slugger's flag. |
| Red A2b 071 | matches (open) | +20 only by attacks, only on the opponent's Active ex (Mega ex included), this turn only, before Weakness. Open: it is always playable (S3). |
| Metal Core Barrier B2 148 | deviates, no play change here | −50 only on a [M] holder, attack damage only, after Weakness; discarded at the end of the opponent's turn. It doesn't check the attacker's side (S2); nothing in these games can reach that. |
| Dratini B2b 051 | matches | One coin, +20 on heads. |
| Gouging Fire B3a 054 | matches | The player picks the 2 Energy to discard. The −30 counts only against attacks during the opponent's next turn and ends on going to the Bench. |
| Dragonair B4 117 | matches (open) | Dragon's Blessing works only from the Bench, needs a [N] Active and Energy in the discard, once per turn per Dragonair; the player picks the type. Open: R1. |
| Mega Rayquaza ex B4 120 | matches | Mega Burst discards all [R] and [L] (nothing else) and does 50 per Energy discarded; the printed 50 is not added. Worth 3 points. |
| Ancient Booster Energy Capsule B3a 069 | matches (open) | +40 HP only on the engine's Ancient list, which includes Gouging Fire. If Field Blower removes it (six of the eight panel decks run Field Blower), HP drops by 40 and the damage stays. Open: R3. |
| Professor Sada B3a 072 | matches (open) | Playable only with an Ancient in play and Energy in the discard. Attaches one Energy of each type present (at most 2 here), assigned by the player. Open: R2. |
| Froakie A1 087 | matches | Flop 10. |
| Greninja A1 089 | deviates, no play change here | Rare Candy from Froakie with no Frogadier in the list is allowed, with its restrictions enforced; that is right (G6). Water Shuriken is Ability damage: no Weakness or boosts, any target, once per turn per Greninja, works from the Bench; Knock Outs count at once. Mist Slash can't be paid with Psychic. G1 to G3 are unreachable here. |
| Oricorio B4 078 | deviates, no play change here | The attacker picks the card to discard; the discard comes after the damage. With an empty hand the attack does 0 (G4 corner; G5 open). |
| Riolu A2 091 | matches | Evolution is by name, so Lucario A2 092 and Mega Lucario ex B3 081 evolve from it. Jab 20. |

## The findings and the skeptics' verdicts

| # | Finding | Skeptic 1 | Skeptic 2 | Skeptic 3 | Changes gauntlet play? |
|---|---|---|---|---|---|
| **S1** | Bullet Slugger's +50 after a promotion that follows an end-of-turn or Checkup Knock Out on the opponent's turn | upheld | upheld | upheld | **yes (3 of 3)** |
| S2 | Metal Core Barrier doesn't check the attacker's side | upheld | upheld | upheld | no |
| S3 | Own-turn promotion would also get +50 (unreachable); Red always playable | upheld | partly | partly | no, or marginal: an idle Red shrinks the hand, which feeds Hiking Trail and cuts the opponent's Copycat |
| G1 | Water Shuriken passes the "by attacks" protections that on-file deviation 2 names | upheld | upheld | upheld | no: no gauntlet Pokémon creates them (all 38 panel Pokémon read) |
| G2 | **New:** Guts' survival coin also flips on Ability damage | upheld | upheld | upheld | no: only Conkeldurr A3 096 and Ursaluna B3b 058 have Guts, in no list |
| G3 | Rare Candy ignores Aerodactyl ex's Primeval Law (on file) | upheld | upheld | upheld | no |
| G4 | Oricorio with an empty hand spends Mimikyu ex's Disguise (on-file deviation 1) | upheld | upheld | upheld | no |
| G5 | Supernatural Feather is offered with an empty hand | upheld | upheld | upheld | no: it equals ending the turn |
| G6 | Rare Candy to Greninja with no Frogadier | upheld (the engine is right) | upheld | upheld | no |
| **R1** | Rainbow Cave's discarded Energy goes to the discard pile (open in Pocket) | upheld | upheld | upheld | **unknown** |
| R2 | Sada attaches only the types present (open: Pocket might require 3) | upheld | upheld | upheld | unknown |
| R3 | The Ancient list omits non-ex Flutter Mane B3b 035 and Koraidon B2a 063 | upheld | upheld | upheld | no (in no list) |
| R4 | The engine offers Rainbow Cave only before the turn's attachment; one review note says Pocket allowed it after | partly | upheld | upheld | unknown |
| Spot-check | Mega Burst, Dragon's Blessing, Gouging Fire, Metal Transport, Water Shuriken | no error | no error | no error | |

**S1 in detail** (the evidence all three skeptics traced):
- **The flag.** `moved_to_active_this_turn` (`state/played_card.rs` 39) is set only in `apply_activate`
  (`actions/apply_action_helpers.rs` 963-965), which Promote reaches (`actions/apply_action.rs` 827-830). It is
  cleared only by `end_turn_maintenance` (`played_card.rs` 473), run by `advance_turn` (`state/mod.rs` 1205).
- **The order.** After an end-of-turn or Checkup Knock Out, one step runs the end-of-turn effects, the Checkup, the
  Knock Outs and `advance_turn` (`apply_action_helpers.rs` 109-116, 146-167, 326, 337-339). The Promote choice goes to
  the bottom of the stack (`state/mod.rs` 1391-1423), under the next turn's draw (1206). The stack resolves from the
  top (`move_generation/mod.rs` 45), so the promotion happens inside the Scizor player's own turn.
- **The result.** The flag survives to Bullet Slugger (`actions/apply_attack_action.rs` 4909-4924), so the attack
  does 150 instead of 100.
- **What is right.** A Knock Out from the opponent's attack is promoted on the opponent's turn, and the flag is
  cleared, so no bonus.
- **The rule.** The official ruling for Scizor's Gale Thrust (the same condition word for word) gives the bonus only
  for a move during your turn (`rules/_research_notes/detailed_battle_faq.md` 76-77). Dustin's footage shows Pocket
  asks for the new Active before the next turn starts (Altaria check, deviation 3). This exact Scizor case is not on
  video.
- **Who can cause it.** Blaziken, Weezing, Hydreigon, Altaria and Sceptile, by Burn, Poison, Deceptive Needle,
  Bad Dreams and the like.
- **A correction to the rules docs.** `rules/05` #20 and `rules/07` line 185 say the engine gets opponent-turn
  promotion right. They only considered Knock Outs from attacks, so that statement is wrong for this case.

**R1 in detail.**
- The engine sends Rainbow Cave's discarded Energy to the discard pile (`actions/apply_stadium_action.rs` 84-87,
  pinned by a test). It treats Energy left unattached at the end of a turn differently: that Energy just vanishes.
- No rules file, research note or recording note says where Rainbow Cave's Energy goes in Pocket
  (`rules/01_game_structure.md` 76 lists the Cave; `rules/_research_notes/C_rulings.md` 40 marks the question
  unresolved).
- Indirect evidence supports the engine: a real placing mono-Fire Entei list runs 2 Rainbow Cave with 2 Flame
  Patch, which makes sense only if the Energy lands in the pile.
- **Where it reaches:**
  - the Rayquaza list (with a Benched Dragonair, about one extra Energy per turn from the start, so possibly a
    Mega Burst a turn earlier);
  - Flame Patch in the Charizard Y lists (`h-`, `l-` and both swaps; swap 1 adds a 2nd Rainbow Cave);
  - Blaziken's 2 Flame Patch, which can use any Rainbow Cave in play.
- How often the pilots use the Cave is not measured.

## Engine deviations for the cloud's repair list (via Dustin)

1. **S1, new: Bullet Slugger after an opponent-turn end-of-turn or Checkup Knock Out.**
   - It is a consequence of the promotion-timing deviation (Altaria check, deviation 3).
   - The repair of that deviation fixes this only if the promotion happens before the turn reset (`state/mod.rs`
     1205), or if a promotion stops setting `moved_to_active_this_turn`. The repair's identity replay should look
     for it.
2. **G2, new: Guts flips on Ability damage** (`actions/apply_action_helpers.rs` 462-491; `apply_action.rs` 704-774).
   The text says "damage from an attack". Unreachable in any gauntlet list.
3. **S2, new: Metal Core Barrier has no attacker-side check** (`hooks/core.rs` 715-735, unlike 693 and 743).
   Unreachable in any gauntlet list.
4. **Confirmations of deviations already on file** (both unreachable here):
   - Water Shuriken is also stopped by the "by attacks" protections of deviation 2 (`hooks/core.rs` 1717-1734,
     1887-1894).
   - Oricorio's "does nothing" is a 0-damage hit that spends Disguise (deviation 1).

## Open questions for Dustin (one in-game look each)

- **R1: answered from footage on Sept 26. It goes to the discard pile, as in the engine** (`video_frame_checks.md` §6). The original question: use Rainbow Cave, then check the discard pile's Energy count. This
  affects how far Rayquaza's (and Charizard Y's) results can be trusted.
- **R4: whether Rainbow Cave can be used after the turn's Energy is attached.** One review note says yes (battle
  015702, turn 16, around 225-228 s). A frame check would settle it.
- **R2: whether Professor Sada can be played with fewer than 3 Energy types in the discard pile.**
