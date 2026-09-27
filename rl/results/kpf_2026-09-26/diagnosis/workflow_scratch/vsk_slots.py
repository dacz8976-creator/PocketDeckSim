"""Slot simulation for one seat: returns, per line, the list of 4 slots (each a dict with name/uid or None) BEFORE the
line's action, validated against the board string. Each Pokemon gets a uid when placed so Energy holders can be tracked."""
import re
from vsk_lib import parse_board


def names_of(board):
    b = parse_board(board)
    return ([b["active"]["name"]] if b["active"] else []) + [p["name"] for p in b["bench"]], b


def simulate(tr, seat):
    slots = [None] * 4
    uid = [0]
    out = []
    bad = 0

    def new(name):
        uid[0] += 1
        return {"name": name, "uid": uid[0]}

    for n, L in enumerate(tr):
        # sync removals with the board: any slot whose Pokemon vanished (KO) is cleared
        nm, b = names_of(L["s"][seat])
        occ = [s for s in slots if s]
        if [s["name"] for s in occ] != nm:
            # try to repair: drop slots in order until names match (KO'd Pokemon removed)
            if b["active"] is None and slots[0] is not None:
                slots[0] = None
            occ = [s for s in slots if s]
            if [s["name"] for s in occ] != nm:
                # remove bench slots whose names are not matched greedily
                j = 0
                keep = [False] * 4
                for i, s in enumerate(slots):
                    if s and j < len(nm) and s["name"] == nm[j] and (i > 0 or b["active"] is not None):
                        keep[i] = True
                        j += 1
                if j == len(nm):
                    for i in range(4):
                        if not keep[i]:
                            slots[i] = None
                else:
                    bad += 1
        out.append([dict(s) if s else None for s in slots])
        a = L["act"]
        mine = L["actor"] == seat
        m = re.match(r"Place\(Pokemon\((.*?)\), (\d)\)", a)
        if m and mine:
            nm2 = re.sub(r"^\S+ \S+ ", "", m.group(1))  # drop set + number
            nm2 = re.sub(r"^P-A \d+ ", "", m.group(1)) if m.group(1).startswith("P-A") else nm2
            slots[int(m.group(2))] = new(nm2)
            continue
        m = re.match(r"Evolve \{ evolution: Pokemon\((.*?)\), in_play_idx: (\d)", a)
        if m and mine:
            s = slots[int(m.group(2))]
            if s:
                s["name"] = re.sub(r"^\S+ \S+ ", "", m.group(1))
            continue
        m = re.match(r"Retreat\((\d)\)", a)
        if m and mine:
            k = int(m.group(1))
            slots[0], slots[k] = slots[k], slots[0]
            continue
        m = re.match(r"(Promote|Activate) \{ player: (\d), in_play_idx: (\d) \}", a)
        if m and int(m.group(2)) == seat:
            k = int(m.group(3))
            slots[0], slots[k] = slots[k], slots[0]
            continue
        m = re.match(r"DiscardOwnBenchedThenDamage \{ in_play_idxs: \[(\d)\]", a)
        if m and mine:
            slots[int(m.group(1))] = None
            continue
    return out, bad
