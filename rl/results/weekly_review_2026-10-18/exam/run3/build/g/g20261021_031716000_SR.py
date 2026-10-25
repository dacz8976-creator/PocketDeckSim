from v2_helpers import P, B
D = 'v2deck_4fa967805c'; G = '20261021_031716000_SR'
WM = 'Wailmer B4 036'; WL = 'Wailord B1 057'; BT = 'Baltoy A3a 030'; CL = 'Claydol A3a 031'; CV = 'Carvanha B4 034'
MSH = 'Mega Sharpedo ex B4 035'; PB = 'Poké Ball P-A 005'; EC = 'Elegant Cape B3b 065'; CC = 'Copycat B1 225'; HH = 'Heavy Helmet B1 219'
WA = 'Wallace B3b 068'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'
TV = "Team Rocket's Voltorb B4a 019"; TE = "Team Rocket's Electrode B4a 020"; SX = 'Shinx A2 058'; LX = 'Luxray A2 060'
ORH = 'Rocky Helmet A2 148'; OPR = "Professor's Research A4b 373"; ORC = 'Rare Candy A3 144'
RCV = {"card": "Rainbow Cave B4 155", "owner": 1}
AP = "opponent's list unknown; opponent's hand size from the visible plays"
OTR = ("the opponent's Trainer printings (Professor's Research, Rare Candy, Rocky Helmet) are not shown; the printing cards.py lists "
       "first is used")
AMB_SX = 'Opponent Shinx: its attack was not shown; printing chosen by HP (60) only'
AMB_LX = 'Opponent Luxray printing chosen by HP (130) and attack title (Volt Bolt); A2 060 is the only match'


def no_energy_now(p):
    """The first player's first turn: no Energy from the zone. With energy_now set, pg_legal_v14 lists an attach as legal on
    global turn 1 (scratch/b3/t_t1energy.py); None makes the zone read ["None", "Some(Water)"]."""
    p['me']['energy_now'] = None
    return p


POS = [
no_energy_now(P(G, 1, 1, [0, 0],
  dict(hand=[WA, MSH, PB, EC, CC], disc=[], dene='', board=[B(WM, 100)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(TV, 60)], ko=0),
  ['Play:Poké Ball', 'Place:Carvanha@1', 'Play:Elegant Cape', 'Tool:Elegant Cape@1', 'Play:Wallace', 'ChooseRandomEvolutionTarget',
   'EndTurn'],
  D, None,
  approx=AP + "; no Energy on the first player's first turn (energy_now None)",
  ambiguous=["Opponent Team Rocket's Voltorb printing chosen by name and HP (60); B4a 019 is the only match"],
  draws={0: [CV], 4: []},
  notes="Global 1 = his 1st turn (he went first). 'Opening and setup': opening five Wallace, Mega Sharpedo ex, Poke Ball, Elegant "
        "Cape, Wailmer; Wailmer 100 Active, empty Bench -> 4 in hand. Opponent: lone Team Rocket's Voltorb 60 -> 4 in hand, no draw "
        "yet. Table row 1: draw Copycat -> 5. His move in the review's order: Poke Ball (Carvanha, ~40-44 s), Carvanha benched (@1), "
        "Elegant Cape on Carvanha (~50-54 s), Wallace (~56-62 s) on Carvanha -> Mega Sharpedo ex 220 from the deck, end; no Energy, "
        "no attack. Wallace's chance step: draws {4: []} (nothing to the hand). No vpatch: no label after Wallace depends on the "
        "evolution, and putting Mega Sharpedo on the board up front would block the variant's earlier Place. The single-target label "
        "'ChooseRandomEvolutionTarget' (no arguments) is from scratch/b3/t_wallace2.py (Place, Cape, Wallace on turn 1). energy_now "
        "set to None after P().")),
P(G, 3, 2, [0, 0],
  dict(hand=[MSH, CC, PR], disc=[PB, WA], dene='', board=[B(WM, 60), B(MSH, 220, tool=EC, behind=[CV])], ko=0),
  dict(hand_count=3, disc=[OPR], dene='', board=[B(TV, 60, 'L', tool=ORH), B(SX, 60)], ko=0),
  ["Play:Professor's Research", 'Evolve:Wailord@0', 'Attach:1Water@0 zone', 'Play:Elegant Cape', 'Tool:Elegant Cape@0', 'EndTurn'],
  D, None, stadium=RCV,
  approx=AP + "; " + OTR + "; how the opponent found Shinx on global turn 2 is not named (any search card is not listed in the "
            "discard); the opponent's hand count (3) is the same either way and matches the 1-card hand Copycat reads on global turn 7",
  ambiguous=["Opponent Team Rocket's Voltorb printing chosen by HP (60) and attack title (Rolling Attack); B4a 019 is the only match",
             AMB_SX],
  draws={0: [WL, EC]},
  notes="Global 3 = his 2nd turn. Hand after global 1: Mega Sharpedo ex, Copycat (Poke Ball, Cape, Wallace played). Table row 3: draw "
        "Professor's Research -> 3. Board: Wailmer 60 (row 2: Rolling Attack 20 + Weakness = 40); Bench Mega Sharpedo ex 220 with Cape. "
        "Opponent row 2: draw (5), Shinx searched and benched, Professor's Research, Rainbow Cave, Rocky Helmet on Voltorb, Lightning "
        "to Voltorb, Rolling Attack. Opp hand: 5 -> Shinx 4 -> Research 5 -> Cave 4 -> Helmet 3 (a Poke Ball for Shinx gives the "
        "same 3); check: global 4 (+1 -Rare Candy -Luxray -Electrode) and 6 (+1 -Voltorb) leave 1, the 'one-card hand' of row 7. His "
        "move in the review's order: Professor's Research (Wailord, Elegant Cape), Wailmer -> Wailord 160, Water to Wailord, 2nd "
        "Cape on Wailord (190), end."),
P(G, 5, 3, [0, 0],
  dict(hand=[MSH, CC, PR], disc=[PB, WA, PR], dene='',
       board=[B(WL, 190, 'W', tool=EC, behind=[WM]), B(MSH, 190, tool=EC, behind=[CV])], ko=0),
  dict(hand_count=1, disc=[OPR, ORC], dene='', board=[B(TE, 70, 'L', tool=ORH, behind=[TV]), B(LX, 130, 'L', behind=[SX])], ko=0),
  ["Play:Professor's Research", 'Place:Baltoy@2', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None, stadium=RCV,
  approx=AP + "; " + OTR + "; the Shinx under Luxray (Rare Candy): printing chosen by HP (60) only",
  ambiguous=["Opponent Team Rocket's Electrode printing chosen by HP (70), Ability title (Destiny Burst) and attack title (Random "
             "Spark); B4a 020 is the only match", AMB_LX, 'Opponent Shinx under Luxray: its attack was not shown; printing chosen by '
             'HP (60) only'],
  draws={0: [BT, CL]},
  notes="Global 5 = his 3rd turn. Hand after global 3: Mega Sharpedo ex, Copycat. Row 5: draw 2nd Professor's Research -> 3. Board: "
        "Wailord 190 (Cape, one Water); Bench Mega Sharpedo 190 (row 4: Random Spark 30). Opponent row 4: draw (4), Rare Candy on "
        "Shinx -> Luxray 130 (3, 2), Voltorb -> Team Rocket's Electrode 70 keeping Rocky Helmet and Lightning (1), Lightning to "
        "Luxray, Random Spark 30 on the Benched Mega. His move in the review's order: Professor's Research (Baltoy, Claydol), Baltoy "
        "benched (@2), Water to Wailord, no attack, end."),
P(G, 7, 4, [0, 0],
  dict(hand=[MSH, CC, CL, WM], disc=[PB, WA, PR, PR], dene='',
       board=[B(WL, 190, 'WW', tool=EC, behind=[WM]), B(MSH, 160, tool=EC, behind=[CV]), B(BT, 60)], ko=0),
  dict(hand_count=1, disc=[OPR, ORC], dene='',
       board=[B(TE, 70, 'L', tool=ORH, behind=[TV]), B(LX, 130, 'LL', behind=[SX]), B(TV, 60)], ko=0),
  ['Place:Wailmer@3', 'Evolve:Claydol@2', 'Attach:1Water@0 zone', 'Play:Copycat', 'Play:Heavy Helmet', 'Tool:Heavy Helmet@3', 'EndTurn'],
  D, None, stadium=RCV,
  approx=AP + "; " + OTR + "; the Shinx under Luxray: printing chosen by HP (60) only",
  ambiguous=["Opponent Team Rocket's Electrode printing chosen by HP (70), Ability title (Destiny Burst) and attack title (Random "
             "Spark); B4a 020 is the only match", AMB_LX, 'Opponent Shinx under Luxray: its attack was not shown; printing chosen by '
             'HP (60) only', "Opponent second Team Rocket's Voltorb printing chosen by name and HP (60); B4a 019 is the only match"],
  draws={3: ['-' + MSH, HH]},
  notes="Global 7 = his 4th turn. Hand after global 5: Mega Sharpedo ex, Copycat, Claydol (Research played, Baltoy benched). Row 7: "
        "draw Wailmer -> 4. Board: Wailord 190 (Cape, two Water); Bench Mega Sharpedo 160 (row 6: Random Spark), Baltoy 60. Opponent "
        "row 6: draw (2), 2nd Team Rocket's Voltorb benched (1), Lightning to Luxray (2), Rainbow Cave, Random Spark. His move in the "
        "review's order: Wailmer benched (@3), Baltoy -> Claydol, Water to Wailord, Copycat (his hand then only Mega Sharpedo ex; "
        "draws 1 for the opponent's one card: Heavy Helmet), Heavy Helmet on Wailmer, end. Row 7's 'Select Rainbow Cave ~208; Can't "
        "heal appears and no healing occurs' is not in force: no Stadium effect happened (Rainbow Cave's text, cards.py, is a zone "
        "Energy discard, and the Water had already been attached)."),
P(G, 9, 5, [0, 0],
  dict(hand=[WL], disc=[PB, WA, PR, PR, CC], dene='',
       board=[B(WL, 190, 'WWW', tool=EC, behind=[WM]), B(MSH, 130, tool=EC, behind=[CV]), B(CL, 100, behind=[BT]), B(WM, 100, tool=HH)],
       ko=0),
  dict(hand_count=2, disc=[OPR, ORC], dene='',
       board=[B(TE, 70, 'L', tool=ORH, behind=[TV]), B(LX, 130, 'LL', behind=[SX]), B(TV, 60, 'L')], ko=0),
  ['Evolve:Wailord@3', 'Attach:1Water@0 zone', 'Attack:Whale Pump'],
  D, None, stadium=RCV,
  approx=AP + "; " + OTR + "; the Shinx under Luxray: printing chosen by HP (60) only",
  ambiguous=["Opponent Team Rocket's Electrode printing chosen by HP (70), Ability title (Destiny Burst) and attack title (Random "
             "Spark); B4a 020 is the only match", AMB_LX, 'Opponent Shinx under Luxray: its attack was not shown; printing chosen by '
             'HP (60) only'],
  notes="Global 9 = his 5th turn. Hand after global 7: empty (Wailmer benched, Claydol played, Copycat -> Heavy Helmet, attached). "
        "Row 9: draw 2nd Wailord -> 1. Board: Wailord 190 (Cape, three Water); Bench Mega Sharpedo 130 (row 8 Random Spark), Claydol "
        "100, Wailmer 100 with Heavy Helmet. Opponent row 8: draw (2), Lightning to the 2nd Voltorb, Random Spark. His move in the "
        "review's order: Wailmer -> Wailord (@3), 4th Water to the Active Wailord, Whale Pump 100 (KOs Electrode)."),
P(G, 11, 6, [1, 0],
  dict(hand=[CY], disc=[PB, WA, PR, PR, CC], dene='',
       board=[B(WL, 100, 'WWWW', tool=EC, behind=[WM]), B(MSH, 10, tool=EC, behind=[CV]), B(CL, 100, behind=[BT]),
              B(WL, 200, tool=HH, behind=[WM])], ko=0),
  dict(hand_count=3, disc=[OPR, ORC, TE, TV, ORH], dene='LLLL', board=[B(LX, 130, behind=[SX]), B(TV, 60, 'L')], ko=1),
  ['Attach:1Water@0 zone', 'Attack:Whale Pump'],
  D, None, stadium=RCV,
  approx=AP + "; " + OTR + "; the Shinx under Luxray: printing chosen by HP (60) only",
  ambiguous=[AMB_LX, 'Opponent Shinx under Luxray: its attack was not shown; printing chosen by HP (60) only'],
  notes="Global 11 = his 6th turn. Hand after global 9: empty. Row 11: draw Cyrus -> 1. Board: Wailord 100 (row 9: Rocky Helmet 20 "
        "and Destiny Burst 70 after Whale Pump KOs Electrode; Cape, four Water); Bench Mega Sharpedo 10 (row 10 Volt Bolt 120), "
        "Claydol 100, Wailord 200 with Heavy Helmet. Score 1-0. Opponent: Electrode KO'd (Electrode, Voltorb, Rocky Helmet, one "
        "Lightning to discard; opp ko 1); Luxray promoted (2 Lightning); row 10: draw (3), Lightning to Luxray (3), Volt Bolt "
        "discards all three. Opp Bench: 2nd Voltorb 60 with one Lightning. His move: 5th Water to Wailord, Whale Pump 110."),
]
