from v2_helpers import P, B
D = 'v2deck_4af97d2795'; G = '20261022_233003000_SR'
BA = 'Baltoy A3a 030'; CD = 'Claydol A3a 031'; WD = 'Wailord B1 057'; CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'
WM = 'Wailmer B4 036'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; SA = 'Sabrina A1 225'; CY = 'Cyrus A2 150'
BM = 'Big Malasada A3 142'; HH = 'Heavy Helmet B1 219'; CC = 'Copycat B1 225'; EC = 'Elegant Cape B3b 065'; WA = 'Wallace B3b 068'
# opponent's cards (printing: the first cards.py lists among those matching the shown facts)
O_DK = 'Darkrai ex A2 110'; O_HO = 'Hoopa ex B4 103'; O_SY = 'Mega Sableye ex B3b 041'; O_DN = 'Deceptive Needle B4 148'
O_LI = 'Lucky Ice Pop B2 145'; O_RE = 'Repel A3a 064'; O_XS = 'X Speed P-A 002'; O_PR = "Professor's Research A4b 373"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AP_UNK = ("the Trainers that started the opponent's hidden deck-to-hand acquisitions on global 1 and 3 were not read: each is counted "
          "as -1 +1 and is not listed in the discard")
AMB_DK = ('Opponent Darkrai ex printing chosen by HP (140), Ability title (Nightmare Aura) and attack title (Dark Prism); A2 110, A2 187, '
          'A2 202, A4b 245, A4b 378 and P-A 042 match')
AMB_HO = 'Opponent Hoopa ex printing chosen by HP (150) and attack titles (Shadow Bullet, Dynamite Punch); B4 103, B4 186 and B4 199 match'
AMB_SY = 'Opponent Mega Sableye ex printing chosen by HP (170) and attack title (Cursed Jewel); B3b 041, B3b 081 and B3b 088 match'

POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[CD, PB, BM, EC, WM], disc=[], dene='', board=[B(CV, 40)], ko=0),
  dict(hand_count=3, disc=[], dene='', board=[B(O_DK, 140, tool=O_DN), B(O_HO, 150)], ko=0),
  ['Place:Wailmer@1', 'Play:Poké Ball', 'Place:Baltoy@2', 'Play:Big Malasada', 'Attach:1Water@0 zone', 'Attack:Sharp Fang'],
  D, None,
  approx=AP + "; " + AP_UNK + "; the Deceptive Needle printing is not shown, the first listed printing is used",
  ambiguous=[AMB_DK, AMB_HO],
  draws={1: [BA]},
  notes="Global 2 = his 1st turn (he went second). Opening five Carvanha, Claydol, Poke Ball, Big Malasada, Elegant Cape; Carvanha Active "
        "-> 4; draw Wailmer (79) -> 5. Global 1: Deceptive Needle on Darkrai ex, a hidden acquisition (initiator not read), Hoopa ex "
        "benched, no Energy; Needle 10 -> Carvanha 40. Opponent hand: 5 - 1 = 4, draw 5, Needle 4, acquisition (-1 +1) 4, Hoopa ex 3. "
        "His move in the review's order (77-108): Wailmer benched, Poke Ball (Baltoy, public), Baltoy benched, Big Malasada (Carvanha "
        "40 -> 50), Water to Carvanha, Sharp Fang 30 (Darkrai 140 -> 110)."),
P(G, 4, 2, [0, 0],
  dict(hand=[CD, EC, PR], disc=[PB, BM], dene='', board=[B(WM, 90), B(CV, 30, 'W'), B(BA, 60)], ko=0),
  dict(hand_count=2, disc=[O_LI, O_RE], dene='', board=[B(O_DK, 130, 'D', tool=O_DN), B(O_HO, 150)], ko=0),
  ["Play:Professor's Research", 'Evolve:Mega Sharpedo ex@1', 'Evolve:Claydol@2', 'Evolve:Wailord@0', 'Play:Elegant Cape',
   'Tool:Elegant Cape@1', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + AP_UNK + "; the opponent's Trainer printings (Deceptive Needle, Lucky Ice Pop, Repel) are not shown, the first "
            "listed printings are used",
  ambiguous=[AMB_DK, AMB_HO],
  draws={0: [WD, MS]},
  notes="Global 4 = his 2nd turn. Hand after global 2: Claydol, Elegant Cape; draw Professor's Research (161) -> 3. Global 3: Lucky Ice "
        "Pop (Darkrai 110 -> 130, tails, discarded), hidden acquisition, Darkness to Darkrai (Nightmare Aura 20: Carvanha 50 -> 30), Repel "
        "(he promoted Wailmer; Carvanha 30 with its Water to the Bench, into Wailmer's spot @1), Needle 10 -> Wailmer 90. Opponent hand "
        "3 + draw 4, Ice Pop 3, acquisition (-1 +1) 3, Repel 2. Discard: Poke Ball, Big Malasada. His move in the review's order "
        "(159-192): Research (Wailord, Mega Sharpedo ex), Benched Carvanha -> Mega Sharpedo ex (170/190, Water kept), Baltoy -> Claydol, "
        "Wailmer -> Wailord (190/200), Cape to Mega Sharpedo ex (200/220), Water to Wailord, no attack."),
P(G, 8, 4, [0, 0],
  dict(hand=[CV, CY], disc=[PB, BM, PR, PB], dene='',
       board=[B(WD, 130, 'WW', behind=[WM]), B(MS, 160, 'W', tool=EC, behind=[CV]), B(CD, 100, behind=[BA])], ko=0),
  dict(hand_count=2, disc=[O_LI, O_RE, O_XS, O_PR], dene='D',
       board=[B(O_HO, 150, 'D'), B(O_DK, 130, tool=O_DN), B(O_HO, 150), B(O_SY, 170, 'D')], ko=0),
  ['Play:Cyrus', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + AP_UNK + "; the effect prevented on Darkrai ex on global 5 (initiator not established) is counted as no card from "
            "the hand, which makes the count agree with the 3 cards his Copycat drew on global 10; the opponent's Trainer printings "
            "(Deceptive Needle, Lucky Ice Pop, Repel, X Speed, Professor's Research) are not shown, the first listed printings are used",
  ambiguous=[AMB_DK, AMB_HO, AMB_SY],
  notes="Global 8 = his 4th turn. Hand after global 4: none; global 6: draw Poke Ball, played (2nd Carvanha, kept), Water to Wailord (2); "
        "global 8 draw Cyrus -> Carvanha, Cyrus. Board: Wailord 200 - 10 (Needle on Wailmer) - 30 - 30 (Shadow Bullet x2) = 130, two "
        "Water; Mega Sharpedo ex 220 - 20 (Carvanha's damage) - 20 - 20 (bench hits) = 160, one Water, Cape; Claydol 100. Opponent: global "
        "5 prevented effect on Darkrai, X Speed, Darkrai retreats (its Darkness discarded), Hoopa ex Active, Darkness to it, Shadow "
        "Bullet; global 7 Research, 2nd Hoopa ex and Mega Sableye ex benched, Darkness to Sableye, Shadow Bullet. Hand 2 + draw 3, X "
        "Speed 2; + draw 3, Research 4, two benched = 2. Bench: Darkrai (in Hoopa's old spot), 2nd Hoopa ex, Mega Sableye ex. His move "
        "in the review's order (270-284): Cyrus on the only damaged Benched Pokemon, Darkrai ex 130 (no target label: one option), "
        "third Water to Wailord, no attack."),
P(G, 10, 5, [0, 0],
  dict(hand=[CV, CC], disc=[PB, BM, PR, PB, CY], dene='',
       board=[B(WD, 100, 'WWW', behind=[WM]), B(MS, 160, 'W', tool=EC, behind=[CV]), B(CD, 100, behind=[BA])], ko=0),
  dict(hand_count=3, disc=[O_LI, O_RE, O_XS, O_PR], dene='D',
       board=[B(O_DK, 130, 'D', tool=O_DN), B(O_HO, 150, 'D'), B(O_HO, 150), B(O_SY, 170, 'D')], ko=0),
  ['Play:Copycat', 'Place:Wailmer@3', 'Play:Heavy Helmet', 'Tool:Heavy Helmet@0', 'Attach:1Water@0 zone', 'Attack:Whale Pump'],
  D, None,
  approx=AP + "; " + AP_UNK + "; the effect prevented on Darkrai ex on global 5 (initiator not established) is counted as no card from "
            "the hand, which makes the count (3) agree with the 3 cards his Copycat drew this turn; the opponent's Trainer printings "
            "(Deceptive Needle, Lucky Ice Pop, Repel, X Speed, Professor's Research) are not shown, the first listed printings are used",
  ambiguous=[AMB_DK, AMB_HO, AMB_SY],
  draws={0: ['-' + CV, HH, WM, WD]},
  notes="Global 10 = his 5th turn. Hand after global 8: Carvanha; draw Copycat (303) -> 2. Board: Wailord 130 - 20 (Nightmare Aura) - 10 "
        "(Needle) = 100 with three Water; Bench as before. Opponent global 9: draw (3), Darkness to the Active Darkrai ex, no Trainer. "
        "Bench: the 1st Hoopa ex (one Darkness) in Darkrai's old spot, 2nd Hoopa ex, Mega Sableye ex. His move in the review's order "
        "(301-341): Copycat (Carvanha shuffled; draws 3 = the opponent's hand: Heavy Helmet, Wailmer, Wailord, revealed), Wailmer "
        "benched (@3), Heavy Helmet to Wailord, fourth Water, Whale Pump 100 (Darkrai 130 -> 30)."),
]
