#!/usr/bin/env python3
"""SKIP_ATTACK.md for the combined run: how often each bot did not attack when it (probably) could have (the pre-registration's
promised comparison, PREREGISTRATION.md line 7, which PAIR_COMBINED.txt does not contain).

  python3 -P skip_attack.py [REPO_ROOT [OUT_FILE]]     (writes SKIP_ATTACK.md next to this file unless OUT_FILE is given)
  python3 -m unittest test_skip_attack                  (from this folder)

Reads only games.jsonl of this run and of the development run (rl/results/strength_2026-10-03_kx3_dev), the same pairing as
pair_combined.py: candidate = this run's arm X, frozen kx3 = the dev run's arm X on the same key, km3 = this run's arm ref (equal to the
dev run's, game for game; checked below). From each game it uses: key, arm, deck, first, turns, and from every logged decision of the
deck's seat: t (game turn), a (the action), act (the Active Pokemon's name before the action), n (how many moves were offered).
The log does not record WHICH moves were offered, so "an attack was available" cannot be read off it; the report says what can be."""
import json, math, os, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[2]
COMB = ROOT / "rl/results/strength_2026-10-08_kx3_combined/games.jsonl"
DEV = ROOT / "rl/results/strength_2026-10-03_kx3_dev/games.jsonl"
GROUPS = {"09-mega-manectric-heliolisk": "fast", "06-mega-blaziken-tournament-list": "fast", "10-xatu-oricorio-tr-weezing": "fast",
          "03-wailord-indeedee-wall": "setup", "01-muk-glimmora-kingambit-regigigas": "setup", "05-indeedee-stoutland": "setup"}
SCOPES = ["all", "fast", "setup", "middle"]
BOTS = ("candidate", "frozen", "km3")


def load(p):
    return {x["key"]: x for x in (json.loads(l) for l in open(p, encoding="utf-8") if l.strip())}


def facts(x):
    return (x["seed"], x["first"], x["winner"], x["points"], x["turns"], x["plies"], x["moves_deck"]["n"], x["moves_opp"]["n"],
            [{k: v for k, v in d.items() if k != "ms"} for d in (x.get("log") or [])])


def turn_records(g):
    """{own turn t: record} for every own turn of the game (t from 1 up to the game's last turn, of the deck's parity).
    out: A the turn has an Attack decision; E it ended with the chosen EndTurn while other moves were offered (n >= 2);
    F anything else: the last logged decision was not EndTurn, so the turn's final EndTurn was forced (nothing else legal: no attack
    was available at the end of the turn), or no decision was logged at all."""
    mine = 1 if g["first"] == "deck" else 0
    byt = defaultdict(list)
    for d in g["log"]:
        if d["t"] % 2 == mine:
            byt[d["t"]].append(d)
    recs = {}
    for t in range(1, g["turns"] + 1):
        if t % 2 != mine:
            continue
        ds = byt.get(t, [])
        atk = [d for d in ds if d["a"].startswith("Attack:")]
        out = "A" if atk else ("E" if ds and ds[-1]["a"] == "EndTurn" else "F")
        recs[t] = {"out": out, "act0": ds[0]["act"] if ds else None, "attacker": atk[0]["act"] if atk else None,
                   "attack": atk[0]["a"][len("Attack:"):] if atk else None, "retreat": any(d["a"].startswith("Retreat") for d in ds)}
    return recs


def cohorts(g):
    """Per game: {cohort: Counter}. after: every own turn after the game's first attack turn. R: a repeat-attacker turn, the Active at
    the start of the turn has the name of the Active that attacked on the previous own turn. R2: the same Pokemon (by name) also
    attacked two own turns back. For R and R2, 'na' counts the turns without an attack and ret / eo / fo split them: a Retreat was
    played; no Retreat and the turn ended by the chosen EndTurn; no Retreat and the end was forced."""
    recs = turn_records(g)
    attacked = [t for t, r in recs.items() if r["out"] == "A"]
    first_a = min(attacked) if attacked else None
    out = {c: Counter() for c in ("own", "after", "R", "R2")}
    for t, r in recs.items():
        out["own"]["n"] += 1
        out["own"][r["out"]] += 1
        if first_a is not None and t > first_a:
            out["after"]["n"] += 1
            out["after"][r["out"]] += 1
        p1, p2 = recs.get(t - 2), recs.get(t - 4)
        is_r = bool(p1 and p1["out"] == "A" and r["act0"] and p1["attacker"] == r["act0"])
        is_r2 = bool(is_r and p2 and p2["out"] == "A" and p2["attacker"] == r["act0"])
        for c, on in (("R", is_r), ("R2", is_r2)):
            if on:
                o = out[c]
                o["n"] += 1
                o[r["out"]] += 1
                if r["out"] != "A":
                    o["na"] += 1
                    o["ret" if r["retreat"] else ("eo" if r["out"] == "E" else "fo")] += 1
                    o["prev:" + p1["attack"]] += 1
    return out


def metric_value(c, m):
    """(numerator, denominator) of one game's metric."""
    kind, coh = m
    key = {"A": "A", "E": "E", "NA": "na", "RET": "ret", "EO": "eo"}[kind]
    return c[coh][key], c[coh]["n"]


METRICS = [("after: attack share", ("A", "after")), ("after: chose-to-end share", ("E", "after")),
           ("R: did-not-attack share", ("NA", "R")), ("R: retreated-instead share", ("RET", "R")),
           ("R: chose-EndTurn share", ("EO", "R")), ("R2: did-not-attack share", ("NA", "R2"))]


def ratio_diff(v1, v2=None):
    """The pooled share of bot 1 (and its paired difference from bot 2's) with a 1.96-SE half width: the ratio estimator over
    games, SE = sqrt(sum w_i^2 / (n (n-1))) with w_i the game's linearised residual (num_i - r den_i) / mean(den), differenced
    between the two bots on the same keys. v1, v2: lists of (num, den) per game, aligned."""
    n = len(v1)
    d1 = sum(x[1] for x in v1)
    if n < 2 or d1 == 0:
        return None
    r1 = sum(x[0] for x in v1) / d1
    w = [(a - r1 * b) / (d1 / n) for a, b in v1]
    r = r1
    if v2 is not None:
        d2 = sum(x[1] for x in v2)
        if d2 == 0:
            return None
        r2 = sum(x[0] for x in v2) / d2
        w = [x - (a - r2 * b) / (d2 / n) for x, (a, b) in zip(w, v2)]
        r = r1 - r2
    se = math.sqrt(sum(x * x for x in w) / (n * (n - 1)))
    return r, 1.96 * se


def pct(x, signed=False):
    return "n/a" if x is None else (f"{100 * x[0]:+.1f} ± {100 * x[1]:.1f}" if signed else f"{100 * x[0]:.1f} ± {100 * x[1]:.1f}")


def main():
    comb, dev = load(COMB), load(DEV)
    xkeys = sorted(k for k, g in comb.items() if g["arm"] == "X")
    same = sum(1 for k, g in comb.items() if g["arm"] == "ref" and k in dev and facts(g) == facts(dev[k]))
    nref = sum(1 for g in comb.values() if g["arm"] == "ref")
    games = {"candidate": {}, "frozen": {}, "km3": {}}
    for k in xkeys:
        kr = k[: -len("X")] + "ref"
        games["candidate"][k], games["frozen"][k], games["km3"][k] = comb[k], dev[k], comb[kr]
    per = {b: {k: cohorts(g) for k, g in games[b].items()} for b in BOTS}
    deck_of = {k: comb[k]["deck"] for k in xkeys}
    decks = sorted(set(deck_of.values()), key=lambda d: (GROUPS.get(d, "middle") != "fast", GROUPS.get(d, "middle") != "setup", d))
    scope_keys = {"all": xkeys}
    for s in SCOPES[1:]:
        scope_keys[s] = [k for k in xkeys if GROUPS.get(deck_of[k], "middle") == s]
    for d in decks:
        scope_keys[d] = [k for k in xkeys if deck_of[k] == d]
    scopes = SCOPES + decks

    def label(s):
        return s if s in SCOPES else f"{s} ({GROUPS.get(s, 'middle')})"

    def tot(b, s, coh, field):
        return sum(per[b][k][coh][field] for k in scope_keys[s])

    L = []
    w = L.append
    # ---- counts
    w("## 3. What the games show, per bot\n")
    w("Counts of the deck's own turns, summed over the games in each row (560 games per bot; 80 per deck). A = a turn with an attack; "
      "E = ended by the chosen EndTurn with other moves offered; F = ended with nothing else legal (the log shows no choice).\n")
    for b in BOTS:
        w(f"### {b}\n")
        w("| scope | games | own turns after the first attack: n | A | E | F | R turns | did not attack | share % | R2 turns | did not attack | share % |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for s in scopes:
            nR, naR, nR2, naR2 = tot(b, s, "R", "n"), tot(b, s, "R", "na"), tot(b, s, "R2", "n"), tot(b, s, "R2", "na")
            w(f"| {label(s)} | {len(scope_keys[s])} | {tot(b, s, 'after', 'n')} | {tot(b, s, 'after', 'A')} | {tot(b, s, 'after', 'E')} | "
              f"{tot(b, s, 'after', 'F')} | {nR} | {naR} | {100 * naR / nR:.1f} | {nR2} | {naR2} | {100 * naR2 / nR2:.1f} |"
              if nR and nR2 else f"| {label(s)} | {len(scope_keys[s])} | {tot(b, s, 'after', 'n')} | {tot(b, s, 'after', 'A')} | {tot(b, s, 'after', 'E')} | "
              f"{tot(b, s, 'after', 'F')} | {nR} | {naR} | - | {nR2} | {naR2} | - |")
        w("")
    # ---- pooled shares and paired differences
    w("## 4. Paired differences (same deck, opponent, deal and seat in both arms)\n")
    w("Each cell: the first bot's pooled share minus the second's, in percentage points, ± 1.96 SE (the ratio estimator over games, "
      "paired on the key; see section 2). Positive in a *did-not-attack* column = the first bot skipped more.\n")
    for b1, b2 in (("candidate", "frozen"), ("candidate", "km3"), ("frozen", "km3")):
        w(f"### {b1} − {b2}\n")
        w("| scope | " + " | ".join(m[0] for m in METRICS) + " |")
        w("|---|" + "---|" * len(METRICS))
        for s in scopes:
            cells = []
            for _, m in METRICS:
                v1 = [metric_value(per[b1][k], m) for k in scope_keys[s]]
                v2 = [metric_value(per[b2][k], m) for k in scope_keys[s]]
                cells.append(pct(ratio_diff(v1, v2), True))
            w(f"| {label(s)} | " + " | ".join(cells) + " |")
        w("")
    w("### Each bot's own pooled shares (± 1.96 SE), for reading the differences against\n")
    w("| bot | scope | " + " | ".join(m[0] for m in METRICS) + " |")
    w("|---|---|" + "---|" * len(METRICS))
    for b in BOTS:
        for s in SCOPES:
            w(f"| {b} | {s} | " + " | ".join(pct(ratio_diff([metric_value(per[b][k], m) for k in scope_keys[s]])) for _, m in METRICS) + " |")
    w("")
    # ---- what the not-attacked R turns look like
    w("## 5. The repeat-attacker turns that did not end in an attack\n")
    w("Counts of the R turns, by what happened (a turn is in exactly one column): an attack; no attack and a Retreat was played that turn; "
      "no attack, no Retreat, and the turn ended by the chosen EndTurn with other moves offered; no attack, no Retreat, and the end "
      "was forced (nothing else legal).\n")
    w("| bot | scope | R turns | attacked | retreated, no attack | chose EndTurn | forced end |")
    w("|---|---|---|---|---|---|---|")
    for b in BOTS:
        for s in SCOPES:
            n, na = tot(b, s, "R", "n"), tot(b, s, "R", "na")
            w(f"| {b} | {s} | {n} | {n - na} | {tot(b, s, 'R', 'ret')} | {tot(b, s, 'R', 'eo')} | {tot(b, s, 'R', 'fo')} |")
    w("")
    w("The attack the same Pokémon had used on the previous own turn, on the R turns without an attack (all 560 games per bot; the ten "
      "most common). An attack that discards its own Energy would explain a turn without an attack by itself; none of these names is "
      "looked up here.\n")
    w("| bot | previous attack (count) |")
    w("|---|---|")
    for b in BOTS:
        prev = Counter()
        for k in xkeys:
            for f, v in per[b][k]["R"].items():
                if f.startswith("prev:"):
                    prev[f[5:]] += v
        w(f"| {b} | " + "; ".join(f"{a} {c}" for a, c in prev.most_common(10)) + " |")
    w("")
    head = {}
    for b in BOTS:
        head[b] = ratio_diff([metric_value(per[b][k], ("NA", "R")) for k in xkeys])
    cf = ratio_diff([metric_value(per["candidate"][k], ("NA", "R")) for k in xkeys], [metric_value(per["frozen"][k], ("NA", "R")) for k in xkeys])
    ck = ratio_diff([metric_value(per["candidate"][k], ("NA", "R")) for k in xkeys], [metric_value(per["km3"][k], ("NA", "R")) for k in xkeys])
    fk = ratio_diff([metric_value(per["frozen"][k], ("NA", "R")) for k in xkeys], [metric_value(per["km3"][k], ("NA", "R")) for k in xkeys])
    diff = lambda b1, b2, m, s="all": ratio_diff([metric_value(per[b1][k], m) for k in scope_keys[s]], [metric_value(per[b2][k], m) for k in scope_keys[s]])
    info = {"same": same, "nref": nref, "n": len(xkeys), "head": head, "cf": cf, "ck": ck, "fk": fk, "diff": diff,
            "nR": {b: tot(b, "all", "R", "n") for b in BOTS}, "naR": {b: tot(b, "all", "R", "na") for b in BOTS},
            "ret": {b: tot(b, "all", "R", "ret") for b in BOTS}, "eo": {b: tot(b, "all", "R", "eo") for b in BOTS},
            "fo": {b: tot(b, "all", "R", "fo") for b in BOTS}, "tot": tot, "scopes": scopes, "label": label}
    return "\n".join(L), info


TOP = """# Skip-attack comparison for the combined run (kx3_combined_v_frozen)

Sonnet "Opus agents progress", for the laptop and Fable; produced by `skip_attack.py` in this folder from the two `games.jsonl` files
(this run's and the development run's). Nothing was run: no engine, no cargo, no new games. The pre-registration (line 7) promised
a comparison of how often each bot skipped an attack it could have made; `PAIR_COMBINED.txt` does not contain it.

## 1. Short answer

**The traces cannot decide "an attack was available" at a decision point, so the pre-registered measure is not produced.** This is
said once here and the definitions are in section 2. What is below is what the files do show:

{short}

## 2. What the log holds, what is used, and the definitions

**Files.** `games.jsonl` of this run (1120 games: 560 candidate arm X, 560 km3 arm ref) and of the development run
`rl/results/strength_2026-10-03_kx3_dev` (its arm X is the frozen kx3, on the same keys). The folder holds no `KX_TRACE` or other
decision record (besides `games.jsonl` it holds `errors.jsonl`, which is empty, `run_log.jsonl`, the manifest and configuration,
the reports and the two scripts). km3: this run's arm ref equals the development run's game for game and decision for decision
({same} of {nref} reference games, `pair_combined.py`'s build check re-run on the fields it compares), so one set of km3 games serves
both runs. The pairing is `pair_combined.py`'s: the same (deck, opponent, deal, seat) key, {n} keys, the candidate against the
frozen kx3 against km3.

**Fields used.** Per game: `key`, `arm`, `deck`, `first` (which seat moved first: `deck` means the deck's turns are the odd game turns),
`turns`. Per logged decision of the deck's seat: `t` (game turn), `a` (the action, e.g. `Attack:Psychic`, `Retreat:2`, `EndTurn`), `act`
(the name of the deck's Active Pokémon before the action) and `n` (how many moves were offered). Not used: `ms`, `p`, `b`, `o`,
`moves_deck`, `moves_opp`, the outcomes. The log keeps only decisions with a real choice (`n` is never 1): a turn whose only legal
move was EndTurn leaves no entry for that move.

**Why "available" cannot be read off.** The log says how many moves were offered (`n`) but not which. When the bot chose EndTurn with
`n >= 2`, an attack may or may not have been among the other moves; the energy on the Active, its attack costs and the opponent's
effects are not logged. Rebuilding them from the log would mean replaying the engine, which is what the pre-registered
`trainer_habits scripted --attack-scan` does (I found no scan output for either arm in the repository, and the tool itself is not
under `rl/` or `engine/`). That replay is the way to get the exact measure.

**What can be shown, by turn.** The deck's *own turns* are the game turns of its parity, 1 up to the game's last turn. Each is exactly one of:
- **A**: the turn has an `Attack:` decision.
- **E**: no attack, and the last logged decision is the chosen `EndTurn` (with `n >= 2`): other moves were still legal. An attack may have been among them.
- **F**: no attack, and the last logged decision is not EndTurn (or none was logged): the final EndTurn was forced, nothing else was legal, so **no attack was available at the end of the turn**.

**Three sets of turns** (a game's turns are counted for each bot separately; a bot that plays differently has different sets):
- **after**: the own turns after the game's first attack turn. Context, not a skip measure: F turns (nothing to attack with, e.g. after a Knock Out) are in it.
- **R, repeat-attacker turns**: the Pokémon that is the Active at the start of the turn has the name of the Active that attacked on the previous own turn. This is the closest the log gets to "an attack was probably available": the same Pokémon, already charged for an attack, stayed in front. It is not certain: an attack that discards its own Energy, a Special Condition or an effect from the opponent's attack can leave nothing to use, and a different copy of the same name would be read as the same. Turns with no logged decision are not in R (the Active is not known).
- **R2**: R, and the same Pokémon (by name) also attacked two own turns back. Stricter, smaller.
On R turns, **did not attack** means not A, split into: a Retreat was played that turn (the attacker was moved out, whatever followed); the chosen EndTurn with other moves offered; a forced end.

**Intervals.** Shares are pooled over games (sum of the counts over the sum of the turns). The interval is ± 1.96 SE of the ratio estimator over
games: for each game the residual `(count - share * turns) / mean(turns)`, and for a difference between two bots on the same key the difference of the two
bots' residuals, SE = sqrt(sum of squares / (n (n - 1))). That is the pre-registration's mean ± 1.96 sd / sqrt(n) generalised to a rate whose
denominator differs by game. Group rows and deck rows are the same computation on their games (240, 240, 80; 80 per deck).

"""

BOTTOM = """
## 6. Reading and limits

{reading}

- **Not the pre-registered measure.** "Km3 proposed an attack, kx3 played something else, and no attack followed that turn" needs km3's proposal at each of the candidate's decisions, which only a replay gives. R turns are a subset where an attack was probably available, chosen from the log alone; they are about {rshare:.0f}% of the own turns, and they leave out the turns where the attacker changed (a new Pokémon was promoted or switched in), where skips may also happen.
- **The sets are each bot's own.** A bot's R turns exist because it attacked last turn, so a bot that skips more earlier has fewer R turns. The paired differences compare each bot's pooled share on its own R turns, not the same turns.
- **Deck effects are large** (the line above): the differences between bots within a deck are mostly inside their intervals, which are for the number of games shown (80 per deck, 240 per group, 560 pooled).
- **Many cells.** Sections 3 and 4 show 3 contrasts x 11 rows x 6 measures at 95%; some will exclude zero by chance. Nothing here was pre-registered as a test, and the retreat figures in section 1 are the ones picked out after looking.
- **A Retreat without an attack is not shown to be a mistake.** It can be a sound move (a damaged attacker moved out, its replacement not yet charged); the table only counts it.
- **Nothing is decided on this.** The pre-registered reading (the pooled interval for the score) is in `PAIR_COMBINED.txt` and is unchanged by it.
"""


def build_doc():
    body, info = main()
    h, d = info["head"], info["diff"]
    pr = lambda x: pct(x)
    sg = lambda x: pct(x, True)
    nR, naR = info["nR"], info["naR"]
    ret, eo, fo = info["ret"], info["eo"], info["fo"]
    short = "\n".join([
        f"1. **Repeat-attacker turns (R)**, the closest proxy for \"an attack was available\": the candidate had {nR['candidate']} such turns and did not attack on "
        f"{naR['candidate']} ({pr(h['candidate'])}%); the frozen kx3 {nR['frozen']} and {naR['frozen']} ({pr(h['frozen'])}%); km3 {nR['km3']} and {naR['km3']} ({pr(h['km3'])}%), "
        f"each over 560 games.",
        f"2. **Paired differences on R turns**, in points of did-not-attack share: candidate − frozen {sg(info['cf'])}; candidate − km3 {sg(info['ck'])}; "
        f"frozen − km3 {sg(info['fk'])}.",
        f"3. Of the turns without an attack: the candidate retreated {ret['candidate']}, chose EndTurn {eo['candidate']}, was forced {fo['candidate']}; "
        f"frozen {ret['frozen']} / {eo['frozen']} / {fo['frozen']}; km3 {ret['km3']} / {eo['km3']} / {fo['km3']}. Paired, the candidate's share of R turns that ended in a "
        f"Retreat without an attack is {sg(d('candidate', 'frozen', ('RET', 'R')))} against the frozen kx3 and {sg(d('candidate', 'km3', ('RET', 'R')))} against km3.",
        f"4. **By group (Dustin's Oct 5 ask)**, did-not-attack share on R turns, candidate / frozen / km3: "
        + "; ".join(f"{g} " + " / ".join(f"{100 * info['tot'](b, g, 'R', 'na') / info['tot'](b, g, 'R', 'n'):.1f}" for b in BOTS) for g in ("fast", "setup", "middle"))
        + f". Candidate − frozen: fast {sg(d('candidate', 'frozen', ('NA', 'R'), 'fast'))}, setup {sg(d('candidate', 'frozen', ('NA', 'R'), 'setup'))}, "
        f"middle {sg(d('candidate', 'frozen', ('NA', 'R'), 'middle'))} (points). The counts for every deck are in section 3, the paired differences in section 4.",
    ])
    cf, ck = info["cf"], info["ck"]
    reading = (
        f"- On R turns the candidate does not skip measurably more than the frozen kx3 (candidate − frozen {sg(cf)}), and is {'above' if ck[0] - ck[1] > 0 else 'not clearly above'} km3 "
        f"(candidate − km3 {sg(ck)}; {'the interval just excludes zero' if ck[0] - ck[1] > 0 else 'the interval includes zero'}). "
        f"The one pattern that stands out is the Retreat: {ret['candidate']} R turns ended with a Retreat and no attack for the candidate, {ret['frozen']} for the frozen kx3, {ret['km3']} for km3; "
        f"as a share of R turns the candidate's is {sg(d('candidate', 'frozen', ('RET', 'R')))} against the frozen kx3 and {sg(d('candidate', 'km3', ('RET', 'R')))} against km3 "
        f"({'both intervals exclude zero' if all(abs(x[0]) > x[1] for x in (d('candidate', 'frozen', ('RET', 'R')), d('candidate', 'km3', ('RET', 'R')))) else 'not both intervals exclude zero'}).\n"
        f"- By group, candidate − frozen on R turns: "
        + "; ".join(f"{g} {sg(d('candidate', 'frozen', ('NA', 'R'), g))} ({'excludes zero' if abs(d('candidate', 'frozen', ('NA', 'R'), g)[0]) > d('candidate', 'frozen', ('NA', 'R'), g)[1] else 'includes zero'})"
                    for g in ("fast", "setup", "middle"))
        + ". Candidate − km3: "
        + "; ".join(f"{g} {sg(d('candidate', 'km3', ('NA', 'R'), g))} ({'excludes zero' if abs(d('candidate', 'km3', ('NA', 'R'), g)[0]) > d('candidate', 'km3', ('NA', 'R'), g)[1] else 'includes zero'})"
                    for g in ("fast", "setup", "middle"))
        + ".\n"
        + "- The two decks with the highest did-not-attack share on R turns, per bot: "
        + "; ".join(f"{b} " + " and ".join(f"{dk} ({100 * info['tot'](b, dk, 'R', 'na') / info['tot'](b, dk, 'R', 'n'):.1f}%)"
                                         for dk in sorted((x for x in info["scopes"] if x not in SCOPES),
                                                          key=lambda x: -info['tot'](b, x, 'R', 'na') / max(1, info['tot'](b, x, 'R', 'n')))[:2])
                    for b in BOTS)
        + ". A deck's own pattern is in every bot's numbers.")
    top = TOP.format(short=short, same=info["same"], nref=info["nref"], n=info["n"])
    rshare = 100 * nR["candidate"] / info["tot"]("candidate", "all", "own", "n")
    return top + body + BOTTOM.format(reading=reading, rshare=rshare)


if __name__ == "__main__":
    out = sys.argv[2] if len(sys.argv) > 2 else str(HERE / "SKIP_ATTACK.md")
    Path(out).write_text(build_doc(), encoding="utf-8", newline="\n")
    print("wrote", out)
