# Pokémon TCG Pocket battle rules — reference for checking the simulator and bots

Written 2026-09-21 (Claude, overnight research); updated 2026-09-22 with Dustin's in-game tests and statements, the
complete in-app Tips page, and 13 more reviewed recordings; **second update 2026-09-22: a full engine audit (every card
effect in the pool, the core rules code and the bots — `07`), a list of in-game tests that would settle what's left
(`08`), and a fresh web sweep.** App version 1.7.2, cards through B4a (B4b arrives Sep 29–30). This is a rules
reference, not a process: use it to check that the engine and bots play the real game. `RULES_FOR_AGENTS.md` was
brought in line with it on 2026-09-21, and the opening-hand line was updated on 2026-09-22 (bottom of this file).
**Rules4 update, 2026-09-22:** rules4 is active as `deckgym 0.1.0-pdl.rules4`; engine SHA-256 `e6593ed816d0d5dbaf24fc8bc81a8317ed8069cda6ae7162c3d53e1fa7a12415`. Validation passed: 1,826 engine tests, 44 replay segments with 441 assertions, and 48 replay-tool tests; normal launcher smoke passed. Rules4 repairs the narrow T2 outcome below. See the [rules4 repair record](../Boss%20Folder/rules4-t2-repair-2026-09-22/README.md). The separate add-on 0.7.2 recheck is still running.

**Replay checks:** the rules2 corpus originally had 37 source-backed segments; rules3 passed 44 segments with 441 outcome assertions and 70 scripted actions across 15 accepted packets. Rules4 revalidated 44 segments/441 assertions and passed 48 replay-tool tests. These are constructed segments, not full-match replay certification. See the [rules4 repair record](../Boss%20Folder/rules4-t2-repair-2026-09-22/README.md).

## Where things stand (2026-09-22, evening)

- **Settled:** damage order (official FAQ + Dustin's Skarmory game), end-of-turn and Checkup order (Burn versus Checkup healing and the order of other Checkup Abilities remain open; Poison before Blessed Salt is observed), all five Special
  Conditions, winning by points or an empty board, turn-limit ties and timers (other simultaneous finishes remain open —
  see below), setup and first turn, **how the opening hand is dealt (new: two statistical studies)**, mid-turn Knock
  Outs, double-KO promotion after an attack (attacker first), when a card can be played (Dustin's rule + the 1.7.0
  change, both seen in play), hidden information, Wallace timing, retaliation vs an attack that removes Abilities
  (official JP FAQ).
- **Engine audit (`07`):** the original 560/560 attack-effect, 156/156 Ability, 163/163 Trainer and core-rules audit is
  preserved as a historical snapshot.
- **Engine repairs (`09`):** H1, H2 and M1–M6 plus the bounded earlier findings are in the verified rules2 repair. Rules3 adds R1's attack-reduction target fix and R2/M7 player-selected Energy discards for retreat and untyped discard attacks. Rules4 is active and verified; its narrow T2 repair is recorded in the [rules4 repair record](../Boss%20Folder/rules4-t2-repair-2026-09-22/README.md).
- **Dustin's in-game tests, 2026-09-22:** T1 (50 opening hands) confirms the swap-in opening-hand rule on the current
  app (both Basics in 3/50; Basic-first rejected, p = 0.0035). T10 (video) confirms one Stadium play per turn ("You can't
  use any more Stadium cards this turn"). Evidence: `_research_notes/audit_2026-09-22/T1_T10_results.md`. T6 (Dustin): the player chooses which Energy to discard
  for retreat and untyped "discard X Energy" attacks (confirmed on video); rules3 implements the choice. Checkup order (#4):
  Poison resolves before Blessed Salt (recording 010316); the engine already does this. T9 (Dustin): heals can't
  target a full-HP Pokémon except Pokémon Center Lady on one with a Special Condition. T2 (Dustin): your last Pokémon
  taking his 3rd point while being Knocked Out in the same attack; the result overlay showed **Tie**. The opponent still had Pokémon; its final 2 points are inferred from the ex Knock Out, not read on the overlay. This was one observed video seat; both-seat engine fixtures are regression coverage.
- **Review of rules1 (`10`):** historical review of that release, including findings later corrected in rules3: R1 fixed the Cubone/Clefable/Bonsly attack-reduction target and R2/M7 added player-selected Energy discards.
- **Still open** (`05_open_questions.md`, tests in `08`): Checkup double-KO promotion order (#21); a card returning to a
  full hand (#9); Weakness on an attack debuffed to 0 (#11); Heavy Helmet with a changed Retreat Cost (#19); turn-limit
  timing (#22).

## Files

| File | Contents |
|---|---|
| `01_game_structure.md` | Deck rules, setup, turn order, first turn, Energy Zone, hand limit, winning and ties, turn/time limits, history |
| `02_damage_knockouts_points.md` | **Official damage-calculation order**, Weakness, Bench damage, kinds of damage and prevention, what happens after an attack, Knock Outs, points, promotion, HP changes |
| `03_status_checkup_timing.md` | The five Special Conditions, stacking, cures, the end-of-turn sequence and Pokémon Checkup order |
| `04_actions_cards_effects.md` | Energy attachment, retreat vs switching, evolution (incl. Mega), Abilities, Supporters/Items/Tools/Stadiums/Fossils, effect lifetimes, copy attacks, randomness, hidden info, all official card rulings |
| `05_open_questions.md` | What is still unknown or contested, why it matters, and how to settle each |
| `06_sources.md` | Every source with its grade; what "reading the app's code" turned up |
| `07_engine_audit_2026-09-22.md` | **What the simulator gets wrong** — full audit of core rules, every card effect and the bots, with file:line, run results and a fix order |
| `08_tests_to_record.md` | In-game tests and recordings that would settle each open question, with setups; what makes ordinary recordings useful |
| `10_review_of_rules1_2026-09-22.md` | Historical Claude review of rules1: independent rebuild, black-box checks and findings later implemented in rules3 |
| `09_engine_repairs_2026-09-22.md` | Repair ledger: verified rules1/2/3 repairs and remaining open questions |
| `_research_notes/` | Raw notes from the research agents and captured official pages (for tracing any claim). `audit_2026-09-22/` has the ten audit/research reports (with one-line verdicts for every card text) and the probe tests |

**Grades used everywhere:** [OFFICIAL] the in-app Tips › About Battle Rules text (from Dustin's screenshots), Pokémon/Creatures pages, or printed card text · [IN-GAME TEXT] the game's own
tutorial/UI strings · [OBSERVED] seen in Dustin's recorded games · [COMMUNITY] wikis/guides that agree ·
[SINGLE] one community source · [DUSTIN] stated by Dustin from his own play · [INFERRED] reasoning, not a source · [UNRESOLVED]. Nothing here is from memory.

## The rules most likely to be wrong in a simulator

1. **Damage order [OFFICIAL]: attack's damage → attacker-side effects → Weakness → Defending-Pokémon effects**, never
   below 0. Example from the official FAQ: 50 damage, Bounded Field (Weakness ×2), defender "−20 from attacks" = 80.
   rules1, rules2 and active rules4 follow this order (verified: Claude's rebuild and probes in `10`, and the Skarmory replay). `07` preserves
   the original engine defect and examples.
   **Confirmed in play** (Dustin's Skarmory game): 60 Fire into Skarmory ex with Metal Core Barrier under Bounded Field did **70** (official 60×2−50); the former engine behavior gave 20.
2. **End of turn [OFFICIAL + OBSERVED]:** attack fully resolves → "end of turn" effects, **turn player's first** →
   Pokémon Checkup (both Actives; player whose turn ended first; Poison → Burn → Sleep → Paralysis) → KOs.
3. **Effects of attacks on a Pokémon, and its Special Conditions, end when it goes to the Bench *or evolves*
   [OFFICIAL, in-app Tips]**; player-wide effects ("during this turn your attacks…", "+20 next turn") persist even if
   the Pokémon that made them is Knocked Out [OBSERVED].
4. **After an attack [OBSERVED + OFFICIAL]:** damage → the attack's own effects → Tool retaliation (Rocky Helmet) →
   on-KO Abilities (Destiny Burst) → Knock Outs, points, promotion. After a double KO the **attacker (turn player)
   promotes first** [DUSTIN + OBSERVED 225430]. rules1, rules2, rules3 and rules4 promote the turn player first in either seat; the 225430 double KO replays correctly (Checkup double KOs are still open, `05` #21). Knock Outs from Abilities or from removing an HP bonus are scored at once and the turn goes on — you can still attack [DUSTIN + OBSERVED]. **Rocky Helmet fires even when its holder is Knocked
   Out** (5 recorded cases; Poison Barb likewise poisoned the attacker after its holder was KO'd, 004344). The attack's effects still happen after lethal damage.
5. **Winning [OFFICIAL, in-app Tips]:** you win by reaching the points "before the other player"; a player with no
   Pokémon left in play loses "regardless of the number of points each player has." **Observed T2 exception:** in the
   recorded seat, Dustin had 2 points and his last Pokémon was Knocked Out in the same attack that awarded his 3rd point;
   the result overlay was a tie. The opponent still had Pokémon; its final 2 points are inferred from the ex Knock Out,
   not shown on the overlay. Rules4 implements this narrow case: when exactly one player has at least 3 points, that
   player has no Pokémon, and the opponent still has Pokémon and fewer than 3 points, the result is a tie. Both-seat
   engine fixtures pass; the video itself shows only one seat. Broader count-win claims remain community/inferred and
   unverified; rules4 does not establish both-empty or both-at-least-3 cases. See the [rules4 repair record](../Boss%20Folder/rules4-t2-repair-2026-09-22/README.md) and `05` #2.
6. **First turn [OBSERVED + COMMUNITY + OFFICIAL]:** the player going first **does draw**, gets **no Energy**, **can**
   play a Supporter, **can** attack if the cost is payable (0-cost attacks), **can't** evolve. The second player can't
   evolve on their first turn either. (Game8's "first player doesn't draw" is wrong.)
7. **Mega Evolving does not end the turn** [OBSERVED ×3]. Mega ex evolve from the *pre-evolution* of the named Pokémon
   (Mega Lucario ex ← Riolu, Mega Blaziken ex ← Combusken) or are Basics; 3 points when Knocked Out.
8. **Bench damage:** no Weakness ever [OFFICIAL, in-app Tips: "Don't apply Weakness for Benched Pokémon"]; attacker boosts reach the Bench only if their text says "your opponent's
   Pokémon" (Clemont's Backpack) rather than "…Active Pokémon" (Giovanni, Training Area, Fighting Coach) [OBSERVED ×4].
9. **Non-attack damage (Poison/Burn, Abilities, Tools, retaliation) is not "damage from an attack"** — no Weakness, no
   Giovanni, not reduced by "−X from attacks", not blocked by Disguise/Safeguard [OFFICIAL + OBSERVED].
10. **Energy:** unattached Energy is discarded at end of turn; card effects that attach from the Zone don't use the
    once-per-turn attachment [COMMUNITY + OBSERVED]. Both players see both "next" Energies.
11. **Hand limit 10:** draws past 10 are skipped (card stays in deck); an empty deck is never a loss [IN-GAME TEXT].
12. **Special Conditions [OFFICIAL, in-app Tips]:** only the Active can have them; Asleep/Paralyzed/Confused replace each other; Poison and Burn stack with anything; Confused
    Tails = attack doesn't happen, no self-damage; Sleep flips at the very next Checkup (can wake before its own turn);
    Paralysis lasts through the victim's next turn; moving to the Bench or evolving cures everything; healing doesn't.
13. **Stadiums:** one play per turn, one in play, same name can't be played, different name replaces either player's,
    affects both players [IN-GAME TEXT + OBSERVED].
14. **Turn limit → tie** [OFFICIAL]; 30 turns in versus [COMMUNITY]; the turn counter counts both players' turns [OBSERVED]. **Battle clock out → that player loses** [OFFICIAL] (Bulbapedia/Game8 EN are wrong). Pokémon Checkup "is not considered to be part of either player's turn" [OFFICIAL].
15. **Abilities:** "once during your turn" is per Pokémon (two copies = two uses) [OBSERVED]; same-name passives stack
    [COMMUNITY]; no Special Condition blocks Abilities [INFERRED].
16. **Named-card searches can be played for nothing since v1.7.0** (Clemont, Gladion, Team Galactic Grunt) [SINGLE + seen in play: Gladion, recording 152812];
    still blocked with an empty deck. The `0.1.0-pdl.rules1` repair makes legality depend on visible state and blocks
    confirmed deck-taking effects when the deck is visibly empty. The empty play still
    counts as the turn's Supporter: it uses up the one-Supporter limit and turns on "played a Supporter this turn"
    bonuses (Brave Buddies +50, seen in 152812). Clemont and Grunt rest on the Japanese source only — not seen in play.
17. **When a card can be played (Dustin's rule):** if what's visible (hand, boards, discards, deck empty or not) shows the card can't
    work, it's blocked; if it depends on what's left in the deck, it's allowed. The `0.1.0-pdl.rules1` repair applies
    this to the confirmed Trainer, Stadium and Ability cases and uses Wallace's maximum HP after bonuses. Details:
    `04` §6 and `09`. Draw cards are blocked on an empty deck, except Copycat (shuffles the hand in first) [DUSTIN].

18. **Opening hand [COMMUNITY-TESTED + OBSERVED T1]:** 5 random cards; only if none is a Basic is one swapped for a Basic. Extra
    Basics are not favoured (2-Basic deck: both in hand ~5–6%, not ~21%). rules1, rules2 and rules3 implement
    this method (verified in `10`: 5.31% over 40,000 deals).

## Card-effect pass, 2026-09-21 (engine `deckgym-fork-s193` working tree; 65 cards from the 8 Limitless study decks + Dustin's Blaziken list)

Sonnet reviewers checked each card on both halves (does the code match the text; does the effect then behave per this folder); every problem below was re-checked against the code by Claude. From reading code, not from running games. 57 of the 65 cards had no card-specific problem; two of the findings below are general rules bugs that several cards run into. This section preserves that audit snapshot; `09` records the implemented repair status.

- **High — Eevee (B1 184) Boosted Evolution applies to the whole board.** Text: "As long as this Pokémon is in the Active Spot, *it* can evolve during your first turn or the turn you play it." `move_generation/mod.rs` ~194–205 skips the first-turn block for every hand card when Eevee is Active, so any Pokémon placed at setup can evolve on turn 1 — e.g. a Benched Swablu → Mega Altaria ex on turn 1 in the Altaria deck.
- **High — Quick-Grow Extract (B1a 067) and Wallace (B3b 068/085) pick the target Pokémon at random.** Text: "*Choose* 1 of your [G]/[W] Pokémon … Put a *random* … Pokémon from your deck that evolves from that Pokémon onto it." `apply_trainer_action.rs` ~2415 and ~2445 build one random outcome per (your Pokémon, deck evolution) pair, so the player can't choose which Pokémon evolves. Core to the Sceptile deck; Wallace is in Dustin's Magikarp deck. **Confirmed in play:** on Wallace the game asks "Please choose a Pokémon to evolve" and highlights every eligible Pokémon (recording 150630, 00:14.5).
- **Medium — Asleep, Paralyzed and Confused don't replace each other.** In-app Tips: only one at a time, the newest wins. `state/mod.rs` `apply_status_condition` → `played_card.rs` `set_status_raw` just sets another flag, so a Pokémon can be Asleep and Paralyzed (or Confused) at once. Hits every Sleep/Paralysis/Confusion deck (Altaria, Team Rocket's Weezing's Confusion Gas, …).
- **Medium — Lum Berry always resolves before Darkrai's Bad Dreams.** Official FAQ (`03` §end-of-turn): when Darkrai's owner's turn ends, Bad Dreams does 20 first, then Lum Berry cures. `hooks/core.rs` `on_end_turn` runs berries (~412) before Bad Dreams (~569) on every turn.
- **Low/medium — Caterpie (B3b 001) Quick Growth resolves after the Pokémon Checkup.** Text: "At the end of your opponent's turn…" — end-of-turn effects come before the Checkup, and evolving would cure its conditions first. `apply_action_helpers.rs` `forecast_pokemon_checkup` runs it as a start-of-turn step after the Checkup.
- **Low — Protective Poncho (B2 147) also blocks your own attacks' damage to your own Benched Pokémon.** Text: "…prevent all damage done to that Pokémon by *your opponent's* attacks and Abilities." `hooks/core.rs` ~1569 doesn't check whose attack it is.
- **Low — Fragrant Forest (B3 153) can't be used when no Basic [G] Pokémon is left in the deck** (`stadiums.rs` ~168). Same class as item 17; Dustin gave this exact case as allowed.
- **Low — Pokémon Checkup handles both players' conditions in seat order** (`apply_action_helpers.rs` `collect_checkup_targets`), not "the player whose turn just ended first" (in-app Tips). Rarely changes a result. Bad Dreams from both players' Darkrai also resolves in seat order.
- **Low, probable — Darkrai ex (A2 110) Nightmare Aura fires only on the once-per-turn manual attachment** (`only_turn_energy: true`, `state/energy.rs` ~150). Text: "Whenever you attach a [D] Energy from your Energy Zone…"; the official Jolteon ex ruling for the same wording counts attachments by card effects too. Worth a quick in-game check.
- **Unsure, low — Teal Mask Ogerpon ex (B2 017) Energized Leaves counts attached Energy cards**, while Scrafty and Enamorus count Serperior's Jungle Totem doubling. Which is right needs a ruling; only matters with Serperior in play.

The original pass spot-checked the engine for items 1 and 5 and confirmed the upstream deckgym model for several
others. Current repair and verification status is tracked in `09`.

## Changes to `RULES_FOR_AGENTS.md` — applied 2026-09-21 with Dustin's OK

Everything below is now in that file, plus later findings (mid-turn Knock Outs, double-KO promotion, when a card can
be played, hidden information). Kept here as the record of what changed.

- **Wrong:** "Mega Evolution ex cards evolve from the named Pokémon (Mega Lucario ex from Lucario)". Mega Lucario ex
  evolves from **Riolu** (Stage 1); Mega Blaziken ex from Combusken. The Mega replaces the named Pokémon in the line.
- **Add:** official damage order (item 1); end-of-turn order (item 2); effects and conditions cleared on going to the Bench *or evolving* (item 3); win/lose wording from Tips (item 5);
  first player draws on turn 1; Mega Evolving doesn't end the turn; tie counting; 30-turn cap; Bench damage rules;
  one Stadium *play* per turn (in addition to one in play).
- **Upgrade the [verify] tags:** the in-app Tips now state every Special Condition word for word — Poison 10, Burn 20 +
  flip, Sleep flip, Paralysis recovers at the Checkup after its owner's next turn, Confused Tails = no attack. "Unattached
  Energy is discarded" now has Bulbapedia as a second source. "Damage from Abilities and Special Conditions is not damage
  from an attack" is now official (Mimikyu ex FAQ). Add: running out of battle time loses; turn limit = tie.
- **Nuance:** the file says a zero-cost attack is allowed on the first turn — the official wording is "can be used on the
  first turn of the player that goes first"; any attack whose cost is paid by a card effect (e.g. Energy from a
  Supporter) is also allowed.

## What "read the app's code" turned up (short version)

No public code or protocol dump exists; the battle logic probably runs on the server anyway. The public extraction of
the game's own text strings (tutorial, battle messages) was the closest thing and it answered a dozen questions word for
word. I did not download or decompile the app. The official "Detailed Battle FAQ" that the app itself links to turned
out to be online and was the best source of the night. Details in `06_sources.md`.

## Change to `RULES_FOR_AGENTS.md` — applied 2026-09-22 with Dustin's OK

- "Setup: 5-card opening hand guaranteed to contain a Basic" → add: "dealt as 5 random cards; if none is a Basic, one
  of them is swapped for a Basic, so extra Basics are **not** favoured (two statistical studies; the engine currently
  deals a Basic first, `rules/07` H1)."

Implementation status, 2026-09-22: the historical Basic-first limitation quoted above was repaired in rules1. Rules2 added the replay-discovered simultaneous-KO repair; active rules4 retains both fixes.
