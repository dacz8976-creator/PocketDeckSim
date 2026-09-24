# Pokémon TCG Pocket — open rules questions (grey areas) to resolve

Scope: the mobile game Pokémon TCG Pocket (Creatures / DeNA), NOT the physical Pokémon TCG.
Many physical-TCG rules differ in Pocket; do not assume a physical rule applies unless a Pocket source says so.
Card pool currently runs through set B4a (2026). Card text is available locally; you do not need to look it up.

## Setup and deck
Q1  Deck construction: 20 cards, max 2 copies per card NAME, at least 1 Basic. How many Energy types may a deck declare (1–3?). Any restriction on declaring types the deck doesn't use?
Q2  Opening hand: 5 cards with a guaranteed Basic — how is it guaranteed (Basic placed first then 4 random? redraw?). Any mulligan?
Q3  Setup: Active + up to 3 Bench chosen simultaneously / face-down? Time limit for setup?
Q4  Who goes first: coin flip? Is it shown before setup or after? Any difference in Ranked?
Q5  First-turn restrictions for the player going first (P1) and second (P2): energy (P1 gets none?), Supporter allowed turn 1 for both?, attack allowed for P1 on turn 1 (only 0-cost?), retreat on turn 1?, evolution banned on each player's first turn?, abilities?
Q6  Energy Zone: when is energy generated (start of turn? after draw?). Is the "next energy" preview visible to both players? With 2–3 types, is each turn's type uniformly random and independent? P1 turn 1: is an energy shown/generated at all? Unattached energy discarded at end of turn?
Q7  Energy attachment: once per turn from the Zone, to Active or Bench; attach to a Pokémon played this turn allowed?

## Turn
Q8  Draw at start of turn. Empty deck: no draw, no loss? Hand limit: is it 10? What exactly happens when a draw (start-of-turn or card effect) would exceed the limit — draw skipped, card discarded, or effect capped?
Q9  Order of actions in the main phase is free? Attack ends the turn. Anything that can be done after attacking?
Q10 Timers: per-turn time limit, total battle time, any turn cap (e.g. max turns → draw?). What happens when a timer runs out (auto end turn? loss?)
Q11 Pokémon Checkup: when exactly (between turns, after every turn)? Order of Poison, Burn, Sleep, Paralysis. Whose Pokémon are processed first (current player vs opponent)? KOs during Checkup: points and promotion order.

## Winning / draws
Q12 3 points to win; ex = 2 points; Mega Evolution ex = 3 points. Other point rules?
Q13 Loss when you have no Pokémon in play (Active KO'd with empty Bench). Timing: immediate?
Q14 Simultaneous win conditions (both reach 3 points at once, or one reaches 3 while the other is out of Pokémon, e.g. via recoil / Rocky Helmet / Checkup): draw? sudden death? tiebreak by current player?
Q15 Deck-out is not a loss — confirm. Concede and disconnect handling.

## Damage
Q16 Damage calculation ORDER: base damage → attacker-side modifiers (+X from Supporters like Giovanni/Red/Blaine, Tools, abilities) → Weakness (+20) → defender-side reductions (−X) → floor at 0? Does Weakness apply if the damage is 0? Is Weakness applied before or after reductions (matters when reduction floors damage at 0)?
Q17 Does Weakness apply to Benched Pokémon hit by an attack? Do damage-reduction effects on a Benched Pokémon apply to bench damage?
Q18 "Prevent all damage" vs "prevent all effects of attacks" — what each blocks (status conditions? bench damage? recoil?).
Q19 Damage vs "damage from attacks": poison/burn, ability damage, Rocky Helmet damage not reduced by "−X damage from attacks". Confirm.
Q20 Knock Out timing: checked after the attack fully resolves? Multiple KOs from one attack (Active + Bench): all points awarded? Order of promotion? Recoil KO of the attacker gives opponent points?
Q21 "When this Pokémon is damaged by an attack" retaliation (Rocky Helmet, Rough Skin-type abilities): does it still fire if the holder is Knocked Out by that attack? If the retaliation KOs the attacker too, who promotes first and how are points/win decided?

## Special Conditions
Q22 Exact values and timing: Poison 10 per Checkup (both turns), Burn 20 per Checkup then flip (heads cures), Asleep flip at Checkup (heads wakes), Paralyzed lasts until end of owner's next turn, Confused flip on attack (tails = attack fails; no self-damage). Confirm each with a Pocket source.
Q23 Which conditions coexist? (Asleep/Paralyzed/Confused mutually exclusive; Poison/Burn stack with those?) Can a Pokémon be both Poisoned and Burned?
Q24 Can an Asleep/Paralyzed/Confused Pokémon use Abilities? Retreat while Confused? Be switched out by Trainer/effects while Asleep/Paralyzed?
Q25 What removes conditions: retreat, switching to Bench, evolving, specific cards. Does healing remove them?
Q26 Poison damage modifiers (Nihilego-style "+10 poison damage"): stack with multiple copies? Apply to all opponent Pokémon?
Q27 Sleep flip timing: does the victim flip at the Checkup immediately after being put to sleep (so it can wake before its own turn)?

## Evolution
Q28 Restrictions: not on either player's first turn; not on a Pokémon put into play this turn; not twice in one turn on the same Pokémon. Is there any other? Can the Active and Bench both evolve?
Q29 What carries over on evolution: damage, energy, tools. What is removed: Special Conditions, attack effects ("can't attack next turn", "takes −X damage next turn")? Ability once-per-turn usage reset on evolving?
Q30 Rare Candy exact rules. Mega Evolution ex specifics: anything like the physical XY rule "Mega Evolving ends your turn"? Deck limits on Megas?

## Retreat and switching
Q31 Retreat: once per turn; who chooses which Energy to discard; retreat-cost reductions; blocked by Asleep/Paralyzed and by "can't retreat" effects. Do switch effects (cards that switch Active with Bench) count as retreat? Are they usable while Asleep/Paralyzed?
Q32 Promotion after KO: owner chooses; if both players must promote at once, order.
Q33 Effects attached to the Active (from attacks) that end when it moves to the Bench.

## Abilities
Q34 "Once during your turn" — per Pokémon instance? Usable from Bench and Active? Does evolving a Pokémon let it use the new form's ability again the same turn?
Q35 Same-name abilities stacking (e.g. two copies of a passive +damage ability).
Q36 Triggered abilities ("when you play this Pokémon from your hand", "if this Pokémon is Knocked Out") timing.

## Trainers
Q37 Supporters: one per turn, allowed on the first turn for both players? Items unlimited. Can you play a Trainer that would have no effect (e.g. Potion on an undamaged Pokémon)? Does the UI block unplayable cards?
Q38 Tools: one per Pokémon; can they be moved/removed? Discard when the Pokémon leaves play. HP-boosting Tool removed when damage ≥ new HP → immediate KO?
Q39 Stadiums: one in play; can you play a Stadium with the same name as the one in play? Replace opponent's Stadium? Limit per turn? Where does the replaced Stadium go? Are Stadium effects symmetric?
Q40 Fossils: played as a 40-HP Basic Colorless Pokémon; can't retreat; discard at any time during your turn. Do they count as Basic Pokémon for the guaranteed opening hand and for Poké Ball? Can one be placed in setup? KO gives 1 point?
Q41 Search/draw cards: random vs chosen (Poké Ball random Basic?), what's revealed to the opponent.
Q42 Supporter targeting: Sabrina (opponent chooses new Active?), Cyrus (you choose a damaged benched Pokémon), Guzma-style tool removal, Iono/Mars/Red Card hand disruption details.

## Hidden info, randomness, misc
Q43 What is public: opponent hand size, deck count, discard pile, both Energy Zones (current + next), points.
Q44 Coin flips: 50/50 independent; "flip until tails" unbounded.
Q45 Copy-attack effects (Mew ex Genome Hacking and similar): energy requirements of the copied attack, whether modifiers apply, "this Pokémon" references.
Q46 Effects that attach energy from the Energy Zone (not the once-per-turn attachment) — do they use up the manual attachment?
Q47 "During your opponent's next turn" effects when the source Pokémon is KO'd, retreats, or evolves.
Q48 Effects that need a target that doesn't exist (switch with empty Bench) — can the card be played / does the attack still do damage?
Q49 Any differences between Ranked, casual/random matches, event battles, and solo/AI battles in rules or timers.
Q50 Any official rule CHANGES or card behaviour fixes/errata announced since launch (Oct 2024) — list each with date.
