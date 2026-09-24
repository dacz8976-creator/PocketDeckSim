# Community Rulings Research — Pokémon TCG Pocket (PTCGP)

Research log answering QUESTIONS.md from player observations (Reddit, pokemon-zone, Limitless TCG, Game8, YouTube, deckgym-core GitHub issues).

Grades: OBSERVED (direct report/screenshot of actual game behavior) > COMMUNITY-CONSENSUS (multiple independent sources agree, no direct evidence shown) > SINGLE-SOURCE (one claim, unverified) > MEMORY-UNVERIFIED (my own training knowledge, not sourced — never trust for simulator).

Work in progress — appending as research proceeds.

---

## Q1 — Energy types per deck
**Answer:** Deck builder allows up to **3 different energy types** per deck; no restriction found on declaring types the deck "doesn't use" (Game8 explicitly warns meta decks should limit to 1 type for consistency, implying the game allows but doesn't optimally reward 2-3). Generation order among declared types is not player-controllable/random.
- Game8 Energy Zone guide: "You can have up to three different energy types in a deck, but keep in mind that you cannot choose what order these energies will generate." — COMMUNITY-CONSENSUS
- TheGamer: deck builder lets you "turn off" energy types you don't want generated — SINGLE-SOURCE (title only, fetch blocked by robots.txt) — suggests you actively select which of a Pokémon's possible types to include, i.e., you are not forced to include every color present in your Pokémon.

## Q2 — Opening hand guaranteed Basic / mulligan
**Not resolved with a direct source.** No reddit/Game8 source found explicitly describing the algorithm (basic-first-then-4-random vs. reshuffle-and-redraw) or confirming/denying a mulligan. MEMORY-UNVERIFIED only (not used).

## Q3 — Setup simultaneity / time limit
**Not resolved.** No source found describing whether Active+Bench selection is simultaneous/face-down or sequential, or any explicit setup timer (may be folded into the general 90s first-turn timer — unconfirmed).

## Q4 — Coin flip for going first
**Not resolved for timing (before/after setup).** Game8 (Battle System guide) confirms "Who goes first or second will be decided by a coin toss" but doesn't state whether this happens before or after Active/Bench placement. No Ranked-vs-casual difference found.

## Q5 — First-turn restrictions
**Answer, partially resolved:**
- Player going first (P1) **does NOT draw a card** on turn 1 — Game8 Rule Differences: "the player going first does not draw a card" (contrast with physical TCG where P1 does draw). — COMMUNITY-CONSENSUS
- **Supporter IS allowed turn 1 for both players** in Pocket — Game8 Rule Differences: "Player going first can use a Supporter card," explicitly called out as a difference from the physical game (which bans it turn 1). — COMMUNITY-CONSENSUS
- Evolution banned each player's own first turn (see Q28) — Game8 Evolution guide (see below).
- P1 attack turn 1: not explicitly documented, but since P1 gets no Energy Zone generation info found yet (Q6 unresolved) this is inferred, not confirmed. **Unresolved.**
- Retreat turn 1: not explicitly documented. **Unresolved.**

## Q6 — Energy Zone timing/visibility
**Answer, partially resolved:**
- Energy generates **at the start of a turn**: Game8 Energy Zone guide: "The energy zone is where energy is generated at the start of a turn." — COMMUNITY-CONSENSUS
- Bluestacks guide corroborates: "each turn your Energy Zone automatically generates one Energy, based on your deck's setup." — COMMUNITY-CONSENSUS (independent source agreement)
- **Next-energy preview**: both Game8 and Bluestacks confirm a small icon shows the upcoming energy type for **your own** Energy Zone. Neither source states whether the opponent's upcoming energy is visible to you (Q43 also unresolved on this point). Given the game shows an opponent's current Energy Zone type on their side of the board in the match UI (common player experience, but no citable source found), this is **SINGLE-SOURCE/unclear** — flag for the simulator to verify by screenshot if possible.
- With 2-3 declared types, generation appears to be "random order" each turn per both Game8 and Bluestacks, independent draws (not confirmed to exclude repeats). — COMMUNITY-CONSENSUS
- Whether P1 gets an Energy Zone generation/preview on turn 1 at all: **not resolved** — contradictory Game8 phrasing found twice ("If Energy is not used during the Pokemon Check phase between turns, new Energy will not be generated" appeared in two different fetches with slightly different wording, both grammatically unclear/possibly mistranslated by the extraction tool). **Do not trust this specific quote — flag as needs-better-source.**
- Unattached energy discarded at end of turn: **not resolved**, no direct source found.

## Q7 — Energy attachment mechanics
**Not directly sourced**, but Bluestacks/Game8 both discuss "once per turn" attachment implicitly (standard, undisputed community knowledge); no source explicitly confirms attaching to a Pokémon played the same turn is allowed. **Unresolved with citation**, though this is very likely allowed (no counter-evidence found and it's routine in gameplay videos, e.g. turn 1 basic + turn 1 energy attach is a standard opening).

## Q8 — Draw / hand limit
**Answer:**
- Empty deck: **no draw, no loss.** Game8 Rule Differences: "will not lose by decking out when drawing a card for turn from an empty deck." — COMMUNITY-CONSENSUS
- **Hand limit is 10 cards** — Game8 Rule Differences and Battle System guide both state "Maximum Hand Size 10 Cards." — COMMUNITY-CONSENSUS, but **a Facebook commenter disputed this** (title: "Discovering the 10-card hand limit in Pokemon TCG" — implies some players were surprised/unsure this was a hard rule) and a Game8-page commenter also flagged inaccuracy in the same guide (unspecified which claim). Net: 10-card limit is the community consensus figure but treat as not 100% bulletproof.
- What happens when a draw would exceed 10: **not resolved** — no source found describing whether the draw is simply skipped, cards are auto-discarded, or effect is capped. Flag as open.

## Q9 — Main phase order / post-attack actions
**Not resolved directly**, though universally understood among players that action order (Trainers, energy, retreat, evolve) before attacking is free-form and attacking ends the turn (no source explicitly enumerates "anything after attack" — strong community assumption is nothing can follow an attack). MEMORY-UNVERIFIED-adjacent; no explicit contradicting or confirming citation found this session.

## Q10 — Timers
**Answer (COMMUNITY-CONSENSUS, Game8 Time Limit guide):**
- Per-turn timer: **90 seconds**; turn auto-ends when it expires ("your turn will end, passing the turn over to the opponent").
- Total battle timer: **20 minutes**.
- At time-out: "points will be checked to see who wins the match. If both players have the same number of points at the end of the time limit, the Battle ends in a draw." — **implies the player with MORE points (even <3) wins outright at timeout; only a tie in points produces a draw.** This is a notable, specific finding for the simulator.
- No explicit info found on a hard turn-count cap separate from the 20-min timer.
Source: https://game8.co/games/Pokemon-TCG-Pocket/archives/474572

## Q11 — Pokémon Checkup timing and order
**Answer (COMMUNITY-CONSENSUS, Game8 "All Status Effects Explained"):**
- Checkup happens **at the end of every turn, for both players** — not just once per round: "Pokemon checks also occur at the end of your opponent's turn." This directly confirms Sleep/Paralysis/Poison/Burn are evaluated after EVERY single turn (P1's turn end AND P2's turn end), not merely "between rounds."
- **Processing order: Poison → Burn → Sleep → Paralysis.** Confusion is NOT part of the Checkup sequence — it's checked only when the confused Pokémon attempts to attack (flip then), not at Checkup.
- Source: https://game8.co/games/Pokemon-TCG-Pocket/archives/483132
- Not resolved: whether current-player's Pokémon or opponent's Pokémon is processed first when both have conditions at the same Checkup (no source found distinguishing this).

## Q12-15 — Winning / draws
**Partially resolved:**
- 3 points to win, regular KO = 1 point, ex = 2 points — confirmed widely (Game8 Battle System guide, standard knowledge, COMMUNITY-CONSENSUS). Mega Evolution ex = 3 points is stated in official marketing (not independently verified this session — flag for cross-check with official-sources agent A_official.md).
- Deck-out is NOT a loss — confirmed (see Q8). — COMMUNITY-CONSENSUS
- Q13 (loss on empty bench after Active KO), Q14 (simultaneous win conditions/tiebreak), Q15 (concede/disconnect handling): **not resolved**, no direct sources found this session.

## Q16 — Damage calculation order
**Not resolved with an explicit step-by-step order.** No source found sequencing attacker-modifiers → Weakness → defender-reductions → floor-at-0, or stating whether Weakness applies when base damage is already 0. Flag as open; important for simulator.

## Q17 — Weakness/reductions on Bench damage
**Answer (COMMUNITY-CONSENSUS, Game8):** **Weakness does NOT apply to bench damage** — "When damaging Benched Pokemon you do not apply Weakness. Weakness is applied only to Active Pokemon." Concrete example given: Zebstrika's Thunder Spear cannot KO a benched Staryu because Weakness isn't added to bench hits (only base 30 dealt). Source: https://game8.co/games/Pokemon-TCG-Pocket/archives/522247
- Whether defender-side damage-REDUCTION effects apply to a Benched Pokemon: **not resolved**, no source found either way.

## Q18 — "Prevent all damage" vs "prevent all effects of attacks"
**Not resolved.** No source distinguishing these two effect templates found this session (relevant cards: e.g. Mew ex/other "prevent all effects/damage" cards not searched individually — flag for follow-up per-card search if time allows).

## Q19 — "Damage from attacks" scope
**Answer, partial (COMMUNITY-CONSENSUS via pokemon-zone.com Space-Time Smackdown rulings article):**
- Rocky Helmet's retaliation damage functions like an ability trigger ("like Druddigon's Rough Skin ability"), fires only while the holder is Active, and **requires actual attack damage** — e.g. Bidoof's Super Fang (a non-damage-dealing attack effect) does NOT trigger it. This implies Rocky Helmet's own output is not itself "damage from an attack" (it's a triggered Tool effect), and that things which aren't attack damage don't trigger damage-based Tool retaliation either.
- Poison/Burn Checkup damage being exempt from "−X damage from attacks" reduction Trainer/ability effects: **not independently confirmed this session** (logical inference from card-template naming convention, not a direct citation — do not treat as verified).
- Source: https://www.pokemon-zone.com/articles/space-time-smackdown-rulings-interactions/

## Q20 — Knock Out timing / multi-KO / recoil
**Not resolved with a direct source** on: exact resolution point relative to full attack effect stack, whether Active+Bench KOs from one attack both award full points, promotion order after a double-KO, or whether a recoil-KO of the attacker awards the opponent a point. No sources found this session despite multiple search attempts. Flag as fully open — high priority for a targeted follow-up (try Limitless TCG Pocket rules FAQ directly, or search for a Regieleki/Explosion-style recoil clip).

## Q21 — Retaliation Tools (Rocky Helmet) and KO interaction
**Partially resolved:**
- Rocky Helmet only works while equipped Pokémon is **Active**, and only triggers on genuine attack damage (not non-damage attack effects) — pokemon-zone.com (COMMUNITY-CONSENSUS), see Q19.
- Whether it still fires when the damage that triggers it ALSO knocks out the holder, and who promotes first / how points are awarded if both attacker and defender are KO'd simultaneously by the retaliation: **not resolved**, no source found.

---

## Q22 — Special condition exact values/timing
**Answer (COMMUNITY-CONSENSUS, cross-confirmed by Game8 + Sportskeeda, consistent across sources):**
| Condition | Effect | Cure |
|---|---|---|
| Poison | 10 damage every Checkup (both turns' checkups) | Retreat/switch to bench; evolve; Lum Berry |
| Burn | 20 damage every Checkup, THEN coin flip; heads cures | Coin flip (heads); retreat; evolve; Lum Berry |
| Asleep | Cannot attack or retreat; coin flip each Checkup, heads wakes | Coin flip (heads); evolve; forced switch to bench |
| Paralyzed | Cannot attack or retreat; "automatically recovers at the end of the next Pokémon Checkup" (Sportskeeda's precise wording) | Automatic after ~1 full turn cycle; evolve; forced switch |
| Confused | On attack attempt, coin flip; **tails = attack fails, turn ends** (Sportskeeda explicit: no self-damage mentioned) | Evolve; retreat/switch (implied) |
Sources: https://game8.co/games/Pokemon-TCG-Pocket/archives/483132 , https://www.sportskeeda.com/pokemon/all-status-conditions-explained-pokemon-tcg-pocket
- **Notable Pocket-specific finding:** Confusion in Pocket does **NOT** deal self-damage on a failed (tails) attack, unlike the physical TCG's 30-damage self-hit. Corroborated by a Facebook PTCGP-group post explicitly titled "Someone knows why confusion does not damage when..." (title-only, fetch blocked by robots.txt) plus the Sportskeeda text omitting any self-damage clause. Grade: COMMUNITY-CONSENSUS (two independent sources, neither with a full screenshot/video, so not OBSERVED).

## Q23 — Condition coexistence
**Answer (COMMUNITY-CONSENSUS, Sportskeeda):** Poison "can stack with other special conditions" and Burn "can overlap with other status conditions" — meaning a Pokémon CAN be both Poisoned and Burned simultaneously, and Poison/Burn can coexist with Sleep/Paralyzed/Confused. Whether Sleep, Paralyzed, and Confused are mutually exclusive with EACH OTHER specifically was not explicitly stated by any source found (this mirrors the physical-TCG rule, but is not confirmed for Pocket — flag as inference only, not verified).

## Q24 — Abilities/retreat while afflicted
**Answer, partial:**
- **Cannot retreat while Asleep or Paralyzed** — confirmed by Sportskeeda's explicit "cannot attack or retreat" wording for both conditions, and independently corroborated by a Facebook PTCGP-group post title framed as correcting a misconception: "Why do people think they can retreat while asleep or paralyzed?" (title implies the true rule is they cannot). Grade: COMMUNITY-CONSENSUS (2 independent sources agree; title-only for the second, fetch blocked by robots.txt).
- Retreat while Confused: **not explicitly resolved** — no source states Confusion blocks retreat (only blocks/risks the attack). Community game-info pages consistently list Confusion's restriction as attack-only.
- Whether Abilities can be used while Asleep/Paralyzed/Confused: **not resolved**, no source found either way this session.
- Can Trainer/effect cards switch out an Asleep/Paralyzed Pokémon (bypassing the Pokémon's own inability to retreat)? **Yes** — pokemon-zone.com's Space-Time Smackdown article notes Koga can force a Weezing/Muk to bench specifically to cure their own status, i.e., forced switching from a Trainer effect works regardless of the Pokémon's own condition. Also directly stated by Game8's Sleep/Paralysis pages: "if a Weezing or Muk are afflicted with Paralysis, you can use the supporter card Koga to force them to return to bench." Grade: COMMUNITY-CONSENSUS.

## Q25 — What removes conditions
**Answer (COMMUNITY-CONSENSUS, Game8, multiple pages agree):** Evolving cures Sleep/Paralysis/Burn (and by extension likely all conditions — not explicitly itemized as "all" anywhere, but every condition-specific page states evolve as a cure). Retreating/switching to the Bench (by choice or by forced-switch Trainer effect) cures status conditions. Lum Berry (Tool) cures "any condition" at turn's end. Healing (removing damage) does **not** appear anywhere as a stated cure for conditions — no source claims HP-healing removes status; treat as NOT curing (absence-of-evidence but consistent across many "what cures X" lists that never mention healing).

## Q26 — Poison damage modifiers (stacking, whom they hit)
**Not resolved.** No source found this session addressing multi-copy stacking of poison-damage-boosting abilities (e.g., Nihilego-style) or whether such effects apply to all opposing Pokémon vs. just the poisoned Active. Flag open.

## Q27 — Sleep flip timing (can wake before own turn)
**Answer (COMMUNITY-CONSENSUS, Game8):** Yes — because Checkup runs at the end of EVERY turn (see Q11), a Pokémon put to sleep during the opponent's turn is flip-checked at that same turn's-end Checkup, so it can wake up before it ever reaches its own turn. Direct support: "There is a phase at the end of each Player's turn where all pokemon with status effects will be checked," combined with "Pokemon checks also occur at the end of your opponent's turn." Sources as in Q11/Q22.

---

## Q28-29 — Evolution restrictions & carry-over
**Answer (COMMUNITY-CONSENSUS, Game8 Evolution guide, https://game8.co/games/Pokemon-TCG-Pocket/archives/507683):**
- A Pokémon must have "been in play for at least one turn" before it can evolve — this single rule is what produces BOTH the "not on either player's first turn" restriction (nothing has been in play a full turn yet on turn 1) AND the "not a Pokémon played this same turn" restriction; they appear to be the same underlying rule, not two separate ones.
- **Cannot evolve twice in one turn on the same Pokémon**: explicitly confirmed — "if you evolve a Basic Pokemon into a Stage 1 Pokemon in one turn, you cannot evolve it into a Stage 2 Pokemon in the same turn."
- **ex Pokémon cannot evolve** (as of that guide's writing, pre-Mega-Evolution era): "As of now, ex Pokemon cannot evolve, even if their non-ex counterparts can." **This needs re-verification post-Mega-Evolution-ex launch (Sept 2025)** — see Q30 below; not re-confirmed this session whether Mega Evolution ex changed this by evolving FROM a Basic ex.
- Evolving **removes Special Conditions** (Poison/Burn/Sleep/Paralysis/Confusion cured) — explicitly stated ("you can heal it by evolving that Pokemon... Other conditions caused by your opponent's moves may also be negated").
- Whether damage, energy, and Tools carry over on evolution: **not explicitly stated by any source found** (the Game8 guide is silent on this). This is common knowledge among players (damage and energy persist, Tools stay attached) but **no citable source found this session — do not treat as verified, flag as MEMORY-UNVERIFIED-adjacent gap.**
- Whether both Active and Bench can evolve same turn: not explicitly stated, but no restriction found against it either.

## Q30 — Rare Candy / Mega Evolution ex specifics
**Not well resolved for Pocket specifically:**
- Rare Candy lets you "skip the Stage 1 evolution and jump straight from Basic to Stage 2" (pokemon-zone.com, COMMUNITY-CONSENSUS) — mechanically confirmed, but timing restrictions (same-turn-as-playing-the-Basic? first-turn-of-game?) were **not found for Pocket**. A PokeBeach ruling thread found on this topic is explicitly about the **physical TCG Compendium rules** ("Can I use Rare Candy on the first turn of a game... Yes, this is now permissible" — physical TCG only) and must NOT be assumed to carry over to Pocket, which has its own separate no-evolve-on-first-turn rule already. **Flag as unresolved for Pocket; do not import the physical ruling.**
- Mega Evolution ex "ends your turn" physical-XY-style restriction: **not found for Pocket** — no source confirmed or denied this. Given Mega Evolution ex launched in Pocket in Fall 2025 (Pokemon.com: "Mega-Evolved Pokémon Arrive in Pokémon TCG Pocket This Fall"), and whether Mega ex evolves from a Basic ex (contradicting the older "ex can't evolve" rule) was not independently re-verified this session. Flag as high-priority follow-up — check Limitless TCG's Mega Evolution ex card pages or a "how to Mega Evolve" Game8/pokemon-zone guide directly.
- Deck limits on Megas: not found.
- **UPDATE — RESOLVED (COMMUNITY-CONSENSUS, Game8 Mega Evolution list, https://game8.co/games/Pokemon-TCG-Pocket/archives/501550):** Mega ex Pokémon evolve directly from their Stage-1 form, NOT from an ex Pokémon — "Mega Evolved Pokemon will directly evolve from their previous stages. For example, Mega Blaziken ex will evolve directly from Combusken." This means the older "ex Pokémon cannot evolve" rule is **preserved, not broken**, by Mega Evolution ex — there is no intermediate "Blaziken ex" stage in this line. Separately, "Other Basic Stage Megas like Mega Absol and Mega Pinsir can be played as [Basics] immediately" — some Mega ex cards ARE Basics with no evolution requirement at all.
- **Mega ex KO = 3 points CONFIRMED** with citable source: "knocking out a Mega Evolved ex Pokemon will give you Three Points" (same Game8 page) — resolves part of Q12.
- Mega-Evolving-ends-your-turn (physical XY-style rule): **no source found stating this applies in Pocket** despite specific searching — treat as likely NOT a Pocket rule (absence of any mention across several Mega-focused guides), but not 100% confirmed absent.

---

## Q31-33 — Retreat / switching / Active-only effects
**Partially resolved:**
- Retreat is once per turn (Game8 Battle System guide, COMMUNITY-CONSENSUS): "You are allowed to Retreat only once per turn."
- **Cannot retreat while Asleep or Paralyzed** (see Q24) — COMMUNITY-CONSENSUS, 2 sources.
- Who chooses which attached Energy to discard on retreat, retreat-cost-reduction stacking, whether Trainer "switch" effects (Sabrina-style, Sabrina moves the OPPONENT's Active, not a self-retreat) count as "retreat" for once-per-turn purposes, and whether self-switch Trainer effects are blocked while Asleep/Paralyzed (vs. being forced-switch by an OPPONENT'S card, which Q24 confirms IS allowed): **not resolved**. Note: Q24's Koga-forces-Weezing-to-bench example is the OPPONENT forcing YOUR Pokémon to switch — this is different from a self-owned "switch" Trainer card (e.g., a card that lets you switch your own Active/Bench); that self-switch-while-afflicted case remains unconfirmed.
- Q32 (promotion order when both players must promote simultaneously) and Q33 (which Active-attached attack-effects end when the Pokémon moves to Bench): **not resolved**, no sources found.

---

## Q34-36 — Abilities
**Partially resolved:**
- Q35 **RESOLVED (OBSERVED-adjacent, pokemon-zone.com rulings article, high confidence)**: Same-name passive abilities DO stack. Explicit example: "Lucario's Fighting Coach... stacks, boosting Fighting-type damage by 20 per copy (includes Lucario's own attack)." This is a concrete, specific, testable finding — two Lucario Fighting Coach abilities in play = +40 damage to Fighting attacks, not +20 capped.
- Q34 (once-per-turn scope: per Pokémon instance? usable from Bench? new form gets its own use after evolving?) and Q36 (triggered-ability timing, e.g. "when played from hand," "when Knocked Out"): **not resolved**, no direct sources found this session despite several search attempts.
- Related finding also from pokemon-zone.com: Regice's Clear Body ability "Blocks attack effects targeting it; doesn't prevent damage or global effects like Meowth's Pay Day" — a useful "prevent effects vs prevent damage" data point relevant to Q18, showing an ability-based block only stops targeted attack EFFECTS, not damage, and not non-attack global effects.

---

## Q37-42 — Trainers
- Q37: Supporter is once per turn; **allowed on first turn for BOTH players** in Pocket (Game8 Rule Differences, explicit contrast with physical TCG) — COMMUNITY-CONSENSUS. Items are unlimited per turn (implicit/undisputed community knowledge; also implied by the Poké Ball + Professor's Research "which first" strategy debate found on Sportskeeda, which presupposes both Items are playable the same turn). Whether the UI blocks visibly-unplayable Trainers (e.g., Potion on full-HP Pokémon): **not resolved**, no source found.
- Q38: Tools — one per Pokémon (pokemon-zone.com: "You can attach only one tool to a Pokémon"). **Discarded when the Pokémon leaves play**: confirmed — "When a Pokémon returns to hand, the attached tool does not come with it. Instead, it is sent to the discard pile." Giant Cape (+20 HP) — "If Giant Cape is removed, the Pokémon immediately loses the extra 20 HP," which by direct implication means a Pokémon sitting exactly at/above its base HP threshold could be instantly Knocked Out the moment the Tool is removed (this specific KO-on-removal scenario itself wasn't shown in an example, but follows directly from the quoted mechanic). Grade: COMMUNITY-CONSENSUS. Source: https://www.pokemon-zone.com/articles/space-time-smackdown-rulings-interactions/
- Q39: Stadiums — **RESOLVED (COMMUNITY-CONSENSUS, Game8)**: "Stadium cards of the same name cannot be played when a Stadium that shares its name is already in play." Only one Stadium in play at a time; playing a new (different-named) Stadium discards the old one and ends its effect immediately: "if a new Stadium card comes into play, the previous Stadium is discarded and its effects end." Once per turn, like Supporters. Whether effects are symmetric (both players) was not explicitly confirmed, though Stadium effects are generally described as affecting "all Pokemon in play" (implying symmetry is the default, card-by-card). Source: https://game8.co/games/Pokemon-TCG-Pocket/archives/575671
- Q40: Fossils — **RESOLVED well (COMMUNITY-CONSENSUS, gameland.gg)**: Fossils are Item cards that become 40-HP Pokémon when played; "do not count as Pokemon while in the deck" (so **Poké Ball cannot fetch them**, and by the same logic they would NOT count toward the guaranteed-Basic opening hand check, though that specific opening-hand interaction wasn't independently tested/quoted). Can be discarded from play "at any time during your turn" with **no point given to the opponent** for self-discard, but "when destroyed by the opponent, fossils will give them a single point because it counts as a Pokemon" once in play. Whether one can be placed during initial Setup: not explicitly stated but logically follows since they're playable as a Basic-slot Pokémon. Retreat-cost/can't-retreat property not independently re-confirmed this session (matches well-known common knowledge but no fresh citation found).
- Q41: Search/draw — Sabrina's targeting is resolved (below); general Poké-Ball-randomness and what's revealed to the opponent were not independently sourced this session beyond the fossil-exclusion fact above.
- Q42: Supporter targeting — **Sabrina RESOLVED (near-official, card-text-level confidence)**: "Switch out your opponent's Active Pokemon to the Bench. (Your opponent chooses the new Active Pokemon.)" — i.e., Sabrina forces a swap but the OPPONENT (not you) picks their new Active. Source: https://game8.co/games/Pokemon-TCG-Pocket/archives/476278. Cyrus, Guzma-style tool removal, and Iono/Mars/Red Card hand-disruption specifics: **not independently re-verified this session** (card text is presumably already known locally per the project scope note; no new community disputes/clarifications surfaced).

---

## Q43-50 — Hidden info, randomness, misc
- Q43: Public info — **not independently sourced this session** beyond routine UI observation; no explicit article found confirming exactly what's visible (opponent hand size as card-backs, deck count, discard pile, both Energy Zones' current+next). Flag as needing a direct gameplay-screenshot source or UI walkthrough video citation.
- Q44: Coin flips — "flip until tails" mechanics (e.g. multi-flip attacks) not specifically sourced this session; 50/50 independence is standard/undisputed.
- Q45: **RESOLVED — valuable OBSERVED finding.** Copy-attack effects (Mew ex's Genome Hacking) use the COPYING Pokémon's own attached Energy/conditions to determine the copied attack's damage, NOT the original attacker's board state. Direct observed report (Threads, @bobabr0, quoted in search result): "when using mew ex's genome hacking, you still need all the energy requirements to do optimal damage of an attack. this mew ex player confidently sent his mew in to copy my blastoise ex's hydro bazooka (which was fully juiced on my end) and conceded after realizing he didn't copy my damage." Also covered by TheGamer article title "PSA: Mew ex Is Useless Against Pikachu ex" (fetch blocked by robots.txt, but headline is consistent with the same underlying mechanic — Mew ex copying an attack whose damage scales off the ORIGINAL attacker's energy/board state does not inherit that scaling). Grade: **OBSERVED** (direct first-hand account with specific game state described) for the Blastoise ex case.
- Q46: Effects that attach Energy from the Energy Zone outside the once-per-turn manual attachment (e.g., Manaphy's Oceanic Gift): confirmed to exist and function independently — pokemon-zone.com: "Manaphy's Oceanic Gift: Attaches Water Energy to up to two Benched Pokémon; still works with one Benched Pokémon" (i.e., it doesn't fizzle/fail if only one valid Bench target exists, an easy Q48-adjacent edge case). Whether it also consumes/blocks the separate manual once-per-turn attachment was **not explicitly stated** — flag as open.
- Q47: "During your opponent's next turn" effects when source is KO'd/retreats/evolves: **not resolved**, no sources found this session.
- Q48: Effects needing a target that doesn't exist (e.g. switch effect with empty Bench): **not resolved directly**, though the Manaphy finding above (Q46) shows at least one "up to N targets" effect gracefully handles fewer available targets rather than failing outright — this is suggestive but not a direct answer to the "completely empty bench" case for a self-switch or forced-switch effect.
- Q49: Ranked vs. casual/event/solo differences — **partially resolved**: Ranked Battles were **not present at launch** and were added "at the end of March 2025" (Game8 news page, announced at Pokemon Day 2025) — meaning for roughly 5 months post-launch (Oct 2024–Mar 2025) all matches were casual/unranked. No specific rules/timer differences between modes were found (e.g., whether the 90s/20-min timers differ in Ranked vs casual) — flag as open.
- Q50: Rule changes/errata since launch — **RESOLVED, well-dated (COMMUNITY-CONSENSUS / near-OFFICIAL via Bulbapedia, which tracks official set contents carefully)**: The **Space-Time Smackdown** expansion, released **January 30, 2025**, introduced **Pokémon Tool cards** and the **Burned and Confused Special Conditions** to the game for the first time — Bulbapedia: "It also sees the introduction of Pokémon Tool cards to the game, as well as the Burned and Confused Special Conditions." **This means from launch (Oct 2024) through Jan 29, 2025, the game had NO Tools and only 3 special conditions (Poison, Sleep, Paralysis) — Burn, Confusion, and everything about Rocky Helmet/Giant Cape/Lum Berry etc. did not exist yet.** Source: https://bulbapedia.bulbagarden.net/wiki/Space-Time_Smackdown_(TCG_Pocket). Additional dated changes: (2) Ranked Battles added end of March 2025 (see Q49). (3) Trading feature changes announced July 29 2025 and again for "Autumn 2025," plus a card-gifting feature for ◇–◇◇◇◇ rarities — economy/feature changes, not battle-rules changes. (4) No specific card-TEXT errata (a card's wording corrected post-release) was found this session — the only patch-note page fetched (v1.7.2, Sept 2026) yielded no itemized fix list; a follow-up should fetch the Game8 "All Patch Notes" archive index directly.

---

# Other edge cases found (not in the original 50, but valuable)

All from https://www.pokemon-zone.com/articles/space-time-smackdown-rulings-interactions/ unless noted — grade COMMUNITY-CONSENSUS (rulings-article format, no direct screenshot/video, but pokemon-zone.com rulings articles are generally well-regarded/close to official-adjacent in the community).

1. **Starly's Pluck discards the target's Tool BEFORE damage calculation** — meaning a Rocky-Helmet-holding Pokémon hit by Pluck takes the Pluck damage but its Rocky Helmet retaliation is denied because the Tool is already gone by the time damage resolves. A concrete, non-obvious ordering rule (effect-resolution-before-damage) that a simulator could easily get backwards.

2. **Regice's Clear Body ability** blocks attack EFFECTS specifically targeting Regice, but does NOT block damage, and does NOT block non-attack/global effects like Meowth's Pay Day (a bonus-points-style effect). Useful concrete example of "prevent effects" vs "prevent damage" vs "global effect" as three distinct categories (relevant to Q18).

3. **Pokémon Communication** (search Trainer) lets you search for a different card than the one you shuffle back, and explicitly CAN find a duplicate/same-name card as the one you returned — i.e., "search for a card" is not restricted to exclude the just-shuffled name.

4. **Manaphy's Oceanic Gift** attaches Energy to "up to two" Benched Pokémon and still functions normally with only one valid Bench target — confirms "up to N" targeting effects gracefully scale down rather than failing/fizzling when fewer targets exist (relevant to Q48's broader question).

5. **Lucario's Fighting Coach ability stacks additively across copies** — two Lucarios in play add +40 (not capped at +20) to Fighting-type attack damage, including Lucario's own attack benefiting from its ally's copy. Directly answers Q35 with a concrete number.

6. **Mew ex's Genome Hacking copies an attack's TEXT but re-evaluates any energy-count-scaling damage against Mew's OWN attached Energy**, not the original attacker's. Observed case: copying a "fully juiced" Blastoise ex Hydro Bazooka (which scales damage per extra Water Energy) did NOT copy the boosted damage because Mew itself lacked the extra Energy. This is the single most concrete, high-value finding in this research pass for Q45 — it's a first-hand, specific, OBSERVED game-state report (Threads/@bobabr0).

7. **Giant Cape's +20 HP is truly dynamic**, not a one-time heal: removing the Tool (e.g., via a tool-removal Supporter) immediately subtracts the 20 HP again, which can retroactively put existing damage at/above the new (lower) max HP. The article doesn't show an actual KO-on-removal case, but the mechanic as described logically produces one — worth a simulator test case.

8. **Confusion in Pocket deals NO self-damage on a failed attack** (tails), diverging from the physical TCG's 30-damage self-hit — this is a very easy trap for anyone porting physical-TCG logic into a Pocket engine. Two independent community sources (Sportskeeda's explicit condition list + a Facebook PTCGP-group post specifically asking "why doesn't confusion damage") agree.

9. **Fossils never count as Pokémon while sitting in the deck** — so Poké Ball (and by strong implication any other "search for a Basic Pokémon" effect) can never fetch a Fossil card. Self-discarding a Fossil from play gives the opponent NO point, but the opponent knocking it out DOES give them a point (it counts as a Pokémon only once in play).

10. **Space-Time Smackdown (Jan 30, 2025) was the origin point for both Pokémon Tools AND the Burn/Confused conditions** — before that patch the game's entire special-condition roster was just Poison, Sleep, and Paralysis, and no Tool cards (Rocky Helmet, Giant Cape, Lum Berry, etc.) existed at all. Any simulator or ruleset that tries to model "day one" Pocket needs to strip all of this out.





