from v2_helpers import P, B
D = 'v2deck_4fa967805c'; G = '20261021_225620000_SR'
BA = 'Baltoy A3a 030'; CD = 'Claydol A3a 031'; WD = 'Wailord B1 057'; CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'
WM = 'Wailmer B4 036'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; HH = 'Heavy Helmet B1 219'
CC = 'Copycat B1 225'; EC = 'Elegant Cape B3b 065'; WA = 'Wallace B3b 068'
# opponent's cards (printing: the first cards.py lists among those matching the shown facts)
O_SWS = 'Swablu B1 196'      # the Active Swablu (Sing)
O_SW = 'Swablu A4a 064'      # the Benched Swablu (HP only)
O_DK = 'Darkrai B2b 040'; O_IG = 'Igglybuff A4a 059'
O_PB = 'Poké Ball A2b 111'; O_CC = 'Copycat B1 225'
AP = "opponent's list unknown; opponent's hand size from the visible plays"


def _wallace_t3(v):
    # Wallace's random evolution (review: Benched Carvanha with Elegant Cape -> Mega Sharpedo ex, 190 + 30 = 220)
    v['me']['board'][1] = B(MS, 220, tool=EC, behind=[CV])


POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[CY, PR, PR, MS], disc=[], dene='', board=[B(CV, 50), B(CV, 50)], ko=0),
  dict(hand_count=2, disc=[], dene='', board=[B(O_SWS, 50), B(O_DK, 100), B(O_SW, 50)], ko=0),
  ["Play:Professor's Research", 'Play:Elegant Cape', 'Tool:Elegant Cape@1', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand count (2) is the opening five less the three Pokemon placed (the opponent has not drawn yet)",
  ambiguous=['Opponent Active Swablu printing chosen by HP (50) and attack title (Sing); B1 196 and B3a 102 match',
             'Opponent Benched Swablu printing chosen by HP (50) only; its attack was not shown (50-HP Swablu printings have Peck, Sing, '
             'Fury Attack or Find a Friend)',
             'Opponent Darkrai printing chosen by HP (100) and Ability title (Bad Dreams); only B2b 040 matches'],
  draws={0: [CC, EC]},
  notes="Global 1 = his 1st turn (he went first). Setup row 24-39: opening five two Carvanha, Cyrus, two Professor's Research; Carvanha "
        "Active, 2nd Carvanha Benched -> hand Cyrus, two Research; draw Mega Sharpedo ex (row 40-56) -> 4. Opponent setup: Swablu 50 "
        "Active, Darkrai 100 and 2nd Swablu 50 Benched -> 5 - 3 = 2 in hand. The Active Swablu's attack (Sing) is seen on global 2 "
        "(row 89-100); the printing is a fact of the card in play at this turn, so the Sing printing is used. His move in the review's "
        "order (row 40-56): Professor's Research (draws Copycat, Elegant Cape), Cape to the BENCHED Carvanha, no Energy, no attack."),
P(G, 3, 2, [0, 0],
  dict(hand=[CY, PR, MS, CC, WA], disc=[PR], dene='', board=[B(CV, 30, cond=['Asleep']), B(CV, 50, tool=EC)], ko=0),
  dict(hand_count=4, disc=[O_PB, O_CC, O_PB], dene='', board=[B(O_SWS, 50, 'P'), B(O_DK, 100), B(O_SW, 50), B(O_IG, 30)], ko=0),
  ['Evolve:Mega Sharpedo ex@0', 'Play:Wallace', 'ChooseRandomEvolutionTarget', 'Attach:1Water@0 zone', 'Attack:Turbo Shark',
   'Attach:1Water@1 fx'],
  D, None,
  approx=AP + "; the opponent's two Poke Balls are each counted as +1 card (their results were hidden); the opponent's Trainer "
            "printings (Poke Ball, Copycat) are not shown, the first listed printings are used",
  ambiguous=['Opponent Active Swablu printing chosen by HP (50) and attack title (Sing); B1 196 and B3a 102 match',
             'Opponent Benched Swablu printing chosen by HP (50) only; its attack was not shown (50-HP Swablu printings have Peck, Sing, '
             'Fury Attack or Find a Friend)',
             'Opponent Darkrai printing chosen by HP (100) and Ability title (Bad Dreams); only B2b 040 matches'],
  draws={1: []}, vpatch=_wallace_t3,
  notes="Global 3 = his 2nd turn. After global 1 his hand is Cyrus, Research, Mega Sharpedo ex, Copycat (Cape attached); row 100-125 draw "
        "Wallace -> 5. Board: Active Carvanha 50 - 20 (Bad Dreams, row 89-100) = 30, Asleep (checkup tails at 99s); Benched Carvanha 50 "
        "with Cape. Discard: Professor's Research. Opponent global 2 (row 57-100): 2 + draw = 3, Poke Ball (-1 +1) = 3, Igglybuff benched "
        "= 2, Copycat (-1, shuffle 1, draw 4 = his hand of 4) = 4, Psychic to Active Swablu, 2nd Poke Ball (-1 +1) = 4, Sing. Bench "
        "order: Darkrai, Swablu (setup), Igglybuff. His move in the review's order (row 100-140): evolve the Active Carvanha to Mega "
        "Sharpedo ex (from hand), Wallace on the Benched Carvanha (random evolution: Mega Sharpedo ex from the deck, 220 with Cape; "
        "variant patch sets it on the Bench), Water to the Active, Turbo Shark 70 on Swablu 50 (KO; Water from the zone to the only "
        "Benched Water Pokemon, the engine's follow-up 'Attach:1Water@1 fx'). check_game's shipped run stops at the hidden random choice "
        "ChooseRandomEvolutionTarget and reports that forced label unmatched (tool behaviour, see scratch/b5/probe.sh)."),
]
