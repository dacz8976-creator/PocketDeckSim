#!/usr/bin/env python3
"""floor.py's pricing-pilot pattern (the Sept 30 engine switch, which moved the floor to km3).

floor.py drops kp's 62 audited texts from the coverage flag only when the pilot is a public-pricing code
(PRICING_PILOT). A pattern that misses a pricing code doesn't crash: the floor flags cards that pilot does price and
can read "untrusted" wrongly. Before Sept 30 the pattern was k(?:[pqd]|og)\\d+, which missed kta3 and km3.

This lists every code B (1f6319e) builds as PublicPricingPlayer (engine/src/players/mod.rs, get_player: the KP, KQ,
KD and KPR arms and the combined arm at lines 668-708) and checks that the pattern matches each of them at any depth,
and does not match k3 or other families. It also reads mod.rs itself, so a pricing code added later without updating
the pattern (or this list) fails here. Last, the screen and the floor must name the same default pilot, a pricing one.

    python3 decks/screen/test_floor_pricing_pilot.py
PLAYERS_MOD_RS=<path> reads another copy of mod.rs (e.g. `git show 1f6319e:engine/src/players/mod.rs`).
"""
import ast, os, re, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import floor  # noqa: E402

# players/mod.rs at 1f6319e: every PlayerCode that get_player wraps in PublicPricingPlayer, by its parse prefix.
PRICING_PREFIXES = (
    "kp", "kq", "kd", "kpr",                                    # their own arms
    "koa", "kob", "kor", "kpf", "kpg", "kog", "koh",            # the combined arm ...
    "kph", "kpha", "kphb", "kt", "kta", "ktb", "ktc", "km",     # ... to km (kta + N2)
)
# Not public-pricing players (k<N> is the plain k search), unknown codes, and codes without a depth: must not match.
NOT_PRICING = ("k1", "k3", "k5", "k10", "e3", "p3", "d3", "t3", "v3", "f3", "g3", "b3", "b3o3n4", "x3", "y3", "s3",
               "r", "v", "h", "et", "er", "kk", "km", "kta", "kog", "kx3", "kpx3", "kmm3", "km3x", "k", "")


def mod_rs():
    path = os.environ.get("PLAYERS_MOD_RS") or os.path.join(ROOT, "engine", "src", "players", "mod.rs")
    with open(path, encoding="utf-8") as f:
        return f.read()


def pricing_variants(src):
    """The PlayerCode variants whose get_player arm builds a PublicPricingPlayer. Arms are split at their heads
    (`PlayerCode::X { max_depth } | ... =>`); heads binding `{ .. }` belong to the inner value-function match and are
    skipped, so the combined arm's body runs to the end of get_player."""
    start = re.search(r"\bfn get_player\(", src).start()
    end = src.find("\n#[cfg(test)]", start)
    body = src[start:end if end > 0 else len(src)]
    heads = []
    for m in re.finditer(r"(?:\|?\s*PlayerCode::\w+\s*(?:\{[^{}]*\})?\s*)+=>", body):
        pats = re.findall(r"PlayerCode::(\w+)\s*(\{[^{}]*\})?", m.group(0))
        if all(re.fullmatch(r"\{\s*\.\.\s*\}", b) for _, b in pats):
            continue
        heads.append((m.start(), m.end(), [v for v, _ in pats]))
    out = set()
    for i, (_, e, variants) in enumerate(heads):
        arm = body[e:heads[i + 1][0] if i + 1 < len(heads) else len(body)]
        if "PublicPricingPlayer" in arm:
            out |= set(variants)
    return out


class PricingPilotPattern(unittest.TestCase):
    def test_every_pricing_code_matches_at_any_depth(self):
        for prefix in PRICING_PREFIXES:
            for depth in (1, 2, 3, 4, 10):
                self.assertTrue(floor.PRICING_PILOT.fullmatch(f"{prefix}{depth}"), f"{prefix}{depth}")

    def test_the_adopted_pilots_match(self):
        for code in ("kp3", "kog3", "kta3", "km3"):
            self.assertTrue(floor.PRICING_PILOT.fullmatch(code), code)

    def test_other_codes_do_not_match(self):
        for code in NOT_PRICING:
            self.assertIsNone(floor.PRICING_PILOT.fullmatch(code), code)

    def test_the_list_is_what_mod_rs_builds(self):
        src = mod_rs()
        found = {v.lower() for v in pricing_variants(src)}
        self.assertEqual(found, set(PRICING_PREFIXES), "PRICING_PREFIXES differs from mod.rs's PublicPricingPlayer arms")
        self.assertNotIn("k", found)                      # the plain k search is not a pricing player
        parse = src[src.index("pub fn parse_player_code("):re.search(r"\bfn get_player\(", src).start()]
        for prefix in PRICING_PREFIXES:                   # each variant parses from its lower-case name
            self.assertIn(f'"{prefix}"', parse, f"parse_player_code has no \"{prefix}\"")

    def test_screen_and_floor_share_a_pricing_default(self):
        with open(os.path.join(HERE, "run_screen.py"), encoding="utf-8") as f:
            tree = ast.parse(f.read())
        defaults = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "add_argument" and node.args \
                    and isinstance(node.args[0], ast.Constant) and node.args[0].value in ("--pilot", "--meta-pilot"):
                for kw in node.keywords:
                    if kw.arg == "default":
                        defaults[node.args[0].value] = kw.value.value
        self.assertEqual(defaults, {"--pilot": floor.FLOOR_PILOT, "--meta-pilot": floor.FLOOR_PILOT})
        self.assertTrue(floor.PRICING_PILOT.fullmatch(floor.FLOOR_PILOT), floor.FLOOR_PILOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
