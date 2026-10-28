# Score: ScreenRecording_10-25-2026 21-28-49_1 (Draft A: Shark Tempo, Dustin went second, won by concession 2-2, 16 global turns)

G = Gemini review (`gemini/REVIEW.md`). X = Codex review (`codex/REVIEW.md`, amended by `codex/independent_check_eight/VERIFICATION.json` and `LEAD_ACCEPTANCE.json`; neither adds a correction).
Frames opened: 39 of the 120 allowed. All frame numbers below are seconds (`frames/t_SSSS.jpg`).

## Facts the two reviews agree on, and the frames did not contradict
Opponent went first; Dustin's opening hand (Mega Sharpedo ex, Lucky Ice Pop, Alolan Ninetales ex, Alolan Vulpix, Irida; frame 24); Energy Zones (opponent Lightning, Dustin Water; frames 24, 186); all 16 turns' cards played other than the items below; every attack and damage number (Gnaw 20, Binding Snow 80 x2, Sharp Fang 30, Zzzap 50/70, Turbo Shark 0 into Safeguard, Lightning Claw 70, Surf 70, Ultimate Force 130 -- frame 511 shows 130 on Lapras); every KO and point (1-0, 1-1, 2-1, 2-2); concession ended the game at 2-2 (banner at frame 543); result screen: went second, 16 turns, 2-2, 280 damage, Card of the Game Alolan Ninetales ex (frames 552, 553). G alone adds rank 972 -> 977, +1 pt, +4 win streak pts, 2 win streak; frame 555 shows 977 pts, 1 gained, 4 win streak pts, 2 win streak, so that claim is right.

## Disagreement table

| Turn | Item | G says | X says | Frames | Verdict |
|---|---|---|---|---|---|
| 5 (opp) | Elemental Switch (card name agrees) | moves 1 Lightning from Benched **Pichu** to Active Oricorio (Pichu 0, Zeraora 2, Oricorio 2) | moves it from Benched **Zeraora** (Zeraora 1, Oricorio 2, Pichu keeps its Energy) | 186: Pichu 1 icon, Zeraora 2, Oricorio 1. 188: Elemental Switch card. 190/194: Pichu has no icon, Zeraora still 2 icons, Oricorio 2. Zeraora shows 3 icons at 278, so it was never at 1 | **G right** (X's later "Zeraora two after T7" follows from this error) |
| 8 (Dustin) | Misty's chosen Pokémon (flip is tails, nothing attached, so the outcome does not show it) | Benched Alolan Ninetales ex (cites t=270) | Mega Sharpedo ex | 268/269: Sharpedo is the only Pokémon lit while Misty is held in hand; 270: the Misty card passes over the Ninetales slot as the play animation; 271-272: popup, no selection screen; 273-277: coin flip. No frame shows the choice being made | **unsettled** (weakly leans X; G's cited frame is the card animation) |
| 9 (opp) | Energy from the Energy Zone this turn | Lightning to Benched **Pichu** (t=304) | Lightning to Benched **Zeraora**, bringing it to 3 (the Gemini cheap sheet says no attach) | 302: Pichu has no icon (banner). 304, 306, 310: Pichu now has 1 Lightning icon; Zeraora has 3 icons, the same 3 it has at 278 | **G right** |
| 12 (Dustin) | Retreating Mega Sharpedo ex | discards 1 Water | free retreat, Water stays on it | 385: Sharpedo Active with 1 Water. 388: choose switch-in. 393: Sharpedo on the Bench still shows its Water icon. 534, 537, 543: Sharpedo (120 HP, Cape) Active with 1 Water icon. Ninetales/Sharpedo card shows an empty retreat cost | **X right** (G's later "Sharpedo 0 Energy" board lines at T12-T16 follow from this) |
| 15 (opp) | Professor's Research | played (t=474), draws 2 | not mentioned | 474: Professor's Research popup on the opponent side; 476: opponent hand has grown, Pichu Active | **G right** (X omits a card played) |
| 16 (Dustin) | Water Energy attach before the concession | none; concession comes before the turn's Water is attached | attaches Water to the new Alolan Ninetales ex | 534, 537, 542, 543, 545: the new Ninetales (left Bench, 150 HP) shows no Energy icon and the Water orb is still unused in Dustin's Energy Zone; concession banner at 543 | **G right** |

Timestamp-only differences of 3 s or less were ignored (for example concession 543 in G against 545 in X: the banner is already up at 543, so within tolerance).

## Errors per review

### G (Gemini): 1 major, 0 minor
1. **Major, T12:** says the retreat of Mega Sharpedo ex discarded 1 Water; it was a free retreat and the Water stayed (frames 385, 393, 534, 543). The board-state lines that give Sharpedo 0 Energy at T12-T16 (and the final board) repeat this one error and are not counted again.
2. Not graded: the Misty target (unsettled).

### X (Codex): 4 major, 0 minor
1. **Major, T5:** Elemental Switch moved the Energy from Zeraora; it came from Pichu (frames 186, 190, 194). The statement "Pichu's Energy remains" and the T7 "Zeraora now two" are the same error and are not counted again.
2. **Major, T9:** puts the Lightning on Zeraora (making 3); it went to Pichu (frames 302, 304, 310; Zeraora is 3 before and after).
3. **Major, T15:** omits the opponent's Professor's Research (frame 474).
4. **Major, T16:** says Dustin attached Water to the new Alolan Ninetales ex before the concession; no Energy was attached (frames 534-545).
5. Not graded: the Misty target (unsettled).

## Opponent sheets (12 fields, checked against the frames)
The 12 fields: went_first, global_turns, final_score, end, Energy Zone type(s), set of Pokémon names, attack names, Trainer names, special_conditions, healed, bench_damage, card of the game.

| Field | Truth (frames) | gemini | gemini_cheap | codex |
|---|---|---|---|---|
| went_first | opponent (24; 552 "Went second") | right | right | right |
| global_turns | 16 (552) | right | right | right |
| final_score | 2-2 (552) | right | right | right |
| end | opponent concedes (543, 545) | right | right | right |
| Energy Zone | Lightning (24, 186) | right | right | right |
| Pokémon names | Pichu, Zeraora, Oricorio, Arceus ex (524, 534, 543) | right | right | right |
| attack names | Crackly Toss, Lightning Claw, Zzzap, Ultimate Force (card text in 186, 524, 534) | right | right | right |
| Trainer names | Starting Plains, Professor's Research, Poké Ball, Copycat, Elemental Switch, Small Balloon (474 for Research) | right | right | right as a set of names (the turn-15 Professor's Research entry is missing, but the name is also listed at turn 1) |
| special_conditions | none (Fabled Luster only blocks conditions) | right | right | right |
| healed | false | right | right | right |
| bench_damage | false (Ultimate Force hits only the Active, frame 511) | right | right | right |
| card of the game | Oricorio (553) | right | right | right |
| **Total** | | **12/12** | **12/12** | **12/12** |

Points not in the 12 fields: Small Balloon's name could not be read in the frames (frame 193 is a glow effect) but all three sheets and both reviews agree and nothing contradicts it. The Energy ledgers (not scored): gemini is right (T9 to Pichu, two T5 entries); gemini_cheap lists only one T5 entry and says no attach at T9 (wrong); codex puts the T9 Lightning on Zeraora (wrong).

## Which record to rely on
For this game a player could rely on G more. G's one real error is the Sharpedo retreat cost at T12 (a discarded Water that did not happen), which leaves Sharpedo showing 0 Energy for the rest of the record. X's four errors all concern the Energy ledger and the cards played: the wrong source of the Elemental Switch Energy and the wrong T9 attach target (which leave Zeraora's and Pichu's Energy wrong for the rest of the game), a missing opponent Professor's Research, and an invented Water attach on Dustin's last turn. G is correct on every attack, damage number, KO and point, and X is as well. The two sheets from Gemini and the Codex sheet all score 12/12 on the scored fields; the two reviews differ mainly in which of them keeps the Energy ledger straight, and here G's ledger is closer to the frames. The Misty target stays unsettled for both.
