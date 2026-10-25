from v2_helpers import P, B
D = 'v2deck_589bb9927a'; G = '20261023_220413000_SR'
SQ = 'Squirtle P-A 033'; OR = 'Oricorio A3 066'; EI = 'Eiscue B1 080'; WT = 'Wartortle B1a 018'; MB = 'Mega Blastoise ex B1a 020'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; LI = 'Lillie A3 155'; CC = 'Copycat B1 225'; LP = 'Lucky Ice Pop B2 145'
SS = 'Soothing Shore B4 154'; CY = 'Cyrus A2 150'; PL = 'Parasol Lady B3 152'
CP = 'Chien-Pao ex B2a 037'; CV = 'Carvanha B4 034'
OPB = 'Poké Ball A2b 111'; OPR = "Professor's Research A4b 373"; OCC = 'Copycat B1 225'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
TR3 = ["Opponent Professor's Research printing in the discard not shown; A4b 373 used (P-A 007 also matches)"]
TR5 = ["Opponent Trainer printings in the discard not shown: Professor's Research A4b 373 used (P-A 007 also matches), Copycat "
       "B1 225 used (B1 270 also matches), Poké Ball A2b 111 used (P-A 005 also matches)"]
AMB_CP = 'Opponent Chien-Pao ex printing chosen by HP (130) and attack title (Icicle); B2a 037, B2a 102, B2a 112 and P-B 041 match'
AMB_CV = 'Opponent Carvanha printing chosen by HP (50) only (its attack was not shown); B4 034 and P-B 081 match'
POS = [
P(G, 3, 2, [0, 0],
  dict(hand=[SQ, LI, PL, WT], disc=[PB], dene='', board=[B(OR, 70), B(SQ, 60), B(EI, 80)], ko=0),
  dict(hand_count=6, disc=[OPR], dene='', board=[B(CP, 130, 'W')], ko=0),
  ['Evolve:Wartortle@1', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Professor's Research printing is not shown (first listed printing used)",
  ambiguous=[AMB_CP] + TR3,
  notes="Global 3 = his 2nd turn (he went first). Setup row: opening Oricorio, two Squirtle, Lillie, Poke Ball; Oricorio Active, one "
        "Squirtle benched -> hand Squirtle, Lillie, Poke Ball. Global 1 row: draws Parasol Lady, Poke Ball finds Eiscue, Eiscue benched "
        "-> hand Squirtle, Lillie, Parasol Lady. Global 3 row: draws Wartortle -> 4. Bench order: Squirtle (setup) @1, Eiscue @2. "
        "Opponent: Chien-Pao ex 130 Active, empty Bench; global 2 Water to it, Professor's Research; hand 5 - 1 = 4, draw 5, Research "
        "(-1 +2) = 6; Icicle prevented by Safeguard (Oricorio 70). Move (global 3 row): evolve the benched Squirtle to Wartortle, Water "
        "to it, no attack."),
P(G, 5, 3, [0, 0],
  dict(hand=[SQ, LI, PL, PR], disc=[PB], dene='', board=[B(OR, 70), B(WT, 90, 'W', behind=[SQ]), B(EI, 80)], ko=0),
  dict(hand_count=1, disc=[OPR, OCC, OPB], dene='', board=[B(CP, 130, 'WW'), B(CV, 50), B(CV, 50)], ko=0),
  ["Play:Professor's Research", 'Attach:1Water@1 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand (1) counts its global-4 Copycat as drawing 3 (his hand then held 3) and its Poke Ball as +1, "
            "then both Carvanha benched; the opponent's Trainer printings (Professor's Research, Copycat, Poke Ball) are not shown, the "
            "first listed are used",
  ambiguous=[AMB_CP, AMB_CV] + TR5,
  draws={0: [EI, CC]},
  notes="Global 5 = his 3rd turn. Hand after global 3: Squirtle, Lillie, Parasol Lady; global 5 row: draws Professor's Research -> 4. "
        "Global 4 row: 2nd Water on Chien-Pao, Copycat, Poke Ball, two Carvanha 50 benched, Icicle prevented. Opponent hand 6 + 1 = 7, "
        "Copycat -> 3 (his hand held 3), Poke Ball (-1 +1) 3, two Carvanha -> 1. Move (global 5 row, in order): Professor's Research "
        "(draws Eiscue and Copycat; neither played), Water to Wartortle ~117, no attack."),
]
