from v2_helpers import P, B
D = 'v2deck_f5671a4e7f'; G = '20261022_130806000_SR'
BA = 'Baltoy A3a 030'; CD = 'Claydol A3a 031'; WD = 'Wailord B1 057'; GO = 'Goldeen B3b 012'; SK = 'Seaking B3b 013'
CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'; WM = 'Wailmer B4 036'; PB = 'Poké Ball P-A 005'
PR = "Professor's Research P-A 007"; SA = 'Sabrina A1 225'; CY = 'Cyrus A2 150'; BM = 'Big Malasada A3 142'; HH = 'Heavy Helmet B1 219'
CC = 'Copycat B1 225'; EC = 'Elegant Cape B3b 065'; WA = 'Wallace B3b 068'
# opponent's cards (printing: the first cards.py lists among those matching the shown facts)
O_EN = 'Entei ex A4a 010'; O_DR = 'Dratini A3b 051'; O_DA = 'Dragonair B4 117'; O_MR = 'Mega Rayquaza ex B4 120'
O_PB = 'Poké Ball A2b 111'; O_PR = "Professor's Research A4b 373"
RC = {"card": "Rainbow Cave B4 155", "owner": 1}
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AP_TR = "the opponent's Trainer printings (Poke Ball, Professor's Research) are not shown, the first listed printings are used"
AMB_EN = ('Opponent Entei ex printing chosen by HP (140), Ability title (Legendary Pulse) and attack title (Blazing Beatdown); A4a 010, '
          'A4a 079, A4a 087, B2a 126 and P-A 110 match')
AMB_DR = 'Opponent Dratini printing chosen by HP (60) only; its attack was not shown'


def _wallace_t3(v):
    # Wallace's random evolution (review: Goldeen -> Seaking 90 from the deck): the variant holds Seaking on the Bench already
    v['me']['hand'].remove(GO)
    v['me']['board'].append(B(SK, 90, behind=[GO]))
    v['force'] = [l for l in v['force'] if l != 'Place:Goldeen@1']


POS = [
P(G, 3, 2, [0, 0],
  dict(hand=[MS, WD, SA, WA, CY, CC, GO], disc=[PR], dene='', board=[B(WM, 100)], ko=0),
  dict(hand_count=5, disc=[O_PB, O_PR], dene='L', board=[B(O_EN, 140, 'R'), B(O_DR, 60)], ko=0),
  ['Place:Goldeen@1', 'Evolve:Wailord@0', 'Play:Wallace', 'ChooseRandomEvolutionTarget', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None, stadium=RC,
  approx=AP + "; the opponent's Poke Ball is counted as +1 card (its result was hidden); " + AP_TR + "; Legendary Pulse's end-of-turn "
            "draw counted as +1",
  ambiguous=[AMB_EN, AMB_DR],
  draws={2: []}, vpatch=_wallace_t3,
  notes="Global 3 = his 2nd turn (he went first). Setup row: opening five Wailmer, Mega Sharpedo ex, Wailord, Sabrina, Wallace; Wailmer "
        "Active, no Bench -> 4. Global 1: draw Professor's Research, played (Cyrus, Copycat) -> 6. Global 3: draw Goldeen -> 7. Opponent: "
        "setup Entei ex 140 alone (5 - 1 = 4); global 2: draw 5, Poke Ball (-1 +1) 5, Dratini benched 4, Research (-1 +2) 5, Rainbow "
        "Cave 4 (the generated Lightning discarded, Fire made and attached to Entei ex), Legendary Pulse draw = 5. His move in the "
        "review's order (104-130): Goldeen benched, Wailmer -> Wailord, Wallace on Goldeen (random evolution: Seaking 90 from the deck; "
        "variant patch puts Seaking on the Bench and drops the Place), Water to Wailord, no attack. check_game's shipped run stops at "
        "ChooseRandomEvolutionTarget and reports it unmatched (tool behaviour; the rest checked by hand in scratch/b5/var_wallace.py)."),
P(G, 5, 3, [0, 0],
  dict(hand=[MS, SA, CY, CC, BA], disc=[PR, WA], dene='', board=[B(WD, 200, 'W', behind=[WM]), B(SK, 90, behind=[GO])], ko=0),
  dict(hand_count=6, disc=[O_PB, O_PR, O_PR, O_PB], dene='L',
       board=[B(O_EN, 140, 'R'), B(O_DA, 80, behind=[O_DR]), B(O_MR, 180, 'L')], ko=0),
  ['Place:Baltoy@2', 'Play:Copycat', 'Play:Poké Ball', 'Place:Carvanha@3', 'Play:Poké Ball', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None, stadium=RC,
  approx=AP + "; the opponent's Poke Balls are each counted as +1 card (results hidden); " + AP_TR + "; Legendary Pulse's end-of-turn "
            "draws counted as +1; the Energy the opponent discarded with Rainbow Cave on global 4 is not named and is not listed",
  ambiguous=[AMB_EN, AMB_DR,
             "Opponent Dragonair printing chosen by HP (80) and Ability title (Dragon's Blessing); B4 117, B4 175 and B4 233 match",
             'Opponent Mega Rayquaza ex printing chosen by name and HP (180); B4 120, B4 188 and B4 203 match'],
  draws={1: ['-' + MS, '-' + SA, '-' + CY, MS, CV, WA, BM, PB, PB], 2: [], 4: []},
  notes="Global 5 = his 3rd turn. Hand after global 3: Mega Sharpedo ex, Sabrina, Cyrus, Copycat; draw Baltoy -> 5. Board: Wailord 200 one "
        "Water, Seaking 90 Benched. Discard: Research, Wallace. Opponent global 4: 5 + draw 6, Dratini -> Dragonair (5), Research (-1 +2) "
        "6, Rainbow Cave used, Poke Ball (-1 +1) 6, Mega Rayquaza ex benched 5, Lightning to it, Legendary Pulse 6. His move in the "
        "review's order (166-215): Baltoy benched, Copycat (his hand then Mega Sharpedo ex, Sabrina, Cyrus shuffled; draws 6 = the "
        "opponent's 6: Mega Sharpedo ex, Carvanha, Wallace, Big Malasada, two Poke Balls, as the review's later turns confirm: Big "
        "Malasada and Wallace held, Carvanha benched, both Poke Balls used), Poke Ball (no Basic left in the deck), Carvanha benched "
        "(between the two Poke Balls), Poke Ball (none), 2nd Water to Wailord, no attack."),
]
