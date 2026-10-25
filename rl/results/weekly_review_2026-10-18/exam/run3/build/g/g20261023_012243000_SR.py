from v2_helpers import P, B
D = 'v2deck_589bb9927a'; G = '20261023_012243000_SR'
SQ = 'Squirtle P-A 033'; WT = 'Wartortle B1a 018'; EI = 'Eiscue B1 080'; PB = 'Poké Ball P-A 005'
CC = 'Copycat B1 225'; PL = 'Parasol Lady B3 152'; CY = 'Cyrus A2 150'
NM = 'Nidoran♂ A1 169'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[CC, PL, WT, PB, CY], disc=[], dene='', board=[B(EI, 80)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(NM, 60)], ko=0),
  ['Play:Poké Ball', 'Place:Squirtle@1', 'Play:Copycat', 'Place:Eiscue@2', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand (4) is the opening five less the Active Nidoran♂ (no Bench, no draw yet: he went first)",
  ambiguous=["Opponent Nidoran♂ printing chosen by HP (60) and attack title (Peck); A1 169 and A4 226 match"],
  draws={0: [SQ], 2: ['-' + PL, '-' + WT, '-' + CY, WT, EI, CY, PL]},
  notes="Global 1 = his 1st turn (he went first). Setup (25-123s): opening five Copycat, Parasol Lady, Wartortle, Eiscue, Poké Ball; "
        "Eiscue 80 Active, no Bench, so 4 in hand; opponent lone Nidoran♂ 60 (Peck 20), no Bench, no Energy. Turn 1 (123-156s): draw "
        "Cyrus -> 5 cards. His move in time order: Poké Ball 127-130s (Squirtle revealed 131s), Squirtle benched at the RIGHT spot "
        "133-134s (compacted Bench: slot 1), Copycat 136-140s (remaining hand Parasol Lady, Wartortle, Cyrus shuffled away, draws four "
        "= the opponent's four cards: Wartortle, Eiscue, Cyrus, Parasol Lady revealed 142-145s), second Eiscue benched in the MIDDLE "
        "151-154s (compacted: slot 2), end turn; no Energy on the first player's first turn, no attack."),
]
