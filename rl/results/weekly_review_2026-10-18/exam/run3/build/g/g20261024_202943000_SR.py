from v2_helpers import P, B
D = 'v2deck_7907f1e146'; G = '20261024_202943000_SR'
CAJ = 'Carvanha P-B 081'; CAS = 'Carvanha B4 034'; FE = 'Feebas B3b 014'; MK = 'Magikarp P-B 014'; MSH = 'Mega Sharpedo ex B4 035'
MGY = 'Mega Gyarados ex B1 052'; CAPE = 'Elegant Cape B3b 065'; WAL = 'Wallace B3b 068'; CAB = 'Cabbie B3 150'; CC = 'Copycat B1 225'
LIS = 'Lisia B1 226'; SS = 'Soothing Shore B4 154'; PB = 'Poké Ball P-A 005'
BUN = 'Buneary A2 137'; LOP = 'Mega Lopunny ex B1a 042'; SER = 'Serena B1a 069'; OCC = 'Copycat B1 225'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_B = 'Opponent Buneary printing chosen by HP (60) only; its attack was not shown (A2 137, B1a 062, B1a 075, B4 223 and P-B 019 have 60 HP)'
AMB_L = 'Opponent Mega Lopunny ex printing chosen by HP (190) and attack title (Rapid Smashers); B1a 042, B1a 079, B1a 085 and B4 228 match'
AMB_SE = "Opponent's Serena printing not shown; B1a 069 used (B1a 082 also matches)"


def _wallace_sharpedo(v):
    # the variant starts before Elegant Cape is attached: Mega Sharpedo ex at its printed 190
    v['me']['board'][0].update({'card': MSH, 'hp': 190, 'behind': [CAJ]})


POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[CAPE, WAL, CAB, MGY, CC], disc=[], dene='', board=[B(CAJ, 50)], ko=0),
  dict(hand_count=4, disc=[SER], dene='', board=[B(BUN, 60), B(BUN, 60)], ko=0),
  ['Play:Wallace', 'ChooseRandomEvolutionTarget', 'Play:Elegant Cape', 'Tool:Elegant Cape@0', 'Attach:1Water@0 zone', 'Attack:Turbo Shark'],
  D, None,
  approx=AP + "; the opponent's hand (4) counts Serena's hidden Mega Evolution Pokémon ex search on global 1 as +1 card; the "
            "opponent's Serena printing is not shown (the first listed printing is used); both Buneary printings are chosen by HP (60) only",
  ambiguous=[AMB_B, AMB_SE],
  draws={0: []}, vpatch=_wallace_sharpedo,
  notes="Global 2 = his 1st turn (he went second). '0-42s, opening and setup': opening five Carvanha (Aqua Jet 10, 50HP -> P-B 081), "
        "Elegant Cape, Wallace, Cabbie, Mega Gyarados ex; Carvanha Active, no Bench. Opponent: Buneary 60 Active and Buneary 60 Bench -> "
        "3 in hand. '43-50s, global1': draw 4, Serena (-1, a random Mega Evolution ex into the hand, +1) -> 4; no Energy, no attack. "
        "'51-82s, global2': draw Copycat -> Cape, Wallace, Cabbie, MGy, Copycat. His move in order: Wallace on Carvanha (Mega Sharpedo "
        "ex from the deck, 59-62; the variant sets it), Cape 63-68 (190 -> 220), zone Water 69.5, Turbo Shark 72-75 (KO Buneary; no "
        "Benched Water Pokemon, 'explicit message'). pg_legal_v14 stops at 'hidden random choice (ChooseRandomEvolutionTarget)' and "
        "leaves that step unmatched; scratch/b10/vcheck.py runs check_game's own variant."),
P(G, 4, 2, [1, 0],
  dict(hand=[CAB, MGY, CC, LIS], disc=[WAL], dene='', board=[B(MSH, 220, 'W', tool=CAPE, behind=[CAJ])], ko=0),
  dict(hand_count=4, disc=[SER, BUN], dene='', board=[B(LOP, 190, 'F', behind=[BUN])], ko=1),
  ['Play:Lisia', 'Place:Feebas@1', 'Place:Carvanha@2', 'Attach:1Water@1 zone', 'Attack:Turbo Shark', 'Attach:1Water@1 fx'],
  D, None,
  approx=AP + "; the opponent's hand (4) is global 2's (4) +1 draw -Mega Lopunny ex on global 3; the opponent's Serena printing is not "
            "shown (the first listed printing is used); the Buneary printings (in the discard and under Mega Lopunny ex) are chosen by "
            "HP (60) only",
  ambiguous=[AMB_B, AMB_L, AMB_SE],
  draws={0: [FE, CAS]},
  notes="Global 4 = his 2nd turn. Hand after global 2: Cabbie, MGy, Copycat; '96-121s, global4' draw Lisia 97-99. Board: Mega Sharpedo ex "
        "220 (Cape) with 1 Water over Carvanha. Discard: Wallace. Opponent '83-95s, global3': the surviving Buneary (promoted) evolves to "
        "Mega Lopunny ex 190, first Fighting; no attack; the KO'd Buneary in the discard; score 1-0. His move in order: Lisia 102-104 "
        "(Feebas 30 and Sharp Fang Carvanha 50), both benched 109-112 (Feebas @1, Carvanha @2, in the order the review names them; "
        "compacted Bench), zone Water to Feebas 113-114, Turbo Shark 116-118 (190 -> 120), its Water to Feebas (119-121: Feebas 2 Water, "
        "Carvanha none) = 'Attach:1Water@1 fx'."),
P(G, 6, 3, [1, 0],
  dict(hand=[CAB, MGY, CC, SS], disc=[WAL, LIS], dene='',
       board=[B(MSH, 130, 'W', tool=CAPE, cond=['Confused'], behind=[CAJ]), B(FE, 30, 'WW'), B(CAS, 50)], ko=0),
  dict(hand_count=3, disc=[SER, BUN, OCC], dene='', board=[B(LOP, 120, 'FF', behind=[BUN])], ko=1),
  ['Play:Soothing Shore', 'Play:Copycat', 'Play:Poké Ball', 'Place:Magikarp@3', 'Retreat:2', 'Attach:1Water@0 zone', 'Attack:Sharp Fang'],
  D, None,
  approx=AP + "; the opponent's hand (3) is the three cards its Copycat drew on global 5 (his three cards then); the opponent's Serena "
            "and Copycat printings are not shown (the first listed printings are used); the Buneary printings are chosen by HP (60) only; "
            "his Copycat's three cards are read as Mega Gyarados ex, Poké Ball and Magikarp, and his one Poké Ball as finding nothing (the "
            "review names two Poké Ball plays, one finding Magikarp and one finding no card, but his list holds one Poké Ball)",
  ambiguous=[AMB_B, AMB_L, AMB_SE, "Opponent's Copycat printing not shown; B1 225 used (B1 270 also matches)"],
  draws={1: ['-' + CAB, '-' + MGY, MGY, PB, MK], 2: []},
  notes="Global 6 = his 3rd turn. Hand after global 4: Cabbie, MGy, Copycat; '157-202s, global6' draw Soothing Shore. Board: Mega Sharpedo "
        "220 -> 130 (Rapid Smashers one head, 90) and Confused, 1 Water, Cape; Bench Feebas 30 with 2 Water, Sharp Fang Carvanha 50. "
        "Discard: Wallace, Lisia. Opponent '122-156s, global5': second Fighting to Mega Lopunny ex, Copycat (draws three, his hand), Rapid "
        "Smashers. His move in order: Soothing Shore 161-162, Copycat 164-167 (shuffles Cabbie and MGy, draws three = the opponent's 3), "
        "Poké Ball 170-178, bench Magikarp 178-180 (@3), retreat 186-191 (Mega Sharpedo, cost 0, Confusion removed, swaps with Sharp "
        "Fang Carvanha @2), zone Water to Carvanha 192-193, Sharp Fang 196-198 (30). Reading fix: the review says Copycat gave 'Mega "
        "Gyarados ex, two Poke Balls and Magikarp', a Poké Ball at 170 'obtains Magikarp' and a 'second Poke Ball' at 174-178 'finds no "
        "eligible card'. His list has ONE Poké Ball and Copycat drew three. The one consistent reading: Copycat drew MGy, Poké Ball and "
        "Magikarp, and the single Poké Ball found nothing (after Magikarp left the deck no Basic was in it: Feebas and Sharp Fang "
        "Carvanha benched, Aqua Jet Carvanha under the Mega) = draws {2: []}."),
]
