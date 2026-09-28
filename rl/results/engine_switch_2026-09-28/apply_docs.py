"""The pin's doc changes (Dustin's conditions: START_HERE and CLAUDE.md point at the new engine; Fable, Sept 28:
START_HERE carries no status, which moves to RUN5 "Where things stand").
Usage: python3 apply_docs.py <merge commit short sha>"""
import os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
M = sys.argv[1]
SCR = sys.argv[2]  # the draft top (scratch)


CRLF = {}


def rw(rel):
    """Read with line endings normalized to \\n; save() writes them back as the file had them."""
    p = os.path.join(ROOT, rel)
    raw = open(p, "rb").read().decode("utf-8")
    CRLF[p] = "\r\n" in raw
    return p, raw.replace("\r\n", "\n")


def save(p, text):
    if CRLF.get(p):
        text = text.replace("\n", "\r\n")
    open(p, "wb").write(text.encode("utf-8"))


# START_HERE: the new top, the standing sections unchanged, the seed registry.
p, old = rw("START_HERE.md")
top = open(SCR, encoding="utf-8").read().replace("{MERGE}", M)
i0 = old.index("## Before you do anything")
i1 = old.index("## Running now, and seed ranges already used")
middle = old[i0:i1]
middle = middle.replace(
    "## Where things are\n\n",
    "## Where things are\n\n- `rl/RUN5.md`: the approved plan, its rules and \"Where things stand\" (all status). "
    "`rl/results/<topic>_<date>/`: each run's files and reading. `project_manifest.json`: the official engine and its hashes.\n")
j = old.index("**Seed ranges already used.**")
seeds = "## Seed ranges already used\n\n" + old[j:]
new = top.rstrip("\n") + "\n\n" + middle + seeds
save(p, new)
print("START_HERE rewritten:", len(old), "->", len(new), "chars")

# RUN5: "Where things stand", right before the approved plan's order of work.
p, run5 = rw("rl/RUN5.md")
block = f"""**Where things stand** (status; updated with each reading. START_HERE carries none since Sept 28)
- **Official engine:** `rl/engine-2026-09-28/`, main-{M} (pinned Sept 28; rules4 + the ten rules/09 repairs, with the kog, koh, kph and kt players). The rules-file refactor it carries passed RUN5's three-part check (`results/engine_switch_2026-09-28/`).
- **Pilot:** kog3 = kp3 + koa's opening switch A + kpg's discard-Energy credit F.
  - It passed its composition check Sept 28 (`results/kog_composition_2026-09-27/READING.md`) and is "unconfirmed" until the post-freeze read.
  - The screen and the floor use it on both sides; the floor was re-checked under it (`results/floor_recheck_2026-09-28/`).
  - k3 stays the reproduction reference.
- **The yardstick:** scoreboard v3, 45 cells (`results/scoreboard_v3_2026-09-27/`). Development real error: k3 15.3, kp3 15.5, kog3 14.0; the target is 5.5. Every 45-cell reading prints the by-event interval beside the match-level one.
- **Candidates:**
  - koh (kog + R′, kph's registration): footprint 93.4%, so it is read by the ordinary rule. Its runs are in the cloud; nothing else has been read.
  - kt: being re-issued on kog (amendment 2, one review done). No kt game until Dustin's word on its tables.
  - kph is not run (superseded by koh on the composed base).
- **Waiting on post-freeze data:** kpg's confirmation, koa's no-harm re-check and kog's own row (`results/postfreeze_2026-09-27/README.md`). Read once, at 804 + 303 matches (about mid-October) or at the last pull before Mega Garchomp ex.
- **Holds:** deck ranking stays on hold (14.0 against 5.5; the ladder-weighted panel and calibration are unfinished). The floor check may be used under the A2 decision. The quick screen's ranking is on hold.
- **Finished, with where:**
  - kp3 was confirmed on the Sept 25 holdout, which is now spent (`results/holdout_kp3_2026-09-25/`).
  - Not adopted: kd3, kq3, and b3o3n4; kpr3 and kpf "not adopted, provisional".
  - kpg and koa were read (`results/kpg_2026-09-27/`, `results/koa_2026-09-26/`) and composed into kog.
  - The gauntlet: the 45 cells and the variation check (`results/gauntlet_runs_2026-09-26/`).
  - The blind quizzes 1 and 2 (`results/blind_quiz_2026-09-25/`, `results/blind_quiz2_2026-09-27/`).
  - The recordings and frame checks (`results/recordings_check_2026-09-25/`).
  - The engine switches of Sept 25, 27 and 28.
  - The Hydreigon and Altaria detector networks; B2c and B2e; the X Speed census; the brew pilot checks.

"""
anchor = "**Order of work.**\n1. Scoreboard v2 is the table for decisions"
assert run5.count(anchor) == 1
run5 = run5.replace(anchor, block + anchor)
save(p, run5)
print("RUN5: 'Where things stand' inserted")

# CLAUDE.md: the engine paragraph, and two stale lines (the plan's name, the yardstick).
p, cl = rw("CLAUDE.md")
cl2 = re.sub(r"- The official engine program is `rl/engine-2026-09-27/deckgym`.*?(?=\n- `engine/CLAUDE.md`)",
             f"- The official engine program is `rl/engine-2026-09-28/deckgym` (since Sept 28; main-{M}: rules4 plus the ten\n"
             f"  rules/09 repairs, with the kog, koh, kph and kt players; `rl/engine-2026-09-28/README.md`). The working pilot\n"
             f"  is kog3, on both sides of the screen. Earlier programs (`rl/engine-2026-09-27/`, `-09-25/`, `rl/addon-0.7.2/deckgym`)\n"
             f"  are history; the verified add-on 0.7.2 wheel (`rl/addon-0.7.2/wheels/`) is unchanged, and run identities bind\n"
             f"  to it: copy it, never rebuild it.\n"
             f"  Hashes for all of them are in `project_manifest.json`. All are Linux files (WSL or the cloud).",
             cl, flags=re.S)
cl2 = cl2.replace("- Current plan: `rl/RUN5.md`, \"The plan, revised Sept 24\". The yardstick is the 28-matchup table vs\n  Limitless (`rl/results/limitless_check_2026-09-23.md`; tool in `rl/results/deep_search_table/`).",
                  "- Current plan and status: `rl/RUN5.md`, \"The plan, revised Sept 25\" and its \"Where things stand\". The\n  yardstick is scoreboard v3's 45 cells vs Limitless (`rl/results/scoreboard_v3_2026-09-27/`).")
assert cl2 != cl and "engine-2026-09-28" in cl2 and "`engine/CLAUDE.md`" in cl2 and "RUN5.md`, \"The plan, revised Sept 25\"" in cl2, "CLAUDE.md edit incomplete"
save(p, cl2)
print("CLAUDE.md updated")
