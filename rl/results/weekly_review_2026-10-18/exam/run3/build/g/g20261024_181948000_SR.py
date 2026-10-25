from v2_helpers import P, B
D = 'v2deck_7907f1e146'; G = '20261024_181948000_SR'
MK = 'Magikarp P-B 014'; MGY = 'Mega Gyarados ex B1 052'; CAPE = 'Elegant Cape B3b 065'; WAL = 'Wallace B3b 068'; CC = 'Copycat B1 225'
SS = 'Soothing Shore B4 154'; MSH = 'Mega Sharpedo ex B4 035'; MIL = 'Milotic ex B3b 015'; CAB = 'Cabbie B3 150'; CAJ = 'Carvanha P-B 081'
ZAP = "Team Rocket's Zapdos ex B4a 021"; GC = 'Giant Cape A2 147'; FRO = 'Froakie A1 087'; GRE = 'Greninja A1 089'
OCC = 'Copycat B1 225'; OPB = 'Poké Ball A2b 111'; RC = 'Rare Candy A3 144'; HT = 'Hiking Trail B2b 069'; EG = 'Electric Generator B2a 086'
CY = 'Cyrus A2 150'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_Z = ("Opponent Team Rocket's Zapdos ex printing chosen by HP (120) and attack titles (Electro Ball, Thunderclaw); B4a 021, B4a 081 and "
         "B4a 090 match")
AMB_GC = 'Opponent Giant Cape printing not shown; A2 147 used (A4b 320 and A4b 321 also match)'
AMB_CC = "Opponent's Copycat printing not shown; B1 225 used (B1 270 also matches)"
AMB_PB = "Opponent's Poké Ball printing not shown; A2b 111 used (P-A 005 also matches)"
AMB_FR = 'Opponent Froakie (under Greninja) printing chosen by HP (60) only; its attack was not shown'
AMB_GR = ('Opponent Greninja printing chosen by HP (120), Ability title (Water Shuriken) and attack title (Mist Slash); A1 089, A3a 093, '
          'A4b 114, A4b 115, A4b 356 and P-A 019 match')
AMB_RC = "Opponent's Rare Candy printing not shown; A3 144 used (A4b 314, A4b 315 and A4b 379 also match)"


def _wallace_gyarados(v):
    # the variant starts before Elegant Cape is attached: Mega Gyarados ex at its printed 210
    v['me']['board'][0].update({'card': MGY, 'hp': 210, 'behind': [MK]})


POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[CC, MSH, WAL, CAPE, SS], disc=[], dene='', board=[B(MK, 30)], ko=0),
  dict(hand_count=4, disc=[OCC], dene='', board=[B(ZAP, 140, tool=GC)], ko=0),
  ['Play:Elegant Cape', 'Tool:Elegant Cape@0', 'Play:Wallace', 'ChooseRandomEvolutionTarget', 'Play:Soothing Shore',
   'Attach:1Water@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand (4) is the four cards its Copycat drew on global 1 (his four cards then); the opponent's Giant "
            "Cape and Copycat printings are not shown (the first listed printings are used)",
  ambiguous=[AMB_Z, AMB_GC, AMB_CC],
  draws={2: []}, vpatch=_wallace_gyarados,
  notes="Global 2 = his 1st turn (he went second). 'Source-bound deck and opening': opening five Copycat, Mega Sharpedo ex, Wallace, "
        "Elegant Cape, Magikarp; lone Magikarp Active, no Bench. Opponent: lone Team Rocket's Zapdos ex 120. 'Global1': Giant Cape to "
        "Zapdos (140), Copycat draws to match his four cards -> 4; no Energy, no attack. 'Global2': draw Soothing Shore 60-62 -> Copycat, "
        "MSh, Wallace, Cape, Soothing Shore. His move in order: Cape to Magikarp 64-67, Wallace 69-79 (Mega Gyarados ex from the deck onto "
        "Magikarp; 210 + Cape 30 = 240; the variant sets Mega Gyarados ex), Soothing Shore 80-82, zone Water to Gyarados 83-84, end. "
        "pg_legal_v14 stops at 'hidden random choice (ChooseRandomEvolutionTarget)' and leaves that step unmatched, so check_game reports "
        "FIX before its variant; scratch/b10/vcheck.py runs check_game's own variant."),
P(G, 4, 2, [0, 0],
  dict(hand=[CC, MSH, MIL], disc=[WAL], dene='', board=[B(MGY, 240, 'W', tool=CAPE, behind=[MK])], ko=0),
  dict(hand_count=4, disc=[OCC, OPB], dene='', board=[B(ZAP, 140, 'L', tool=GC), B(FRO, 60)], ko=0),
  ['Play:Copycat', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None, stadium={"card": SS, "owner": 0},
  approx=AP + "; the opponent's hand (4) counts global 3's Poké Ball as +1 (Froakie, revealed and benched) and matches his Copycat's "
            "four draws; the opponent's Giant Cape, Copycat and Poké Ball printings are not shown (the first listed printings are used); "
            "Froakie's printing is chosen by HP (60) only",
  ambiguous=[AMB_Z, AMB_GC, AMB_CC, AMB_PB, 'Opponent Benched Froakie printing chosen by HP (60) only; its attack was not shown'],
  draws={0: ['-' + MSH, '-' + MIL, MSH, MSH, CAB, SS]},
  notes="Global 4 = his 2nd turn. Hand after global 2: Copycat, MSh; 'Global4' draw Milotic ex 105 -> Copycat, MSh, Milotic ex. Board: "
        "Mega Gyarados ex 240 with Cape and 1 Water over Magikarp; his Soothing Shore in play; discard Wallace. Opponent 'Global3': draw "
        "5, Poké Ball 4 +1 (Froakie, publicly revealed) 5, bench Froakie 60 -> 4, Lightning to Zapdos. His move in order: Copycat 108-112 "
        "(shuffles MSh and Milotic ex; draws two Mega Sharpedo ex, Cabbie, Soothing Shore), zone Water to Gyarados 118-119, end."),
P(G, 6, 3, [0, 0],
  dict(hand=[MSH, MSH, CAB, SS, CAJ], disc=[WAL, CC, SS], dene='', board=[B(MGY, 160, 'WW', tool=CAPE, behind=[MK])], ko=0),
  dict(hand_count=3, disc=[OCC, OPB, RC], dene='', board=[B(ZAP, 140, 'LW', tool=GC), B(GRE, 120, behind=[FRO])], ko=0),
  ['Place:Carvanha@1', 'Play:Cabbie', 'Play:Soothing Shore', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None, stadium={"card": HT, "owner": 1},
  approx=AP + "; the opponent's hand (3) is Hiking Trail's end-of-turn refill to 3 on global 5; the opponent's Giant Cape, Copycat, "
            "Poké Ball and Rare Candy printings are not shown (the first listed printings are used); Froakie's printing (under "
            "Greninja) is chosen by HP (60) only",
  ambiguous=[AMB_Z, AMB_GC, AMB_CC, AMB_PB, AMB_GR, AMB_FR, AMB_RC],
  draws={1: []},
  notes="Global 6 = his 3rd turn. Hand after global 4: MSh, MSh, Cabbie, Soothing Shore; 'Global6' draw Carvanha 157-158 (50HP Aqua Jet "
        "-> P-B 081). Board: Gyarados 240 -> 220 (Water Shuriken) -> 160 (Electro Ball 40 + 20 Weakness), 2 Water, Cape. Discard: "
        "Wallace, Copycat, and the 1st Soothing Shore (replaced by Hiking Trail on global 5). Opponent 'Global5': draw 5, Rare Candy 4, "
        "Greninja 3 (120, Water Shuriken / Mist Slash, over Froakie), Water to Zapdos (L+W), Hiking Trail 2, Electro Ball, Hiking Trail "
        "refill to 3. His move in order: bench Carvanha 159-160 (@1), Cabbie 162-166 (the game says no card in the deck can be the "
        "target: both Soothing Shores are out of the deck; nothing found), Soothing Shore 167-170 (replacing Hiking Trail), zone Water "
        "to Gyarados 172-174, end (Shore heals Gyarados 160 -> 180). With no Stadium left in his deck pg_legal_v14 does not stop at "
        "Cabbie; draws={1: []} (nothing found) is kept only for a chance-step rule that counts Cabbie."),
P(G, 8, 4, [0, 0],
  dict(hand=[MSH, MSH, WAL], disc=[WAL, CC, SS, CAB], dene='', board=[B(CAJ, 30), B(MGY, 180, 'WWW', tool=CAPE, behind=[MK])], ko=0),
  dict(hand_count=1, disc=[OCC, OPB, RC, HT, EG, CY], dene='', board=[B(ZAP, 140, 'LW', tool=GC), B(GRE, 120, 'W', behind=[FRO]), B(ZAP, 120, 'L')],
       ko=0),
  ['Evolve:Mega Sharpedo ex@0', 'Attach:1Water@0 zone', 'Attack:Turbo Shark'],
  D, None, stadium={"card": SS, "owner": 0},
  approx=AP + "; the opponent's hand (1) follows global 6's (3) with +1 draw, -Zapdos ex, -Electric Generator, -Cyrus on global 7 (no "
            "Hiking Trail refill: Soothing Shore was in play); the opponent's Trainer printings (Copycat, Poké Ball, Rare Candy, "
            "Electric Generator, Cyrus) and Giant Cape are not shown (the first listed printings are used); Froakie's printing (under "
            "Greninja) is chosen by HP (60) only; Bench order is the order benched",
  ambiguous=[AMB_Z, AMB_GC, AMB_CC, AMB_PB, AMB_GR, AMB_FR, AMB_RC,
             "Opponent's Electric Generator and Cyrus printings not shown; B2a 086 and A2 150 used"],
  notes="Global 8 = his 4th turn. Hand after global 6: MSh, MSh; 'Global8' draw Wallace 235-237 -> MSh, MSh, Wallace. Board ('Global7'): "
        "Water Shuriken 20 on benched Carvanha (50 -> 30), then Cyrus switched Carvanha Active and Gyarados (180 after Shore's heal, 3 "
        "Water, Cape) to the Bench. Discard adds Cabbie. Stadium: his Soothing Shore (global 6). Opponent: draw, Water to benched Greninja, "
        "bench 2nd Zapdos ex 120, Electric Generator heads (Lightning to the 2nd Zapdos), Water Shuriken, Cyrus, no attack. Score 0-0. "
        "His move in order: evolve Active Carvanha to Mega Sharpedo ex 245-249 (190 - 20 = 170), zone Water 250-251, Turbo Shark 253-258 "
        "(70 to Zapdos; its Water to benched Gyarados, the only Benched Water Pokemon, so no target label)."),
]
