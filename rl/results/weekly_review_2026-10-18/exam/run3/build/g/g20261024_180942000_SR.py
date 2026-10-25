from v2_helpers import P, B
D = 'v2deck_7907f1e146'; G = '20261024_180942000_SR'
FE = 'Feebas B3b 014'; CAPE = 'Elegant Cape B3b 065'; WAL = 'Wallace B3b 068'; CC = 'Copycat B1 225'; IRI = 'Irida A2a 072'
SS = 'Soothing Shore B4 154'; MSH = 'Mega Sharpedo ex B4 035'; MGY = 'Mega Gyarados ex B1 052'; PB = 'Poké Ball P-A 005'
CAS = 'Carvanha B4 034'; CAJ = 'Carvanha P-B 081'; MK = 'Magikarp P-B 014'
KOF = "Team Rocket's Koffing B4a 042"; WEE = "Team Rocket's Weezing ex B4a 043"; ABS = 'Mega Absol ex B1 151'; DN = 'Deceptive Needle B4 148'
OPB = 'Poké Ball A2b 111'; SAB = 'Sabrina A1 225'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_W = "Opponent Team Rocket's Weezing ex printing chosen by HP (140), Ability title (Boiler Smog) and attack title (Confusion Gas); B4a 043, B4a 083 and B4a 092 match"
AMB_A = 'Opponent Mega Absol ex printing chosen by HP (170) and attack title (Darkness Claw); B1 151, B1 262, B1 280, B3 230 and P-B 009 match'
AMB_PB = "Opponent's Poké Ball printing not shown; A2b 111 used (P-A 005 also matches)"
HC = ("the opponent's hand (3) is the number of cards his Copycat drew on global 3; the visible plays of global 2 alone (draw, Poké Ball +1, "
      "Mega Absol ex benched, Deceptive Needle) give 2, so one opponent card is not accounted for in the review")


def _wallace_sharpedo(v):
    v['me']['board'][1].update({'card': MSH, 'hp': 190, 'behind': [CAS]})


POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[CC, SS, IRI, MSH, CAS], disc=[], dene='', board=[B(FE, 30)], ko=0),
  dict(hand_count=3, disc=[], dene='', board=[B(KOF, 60), B(KOF, 60)], ko=0),
  ['Place:Carvanha@1', 'Play:Soothing Shore', 'Play:Copycat', 'Play:Poké Ball', 'Place:Carvanha@2', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's hand (3) is the opening five less the two Koffing (Copycat drew three)",
  draws={2: ['-' + IRI, '-' + MSH, IRI, PB, CC], 3: [CAJ]},
  notes="Global 1 = his 1st turn (he went first). 'Setup, 0-35s': opening five Feebas, Copycat, Soothing Shore, Irida, Mega Sharpedo ex; "
        "Feebas Active, no Bench. Opponent: Team Rocket's Koffing Active and Koffing Bench (60 -> B4a 042) -> 3 in hand. 'Global turn1': "
        "draw Sharp Fang Carvanha (B4 034) -> Copycat, Soothing Shore, Irida, MSh, Carvanha. His move in order: bench Carvanha 38-40 (@1), "
        "Soothing Shore 43, Copycat 47 (shuffles Irida/MSh, draws Irida, Poké Ball, Copycat; lead correction v2), Poké Ball 57 (Aqua Jet "
        "Carvanha P-B 081, 59), bench it 62 (@2), end 63; no Energy (first player). The shipped run matches 'Place:Carvanha@1' (one "
        "Carvanha in hand). check_game's variant puts the Poké Ball's Aqua Jet Carvanha in the hand up front, so at its step 0 two "
        "printings can be placed and the engine wants 'Place:Carvanha@1(Pokemon(B4034Carvanha),1)'; no one label fits both runs (tool "
        "artifact). scratch/b10/vcheck.py with that one variant step overridden applies the variant 4/4."),
P(G, 3, 2, [0, 0],
  dict(hand=[IRI, CC, SS], disc=[CC, PB], dene='', board=[B(FE, 20), B(CAS, 50), B(CAJ, 50)], ko=0),
  dict(hand_count=3, disc=[OPB], dene='', board=[B(KOF, 60, 'D', tool=DN), B(KOF, 60), B(ABS, 170)], ko=0),
  ['Play:Copycat', 'Play:Elegant Cape', 'Tool:Elegant Cape@0', 'Attach:1Water@0 zone', 'Play:Elegant Cape', 'Tool:Elegant Cape@2',
   'Attack:Splash'],
  D, None, stadium={"card": SS, "owner": 0},
  approx=AP + "; " + HC + "; the opponent's Poké Ball printing is not shown (the first listed printing is used); Bench order is the "
            "order benched (the review gives no left/right arrangement)",
  ambiguous=[AMB_A, AMB_PB],
  draws={0: ['-' + IRI, '-' + SS, CAPE, CAPE, MGY]},
  notes="Global 3 = his 2nd turn. Hand after global 1: Irida, Copycat; 'Global turn3' draw the 2nd Soothing Shore 110 -> Irida, Copycat, "
        "Soothing Shore. Board: Feebas 20 (Needle 10 at the end of global 2), Bench Sharp Fang Carvanha (benched first) and Aqua Jet "
        "Carvanha. Discard: Copycat, Poké Ball. Stadium: his Soothing Shore (global 1). Opponent ('Global turn2'): Koffing 60 Active with "
        "1 Darkness and Deceptive Needle; Bench Koffing 60 and Mega Absol ex 170 (benched 76-78); discard Poké Ball. His move in order: "
        "Copycat 114 (shuffles Irida and Soothing Shore; draws two Elegant Capes and Mega Gyarados ex, 'three opponent cards'), Cape on "
        "Feebas 124-126, zone Water to Feebas 138-139, Cape on Aqua Jet Carvanha 141-142 (@2), Splash 146-147 (10 to Koffing)."),
P(G, 5, 3, [0, 1],
  dict(hand=[MGY, MSH], disc=[CC, PB, CC, FE, CAPE], dene='W', board=[B(CAJ, 50, tool=CAPE), B(CAS, 50)], ko=1),
  dict(hand_count=3, disc=[OPB], dene='', board=[B(WEE, 130, 'D', tool=DN, behind=[KOF]), B(KOF, 60), B(ABS, 170, 'D')], ko=0),
  ['Evolve:Mega Sharpedo ex@0', 'Attach:1Water@0 zone', 'Attack:Turbo Shark'],
  D, None, stadium={"card": SS, "owner": 0},
  approx=AP + "; the opponent's hand (3) follows global 3's (3, from his Copycat's draws) with +1 draw and -Weezing ex on global 4; "
            "the opponent's Poké Ball printing is not shown (the first listed printing is used)",
  ambiguous=[AMB_W, AMB_A, AMB_PB],
  notes="Global 5 = his 3rd turn. Hand after global 3: Mega Gyarados ex (both Capes played); 'Global turn5' draw Mega Sharpedo ex 202. "
        "'Global turn4': Feebas KO'd at the end of the turn (Needle, Poison, Burn), opponent +1; Feebas with its Cape and 1 Water to his "
        "discard; Cape Aqua Jet Carvanha promoted (Active), Sharp Fang Carvanha on the Bench. Opponent: Koffing evolved to Team Rocket's "
        "Weezing ex 140 keeping 10 damage (130) with 1 Darkness and Needle; Darkness to benched Mega Absol ex; Bench Koffing 60, Absol "
        "170. Score 0-1. His move in order: evolve Cape Carvanha to Mega Sharpedo ex 204-211 (220), zone Water by 214, Turbo Shark 215-217 "
        "(70 to Weezing; its Water to benched Sharp Fang Carvanha by 219/243)."),
P(G, 7, 4, [0, 1],
  dict(hand=[MGY, WAL], disc=[CC, PB, CC, FE, CAPE], dene='W',
       board=[B(MSH, 120, 'W', tool=CAPE, cond=['Poisoned', 'Confused'], behind=[CAJ]), B(CAS, 50, 'W')], ko=1),
  dict(hand_count=3, disc=[OPB], dene='', board=[B(WEE, 60, 'DD', tool=DN, behind=[KOF]), B(WEE, 140, behind=[KOF]), B(ABS, 170, 'D')], ko=0),
  ['Play:Wallace', 'ChooseRandomEvolutionTarget', 'Attach:1Water@1 zone', 'Retreat:1', 'Attack:Turbo Shark'],
  D, None, stadium={"card": SS, "owner": 0},
  approx=AP + "; the opponent's hand (3) follows global 5's (3) with +1 draw and -Weezing ex on global 6; the opponent's Poké Ball "
            "printing is not shown (the first listed printing is used); Bench order is the order benched",
  ambiguous=[AMB_W, AMB_A, AMB_PB],
  draws={0: []}, vpatch=_wallace_sharpedo,
  notes="Global 7 = his 4th turn. Hand after global 5: Mega Gyarados ex; 'Global turn7' draw Wallace 265. Board ('Global turn6'): Mega "
        "Sharpedo ex 220 -> 160 Confusion Gas -> 150 Needle -> 140 Poison -> 120 Burn; Burn healed by the coin, Poisoned and Confused "
        "remain; Cape, 1 Water, over Aqua Jet Carvanha. Bench: Sharp Fang Carvanha 50 with 1 Water (Turbo Shark's attachment). Opponent: "
        "Active Weezing ex 60 with 2 Darkness and Needle; the 2nd Koffing evolved to Weezing ex 140 on the Bench (Bench slot 1, where "
        "that Koffing was); Absol 170 with 1 Darkness. His move in order: Wallace 268 on benched Carvanha (2nd Mega Sharpedo ex 190, "
        "1 Water, 271-273; the variant sets it), zone Water to the new Mega (2 Water, confirmed by 283), retreat the original Mega "
        "277-281 (cost 0; the fresh Mega comes in), Turbo Shark 284-287 (KO Weezing; its Water to the original Mega, the only Benched "
        "Water Pokemon, so no target label). The review's text gives the attachment before the retreat (the retreat's 277-281 and the "
        "attachment's 'by 283' fit either order), so the text order is used: Attach@1 on the Bench, then Retreat:1. pg_legal_v14 stops at "
        "'hidden random choice (ChooseRandomEvolutionTarget)' and leaves that step unmatched, so check_game reports FIX before its "
        "variant; scratch/b10/vcheck.py runs check_game's own variant."),
P(G, 9, 5, [2, 1],
  dict(hand=[MGY, MK], disc=[CC, PB, CC, FE, CAPE, WAL], dene='W',
       board=[B(MSH, 60, 'WW', tool=CAPE, behind=[CAJ]), B(MSH, 190, 'WW', behind=[CAS])], ko=1),
  dict(hand_count=3, disc=[OPB, WEE, KOF, DN, SAB], dene='DD', board=[B(ABS, 170, 'DD'), B(WEE, 140, behind=[KOF])], ko=1),
  ['Place:Magikarp@2', 'Attach:1Water@2 zone', 'Retreat:1', 'Attack:Turbo Shark', 'Attach:1Water@2 fx'],
  D, None, stadium={"card": SS, "owner": 0},
  approx=AP + "; the opponent's hand (3) follows global 7's (3) with +1 draw and -Sabrina on global 8; the opponent's Poké Ball and "
            "Sabrina printings are not shown (the first listed printings are used)",
  ambiguous=[AMB_W, AMB_A, AMB_PB, "Opponent's Sabrina printing not shown; A1 225 used (A1 272, A4b 338 and A4b 339 also match)"],
  notes="Global 9 = his 5th turn. Hand after global 7: Mega Gyarados ex (Darkness Claw on global 8 found no Supporter: 'Owner hand still "
        "Mega Gyarados ex'); 'Global turn9' draw Magikarp 332. Board: Sabrina on global 8 switched the original Mega (140 after Shore's "
        "heal at the end of global 7) in; Darkness Claw 80 -> 60; Cape, 2 Water, over Aqua Jet Carvanha. Bench: the fresh Mega 190 with "
        "2 Water over Sharp Fang Carvanha. Discard adds Wallace. Opponent: Mega Absol ex 170 Active with 2 Darkness; Bench 2nd Weezing ex "
        "140, no Energy (its Darkness comes on global 10). The KO'd Weezing ex with Koffing, Needle and 2 Darkness, and Sabrina in the "
        "opponent's discard. Score 2-1. His move in order: bench Magikarp 334 (@2), zone Water to Magikarp 336, retreat the original Mega "
        "339-342 (fresh Mega in), Turbo Shark 345-347 (70 to Absol), Energy recipient Magikarp 348-353 (U6)."),
]
