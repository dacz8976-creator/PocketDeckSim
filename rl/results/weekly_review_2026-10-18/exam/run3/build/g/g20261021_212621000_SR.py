from v2_helpers import P, B
D = 'v2deck_4fa967805c'; G = '20261021_212621000_SR'
CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'; WM = 'Wailmer B4 036'; WL = 'Wailord B1 057'; BT = 'Baltoy A3a 030'
CL = 'Claydol A3a 031'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; HH = 'Heavy Helmet B1 219'
CC = 'Copycat B1 225'; EC = 'Elegant Cape B3b 065'; WA = 'Wallace B3b 068'
# opponent (printings by convention 3: the first cards.py lists among those matching what the review shows)
AB = 'Absol A4 120'; DE = 'Deino B1 155'; MA = 'Mega Absol ex B1 151'; NI = 'Nihilego A3a 042'; BARB = 'Poison Barb A3 146'
oPB = 'Poké Ball A2b 111'; oPR = "Professor's Research A4b 373"; oCC = 'Copycat B1 225'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
TR = ("the opponent's Trainer printings are not shown; the first-listed printings are used (Poké Ball A2b 111, Professor's Research "
      "A4b 373, Copycat B1 225, Poison Barb A3 146)")
AM_AB = 'Opponent Absol printing chosen by HP (80) and attack title (Leap Over); A4 120 and P-A 117 match'
AM_DE = 'Opponent Deino printing: B1 155 is the only Deino listed'
AM_MA = 'Opponent Mega Absol ex printing chosen by HP (170) and attack title (Darkness Claw); B1 151, B1 262, B1 280, B3 230 and P-B 009 match'
AM_NI = 'Opponent Nihilego printing chosen by HP (70) and Ability title (More Poison); A3a 042, A3a 103, A4b 246 and A4b 247 match'
AM_TR = ("Opponent's Trainers: printings not shown; Poké Ball A2b 111, Professor's Research A4b 373, Copycat B1 225 and Poison Barb "
         "A3 146 listed")
# verifier (Oct 25): the opponent's first Copycat is on global 4 and its Poké Ball on global 8, so t3 and t5 name only the Trainers seen by then
TR3 = ("the opponent's Trainer printings are not shown; the first-listed printings are used (Professor's Research A4b 373, Poison Barb "
       "A3 146)")
AM_TR3 = "Opponent's Trainers: printings not shown; Professor's Research A4b 373 and Poison Barb A3 146 listed"
TR5 = ("the opponent's Trainer printings are not shown; the first-listed printings are used (Professor's Research A4b 373, Copycat "
       "B1 225, Poison Barb A3 146)")
AM_TR5 = "Opponent's Trainers: printings not shown; Professor's Research A4b 373, Copycat B1 225 and Poison Barb A3 146 listed"
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[PR, CC, PB, EC, MS], disc=[], dene='', board=[B(WM, 100)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(AB, 80)], ko=0),
  ['Play:Poké Ball', 'Place:Carvanha@1', 'Play:Elegant Cape', 'Tool:Elegant Cape@0', 'Play:Copycat', 'Place:Wailmer@2', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand count (4) is the opening five less the Active Absol (no Bench at setup, no draw yet)",
  ambiguous=[AM_AB],
  draws={0: [CV], 4: ['-' + PR, '-' + MS, MS, WL, WM, CL]},
  notes="Global 1 = his 1st turn (he went first). Review table 'QR, queue, setup' 0-56: opening five Professor's Research, Copycat, "
        "Wailmer, Poke Ball, Elegant Cape (native 35s); Wailmer Active, no Bench -> 4 in hand. Row '1, owner own 1' 57-94: draws Mega "
        "Sharpedo ex -> 5. Opponent: Absol Active, no Bench, 5-1 = 4 cards. His move in the review's order: Poke Ball (finds Carvanha), "
        "bench Carvanha (slot 1), Elegant Cape on Active Wailmer, Copycat (his remaining hand Research and Sharpedo shuffled in; draws "
        "4 = opponent's 4: Mega Sharpedo ex, Wailord, Wailmer, Claydol), bench the 2nd Wailmer (slot 2). No Energy (first turn), no "
        "attack."),
P(G, 3, 2, [0, 0],
  dict(hand=[MS, WL, CL, EC], disc=[PB, CC], dene='', board=[B(WM, 100, tool=EC), B(CV, 50), B(WM, 100)], ko=0),
  dict(hand_count=3, disc=[oPR], dene='', board=[B(AB, 80), B(DE, 60, 'D', tool=BARB), B(DE, 60)], ko=0),
  ['Evolve:Mega Sharpedo ex@1', 'Evolve:Wailord@0', 'Play:Elegant Cape', 'Tool:Elegant Cape@1', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + TR3,
  ambiguous=[AM_AB, AM_DE, AM_TR3],
  notes="Global 3 = his 2nd turn. His hand after global 1: Mega Sharpedo ex, Wailord, Claydol (Copycat's four less the benched "
        "Wailmer); row '3, owner own 2' 121-144: draws Elegant Cape -> 4. Discard Poke Ball, Copycat. Board: Active Wailmer 100 with "
        "Cape, Bench Carvanha 50 (slot 1), Wailmer 100 (slot 2). Opponent row '2' 95-120: draw (4->5), Professor's Research (6), two "
        "Deino benched (4), Poison Barb on the left Deino (3), Darkness on that Deino; Absol no Energy, no attack. Bench listed left "
        "to right: Barb Deino, Deino. His move in the review's order: Carvanha -> Mega Sharpedo ex, Active Wailmer -> Wailord (230 "
        "with Cape), 2nd Cape on Sharpedo (220), Water to Sharpedo; no attack (native 141/153s)."),
P(G, 5, 3, [0, 0],
  dict(hand=[CL, PR], disc=[PB, CC], dene='', board=[B(WL, 230, tool=EC, behind=[WM]), B(MS, 190, 'W', tool=EC, behind=[CV]), B(WM, 100)],
       ko=0),
  dict(hand_count=1, disc=[oPR, oCC], dene='', board=[B(AB, 80, 'D'), B(DE, 60, 'D', tool=BARB), B(DE, 60)], ko=0),
  ["Play:Professor's Research", 'Play:Heavy Helmet', 'Tool:Heavy Helmet@2', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + TR5 + "; the opponent's Copycat on global 4 drew 1 card, his hand size then (Claydol)",
  ambiguous=[AM_AB, AM_DE, AM_TR5],
  draws={0: [MS, HH]},
  notes="Global 5 = his 3rd turn. His hand after global 3: Claydol (Sharpedo, Wailord, Cape played); row '5' 175-192: draws "
        "Professor's Research -> 2. Opponent row '4' 145-174: draw (3->4), Copycat (native 154.4s; 3 shuffled, draws his 1-card hand "
        "count -> 1), Darkness to Absol, Leap Over 30 to the Benched Sharpedo 220->190. His move in the review's order: Research "
        "(2nd Mega Sharpedo ex, Heavy Helmet), Helmet on the Benched Wailmer (slot 2), Water to Active Wailord (its first); no attack."),
P(G, 11, 6, [0, 0],
  dict(hand=[CL, MS, BT, CV, CY, PB], disc=[PB, CC, PR, PR], dene='',
       board=[B(WL, 230, 'WWW', tool=EC, behind=[WM]), B(MS, 100, 'W', tool=EC, behind=[CV]), B(WM, 100, tool=HH)], ko=0),
  dict(hand_count=2, disc=[oPR, oCC, oCC, oPB], dene='',
       board=[B(AB, 80, 'D', tool=BARB), B(DE, 60, 'DDD', tool=BARB), B(DE, 60), B(MA, 170, 'D')], ko=0),
  ['Play:Poké Ball', 'Place:Baltoy@3', 'Attach:1Water@0 zone', 'Attack:Whale Pump'],
  D, None,
  approx=AP + "; " + TR + "; the opponent's global-8 Poké Ball is counted as finding a card (the review: a concealed card enters "
            "the hand); the opponent's Copycat on global 6 drew 2 cards, his hand size then (Claydol, Mega Sharpedo ex)",
  ambiguous=[AM_AB, AM_DE, AM_MA, AM_TR],
  draws={0: []},
  notes="Global 11 = his 6th turn. His hand: after global 5 Claydol, Mega Sharpedo ex; global 7 draws and plays the 2nd Research "
        "(Baltoy, Carvanha); global 9 draws Cyrus; row '11' 290-322 draws Poke Ball -> Claydol, Sharpedo, Baltoy, Carvanha, Cyrus, "
        "Poke Ball (6; matches the 4-card hand revealed on global 14 after Baltoy and Poke Ball left it). Discard Poke Ball, Copycat, "
        "Research x2. Board: Wailord 230 with Cape and three Water (globals 5, 7, 9), Sharpedo 100 (four Leap Overs) with Cape and one "
        "Water, Wailmer 100 with Helmet. Opponent hand: 1 after global 4; global 6 draw 2, Copycat (1 shuffled, draws 2), bench Mega "
        "Absol ex (1), Darkness to it; global 8 draw 2, Poke Ball (2), 2nd Darkness to the left Deino; global 10 draw 3, Poison Barb "
        "to Absol (2), 3rd Darkness to the left Deino. Bench left to right: Barb Deino DDD, Deino, Mega Absol ex D. His move in the "
        "review's order: Poke Ball (no Basic left in the deck: no target message), bench Baltoy (slot 3), 4th Water to Wailord, Whale "
        "Pump 100 KOs Absol (306-308s)."),
P(G, 13, 7, [1, 0],
  dict(hand=[CL, MS, CV, CY, WL], disc=[PB, CC, PR, PR, PB], dene='',
       board=[B(WL, 180, 'WWWW', tool=EC, cond=['Poisoned'], behind=[WM]), B(MS, 100, 'W', tool=EC, behind=[CV]), B(WM, 100, tool=HH),
              B(BT, 60)], ko=0),
  dict(hand_count=2, disc=[oPR, oCC, oCC, oPB, AB, BARB], dene='D',
       board=[B(DE, 60, 'DDD', tool=BARB), B(DE, 60, 'D'), B(MA, 170, 'D'), B(NI, 70)], ko=1),
  ['Evolve:Wailord@2', 'Attach:1Water@2 zone', 'Attack:Whale Pump'],
  D, None,
  approx=AP + "; " + TR + "; the opponent's Bench is listed Deino, Mega Absol ex, then Nihilego (benched last); the review does "
            "not give the spots after the promotion",
  ambiguous=[AM_AB, AM_DE, AM_MA, AM_NI, AM_TR],
  notes="Global 13 = his 7th turn. His hand after global 11: Claydol, Sharpedo, Carvanha, Cyrus; row '13' 342-371 draws the 2nd "
        "Wailord -> 5. Board: Wailord 230 - poison 10 (end of global 11) - Headbutt 20 - poison 20 (Nihilego) = 180, four Water, Cape, "
        "Poisoned (Absol's Barb); Sharpedo 100; Helmet Wailmer 100; Baltoy 60 (slot 3). Score 1-0 (Absol KO). Opponent: Barb Deino "
        "DDD promoted; row '12' 323-341: draw (2->3), Nihilego benched (2), Darkness to the other Deino, Headbutt 20. Opponent discard "
        "gains Absol, its Barb and its Darkness. His move in the review's order: Helmet Wailmer -> Wailord (slot 2), Water to it, "
        "Active Wailord's Whale Pump 100 KOs Deino."),
P(G, 15, 8, [2, 0],
  dict(hand=[CL, MS, CV, WA], disc=[PB, CC, PR, PR, PB, CY], dene='',
       board=[B(WL, 60, 'WWWW', tool=EC, cond=['Poisoned'], behind=[WM]), B(MS, 100, 'W', tool=EC, behind=[CV]),
              B(WL, 200, 'W', tool=HH, behind=[WM]), B(BT, 60)], ko=0),
  dict(hand_count=3, disc=[oPR, oCC, oCC, oPB, AB, BARB, DE, BARB], dene='DDDD',
       board=[B(MA, 170, 'DD'), B(DE, 60, 'D'), B(NI, 70)], ko=2),
  ['Evolve:Claydol@3', 'Attach:1Water@2 zone', 'Attack:Whale Pump'],
  D, None,
  approx=AP + "; " + TR + "; the opponent's discarded Energy counts the Darkness on the knocked-out Absol (1) and Deino (3)",
  ambiguous=[AM_AB, AM_DE, AM_MA, AM_NI, AM_TR],
  notes="Global 15 = his 8th turn. His hand after global 13: Claydol, Sharpedo, Carvanha, Cyrus; Darkness Claw (row '14' 372-389) "
        "revealed it and discarded Cyrus (in his discard at 392s); row '15' 390-407 draws Wallace -> Claydol, Sharpedo, Carvanha, "
        "Wallace. Board: Active Wailord 180 - poison 20 - Claw 80 - poison 20 = 60, Poisoned, four Water, Cape; Sharpedo 100; 2nd "
        "Wailord 200, Helmet, one Water (slot 2); Baltoy 60 (slot 3). Score 2-0. Opponent: Deino KO'd, Mega Absol ex promoted; "
        "global 14 draw (2->3), 2nd Darkness to it, Darkness Claw. His move in the review's order: Baltoy -> Claydol, 2nd Water to "
        "the Benched Wailord, Whale Pump 100 (Mega Absol ex 170 -> 70)."),
]
