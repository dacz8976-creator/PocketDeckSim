from v2_helpers import P, B
D = 'v2deck_589bb9927a'; G = '20261023_213639000_SR'
SQ = 'Squirtle P-A 033'; OR = 'Oricorio A3 066'; EI = 'Eiscue B1 080'; WT = 'Wartortle B1a 018'; MB = 'Mega Blastoise ex B1a 020'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; LI = 'Lillie A3 155'; CC = 'Copycat B1 225'; LP = 'Lucky Ice Pop B2 145'
SS = 'Soothing Shore B4 154'
RI = 'Riolu A2 091'; SF = 'Skull Fossil A2 144'; RA = 'Rampardos A2 089'; SAB = 'Sabrina A1 225'; RC = 'Rare Candy A3 144'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
RIOLU_AMB = 'Opponent Riolu printing chosen by HP (60) only (its attack was not shown); A2 091, B3 079 and B3 169 match'
SHORE = {"card": SS, "owner": 0}
TR5 = ['Opponent Sabrina printing in the discard not shown; A1 225 used (A1 272, A4b 338 and A4b 339 also match)']
TR7 = TR5 + ['Opponent Rare Candy printing in the discard not shown; A3 144 used (A4b 314, A4b 315 and A4b 379 also match)']
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[CC, WT, PR, LI, PB], disc=[], dene='', board=[B(EI, 80)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(RI, 60)], ko=0),
  ['Play:Poké Ball', 'Place:Oricorio@1', "Play:Professor's Research", 'Place:Eiscue@2', 'EndTurn'],
  D, None, approx=AP + "; the opponent's hand (4) is the opening five less the Active Riolu (going second, no draw yet)",
  ambiguous=[RIOLU_AMB],
  draws={0: [OR], 2: [SS, EI]},
  notes="Global 1 = his 1st turn (he went first). Setup line (25-45): opening five Copycat, Wartortle, Eiscue, Professor's Research, "
        "Lillie; regular Eiscue Active, no Bench -> hand of 4. Global 1 line: draws Poke Ball -> 5. Move in the review's order: Poke Ball "
        "(finds Oricorio), bench Oricorio, Professor's Research (draws Soothing Shore and the 2nd Eiscue), bench the 2nd Eiscue; no "
        "attachment (first turn going first), no attack. Opponent: Riolu 60 Active, no Bench, 5 - 1 = 4 in hand. Bench slots: Oricorio "
        "@1 then Eiscue @2, the order benched (lowest empty slot)."),
P(G, 3, 2, [0, 0],
  dict(hand=[CC, WT, LI, SS, MB], disc=[PB, PR], dene='', board=[B(EI, 80), B(OR, 70), B(EI, 80)], ko=0),
  dict(hand_count=3, disc=[], dene='', board=[B(RI, 60, 'F'), B(SF, 40), B(SF, 40)], ko=0),
  ['Play:Soothing Shore', 'Play:Copycat', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None, approx=AP + "; Bench order (Oricorio, then Eiscue) is the order benched, the review does not give the arrangement",
  ambiguous=[RIOLU_AMB],
  draws={1: ['-' + WT, '-' + LI, '-' + MB, MB, LI, PR]},
  notes="Global 3 = his 2nd turn. Hand after global 1: Copycat, Wartortle, Lillie, Soothing Shore (Professor's Research and Poke Ball "
        "played; Oricorio and Eiscue benched); global 3 line: draws Mega Blastoise ex -> 5. Opponent global 2: Fighting to Riolu, two Skull "
        "Fossils benched; hand 4 + draw 1 - 2 fossils = 3 (and his Copycat redraw shows exactly 3 cards: Mega Blastoise ex, Lillie, "
        "Professor's Research). Move: Soothing Shore (~98-100), Copycat (~103-106; hand Wartortle, Lillie, Mega Blastoise ex shuffled "
        "away, 3 drawn), Water to Active regular Eiscue (~112), no attack."),
P(G, 5, 3, [0, 0],
  dict(hand=[MB, LI, PR, WT], disc=[PB, PR, CC], dene='', board=[B(EI, 80), B(OR, 70), B(EI, 80, 'W')], ko=0),
  dict(hand_count=3, disc=[SAB], dene='', board=[B(RI, 60, 'FF'), B(SF, 40), B(SF, 40)], ko=0),
  ["Play:Professor's Research", 'Attach:1Water@0 zone', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + "; the opponent's Sabrina printing is not shown (first listed printing used); his Bench order assumes the "
            "switched-out Eiscue took the Bench spot the new Active left",
  ambiguous=[RIOLU_AMB] + TR5,
  draws={0: [WT, LP]},
  notes="Global 5 = his 3rd turn. Hand after global 3: Mega Blastoise ex, Lillie, Professor's Research (the Copycat redraw, kept); "
        "draws Wartortle -> 4. Global 4: opponent attaches 2nd Fighting to Riolu, plays Sabrina; he chose the alternate Eiscue (empty) "
        "as Active, the regular Eiscue with one Water to the Bench. Opponent hand 3 + draw 1 - Sabrina = 3. Move (global 5 line): "
        "Professor's Research ~149 (draws the 2nd Wartortle and Lucky Ice Pop), Water to Active alternate Eiscue ~154, no attack."),
P(G, 7, 4, [0, 1],
  dict(hand=[MB, LI, WT, WT, LP, SQ], disc=[PB, PR, CC, PR, EI], dene='W', board=[B(EI, 80, 'W'), B(OR, 70)], ko=1),
  dict(hand_count=2, disc=[SAB, RC], dene='F', board=[B(RA, 100, 'F', behind=[SF]), B(SF, 40), B(RI, 60, 'F')], ko=0),
  ['Place:Squirtle@2', 'Attach:1Water@2 zone', 'EndTurn'],
  D, None, stadium=SHORE,
  approx=AP + "; the opponent's Sabrina and Rare Candy printings are not shown (first listed printings used); the opponent's Bench "
            "order (Skull Fossil, Riolu) follows the review's final-battlefield line",
  ambiguous=[RIOLU_AMB] + TR7,
  notes="Global 7 = his 4th turn. Hand after global 5: Mega Blastoise ex, Lillie, two Wartortle, Lucky Ice Pop; draws Squirtle -> 6. "
        "Global 6: Rare Candy evolves the right-hand Skull Fossil to Rampardos 150, Fighting to Rampardos, Riolu retreats (one of its "
        "two Fighting discarded), Rampardos promoted, Head Smash 130-40 = 90 KOs the alternate Eiscue (its one Water discarded), recoil "
        "50 -> Rampardos 100; opponent 1 point; regular Eiscue 80 with one Water promoted, Oricorio 70 on the Bench. Opponent hand 3 + "
        "draw 1 - Rare Candy - Rampardos = 2. Move: bench Squirtle ~194 (lowest empty slot @2), Water to Squirtle ~208, no attack."),
]
