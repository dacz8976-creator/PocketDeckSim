from v2_helpers import P, B
D = 'v2deck_7907f1e146'; G = '20261024_180350000_SR'
FE = 'Feebas B3b 014'; MIL = 'Milotic ex B3b 015'; CAPE = 'Elegant Cape B3b 065'; WAL = 'Wallace B3b 068'; CC = 'Copycat B1 225'
CAB = 'Cabbie B3 150'; MGY = 'Mega Gyarados ex B1 052'; SS = 'Soothing Shore B4 154'; CAS = 'Carvanha B4 034'
MSH = 'Mega Sharpedo ex B4 035'; MK = 'Magikarp P-B 014'
TED = 'Teddiursa B3b 056'; URS = 'Ursaring B3 132'; GC = 'Giant Cape A2 147'; FF = 'Fragrant Forest B3 153'; MAY = 'May B1 223'
AP = "opponent's list unknown; opponent's hand size from the visible plays"


def _wallace_milotic(v):
    v['me']['board'][0].update({'card': MIL, 'hp': 140, 'behind': [FE]})


POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[WAL, CAB, CC, MGY, SS], disc=[], dene='', board=[B(FE, 30)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(TED, 60)], ko=0),
  ['Play:Wallace', 'ChooseRandomEvolutionTarget', 'Play:Soothing Shore', 'Ability@0', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand (4) is the opening five less the Active",
  draws={0: []}, vpatch=_wallace_milotic,
  notes="Global 1 = his 1st turn (he went first). 'Opening and setup' 26-28s: opening five Feebas, Wallace, Cabbie, Copycat, Mega Gyarados "
        "ex; Feebas 30 Active, no Bench. Opponent: Active Teddiursa 60, no Bench (Teddiursa 60 HP / Charm per 'Result and classification' "
        "-> B3b 056, the only Charm printing). 'Global turn 1' 33-35s: draw Soothing Shore -> Wallace, Cabbie, Copycat, MGy, Soothing "
        "Shore. His move in order: Wallace 38-43 on Feebas (Milotic ex from the deck onto it; the verification variant sets Milotic ex 140 "
        "over Feebas), Soothing Shore 46-49, Aqua Charge 50-54 (one Water to Milotic), no attack, end turn. pg_legal_v14 stops at "
        "'hidden random choice (ChooseRandomEvolutionTarget)' and leaves that forced step unmatched (with or without the label in the "
        "line), so check_game reports FIX before its variant; scratch/b10/vcheck.py runs check_game's own variant (Wallace and its "
        "ChooseRandomEvolutionTarget removed, vpatch Milotic ex) and applies the rest 3/3."),
P(G, 3, 2, [0, 0],
  dict(hand=[CAB, CC, MGY, CAS], disc=[WAL, SS], dene='', board=[B(MIL, 140, 'W', behind=[FE])], ko=0),
  dict(hand_count=3, disc=[MAY], dene='', board=[B(TED, 60), B(TED, 60, 'G')], ko=0),
  ['Place:Carvanha@1', 'Play:Cabbie', 'Play:Soothing Shore', 'Ability@0', 'Attach:1Water@0 zone', 'Attack:Water Pulse'],
  D, None, stadium={"card": FF, "owner": 1},
  approx=AP + "; the opponent's hand (3) counts the hidden Fragrant Forest search on global 2 as +1 card and May as net 0 (2 found, "
            "2 shuffled back); the opponent's May printing is not shown (the first listed printing is used); Cabbie's Stadium is taken "
            "as the 2nd Soothing Shore from his deck (the card text searches the deck), so the 1st Soothing Shore stays in his discard",
  ambiguous=['Opponent May printing not shown; B1 223 used (B1 268 also matches)'],
  draws={1: [SS]},
  notes="Global 3 = his 2nd turn. Hand after global 1: Cabbie, Copycat, MGy; 'Global turn 3' 88-92s draw Sharp Fang Carvanha (-> B4 034). "
        "Board: Milotic ex 140 with 1 Water over Feebas. Discard: Wallace, and Soothing Shore (replaced by the opponent's Fragrant Forest, "
        "'Global turn 2' 61-64s). Opponent, 'Global turn 2': hand 4, draw 5, Fragrant Forest 4, Forest activation +1 hidden 5, May (B1 "
        "223, read from the discard at 89s) 4 net, bench 2nd Teddiursa 3, Grass to the Bench Teddiursa; Active Teddiursa no Energy. "
        "Cross-check: 3 here gives 2 at global 5, which Copycat's two draws confirm. His move in order (88-123s): bench Carvanha at right "
        "(compacted: @1), Cabbie 94-99, Soothing Shore 101-104 (replacing Forest), Aqua Charge 106-109, zone Water to Milotic 111-113, "
        "Water Pulse 114-119 (KO Teddiursa). The review says Cabbie 'returns' Soothing Shore 'from the discard'; Cabbie's text puts a "
        "random Stadium from the DECK into the hand and his list has 2 Soothing Shore, so the build takes the 2nd copy from the deck. "
        "pg_legal_v14 stops at Play:Cabbie as a hidden draw; v2_helpers has no Cabbie chance step, so check_game's variant says 'no "
        "chance step'; scratch/b10/vcheck.py (Cabbie added) applies the rest 5/5."),
P(G, 5, 3, [1, 0],
  dict(hand=[CC, MGY, CAPE], disc=[WAL, SS, CAB], dene='', board=[B(MIL, 100, 'WWW', behind=[FE]), B(CAS, 50)], ko=0),
  dict(hand_count=2, disc=[MAY, FF, TED], dene='', board=[B(URS, 130, 'GG', tool=GC, behind=[TED])], ko=1),
  ['Play:Elegant Cape', 'Tool:Elegant Cape@1', 'Play:Copycat', 'Place:Magikarp@2', 'Evolve:Mega Sharpedo ex@1', 'Attach:1Water@2 zone',
   'Ability@0', 'Attack:Water Pulse'],
  D, None, stadium={"card": SS, "owner": 0},
  approx=AP + "; the opponent's hand (2) follows global 3's count (3), +1 draw, -Ursaring, -Giant Cape, and matches Copycat's two "
            "draws; the opponent's Giant Cape and May printings are not shown (the first listed printings are used); Bench compacted "
            "(Carvanha was benched at the right; Magikarp goes to the lowest empty slot)",
  ambiguous=['Opponent Giant Cape printing not shown; A2 147 used (A4b 320 and A4b 321 also match)',
             'Opponent May printing not shown; B1 223 used (B1 268 also matches)'],
  draws={2: ['-' + MGY, MSH, MK]},
  notes="Global 5 = his 3rd turn. Hand after global 3: Copycat, MGy; 'Global turn 5' 149-150s draw Elegant Cape. Board: Milotic ex 100 "
        "(140 - Raging Claws 40, 'Global turn 4'; Soothing Shore heals only the turn player's Pokemon, so no heal at the end of global 4) "
        "with 3 Water; Carvanha 50 on the Bench. Discard: Wallace, Soothing Shore (1st), Cabbie. Stadium: his Soothing Shore (replayed "
        "global 3). Opponent: Ursaring (Raging Claws -> B3 132) 110 + Giant Cape 20 = 130 undamaged, 2 Grass, over Teddiursa, no Bench; "
        "discard May, Fragrant Forest, the KO'd Teddiursa (no Energy). Score 1-0. His move in order (149-189s): Cape to benched Carvanha "
        "151-154, Copycat 156-163 (shuffles MGy, draws Mega Sharpedo ex and Magikarp), bench Magikarp 165-166 (review: 'left'; "
        "compacted: @2), evolve the right Carvanha (@1) to Mega Sharpedo ex 168-173, zone Water to Magikarp 174-177, Aqua Charge "
        "178-181, Water Pulse 184-189."),
]
