from v2_helpers import P, B
D = 'v2deck_693850eaa5'; G = '20261022_004518000_SR'
BA = 'Baltoy A3a 030'; CD = 'Claydol A3a 031'; WD = 'Wailord B1 057'; AG = 'Alolan Grimer B2 096'; AM = 'Alolan Muk B2 097'
CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'; WM = 'Wailmer B4 036'; XS = 'X Speed P-A 002'; PB = 'Poké Ball P-A 005'
PR = "Professor's Research P-A 007"; SA = 'Sabrina A1 225'; CY = 'Cyrus A2 150'; HH = 'Heavy Helmet B1 219'; CC = 'Copycat B1 225'
EC = 'Elegant Cape B3b 065'; WA = 'Wallace B3b 068'
# opponent's cards (printing: the first cards.py lists among those matching the shown facts)
O_GI = 'Gible B4a 052'; O_GA = 'Gabite B4a 053'; O_GC = 'Garchomp B4a 054'; O_MT = 'Mantyke A4a 023'; O_SB = 'Small Balloon B3b 064'
O_CC = 'Copycat B1 225'; O_PR = "Professor's Research A4b 373"; O_PB = 'Poké Ball A2b 111'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AP_TR = ("the opponent's Trainer printings (Copycat, Professor's Research, Poke Ball, Small Balloon) are not shown, the first listed "
         "printings are used")
AMB_GI = 'Opponent Gible printing chosen by HP (60) and attack title (Take Down); only B4a 052 matches'
AMB_MT = 'Opponent Mantyke printing chosen by HP (30) and attack title (Splashy Toss); A4a 023, A4a 105 and B2 210 match'
AMB_SB = 'Opponent Small Balloon printing not shown; B3b 064 and B3b 106 match'

POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[CY, CC, PB, MS, PB], disc=[], dene='', board=[B(WM, 100)], ko=0),
  dict(hand_count=4, disc=[O_CC], dene='', board=[B(O_MT, 30), B(O_GI, 60, tool=O_SB), B(O_GI, 60, 'W')], ko=0),
  ['Play:Poké Ball', 'Play:Poké Ball', 'Place:Carvanha@1', 'Play:Copycat', 'Place:Baltoy@2', 'Place:Alolan Grimer@3',
   'Attach:1Water@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + AP_TR + "; the opponent's Bench is listed left to right as the review gives it (the Small Balloon Gible left, "
            "the Gible with Water right)",
  ambiguous=[AMB_GI, AMB_MT, AMB_SB],
  draws={0: [CV], 1: [CV], 3: ['-' + CY, '-' + MS, '-' + CV, AM, AG, BA, MS]},
  notes="Global 2 = his 1st turn (he went second). Setup row: opening five Wailmer, Cyrus, Copycat, Poke Ball, Mega Sharpedo ex; Wailmer "
        "Active, Bench empty -> 4; global 2 row: draw 2nd Poke Ball -> 5. Opponent: setup Gible 60 Active + Gible 60 Bench (5 - 2 = 3); "
        "global 1: draw 4, Mantyke benched 3, Small Balloon to the Active Gible 2, Copycat (-1, draw 4 = his 4-card hand) 4, the Balloon "
        "Gible retreats to Mantyke, Splashy Toss puts one Water on the right (non-Tool) Gible. His move in the review's order: both Poke "
        "Balls (Carvanha each), one Carvanha benched, Copycat (his hand then Cyrus, Mega Sharpedo ex, the 2nd Carvanha; draws 4 = the "
        "opponent's 4: Alolan Muk, Alolan Grimer, Baltoy, Mega Sharpedo ex, all revealed), Baltoy and Alolan Grimer benched, Water to "
        "Wailmer, no attack. The order of the 2nd Poke Ball and the Carvanha placement is as the review words it."),
P(G, 4, 2, [0, 0],
  dict(hand=[AM, MS, CV], disc=[PB, PB, CC], dene='', board=[B(WM, 100, 'W'), B(CV, 50), B(BA, 60), B(AG, 80)], ko=0),
  dict(hand_count=5, disc=[O_CC, O_PR, O_PB], dene='', board=[B(O_MT, 30), B(O_GI, 60, 'W', tool=O_SB), B(O_GI, 60, 'WW')], ko=0),
  ['Attach:1Water@0 zone', 'Evolve:Alolan Muk@3', 'Evolve:Mega Sharpedo ex@1', 'EndTurn'],
  D, None,
  approx=AP + "; " + AP_TR + "; the opponent's Poke Ball found nothing (review: no eligible-card message), so it is counted as -1",
  ambiguous=[AMB_GI, AMB_MT, AMB_SB],
  notes="Global 4 = his 2nd turn. Hand after global 2: Alolan Muk, Mega Sharpedo ex; draw Carvanha -> 3. Board: Wailmer 100 one Water; "
        "Bench Carvanha (@1), Baltoy (@2), Alolan Grimer (@3), in the order benched. Discard: two Poke Balls, Copycat. Opponent global 3: "
        "4 + draw 5, Research (-1 +2) 6, Water to the right Gible (2 Water), Poke Ball failed (-1) 5, Splashy Toss 1 Water to the left "
        "Balloon Gible. His move in the review's order: 2nd Water to Wailmer, Grimer -> Alolan Muk, Carvanha -> Mega Sharpedo ex, no attack."),
P(G, 6, 3, [0, 0],
  dict(hand=[CV, SA], disc=[PB, PB, CC], dene='', board=[B(WM, 100, 'WW'), B(MS, 190, behind=[CV]), B(BA, 60), B(AM, 110, behind=[AG])],
       ko=0),
  dict(hand_count=6, disc=[O_CC, O_PR, O_PB], dene='', board=[B(O_MT, 30), B(O_GI, 60, 'WW', tool=O_SB), B(O_GI, 60, 'WWF')], ko=0),
  ['Attach:1Water@0 zone', 'Play:Sabrina', 'Attack:Wave Splash'],
  D, None,
  approx=AP + "; " + AP_TR + "; the opponent's Poke Ball found nothing (review: no eligible-card message), so it is counted as -1",
  ambiguous=[AMB_GI, AMB_MT, AMB_SB],
  notes="Global 6 = his 3rd turn. Hand after global 4: Carvanha; draw Sabrina -> 2. Board: Wailmer 100 two Water; Bench Mega Sharpedo ex "
        "190, Baltoy 60, Alolan Muk 110. Opponent global 5: 5 + draw 6, Fighting to the right Gible (Water 2, Fighting 1), Splashy Toss "
        "to the left Balloon Gible (Water 2). His move in the review's order (181-210): 3rd Water to Wailmer, Sabrina (the opponent chose "
        "the left Balloon Gible with two Water: the opponent's choice, not in the move), Wave Splash 60 KOs it."),
P(G, 8, 4, [1, 0],
  dict(hand=[CV, WA], disc=[PB, PB, CC, SA], dene='', board=[B(WM, 100, 'WWW'), B(MS, 190, behind=[CV]), B(BA, 60), B(AM, 110, behind=[AG])],
       ko=0),
  dict(hand_count=6, disc=[O_CC, O_PR, O_PB, O_GI, O_SB], dene='WW', board=[B(O_MT, 30), B(O_GA, 80, 'WWWF', behind=[O_GI])], ko=1),
  ['Attach:1Water@0 zone', 'Attack:Wave Splash'],
  D, None,
  approx=AP + "; " + AP_TR + "; the opponent's Poke Ball found nothing (review: no eligible-card message), so it is counted as -1",
  ambiguous=[AMB_GI, AMB_MT, AMB_SB, 'Opponent Gabite printing chosen by HP (80) and attack title (Linear Attack); only B4a 053 matches'],
  notes="Global 8 = his 4th turn. Hand after global 6: Carvanha; draw Wallace -> 2. Board: Wailmer 100 three Water; Bench as before. "
        "Discard + Sabrina. Opponent: Mantyke promoted after the KO; the KO'd Gible, its Small Balloon and two Water in the discard; "
        "global 7: 6 + draw 7, Water to the remaining Gible (Water 3, Fighting 1), Gible -> Gabite 80 (6), Splashy Toss attached nothing. "
        "His move in the review's order (228-247): 4th Water to Wailmer, Wave Splash 60 KOs Mantyke 30."),
P(G, 10, 5, [2, 1],
  dict(hand=[CV, WA, PR], disc=[PB, PB, CC, SA, WM], dene='WWWW', board=[B(MS, 190, behind=[CV]), B(BA, 60), B(AM, 110, behind=[AG])], ko=1),
  dict(hand_count=5, disc=[O_CC, O_PR, O_PB, O_GI, O_SB, O_MT, O_PB], dene='WW',
       board=[B(O_GC, 150, 'WWWFF', behind=[O_GA, O_GI], effects=[{"effect": "PreventAllDamageAndEffects", "turns": 1}])], ko=2),
  ["Play:Professor's Research", 'Attach:1Water@0 zone', 'Retreat:2', 'Place:Carvanha@3', 'EndTurn'],
  D, None,
  approx=AP + "; " + AP_TR + "; the opponent's two Poke Balls found nothing (review: no eligible-card message), each counted as -1",
  ambiguous=[AMB_GI, AMB_MT, AMB_SB, 'Opponent Gabite printing chosen by HP (80) and attack title (Linear Attack); only B4a 053 matches',
             'Opponent Garchomp printing chosen by HP (150), Ability title (Mach Stealth) and attack title (Land Crush); only B4a 054 '
             'matches'],
  draws={0: [XS, WD]},
  notes="Global 10 = his 5th turn. Hand after global 8: Carvanha, Wallace; draw Professor's Research (279) -> 3. Global 9: Land Crush KOs "
        "Wailmer (four Water to the discard), he promoted Mega Sharpedo ex 190 (no Energy); Bench Baltoy, Alolan Muk (compacted). "
        "Opponent: Mantyke KO'd on global 8 (to the discard), Gabite promoted; global 9: 6 + draw 7, Fighting to Gabite, Poke Ball failed "
        "(6), Gabite -> Garchomp 150 (5), Land Crush 120 KO; Mach Stealth shown protecting Garchomp during his next turn (review: Turbo "
        "Shark preview 0), so the effect PreventAllDamageAndEffects for 1 turn is set. His move in the review's order (279-316): Research "
        "(X Speed, Wailord), Water to Mega Sharpedo ex, attack menu opened and closed (not an action), retreat (cost 0) to Alolan Muk "
        "(@2), the spare Carvanha benched (@3), no attack."),
]
