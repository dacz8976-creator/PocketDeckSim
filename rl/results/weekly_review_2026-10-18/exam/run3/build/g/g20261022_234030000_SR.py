from v2_helpers import P, B
D = 'v2deck_4af97d2795'; G = '20261022_234030000_SR'
BA = 'Baltoy A3a 030'; CD = 'Claydol A3a 031'; WD = 'Wailord B1 057'; CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'
WM = 'Wailmer B4 036'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; SA = 'Sabrina A1 225'; CY = 'Cyrus A2 150'
BM = 'Big Malasada A3 142'; HH = 'Heavy Helmet B1 219'; CC = 'Copycat B1 225'; EC = 'Elegant Cape B3b 065'; WA = 'Wallace B3b 068'
# opponent's cards (printing: the first cards.py lists among those matching the shown facts)
O_CA = 'Caterpie B3b 001'; O_ME = 'Metapod B3b 002'; O_BF = 'Butterfree B3b 003'; O_TR = 'Treecko B3 005'; O_GR = 'Grovyle B3 006'
O_CC = 'Copycat B1 225'; O_QG = 'Quick-Grow Extract B1a 067'; O_PR = "Professor's Research A4b 373"
FF = {"card": "Fragrant Forest B3 153", "owner": 1}
AP = "opponent's list unknown; opponent's hand size from the visible plays"


def _wallace_t7(v):
    # Wallace's random evolution (review: the centre Carvanha with Elegant Cape -> Mega Sharpedo ex, 190 + 30 = 220)
    v['me']['board'][2] = B(MS, 220, tool=EC, behind=[CV])


POS = [
P(G, 7, 4, [0, 0],
  dict(hand=[CV, WA], disc=[PR, CC, PB], dene='W',
       board=[B(WD, 130, behind=[WM]), B(WM, 100, 'W'), B(CV, 50, tool=EC), B(CD, 50, behind=[BA])], ko=0),
  dict(hand_count=3, disc=[O_CC, O_QG, O_PR], dene='G',
       board=[B(O_CA, 40, 'G'), B(O_BF, 130, behind=[O_ME, O_CA]), B(O_GR, 80, 'G', behind=[O_TR])], ko=0),
  ['Play:Wallace', 'ChooseRandomEvolutionTarget', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None, stadium=FF,
  approx=AP + "; the opponent's Trainer printings (Copycat, Quick-Grow Extract, Professor's Research) are not shown, the first listed "
            "printings are used; the opponent's Fragrant Forest is counted as not used on global 6 (review: no search result shown)",
  ambiguous=['Opponent Caterpie printing chosen by HP (40), Ability title (Quick Growth) and attack title (Hook); B3b 001 and B3b 091 match',
             'Opponent Metapod under Butterfree: printing chosen by HP (80) and attack title (Ram); B3b 002 and B3b 092 match',
             'Opponent Butterfree printing chosen by HP (130) and attack title (Sunny Wind); B3b 003 and B3b 093 match',
             'Opponent Treecko under Grovyle: printing chosen by HP (60) only; B3 005, B3 156 and P-B 061 match',
             'Opponent Grovyle printing chosen by HP (80) and attack title (Slicing Snipe); B3 006 and B3 157 match'],
  draws={0: []}, vpatch=_wallace_t7,
  notes="Global 7 = his 4th turn (he went first). His hand: the review gives his hand on global 11 as exactly Carvanha and Big Malasada "
        "after Heavy Helmet was drawn and attached; global 9 drew Big Malasada (no play), global 7 drew Wallace (played), so the hand at "
        "global 7 is Carvanha (the 2nd, kept on global 3 because the Bench was full) and Wallace. Forward check: global 3 Copycat drew 3 "
        "(Carvanha, Poke Ball, Elegant Cape) = the opponent's 3 (4 after setup, draw 5, Copycat -1 + his 5-card hand = 5, Treecko and "
        "Caterpie benched = 3). Board: Wailord 200 - 60 (Sunny Wind on Wailmer, global 4) - 10 (Hook, global 6) = 130, no Energy; Bench "
        "left to right: 2nd Wailmer 100 one Water (global 5), Carvanha 50 with Cape (centre), Claydol 50 (100 - 50 from Ram on Baltoy). "
        "Discard: Research (global 1), Copycat, Poke Ball (global 3); Energy: the Water Baltoy spent to retreat. Opponent: Active "
        "Caterpie 40 with Grass (global 6); Bench left Butterfree 130 (its Grass spent retreating on global 6), right Grovyle 80 one "
        "Grass. Hand 3 (global 3) + draw 4, Grovyle 3, Quick-Grow 2; + draw 3, Research 4, Fragrant Forest 3. His move in the review's "
        "order (255-276): Wallace on the centre Carvanha (@2; random evolution: Mega Sharpedo ex 220 with Cape, variant patch), Water to "
        "the left Wailmer (@1), no attack. Caterpie's Quick Growth after his turn is the opponent's, not his move."),
]
