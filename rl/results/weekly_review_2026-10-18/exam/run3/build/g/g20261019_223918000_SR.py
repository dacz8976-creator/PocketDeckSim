from v2_helpers import P, B
D = 'v2deck_06ee642b71'; G = '20261019_223918000_SR'
DK = 'Darkrai ex A2 110'; KO = "Team Rocket's Koffing B4a 042"; WZ = "Team Rocket's Weezing ex B4a 043"; HO = 'Hoopa ex B4 103'
BA = 'Baltoy A3a 030'; AG = 'Alolan Grimer A3 110'
PR = "Professor's Research P-A 007"; PB = 'Poké Ball P-A 005'; SP = 'Starting Plains B2 154'; DN = 'Deceptive Needle B4 148'
# opponent's cards (printing: the first cards.py lists among those matching every shown fact)
FX = 'Frigibax B2a 034'; OHH = 'Heavy Helmet B1 219'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_FX = 'Opponent Frigibax printing chosen by HP (60) and attack title (Chilly); B2a 034 is the only match'
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[PB, PR, SP, WZ], disc=[], dene='', board=[B(DK, 140), B(KO, 60)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(FX, 60)], ko=0),
  ['Play:Poké Ball', "Play:Professor's Research", 'Place:Baltoy@2', 'Place:Alolan Grimer@3', 'EndTurn'],
  D, None,
  approx=AP,
  ambiguous=[AMB_FX],
  draws={0: [HO], 1: [AG, BA]},
  notes="Global 1 = his 1st turn (he went first; no Energy). '24-38s setup': opening five Darkrai ex, Poke Ball, Professor's Research, "
        "Starting Plains, Team Rocket's Koffing; Darkrai ex Active, Koffing on the right Bench -> hand Poke Ball, Research, Starting "
        "Plains. Opponent: sole Active Frigibax 60, empty Bench; hand 5-1 = 4 (no draw yet). '39-65s owner1/global1': draw Team "
        "Rocket's Weezing ex -> 4 cards. His move in the review's order: Poke Ball ~42-45s (reveals Hoopa ex), Professor's Research "
        "~48-52s (draws Alolan Grimer and Baltoy), Baltoy benched ~54-58s, Grimer benched ~61-63s (compacted Bench: Koffing is slot 1 "
        "here, so Baltoy @2 and Grimer @3), no Energy, no attack, Starting Plains kept, end. Frigibax's printed attack (Chilly, used on "
        "global 2) is on the face-up card; B2a 034 is also the first 60-HP Frigibax cards.py lists."),
P(G, 3, 2, [0, 0],
  dict(hand=[SP, WZ, HO, DN], disc=[PB, PR], dene='', board=[B(DK, 120), B(BA, 60), B(AG, 70), B(KO, 60)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(FX, 60, 'W', tool=OHH)], ko=0),
  ['Play:Deceptive Needle', 'Tool:Deceptive Needle@0', "Evolve:Team Rocket's Weezing ex@3", 'Ability@3', 'Attach:1Darkness@0 zone',
   'EndTurn'],
  D, None,
  approx=AP + "; his Bench order left to right (Baltoy, Grimer, Koffing) from the review's 'Koffing on right Bench' and its listing "
              "'Baltoy60, Grimer70, Weezing140'",
  ambiguous=[AMB_FX],
  notes="Global 3 = his 2nd turn. Hand after global 1: Starting Plains, Weezing ex, Hoopa ex ('Hand remaining ...'); '121-139s "
        "owner2/global3': draw Deceptive Needle -> 4 cards. Discard Poke Ball, Research. Board: Darkrai ex 120 (Chilly 20, global 2); "
        "Bench left to right Baltoy 60, Grimer 70, Koffing 60 (Koffing was set on the right; the review lists 'Darkrai120, Baltoy60, "
        "Grimer70, Weezing140'), so Koffing is slot 3 here. Opponent, '66-117s' and '118-120s': hand 4, draw 5, Heavy Helmet on "
        "Frigibax (-1) 4, one Water attached, Chilly 20. His move in the review's order: Needle ~123-127s to Darkrai (@0), Koffing (@3) "
        "-> Weezing ex ~129-131s, Boiler Smog Yes (Ability@3; Frigibax Poisoned and Burned), Darkness from the zone to Darkrai "
        "~140-146s (Nightmare Aura 20, Frigibax 40), end without attacking."),
]
