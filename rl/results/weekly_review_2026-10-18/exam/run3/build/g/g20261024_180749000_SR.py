from v2_helpers import P, B
D = 'v2deck_7907f1e146'; G = '20261024_180749000_SR'
FE = 'Feebas B3b 014'; MIL = 'Milotic ex B3b 015'; CAPE = 'Elegant Cape B3b 065'; WAL = 'Wallace B3b 068'; CC = 'Copycat B1 225'
RAL = 'Ralts B4 071'
AP = "opponent's list unknown; opponent's hand size from the visible plays"


def _wallace_milotic(v):
    # the variant starts before Elegant Cape is attached, so Milotic ex starts at its printed 140
    v['me']['board'][0].update({'card': MIL, 'hp': 140, 'behind': [FE]})


POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[CC, WAL, CAPE, WAL, CC], disc=[], dene='', board=[B(FE, 30)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(RAL, 60)], ko=0),
  ['Play:Elegant Cape', 'Tool:Elegant Cape@0', 'Play:Wallace', 'ChooseRandomEvolutionTarget', 'Ability@0', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand (4) is the opening five less the Active",
  ambiguous=['Opponent Ralts printing chosen by HP (60) and attack title (Lead); B4 071 and B4 167 match'],
  draws={2: []}, vpatch=_wallace_milotic,
  notes="Global 1 = his 1st turn (he went first). Rows 22-34.5: opening five Copycat, Wallace, Elegant Cape, Wallace, Feebas; Feebas 30 sole "
        "Active, no Bench. Opponent: Ralts 60 (Lead) sole Active, empty Bench -> 4 in hand. Row 34.5-39: draw a second Copycat -> Copycat, "
        "Wallace, Cape, Wallace, Copycat (Copycat only inspected, not played). His move in order: Cape to Feebas 39-42.5, Wallace on Feebas "
        "42.5-51.5 (Milotic ex from the deck; 140 -> 170 with Cape), Aqua Charge 51.5-57.5 (1 Water to Milotic), end turn ~56-57. "
        "pg_legal_v14 stops at 'hidden random choice (ChooseRandomEvolutionTarget)' and leaves that forced step unmatched, so check_game "
        "reports FIX before its variant; scratch/b10/vcheck.py runs check_game's own variant (Wallace and ChooseRandomEvolutionTarget "
        "removed, vpatch Milotic ex) to check the rest."),
]
