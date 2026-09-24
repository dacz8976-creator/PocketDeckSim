# 02 — Damage, Weakness, Knock Outs, points

Grades as in `01_game_structure.md`. Sources in `06_sources.md`.

---

## 1. Damage calculation order — OFFICIAL

The game's "Detailed Battle FAQ" (reached in-app from Menu › Tips › Detailed Battle FAQ) answers this directly:

> 1. Start with the attack's damage.
> 2. Apply any effects that affect the Attacking Pokémon.
> 3. Apply Weakness.
> 4. Apply any effects that affect the Defending Pokémon.
>
> Example: a 50-damage attack against an Active Pokémon that "takes –20 damage from attacks", with Bounded Field
> in play (Weakness ×2): **50 × 2 – 20 = 80**.

Japanese original: ワザの基本ダメージ → ワザを使うポケモンにかかっている効果 → 弱点 → ワザを受けるポケモンにかかっている効果. **[OFFICIAL]**

What belongs in each step (the FAQ does not list them; this sorting is **[INFERRED]** from the card wording, and the
observed cases below all fit it):

| Step | Contents | Examples |
|---|---|---|
| 1. Attack's damage | Printed number plus the attack's own text: "X more damage", "+30 for each…", "instead", coin-flip multipliers, "for each point you have" | Indeedee ex Psychic 30 + 30/Energy on the defender = 90/120/180 [OBSERVED]; Lightning Accelerator 80 + 30/point [OBSERVED]; Brilliant Storm 40 + 20/team Psychic [OBSERVED] |
| 2. Attacker-side effects | Supporter/Item "during this turn" boosts (Giovanni, Red, Clemont's Backpack), attacker Abilities (Lucario Fighting Coach, Aegislash Cursed Metal), Stadiums (Training Area), "your next turn +X" (Happiny Chubby Cheer), Tools on the attacker, and debuffs placed on the attacker ("Attacks do −X damage") | Training Area +10 and 2× Clemont's Backpack +20 each on Electrispark: 40+20+20+10 = 90 [OBSERVED trial-manectric] |
| 3. Weakness | +20 to the opponent's **Active** Pokémon if the attacker's type matches its Weakness (×2 instead under Bounded Field, for non-Mega attackers) | Phoenix Turbo 80 → on-screen "Weakness 100" [OBSERVED trial-revavroom]; V-Flame 40 → 60 [OBSERVED 014933] |
| 4. Defender-side effects | "takes −X damage from attacks" (Heavy Helmet, Metal Core Barrier, Steel Apron, Abilities, attack effects like Superb Shield), "takes +X damage from attacks", damage prevention (Safeguard, Disguise, "prevent all damage that is X or less", coin-flip prevention like Securely Sheltered) | Metal Core Barrier −50: Wild Swing 60 → 10, Mega Blaster 140 → 90 [OBSERVED 220914]; Fighting Coach +20 and Heavy Helmet −20 on 110 → 110 [OBSERVED 031007] |

- **Damage never goes below 0.** Hisuian Goodra's Securely Sheltered (Heads, −80) against a 70-damage Quick Straight gave a literal 0. [OBSERVED 031007]
- Boosts from several sources add up (two Clemont's Backpacks + Training Area = +50) [OBSERVED trial-manectric]; same-name passive boosts stack (two Fighting Coach = +40) [COMMUNITY] pokemon-zone. Several reductions on one Pokémon add up the same way: Metal Core Barrier (−50) plus Skarmory ex's Steel Wing ("During your opponent's next turn, this Pokémon takes −20 damage from attacks") stopped a 70-damage Turbo Shark completely (70 − 50 − 20 = 0) [OBSERVED native-skarmory-indeedee]. (An earlier fact-check wrongly said Steel Wing wasn't a real card and this was dropped; it is Skarmory ex's attack, A4 124.)
- The GameWith JP weakness page gives the same order independently: "10(ワザのダメージ)+20(弱点)-20(ワザの効果)". [COMMUNITY]

### Where this differs from the deckgym engine (upstream and the project fork)

`deckgym-fork-s193/src/hooks/core.rs` (~line 1705, the unified1 source; upstream `core.rs` ~lines 1308–1329) computes
`(base + all attacker bonuses + "takes +X" vulnerability) − all reductions, floored at 0`, **then** adds Weakness. Upstream
`bcollazo/deckgym-core` (Sep 17, 2026) does the same. Per the official order this is wrong whenever the order matters:

| Case | Official | Engine |
|---|---|---|
| 10 damage, Weak, defender −20 | 10 + 20 − 20 = **10** | max(10 − 20, 0) + 20 = **20** |
| 50 damage, Bounded Field (×2), defender −20 | 50 × 2 − 20 = **80** | (50 − 20) × 2 = **60** |
| **Seen in play (Dustin, 2026-09-21):** 60-damage Fire attack into Skarmory ex (weak to Fire) holding Metal Core Barrier (−50), Bounded Field in play | 60 × 2 − 50 = **70** ✓ — the game showed **70** | (60 − 50) × 2 = **20** ✗ |
| 30 damage, Weak, defender "prevent all damage done by attacks that is 40 or less" | 30 + 20 = 50 → **not** prevented, *if* the threshold is a step-4 Defending-Pokémon effect [INFERRED] | engine also checks the threshold after Weakness → 50, same |
| Flat additive cases with no floor (e.g. 60 +20 −30) | 50 | 50 (same) |

So flat cases agree; cases with a reduction bigger than the pre-Weakness damage, or Bounded Field, disagree. Dustin's Skarmory game confirms the official order in play (row above) [OBSERVED, video]. Same game, next turn: 60 into Skarmory ex with Metal Core Barrier + Jasmine + Steel Wing (−120 total per Dustin) → 0; both orders give 0 there. A 20-damage Fire hit on Skarmory ex under Bounded Field + Steel Wing also showed 0: the official order explains that only if more than −40 of reductions were on it (e.g. Metal Core Barrier still attached) — to check in the video.

## 2. Weakness details

| Rule | Grade |
|---|---|
| Weakness is **+20**, not ×2. There is **no Resistance**. | [COMMUNITY] Bulbapedia, Game8, GameWith, pokemon-zone + [OBSERVED] (80 → "Weakness 100") |
| Weakness applies **only to the Active Pokémon**, never to Benched Pokémon hit by an attack ("Don't apply Weakness for Benched Pokémon"). | [OFFICIAL] in-app Tips + [COMMUNITY] Game8 (Zebstrika/Staryu example), GameWith, pokemon-zone (Swirling Disaster "applies Weakness to the opponent's Active Pokémon") |
| Weakness does **not** apply when the attack does no damage: a no-damage attack, a failed attack, a coin-flip attack that rolled 0. It never applies to Poison/Burn or other non-attack damage. | [COMMUNITY] GameWith JP (five-item list) |
| Some attacks ignore it: "This attack's damage isn't affected by Weakness" (Hitmonchan ex Quick Straight); Ledian's Swift ignores Weakness **and** every effect on the Defending Pokémon (skip steps 3 and 4); "isn't affected by any effects on your opponent's Active Pokémon" (Morgrem, Mega Medicham ex) skips step 4. | card text + [OFFICIAL] Mimikyu ex FAQ (Swift ignores Disguise) |
| Some Pokémon have no Weakness (Baby Pokémon; effects that grant "No Weakness"). | card text + [IN-GAME TEXT] status labels |
| Bounded Field (Stadium): Weakness from non-Mega-ex attackers is ×2 instead of +20, for both players. | card text + [OFFICIAL] FAQ example |

## 3. Bench damage and which boosts reach it

- Weakness: never on the Bench (above).
- **Attacker-side boosts apply to whatever targets their text names.** "+X damage to your opponent's **Active** Pokémon" (Giovanni, Training Area, Fighting Coach, Cursed Metal, most Abilities) does **not** add to Bench hits; "+X damage to your opponent's **Pokémon**" (Clemont's Backpack) **does**.
  - [OBSERVED] four times: Electrispark's Bench portion got Clemont's Backpack's +20 but not Training Area's +10 (023151, trial-manectric); Random Spark on a Benched Darkrai got no Training Area bonus (second-altaria).
  - [COMMUNITY] did2memo (JP): Giovanni's +10 applies to the Active part of a spread/random attack only; not to Bench picks, not to Ability damage, not to a 0-damage result.
  - ⚠ Engine: every turn-long boost is Active-only (`hooks/core.rs:1015`), so Clemont's Backpack's +20 never reaches the Bench (`07` M2, shown by running it).
- Defender-side effects on a Benched Pokémon apply if their text doesn't restrict them to the Active Spot (e.g. Protective Poncho *only* works on the Bench; Rocky Helmet *only* in the Active Spot). [INFERRED from card text; Protective Poncho [OBSERVED second-altaria]]
- A protection Ability on the Active (Oricorio's Safeguard vs ex attacks) protects only that Pokémon; the same attack's Bench damage still lands. [OBSERVED 031901, 170229]
- Random multi-hit attacks ("1 of your opponent's Pokémon is chosen at random 4 times… do 50 damage to it"): a JP guide reports Giovanni's +10 was added **once** to the Active's total (50×2 → 110), i.e. hits on the same Pokémon are totalled before modifiers. [SINGLE] did2memo — not verified in the recordings.

## 4. Kinds of damage and prevention

| Damage source | Counts as "damage from an attack"? | Grade |
|---|---|---|
| The attack's damage to Active or Bench | Yes | — |
| Poison / Burn at Checkup | **No** | [OFFICIAL] Mimikyu ex FAQ |
| Ability damage (Greninja Water Shuriken, Crobat Cunning Link, Darkrai Nightmare Aura, Flygon ex Sand Slammer) | **No** | [OFFICIAL] Mimikyu FAQ + [COMMUNITY] did2memo (Giovanni's +10 not added to Water Shuriken). (The recordings show Aegislash's "−80 from attacks by Pokémon ex" not reducing Crobat's Cunning Link, but Crobat isn't an ex, so that case doesn't prove this.) |
| Tool damage (Rocky Helmet, Deceptive Needle) | **No** | [OFFICIAL] Mimikyu FAQ + [OBSERVED 031901]: Safeguard didn't stop Deceptive Needle |
| Retaliation damage (Rough Skin) | **No** — so Rough Skin does not trigger another Rough Skin or Rocky Helmet | [COMMUNITY] pokemon-zone Mythical Island rulings |

Therefore "takes −X damage from attacks", Disguise, Safeguard, "prevent all damage done by attacks", Giovanni-style boosts
and Weakness all ignore those non-attack sources. Historical engine finding: `unified1` Heavy Helmet (B1 219, "−20
damage from attacks") also reduced Poison, Burn, Ability and Tool damage (`07` H2). This was repaired in rules1 and is
retained in active rules4: Heavy Helmet reduces attack damage only. Metal Core Barrier and Steel Apron are right.

The game has three separate prevention wordings, and they do different things **[IN-GAME TEXT]**:
- "Prevent all damage done by attacks" — damage only; Special Conditions and other effects still apply.
- "Prevent all effects of attacks used by the opponent's Pokémon" — effects only; damage still applies ("Damage are not effects": Regice). [COMMUNITY] pokemon-zone
- "Prevent all damage from—and effects of—attacks" — both. (Cramorant's Dive: attack damage/effects only, not Abilities or effects on other Pokémon.) [COMMUNITY]
- "Negate the entire attack" style (Manectric's Flash) stops Bench damage too. [COMMUNITY] pokemon-zone Triumphant Light rulings

## 5. When Knock Outs happen, and the order of everything after an attack

- A Pokémon is Knocked Out when its remaining HP reaches 0. The log shows "Knocked Out". [IN-GAME TEXT]
- **An attack resolves completely before Knock Outs are processed.** After lethal damage, the attack's other effects still happen: Turbo Shark still attached its Bench Energy after KO'ing its target (three uses, 220914); Mega Burning still applied Burn to and discarded Energy from the already-lethal hit (225430); Gyarados ex's Rampaging Whirlpool discards Energy "including from knocked-out Defending Pokémon". [OBSERVED] + [COMMUNITY]
- Observed order after an attack's damage, battle 225430 (Mega Burning / Sunny Scorching into Team Rocket's Electrode holding Rocky Helmet): **attack damage → the attack's own effects (Burn, Energy discard) → Tool retaliation (Rocky Helmet 20) → on-KO Ability (Destiny Burst 70) → Knock Outs, points, promotion.** [OBSERVED, twice in the same battle]
- Official support for "attack effects before after-attack triggers": Budew's **Prickly Powder** (B3 013/159, JP ひりひりパウダー; earlier notes called it "Itchy Pollen": "The Defending Pokémon loses all Abilities…") stops Druddigon's Rough Skin from firing on that same attack — Budew takes no damage — but a pre-existing "−30 from attacks" Ability still reduced that attack. [OFFICIAL] JP Detailed Battle FAQ 57286218211225
  ⚠ The engine gets this wrong (`07` M4, shown by running it): retaliation runs before the attack's own effects, and the Rough Skin family is wired by card number, so it ignores Prickly Powder and Alolan Muk's Power of Alchemy. Iron Jugulis (B3a 046) and Dragalge ex B3 231 never retaliate at all.
- Official (JP Pokémon Support, Gameplay section, article 41083304332057): when Grapploct's attack knocks the Defending Pokémon to the Bench and that damage is lethal, the Pokémon is Knocked Out **on the Bench**. So the attack's effect (the move) happens before the Knock Out, and the Pokémon is no longer "the Active Pokémon" when it's KO'd (it didn't count for an "Active Pokémon Knocked Out" Battle Trial). [OFFICIAL]
- **Retaliation still fires when the holder is Knocked Out by the attack** — Rocky Helmet did its 20 in four separate observed cases (Hydreigon 50→0 then Gabite 80→60; Heatmor; two Electrodes). [OBSERVED ×4]
- Attacks that remove Tools "before doing damage" (Starly's Pluck) prevent Rocky Helmet. [COMMUNITY] pokemon-zone + card text
- A Pokémon cannot retreat or respond during the opponent's attack. [OBSERVED second-altaria]
- An attack's own "discard a card" cost was shown after its damage (Soul Shot). [OBSERVED 221914] — presentation order; whether it can matter is unclear.

## 6. Points

- 1 / 2 (ex) / 3 (Mega Evolution ex), awarded to the opponent of the Pokémon's owner, **no matter who caused the Knock Out** — e.g. Hailstorm's damage to its own Bench KO'd the attacker's own Carvanha and gave the defender a point in the same resolution as the main KO. [OBSERVED 024406, native-skarmory-indeedee]
- Several Knock Outs from one attack or one Checkup all score: "If a player Knocks Out more than one Pokémon at the same time, they get a point for each Pokémon." More than 1 point comes from Pokémon "with a Rule Box" (ex, Mega ex). [OFFICIAL] in-app Tips + [OBSERVED]
- The Knocked-Out Pokémon goes to its owner's discard pile with "all Energy and other cards attached to it" (Tools, the cards it evolved from). [OFFICIAL] in-app Tips
- A Knock Out can happen without points: Glimmora's Shattering Crystal (Heads → "Opponent was unable to get any points"); that Pokémon still counts as Knocked Out for other cards (Kingambit's Overlord's Blade counted it). [OBSERVED 181914] + [IN-GAME TEXT]
  The card text ("When this Pokémon is Knocked Out, flip a coin…") covers any Knock Out, including Poison/Burn and
  Ability damage. ⚠ Engine: the coin only flips for attack Knock Outs; a Poisoned Glimmora always gives the point
  (40/40 runs, `07` M3).
- Extra points: "Get 1 more point if the opponent's Active Pokémon is Knocked Out by damage from an attack used by X". [IN-GAME TEXT]
- Removal without a Knock Out (discard effects, returning to hand) gives **no** points. [OFFICIAL] + [OBSERVED 150630: Gyarados's Wild Swing discarded Dustin's own two Benched Pokémon; the score stayed 1–1.]
- Self-discarding a Fossil gives no points; a Fossil Knocked Out gives 1. [COMMUNITY] Bulbapedia, gameland

## 7. Promotion after a Knock Out

- The owner of a Knocked-Out Active chooses which Benched Pokémon to promote ("After that, the player puts one of their Benched Pokémon in the Active Spot"; a chooser is shown; with one option it is filled at once). [OFFICIAL] in-app Tips + [OBSERVED 031901, 220914]
- No Benched Pokémon → that player loses immediately (no prompt), "regardless of the number of points each player has" [OFFICIAL] in-app Tips. Narrow observed T2 exception: in the recorded seat, Dustin had 2 points and his last Pokémon received the 3rd point while being Knocked Out in the same attack; the result overlay was a tie. The opponent still had Pokémon, and its final 2 points are inferred from the ex Knock Out rather than shown on the overlay. Rules4 implements this narrow case; both-seat engine fixtures are regression coverage, not video evidence. See `05` #2 and the [rules4 repair record](../Boss%20Folder/rules4-t2-repair-2026-09-22/README.md). Other simultaneous-result rows remain unverified.
- A Pokémon promoted after a Knock Out did **not** "move from the Bench to the Active Spot this turn" for cards like Scizor's Gale Thrust. [OFFICIAL] Scizor FAQ
- **Double Knock Out (both Actives at once): the attacker (turn player) promotes first, then the opponent — who went first that battle doesn't matter.** [DUSTIN, from experience] + [OBSERVED 225430, frames 146–168 s, consistent]. It is not "owner of the first Pokémon Knocked Out promotes first": Electrode hit 0 before Castform, yet Dustin (the attacker) promoted first. Full sequence seen: Castform's Sunny Scorching (30) KOs the 20-HP Team Rocket's Electrode and Burns it → Rocky Helmet 20 KOs Castform → Destiny Burst 70 on the already-zero Castform → both Pokémon leave play together → "+1 point!" for the turn player, then "+1 point!" for the opponent → turn player promotes (Mega Blaziken ex) → opponent promotes (Electrode) → "Opponent's turn — Current turn: 6".
  Engine: unified1 promoted by seat (wrong on player 1's turns). Fixed in rules1: after an attack the attacker promotes first in either seat. rules2 also fixed a crash in this exact Rocky Helmet → Destiny Burst double KO, found by replaying 225430 (Astra, 2026-09-22).
- **Knock Outs outside an attack during your turn are processed right away, and your turn goes on.** Ability damage (Greninja Water Shuriken, Crobat Cunning Link) or removing an HP bonus (Tool discarded, Stadium replaced): the point(s) are scored at once (the game ends there if it's the winning point); if the Pokémon was Active its owner promotes; then you can still attack. A Benched Pokémon Knocked Out this way gives the point with no promotion. [DUSTIN] + [OBSERVED 025604: Cunning Link KO'd Aegislash, the opponent promoted, then Crobat's Darkness Fang in the same turn]. Classic line: Water Shuriken a Benched Pokémon → Cyrus brings that damaged Pokémon Active → attack it. Engine ✓: a catch-all Knock Out check runs after every action (`apply_common_action_suffix`), and Guzma/Stadium play check directly.

## 8. HP changes and healing

- HP bonuses (Giant Cape +20, Leaf Cape +30, Elegant Cape +30, Starting Plains +20) raise maximum HP **and** remaining HP by the same amount; damage taken is unchanged (Slowking ex 110 remaining → 140, max 160). [OBSERVED accepted-232035] A Tool whose bonus depends on the holder (Elegant Cape: "The Stage 1 Pokémon this card is attached to gets +30 HP") does nothing on a Basic and starts working when it evolves: Type: Null 80 with Cape → Silvally 110 + 30 = 140. [OBSERVED 152812, twice]
- Removing the bonus (Tool discarded, Stadium replaced) removes the HP immediately ("If Giant Cape is removed, the Pokémon immediately loses the extra 20 HP"). [COMMUNITY] pokemon-zone. A Pokémon whose damage is ≥ its new HP is Knocked Out **right away**: points at once (game over if it's the winning point), its owner promotes if it was Active, and the turn continues — the player who removed the bonus can still attack. [DUSTIN] Engine ✓ (§7).
- Cards that care about maximum HP read the boosted value (Wallace can't choose a 50-HP Staryu wearing Giant Cape). [OFFICIAL] ⚠ The engine's Wallace check reads printed HP (`card_logic/wallace.rs`), so it would allow that Staryu. [INFERRED from code] Dustin confirms the game blocks it.
- Healing can't exceed maximum HP (Watch Over healed only 10 of 20 at 140/150). [OBSERVED 031007]
- Healing does not cure Special Conditions unless the card says so. [IN-GAME TEXT card wording] + [OBSERVED first-altaria]
- Evolution keeps damage (e.g. 30 damage on Electrike → Mega Manectric ex at 150/180). [IN-GAME TEXT] + [OBSERVED ×5]
