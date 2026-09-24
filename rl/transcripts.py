"""Readable game transcripts for checking the bot's play and the engine's rules.
Run inside WSL with run_transcripts.sh (it sets up its own Python so the training run's
setup is never touched). Safe to run while training is still going: it only reads saved files.

For one checkpoint (default: the latest), picks games it played against k3 at that checkpoint:
  - losses, wins from the first seat, and the longest games (where draws and stalling hide)
plus a few k3-vs-k3 games from Astra's baseline, to read first so you know what k3's own
mistakes look like. Writes one text file per game and an INDEX.txt.

At every bot decision a transcript shows the board exactly as the bot could see it, every
legal move with the bot's predicted result for it (-1 = sure loss, +1 = sure win; it plays the
highest), the move it picked, and a clearly marked referee line with the cards it could NOT see.
Every game is replayed from its seed and recorded moves and checked against the saved result.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model import MLP  # noqa: E402
from pdl_rl_env import RawEnv  # noqa: E402

ROOT = HERE.parent  # the repo root (on the laptop this file sat two folders down)
BREW = str(ROOT / "decks/brews/brew-03a-arceus-nihilego-toxapex.txt")
HIDDEN = (512, 256)
SLOT = ["Active", "Bench 1", "Bench 2", "Bench 3"]


# ---------------------------------------------------------------- formatting
def card_name(v):
    if isinstance(v, dict):
        inner = v.get("Pokemon") or v.get("Trainer") or v
        if isinstance(inner, dict) and "name" in inner:
            return inner["name"]
    return None


def compact(v):
    n = card_name(v)
    if n:
        return n
    if isinstance(v, dict):
        return ", ".join(f"{k}={compact(x)}" for k, x in v.items())
    if isinstance(v, list):
        return "[" + ", ".join(compact(x) for x in v) + "]"
    return str(v)


def slot(idx, board=None):
    label = SLOT[idx] if 0 <= idx < 4 else f"slot {idx}"
    if board and 0 <= idx < 4 and board[idx]:
        return f"{board[idx]['name']} ({label})"
    return label


def move_text(js, board=None, boards=None, mover=None):
    """board: the mover's own board (names slots); boards: {player: board}; mover: whose move it is."""
    v = json.loads(js)
    if isinstance(v, str):
        return {"EndTurn": "End turn"}.get(v, v)
    kind, a = next(iter(v.items()))
    try:
        if kind == "Place":
            return f"Put {card_name(a[0])} onto {SLOT[a[1]]}"
        if kind == "Evolve":
            return f"Evolve {slot(a['in_play_idx'], board)} into {card_name(a['evolution'])}" + \
                   (" (from deck)" if a.get("from_deck") else "")
        if kind == "Attack":
            eff = f" — {a['effect']}" if a.get("effect") else ""
            return f"Attack: {a['title']} ({a['fixed_damage']} base damage){eff}"
        if kind == "Retreat":
            return f"Retreat, bringing up {slot(a, board)}"
        if kind == "Attach":
            parts = [f"{amt} {etype} to {slot(idx, board)}" for amt, etype, idx in a["attachments"]]
            return "Attach " + "; ".join(parts) + (" (this turn's energy)" if a.get("is_turn_energy") else "")
        if kind == "Play":
            return f"Play {card_name(a['trainer_card'])}"
        if kind == "AttachTool":
            return f"Attach {card_name(a['tool_card'])} to {slot(a['in_play_idx'], board)}"
        if kind == "UseAbility":
            return f"Use the ability of {slot(a['in_play_idx'], board)}"
        if kind in ("Promote", "Activate"):
            b = boards.get(a["player"]) if boards else None
            whose = "" if mover is None or a["player"] == mover else "opponent's "
            return f"Bring {whose}{slot(a['in_play_idx'], b)} into the Active Spot"
        if kind == "DrawCard":
            return f"Draw {a['amount']} card" + ("s" if a["amount"] != 1 else "")
    except (KeyError, IndexError, TypeError):
        pass
    return f"{kind}({compact(a)})"


def energy_text(lst):
    if not lst:
        return "none"
    counts = {}
    for e in lst:
        counts[e] = counts.get(e, 0) + 1
    return ", ".join(f"{n} {e}" for e, n in counts.items())


def side_lines(label, side, is_viewer):
    hand = side["hand"]
    known = [c for c in hand if c != "?"]
    lines = [f"  {label}: {side['points']} point{'s' if side['points'] != 1 else ''} · "
             f"energy now {side['energy_now'] or '—'}, next {side['energy_next'] or '—'} · "
             f"deck {side['deck']['size']}"]
    for i, p in enumerate(side["board"]):
        if not p:
            lines.append(f"    {SLOT[i]:<8} —")
            continue
        extra = []
        if p["tools"]:
            extra.append("tools: " + ", ".join(p["tools"]))
        if p["status"]:
            extra.append(", ".join(p["status"]))
        if p["played_this_turn"]:
            extra.append("played this turn")
        if p["ability_used"]:
            extra.append("ability used")
        lines.append(f"    {SLOT[i]:<8} {p['name']} — {p['hp_left']} HP left (card {p['hp_card']}) · "
                     f"energy: {energy_text(p['energy'])}" + (" · " + " · ".join(extra) if extra else ""))
    if is_viewer:
        lines.append(f"    Hand ({len(hand)}): " + (", ".join(hand) or "empty"))
        if "contents_unordered" in side["deck"]:
            lines.append("    Deck, order unknown: " + (", ".join(side["deck"]["contents_unordered"]) or "empty"))
    else:
        lines.append(f"    Hand: {len(hand)} card{'s' if len(hand) != 1 else ''}"
                     + (f" (known: {', '.join(known)})" if known else ", all hidden"))
    lines.append("    Discard: " + (", ".join(side["discard"]) or "empty"))
    return lines


def board_block(view, names):
    me, them = view["viewer"], 1 - view["viewer"]
    head = f"Turn {view['turn']}" + (f" · Stadium: {view['stadium']}" if view["stadium"] else "")
    if view.get("opponent_setup_hidden"):
        head += " · opponent's starting Pokémon still face-down"
    return [head] + side_lines(names[me], view["me"], True) + side_lines(names[them], view["them"], False)


# ---------------------------------------------------------------- replay
def load_net(path, dim):
    net = MLP(dim, HIDDEN, seed=0)
    z = np.load(path)
    for i, p in enumerate(net.W + net.b):
        p[...] = z[f"p{i}"]
    return net


def replay(env, dim, seed, bots, moves_by_seat, net, net_seat, names, title):
    """Replays one game, returning (lines, final result, problems)."""
    env.set_recording(True)
    env.reset(BREW, BREW, seed, bots)
    lines, problems = [title, ""], []
    used = {0: 0, 1: 0}
    seen = 0
    last_turn_shown = None

    def feed():
        nonlocal seen, last_turn_shown
        hist = env.history()
        for p, kind, js, view in hist[seen:]:
            if kind == "agent":
                continue  # already printed at the decision
            if kind == "bot" and view:
                v = json.loads(view)
                key = (v["turn"], p)
                if key != last_turn_shown:
                    last_turn_shown = key
                    lines.append("")
                    lines.extend(board_block(v, names) if bots == ["k3", "k3"] else
                                 [f"— {names[p]}'s turn {v['turn']} —"])
                board = v["me"]["board"]
                boards = {p: v["me"]["board"], 1 - p: v["them"]["board"]}
                lines.append(f"  {names[p]}: {move_text(js, board, boards, p)}")
            else:
                lines.append(f"  ({names[p]}, only option) {move_text(js)}")
        seen = len(hist)

    while True:
        feed()
        if env.done:
            break
        p = env.current_player
        if moves_by_seat.get(p) is None:
            problems.append(f"asked for a move from seat {p}, which has no recorded moves")
            break
        if used[p] >= len(moves_by_seat[p]):
            problems.append(f"ran out of recorded moves for seat {p}")
            break
        choice = moves_by_seat[p][used[p]]
        used[p] += 1
        view = json.loads(env.describe(p))
        legal = env.legal_actions_json()
        if choice >= len(legal):
            problems.append(f"recorded move {choice} is not legal here ({len(legal)} options)")
            break
        lines.append("")
        lines.append("=" * 100)
        lines.extend(board_block(view, names))
        boards = {p: view["me"]["board"], 1 - p: view["them"]["board"]}
        if net is not None and p == net_seat:
            obs = np.frombuffer(env.observe(p), dtype="<f4")
            feats = np.frombuffer(env.action_features(), dtype="<f4").reshape(len(legal), env.action_dim)
            q = net.score_actions(obs, feats)
            if q[choice] < q.max() - 1e-6:
                problems.append(f"turn {view['turn']}: recorded move isn't the bot's top-scored move "
                                "(wrong checkpoint or input mismatch)")
            lines.append(f"  {names[p]} to move. Every legal move, best first, with the bot's predicted result "
                         "(-1 sure loss … +1 sure win):")
            for i in np.argsort(-q, kind="stable"):
                mark = "→" if i == choice else " "
                lines.append(f"   {mark} {q[i]:+.2f}  {move_text(legal[i], view['me']['board'], boards, p)}")
        else:
            lines.append(f"  {names[p]} to move ({len(legal)} legal options):")
            for i, js in enumerate(legal):
                mark = "→" if i == choice else " "
                lines.append(f"   {mark} {move_text(js, view['me']['board'], boards, p)}")
        ref = json.loads(env.referee())
        o = 1 - p
        lines.append(f"  [referee view — hidden from {names[p]}] {names[o]}'s hand: "
                     f"{', '.join(ref['hands'][o]) or 'empty'} · top of {names[o]}'s deck: "
                     f"{', '.join(ref['deck_top5'][o]) or 'empty'} · top of own deck: "
                     f"{', '.join(ref['deck_top5'][p]) or 'empty'}")
        env.step(choice)
    result = env.result() if env.done else None
    for s, mv in moves_by_seat.items():
        if mv is not None and used[s] != len(mv):
            problems.append(f"seat {s}: used {used[s]} of {len(mv)} recorded moves")
    return lines, result, problems


def outcome_line(result, names):
    w, pts, turns = result
    if w != -1:
        who = f"{names[w]} wins"
    elif turns > 30:
        who = "Draw (turn limit)"
    elif min(pts) >= 3:
        who = "Draw (both reached 3 points at once)"
    else:
        who = "Draw"
    return f"Result: {who} · points {names[0]} {pts[0]}, {names[1]} {pts[1]} · {turns} turns"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="training run folder, e.g. runs/brew03a-01")
    ap.add_argument("--ckpt", default="latest", help="checkpoint name, or 'latest' (default)")
    ap.add_argument("--per-group", type=int, default=5, help="games per group (losses, seat-0 wins, longest)")
    ap.add_argument("--mirror", type=int, default=3, help="k3-vs-k3 baseline games to include")
    ap.add_argument("--seeds", default="", help="specific games instead: seed:seat,seed:seat (seat = bot's seat)")
    ap.add_argument("--out", default="", help="output subfolder name (default: the checkpoint name)")
    a = ap.parse_args()
    run_dir = Path(a.run) if Path(a.run).is_absolute() else HERE / a.run
    st = json.loads((run_dir / "state.json").read_text())
    name = st["checkpoints"][-1]["name"] if a.ckpt == "latest" else a.ckpt
    out_dir = run_dir / "transcripts" / (a.out or name)
    out_dir.mkdir(parents=True, exist_ok=True)

    env = RawEnv(sorted(set(RawEnv.deck_card_ids(BREW))))
    env.reset(BREW, BREW, 1)
    dim = env.obs_dim + env.action_dim
    net = load_net(run_dir / f"{name}.npz", dim)

    games = [json.loads(l) for l in (run_dir / "eval_games.jsonl").read_text().splitlines() if l.strip()]
    games = [g for g in games if g.get("ckpt") == name and g.get("opp") == "k3"]
    if not games:
        raise SystemExit(f"No recorded k3 games for {name}.")
    picked, seen = [], set()

    def take(group, pool):
        n = 0
        for g in pool:
            key = (g["seed"], g["net_seat"], g.get("kind"))
            if key in seen or n >= a.per_group:
                continue
            seen.add(key)
            picked.append((group, g))
            n += 1

    if a.seeds:
        want = {tuple(int(x) for x in pair.split(":")) for pair in a.seeds.split(",") if pair}
        for g in games:
            if (g["seed"], g["net_seat"]) in want and (g["seed"], g["net_seat"]) not in {k[:2] for k in seen}:
                seen.add((g["seed"], g["net_seat"], g.get("kind")))
                picked.append(("picked", g))
        a.per_group = 0
    losses = [g for g in games if g["winner"] not in (-1, g["net_seat"])]
    take("loss", losses[::max(1, len(losses) // max(1, a.per_group))] + losses)
    take("win-first-seat", [g for g in games if g["net_seat"] == 0 and g["winner"] == 0])
    take("longest", sorted(games, key=lambda g: -g["turns"]))
    take("draw", [g for g in games if g["winner"] == -1])

    index = [f"Transcripts for {run_dir.name}, checkpoint {name}, against k3 (brew-03a mirror).",
             "Read the k3-vs-k3 baseline games first. In each bot game, the numbers next to the moves are the",
             "bot's predicted result for that move (-1 sure loss, +1 sure win); it plays the highest (→).",
             "What to look for: (1) a bad pick with the right move scored close behind = training;",
             "(2) the right move scored clearly lower = it misjudges the position (often knockout arithmetic);",
             "(3) the right move not in the list, or a move that shouldn't be legal = engine or move-list bug —",
             "that outranks everything else.",
             "Two identical move lines = the engine lists each copy of a card in hand separately.", ""]
    problems_total = 0
    for group, g in picked:
        seat = g["net_seat"]
        names = {seat: "Bot", 1 - seat: "k3"}
        bots = [None, "k3"] if seat == 0 else ["k3", None]
        title = f"{group} · seed {g['seed']} · bot in seat {seat} ({'first' if seat == 0 else 'second'}) · " \
                f"checkpoint {name} vs k3"
        lines, result, problems = replay(env, dim, g["seed"], bots, {seat: g["moves"], 1 - seat: None},
                                         net, seat, names, title)
        saved = (g["winner"], list(g["points"]), g["turns"])
        if result is None or (result[0], list(result[1]), result[2]) != saved:
            problems.append(f"replay result {result} differs from the saved result {saved}")
        lines += ["", outcome_line(result, names) if result else "Replay stopped early."]
        if problems:
            lines += ["", "REPLAY PROBLEMS: " + " | ".join(problems)]
            problems_total += 1
        fname = f"{group}_seed{g['seed']}_seat{seat}.txt"
        (out_dir / fname).write_text("\n".join(lines) + "\n")
        index.append(f"{fname:<40} {outcome_line(result, names) if result else 'replay stopped'}"
                     + ("   ** REPLAY PROBLEM **" if problems else ""))

    mirror_file = HERE / "results/astra-review/mirror_games.jsonl"
    if a.mirror and mirror_file.exists():
        mg = [json.loads(l) for l in mirror_file.read_text().splitlines() if l.strip()]
        chosen = sorted(mg, key=lambda g: -g["turns"])[:1] + mg[: max(0, a.mirror - 1)]
        for g in chosen:
            names = {0: "k3 (seat 0)", 1: "k3 (seat 1)"}
            env.set_recording(True)
            env.reset(BREW, BREW, g["seed"], ["k3", "k3"])
            lines = [f"baseline · seed {g['seed']} · k3 vs k3 (Astra's mirror baseline)", ""]
            seen_turn = None
            for p, kind, js, view in env.history():
                if kind == "bot" and view:
                    v = json.loads(view)
                    if (v["turn"], p) != seen_turn:
                        seen_turn = (v["turn"], p)
                        lines += ["", "=" * 100] + board_block(v, names)
                    lines.append(f"  {names[p]}: {move_text(js, v['me']['board'], {p: v['me']['board'], 1 - p: v['them']['board']}, p)}")
                else:
                    lines.append(f"  ({names[p]}, only option) {move_text(js)}")
            result = env.result()
            ok = (result[0], list(result[1]), result[2]) == (g["winner"], list(g["points"]), g["turns"])
            lines += ["", outcome_line(result, names)]
            if not ok:
                lines.append(f"REPLAY PROBLEMS: result differs from Astra's saved result {g}")
                problems_total += 1
            fname = f"baseline_k3_vs_k3_seed{g['seed']}.txt"
            (out_dir / fname).write_text("\n".join(lines) + "\n")
            index.insert(9, f"{fname:<40} {outcome_line(result, names)}" + ("" if ok else "   ** REPLAY PROBLEM **"))
    index += ["", f"{len(picked)} bot games; replay problems: {problems_total}"]
    (out_dir / "INDEX.txt").write_text("\n".join(index) + "\n")
    print("\n".join(index))
    print(f"\nWritten to {out_dir}")


if __name__ == "__main__":
    main()
