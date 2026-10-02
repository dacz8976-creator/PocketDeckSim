#!/usr/bin/env python3
"""Dustin's real turns in the five Draft A pause games, as constructed-board positions for km3 (stage 2, Oct 2).
Every position is the start of one of his turns after his draw. Sources: each game's REVIEW.md / COVERAGE.md under
C:\\Users\\dacz8\\OneDrive\\Desktop\\Battle Logs\\Recording_QA\\<stem>_iOS_shark_sol, plus still-frame reads for the hands.
`hand_source`: text = rebuilt from the review (opening hand + named draws - named plays); frame = read from still frames;
elimination = the one card the review's own later plays force.
Writes positions_A.json (the harness input)."""
import json, sys, os

A = dict(carv='Carvanha B4 034', sharp='Mega Sharpedo ex B4 035', vulp='Alolan Vulpix B2 028', nine='Alolan Ninetales ex B2 029',
         lap='Lapras A3 044', misty='Misty A1 220', rs="Professor's Research P-A 007", ball='Poké Ball P-A 005', copy='Copycat B1 225',
         cyrus='Cyrus A2 150', irida='Irida A2a 072', cape='Elegant Cape B3b 065', pop='Lucky Ice Pop B2 145')
O = dict(ogerpon='Teal Mask Ogerpon ex B2 017', sprig='Sprigatito B2a 001', meow='Meowscarada ex B2a 003', leafcape='Leaf Cape A3 147',
         snor='Snorlax B3b 055', skull='Skull Fossil A2 144', ching='Chingling B1 109', amber='Old Amber A1 218', litw='Litwick B1 041',
         shay='Shaymin A2 022', furf='Furfrou B3b 061', sigi='Sigilyph A1a 033', ralts='Ralts A1 130', kirl='Kirlia A1 131',
         gard='Gardevoir A1 132', mew2='Mewtwo ex A1 129', arena='Arena of Antiquity B3 154')


def pk(card, hp=None, energy=(), tools=(), behind=(), new=False):
    d = {"card": card}
    if hp is not None: d["hp"] = hp
    if energy: d["energy"] = list(energy)
    if tools: d["tools"] = list(tools)
    if behind: d["behind"] = list(behind)
    if new: d["new"] = True
    return d


def pos(id, game, his_turn, turn_count, points, me_hand, me_board, opp_board, opp_hand, opp_energy_next, *, me_discard=(), me_discard_energy=(),
        opp_discard_n=0, opp_discard_energy=(), energy_now="Water", stadium=None, effects=(), his=(), hand_source="text", notes="", force=(),
        top=None, flags=None, milestones=()):
    p = {"id": id, "game": game, "his_turn": his_turn, "deck": "A", "turn_count": turn_count, "points": list(points),
         "me": {"hand": list(me_hand), "discard": list(me_discard), "discard_energy": list(me_discard_energy), "board": me_board,
                "energy_now": energy_now, "energy_next": "Water"},
         "opp": {"hand_count": opp_hand, "discard_n": opp_discard_n, "discard_energy": list(opp_discard_energy), "board": opp_board,
                 "energy_next": opp_energy_next},
         "stadium": stadium, "turn_effects": list(effects), "his_plan": list(his), "hand_source": hand_source, "notes": notes, "milestones": list(milestones)}
    if force: p["force"] = list(force)
    if top: p["me"]["top"] = list(top)
    if flags: p["flags"] = flags
    return p


P = []

# ------------------------------------------------------------------ 143309 (won 3-0, went second; opp Psychic: Sigilyph, Ralts line, Mewtwo ex)
G = "143309"
P.append(pos(f"A-{G}-t02", G, 1, 2, (0, 0), [A['nine'], A['nine'], A['rs'], A['copy'], A['cyrus']],
             [pk(A['vulp'], 60)], [pk(O['sigi'], 80), pk(O['ralts'], 60)], 4, "Psychic",
             his=["Play:Professor's Research", "(then: bench Lapras, Water on Vulpix, Gnaw 20)"],
             notes="Opening Vulpix(Active) + 2 Ninetales ex + Research + Copycat; T2 draw Cyrus. Opp hand 4 by bookkeeping."))
P.append(pos(f"A-{G}-t04", G, 2, 4, (0, 0), [A['nine'], A['nine'], A['copy'], A['cyrus'], A['irida'], A['misty']],
             [pk(A['vulp'], 50, ["Water"]), pk(A['lap'], 110)], [pk(O['sigi'], 60, ["Psychic"]), pk(O['kirl'], 80, behind=[O['ralts']])], 5, "Psychic",
             me_discard=[A['rs']],
             his=["Evolve:Alolan Ninetales ex@0", "Play:Misty", "MistyTarget@1", "Attach:1Water@0 zone", "Attack:Binding Snow"],
             notes="Research at T2 drew Lapras + Irida; Lapras benched. Draw Misty."))
P.append(pos(f"A-{G}-t06", G, 3, 6, (1, 0), [A['nine'], A['copy'], A['cyrus'], A['irida'], A['rs']],
             [pk(A['nine'], 140, ["Water", "Water"], behind=[A['vulp']]), pk(A['lap'], 110, ["Water", "Water"])],
             [pk(O['mew2'], 150), pk(O['gard'], 110, ["Psychic"], behind=[O['ralts'], O['kirl']]), pk(O['ralts'], 60)], 2, "Psychic",
             me_discard=[A['rs'], A['misty']], opp_discard_n=3,
             his=["Play:Professor's Research", "(then: Poké Ball, bench Carvanha, Cape on Ninetales, Water on Lapras, Binding Snow 80)"],
             notes="Draw Research (played). Sigilyph KO'd on T4 (point 1). Opp hand 2 by bookkeeping."))
P.append(pos(f"A-{G}-t08", G, 4, 8, (1, 0), [A['nine'], A['copy'], A['cyrus'], A['irida'], A['sharp']],
             [pk(A['nine'], 170, ["Water", "Water"], tools=[A['cape']], behind=[A['vulp']]), pk(A['lap'], 110, ["Water", "Water", "Water"]),
              pk(A['carv'], 50)],
             [pk(O['mew2'], 90), pk(O['gard'], 110, ["Psychic", "Psychic"], behind=[O['ralts'], O['kirl']]), pk(O['kirl'], 80, behind=[O['ralts']])], 1, "Psychic",
             me_discard=[A['rs'], A['misty'], A['rs'], A['ball']], opp_discard_n=4,
             his=["Evolve:Mega Sharpedo ex@2", "Attach:1Water@2 zone", "Attack:Binding Snow"],
             notes="Draw Mega Sharpedo ex. Turbo Shark was reachable only by retreating the Mega (retreat 0) into the Active Spot."))

# ------------------------------------------------------------------ 115323 (lost 2-3, went first; opp Fighting: Snorlax, Skull Fossil -> Rampardos, Arena of Antiquity)
G = "115323"
P.append(pos(f"A-{G}-t01", G, 1, 1, (0, 0), [A['cape'], A['copy'], A['misty'], A['misty'], A['ball']],
             [pk(A['lap'], 110)], [pk(O['snor'], 130)], 5, "Fighting", energy_now=None,
             his=["Play:Poké Ball", "(then: bench Carvanha, Cape on Carvanha, Misty: no heads)"],
             notes="Opening hand Lapras(Active) + Cape + Copycat + 2 Misty; T1 draw Poké Ball. First player: no Energy."))
P.append(pos(f"A-{G}-t03", G, 2, 3, (0, 0), [A['copy'], A['misty'], A['irida']],
             [pk(A['lap'], 110), pk(A['carv'], 50, tools=[A['cape']])], [pk(O['snor'], 130), pk(O['snor'], 130, ["Fighting"])], 4, "Fighting",
             me_discard=[A['ball'], A['misty']], opp_discard_n=3, stadium={"card": O['arena'], "owner": 1},
             his=["Play:Misty", "MistyTarget@0", "Attach:1Water@0 zone"],
             notes="Draw Irida. Opp played Arena of Antiquity on T2 (Snorlax's Massive Body bars Stadiums from my hand)."))
P.append(pos(f"A-{G}-t05", G, 3, 5, (0, 0), [A['copy'], A['irida'], A['carv']],
             [pk(A['lap'], 40, ["Water", "Water"]), pk(A['carv'], 50, tools=[A['cape']])],
             [pk(O['snor'], 130, ["Fighting"]), pk(O['snor'], 130, ["Fighting"]), pk(O['skull'], 40)], 3, "Fighting",
             me_discard=[A['ball'], A['misty'], A['misty']], opp_discard_n=4, stadium={"card": O['arena'], "owner": 1},
             his=["Place:Carvanha@2", "Play:Copycat", "(then: bench Vulpix, evolve the caped Carvanha, retreat Lapras, Water, Turbo Shark)"],
             notes="Draw the second Carvanha. Opp Barry + Mega Punch took Lapras to 40 on T4. Opp hand 3 = what his Copycat drew."))
P.append(pos(f"A-{G}-t07", G, 4, 7, (0, 0), [A['cyrus'], A['irida']],
             [pk(A['sharp'], 220, ["Water"], tools=[A['cape']], behind=[A['carv']]), pk(A['lap'], 40), pk(A['carv'], 50), pk(A['vulp'], 60, ["Water"])],
             [pk(O['snor'], 130, ["Fighting", "Fighting"]), pk(O['snor'], 130), pk(O['skull'], 40)], 3, "Fighting",
             me_discard=[A['ball'], A['misty'], A['misty'], A['copy']], me_discard_energy=["Water", "Water"], opp_discard_n=5,
             stadium={"card": O['arena'], "owner": 1},
             his=["Attach:1Water@1 zone", "Attack:Turbo Shark", "Attach:1Water@1 fx"],
             force=["Attach:1Water@1 zone", "Attack:Turbo Shark"],
             notes="Draw Irida (shuffled away by Copycat on T5, drawn again). Opp Penny'd the damaged Snorlax back to hand on T6. "
                   "Turbo Shark's Bench target: Lapras (his pick), Carvanha or Vulpix."))
# mid-turn: the same turn T5 after the Copycat resolved (Sharpedo, Vulpix, Cyrus drawn), to ask the Turbo Shark question
P.append(pos(f"A-{G}-t05b", G, 3, 5, (0, 0), [A['sharp'], A['vulp'], A['cyrus']],
             [pk(A['lap'], 40, ["Water", "Water"]), pk(A['carv'], 50, tools=[A['cape']]), pk(A['carv'], 50, new=True)],
             [pk(O['snor'], 130, ["Fighting"]), pk(O['snor'], 130, ["Fighting"]), pk(O['skull'], 40)], 3, "Fighting",
             me_discard=[A['ball'], A['misty'], A['misty'], A['copy']], opp_discard_n=4, stadium={"card": O['arena'], "owner": 1},
             flags={"has_played_support": True},
             his=["Place:Alolan Vulpix@3", "Evolve:Mega Sharpedo ex@1", "Retreat:1", "Attach:1Water@0 zone", "Attack:Turbo Shark", "Attach:1Water@3 fx"],
             force=["Place:Alolan Vulpix@3", "Evolve:Mega Sharpedo ex@1", "Retreat:1", "Attach:1Water@0 zone", "Attack:Turbo Shark"],
             notes="MID-TURN position: turn 5 after the second Carvanha was benched and Copycat drew Sharpedo, Vulpix, Cyrus. Turbo Shark's Bench target: "
                   "Lapras (0 Energy after the retreat), the second Carvanha, or Vulpix (his pick)."))

# ------------------------------------------------------------------ 143837 (won by concession 2-1, went first; opp Grass: Ogerpon ex, Meowscarada ex)
G = "143837"
P.append(pos(f"A-{G}-t01", G, 1, 1, (0, 0), [A['rs'], A['ball'], A['misty'], A['sharp'], A['cape']],
             [pk(A['lap'], 110)], [pk(O['ogerpon'], 130)], 5, "Grass", energy_now=None, hand_source="frame",
             his=["Play:Poké Ball", "(then: bench Vulpix, Misty one head)"],
             notes="Hand read from frames 00010/00011 (Research, Poké Ball, Misty, a Mega Sharpedo ex, and the drawn Elegant Cape)."))
P.append(pos(f"A-{G}-t03", G, 2, 3, (0, 0), [A['rs'], A['sharp'], A['cape'], A['pop']],
             [pk(A['lap'], 110, ["Water"]), pk(A['vulp'], 60)], [pk(O['ogerpon'], 130, ["Grass"]), pk(O['sprig'], 60)], 6, "Grass",
             me_discard=[A['ball'], A['misty']], opp_discard_n=1, hand_source="frame",
             his=["Play:Professor's Research", "(then: evolve Vulpix, Cape on Ninetales, Water on Lapras)"],
             notes="Draw Lucky Ice Pop. Hand read from frames 00023 and native t0100."))
P.append(pos(f"A-{G}-t05", G, 3, 5, (0, 0), [A['sharp'], A['pop'], A['copy'], A['ball']],
             [pk(A['lap'], 110, ["Water", "Water"]), pk(A['nine'], 180, tools=[A['cape']], behind=[A['vulp']])],
             [pk(O['meow'], 190, ["Grass"], tools=[O['leafcape']], behind=[O['sprig']]), pk(O['ogerpon'], 130)], 2, "Grass",
             me_discard=[A['ball'], A['misty'], A['rs']], opp_discard_n=3, opp_discard_energy=["Grass"], hand_source="elimination",
             effects=[{"turn": 5, "effect": {"DelayedSpotDamage": {"source_player": 1, "target_player": 0, "target_in_play_idx": 0, "amount": 70, "knock_out": False}}}],
             his=["Play:Poké Ball", "(then: bench Carvanha, Water on Lapras, Surf)"],
             notes="The turn-5 draw is the Poké Ball he plays (nothing else in hand could be it). Flower Trick's mark on the Active Spot (70 at the end of this turn) is set."))
P.append(pos(f"A-{G}-t07", G, 4, 7, (0, 1), [A['sharp'], A['pop'], A['copy'], A['misty']],
             [pk(A['carv'], 50), pk(A['nine'], 180, tools=[A['cape']], behind=[A['vulp']])],
             [pk(O['meow'], 120, ["Grass", "Grass"], tools=[O['leafcape']], behind=[O['sprig']]), pk(O['ogerpon'], 130)], 3, "Grass",
             me_discard=[A['ball'], A['misty'], A['rs'], A['ball'], A['lap']], me_discard_energy=["Water", "Water", "Water"],
             opp_discard_n=3, opp_discard_energy=["Grass"], hand_source="elimination",
             his=["Evolve:Mega Sharpedo ex@0", "Attach:1Water@0 zone", "Play:Copycat", "(then: Turbo Shark, Water to Ninetales)"],
             notes="Lapras was KO'd on T6 (Flower Trick 70 + Solar Beam 80); Carvanha promoted. Draw Misty."))

# ------------------------------------------------------------------ 114458 (won 3-2, went second; opp Fire/Psychic: Chingling, Old Amber, Litwick) -- T2 only is fully determined
G = "114458"
P.append(pos(f"A-{G}-t02", G, 1, 2, (0, 0), [A['sharp'], A['copy'], A['pop'], A['nine'], A['rs']],
             [pk(A['vulp'], 50)], [pk(O['ching'], 30), pk(O['amber'], 40), pk(O['litw'], 50)], 3, "Fire",
             opp_discard_n=1, effects=[{"turn": 2, "effect": "NoItemCards"}],
             his=["Play:Professor's Research", "(then: Water on Vulpix, Gnaw 20)"],
             notes="Opening Vulpix(Active) + Sharpedo + Copycat + Ice Pop + Ninetales; T2 draw Research. Chingling's Jingly Noise item-locks this turn."))

# ------------------------------------------------------------------ 132311 (won on a timeout 2-0, went first; opp Grass/Fighting: Shaymin, Furfrou, Flygon ex) -- T1 only is fully determined
G = "132311"
P.append(pos(f"A-{G}-t01", G, 1, 1, (0, 0), [A['sharp'], A['pop'], A['ball'], A['rs'], A['cyrus']],
             [pk(A['carv'], 50)], [pk(O['shay'], 60)], 5, "Fighting", energy_now=None,
             his=["Play:Poké Ball", "(then: bench Carvanha, Research)"],
             notes="Opening Carvanha(Active) + Sharpedo + Ice Pop + Poké Ball + Research; T1 draw Cyrus."))

# ---- 114458 turns 4, 6, 8: hands read from stills (helper, Oct 2): T4 7 cards incl. Irida + Poké Ball (Research's draws) and the drawn Sharpedo #2
O['aero'] = 'Aerodactyl A1 210'; O['chand'] = 'Chandelure B1 043'
G = "114458"
P.append(pos(f"A-{G}-t04", G, 2, 4, (0, 0), [A['sharp'], A['copy'], A['pop'], A['nine'], A['irida'], A['ball'], A['sharp']],
             [pk(A['vulp'], 40, ["Water"])],
             [pk(O['ching'], 10), pk(O['aero'], 100, ["Fire"], behind=[O['amber']]), pk(O['litw'], 50)], 4, "Fire",
             me_discard=[A['rs']], opp_discard_n=2, effects=[{"turn": 4, "effect": "NoItemCards"}], hand_source="frame",
             his=["Evolve:Alolan Ninetales ex@0", "Attach:1Water@0 zone", "Play:Copycat", "(then: bench Lapras, Binding Snow 80)"],
             notes="Hand read from stills: Research (T2) drew Irida + Poké Ball; the T4 draw is the second Mega Sharpedo. Item lock again (Jingly Noise on T3). "
                   "Opp hand 4 = what his Copycat drew."))
P.append(pos(f"A-{G}-t06", G, 3, 6, (1, 0), [A['sharp'], A['misty'], A['ball'], A['nine']],
             [pk(A['nine'], 130, ["Water", "Water"], behind=[A['vulp']]), pk(A['lap'], 110)],
             [pk(O['aero'], 100, ["Fire"], behind=[O['amber']]), pk(O['chand'], 140, ["Fire"], behind=[O['litw']]), pk(O['ching'], 30), pk(O['amber'], 40)], 2, "Fire",
             me_discard=[A['rs'], A['copy']], opp_discard_n=5, hand_source="frame",
             his=["Play:Poké Ball", "(then: bench Vulpix, Misty on Lapras four heads, Water on Vulpix, Binding Snow 80)"],
             notes="Draw: a second Alolan Ninetales ex (pink art) read from stills. Opp hand 2 by a visual count of card backs."))
P.append(pos(f"A-{G}-t08", G, 4, 8, (1, 0), [A['sharp'], A['nine'], A['misty']],
             [pk(A['nine'], 50, ["Water", "Water"], behind=[A['vulp']]), pk(A['lap'], 110, ["Water", "Water", "Water", "Water"]), pk(A['vulp'], 60, ["Water"])],
             [pk(O['chand'], 140, ["Fire", "Fire"], behind=[O['litw']]), pk(O['aero'], 20, behind=[O['amber']]), pk(O['ching'], 30), pk(O['amber'], 40)], 3, "Fire",
             me_discard=[A['rs'], A['copy'], A['ball'], A['misty'], A['irida']], opp_discard_n=5, opp_discard_energy=["Fire"], hand_source="frame",
             his=["Evolve:Alolan Ninetales ex@2", "Play:Misty", "MistyTarget@?", "Attach:1Water@2 zone", "Attack:Binding Snow"],
             notes="Draw: the second Misty. Irida was milled by Slow Sear on the opponent's T7. Misty's target was not preserved in the review (MistyTarget@?)."))

# ---- 132311 turns 3, 5, 7 (T1 above): hands read from stills (helper, Oct 2); Research on T1 drew Alolan Ninetales ex + Misty
G = "132311"
P.append(pos(f"A-{G}-t03", G, 2, 3, (0, 0), [A['sharp'], A['pop'], A['cyrus'], A['nine'], A['misty'], A['irida']],
             [pk(A['carv'], 50), pk(A['carv'], 50)], [pk(O['furf'], 70), pk(O['shay'], 60)], 5, "Fighting",
             me_discard=[A['ball'], A['rs']], opp_discard_n=1, opp_discard_energy=["Fighting"], hand_source="frame",
             his=["Evolve:Mega Sharpedo ex@0", "Attach:1Water@0 zone", "Attack:Turbo Shark", "Attach:1Water@1 fx"],
             force=["Evolve:Mega Sharpedo ex@0", "Attach:1Water@0 zone", "Attack:Turbo Shark"],
             notes="Draw Irida. Opp Furfrou's Fur Coat takes 20 off attacks. The Bench holds only one Water Pokémon, so Turbo Shark has no real target choice here."))
P.append(pos(f"A-{G}-t05", G, 3, 5, (0, 0), [A['pop'], A['cyrus'], A['nine'], A['misty'], A['irida'], A['sharp']],
             [pk(A['sharp'], 130, ["Water"], behind=[A['carv']]), pk(A['carv'], 50, ["Water"])],
             [pk(O['furf'], 70, ["Grass"]), pk(O['shay'], 60)], 5, "Fighting",
             me_discard=[A['ball'], A['rs']], opp_discard_n=2, opp_discard_energy=["Fighting"], hand_source="frame",
             his=["Evolve:Mega Sharpedo ex@1", "Play:Lucky Ice Pop", "Play:Lucky Ice Pop", "Attach:1Water@0 zone", "Attack:Turbo Shark", "Attach:1Water@1 fx"],
             notes="Draw: the second Mega Sharpedo ex (probable, by card count). Opp healed Furfrou back to 70 with Ice Pop (twice) and Shaymin."))
P.append(pos(f"A-{G}-t07", G, 4, 7, (0, 0), [A['cyrus'], A['nine'], A['misty'], A['irida'], A['rs']],
             [pk(A['sharp'], 140, ["Water", "Water"], behind=[A['carv']]), pk(A['sharp'], 190, ["Water", "Water"], behind=[A['carv']])],
             [pk(O['furf'], 30, ["Grass"]), pk(O['shay'], 60, ["Fighting"])], 5, "Fighting",
             me_discard=[A['ball'], A['rs'], A['pop']], opp_discard_n=2, opp_discard_energy=["Fighting"], stadium={"card": "Rainbow Cave B4 155", "owner": 1},
             hand_source="frame",
             his=["Play:Professor's Research", "(then: Poké Ball, bench Vulpix, Water on Vulpix, free retreat to the fresh Mega, Turbo Shark KOs Furfrou, Water to Vulpix)"],
             notes="Draw Professor's Research (alternate art). It drew Poké Ball + Alolan Vulpix. Opp played Rainbow Cave on T6."))
# mid-turn: T7 after Research + Poké Ball (hand: Cyrus, Ninetales ex, Misty, Irida, two Vulpix), for the Turbo Shark target question
P.append(pos(f"A-{G}-t07b", G, 4, 7, (0, 0), [A['cyrus'], A['nine'], A['misty'], A['irida'], A['vulp'], A['vulp']],
             [pk(A['sharp'], 140, ["Water", "Water"], behind=[A['carv']]), pk(A['sharp'], 190, ["Water", "Water"], behind=[A['carv']])],
             [pk(O['furf'], 30, ["Grass"]), pk(O['shay'], 60, ["Fighting"])], 5, "Fighting",
             me_discard=[A['ball'], A['rs'], A['pop'], A['rs'], A['ball']], opp_discard_n=2, opp_discard_energy=["Fighting"],
             stadium={"card": "Rainbow Cave B4 155", "owner": 1}, flags={"has_played_support": True}, hand_source="frame",
             his=["Place:Alolan Vulpix@2", "Attach:1Water@2 zone", "Retreat:1", "Attack:Turbo Shark", "Attach:1Water@2 fx"],
             force=["Place:Alolan Vulpix@2", "Attach:1Water@2 zone", "Retreat:1", "Attack:Turbo Shark"],
             notes="MID-TURN position: turn 7 after Research and Poké Ball. Turbo Shark's Bench target: the damaged Mega (2 Water) or the new Vulpix (1 Water, his pick)."))

# ======================================================================== his turns 5-7 (hands: expected from the review's bookkeeping, checked by still frames)
O['rowlet'] = 'Rowlet A3 010'; O['ramp'] = 'Rampardos A2 089'; O['fragrant'] = 'Fragrant Forest B3 153'; O['flygon'] = 'Flygon ex B3 126'; O['trap'] = 'Trapinch B3 076'
W3 = ["Water", "Water", "Water"]

# ---- 143837 (first, won 2-1 by concession)
G = "143837"
FF = {"card": O['fragrant'], "owner": 1}
P.append(pos(f"A-{G}-t09", G, 5, 9, (0, 1), [A['irida'], A['nine'], A['cyrus'], A['pop']],
             [pk(A['sharp'], 110, ["Water"], behind=[A['carv']]), pk(A['nine'], 180, ["Water"], tools=[A['cape']], behind=[A['vulp']])],
             [pk(O['meow'], 50, ["Grass", "Grass"], tools=[O['leafcape']], behind=[O['sprig']]), pk(O['ogerpon'], 130, ["Grass"]), pk(O['sprig'], 60)], 2, "Grass",
             me_discard=[A['ball'], A['misty'], A['rs'], A['ball'], A['lap'], A['copy']], me_discard_energy=W3, opp_discard_n=4, opp_discard_energy=["Grass"],
             stadium=FF, hand_source="frame",
             his=["Play:Lucky Ice Pop", "Play:Lucky Ice Pop", "Play:Lucky Ice Pop", "Attach:1Water@1 zone", "Retreat:1", "Attack:Binding Snow"],
             milestones=["preparing an attacker", "managing a sacrifice"],
             notes="Draw Lucky Ice Pop. He heals the Mega Sharpedo ex (a 3-point liability) 110 -> 170 with three Ice Pops (heads, heads, tails), arms Ninetales with the turn's Water, retreats the Mega into it and KOs the 50-HP Meowscarada ex with Binding Snow."))
P.append(pos(f"A-{G}-t11", G, 6, 11, (2, 1), [A['irida'], A['nine'], A['cyrus'], A['misty']],
             [pk(A['nine'], 180, ["Water", "Water"], tools=[A['cape']], behind=[A['vulp']]), pk(A['sharp'], 170, ["Water"], behind=[A['carv']])],
             [pk(O['ogerpon'], 130, ["Grass"]), pk(O['sprig'], 60, ["Grass"])], 3, "Grass",
             me_discard=[A['ball'], A['misty'], A['rs'], A['ball'], A['lap'], A['copy'], A['pop']], me_discard_energy=W3, opp_discard_n=7, opp_discard_energy=["Grass"] * 3,
             stadium=FF, hand_source="frame",
             his=["Attack:Binding Snow"], milestones=[],
             notes="Draw Misty (kept). He attacks with Binding Snow and does not attach the turn's Water at all (the review sees no attachment)."))
P.append(pos(f"A-{G}-t13", G, 7, 13, (2, 1), [A['irida'], A['nine'], A['cyrus'], A['misty'], A['sharp']],
             [pk(A['nine'], 180, ["Water", "Water"], tools=[A['cape']], behind=[A['vulp']]), pk(A['sharp'], 170, ["Water"], behind=[A['carv']])],
             [pk(O['sprig'], 90, ["Grass", "Grass"], tools=[O['leafcape']]), pk(O['ogerpon'], 50)], 3, "Grass",
             me_discard=[A['ball'], A['misty'], A['rs'], A['ball'], A['lap'], A['copy'], A['pop']], me_discard_energy=W3, opp_discard_n=7, opp_discard_energy=["Grass"] * 4,
             stadium=FF, hand_source="frame",
             his=["Play:Cyrus", "Activate:1@1"], milestones=["recognising an immediate win"],
             notes="Draw Mega Sharpedo ex. He plays Cyrus to bring the damaged benched Ogerpon ex (50 HP) Active; Binding Snow would then KO it for 2 points (2 -> 4 wins the game). The opponent conceded after Cyrus."))

# ---- 114458 (second, won 3-2)
G = "114458"
P.append(pos(f"A-{G}-t10", G, 5, 10, (1, 2), [A['sharp'], A['cape']],
             [pk(A['lap'], 110, ["Water"] * 4), pk(A['nine'], 150, ["Water", "Water"], behind=[A['vulp']])],
             [pk(O['chand'], 40, ["Fire", "Fire"], behind=[O['litw']]), pk(O['aero'], 20, ["Fire"], behind=[O['amber']]), pk(O['ching'], 30), pk(O['amber'], 40)], 4, "Fire",
             me_discard=[A['rs'], A['copy'], A['ball'], A['misty'], A['misty'], A['irida'], A['pop'], A['nine'], A['vulp']], me_discard_energy=["Water", "Water"], opp_discard_n=5,
             hand_source="frame",
             his=["Tool:Elegant Cape@1", "Attack:Surf"], milestones=["adapting when the plan fails"],
             notes="His first Ninetales ex was KO'd by Heat Blast (2 points to the opponent); the four-Water Lapras (Misty's four heads) was promoted. Cape on the second Ninetales, Surf (70 + Water weakness) KOs the 40-HP Chandelure."))
P.append(pos(f"A-{G}-t12", G, 6, 12, (2, 2), [A['sharp'], A['rs']],
             [pk(A['nine'], 180, ["Water", "Water"], tools=[A['cape']], behind=[A['vulp']])],
             [pk(O['aero'], 20, ["Fire", "Fire"], behind=[O['amber']]), pk(O['ching'], 30), pk(O['amber'], 40), pk(O['litw'], 50)], 3, "Fire",
             me_discard=[A['rs'], A['copy'], A['ball'], A['misty'], A['misty'], A['irida'], A['pop'], A['nine'], A['vulp']], opp_discard_n=6, hand_source="frame",
             his=["Attack:Binding Snow"], milestones=["recognising an immediate win"],
             notes="Will + Primal Wingbeat shuffled his Lapras away; the second Ninetales ex (180 HP, two Water) was promoted. Draw Research. Binding Snow KOs the 20-HP Aerodactyl: the third point, the game."))

# ---- 115323 (first, lost 2-3)
G = "115323"
AR = {"card": O['arena'], "owner": 1}
P.append(pos(f"A-{G}-t09", G, 5, 9, (0, 0), [A['cyrus'], A['irida'], A['pop']],
             [pk(A['sharp'], 150, ["Water"], tools=[A['cape']], behind=[A['carv']]), pk(A['lap'], 40, ["Water", "Water"]), pk(A['carv'], 50), pk(A['vulp'], 60, ["Water"])],
             [pk(O['snor'], 60, ["Fighting"] * 3), pk(O['snor'], 130), pk(O['ramp'], 150, behind=[O['skull']])], 2, "Fighting",
             me_discard=[A['ball'], A['misty'], A['misty'], A['copy']], me_discard_energy=["Water", "Water"], opp_discard_n=6, opp_discard_energy=["Fighting"],
             stadium=AR, hand_source="frame",
             his=["Play:Irida", "Play:Lucky Ice Pop", "Play:Lucky Ice Pop", "Retreat:1", "Attach:1Water@0 zone", "Attack:Surf"],
             milestones=["managing a sacrifice", "preparing an attacker"],
             notes="Draw Lucky Ice Pop. Irida and two Ice Pops restore the Mega Sharpedo ex (a 3-point liability) 150 -> 220 and Lapras 40 -> 80; he retreats the Mega (free) into the three-Energy-ready Lapras and Surf KOs the 60-HP Snorlax."))
P.append(pos(f"A-{G}-t11", G, 6, 11, (1, 1), [A['cyrus'], A['vulp']],
             [pk(A['sharp'], 220, ["Water"], tools=[A['cape']], behind=[A['carv']]), pk(A['carv'], 50), pk(A['vulp'], 60, ["Water"])],
             [pk(O['ramp'], 100, ["Fighting"], behind=[O['skull']]), pk(O['snor'], 130), pk(O['rowlet'], 60)], 2, "Fighting",
             me_discard=[A['ball'], A['misty'], A['misty'], A['copy'], A['irida'], A['pop'], A['lap']], me_discard_energy=["Water"] * 5, opp_discard_n=7, opp_discard_energy=["Fighting"] * 4,
             stadium=AR, hand_source="frame",
             his=["Place:Alolan Vulpix@3", "Attach:1Water@3 zone", "Attack:Turbo Shark", "Attach:1Water@3 fx"],
             force=["Place:Alolan Vulpix@3", "Attach:1Water@3 zone", "Attack:Turbo Shark"],
             milestones=["adapting when the plan fails", "preparing an attacker"],
             notes="Head Smash (130 + Arena's 20 only against ex) KO'd the 80-HP Lapras; the Mega Sharpedo ex was promoted at 220 HP. Draw Vulpix: bench it, give it the turn's Water, Turbo Shark (70) hits Rampardos 100 -> 30 and sends the second Water to the new Vulpix."))
P.append(pos(f"A-{G}-t13", G, 7, 13, (1, 1), [A['cyrus'], A['nine']],
             [pk(A['sharp'], 70, ["Water"], tools=[A['cape']], behind=[A['carv']]), pk(A['carv'], 50), pk(A['vulp'], 60, ["Water"]), pk(A['vulp'], 60, ["Water", "Water"])],
             [pk(O['ramp'], 30, ["Fighting"], behind=[O['skull']]), pk(O['snor'], 130), pk(O['rowlet'], 60), pk(O['skull'], 40, ["Fighting"])], 2, "Fighting",
             me_discard=[A['ball'], A['misty'], A['misty'], A['copy'], A['irida'], A['pop'], A['lap']], me_discard_energy=["Water"] * 5, opp_discard_n=7, opp_discard_energy=["Fighting"] * 4,
             stadium=AR, hand_source="frame",
             his=["Evolve:Alolan Ninetales ex@3", "Attach:1Water@2 zone", "Retreat:3", "Attack:Binding Snow"],
             milestones=["managing a sacrifice"],
             notes="Draw Alolan Ninetales ex. The Mega Sharpedo ex (a 3-point liability) is at 70 HP in front of a Rampardos that hits for 150; he evolves the newly benched Vulpix, retreats the Mega into the Ninetales (2 points) and Binding Snow KOs the 30-HP Rampardos (2-1). The next opponent turn Head Smash KO'd the Ninetales for the game."))

# ---- 132311 (first, won 2-0 on the opponent's timeout)
G = "132311"
RC = {"card": "Rainbow Cave B4 155", "owner": 1}
P.append(pos(f"A-{G}-t09", G, 5, 9, (1, 0), [A['cyrus'], A['nine'], A['misty'], A['irida'], A['vulp'], A['copy']],
             [pk(A['sharp'], 190, ["Water", "Water"], behind=[A['carv']]), pk(A['sharp'], 140, ["Water", "Water"], behind=[A['carv']]), pk(A['vulp'], 60, ["Water", "Water"])],
             [pk(O['shay'], 60, ["Fighting"]), pk(O['trap'], 60, ["Fighting"])], 4, "Fighting",
             me_discard=[A['ball'], A['rs'], A['pop'], A['rs'], A['ball']], opp_discard_n=4, opp_discard_energy=["Fighting", "Grass"], stadium=RC, hand_source="frame",
             his=["Evolve:Alolan Ninetales ex@2", "Attach:1Water@2 zone", "Retreat:2", "Attack:Binding Snow"],
             milestones=["preparing an attacker"],
             notes="Draw Copycat (kept). After Turbo Shark's Water the Vulpix holds two Water; he evolves it, gives it a third, retreats the Mega into it and Binding Snow KOs the 60-HP Shaymin (2-0) while starting the Active-attachment block before the Flygon ex appears."))
P.append(pos(f"A-{G}-t11", G, 6, 11, (2, 0), [A['cyrus'], A['misty'], A['irida'], A['vulp'], A['copy'], A['cape']],
             [pk(A['nine'], 140, W3, behind=[A['vulp']]), pk(A['sharp'], 130, ["Water", "Water"], behind=[A['carv']]), pk(A['sharp'], 180, ["Water", "Water"], behind=[A['carv']])],
             [pk(O['flygon'], 180, ["Fighting"], behind=[O['trap']])], 3, "Fighting",
             me_discard=[A['ball'], A['rs'], A['pop'], A['rs'], A['ball']], opp_discard_n=6, opp_discard_energy=["Fighting", "Grass", "Fighting"], stadium=RC, hand_source="frame",
             his=["Tool:Elegant Cape@0", "Play:Irida", "Place:Alolan Vulpix@3", "Attach:1Water@3 zone", "Attack:Binding Snow"],
             milestones=["preparing an attacker"],
             notes="Draw Elegant Cape. The opponent's Flygon ex (Rare Candy from Trapinch) has one Fighting and Sand Slammer chips 10 off each of his Pokémon at every checkup. Cape on the Ninetales, Irida heals the three Water Pokémon, the second Vulpix is benched with the turn's Water, Binding Snow 180 -> 100."))
P.append(pos(f"A-{G}-t13", G, 7, 13, (2, 0), [A['cyrus'], A['misty'], A['copy'], A['lap']],
             [pk(A['nine'], 160, W3, tools=[A['cape']], behind=[A['vulp']]), pk(A['sharp'], 150, ["Water", "Water"], behind=[A['carv']]), pk(A['sharp'], 170, ["Water", "Water"], behind=[A['carv']]), pk(A['vulp'], 40, ["Water"])],
             [pk(O['flygon'], 100, ["Fighting"], behind=[O['trap']]), pk(O['furf'], 70, ["Grass"])], 3, "Fighting",
             me_discard=[A['ball'], A['rs'], A['pop'], A['rs'], A['ball'], A['irida']], opp_discard_n=6, opp_discard_energy=["Fighting", "Grass", "Fighting"], stadium=RC, hand_source="frame",
             his=["Play:Copycat"], milestones=["preparing an attacker"],
             notes="Draw Lapras. He plays Copycat (drawing Misty, Cyrus, Lapras back), puts the second Water on the Vulpix and Binding Snow takes the Flygon ex 100 -> 20. The opponent then failed to return."))

# ---- 143309 (second, won 3-0)
G = "143309"
P.append(pos(f"A-{G}-t10", G, 5, 10, (1, 0), [A['nine'], A['copy'], A['cyrus'], A['irida'], A['vulp']],
             [pk(A['nine'], 170, ["Water", "Water"], tools=[A['cape']], behind=[A['vulp']]), pk(A['lap'], 110, W3), pk(A['sharp'], 190, ["Water"], behind=[A['carv']])],
             [pk(O['mew2'], 10), pk(O['gard'], 110, ["Psychic", "Psychic"], behind=[O['ralts'], O['kirl']]), pk(O['gard'], 110, ["Psychic"], behind=[O['ralts'], O['kirl']])], 1, "Psychic",
             me_discard=[A['rs'], A['misty'], A['rs'], A['ball']], opp_discard_n=5, hand_source="frame",
             his=["Place:Alolan Vulpix@3", "Play:Irida", "Attach:1Water@3 zone", "Attack:Binding Snow"], milestones=["recognising an immediate win"],
             notes="Draw Alolan Vulpix. Mewtwo ex is Active at 10 HP with no Energy: Binding Snow (80) KOs it for 2 points, 1 -> 3, the game. He benched the Vulpix, healed the last 10 damage with Irida and attached to the new Vulpix first."))

# fix an accidental key from a helper call above
for p in P:
    p.pop("discard_n", None)

# ---- milestone tags for the earlier turns (my reading of what each turn is about: preparing an attacker, managing a sacrifice,
#      recognising an immediate win, adapting when the plan fails); turns with nothing of the four carry none
MS = {
    "A-143309-t04": ["preparing an attacker"], "A-143309-t06": ["preparing an attacker"], "A-143309-t08": ["preparing an attacker"],
    "A-115323-t05": ["managing a sacrifice", "preparing an attacker"], "A-115323-t05b": ["managing a sacrifice", "preparing an attacker"], "A-115323-t07": ["preparing an attacker"],
    "A-143837-t05": ["preparing an attacker"], "A-143837-t07": ["preparing an attacker"],
    "A-114458-t04": ["preparing an attacker"], "A-114458-t06": ["preparing an attacker"], "A-114458-t08": ["managing a sacrifice"],
    "A-132311-t03": ["preparing an attacker"], "A-132311-t05": ["preparing an attacker", "managing a sacrifice"],
    "A-132311-t07": ["preparing an attacker", "managing a sacrifice"], "A-132311-t07b": ["preparing an attacker", "managing a sacrifice"],
}
for _p in P:
    if not _p.get("milestones"):
        _p["milestones"] = MS.get(_p["id"], [])

# ---- the held-out set of positions: a quarter of the GAMES, chosen by a fixed hash of the game id (not by turn), stable as games are added.
#      No development pilot is run on a held-out position until the lock file says so (run_pilot.sh skips them while locked).
import hashlib
HELDOUT_RULE = "held out iff int(sha256('pause-heldout-v1|' + game_id), 16) % 4 == 0  (game_id = the recording stem, e.g. 143837, or ladder-<stem>)"


def is_heldout(game_id):
    return int(hashlib.sha256(f"pause-heldout-v1|{game_id}".encode()).hexdigest(), 16) % 4 == 0


for _p in P:
    _p["heldout"] = is_heldout(_p["game"])

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "positions_A.json"
    json.dump(P, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    games = sorted({p["game"] for p in P})
    lock = {"locked": True, "unlocked_by": None, "rule": HELDOUT_RULE, "games_held_out": [g for g in games if is_heldout(g)],
            "games_development": [g for g in games if not is_heldout(g)]}
    json.dump(lock, open(os.path.join(os.path.dirname(os.path.abspath(out)), "positions_heldout.json"), "w"), indent=1)
    print(len(P), "positions ->", out, "| held-out games:", lock["games_held_out"], "| development games:", lock["games_development"])

