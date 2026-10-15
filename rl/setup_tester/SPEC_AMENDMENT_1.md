# Setup tester, amendment 1: Kingambit plays Dustin's plan, not speed (Oct 15)

Audited and approved by Fable on Oct 15, with the P4 two-column change. It changes `SPEC.md`'s Kingambit plan config, script and measures. The general parts (inputs, exact
part, pairing, seeds, output format, out of scope) stand. **Nothing from the tester goes to Dustin until this is built and
reviewed.** The first run on `sonnet/setup-tester` d0eb22eb used the old defaults (Pawniard benched first, a fixed Copycat
rule, the Blade target as a count), so its numbers are not his plan's numbers.

## Why
Dustin, Oct 15 (verbatim): "That deck is not about getting kingambit as quickly as possible. I don't play pawniard right away
because of that. You want both glimmora to have a turn. Starting with regigigas as a wall with the chance to use ilima to pull
him back. You don't want muk/pawniard up front and that is the way you lose. Your copycat rule isn't how I think. It depends on
what I have in my hand and how many cards I get to draw. A big enough blade is defined as enough to knock out their likely
strongest pokemon and win the game."

So speed is not the yardstick. The question is whether the pieces line up with his plan at the moment that plan needs them.

## Card texts this rests on (lib/card.py)
- **Ilima** A3 149: "Put 1 of your [C] Pokémon that has damage on it into your hand." Regigigas is the list's only Colorless
  Pokémon, so Ilima is the Regigigas pull-back.
- **Lucky Ice Pop** B2 145: heals 20 from the Active; on heads it returns to the hand.
- **Copycat** B1 225: shuffle the hand into the deck, then draw one card for each card in the opponent's hand.
- **Mesagoza** B2a 093: once per turn, a coin; heads puts a random Pokémon from the deck into the hand.

## Script changes (Kingambit plan config)
1. **Lead.** Regigigas first, then Glimmet, then Alolan Grimer. Pawniard leads only when it is the only Basic (forced, and
   counted under P3).
2. **Pawniard stays in the hand** until the config's bench trigger.
   - **Default, T-first-KO (Dustin, Oct 15):** "Well I need time to get two energies on it which is two turns, which is how
     long it takes to evolve. Ideally pawniard hits the bench after one pokemon has been ko'ed. The deck has 5 pokemon (with
     evolutions), 2 glimmora, muk, Regigas and kingambit. The playfield has 4 spots. So pawniard taking a spot doesn't help".
     So Pawniard is benched on our first turn after one of our Pokémon has been knocked out, when a spot is free. It then gets
     the turn's Energy on our next turns until it has [DD], and evolves by Rare Candy no earlier than the turn after it was
     benched. Kingambit arrives already carrying [DD].
   - No Bench slot is reserved for Pawniard before the first knockout. The Bench holds the other lines (Glimmet/Glimmora,
     Alolan Grimer/Muk, Regigigas).
   - **T-now** (benched as soon as drawn, the old default) is run once on the base, for comparison only.
3. **Alolan Grimer and Muk** go to the Bench. They are never Active unless nothing else is left (P3).
4. **Glimmora gets a turn:** Glimmet evolves when legal. Energy goes to Glimmora so it can attack (Venomous Hit, [D]). A
   Glimmora "has had its turn" once it has been Active at the start of one of our turns with [D] attached.
5. **Promotion after a knockout:**
   - Kingambit, if it has [DD] and the Blade meets the target;
   - otherwise a Glimmora that has not had its turn, then the other Glimmora, then Glimmet, then Regigigas;
   - Muk or Pawniard only if nothing else is in play (P3).
6. **Energy order:**
   - Pawniard on the Bench, or Kingambit, up to [DD];
   - then the Active Glimmora up to [D];
   - then Regigigas while Muk is in play (Giga Turbo [CCC]);
   - otherwise the Active.
   Pawniard in the hand gets nothing.
7. **Copycat,** following his description. Play it when both hold:
   - (a) fewer than N of the plan cards still needed are in the hand (Pawniard, Rare Candy, Kingambit, Glimmet, Glimmora,
     Alolan Grimer, Muk);
   - (b) the opponent's hand is at least M larger than our hand without the Copycat.
   The opponent's hand comes from the clock record when it has one (C-his), otherwise 4. **N and M are asked of him once.**
   Until then the tables show N in {1, 2, 3} × M in {0, 1, 2} on the base, and the headline uses N=2, M=1, saying so.
8. **Not modelled, and why:**
   - Ilima's pull-back, the Pops' heals and the Helmet all act on damage, and the tester's clocks count knockouts, not damage.
     So they are blanks here, and the summary says "not valued here" for them.
   - That is a real limit for his plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them.
     Only his games or a bot that plays the plan can measure those.

## The measures that lead the tables (P-lines)
- **P1 Regigigas leads.** Regigigas is the Active at the start of the game (exact).
- **P2 Both Glimmora had their turn.** Under the clock: both Glimmora had a turn (rule 4) before the deal ends; also each one
  separately.
- **P3 Plan broken in front.** Under the clock: Muk or Pawniard is Active at any point (forced). Shown by cause: the opening,
  or nothing else left to promote.
- **P4 Ready at the winning moment.** The winning moment is the first point at which both hold:
  - the Blade (60 + 40·k) is at least their strongest Pokémon's HP;
  - that Pokémon's points (3 for a Mega ex, 2 for an ex, 1 otherwise) are at least the points we still need.

  At that moment, is Kingambit in play with [DD] or able to be that turn? "Able" means legal this turn from the hand and
  board: Pawniard on the Bench since the last turn, plus Rare Candy and Kingambit in the hand, plus the Energy. Shown as the
  share ready, and how many turns late it was when not ready.

  **P4 is reported in two columns (Fable's audit):**
  - **"Knocks out their strongest":** the HP condition alone.
  - **"Wins outright":** the HP condition plus enough points from zero.

  The table note says that any points we score before the Blade (Glimmora's Venomous Hit knockouts, for example) are not
  modelled, so "wins outright" is a lower bound. Without this split, a 2-point target like C-fixed medium could never fire,
  and that would read as a plan failure when it is a model gap.
- **P5 Plan reached in time.** P4 is ready before the opponent reaches 3 points.

The old G and K lines stay in the tables, below a line marked "descriptive (speed is not the goal)".

## The opponent's strongest Pokémon (each clock carries it)
- **C-his:** from his recorded opponents' boards in the positions file: per game, the highest-HP Pokémon seen in play, and
  its points.
- **C-bot:** the panel list's biggest HP in play at that game turn from the logs. When the logs don't show it, the list's
  biggest Pokémon, flagged.
- **C-fixed:** an assumed opponent per pace, stated in every table:
  - Fast: a 180-HP Mega ex, 3 points (the Blade needs k=3);
  - Medium: a 150-HP ex, 2 points (k=3, because 140 < 150);
  - Slow: a 220-HP Mega ex, 3 points (k=4).
  A row with a 190-HP Mega (k=4 without Red) is shown for reference.

## Tests to add (first, shown failing on d0eb22eb)
- Under T-first-KO, Pawniard is never benched before our first knockout. It gets [DD] on the next two turns of ours and
  evolves the turn after it was benched at the earliest. T-now reproduces d0eb22eb's numbers.
- Muk or Pawniard is promoted only when nothing else is in play, and each case counts under P3.
- Glimmora turn counting, on a fixed deck order.
- The winning moment: a hand-built game per C-fixed pace, with the k at which P4 fires and the ready or not ready result.
- The Copycat grid: N=0 never plays it. Very large N and M=-20 play it whenever legal.
- P1 matches the exact lead chance for Regigigas.

## Also: ky3 item 7's pilot test
`rl/results/next_pilot_2026-10/KINGAMBIT_ITEM7.md` section 3 adopts P2-P5 as its plan lines on his played list, with the
same definitions, before any run. In a bot game, "had its turn" means attacked at least once.
