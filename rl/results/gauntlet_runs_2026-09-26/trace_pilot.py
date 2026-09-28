"""What does a gauntlet deck's pilot actually do? Plays N games with the official engine's own traces
(deckgym simulate --data-output, as decks/screen/floor.py) and counts, for the traced deck (seat 0), each own turn's
offered and chosen moves by kind: abilities by Pokémon, Stadium use, Trainers played, attacks by attacker and the
Energy on it when it attacks. Diagnostic only (Sept 26, pre-repair engine 7fc6ccb); seeds 21,108,900,000 + i.
Usage (WSL): python3 trace_pilot.py <deck> <opponent deck> [--games 40] [--pilot kp3] [--seed 21108900000]"""
import argparse, glob, json, os, shutil, subprocess, sys, tempfile
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
from current_engine import resolve  # noqa: E402  (the official engine, hash-checked against project_manifest.json)


def fields(card):
    if isinstance(card, dict) and len(card) == 1 and isinstance(next(iter(card.values())), dict):
        return next(iter(card.values()))
    return card if isinstance(card, dict) else {}


def body(action):
    a = action["action"]
    return (a, None) if isinstance(a, str) else next(iter(a.items()))


def slot_name(st, seat, idx):
    s = st["in_play_pokemon"][seat][idx]
    return fields(s["card"]).get("name") if s else None


def energy_of(slot):
    for k in ("attached_energy", "energy", "attached_energies"):
        if slot and k in slot:
            return slot[k]
    return None


def label(kind, v, st, seat):
    if kind == "UseAbility":
        return f"ability:{slot_name(st, seat, v['in_play_idx'])}"
    if kind == "Play":
        return f"play:{fields(v['trainer_card']).get('name')}"
    if kind == "Attack":
        return f"attack:{slot_name(st, seat, 0)}:{v.get('title') if isinstance(v, dict) else v}"
    if kind in ("Place", "Evolve"):
        c = v[0] if kind == "Place" else v["evolution"]
        return f"{kind.lower()}:{fields(c).get('name')}"
    return kind


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck"); ap.add_argument("opp")
    ap.add_argument("--games", type=int, default=40); ap.add_argument("--pilot", default="kp3")
    ap.add_argument("--seed", type=int, default=21108900000)
    ap.add_argument("--opp-pilot", default=None, help="seat 1's pilot (default: the same as --pilot)")
    ap.add_argument("--engine", default=None, help="a diagnostic build instead of the official engine (hash printed)")
    ap.add_argument("--per-game", default=None, help="also write one JSON line per game (seed, seat 0 won, and per "
                    "attack the own turns it was offered and used), for paired comparisons (added Sept 28 for koh)")
    a = ap.parse_args()
    per_game_rows = []
    engine = a.engine or str(resolve())
    if a.engine:
        import hashlib
        print(f"DIAGNOSTIC ENGINE {engine} sha256 {hashlib.sha256(open(engine, 'rb').read()).hexdigest()[:16]}")
    players = f"{a.pilot},{a.opp_pilot or a.pilot}"
    tmp = tempfile.mkdtemp(prefix="trace_", dir="/tmp")
    offered, chosen, attack_energy = Counter(), Counter(), defaultdict(Counter)
    # per own turn: attacks offered at any decision, the attack chosen (or none), Energy on the Active at the first
    # decision where each attack was offered
    turn_off, turn_used, turn_instead, declined_energy = Counter(), Counter(), defaultdict(Counter), defaultdict(Counter)
    move_off, move_used = Counter(), Counter()
    # hoarding check (kpf registration section 9): Energy left in seat 0's discard pile at the end, its retreats, and
    # its recovery moves (Dragon's Blessing, Professor Sada, Flame Patch)
    end_discard, retreats, recoveries = [], 0, 0
    wins = turns = 0; first_slot_keys = None
    try:
        out = subprocess.run([engine, "simulate", "--num", str(a.games), "--players", players,
                              "--seed", str(a.seed), "--seed-stream", "--data-output", os.path.join(tmp, "data"),
                              "--results-output", os.path.join(tmp, "res"), "-p", a.deck, a.opp],
                             capture_output=True, text=True)
        results = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(tmp, "res", "*.json")))]
        if len(results) != a.games:
            raise SystemExit(f"{len(results)} of {a.games} games; {(out.stdout + out.stderr)[-400:]}")
        for r in results:
            wins += r["outcome"] == {"Win": 0}; turns += r["final_turn"]
            per_turn = defaultdict(lambda: {"off": {}, "used": None})
            last_state = None
            for f in sorted(glob.glob(os.path.join(tmp, "data", r["game_id"], "ply_*.json"))):
                p = json.load(open(f))
                last_state = p["state"]
                if p["actor"] == 0:
                    k0, v0 = body(p["chosen_action"])
                    retreats += k0 == "Retreat"
                    lab0 = label(k0, v0, p["state"], 0)
                    recoveries += lab0 in ("ability:Dragonair", "play:Professor Sada", "play:Flame Patch")
                if p["actor"] != 0 or p["state"]["current_player"] != 0:
                    continue
                st = p["state"]
                pt = per_turn[st["turn_count"]]
                for x in p["playable_actions"]:
                    k2, v2 = body(x)
                    if k2 == "Attack":
                        lab2 = label(k2, v2, st, 0)
                        if lab2 not in pt["off"]:
                            e = energy_of(st["in_play_pokemon"][0][0])
                            pt["off"][lab2] = len(e) if isinstance(e, list) else -1
                if body(p["chosen_action"])[0] == "Attack":
                    pt["used"] = label(*body(p["chosen_action"]), st, 0)
                # abilities, Stadium use and Trainers: offered at some decision this turn / chosen this turn
                for x in p["playable_actions"]:
                    lab3 = label(*body(x), st, 0)
                    if lab3.startswith(("ability:", "play:")) or lab3 == "UseStadium":
                        pt.setdefault("moff", set()).add(lab3)
                lab4 = label(*body(p["chosen_action"]), st, 0)
                if lab4.startswith(("ability:", "play:")) or lab4 == "UseStadium":
                    pt.setdefault("mused", set()).add(lab4)
                if first_slot_keys is None and st["in_play_pokemon"][0][0]:
                    first_slot_keys = sorted(st["in_play_pokemon"][0][0].keys())
                t = st["turn_count"]
                for lab in {label(*body(x), st, 0) for x in p["playable_actions"]}:
                    offered[lab] += 1
                kind, v = body(p["chosen_action"]); lab = label(kind, v, st, 0)
                chosen[lab] += 1
                if kind == "Attack":
                    e = energy_of(st["in_play_pokemon"][0][0])
                    attack_energy[lab][len(e) if isinstance(e, list) else str(e)[:40]] += 1
            if last_state is not None and "discard_energies" in last_state:
                end_discard.append(len(last_state["discard_energies"][0]))
            if a.per_game:
                att = defaultdict(lambda: [0, 0])
                for pt in per_turn.values():
                    for lab2 in pt["off"]:
                        att[lab2][0] += 1
                        att[lab2][1] += pt["used"] == lab2
                per_game_rows.append({"seed": (r.get("randomness") or {}).get("game_seed"), "won": r["outcome"] == {"Win": 0},
                                      "final_turn": r["final_turn"], "attacks": {k: v for k, v in att.items()}})
            for pt in per_turn.values():
                for lab3 in pt.get("moff", ()):
                    move_off[lab3] += 1
                    move_used[lab3] += lab3 in pt.get("mused", ())
                for lab2, en in pt["off"].items():
                    turn_off[lab2] += 1
                    if pt["used"] == lab2:
                        turn_used[lab2] += 1
                    else:
                        turn_instead[lab2][pt["used"] or "no attack"] += 1
                        declined_energy[lab2][en] += 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if a.per_game:
        with open(a.per_game, "w", encoding="utf-8") as f:
            for row in sorted(per_game_rows, key=lambda x: (x["seed"] is None, x["seed"])):
                f.write(json.dumps(row) + "\n")
    print(f"{os.path.basename(a.deck)} (seat 0) v {os.path.basename(a.opp)}: players {players}, {a.games} games, "
          f"seeds {a.seed}+ (--seed-stream); seat 0 won {wins}; average final turn {turns / a.games:.1f}")
    print("slot keys:", first_slot_keys)
    print(f"{'move (seat 0 decisions)':60} offered chosen")
    for lab in sorted(offered, key=lambda k: -offered[k]):
        if lab in ("EndTurn",) or offered[lab] >= 3:
            print(f"  {lab[:58]:58} {offered[lab]:7} {chosen[lab]:6}")
    for lab, c in attack_energy.items():
        print(f"  energy on attacker when {lab}: {dict(sorted(c.items(), key=str))}")
    print("per own turn: attack offered at some decision -> used that turn / declined (what instead; Energy on the Active)")
    for lab in sorted(turn_off, key=lambda k: -turn_off[k]):
        print(f"  {lab[:50]:50} turns offered {turn_off[lab]:4}, used {turn_used[lab]:4}; instead "
              f"{dict(turn_instead[lab].most_common(4))}; Energy when declined {dict(sorted(declined_energy[lab].items()))}")
    if end_discard:
        print(f"hoarding check: seat 0's discard-pile Energy at the end {sum(end_discard) / len(end_discard):.2f} per game; "
              f"retreats {retreats / a.games:.2f} per game; recovery moves {recoveries / a.games:.2f} per game")
    print("per own turn: ability / Stadium use / Trainer offered at some decision -> used that turn")
    for lab in sorted(move_off, key=lambda k: -move_off[k]):
        print(f"  {lab[:50]:50} turns offered {move_off[lab]:4}, used {move_used[lab]:4} ({100 * move_used[lab] / move_off[lab]:.0f}%)")


if __name__ == "__main__":
    main()
