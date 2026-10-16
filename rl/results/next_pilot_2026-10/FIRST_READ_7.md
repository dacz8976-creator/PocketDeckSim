# First read of the seven turns that need a second reader (ky3 item 7, Oct 16)

One reader's verdicts, written before any run, for `KINGAMBIT_ITEM7.md` section 3 ("Need a second reader before they count"). A positive
counts only when his move is upheld by him or by two readers, so every line here is **pending second reader** in `EXPECTED_KG.md`.

**How this was read.** From the v3 position records (`pause_games_new_2026-10-13/v2/positions_all.json`: boards, Energy, hands, discards, points,
his plan), km3's 12 plans per turn (`v2/runs_km3/`), and the card texts from `lib/card.py`. No frames, no video, nothing about how the game
went except what `POSITION_TABLE.md` already says. The opponent's hidden hand is unknown, so every "next turn" below is the board's own threat,
not a prediction. Each verdict says what it rests on, so the second reader can check it from the same files.

Verdict key: **upheld** = on this board his move is at least as good as km3's, for a reason that can be checked; **unclear** = both are
defensible; **km3 better** = none this time.

| turn | verdict | confidence |
|---|---|---|
| 210041 t06 | upheld | medium |
| 203719 t07 | upheld | medium |
| 210823 t08 | upheld | medium |
| 010706 t11 | upheld | medium-high |
| 010837 t05 | upheld | low-medium |
| 014423 t03 | upheld | high (but not a Blade-pricing case) |
| 203719 t11 | upheld | medium-high |

## 210041 t06: Energy on the benched Pawniard and end the turn (km3: Ilima, then Pawniard in front, Slash)

- **Board:** his Active is a 40-HP Regigigas with no Energy. Bench: Glimmet, Alolan Muk, Pawniard (no Energy). Hand: Ilima, Kingambit, Lucky Ice
  Pop. The opponent's Active is Mega Lucario ex (190 HP, FF attached, Fighting Pulse 90, +50 with a third [F]). Regigigas is weak to Fighting.
- **What km3 does (12 of 12):** Ilima takes the Regigigas back, Pawniard is promoted, the Energy goes on that Pawniard, Slash.
- **Reading:** Regigigas at 40 HP falls to Fighting Pulse whatever he does (90 + 20 weakness), so it is one point for them either way. The
  difference is who is in front when it falls. With Ilima, the 50-HP Pawniard is Active and is the one that falls (the opponent's next
  Energy is Fighting, which makes Pulse 140, far more than Pawniard's 50). Pawniard is the future Kingambit and the Energy on it would be
  lost with it. His line lets the damaged Regigigas, which has no Energy on it, be the one that falls, and puts the
  Energy on the Pawniard that stays safe on the Bench. That is his plan lines P3 (Muk or Pawniard never Active) and "Pawniard takes two
  turns to get [DD]" together.
- **Against it:** Ilima would keep a Regigigas wall (full 150 HP back on the Bench). With Pawniard lost the deck loses its only Kingambit
  route this game (Kingambit in hand, no other Pawniard on the board), so the wall is worth much less than what it costs.
- **Verdict: upheld.** Property for the tests: no `Play:Ilima` this turn. `_count` can only see it if the fall of the damaged Regigigas is
  priced as fodder (count 1) and the Pawniard's fall is not.

## 203719 t07: Rare Candy to Kingambit, Ilima, promote Glimmora, Venomous Hit (km3: promote Kingambit, Blade)

- **Board:** count 0. His Active is a 10-HP Regigigas. Hand: Rare Candy, Kingambit, Ilima, Glimmet. Opponent: Active Drampa B4 124 (100 HP,
  Lightning attached; Power Blast 70 once it has [CC]), Mega Rayquaza ex benched (Fire + Lightning: Mega Burst 100), Dragonair, a second Drampa.
- **What km3 does (12 of 12):** the same Candy and Ilima, but it promotes the new Kingambit and uses Overlord's Blade.
- **Reading:** at count 0 the Blade is 60, and the Drampa has 100 HP, so there is no knockout and no point. Kingambit at 140 HP then stands
  in front of Power Blast 70 and a benched Mega Burst for nothing. His line puts the 90-HP Glimmora in front (Venomous Hit 30 and Poison,
  Shattering Crystal on the way out), keeps Kingambit out of reach with its Blade not yet worth swinging, and gives Glimmora the turn his plan
  wants (P2). The Regigigas he benches comes back at 150 HP.
- **Against it:** a Blade swing now would at least make the opponent respond to a 140-HP Active. At count 0 it does 60 and a
  poisoned Drampa is 100 - 30 - 10, so his line's damage is not smaller by much.
- **Verdict: upheld.** Property: no Blade attack this turn (and Glimmora promoted). This is a count-0 turn: `_blade` cannot change it, so it is
  the case that separates `_blade` (kmb3: no change) from `_count` (kmbc3: predicted to change).

## 210823 t08: Ilima, promote Glimmora, bench Glimmet, Venomous Hit (km3: promote Kingambit, Blade)

- **Board:** count 0. His Active is a 50-HP Regigigas. Kingambit is on the Bench with one [D]. The opponent's Active is Mega Pidgeot ex (210 HP,
  [D][D][C]: Giant Twister 100 is ready), under their Soothing Shore.
- **What km3 does (12 of 12):** Ilima, promote Kingambit, bench the Regigigas, attach to Kingambit (now [DD]), Blade 60.
- **Reading:** the Blade is 60 against 210 HP at count 0. Giant Twister flips 3 coins and discards a random Energy from my Active per
  heads, so a Kingambit that has just been loaded with [DD] can lose up to both Energy to the reply (1.5 on average) and may not have the Blade
  ready for the following turn. His Glimmora costs one [D] to use, is the next Pokémon that wants its turn, and Shattering Crystal
  takes the point away on heads.
- **Against it:** Soothing Shore heals only Pokémon with [W] attached, so it is no reason either way here.
- **Verdict: upheld.** Property: no Blade attack this turn (Glimmora promoted). Same role as 203719 t07.

## 010706 t11: Heavy Helmet and the Energy on the benched Kingambit, no attack (km3: both on the Active Muk, no attack)

- **Board:** 1-0 for him, count 1. Active: Alolan Muk (110 HP, one [C]). Bench: Kingambit (no Energy), Regigigas [DDD] (ready, but benched).
  The opponent's Active is Indeedee ex (130 HP, no Energy), with a 40-HP Mega Diancie ex on the Bench ([P]×4, Giant Cape) under Peculiar
  Plaza (their [P] Pokémon retreat for 2 less, so Indeedee retreats for free).
- **Nobody attacks this turn** in either line (Muk's Sludge Bomb needs [DCC]; Muk can't retreat on one Energy).
- **Reading:** Peculiar Plaza lets Indeedee step back for nothing, so the opponent's reply is Mega Diancie in front: Brilliant Storm is
  40 + 20 per [P] on all their Pokémon, so 120 with four and 140 with the turn's fifth. Muk has 110 HP. Heavy Helmet's -20 (Retreat 3 or
  more, which both Muk and Kingambit have) makes it 100 or 120, so **the Helmet does not save the Muk**, and km3's Energy on the Muk goes
  with it. His line spends both on the Kingambit he will promote next turn (Helmet on, one [D] on, the second [D] next turn). The Muk's
  fall is a point for them (1-1) and raises his count to 2.
- **Against it:** it assumes they reply with the Diancie; if they don't, the Helmet on the Active Muk would have counted for something. Their
  Indeedee ex Psychic does 30 more per Energy on my Active, so Energy on the Active is also the wrong place against the other reply.
- **Verdict: upheld.** Property: Heavy Helmet on the Kingambit (@1). Both readers must check the Peculiar Plaza claim against the frame, not
  the record, which has the Stadium as the opponent's (owner 1).

## 010837 t05: Muk, Glimmet, Energy on the benched Pawniard (km3: Glimmet, Muk, Energy on the Active Regigigas)

- **Board:** count 1, 0-0. Active: Regigigas 150 (no Energy), Pawniard and Alolan Grimer on the Bench. Hand: Kingambit, Glimmet, Alolan Muk.
  The opponent's Active is Mega Kangaskhan ex (180 HP, [L][M][M]: Double-Punching Family, 80 then 40).
- **Reading:** the Energy on Regigigas is a first of three [C] it needs for Giga Turbo, which it cannot get to before the Kangaskhan's
  120 a turn has finished it (two turns). His Energy on the Pawniard is the first [D] of the two Kingambit needs, and Rare Candy follows at t07
  (he plays it there, with one [D] already on the Kingambit). The order Muk-then-Glimmet is a tie either way.
- **Against it:** Regigigas as a wall takes 120 and survives, and the Energy on it would make Giga Turbo reachable in two more turns; his plan
  never gets there. It is the weakest of the seven: the board does not show the opponent's reply.
- **Verdict: upheld, low-medium confidence.** Property: the turn's Energy goes to the benched Pawniard (@1).

## 014423 t03: Energy on the benched Pawniard (km3: on the Active Alolan Grimer in 8 of 12, once on the Pawniard)

- **Board:** count 0. Active: Alolan Grimer 70 HP, no Energy. Bench: Pawniard, Regigigas 150. The opponent has Dedenne ex ([L]) in front with
  three Tools in play (Electrical Cord, Rocky Helmet, Small Balloon). Dede-Circuit is 40 per Tool on all their Pokémon, so 120, and
  their next Energy is [L] (the Dedenne then has [LL]).
- **Reading:** the Grimer falls next turn on any reading, so Energy on it is lost. That is the `_expo` pattern ("the turn's Energy goes on
  a doomed Active"), not a Blade-pricing one. It is also the position where km3's forecast (printed 40 for Dede-Circuit, see
  `DESIGN_NOTE_CASES.md` E) is wrong, so `_blade`/`_count` have nothing to read here.
- **Verdict: upheld, high confidence.** Property: the Energy goes on the benched Pawniard (@1). **Expect no change from kmb3, kmbc3 or kmbd3**;
  the case belongs to a later `_expo`. Do not count a kmbc3 failure here against kmbc3.

## 203719 t11: Heavy Helmet on the benched Kingambit, Energy on Glimmora (km3: Energy on Kingambit, Helmet on the 10-HP Regigigas)

- **Board:** count 0. Active: Regigigas 10 HP, no Energy. Bench: Muk [D], Glimmora [D], Kingambit [D]. Hand: Glimmet, Glimmora, Heavy Helmet.
  The opponent's Active is the 90-HP Drampa B4 124 (Poisoned, [L], Power Blast 70 for [CC]; the next Energy is [L]).
- **Reading:** Power Blast 70 minus the Helmet's 20 is 50, still far over 10 HP, so km3's Helmet on the Regigigas protects nothing. It goes on
  the Kingambit, whose Retreat Cost 3 makes the Helmet work once it is in front. The Regigigas is fodder: its fall raises the count to 1, and a
  Blade at count 1 is exactly 100, the second Drampa's HP (that is what 203719 t17 turns on). The Energy: Glimmora already has the one [D]
  Venomous Hit needs, so the second is not for attacking. It may pay a retreat (Cost 2), so the reason for @1 over @3 is not certain.
  km3's [DD] on the Kingambit powers a Blade that is 60 at count 0.
- **Against it:** the Energy placement is the unclear half; if the reason is retreat money, a second reader may rate the two Energy choices
  as a tie and the Helmet as the whole difference.
- **Verdict: upheld, medium-high confidence** on the Helmet; the Energy half is unclear. Property: Heavy Helmet on the Kingambit (@3).

## What I could not settle

- Opponent hands are unknown in all seven; none of the verdicts uses a hidden card.
- 010706 t11 rests on the Stadium's owner in the record and on Peculiar Plaza's text (both checked above); 010837 t05 rests on his later
  play at t07.
- Nothing here is a ruling by him. Where he has said why (010837 t03, 203719 t17), those two are not in this file.
