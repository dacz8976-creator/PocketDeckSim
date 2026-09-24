# 03 — Special Conditions, end of turn, and Pokémon Checkup

Grades as in `01_game_structure.md`. Sources in `06_sources.md`.

---

## 1. The five Special Conditions

| Condition | Effect | How it ends | Grade |
|---|---|---|---|
| **Poisoned** | **10 damage at every Pokémon Checkup** (after both players' turns). | Moving to the Bench, evolving, cure effects. No coin flip. | [OFFICIAL] in-app Tips + [IN-GAME TEXT] + [OBSERVED] 10 per Checkup repeatedly (181914) |
| **Burned** | **20 damage at every Checkup, then a coin flip: Heads cures.** The 20 is dealt before the flip, so Heads can't save a Pokémon that the 20 knocks out. | Heads at Checkup, Bench, evolving, cure effects. | [OFFICIAL] in-app Tips + [OBSERVED] many cycles in 225430/230007; "Checkup deals 20 before the coin" (234514) |
| **Asleep** | **Can't attack or retreat.** Coin flip at every Checkup: Heads wakes it. | Heads at Checkup, Bench (by an effect), evolving, cure effects. | [OFFICIAL] in-app Tips + [IN-GAME TEXT] + [OBSERVED] flips with both results |
| **Paralyzed** | **Can't attack or retreat.** No coin flip. | "After its owner's next turn, it recovers during Pokémon Checkup" — i.e. it always costs the victim exactly one turn. Also Bench, evolving, cure effects. | [OFFICIAL] in-app Tips, word for word. (No Paralysis appears in the recordings.) |
| **Confused** | When it attacks, flip a coin ("Coin flip — Confused"). **Tails: the attack doesn't happen ("The attack did nothing") and the turn ends. No self-damage** (unlike the paper TCG's 30). | Bench (incl. retreat), evolving, cure effects. **Not** cured by any Checkup flip. | [OFFICIAL] in-app Tips ("if tails, the attack doesn't happen and the player's turn ends") + [OBSERVED] "Coin flip — Confused" followed by "The attack did nothing" twice (video 021327); "Whimsicott ex recovered from being Confused" right after it retreated (012720) — OCR scan. No self-damage: [COMMUNITY] Bulbapedia (explicit), pokemon-zone, Sportskeeda + the Sept 10 engine audit |

Variants and modifiers (card text):
- Toxicroak's Toxic and Toxapex's Severe Poison: "Poisoned. Do 20 [40] damage to this Pokémon instead of the usual amount." A newly applied Poison replaces the old one (and its amount). [COMMUNITY] pokemon-zone Triumphant Light rulings
- Nihilego's More Poison: "Your opponent's Active Pokémon takes +10 damage from being Poisoned." Two Nihilego = +20 is **[INFERRED]** from the confirmed stacking of other same-name passive Abilities; not observed.
- Some attacks pick a random condition "from among…" and never pick one already present (Alolan Muk ex Chemical Panic, Dustox Variety Powder).

## 2. Which conditions can exist together

- **Asleep, Paralyzed and Confused replace each other** — a Pokémon has at most one of them; the newest one wins.
- **Poisoned and Burned stack** with each other and with any one of those three (up to three conditions at once).
- Grades: [OFFICIAL] in-app Tips ("Asleep, Paralyzed, and Confused cannot stack with each other. If one of these Special Conditions is applied, it replaces any of the others"; Poisoned and Burned "can stack with other Special Conditions"); [COMMUNITY] pokemon-zone, Game8 JP ("ねむり、マヒ、こんらんの3種類はお互いに重複せず、新たに付与されたほうに上書き"), Altema; [IN-GAME TEXT] the UI has messages for a Pokémon becoming / recovering from one, two or three conditions at once; [OBSERVED] "Comfey is now Poisoned and Burned" and "Team Rocket's Hypno is now Poisoned and Burned" (video 004344, OCR).

## 3. What removes (and prevents) conditions

- **Moving to the Bench for any reason** — retreat, switch effects, being switched out by the opponent ("Pokémon will recover from Special Conditions, such as Poisoned, when they move to the Bench"; Tips: "When the retreating Pokémon returns to your Bench, any effects of attacks … or Special Conditions affecting the Pokémon end"). [OFFICIAL] in-app Tips + [IN-GAME TEXT] + [OBSERVED] "the UI confirms Poison recovery" on retreat (181914)
- **Evolving** — "When a Pokémon evolves, any effects of attacks … or Special Conditions affecting the Pokémon end." [OFFICIAL] in-app Tips + [OBSERVED] "Ivysaur recovered from being Asleep" after Quick-Grow Extract evolved a sleeping Bulbasaur (first-altaria)
- Card effects: Lum Berry (all, at end of each turn, then discarded), Pokémon Center Lady (all), Big Malasada (one random), Steel Apron / Comfey Flower Shield / Ogerpon Soothing Wind (cure and immunity).
- **Healing damage does not cure** a condition unless the card also says "recovers from…". [OBSERVED first-altaria: healed, stayed Asleep] + card wording
- **Immunity** ("can't be affected by any Special Conditions": Arceus ex Fabled Luster, Comfey, Ogerpon, Steel Apron): the condition is never applied — the game shows "…didn't become [condition]". [IN-GAME TEXT] + [OBSERVED] "Teal Mask Ogerpon ex didn't become Poisoned or Burned" / "…didn't become Confused" (video 012720, OCR)
- "Only Active Pokémon can have Special Conditions applied to them." Moving to the Bench "by retreating or some other way" removes them all. [OFFICIAL] in-app Tips

## 4. What each condition blocks

- Asleep / Paralyzed: **attacking and retreating** only. The game's message names exactly those two. Using **Abilities is not blocked** by any condition — no source or message restricts it. [IN-GAME TEXT; the Ability point is INFERRED from the absence of any restriction]
- Card effects can still move an Asleep/Paralyzed Pokémon: Koga returns Muk/Weezing to hand; Sabrina/Repel/Cyrus and switching Abilities work on it — and moving it to the Bench cures it. [COMMUNITY] Game8
- A Poisoned or Burned Pokémon **can** retreat (paying the cost). [OBSERVED 181914]
- A Confused Pokémon **can** retreat. [COMMUNITY] JP guides + [OBSERVED 012720, turn 12: X Speed, then the Confused Whimsicott ex retreated]

## 5. The end-of-turn sequence

After the turn player attacks (or ends the turn), in this order:

1. **The attack resolves completely** (damage, its effects, retaliation), then Knock Outs, points and promotion. (`02_damage_knockouts_points.md` §5)
2. **"At the end of your turn" / "at the end of each turn" effects.**
   **The player whose turn is ending resolves theirs first, then the other player.** [OFFICIAL] Detailed Battle FAQ:
   > "If both players have cards in play with effects that happen at the end of each turn, the effects of the cards
   > belonging to the player whose turn is ending are applied first."
   Official example — Darkrai (Bad Dreams: "At the end of each turn, if your opponent's Active Pokémon is Asleep, do 20
   damage") against an Asleep Pokémon holding Lum Berry:
   - Darkrai's owner's turn ends → Bad Dreams does 20 first → then Lum Berry cures Sleep and is discarded.
   - Lum Berry owner's turn ends → Lum Berry cures first → Bad Dreams does nothing (not Asleep).
   Cards with this timing include Bad Dreams, Lum Berry, Sitrus Berry, Deceptive Needle ("at the end of *your* turn"),
   Metal Core Barrier's self-discard ("at the end of your opponent's turn"), Mismagius's Cursed Prose ("at the end of your
   opponent's next turn, do 90 damage"), Zeraora ("at the end of your first turn").
3. **Pokémon Checkup** — "a step that happens after the end of each turn. During Pokémon Checkup, the state of both players' Pokémon is checked. If there are any Abilities or Trainer cards that come into effect during Pokémon Checkup, those effects are applied." [OFFICIAL] in-app Tips. It happens after **every** turn (the battle log records "Pokémon Checkup" each turn even with no conditions in play [OBSERVED log-scroll]).
   - "If both players' Pokémon are affected by Special Conditions, **the player whose turn just ended checks their Special Conditions first**." [OFFICIAL] in-app Tips
   - Within one Pokémon: **Poisoned → Burned (20, then flip) → Asleep (flip) → Paralyzed (recovers if its owner's turn just passed).** [OFFICIAL] in-app Tips
   - **"Pokémon Checkup is not considered to be part of either player's turn."** [OFFICIAL] in-app Tips. So "once during your turn" Abilities can't be used in it, and effects worded "during your turn" / "during your opponent's next turn" don't cover it [INFERRED from that sentence]; "at the end of … turn" effects happen before it [OBSERVED].
   - "During Pokémon Checkup" Abilities also resolve here: Flygon ex Sand Slammer (10 to each opposing Pokémon while Flygon is Active), Garganacl Blessed Salt (heal 10 each), Glaceon ex Snowy Terrain. Because Checkup happens after both players' turns, these fire **twice per round**. [COMMUNITY] pokemon-zone (Glaceon) + [OBSERVED] Sand Slammer at consecutive Checkups (flygon, 222326). **Poison resolves before Blessed Salt** [OBSERVED 010316: T16 Passimian went 130→120, then back to 130 from two Blessed Salt heals; T18 it went 120→110→130]. Burn is presumably the same [INFERRED]. The order between the two players' Checkup Abilities is [UNRESOLVED].
4. **Knock Outs from the Checkup**: "Any Pokémon that has no HP remaining at the end of Pokémon Checkup is Knocked Out." [OFFICIAL] in-app Tips. So Knock Outs wait until the whole Checkup is done, and a heal during the same Checkup (Blessed Salt) can save a Pokémon that Poison/Burn took to 0 [INFERRED from that wording; a lethal rescue remains unobserved]. Historical engine behavior: `unified1` Knocked a Pokémon Out as soon as Poison/Burn landed, before Blessed Salt, one Pokémon at a time (`07` M1). Fixed in rules1 and retained in active rules3.
5. The other player's turn begins (draw, Energy rotation).

Evidence that step 2 comes before step 3: in second-altaria, after Sleepy Lullaby two Benched Darkrai resolved Bad Dreams (70→60→40→20) **and then** the Checkup Sleep flip happened (Heads, "Oricorio recovered from Sleep"). Later, the first Bad Dreams knocked out a 10-HP Asleep Oricorio, the second Bad Dreams had nothing to hit, and **no Sleep flip happened** because Oricorio had left play. [OBSERVED] So a Pokémon knocked out by an end-of-turn effect is gone before the Checkup.

Consequences worth encoding:
- A Pokémon holding Lum Berry that is Poisoned/Burned/Asleep during the opponent's turn is cured at the end of that turn (before the Checkup), so it takes no Poison/Burn damage — **unless** the opponent's own end-of-turn effect fires first (Bad Dreams). [INFERRED from the OFFICIAL order + OBSERVED step order]
- A Pokémon put to Sleep on the opponent's turn flips at the Checkup right after that turn, so it has a 50% chance to wake before its own turn. [OBSERVED second-altaria] + [COMMUNITY]
- A Pokémon Paralyzed on the opponent's turn stays Paralyzed through its own next turn and recovers at the Checkup after that turn.
- Effects that last "during your opponent's next turn" run until the end of that turn; effects applied to a Pokémon end if it goes to the Bench (the official Cursed Prose ruling: retreat before the end of the next turn → no 90 damage). [OFFICIAL]

## 6. Rules history

Poisoned, Asleep and Paralyzed existed at launch (Oct 30, 2024). **Burned and Confused were added on Jan 29–30, 2025** (A2 Space-Time Smackdown), together with Pokémon Tools. Any data from before that date has no Burn, Confusion or Tools. [COMMUNITY] Bulbapedia

## 7. Engine note

The Sept 10 audit (`AUDIT_2026-09-10/01_ENGINE_FIDELITY.md`) found Asleep/Paralyzed Pokémon could attack and retreat, Paralysis cleared a Checkup early, and the Asleep/Paralyzed/Confused trio could coexist. START_HERE says Sleep and Paralysis work in `deckgym-unified1`. Re-checked 2026-09-22 by reading the unified1 source (`07`): attacking and retreating are now blocked while Asleep/Paralyzed, but **Asleep/Paralyzed/Confused still don't replace each other**, Checkup still goes in seat order, and Checkup Knock Outs happen too early (`07` M1).
