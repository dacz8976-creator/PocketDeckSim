from v2_helpers import P, B
D = 'v2deck_7907f1e146'; G = '20261024_175606000_SR'
CA = 'Carvanha P-B 081'; MSH = 'Mega Sharpedo ex B4 035'; MGY = 'Mega Gyarados ex B1 052'; CAPE = 'Elegant Cape B3b 065'
CC = 'Copycat B1 225'; SS = 'Soothing Shore B4 154'; CAB = 'Cabbie B3 150'
MAG = 'Magby A4 032'; FID = 'Fidough B3b 034'; RR = 'Rockruff B3b 038'
OPR = "Professor's Research A4b 373"; OPB = 'Poké Ball A2b 111'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
RRN = ("the Benched Rockruff's printing (B3b 038, the only 60-HP Rockruff with Puppy Pile) is the face-up card in play from setup; the "
       "review names its attack only when the opponent's Puppy Pile counted it on global 6")
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[MSH, MGY, CAPE, CC, CAPE], disc=[], dene='', board=[B(CA, 50)], ko=0),
  dict(hand_count=2, disc=[], dene='', board=[B(MAG, 30), B(FID, 40), B(RR, 60)], ko=0),
  ['Play:Elegant Cape', 'Tool:Elegant Cape@0', 'Play:Copycat', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand (2) is the opening five less the three Pokémon put in play (Copycat drew two); " + RRN,
  ambiguous=['Opponent Magby printing chosen by HP (30) and attack title (Toasty Toss); A4 032, A4 166 and B2 206 match'],
  draws={2: ['-' + CAPE, '-' + MGY, '-' + MSH, MSH, SS]},
  notes="Global 1 = his 1st turn (he went first). Timeline row 27-44: opening five Carvanha (Aqua Jet, 50HP -> P-B 081), Mega Sharpedo ex, "
        "Mega Gyarados ex, Elegant Cape, Copycat; Carvanha alone Active, Bench empty. Opponent: Magby 30 Active, Fidough 40 (-> B3b 034, the "
        "only 40-HP Fidough) and Rockruff 60 Bench, so 2 in hand (Copycat drew two 'against opponent's two-card hand'). Row 45-67: draw "
        "Elegant Cape -> hand MSh, MGy, Cape, Copycat, Cape. His move in order: Cape to Carvanha 49-52, Copycat 58-63 (shuffles "
        "Cape/MGy/MSh, draws Mega Sharpedo ex and Soothing Shore), no Energy (first player), end turn. Rockruff: row 248 (global 6) and "
        "UNCERTAINTIES 'Puppy Pile target zones' say the benched Rockruff is one of the Puppy Pile Pokemon -> B3b 038; it is the same "
        "face-up card that sat on the Bench from setup."),
P(G, 3, 2, [0, 0],
  dict(hand=[MSH, SS, CAB], disc=[CC], dene='', board=[B(CA, 50, tool=CAPE)], ko=0),
  dict(hand_count=4, disc=[OPR, OPB], dene='', board=[B(MAG, 30), B(FID, 40, 'RR'), B(RR, 60)], ko=0),
  ['Evolve:Mega Sharpedo ex@0', 'Play:Soothing Shore', 'Play:Cabbie', 'Attach:1Water@0 zone', 'Attack:Turbo Shark'],
  D, None,
  approx=AP + "; the opponent's hand (4) counts the hidden Poké Ball search on global 2 as +1 card; the opponent's Professor's Research "
            "and Poké Ball printings are not shown (the first listed printings are used); " + RRN,
  ambiguous=['Opponent Magby printing chosen by HP (30) and attack title (Toasty Toss); A4 032, A4 166 and B2 206 match',
             "Opponent's Professor's Research and Poké Ball printings not shown; A4b 373 and A2b 111 used (P-A 007 and P-A 005 also match)"],
  draws={2: [SS]},
  notes="Global 3 = his 2nd turn. Hand after global 1: Mega Sharpedo ex, Soothing Shore (Copycat draws, row 45-67); row 102-136 draw Cabbie "
        "-> MSh, Soothing Shore, Cabbie. Board: Carvanha 50 with Elegant Cape (Cape gives a Basic no HP). Discard: Copycat. Opponent, row "
        "67-102: hand 2, draw 3, Professor's Research (-1 +2) 4, Poké Ball (-1 +1 hidden Basic) 4, no Basic benched; ordinary Fire and "
        "Toasty Toss both to benched Fidough (native 116: Fidough 2 Fire, Rockruff 0). His move in order (row 102-136): evolve Active "
        "Carvanha to Mega Sharpedo ex 106-110, Soothing Shore 111-114, Cabbie 116 (fetches the 2nd Soothing Shore 118-119; the only "
        "Stadium left in his deck), Water to Active ~120, Turbo Shark 123-128 (KO Magby; no Benched Water target). pg_legal_v14 stops at "
        "Play:Cabbie as a hidden draw, but v2_helpers' chance-step rule has no Cabbie, so check_game's variant says 'no chance step': "
        "draws={2: [Soothing Shore]} is the record for when Cabbie is added; scratch/b10/vcheck.py (check_game's variant with Cabbie added) "
        "applies the rest 4/4."),
]
