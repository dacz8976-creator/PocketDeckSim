from v2_helpers import P, B
D = 'v2deck_4fa967805c'; G = '20261021_222413000_SR'
CV = 'Carvanha B4 034'; MS = 'Mega Sharpedo ex B4 035'; WL = 'Wailord B1 057'; PR = "Professor's Research P-A 007"
HH = 'Heavy Helmet B1 219'; EC = 'Elegant Cape B3b 065'
# opponent
BU = 'Bulbasaur B1a 001'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[WL, MS, PR, PR, HH], disc=[], dene='', board=[B(CV, 50)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(BU, 60)], ko=0),
  ["Play:Professor's Research", 'Play:Elegant Cape', 'Tool:Elegant Cape@0', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand count (4) is the opening five less the Active Bulbasaur (no Bench at setup, no draw yet)",
  ambiguous=['Opponent Bulbasaur printing: B1a 001 is the only one with HP 60 and Tackle'],
  draws={0: [EC, EC]},
  notes="Global 1 = his 1st turn (he went first). Review '24-35s setup': opening five Carvanha, Wailord, Mega Sharpedo ex, two "
        "Professor's Research; Carvanha 50 Active, empty Bench -> 4 in hand; opponent Bulbasaur 60 Active, empty Bench (4 in hand). "
        "'36-51s, global turn 1': draws Heavy Helmet -> 5. His move in the review's order: Professor's Research (two Elegant Cape), "
        "one Cape on the Active Carvanha; no Energy (first turn), no Bench, no attack; ends the turn holding Wailord, Mega Sharpedo "
        "ex, the 2nd Research, Heavy Helmet and the 2nd Cape."),
]
