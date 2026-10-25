from v2_helpers import P, B
D = 'v2deck_4fa967805c'; G = '20261021_225131000_SR'
BA = 'Baltoy A3a 030'; CD = 'Claydol A3a 031'; WD = 'Wailord B1 057'; CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'
WM = 'Wailmer B4 036'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; HH = 'Heavy Helmet B1 219'
CC = 'Copycat B1 225'; EC = 'Elegant Cape B3b 065'; WA = 'Wallace B3b 068'
# opponent's cards (printing: the first cards.py lists among those matching the shown facts)
O_HO = 'Horsea A4 041'; O_SE = 'Seadra A4 042'; O_MK = 'Magikarp A1 077'; O_MG = 'Mega Gyarados ex B1 052'
O_CV = 'Carvanha B4 034'; O_MS = 'Mega Sharpedo ex B4 035'; O_WA = 'Wallace B3b 068'
AP = ("opponent's list unknown; opponent's hand size from the visible plays; the opponent's next Energy is Water from the review's "
      "setup line ('Water Energy Zones visible')")


def _wallace_t1(v):
    # Wallace's random evolution (review: Carvanha -> Mega Sharpedo ex): the variant holds the evolved Pokemon on the Bench already
    v['me']['hand'].remove(CV)
    v['me']['board'].append(B(MS, 190, behind=[CV]))
    v['force'] = [l for l in v['force'] if l != 'Place:Carvanha@1']


POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[EC, PB, CY, WD, WA], disc=[], dene='', board=[B(WM, 100)], ko=0),
  dict(hand_count=4, disc=[], dene='', zone='W', board=[B(O_HO, 50)], ko=0),
  ['Play:Poké Ball', 'Place:Carvanha@1', 'Play:Wallace', 'ChooseRandomEvolutionTarget', 'Play:Elegant Cape', 'Tool:Elegant Cape@1', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand count (4) is the opening five less the Active Horsea (the opponent has not drawn yet)",
  ambiguous=['Opponent Horsea printing chosen by HP (50) and attack title (Hook); A4 041, A4b 088, A4b 089 and B2 208 match'],
  draws={0: [CV], 2: []}, vpatch=_wallace_t1,
  notes="Global 1 = his 1st turn (he went first). Setup line 26-38: opening five Wailmer, Elegant Cape, Poke Ball, Cyrus, Wailord; Wailmer "
        "Active, no Bench -> 4 in hand. Global 1 line: draw Wallace -> 5. Opponent: Horsea 50 (Hook 30) Active, no Bench; 5 - 1 = 4 in hand. "
        "His move in the review's order: Poke Ball (finds Carvanha, public), Carvanha benched, Wallace on Carvanha -> Mega Sharpedo ex "
        "(random evolution: variant patch puts Mega Sharpedo ex 190 on the Bench and drops the Place), Elegant Cape to the Stage 1 "
        "(190 -> 220), no Energy (first player's first turn), no attack."),
P(G, 3, 2, [0, 0],
  dict(hand=[CY, WD, HH], disc=[PB, WA], dene='', board=[B(WM, 100), B(MS, 220, tool=EC, behind=[CV])], ko=0),
  dict(hand_count=3, disc=[O_WA], dene='', zone='W', board=[B(O_HO, 50), B(O_MG, 210, 'W', behind=[O_MK])], ko=0),
  ['Evolve:Wailord@0', 'Play:Heavy Helmet', 'Tool:Heavy Helmet@0', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Wallace printing is not shown, the first listed printing is used",
  ambiguous=['Opponent Horsea printing chosen by HP (50) and attack title (Hook); A4 041, A4b 088, A4b 089 and B2 208 match',
             'Opponent Magikarp under Mega Gyarados ex: printing chosen by HP (30) only; no attack shown',
             'Opponent Mega Gyarados ex printing chosen by name and HP (210); B1 052, B1 255, B1 285 and B3b 101 match'],
  notes="Global 3 = his 2nd turn. After global 1 his hand is Cyrus, Wailord (review global 1 'Hand Cyrus/Wailord'); draw Heavy Helmet -> 3. "
        "Board: Wailmer 100 Active no Energy, Mega Sharpedo ex 220 with Cape on the Bench. Discard: Poke Ball, Wallace. Opponent global 2: "
        "4 + draw 1 = 5, Magikarp benched (4), Wallace (3), Water to the benched Mega Gyarados ex; Horsea 50 Active no Energy. His move in "
        "the review's order: evolve Wailmer to Wailord, Heavy Helmet to Wailord, Water to Wailord, pass."),
P(G, 9, 5, [0, 0],
  dict(hand=[CY, CD, WD], disc=[PB, WA, PB], dene='',
       board=[B(WD, 190, 'WWW', tool=HH, behind=[WM]), B(MS, 220, tool=EC, behind=[CV]), B(BA, 60)], ko=0),
  dict(hand_count=3, disc=[O_WA, O_WA], dene='W', zone='W',
       board=[B(O_MS, 190, behind=[O_CV]), B(O_MG, 210, 'WWW', behind=[O_MK]), B(O_SE, 80, behind=[O_HO])], ko=0),
  ['Evolve:Claydol@2', 'Attach:1Water@0 zone', 'Attack:Whale Pump'],
  D, None,
  approx=AP + "; the opponent's Wallace printing is not shown, the first listed printing is used; the opponent's Bench is listed in "
            "the order benched (Mega Gyarados ex's line first, Seadra moved to the Bench by the retreat on global 8)",
  ambiguous=['Opponent Mega Sharpedo ex printing chosen by name and HP (190); B4 035, B4 182 and B4 196 match',
             'Opponent Carvanha under Mega Sharpedo ex: printing chosen by HP (50) only; B4 034 and P-B 081 have 50 HP',
             'Opponent Horsea under Seadra: printing chosen by HP (50) and attack title (Hook); A4 041, A4b 088, A4b 089 and B2 208 match',
             'Opponent Seadra printing chosen by HP (80) and attack title (Razor Fin); A4 042, A4b 090, A4b 091 and B2 209 match',
             'Opponent Magikarp under Mega Gyarados ex: printing chosen by HP (30) only; no attack shown',
             'Opponent Mega Gyarados ex printing chosen by name and HP (210); B1 052, B1 255, B1 285 and B3b 101 match'],
  notes="Global 9 = his 5th turn. Hand: Cyrus after global 3; global 5 draw Claydol (held), Water to Wailord; global 7 draw 2nd Poke Ball, "
        "played, Baltoy found and benched, Water to Wailord; global 9 draw Wailord -> Cyrus, Claydol, Wailord. Board: Wailord 200 -10 "
        "(Hook 30 - Helmet 20 on global 6) = 190 with three Water and Helmet; Bench Mega Sharpedo ex 220 Cape, Baltoy 60 (slot 2). Discard: "
        "Poke Ball, Wallace, Poke Ball. Opponent hand: 3 after global 2; global 4 +1 = 4 (Water only); global 6 +1, Carvanha benched = 4 "
        "(Water to Horsea, Hook); global 8 +1, Carvanha -> Mega Sharpedo ex (-1), Wallace (-1) on Horsea -> Seadra (from deck) = 3. "
        "Global 8: third Water to Gyarados, Seadra retreats (its one Water discarded), Mega Sharpedo ex 190 no Energy promoted. His "
        "move in the review's order: Baltoy -> Claydol, 4th Water to Wailord, Whale Pump 100 (190 -> 90)."),
]
