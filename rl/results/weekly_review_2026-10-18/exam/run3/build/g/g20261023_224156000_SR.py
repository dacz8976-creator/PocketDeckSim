from v2_helpers import P, B
D = 'v2deck_8561e086a0'; G = '20261023_224156000_SR'
M60 = 'Meowth P-A 012'; M50 = 'Meowth B2 124'; PE = 'Persian A1 197'; TN = 'Type: Null A3a 060'; SV = 'Silvally A3a 061'
SX = 'Snorlax ex A3b 057'; TE = 'Terapagos ex B3a 068'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"
LP = 'Lucky Ice Pop B2 145'
BO = 'Bombirdier B3 115'; NI = 'Nihilego A3a 042'; KO = "Team Rocket's Koffing B4a 042"; WZ = "Team Rocket's Weezing ex B4a 043"
NE = 'Deceptive Needle B4 148'; PBA = 'Poison Barb A3 146'; OPR = "Professor's Research A4b 373"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB = ['Opponent Bombirdier printing chosen by HP (70); B3 115 and B3 234 match',
       'Opponent Nihilego printing chosen by HP (70); A3a 042, A3a 103, A4b 246 and A4b 247 match',
       "Opponent Professor's Research printing in the discard not shown; A4b 373 used (P-A 007 also matches)"]
AMB_WZ = ["Opponent Team Rocket's Weezing ex printing chosen by HP (140), Ability title (Boiler Smog); B4a 043, B4a 083 and B4a 092 match"]


def pop_heads(v):
    # Lucky Ice Pop: heals 20 on the Active Meowth (40 -> 50); coin heads, the Pop goes back to his hand
    v['me']['board'][0]['hp'] = 50
    v['me']['hand'] = list(v['me']['hand']) + [LP]


def pop_tails(v):
    # Lucky Ice Pop: heals 20 on the Active Persian (50 -> 70); coin tails, the Pop goes to the discard
    v['me']['board'][0]['hp'] = 70
    v['me']['discard'] = list(v['me']['discard']) + [LP]


POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[PB, PR, TE, LP], disc=[], dene='', board=[B(M50, 40), B(M60, 60)], ko=0),
  dict(hand_count=2, disc=[OPR], dene='', board=[B(BO, 70, tool=NE), B(NI, 70), B(KO, 60, tool=PBA)], ko=0),
  ['Play:Poké Ball', 'Place:Type: Null@2', "Play:Professor's Research", 'Play:Lucky Ice Pop', 'Attach:1Metal@0 zone',
   "Attack:Feelin' Fine"],
  D, None, ez_now='M', ez_next='G',
  approx=AP + "; his next Energy (Grass) is not named by the review at this turn: it is the Energy he attaches on his next turn "
            "(global 4); the opponent's Professor's Research printing is not shown (first listed printing used); the opponent's "
            "Bench order (Nihilego, Team Rocket's Koffing) is the order the review names them",
  ambiguous=AMB,
  draws={0: [TN], 2: [SV, PE], 3: []}, vpatch=pop_heads,
  notes="Global 2 = his 1st turn (he went second). Opening five both Meowth, Poke Ball, Professor's Research, Terapagos ex; Meowth 50 "
        "(Carefree Steps) Active, Meowth 60 benched -> hand Poke Ball, Research, Terapagos ex; draws Lucky Ice Pop -> 4. Opponent setup "
        "Bombirdier Active, Nihilego and Team Rocket's Koffing benched (5 - 3 = 2); global 1 draw 3, Research (-1 +2) 4, Needle to "
        "Bombirdier 3, Poison Barb to Koffing 2; Needle 10 -> Meowth 40. Move (global 2 section, in order): Poke Ball (Type: Null), "
        "bench it (@2), Research (Silvally, Persian), Lucky Ice Pop heals Meowth 40 -> 50, heads, back to hand (coin patch), Metal to "
        "Active Meowth, Feelin' Fine (draws Poke Ball after the attack)."),
P(G, 4, 2, [0, 1],
  dict(hand=[TE, LP, SV, PE, PB, TE], disc=[PB, PR, M50], dene='M', board=[B(M60, 60), B(TN, 80)], ko=1),
  dict(hand_count=2, disc=[OPR], dene='', board=[B(BO, 70, tool=NE), B(NI, 70), B(WZ, 140, 'D', tool=PBA, behind=[KO])], ko=0),
  ['Play:Poké Ball', 'Place:Type: Null@2', 'Evolve:Persian@0', 'Evolve:Silvally@1', 'Attach:1Grass@1 zone', 'EndTurn'],
  D, None, ez_now='G', ez_next='M',
  approx=AP + "; his next Energy (Metal) is not named by the review at this turn: it is the Energy he attaches on his next turn "
            "(global 6); the opponent's Professor's Research printing is not shown (first listed printing used)",
  ambiguous=AMB + AMB_WZ,
  draws={0: [TN]},
  notes="Global 4 = his 2nd turn. Hand after global 2: Terapagos ex, Lucky Ice Pop (returned), Silvally, Persian, and Poke Ball (Feelin' "
        "Fine draw); draws the 2nd Terapagos ex -> 6. Global 3: Darkness to the benched Koffing, evolved to Team Rocket's Weezing ex "
        "(Poison Barb kept), Boiler Smog poisons and burns Meowth 50; Needle 10 + Poison 20 + Burn 20 KO it (its Metal discarded); "
        "opponent 1 point; Meowth 60 promoted, Type: Null the only Bench Pokemon (@1). Opponent hand 2 + 1 - Weezing ex = 2. Move "
        "(global 4 section): Poke Ball (2nd Type: Null), bench it (@2), Meowth -> Persian, benched Type: Null -> Silvally, Grass to "
        "Silvally, no attack."),
P(G, 6, 3, [0, 1],
  dict(hand=[TE, LP, TE, SX], disc=[PB, PR, M50, PB], dene='M',
       board=[B(PE, 50, behind=[M60]), B(SV, 110, 'G', behind=[TN]), B(TN, 80)], ko=1),
  dict(hand_count=3, disc=[OPR], dene='', board=[B(BO, 70, 'D', tool=NE), B(NI, 70), B(WZ, 140, 'D', tool=PBA, behind=[KO])], ko=0),
  ['Place:Snorlax ex@3', 'Play:Lucky Ice Pop', 'Attach:1Metal@3 zone', 'EndTurn'],
  D, None, ez_now='M', ez_next='D',
  approx=AP + "; his next Energy (Darkness) is not named by the review at this turn: it is the Energy he attaches on his next turn "
            "(global 8); the opponent's Professor's Research printing is not shown (first listed printing used)",
  ambiguous=AMB + AMB_WZ,
  draws={1: []}, vpatch=pop_tails,
  notes="Global 6 = his 3rd turn. Hand after global 4: two Terapagos ex, Lucky Ice Pop; draws Snorlax ex -> 4. Global 5: Darkness to "
        "Active Bombirdier, Dark Cutter 30 (Persian 90 -> 60), Needle 10 -> 50. Opponent hand 2 + 1 = 3 (no card played). Move (global 6 "
        "section, in order): bench Snorlax ex (@3), Lucky Ice Pop heals Persian 50 -> 70, tails, discarded (coin patch), Metal to "
        "Snorlax ex near the turn timer, no attack."),
]
