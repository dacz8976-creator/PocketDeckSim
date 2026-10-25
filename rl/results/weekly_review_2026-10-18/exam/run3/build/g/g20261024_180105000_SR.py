from v2_helpers import P, B
D = 'v2deck_7907f1e146'; G = '20261024_180105000_SR'
FE = 'Feebas B3b 014'; MIL = 'Milotic ex B3b 015'; CAPE = 'Elegant Cape B3b 065'; WAL = 'Wallace B3b 068'; CC = 'Copycat B1 225'
MSH = 'Mega Sharpedo ex B4 035'; PB = 'Poké Ball P-A 005'; CAS = 'Carvanha B4 034'
CHM = 'Charmander A1 033'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[CAPE, WAL, MIL, CC, CC], disc=[], dene='', board=[B(FE, 30)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(CHM, 60)], ko=0),
  ['Play:Elegant Cape', 'Tool:Elegant Cape@0', 'Play:Copycat', 'Play:Poké Ball', 'Place:Carvanha@1', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand (4) is as the review gives it after the Active was placed",
  ambiguous=['Opponent Charmander printing chosen by HP (60) and attack title (Ember); A1 033, A1 230, A4b 055, A4b 056 and P-A 032 match'],
  draws={2: ['-' + WAL, '-' + MIL, '-' + CC, MSH, PB, WAL, WAL], 3: [CAS]},
  notes="Global 1 = his 1st turn (he went first). 'Opening, selection and setup': opening five Feebas, Elegant Cape, Wallace, Milotic ex, "
        "Copycat; Feebas Active 30HP, Bench empty. Opponent: Charmander 60 (Ember) Active, Bench empty, 'four cards after placing its "
        "Active'. Global1 item 1: draw a second Copycat -> Cape, Wallace, Milotic ex, Copycat, Copycat. His move in order (items 2-5): Cape "
        "to Feebas 62-64, Copycat 66-68 (shuffles Wallace, Milotic ex, Copycat; draws four: Mega Sharpedo ex, Poké Ball, Wallace, Wallace), "
        "Poké Ball 76-79 (finds Carvanha 50 Sharp Fang -> B4 034), Carvanha benched 81-82 at the right Bench slot (compacted Bench: the "
        "engine's lowest empty slot @1), end turn 83-84; no Energy (first player)."),
]
