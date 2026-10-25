from v2_helpers import P, B
D = 'v2deck_589bb9927a'; G = '20261023_011134000_SR'
SQ = 'Squirtle P-A 033'; OR = 'Oricorio A3 066'; EI = 'Eiscue B1 080'; WT = 'Wartortle B1a 018'; MB = 'Mega Blastoise ex B1a 020'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; LI = 'Lillie A3 155'; CC = 'Copycat B1 225'
LIP = 'Lucky Ice Pop B2 145'; PL = 'Parasol Lady B3 152'; SS = 'Soothing Shore B4 154'
IN = 'Indeedee ex B1 121'; MA = 'Mega Audino ex B3 141'; BL = 'Bramblin B3 072'; BG = 'Brambleghast B3 073'
OPB = 'Poké Ball A2b 111'; OPR = "Professor's Research A4b 373"; OSP = 'Starting Plains B2 154'   # the opponent's, by convention 3
XS = SS   # stand-in for the one card of his global-8 hand the review does not identify (see the notes of t6 and t8)
AP = "opponent's list unknown; opponent's hand size from the visible plays"
APT = "the opponent's Trainer printings are not shown, the first printing cards.py lists is used"
AMB_IN = 'Opponent Indeedee ex printing chosen by HP (130), Ability title (Watch Over) and attack title (Psychic); B1 121, B1 260, B1 278 and B3b 104 match'
AMB_MA = 'Opponent Mega Audino ex printing chosen by HP (180) and attack title (Heartfelt Shine); B3 141, B3 189 and B3 202 match'
AMB_BG = 'Opponent Brambleghast printing chosen by HP (90) and Ability title (Accept Pain); B3 073 and B3 167 match'
CCX = ("his global-6 Copycat is read as drawing 4 cards (Wartortle, Mega Blastoise ex, Copycat and one unidentified card), not the 7 "
       "the review lists: the opponent held 4 cards then (visible plays), and his global-8 Copycat drew 6 = the opponent's hand after "
       "its global-7 Professor's Research (+2), so it held 4 on global 6; the review's 7-card list also has no Copycat although he plays "
       "one on global 8 after drawing a Poke Ball, and it would make 3 Poke Balls")
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[LIP, PR, PB, SS, PR], disc=[], dene='', board=[B(SQ, 60)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(IN, 130), B(BL, 60)], ko=0),
  ['Play:Poké Ball', "Play:Professor's Research", 'Place:Eiscue@1', 'Attach:1Water@0 zone', 'Retreat:1', 'EndTurn'],
  D, None,
  approx=AP + "; Indeedee ex printing chosen by HP, Ability and attack titles",
  ambiguous=[AMB_IN],
  draws={0: [EI], 1: [CY, PL]},
  notes="Global 2 = his 1st turn (he went second). REVIEW 'Opening and setup' 0-44s: opening five Squirtle, Lucky Ice Pop, Professor's "
        "Research, Poke Ball, Soothing Shore; Squirtle 60 Active, no Bench -> 4. Global 2 (101-138s): draw Professor's Research -> 5. "
        "Opponent: Indeedee ex 130 Active, Bramblin 60 right Bench (5-2 = 3); global 1 draw (4), nothing played. His move 101-138s: Poke "
        "Ball (Eiscue) -> Professor's Research (Cyrus, Parasol Lady) -> Eiscue benched (@1) -> Water to Active Squirtle -> retreat "
        "Squirtle (the Water paid), Eiscue Active (Retreat:1) -> end turn, no attack."),
P(G, 4, 2, [0, 0],
  dict(hand=[LIP, SS, PR, CY, PL, MB], disc=[PB, PR], dene='W', board=[B(EI, 80), B(SQ, 60)], ko=0),
  dict(hand_count=4, disc=[OPB], dene='', board=[B(IN, 130), B(BL, 60), B(MA, 180, 'P')], ko=0),
  ["Play:Professor's Research", 'Place:Oricorio@2', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + APT + "; the opponent's global-3 Poke Ball is counted as +1 (Mega Audino ex, benched); Indeedee ex and Mega "
              "Audino ex printings chosen by HP, Ability and attack titles",
  ambiguous=[AMB_IN, AMB_MA],
  draws={0: [OR, CC]},
  notes="Global 4 = his 2nd turn. After global 2 his hand is Lucky Ice Pop, Soothing Shore, Research, Cyrus, Parasol Lady; 160-195s draw "
        "Mega Blastoise ex -> 6. Board: Eiscue 80 Active, Squirtle 60 Bench (@1). Discard Poke Ball, Research; 1 Water (retreat). "
        "Opponent global 3 (138-160s): draw (5), Poke Ball (+1, 5), Mega Audino ex 180 benched (4), Psychic to Audino. His move "
        "160-195s: Professor's Research (Oricorio, Copycat) -> Oricorio benched (@2) -> Water to the benched Squirtle (@1) -> end turn, "
        "no attack (inspections are not actions)."),
P(G, 6, 3, [0, 0],
  dict(hand=[LIP, SS, CY, PL, MB, CC, EI], disc=[PB, PR, PR], dene='W', board=[B(EI, 80), B(SQ, 60, 'W'), B(OR, 70)], ko=0),
  dict(hand_count=4, disc=[OPB], dene='', board=[B(IN, 130), B(BG, 90, behind=[BL]), B(MA, 180, 'PP')], ko=0),
  ['Play:Soothing Shore', 'Attach:1Water@1 zone', 'Play:Copycat', 'Evolve:Wartortle@1', 'EndTurn'],
  D, None,
  approx=AP + "; " + APT + "; Indeedee ex, Mega Audino ex and Brambleghast printings chosen by HP, Ability and attack titles; " + CCX +
              "; in the verification variant the unidentified card is a stand-in (Soothing Shore)",
  ambiguous=[AMB_IN, AMB_MA, AMB_BG],
  draws={2: ['-' + LIP, '-' + CY, '-' + PL, '-' + MB, '-' + EI, WT, MB, CC, XS]},
  notes="Global 6 = his 3rd turn. After global 4 his hand is Lucky Ice Pop, Soothing Shore, Cyrus, Parasol Lady, Mega Blastoise ex, "
        "Copycat; 212-247s draw the 2nd Eiscue -> 7. Opponent global 5 (195-212s): draw (5), Bramblin -> Brambleghast 90 (4), 2nd Psychic "
        "to Audino. His move 212-247s: Soothing Shore -> 2nd Water to the benched Squirtle (@1) -> Copycat -> evolve Squirtle -> "
        "Wartortle (@1) -> end turn, no attack. Copycat: the review lists a 7-card fan (Cyrus, Poke Ball, Soothing Shore, Parasol Lady, "
        "Mega Blastoise ex, Eiscue, Wartortle); read as 4 cards, see approx (opponent 4 cards: 5-2 at setup, +3 draws, Poke Ball net 0, "
        "Audino and Brambleghast played; global-8 Copycat drew 6 after the opponent's global-7 Research). Wartortle and Mega Blastoise "
        "ex must be among them (evolved on global 6 and 8), and Copycat (played on global 8; the review's global-8 draw is a Poke Ball)."),
P(G, 8, 4, [0, 0],
  dict(hand=[MB, CC, XS, PB], disc=[PB, PR, PR, CC], dene='W', board=[B(EI, 80), B(WT, 90, 'WW', behind=[SQ]), B(OR, 70)], ko=0),
  dict(hand_count=6, disc=[OPB, OPR], dene='', board=[B(IN, 130), B(BG, 90, behind=[BL]), B(MA, 180, 'PPP')], ko=0),
  ['Evolve:Mega Blastoise ex@1', 'Play:Poké Ball', 'Place:Squirtle@3', 'Play:Copycat', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None,
  stadium={"card": SS, "owner": 0},
  approx=AP + "; " + APT + "; Indeedee ex, Mega Audino ex and Brambleghast printings chosen by HP, Ability and attack titles; " + CCX +
              "; so his hand holds Mega Blastoise ex, Copycat, this turn's Poke Ball and one card the review does not identify, given "
              "here as a Soothing Shore (the candidates are Wartortle, Lillie, Soothing Shore, Lucky Ice Pop, Cyrus, Parasol Lady, Eiscue)",
  ambiguous=[AMB_IN, AMB_MA, AMB_BG,
             'His hand: one card, listed as Soothing Shore B4 154, is not identified by the recording review; it is one of Wartortle, '
             'Lillie, Soothing Shore, Lucky Ice Pop, Cyrus, Parasol Lady or Eiscue'],
  draws={1: [SQ], 3: ['-' + XS, LI, LIP, SS, WT, EI, PL]},
  notes="Global 8 = his 4th turn. Hand: after global 6 Mega Blastoise ex, Copycat and the unidentified card (see t6), 263-300s draw "
        "Poke Ball -> 4 (stand-in Soothing Shore for the unidentified card). Board: Eiscue 80 Active; Bench Wartortle 90 with 2 Water "
        "(@1), Oricorio 70 (@2); his Soothing Shore in play. Discard: Poke Ball, Research x2, Copycat; 1 Water. Opponent global 7 "
        "(247-263s): draw (5), Professor's Research (+2 -> 6), 3rd Psychic to Audino. His move 263-300s: evolve Wartortle -> Mega "
        "Blastoise ex (@1) -> Poke Ball (2nd Squirtle) -> Squirtle benched (@3) -> Copycat (shuffles the unidentified card back; draws 6 = "
        "the opponent's 6: Lillie, Lucky Ice Pop, Soothing Shore, Wartortle, Eiscue, Parasol Lady; Cyrus stays as his last deck card, "
        "drawn on global 10) -> 3rd Water to Mega Blastoise ex -> end turn, no attack."),
P(G, 10, 5, [0, 0],
  dict(hand=[LI, LIP, SS, WT, EI, PL, CY], disc=[PB, PR, PR, CC, PB, CC, SS], dene='W',
       board=[B(EI, 100), B(MB, 230, 'WWW', behind=[WT, SQ]), B(OR, 90), B(SQ, 80)], ko=0),
  dict(hand_count=6, disc=[OPB, OPR], dene='', board=[B(IN, 150, 'P'), B(BG, 90, behind=[BL]), B(MA, 200, 'PPP')], ko=0),
  ['Evolve:Wartortle@3', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None,
  stadium={"card": OSP, "owner": 1},
  approx=AP + "; " + APT + "; Indeedee ex, Mega Audino ex and Brambleghast printings chosen by HP, Ability and attack titles",
  ambiguous=[AMB_IN, AMB_MA, AMB_BG],
  notes="Global 10 = his 5th turn. After global 8 his hand is Lillie, Lucky Ice Pop, Soothing Shore, Wartortle, Eiscue, Parasol Lady; "
        "348-368s draw Cyrus (his last deck card) -> 7. Opponent global 9 (300-348s): draw (7), Starting Plains (6) replacing his Soothing "
        "Shore (to his discard), Psychic to Indeedee. Basics +20: Eiscue 100, Oricorio 90, Squirtle 80, Indeedee 150, Audino 200. His "
        "move 348-368s: evolve the 2nd Squirtle -> Wartortle (@3) -> 4th Water to Mega Blastoise ex (@1) -> end turn, no attack (the "
        "unused-Supporter warning is confirmed)."),
P(G, 14, 7, [0, 0],
  dict(hand=[LI, LIP, SS, EI, PL, CY], disc=[PB, PR, PR, CC, PB, CC, SS], dene='W',
       board=[B(EI, 50), B(MB, 230, 'WWWWW', behind=[WT, SQ]), B(OR, 90), B(WT, 90, behind=[SQ])], ko=0),
  dict(hand_count=7, disc=[OPB, OPR, OPR], dene='P',
       board=[B(MA, 200, 'PPP'), B(BG, 90, behind=[BL]), B(IN, 150, 'P'), B(BG, 90, behind=[BL])], ko=0),
  ['Play:Parasol Lady', 'ReturnPokemonToHand{in_play_idx:0}', 'Promote:0@1', 'Play:Soothing Shore', 'Attach:1Water@0 zone',
   'Attack:Triple Bombardment'],
  D, None,
  stadium={"card": OSP, "owner": 1},
  approx=AP + "; " + APT + "; Indeedee ex, Mega Audino ex and Brambleghast printings chosen by HP, Ability and attack titles; the "
              "opponent's Bench is listed Brambleghast, Indeedee ex (retreated into Audino's slot), Brambleghast (the review does not give "
              "left and right)",
  ambiguous=[AMB_IN, AMB_MA, AMB_BG],
  notes="Global 14 = his 7th turn; his deck is empty, no draw. Hand after global 10: Lillie, Lucky Ice Pop, Soothing Shore, Eiscue, "
        "Parasol Lady, Cyrus (global 12: no draw, 5th Water to Mega Blastoise ex, nothing played). Opponent global 11 (368-415s): draw "
        "(7), Professor's Research (8), 2nd Bramblin benched (7), 2nd Psychic to Indeedee, Psychic on Eiscue for 0 (Ice Face). Global 13 "
        "(425-519s): draw (8), Bramblin -> Brambleghast (7), Indeedee retreats (1 Psychic discarded), Mega Audino ex Active, Heartfelt "
        "Shine 90-40 = 50 on Eiscue (100 -> 50). His move 519-560s: Parasol Lady (Active Eiscue to his hand; Mega Blastoise ex promoted) "
        "-> 2nd Soothing Shore (replaces Starting Plains) -> 6th Water to Mega Blastoise ex -> Triple Bombardment (130 Audino, 50 each "
        "Brambleghast). Labels: Parasol Lady's choice is ReturnPokemonToHand{in_play_idx:0}; pg_legal_v14 stops right after it as a "
        "'hidden draw or coin' (it does so for any ReturnPokemonToHand, Active or Benched, deck empty or not: scratch/b6/"
        "t_parasol_test.py), and check_game's variant then finds no chance step, so the point stays FIX on the tool. 'Promote:0@1' "
        "(promote Mega Blastoise ex from slot 1; review 528-532s 'promotes Mega Blastoise ex') is not engine-checked here, since the tool "
        "stops before it. Verifier (v6): the builder's 'Activate:0@1' was changed to 'Promote:0@1' because the engine's label for HIS OWN "
        "choice of a new Active when his Active spot is emptied during his turn is 'Promote:0@<slot>' (scratch/v6/t_promote_label_g6t14.py: "
        "Eiscue at 20 HP knocked out by replacing Starting Plains, legal ['Promote:0@1', 'Promote:0@2', 'Promote:0@3']); 'Activate:' is "
        "the switch form (Ultra Thrusters, Sabrina). Re-check it once the tool goes past ReturnPokemonToHand. The rest (Soothing Shore, Water to the Active, Triple Bombardment) applies in "
        "scratch/b6/t_after_parasol.py; the two bench targets are three identical 'ApplyDamage' labels there, so they are not written."),
]
