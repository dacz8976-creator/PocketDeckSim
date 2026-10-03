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


def pk(card, hp=None, energy=(), tools=(), behind=(), new=False, effects=()):
    d = {"card": card}
    if effects: d["effects"] = [{"effect": e, "turns": n} for e, n in effects]
    if hp is not None: d["hp"] = hp
    if energy: d["energy"] = list(energy)
    if tools: d["tools"] = list(tools)
    if behind: d["behind"] = list(behind)
    if new: d["new"] = True
    return d


def pos(id, game, his_turn, turn_count, points, me_hand, me_board, opp_board, opp_hand, opp_energy_next, *, me_discard=(), me_discard_energy=(),
        opp_discard_n=0, opp_discard_energy=(), energy_now="Water", stadium=None, effects=(), his=(), hand_source="text", notes="", force=(),
        top=None, flags=None, milestones=(), deck="A", energy_next="Water", list_source=None):
    p = {"id": id, "game": game, "his_turn": his_turn, "deck": deck, "turn_count": turn_count, "points": list(points),
         "me": {"hand": list(me_hand), "discard": list(me_discard), "discard_energy": list(me_discard_energy), "board": me_board,
                "energy_now": energy_now, "energy_next": energy_next},
         "opp": {"hand_count": opp_hand, "discard_n": opp_discard_n, "discard_energy": list(opp_discard_energy), "board": opp_board,
                 "energy_next": opp_energy_next},
         "stadium": stadium, "turn_effects": list(effects), "his_plan": list(his), "hand_source": hand_source, "notes": notes, "milestones": list(milestones)}
    if force: p["force"] = list(force)
    if list_source: p["list_source"] = list_source
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
             me_discard=[A['ball'], A['misty'], A['rs']], opp_discard_n=3, opp_discard_energy=["Grass"], hand_source="codex-confirmed",
             effects=[{"turn": 5, "effect": {"DelayedSpotDamage": {"source_player": 1, "target_player": 0, "target_in_play_idx": 0, "amount": 70, "knock_out": False}}}],
             his=["Play:Poké Ball", "(then: bench Carvanha, Water on Lapras, Surf)"],
             notes="The turn-5 draw is the Poké Ball he plays (nothing else in hand could be it). Flower Trick's mark on the Active Spot (70 at the end of this turn) is set."))
P.append(pos(f"A-{G}-t07", G, 4, 7, (0, 1), [A['sharp'], A['pop'], A['copy'], A['misty']],
             [pk(A['carv'], 50), pk(A['nine'], 180, tools=[A['cape']], behind=[A['vulp']])],
             [pk(O['meow'], 120, ["Grass", "Grass"], tools=[O['leafcape']], behind=[O['sprig']]), pk(O['ogerpon'], 130)], 3, "Grass",
             me_discard=[A['ball'], A['misty'], A['rs'], A['ball'], A['lap']], me_discard_energy=["Water", "Water", "Water"],
             opp_discard_n=3, opp_discard_energy=["Grass"], hand_source="codex-confirmed",
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
             me_discard=[A['ball'], A['rs']], opp_discard_n=2, opp_discard_energy=["Fighting"], hand_source="codex-confirmed",
             his=["Evolve:Mega Sharpedo ex@1", "Play:Lucky Ice Pop", "Play:Lucky Ice Pop", "Attach:1Water@0 zone", "Attack:Turbo Shark", "Attach:1Water@1 fx"],
             notes="Draw: the second Mega Sharpedo ex (first read as probable, by card count; confirmed by Codex's native evidence). Opp healed Furfrou back to 70 with Ice Pop (twice) and Shaymin."))
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
             stadium=AR, hand_source="codex-confirmed",
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
             me_discard=[A['ball'], A['rs'], A['pop'], A['rs'], A['ball']], opp_discard_n=6, opp_discard_energy=["Fighting", "Grass", "Fighting"], stadium=RC, hand_source="codex-confirmed",
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

# ======================================================================== deck 03 (the Wailord / Indeedee wall), game 020315: his turns 2-10, all hands from the review text
# (the opening hand and every draw are named in the review; no still frame was used; the opponent's hand sizes are bookkeeping, not counted)
W = dict(wailmer='Wailmer B4 036', wailord='Wailord B1 057', wailordex='Wailord ex B4 037', indee='Indeedee ex B1 121', ball='Poké Ball P-A 005',
         pop='Lucky Ice Pop B2 145', helmet='Heavy Helmet B1 219', rs="Professor's Research P-A 007", cyrus='Cyrus A2 150', irida='Irida A2a 072',
         lady='Pokémon Center Lady A2b 070', copy='Copycat B1 225', shore='Soothing Shore B4 154')
O.update(feebas='Feebas B3b 014', frig='Frigibax B2a 034', bax='Baxcalibur B2a 036', palkia='Palkia ex A2 049', milotic='Milotic ex B3b 015')
G = "020315"
SH = {"card": W['shore'], "owner": 1}
P.append(pos(f"D3-{G}-t02", G, 1, 2, (0, 0), [W['pop'], W['irida'], W['ball'], W['indee'], W['helmet']], [pk(W['wailmer'], 100)],
             [pk(O['feebas'], 30), pk(O['frig'], 60)], 4, "Water", deck="D03", hand_source="text",
             his=["Play:Heavy Helmet", "Tool:Heavy Helmet@0", "Play:Poké Ball", "(then: bench Wailmer and Indeedee ex, Water on the Wailmer)"], milestones=[],
             notes="Going second. Opening hand: Lucky Ice Pop, Irida, Poké Ball, Indeedee ex + the Wailmer he placed; draw Heavy Helmet. Review: Helmet on the Active Wailmer, Poké Ball finds a second Wailmer, bench it and the Indeedee ex, one Water."))
P.append(pos(f"D3-{G}-t04", G, 2, 4, (0, 0), [W['pop'], W['irida'], W['lady']],
             [pk(W['wailmer'], 100, ["Water"], tools=[W['helmet']]), pk(W['wailmer'], 100), pk(W['indee'], 130)],
             [pk(O['feebas'], 30, ["Water"]), pk(O['bax'], 140, behind=[O['frig']]), pk(O['palkia'], 150, ["Water"])], 1, "Water",
             me_discard=[W['ball']], opp_discard_n=3, deck="D03", hand_source="text",
             his=["Attach:1Water@0 zone"], milestones=[],
             notes="Draw Pokémon Center Lady (kept). He attaches the second Water and passes. The review does not say where the opponent's Palkia ex got its first Water (assumed one here); it does not affect this turn."))
P.append(pos(f"D3-{G}-t06", G, 3, 6, (0, 0), [W['pop'], W['irida'], W['lady'], W['indee']],
             [pk(W['wailmer'], 100, ["Water", "Water"], tools=[W['helmet']]), pk(W['wailmer'], 100), pk(W['indee'], 130)],
             [pk(O['feebas'], 30, ["Water", "Water"]), pk(O['bax'], 140, behind=[O['frig']]), pk(O['palkia'], 150, ["Water", "Water"]), pk(O['frig'], 60)], 3, "Water",
             me_discard=[W['ball']], opp_discard_n=4, deck="D03", hand_source="text",
             his=["Place:Indeedee ex@3", "Attach:1Water@0 zone", "Attack:Wave Splash"], milestones=["preparing an attacker"],
             notes="Draw the second Indeedee ex (benched). Third Water on the Wailmer, Wave Splash (60) KOs the 30-HP Feebas: his first point."))
P.append(pos(f"D3-{G}-t08", G, 4, 8, (1, 1), [W['pop'], W['irida'], W['lady'], W['wailord']],
             [pk(W['wailmer'], 80), pk(W['indee'], 110), pk(W['indee'], 110)],
             [pk(O['palkia'], 150, ["Water"]), pk(O['bax'], 140, behind=[O['frig']]), pk(O['frig'], 60), pk(O['feebas'], 30)], 2, "Water",
             me_discard=[W['ball'], W['helmet'], W['wailmer']], me_discard_energy=["Water"] * 3, opp_discard_n=5, opp_discard_energy=["Water"] * 5, stadium=SH,
             deck="D03", hand_source="text",
             his=["Ability:Watch Over@1", "Evolve:Wailord@0", "Attach:1Water@0 zone"], milestones=["adapting when the plan fails"],
             notes="Draw the Wailord. Palkia ex's Dimensional Storm (four Water) KO'd the three-Water Wailmer through its Helmet and chipped 20 off each Bench Pokémon; the reserve Wailmer (80 HP, no Energy) was promoted. Watch Over heals it to 100, it evolves into Wailord (200 HP), one Water, no attack."))
P.append(pos(f"D3-{G}-t10", G, 5, 10, (1, 1), [W['pop'], W['irida'], W['lady'], W['shore']],
             [pk(W['wailord'], 170, ["Water"], behind=[W['wailmer']]), pk(W['indee'], 110), pk(W['indee'], 110)],
             [pk(O['palkia'], 150, ["Water", "Water"]), pk(O['milotic'], 140, ["Water", "Water"], behind=[O['feebas']]), pk(O['bax'], 140, behind=[O['frig']]), pk(O['frig'], 60)], 3, "Water",
             me_discard=[W['ball'], W['helmet'], W['wailmer']], me_discard_energy=["Water"] * 3, opp_discard_n=6, opp_discard_energy=["Water"] * 5, stadium=SH,
             deck="D03", hand_source="text",
             his=["Ability:Watch Over@1", "Ability:Watch Over@2", "Attach:1Water@0 zone"], milestones=["managing a sacrifice"],
             notes="Draw Soothing Shore (cannot be played: the opponent's Shore is in play). Two Watch Overs heal the Wailord 170 -> 190 -> 200; second Water; no attack (it needs four). Next turn the opponent's Cyrus brought an Indeedee ex Active and Dimensional Storm KO'd it (the game)."))

# ======================================================================== deck 03, game 020920 (second, won by concession 0-0; opp Fire: Charmander line, Entei ex): his turns 2, 4, 6, 8, all from the review text
# (opening hand Poké Ball, Wailmer, Research, Cyrus, Lady; every draw named; opponent hand sizes are bookkeeping)
O.update(charmander='Charmander A1 033', charmeleon='Charmeleon B2b 008', entei='Entei ex A4a 010', bonsly='Bonsly B3 078', riolu='Riolu B3 079',
         lucario='Lucario A2 092', mega='Mega Lucario ex B3 081', hitmon='Hitmonchan B2 219', balloon='Small Balloon B3b 064')
G = "020920"
P.append(pos(f"D3-{G}-t02", G, 1, 2, (0, 0), [W['ball'], W['rs'], W['cyrus'], W['lady'], W['helmet']], [pk(W['wailmer'], 100)],
             [pk(O['charmander'], 60)], 6, "Fire", opp_discard_n=1, deck="D03", hand_source="text",
             his=["Play:Poké Ball", "(then: bench Indeedee ex, Research draws Indeedee ex #2 and Wailord, bench the second Indeedee ex, Helmet on Wailmer, Water)"], milestones=[],
             notes="Going second. Opening hand: Poké Ball, Professor's Research, Cyrus, Pokémon Center Lady + the Wailmer he placed; draw Heavy Helmet. "
                   "Poké Ball finds an Indeedee ex (benched), Research draws the second Indeedee ex and the Wailord (benched), Helmet on the Wailmer, first Water, no attack."))
P.append(pos(f"D3-{G}-t04", G, 2, 4, (0, 0), [W['cyrus'], W['lady'], W['wailord'], W['wailordex']],
             [pk(W['wailmer'], 80, ["Water"], tools=[W['helmet']]), pk(W['indee'], 130), pk(W['indee'], 130)],
             [pk(O['charmeleon'], 80, ["Fire", "Fire"], behind=[O['charmander']])], 6, "Fire",
             me_discard=[W['ball'], W['rs']], opp_discard_n=1, deck="D03", hand_source="text",
             his=["Evolve:Wailord@0", "Attach:1Water@0 zone", "Ability:Watch Over@1"], milestones=["preparing an attacker"],
             notes="Draw Wailord ex. The opponent's Charmeleon (Ignition, two Fire) used Slash 40 (20 through the Helmet): Wailmer 80. He evolves the damaged Wailmer into the "
                   "Wailord (180 HP), second Water, one Watch Over heals it to 200, no attack (Whale Pump needs four Energy). The review's alternative (keep the Wailmer unevolved "
                   "for a third-Water Wave Splash on turn 6) is Astra-checked as legal, not proven better."))
P.append(pos(f"D3-{G}-t06", G, 3, 6, (0, 0), [W['cyrus'], W['lady'], W['wailordex'], W['wailmer']],
             [pk(W['wailord'], 200, ["Water", "Water"], tools=[W['helmet']], behind=[W['wailmer']]), pk(W['indee'], 130), pk(W['indee'], 130)],
             [pk(O['charmeleon'], 80, ["Fire", "Fire"], behind=[O['charmander']]), pk(O['charmander'], 60, ["Fire"])], 5, "Fire",
             me_discard=[W['ball'], W['rs']], opp_discard_n=2, deck="D03", hand_source="text",
             his=["Place:Wailmer@3", "Attach:1Water@0 zone"], milestones=["preparing an attacker"],
             notes="Draw the second Wailmer (benched at once), third Water on the Wailord (it needs four), no attack. The opponent's Poké Ball found a second Charmander (one Fire)."))
P.append(pos(f"D3-{G}-t08", G, 4, 8, (0, 0), [W['cyrus'], W['lady'], W['wailordex'], W['pop']],
             [pk(W['wailord'], 160, ["Water", "Water", "Water"], tools=[W['helmet']], behind=[W['wailmer']]), pk(W['wailmer'], 100), pk(W['indee'], 130), pk(W['indee'], 130)],
             [pk(O['entei'], 140, ["Fire", "Fire"]), pk(O['charmeleon'], 80, behind=[O['charmander']]), pk(O['charmander'], 60, ["Fire", "Fire"])], 3, "Fire",
             me_discard=[W['ball'], W['rs']], opp_discard_n=5, deck="D03", hand_source="text",
             his=["Ability:Watch Over@2", "Ability:Watch Over@3", "Evolve:Wailord ex@1", "Attach:1Water@0 zone", "Attack:Whale Pump"], milestones=["preparing an attacker"],
             notes="Draw Lucky Ice Pop. The opponent's Entei ex (Blazing Beatdown, two Fire via two Flame Patch) took the Wailord to 160 through the Helmet. Two Watch Overs heal it to 200, "
                   "the benched Wailmer evolves into Wailord ex (no Energy), fourth Water, Whale Pump (100 + 20 Water weakness) leaves Entei ex on 20 HP; the opponent conceded next turn."))

# ======================================================================== deck 03, game 023418 (first, won by concession 0-1; opp Fighting: Bonsly, Riolu, Lucario, Mega Lucario ex): his turns 1-11, from the review text
# (opening hand Wailmer, Cyrus, Heavy Helmet, Wailord, Indeedee ex; every draw named; opponent hand sizes are bookkeeping)
G = "023418"
SH0 = {"card": W['shore'], "owner": 0}
P.append(pos(f"D3-{G}-t01", G, 1, 1, (0, 0), [W['cyrus'], W['helmet'], W['wailord'], W['indee'], W['rs']], [pk(W['wailmer'], 100)],
             [pk(O['bonsly'], 30)], 4, "Fighting", energy_now=None, deck="D03", hand_source="text",
             his=["Play:Heavy Helmet", "Tool:Heavy Helmet@0", "Place:Indeedee ex@1", "Play:Professor's Research"], milestones=[],
             notes="Going first: no Energy. Opening hand Cyrus, Heavy Helmet, Wailord, Indeedee ex + the Wailmer he placed; draw Professor's Research. Helmet on the Wailmer, bench the Indeedee ex, "
                   "Research (draws Pokémon Center Lady and Soothing Shore)."))
P.append(pos(f"D3-{G}-t03", G, 2, 3, (0, 0), [W['cyrus'], W['wailord'], W['lady'], W['shore'], W['pop']],
             [pk(W['wailmer'], 100, tools=[W['helmet']]), pk(W['indee'], 130)],
             [pk(O['bonsly'], 30), pk(O['riolu'], 60, tools=[O['balloon']]), pk(O['riolu'], 60, ["Fighting"])], 3, "Fighting",
             me_discard=[W['rs']], opp_discard_n=3, deck="D03", hand_source="text",
             his=["Evolve:Wailord@0", "Play:Soothing Shore", "Attach:1Water@0 zone"], milestones=["preparing an attacker"],
             notes="Draw Lucky Ice Pop. The opponent's Bonsly used Teary Attack (a -30 on the Wailmer's next attack, cleared when it evolves; not modelled). He evolves the Wailmer into the Wailord, "
                   "plays Soothing Shore and attaches the first Water; no attack (four Energy)."))
P.append(pos(f"D3-{G}-t05", G, 3, 5, (0, 0), [W['cyrus'], W['lady'], W['pop'], W['ball']],
             [pk(W['wailord'], 200, ["Water"], tools=[W['helmet']], behind=[W['wailmer']]), pk(W['indee'], 130)],
             [pk(O['bonsly'], 30), pk(O['riolu'], 60, tools=[O['balloon']]), pk(O['riolu'], 60, ["Fighting", "Fighting"]), pk(O['hitmon'], 80)], 3, "Fighting",
             me_discard=[W['rs']], opp_discard_n=3, stadium=SH0, deck="D03", hand_source="text",
             his=["Play:Poké Ball", "(then: bench the second Wailmer, second Water, no attack)"], milestones=["preparing an attacker"],
             notes="Draw Poké Ball (finds the second Wailmer, benched); second Water on the Wailord; no attack. The next opponent turn: Sabrina, Mega Lucario ex, and the Wailmer was the sacrificed "
                   "switch-in (a forced choice during the opponent's turn, not built here)."))
P.append(pos(f"D3-{G}-t07", G, 4, 7, (0, 1), [W['cyrus'], W['lady'], W['pop'], W['indee']],
             [pk(W['wailord'], 200, ["Water", "Water"], tools=[W['helmet']], behind=[W['wailmer']]), pk(W['indee'], 130)],
             [pk(O['mega'], 190, ["Fighting", "Fighting", "Fighting"], behind=[O['riolu']]), pk(O['bonsly'], 30), pk(O['lucario'], 100, tools=[O['balloon']], behind=[O['riolu']]), pk(O['hitmon'], 80)], 1, "Fighting",
             me_discard=[W['rs'], W['ball'], W['wailmer']], opp_discard_n=4, stadium=SH0, deck="D03", hand_source="text",
             his=["Place:Indeedee ex@2", "Attach:1Water@0 zone"], milestones=["preparing an attacker"],
             notes="Draw the second Indeedee ex (benched). The opponent's Sabrina dragged the unenergised Wailmer up, Mega Lucario ex's Fighting Pulse took it (1 point to the opponent), the Wailord was promoted. "
                   "Third Water, no attack."))
P.append(pos(f"D3-{G}-t09", G, 5, 9, (0, 1), [W['cyrus'], W['lady'], W['pop'], W['wailordex']],
             [pk(W['wailord'], 60, ["Water", "Water", "Water"], tools=[W['helmet']], behind=[W['wailmer']]), pk(W['indee'], 130), pk(W['indee'], 130)],
             [pk(O['mega'], 190, ["Fighting", "Fighting", "Fighting"], behind=[O['riolu']]), pk(O['bonsly'], 30), pk(O['lucario'], 100, ["Fighting"], tools=[O['balloon']], behind=[O['riolu']]), pk(O['hitmon'], 80)], 2, "Fighting",
             me_discard=[W['rs'], W['ball'], W['wailmer']], opp_discard_n=4, stadium=SH0, deck="D03", hand_source="text",
             his=["Ability:Watch Over@1", "Ability:Watch Over@2", "Play:Lucky Ice Pop", "(Ice Pop four times, four heads, the card back to hand each time)", "Attach:1Water@0 zone", "Attack:Whale Pump"],
             milestones=["preparing an attacker"],
             notes="Draw the Wailord ex (left in hand). Mega Lucario ex's Fighting Pulse took the Wailord to 60. He heals 60 -> 100 with two Watch Overs, then Lucky Ice Pop four times (four heads, "
                   "the card returns each time) to 180, fourth Water, Whale Pump (100): Mega Lucario ex 190 -> 90; Soothing Shore heals the Wailord to 200 at the end of his turn."))
P.append(pos(f"D3-{G}-t11", G, 6, 11, (0, 1), [W['cyrus'], W['lady'], W['wailordex'], W['pop'], W['shore']],
             [pk(W['wailord'], 190, ["Water", "Water", "Water", "Water"], tools=[W['helmet']], behind=[W['wailmer']], effects=[({"ReducedAttackDamage": {"amount": 30}}, 0)]), pk(W['indee'], 130), pk(W['indee'], 130)],
             [pk(O['bonsly'], 30), pk(O['mega'], 110, ["Fighting", "Fighting", "Fighting"], behind=[O['riolu']]), pk(O['lucario'], 100, ["Fighting", "Fighting"], tools=[O['balloon']], behind=[O['riolu']]), pk(O['hitmon'], 80)], 1, "Fighting",
             me_discard=[W['rs'], W['ball'], W['wailmer']], opp_discard_n=6, stadium=SH0, deck="D03", hand_source="text",
             his=["Ability:Watch Over@1", "Attach:1Water@0 zone", "Play:Cyrus", "(then: Mega Lucario ex Active; the opponent conceded before an attack)"], milestones=[],
             notes="Draw the second Soothing Shore (cannot be played). Bonsly's Teary Attack left the Wailord on 190 with a -30 on its next attack (modelled). He heals it to 200, fifth Water, and Cyrus "
                   "brings the damaged Mega Lucario ex (110) Active; the opponent conceded before he attacked (Whale Pump would have done 110 - 30 = 80). The review's Astra check: not a lethal line."))

# ======================================================================== Ladder Log games on brew 8 (Entei ex / Rainbow Cave), hands and boards from the Codex retrospective ledgers (Oct 2)
# Source: RETROSPECTIVE_HANDS_2026-10-02/<stem>/TURN_LEDGER.json (hand at turn start, structured start-of-turn boards, plays in order) + the packet's REVIEW_SUPPLEMENT.md.
# Deck: the stored brew 8 list (decks/brews/brew-08-entei-rainbow-cave.txt, unchanged since Sept 24) -- the Ladder Log entry "brew-08" names both recordings
# (Dustin confirmed all nine Sept 28 Entei ex games were brew 8) and Codex's visible core for each is exactly that list. list_source records that.
# His discard piles are my bookkeeping from the ledger plays (they close: every one of the 20 cards is accounted for, deck empty on 020916 turn 9 as the
# ledger's deck-empty warning says); the opponent's discard is not tracked (0). Not a computer battle: no Auto option seen in either packet's mode check.
E8 = dict(entei='Entei ex A4a 010', rs="Professor's Research P-A 007", copy='Copycat B1 225', lady='Pokémon Center Lady A2b 070', sab='Sabrina A1 225',
          cyrus='Cyrus A2 150', pop='Lucky Ice Pop B2 145', fp='Flame Patch B1 217', repel='Repel A3a 064', ball='Poké Ball P-A 005', cape='Giant Cape A2 147',
          rc='Rainbow Cave B4 155', sp='Starting Plains B2 154')
OE = dict(victini='Victini B3 025', moltres="Team Rocket's Moltres ex B4a 007", hound='Houndour A2a 011', houndoom='Mega Houndoom ex P-B 080', balloon='Small Balloon B3b 064',
          drampa='Drampa B4 124', ray='Mega Rayquaza ex B4 120', dratini_s='Dratini B4 116', dratini_b='Dratini A3b 051', dragonair='Dragonair B4 117')
LS8 = "season-brews: brew 8 (decks/brews/brew-08-entei-rainbow-cave.txt); Ladder Log entry 'brew-08' names this recording"
F = dict(energy_now="Fire", energy_next="Fire", deck="B08", hand_source="codex", list_source=LS8)

# ---- 20260929_020916000 (first, won 3-2; opp Fire: Team Rocket's Moltres ex, Mega Houndoom ex, Victini): his turns 1, 3, 5, 7, 9
G = "ladder-20260929_020916000"
SPL0 = {"card": E8['sp'], "owner": 0}
RC0 = {"card": E8['rc'], "owner": 0}
P.append(pos("L8-020916-t01", G, 1, 1, (0, 0), [E8['rc'], E8['copy'], E8['repel'], E8['cape'], E8['cyrus']], [pk(E8['entei'], 140)], [pk(OE['victini'], 70)], 4, "Fire",
             **{**F, "energy_now": None},
             his=["Play:Giant Cape", "Tool:Giant Cape@0", "Play:Rainbow Cave", "Play:Copycat"],
             notes="Going first: no Energy. Opening hand Rainbow Cave, Copycat, Repel, Entei ex (placed Active), Giant Cape; draw Cyrus. Cape on the Entei ex, Rainbow Cave, Copycat (Repel and Cyrus shuffled back, "
                   "four cards drawn to match the opponent's four). Legendary Pulse then draws Flame Patch. Opponent's discard not tracked."))
P.append(pos("L8-020916-t03", G, 2, 3, (0, 0), [E8['copy'], E8['rs'], E8['pop'], E8['cape'], E8['fp'], E8['rc']],
             [pk(E8['entei'], 160, tools=[E8['cape']])],
             [pk(OE['moltres'], 130, ["Fire"] * 4), pk(OE['moltres'], 130), pk(OE['victini'], 70, tools=[OE['balloon']]), pk(OE['hound'], 60)], 2, "Fire",
             me_discard=[E8['copy']], stadium=RC0, **F,
             his=["UseStadium", "Play:Professor's Research", "(then: Flame Patch to the Active Entei, Fire from the Zone, Blazing Beatdown 60: Moltres 130 -> 70)"], milestones=["preparing an attacker"],
             notes="Draw Rainbow Cave (the second copy; the first is in play, his). Rainbow Cave's reroll, Research (Research and Sabrina), Flame Patch and the turn's Fire give the Entei two Fire; the attack takes the Active Moltres to 70."))
P.append(pos("L8-020916-t05", G, 3, 5, (0, 0), [E8['copy'], E8['pop'], E8['cape'], E8['rc'], E8['rs'], E8['sab'], E8['ball'], E8['pop']],
             [pk(E8['entei'], 10, ["Fire", "Fire"], tools=[E8['cape']])],
             [pk(OE['moltres'], 70, ["Fire"] * 3), pk(OE['moltres'], 130), pk(OE['victini'], 70, tools=[OE['balloon']]), pk(OE['hound'], 60, ["Fire"])], 2, "Fire",
             me_discard=[E8['copy'], E8['rs'], E8['fp']], stadium=RC0, **F,
             his=["Play:Poké Ball", "(then: bench the regular-art Entei ex, Giant Cape on it, three Lucky Ice Pops (heads, tails, tails) 10 -> 70, Research, Rainbow Cave reroll, Flame Patch, Fire, Starting Plains over Rainbow Cave, Blazing Beatdown 120 KOs the first Moltres)"],
             milestones=["managing a sacrifice", "preparing an attacker"],
             notes="Draw the second Lucky Ice Pop. The Active Entei ex is on 10 HP after Netherwing's 150. He benches a second Entei ex (Poké Ball), caps it, heals the Active by 60 with the Pops, and attacks for the first KO (two points)."))
P.append(pos("L8-020916-t07", G, 4, 7, (2, 0), [E8['copy'], E8['rc'], E8['sab'], E8['lady'], E8['cyrus']],
             [pk(E8['entei'], 10, ["Fire"] * 4, tools=[E8['cape']]), pk(E8['entei'], 180, tools=[E8['cape']])],
             [pk(OE['houndoom'], 190, ["Fire"] * 3, behind=[OE['hound']]), pk(OE['moltres'], 150), pk(OE['victini'], 90, tools=[OE['balloon']])], 2, "Fire",
             me_discard=[E8['copy'], E8['rs'], E8['fp'], E8['ball'], E8['pop'], E8['pop'], E8['rs'], E8['fp'], E8['rc']], stadium=SPL0, **F,
             his=["Play:Sabrina", "Attach:1Fire@1 zone", "Attack:Blazing Beatdown"], milestones=["preparing an attacker"],
             notes="Draw Cyrus. The opponent's Houndour became Mega Houndoom ex (190, three Fire) and Starting Plains is in play (his). Sabrina drags the second Moltres Active (the opponent picked it), the turn's Fire goes to the backup Entei ex, Blazing Beatdown takes the Moltres to 30."))
P.append(pos("L8-020916-t09", G, 5, 9, (2, 2), [E8['copy'], E8['rc'], E8['lady'], E8['cyrus'], E8['repel']],
             [pk(E8['entei'], 180, ["Fire"], tools=[E8['cape']])],
             [pk(OE['houndoom'], 210, ["Fire"] * 3, tools=[E8['cape']], behind=[OE['hound']]), pk(OE['moltres'], 30), pk(OE['victini'], 90, tools=[OE['balloon']])], 3, "Fire",
             me_discard=[E8['copy'], E8['rs'], E8['fp'], E8['ball'], E8['pop'], E8['pop'], E8['rs'], E8['fp'], E8['rc'], E8['sab'], E8['entei'], E8['cape']],
             me_discard_energy=["Fire"] * 4, stadium=SPL0, **F,
             his=["Play:Cyrus", "Attach:1Fire@0 zone", "Attack:Blazing Beatdown"], milestones=["recognising an immediate win"],
             notes="His deck is empty (the draw failed): every card of the list is in his hand, on the board or in his discard. The first Entei ex was knocked out by Mega Houndoom ex (two points to the opponent). "
                   "Cyrus brings the 30-HP Moltres ex Active, Fire, Blazing Beatdown KOs it: 2 -> 4 points, the game."))

# ---- 20260929_002539000 (second, won by concession 2-2; opp Dragon: Drampa, Mega Rayquaza ex, Dratini / Dragonair): his turns 2, 4, 6, 8, 10
G = "ladder-20260929_002539000"
RC1 = {"card": E8['rc'], "owner": 1}
P.append(pos("L8-002539-t02", G, 1, 2, (0, 0), [E8['copy'], E8['cape'], E8['fp'], E8['rs'], E8['fp']], [pk(E8['entei'], 140)],
             [pk(OE['drampa'], 100), pk(OE['ray'], 180), pk(OE['dratini_s'], 60)], 2, "Lightning", **F,
             his=["Play:Giant Cape", "Tool:Giant Cape@0", "Play:Professor's Research", "(then: Poké Ball finds the alternate-art Entei ex, bench it, Fire to the Active)"],
             notes="Going second. Opening hand Copycat, Giant Cape, Flame Patch, Research + the Entei ex placed; draw the second Flame Patch. Opponent hand 2 (counted by Codex). Opponent's discard not tracked."))
P.append(pos("L8-002539-t04", G, 2, 4, (0, 0), [E8['copy'], E8['fp'], E8['fp'], E8['pop'], E8['copy'], E8['sab']],
             [pk(E8['entei'], 90, ["Fire"], tools=[E8['cape']]), pk(E8['entei'], 140)],
             [pk(OE['drampa'], 100, ["Lightning"]), pk(OE['ray'], 180), pk(OE['dragonair'], 80, behind=[OE['dratini_s']])], 1, "Lightning",
             me_discard=[E8['rs'], E8['ball']], stadium=RC1, **F,
             his=["Play:Lucky Ice Pop", "Play:Sabrina", "UseStadium", "Attach:1Fire@0 zone", "Play:Flame Patch", "Attack:Blazing Beatdown"],
             notes="Draw Sabrina. Drampa's Power Blast took the Active Entei ex from 160 to 90; the opponent's Rainbow Cave is in play (their Stadium). Pop heals 20 (tails: discarded), Sabrina drags Mega Rayquaza ex Active (the opponent picked it), "
                   "reroll, Fire, Flame Patch (three Fire), Blazing Beatdown 60 takes it to 120."))
P.append(pos("L8-002539-t06", G, 3, 6, (0, 0), [E8['copy'], E8['fp'], E8['copy'], E8['rc'], E8['lady']],
             [pk(E8['entei'], 40, ["Fire"] * 3, tools=[E8['cape']]), pk(E8['entei'], 140)],
             [pk(OE['drampa'], 100, ["Lightning"]), pk(OE['ray'], 120), pk(OE['dragonair'], 80, behind=[OE['dratini_s']])], 2, "Lightning",
             me_discard=[E8['rs'], E8['ball'], E8['pop'], E8['sab'], E8['fp']], stadium=RC1, **F,
             his=["UseStadium", "Attach:1Fire@1 zone", "Play:Flame Patch", "Play:Copycat", "(then: Starting Plains over Rainbow Cave, Blazing Beatdown 120 KOs Drampa)"], milestones=["preparing an attacker"],
             notes="Draw Pokémon Center Lady. The Active Entei ex is on 40 (Power Blast again). Reroll, the turn's Fire to the benched Entei ex, Flame Patch back to the Active (four Fire), Copycat (hand shuffled, two cards to match the opponent's "
                   "two: Starting Plains, Rainbow Cave), Starting Plains replaces the opponent's Rainbow Cave, the attack KOs Drampa."))
P.append(pos("L8-002539-t08", G, 4, 8, (1, 0), [E8['rc'], E8['rc'], E8['lady']],
             [pk(E8['entei'], 60, ["Fire"] * 4, tools=[E8['cape']]), pk(E8['entei'], 160, ["Fire"])],
             [pk(OE['drampa'], 120), pk(OE['ray'], 140), pk(OE['dragonair'], 80, behind=[OE['dratini_s']])], 2, "Lightning",
             me_discard=[E8['rs'], E8['ball'], E8['pop'], E8['sab'], E8['fp'], E8['fp'], E8['copy']], stadium=SPL0, **F,
             his=["Play:Pokémon Center Lady", "Attach:1Fire@1 zone", "Attack:Blazing Beatdown"], milestones=["preparing an attacker"],
             notes="Draw the Lady (shuffled away by Copycat, drawn again). Starting Plains is in play (his). Lady heals the Active 60 -> 90, the turn's Fire to the benched Entei ex, Blazing Beatdown KOs the second Drampa: 2 points."))
P.append(pos("L8-002539-t10", G, 5, 10, (2, 2), [E8['rc'], E8['rc'], E8['cyrus'], E8['rs']],
             [pk(E8['entei'], 160, ["Fire"] * 2)],
             [pk(OE['ray'], 140), pk(OE['dratini_b'], 80), pk(OE['dragonair'], 80, behind=[OE['dratini_s']])], 3, "Lightning",
             me_discard=[E8['rs'], E8['ball'], E8['pop'], E8['sab'], E8['fp'], E8['fp'], E8['copy'], E8['lady'], E8['entei'], E8['cape']], me_discard_energy=["Fire"] * 4,
             stadium=SPL0, **F,
             his=["Play:Professor's Research", "(then: the turn's Fire to the Active, Blazing Beatdown 60: Mega Rayquaza 140 -> 80)"],
             notes="Draw Research. The opponent knocked out his first Entei ex (two points: 2-2); the alternate-art Entei ex (160, two Fire) is Active. He plays Research (Pop and Copycat), Fire, Blazing Beatdown; the opponent conceded two turns later."))

# ======================================================================== deck 03 games 021402 and 022135 (hands from the Codex native-frame packets, Oct 2)
# The positions are data, not code: codex_positions/wl_final_<game>.json (built by two independent builders from the accepted reviews + the Codex hand
# packets, adjudicated, audited by a third reader; see README "Codex hands"). Added to P as they are; milestones and the held-out flag are applied below.
import glob
for _f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "codex_positions", "wl_final_*.json"))):
    P.extend(json.load(open(_f, encoding="utf-8")))

# ---- old Ladder Log games with no stored deck code (Codex retrospective ledgers, Oct 2): the list is RECONSTRUCTED (cards seen + nearest repo list, unseen slots
# chosen conservatively, see reconstructed_decks/<key>.json), so each position is `approximate`, stays out of every verdict-bearing comparison and is tagged as such.
# Data, not code: reconstructed_positions/lr_final_<game>.json (built by one helper, audited by a second reader).
for _f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "reconstructed_positions", "lr_final_*.json"))):
    P.extend(json.load(open(_f, encoding="utf-8")))

# ---- milestone tags for the earlier turns (my reading of what each turn is about: preparing an attacker, managing a sacrifice,
#      recognising an immediate win, adapting when the plan fails); turns with nothing of the four carry none
MS = {
    "A-143309-t04": ["preparing an attacker"], "A-143309-t06": ["preparing an attacker"], "A-143309-t08": ["preparing an attacker"],
    "A-115323-t05": ["managing a sacrifice", "preparing an attacker"], "A-115323-t05b": ["managing a sacrifice", "preparing an attacker"], "A-115323-t07": ["preparing an attacker"],
    "A-143837-t05": ["preparing an attacker"], "A-143837-t07": ["preparing an attacker"],
    "A-114458-t04": ["preparing an attacker"], "A-114458-t06": ["preparing an attacker"], "A-114458-t08": ["managing a sacrifice"],
    "A-132311-t03": ["preparing an attacker"], "A-132311-t05": ["preparing an attacker", "managing a sacrifice"],
    "A-132311-t07": ["preparing an attacker", "managing a sacrifice"], "A-132311-t07b": ["preparing an attacker", "managing a sacrifice"],
    "D3-021402-t03": ["preparing an attacker"], "D3-021402-t05": ["preparing an attacker"],
    "D3-022135-t03": ["preparing an attacker"], "D3-022135-t05": ["preparing an attacker"], "D3-022135-t07": ["preparing an attacker"],
    "D3-022135-t09": ["adapting when the plan fails"],
}
for _p in P:
    if not _p.get("milestones"):
        _p["milestones"] = MS.get(_p["id"], [])

# deck 03: Watch Over (Indeedee ex) heals the Active and the engine offers it at full HP, where it does nothing; a turn on which none of his Pokemon is damaged
# is flagged so the report does not count a no-op use as a difference
MAXHP = {W['wailmer']: 100, W['wailord']: 200, W['wailordex']: 250, W['indee']: 130}
for _p in P:
    if _p["deck"] == "D03":
        _p["noop_ability"] = not any(b.get("hp", MAXHP[b["card"]]) < MAXHP[b["card"]] for b in _p["me"]["board"])

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

