"""Run 5 copy of report_v4.py: imports train_v5 and audit_v5, reads the v5_ audit and transfer_v5 files, and adds
(a) the averaging verdict when the run kept an averaged copy, (b) the accepted rules limits for Weezing vs Lucario
(RUN5.md: reported with every result), and (c) no pass/fail wording when the settings have no criteria.
Run 4's own description follows.

Run 4 last step: REPORT.txt in the run folder, from the run's own results (run_training_v4.sh runs it).
    python report_v4.py --run runs/<name>
Verdict (fixed before the run, Fable): PASS if the pass rules hold on each network's best confirmed checkpoint.
The audit and the held-out test are report lines. Their results are included only if they match their current
inputs and are complete; otherwise REPORT.txt says so (Astra's review)."""
import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import train_v5 as T  # noqa: E402
import audit_v5  # noqa: E402


def load_checked(path, expected, what):
    """(summary lines, problem or None) for a cached report result, checked against its current inputs."""
    if not path.exists():
        return [f"({what} not run yet)"], f"{what} not run yet"
    r = json.loads(path.read_text())
    if r.get("inputs") != expected:
        return [f"({what}: the saved result doesn't match its current inputs; rerun run_training_v5.sh to redo it)"], \
            f"{what} out of date"
    if r.get("complete") is False:
        return r["summary"].split("\n"), f"{what} INCOMPLETE ({r['replay_problems']} of its games didn't replay exactly)"
    return r["summary"].split("\n"), None


def run_history(run_dir, st):
    """Everything that happened to the run besides training: interruptions, resumes and any change to its
    recorded inputs. The report carries this itself rather than leaving it to STATUS.txt (Astra, Sept 21)."""
    changes_path = run_dir / "identity_changes.json"
    changes = json.loads(changes_path.read_text()) if changes_path.exists() else []
    if not st.get("flags") and not changes:
        return ["Run history: trained start to finish with no interruptions and no change to its inputs.", ""]
    out = ["Run history (the run's own flags, in order):"]
    out += [f"  - {f}" for f in st.get("flags", [])]
    if changes:
        out.append("Changes to the run's recorded inputs (identity_changes.json):")
        for c in changes:
            out.append(f"  - {c['when']}, at the {c['games_at_last_save']:,}-game save: {c['input']} "
                       f"{c['from_sha256']} -> {c['to_sha256']}. {c['reason']}")
    return out + [""]


def rules_caveat(run_dir, settings):
    """Qualify the affected frozen experiment without changing its numerical verdict."""
    if "altaria" not in settings["pool"]:
        return []
    identity = json.loads((run_dir / "identity.json").read_text())["sha256"]
    if identity.get("add-on") != "797c211f007bceec7288b111c398ef63c898c1eb40447292494b0feb18c62ab1":
        return []
    return [
        "Rules limitation (reviewed September 21, 2026):",
        "  This frozen add-on offers a turn-1 evolution of Benched Swablu into Mega Altaria ex",
        "  when Eevee is Active. Eevee's exception should apply only to Eevee. This was reproduced",
        "  with this run's add-on and decks; its frequency and effect on results were not measured.",
        "  Altaria rows AND columns, including averages containing them, describe this faulty",
        "  simulator. They do not validate Altaria's real-game strength or the bots' handling of it.",
        "  The other networks also trained against this opponent, so effects can extend beyond",
        "  direct Altaria matchups. Shared rule errors need not affect k3 and the networks equally.",
        "  The pass/fail below retains the original experiment's numerical rules. It is not a",
        "  real-game usability verdict. Altaria must not count as validated usable until retrained",
        "  and reevaluated on a corrected engine. Run 5's pool must follow a corrected k3 screen.",
        "",
    ]


def pair_limits(settings):
    """RUN5.md: the accepted rules limits for Weezing vs Lucario are reported with every result."""
    if set(settings["pool"]) != {"weezing", "lucario"}:
        return []
    return ["Accepted rules limits for Weezing vs Lucario (RUN5.md; reported with every result):",
            "  - Reverse Thrust's delayed knockout: the forecast was fixed in add-on 0.7.1/0.7.2.",
            "  - Hoopa's self-knockout finish: the observed tie case is fixed; broader simultaneous-finish variants",
            "    are still unconfirmed.",
            "  - Open question #22: a Checkup on turn 30.",
            "  - Open question #24: how random deck searches are weighted.",
            "  These are simulator results on rules4 and say nothing about unfamiliar decks.", ""]


def level_off_lines(settings, st):
    """Run 4's level-off rule on the live networks, per checkpoint. Shown whether or not the run stopped on it."""
    cps = [c for c in st["checkpoints"] if "leveled" in c]
    if not cps:
        return []
    how = ("The run stops when every network is leveled off at the same checkpoint." if settings.get("stop_on_level_off", True)
           else f"Shown for information only: this run did not stop on it and ran to its {settings['budget']:,}-game budget.")
    return [f"Level-off (run 4's rule, live networks): {settings['level_window']} checkpoints in a row within "
            f"{100 * settings['level_spread']:.0f} points, the newest winning no more than {settings['level_prev_max']:.0%} "
            f"of the games it and the one before it decided differently. {how}"] + \
           [f"  {c['name']:<14}leveled off: {', '.join(c['leveled']) or 'none'}" for c in cps] + [""]


def averaging_verdict(settings, st):
    """Descriptive, no rule: per checkpoint the live and averaged margins side by side, and each copy's average
    change between consecutive checkpoints (RUN5.md's averaging verdict)."""
    hl = settings.get("avg_half_life_games")
    cps = [c for c in st["checkpoints"] if c.get("decks") and c.get("avg")]
    if not hl or not cps:
        return []
    names = list(settings["pool"])
    out = [f"Averaging verdict (descriptive; no rule). The averaged copy: avg = decay x avg + (1 - decay) x live at "
           f"every publish of that network, decay = 0.5 ** (games since its last update / {hl:,}). Margins are points "
           f"over k3 on the same {settings['eval_k3_per_matchup']:,}-game-per-matchup evaluation seeds and seats; "
           f"'change' is the size of the move from the previous checkpoint.", ""]
    out.append(f"  {'checkpoint':<14}" + "".join(f"{n:>44}" for n in names))
    out.append(f"  {'':<14}" + "".join(f"{'live':>9}{'avg':>8}{'avg-live':>10}{'chg live':>9}{'chg avg':>8}" for _ in names))
    prev = None
    ch = {n: {"live": [], "avg": []} for n in names}
    for c in cps:
        row = f"  {c['name']:<14}"
        for n in names:
            lv, av = 100 * c["decks"][n]["margin"], 100 * c["avg"][n]["margin"]
            if prev is not None:
                dl = abs(lv - 100 * prev["decks"][n]["margin"])
                da = abs(av - 100 * prev["avg"][n]["margin"])
                ch[n]["live"].append(dl)
                ch[n]["avg"].append(da)
                tail = f"{dl:>9.1f}{da:>8.1f}"
            else:
                tail = f"{'—':>9}{'—':>8}"
            row += f"{lv:>+9.1f}{av:>+8.1f}{av - lv:>+10.1f}" + tail
        out.append(row)
        prev = c
    out.append("")
    for n in names:
        higher = sum(c["avg"][n]["margin"] > c["decks"][n]["margin"] for c in cps)
        mean = lambda xs: sum(xs) / len(xs) if xs else float("nan")
        out.append(f"  {n}: averaged copy scored higher at {higher} of {len(cps)} checkpoints; average change between "
                   f"consecutive checkpoints: live {mean(ch[n]['live']):.1f} points, averaged {mean(ch[n]['avg']):.1f} "
                   f"points; best live {max(100 * c['decks'][n]['margin'] for c in cps):+.1f}, best averaged "
                   f"{max(100 * c['avg'][n]['margin'] for c in cps):+.1f}.")
    return out + [""]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    run_dir = Path(a.run) if Path(a.run).is_absolute() else HERE / a.run
    S = json.loads((run_dir / "settings.json").read_text())
    st = json.loads((run_dir / "state.json").read_text())
    names = list(S["pool"])
    problems = []
    rec = [line for line in (run_dir / "eval_games.jsonl").read_text().splitlines()
           if '"kind": "bar"' in line or '"kind": "confirmation"' in line]
    L = [f"Run 5 report — {run_dir.name}   ({time.strftime('%Y-%m-%d %H:%M')})", "",
         f"Result: {st['status']} — {st['reason'].split('. The report steps')[0]}", ""]
    tr, ev = st["elapsed_train_s"] / 3600, st.get("elapsed_eval_s", 0) / 3600
    L.append(f"{st['games']:,} games · {tr:.1f} h of training + {ev:.1f} h of evaluation · "
             f"{len([c for c in st['checkpoints'] if c.get('decks')])} checkpoints · one network per deck")
    L.append("")
    L += run_history(run_dir, st)
    L += rules_caveat(run_dir, S)
    L += pair_limits(S)
    L += level_off_lines(S, st)
    L += averaging_verdict(S, st)
    v = st.get("verdict")
    if v and v.get("pass") is None:
        L += [f"Best confirmed checkpoint per network, live or averaged "
              f"({', '.join(f'{d} {c}' for d, c in sorted(v['picks'].items()))}). No pass/fail rule in code: "
              f"RUN5.md's '+5' decision is read from the confirmation lines below.", "",
              "  Margin by matchup, points (row = the deck's own network, column = the deck k3 pilots):"]
        L += ["  " + r for r in T.grid(names, v["margins"], "{:+.0f}", scale=100)]
        L.append("")
    elif v:
        L += [f"The pass rules, on each network's best confirmed checkpoint "
              f"({', '.join(f'{d} {c}' for d, c in sorted(v['picks'].items()))}):"]
        L += [f"  - {x['text']} → {'yes' if x['ok'] else 'NO'}" for x in v["criteria"]]
        L += [f"  → {'PASS' if v['pass'] else 'Not a pass'}.", "",
              "  Margin by matchup, points (row = the deck's own network, column = the deck k3 pilots):"]
        L += ["  " + r for r in T.grid(names, v["margins"], "{:+.0f}", scale=100)]
        L.append("")
    for cf in st["confirmations"]:
        chosen = " (used for the verdict)" if v and v["picks"].get(cf["deck"]) == cf["name"] else ""
        L += [f"Confirmation of the {cf['deck']} network's {cf['name']}{chosen}: {S['confirm_per_matchup']:,} games "
              f"per matchup on the bars' own seeds (paired). Margin over k3 {100 * cf['margin']:+.1f} points.",
              f"  {'matchup':<22}{'network':>9}{'k3, same deck':>15}{'margin':>9}   games won only by"]
        for t in sorted(cf["rates"], key=lambda t: names.index(t.split(">")[1])):
            r, p, bar = cf["rates"][t], cf["paired"][t], st["bars"][t]
            L.append(f"  {t.replace('>', ' vs '):<22}{r['win_rate']:>9.1%}{bar['win_rate']:>15.1%}"
                     f"{100 * cf['margins'][t]:>+8.1f}   network {p['bot_only']:>4} / k3 {p['k3_only']:>4} (p {p['p']:.2g})")
        L.append("")
        au = HERE / f"results/ko_audit/v5_{run_dir.name}_{cf['deck']}_{cf['name']}.json"
        conf_rec = [line for line in rec if '"kind": "confirmation"' in line
                    and json.loads(line).get("ckpt") == cf["name"] and json.loads(line).get("deck") == cf["deck"]]
        bar_rec = [line for line in rec if '"kind": "bar"' in line and cf["deck"] in json.loads(line)["decks"]]
        exp = T.report_inputs("audit", run_dir, S, cf["name"], ["audit_v5.py"], conf_rec + bar_rec,
                              nets={cf["deck"]: cf["name"]})
        exp["K"] = audit_v5.K
        exp["deck"] = cf["deck"]
        lines, prob = load_checked(au, exp, f"audit of the {cf['deck']} network's {cf['name']}")
        L += lines + [""]
        problems += [prob] if prob else []
    if v and not S.get("held_out"):
        L.append("Held-out test: not part of this run (its settings name no held-out deck).")
    elif v:
        name = "+".join(sorted(set(v["picks"].values())))
        tf = HERE / f"results/transfer_v5_{run_dir.name}_{name}.json"
        exp = T.report_inputs("transfer", run_dir, S, sorted(v["picks"].items())[0][1], ["transfer_v5.py"],
                              nets=v["picks"])
        exp["picks"] = v["picks"]
        lines, prob = load_checked(tf, exp, "held-out test")
        L += lines
        problems += [prob] if prob else []
    else:
        L.append("No network was confirmed (the run stopped before leveling off); see STATUS.txt.")
    if problems:
        L[3:3] = ["Report problems: " + "; ".join(problems) + "."]
    text = "\n".join(L) + "\n"
    (run_dir / "REPORT.txt").write_text(text)
    status = (run_dir / "STATUS.txt").read_text()
    marker = "\nThe full report: REPORT.txt"
    if marker not in status:
        (run_dir / "STATUS.txt").write_text(status + marker + " (verdict, confirmations, audit and held-out test).\n")
    print(text)


if __name__ == "__main__":
    main()
