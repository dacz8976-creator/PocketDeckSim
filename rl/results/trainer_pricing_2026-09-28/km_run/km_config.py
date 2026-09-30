#!/usr/bin/env python3
"""km_config.py: reads and checks km_config.json, km's one set of candidate, baseline, reference files and program hashes
(../REGISTRATION_DRAFT.md, Amendment 1 (Sept 30), (b) item 3: "The runner and the reader use this set and no other").
run_km.sh (through `shell`), km_check.py, footprint_km.py and read_km.py (through load()) take every build, baseline,
reference file and hash from it; none of them names one of its own.

  km_config.py check [--config F]    check the file; print the set it names; exit 0, or 2 naming what is wrong or unset
  km_config.py shell [--config F]    the same checks, then the set as bash assignments for run_km.sh to eval

A null value is required and not known yet (the cloud reports it with B's round): every command, and so every script,
refuses to run until it is set. The values the committed amendment fixes (the codes, the kt build, the official engine,
the counter tool's source and its sha256, and kta3's eight reference files with their sha256, pairings, deals, seed
bases and pairs files) are constants here as well: the JSON carries them too, and any value unlike the constant's is
refused, naming the amendment's item. The JSON's own values are the ones the cloud reports (B, its branch, round head
and round folder, the cloud's outputs). What is checked here is the file alone; git, the files' sha256 and their games
are checked by run_km.sh (part B, km_check.py refs, km_check.py one-list) and read_km.py. After part I, km's one list
(<out>/km_inputs.sha256, Amendment 1 (b) item 4) pins the config's bytes and the set it names.
"""
import argparse, json, os, re, shlex, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT = os.path.join(HERE, "km_config.json")
CANDIDATE, BASELINE = "km3", "kta3"   # Amendment 1 (b) items 1-2: km3 = kta3 + N2, read against kta3 in every test
GROUPS = ("table", "new17", "b2e", "scizor", "var_v-lucario_2", "var_v-suicune_2", "var_v-weezing_2", "var_l-charizardy")
# The committed amendment's values (REGISTRATION_DRAFT.md, Amendment 1, committed at 3aed736), fixed here so that an
# edited km_config.json cannot move km onto another baseline, build or reference file (Dustin, Sept 30: "one consistent
# set of candidate, baseline, reference files and program hashes").
KT_BUILD = "ec7e1a867bdaae2b0b4a3d2730e36dfffb611900"          # (b) item 1: kta<N> is exactly ec7e1a8's
OFFICIAL_ENGINE = "233bced99cf99b2a90aededaa48d1381ef147400"   # (c) item 2: B's engine/ diff from it is players/ only too
TOOL_SOURCE_PATH = "rl/results/tool_turn_effect_census_2026-09-25/tool_census.rs"                  # (e) item 2
TOOL_SOURCE_SHA = "05d7ba4183ce9e3098036de9acb5181ea71f7077ef9b3798ad4e5d165dc22365"                # (e) item 2
REF_FOLDER = "rl/results/kt_tables_2026-09-28"                                                      # (b) item 3
_NEW = "rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv"
_VAR = "rl/results/gauntlet_runs_2026-09-26/tsv/var_{}.tsv"
# (b) item 3's eight files: file, sha256 (its list, "on main (Sept 30)"), pairings, deals, games, seed base ((e) item 3,
# "Deals"), pairs file (None: legality_scan's --decks table). `km_check.py refs --committed` checks each file against it.
REFERENCES = {
    "table": ("ec7e1a8_kta3_table.jsonl", "6b90d3cfa24e17815026dab7c787df327cfc859e491d1399889aaa2369a3c73b",
              list(range(28)), 500, 14000, 72_000_000, None),
    "new17": ("ec7e1a8_kta3_new17.jsonl", "1803e256e45d2d5a6208d61854067e88e05af51315cd4eefecda33c2f84603ba",
              list(range(8, 25)), 500, 8500, 21_108_000_000, _NEW),
    "b2e": ("ec7e1a8_b2e_kta3.jsonl", "38abd687e38c27285383616876729fd465bc4e42fe9445cddfe17ca7cde468ae",
            list(range(96)), 500, 48000, 21_106_000_000, "rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv"),
    "scizor": ("ec7e1a8_scizor_kta3.jsonl", "6b27a513f0709510e75cdf360bb44d13b6044481307bb33e681723d735523839",
               list(range(8)), 500, 4000, 21_108_000_000, _NEW),
    "var_v-lucario_2": ("ec7e1a8_var_v-lucario_2_kta3.jsonl", "d44a4c30f442c74ea46f50cc53c1ce7e399adc2ee90667c81dc540b5b35fc6a0",
                        [2, 8, 13, 18, 19, 20, 21], 500, 3500, 72_000_000, _VAR.format("v-lucario_2")),
    "var_v-suicune_2": ("ec7e1a8_var_v-suicune_2_kta3.jsonl", "c3f763bfe68f34246bd50c6bfd3e1d8df4063384bff0d007a5f8df2a5a8ceab5",
                        [4, 10, 15, 19, 22, 25, 26], 500, 3500, 72_000_000, _VAR.format("v-suicune_2")),
    "var_v-weezing_2": ("ec7e1a8_var_v-weezing_2_kta3.jsonl", "9bb448868dd027f74edd38ec766cf961a8cc71b06d483e14d629cddb5cd85f8c",
                        [6, 12, 17, 21, 24, 26, 27], 500, 3500, 72_000_000, _VAR.format("v-weezing_2")),
    "var_l-charizardy": ("ec7e1a8_var_l-charizardy_kta3.jsonl", "7980b996618ef0efbac8392db0a73a25a9466c700ddab70d58ee35b64ce0d271",
                         list(range(40, 48)), 500, 4000, 21_106_000_000, _VAR.format("l-charizardy")),
}
REF_FIELDS = ("file", "sha256", "pairings", "deals", "games", "seed_base", "pairs")
# History, refused as B (Amendment 1 (c) item 1: "No evaluation game, threshold-sample game or laptop identity game is
# played at 9c11b30, and no 9c11b30 file is a reference for km"). Named here only to be refused.
NOT_B = {"9c11b305b4f9886e295ef546b787171af4633f37": "9c11b30, km on kog (kog + N2): implementation evidence only"}
OLD_ROUND_FOLDER = "rl/results/km_build_2026-09-29"   # 9c11b30's round; B's round is a new folder ((c) item 3)
HEX40, HEX64 = re.compile(r"^[0-9a-f]{40}$"), re.compile(r"^[0-9a-f]{64}$")


class ConfigError(Exception):
    pass


def _get(d, path):
    for k in path:
        if not isinstance(d, dict) or k not in d:
            raise ConfigError(f"km_config.json has no {'.'.join(path)}")
        d = d[k]
    return d


def load(path=None, require=True):
    """The checked set: the JSON with derived fields added (prefix, each reference's repo path). With require, a null
    required value is an error; without, missing() lists them (the others are still checked)."""
    path = path or DEFAULT
    try:
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
    except (OSError, ValueError) as e:
        raise ConfigError(f"{path} cannot be read as JSON ({e})")
    errs, unset = [], []

    def need(p, rx=None, what=""):
        v = _get(c, p)
        if v is None:
            unset.append(".".join(p))
            return None
        if rx is not None and not (isinstance(v, str) and rx.match(v)):
            errs.append(f"{'.'.join(p)} = {v!r} is not {what}")
        return v

    cand, base = _get(c, ("comparison", "candidate")), _get(c, ("comparison", "baseline"))
    if cand != CANDIDATE:
        errs.append(f"comparison.candidate is {cand!r}; km's candidate is {CANDIDATE!r} (Amendment 1 (b) item 1)")
    if base != BASELINE:
        errs.append(f"comparison.baseline is {base!r}; km is read against {BASELINE!r} in every test (Amendment 1 (b) "
                    f"item 2: 'Wherever the registered text names kog3 as km's baseline ... read kta3')")
    kt = need(("build", "kt_build"), HEX40, "a 40-digit commit")
    off = need(("build", "official_engine"), HEX40, "a 40-digit commit")
    if kt != KT_BUILD:
        errs.append(f"build.kt_build is {kt!r}, not the kt build {KT_BUILD} (Amendment 1 (b) item 1: kta<N> is exactly ec7e1a8's)")
    if off != OFFICIAL_ENGINE:
        errs.append(f"build.official_engine is {off!r}, not {OFFICIAL_ENGINE} (Amendment 1 (c) item 2)")
    commit = need(("build", "commit"), HEX40, "a 40-digit lower-case commit hash (B, as BUILD.md names it)")
    if commit is not None:
        if commit in NOT_B:
            errs.append(f"build.commit is {NOT_B[commit]}, never the build km is played on (Amendment 1 (c) item 1)")
        if commit in (kt, off):
            errs.append("build.commit is the kt build or the official engine's commit, not B (B adds N2 to ec7e1a8's players/)")
    br = need(("build", "branch"))
    if br is not None and not (isinstance(br, str) and br.startswith("origin/") and len(br) > 7):
        errs.append(f"build.branch = {br!r} is not a remote branch (origin/...)")
    need(("build", "round_head"), HEX40, "a 40-digit commit")
    rf = need(("build", "round_folder"), re.compile(r"^rl/results/km_build_\d{4}-\d{2}-\d{2}$"), "rl/results/km_build_<date of B>")
    if rf == OLD_ROUND_FOLDER:
        errs.append(f"build.round_folder is {OLD_ROUND_FOLDER}, 9c11b30's round; B's round is a new folder (Amendment 1 (c) item 3)")
    if need(("counter_tool", "source_path")) != TOOL_SOURCE_PATH:
        errs.append(f"counter_tool.source_path is not {TOOL_SOURCE_PATH} (Amendment 1 (e) item 2)")
    if need(("counter_tool", "source_sha256"), HEX64, "a sha256") != TOOL_SOURCE_SHA:
        errs.append(f"counter_tool.source_sha256 is not {TOOL_SOURCE_SHA} (Amendment 1 (e) item 2: 'A source with any other "
                    f"hash is not built or used')")
    for k in ("km3_smoke", "tool_test3_rows", "tool_test3_trace"):
        p = need(("cloud_outputs", k, "path"))
        if p is not None and rf is not None and not (isinstance(p, str) and p.startswith(rf + "/")):
            errs.append(f"cloud_outputs.{k}.path = {p!r} is not in B's round folder {rf}")
        need(("cloud_outputs", k, "sha256"), HEX64, "a sha256")
    for k in ("tool_test1_stdout_sha256", "tool_test1_games_sha256"):
        need(("cloud_outputs", k), HEX64, "a sha256")
    sm = _get(c, ("cloud_outputs", "km3_smoke"))
    if sm.get("code") != CANDIDATE or sorted(sm.get("pairings") or []) != [0, 2, 19] or sm.get("deals") != 40 \
            or sm.get("seed_base") != 72_000_000:
        errs.append("cloud_outputs.km3_smoke is not km3 on table pairings 0, 2 and 19, i < 40, seeds 72,000,000 + pairing x "
                    "10,000 + i (Amendment 1 (c) item 4, identity 7)")
    folder = _get(c, ("references", "folder"))
    if folder != REF_FOLDER:
        errs.append(f"references.folder is {folder!r}, not {REF_FOLDER} (Amendment 1 (b) item 3: kta3's committed games at "
                    f"ec7e1a8 on the development deals; kta's fresh files are 'Not references for km')")
    if _get(c, ("references", "code")) != BASELINE:
        errs.append(f"references.code is not {BASELINE!r}")
    groups = _get(c, ("references", "groups"))
    if set(groups) != set(GROUPS):
        errs.append(f"references.groups are {sorted(groups)}; Amendment 1 (b) item 3 names {list(GROUPS)}")
    refs = {}
    for g in GROUPS:
        e = groups.get(g)
        if not isinstance(e, dict):
            continue
        want = dict(zip(REF_FIELDS, REFERENCES[g]))
        bad = [f for f in REF_FIELDS if e.get(f) != want[f]]
        if bad:
            errs.append(f"references.groups.{g}: {', '.join(f'{f} {e.get(f)!r}' for f in bad[:2])}{' ...' if len(bad) > 2 else ''} "
                        f"not Amendment 1 (b) item 3's ({', '.join(f'{f} {want[f]!r}' for f in bad[:2])}): the reference "
                        f"files are kta3's ec7e1a8 both-sides files with the sha256 its list gives; a step-5 replacement "
                        f"baseline would enter only through km_inputs.sha256 and a dated STATUS.txt line ((b) item 4), and "
                        f"it has no code until Dustin approves one")
        fn = e.get("file") or ""
        refs[g] = dict(e, path=f"{folder}/{fn}", pairings=list(e.get("pairings") or []))
    if _get(c, ("programs", "pins")) != "programs.txt":
        errs.append("programs.pins must be programs.txt (the file part B writes and read_km.py reads)")
    if errs:
        raise ConfigError(f"{path}: " + "; ".join(errs))
    if require and unset:
        raise ConfigError(f"{path}: required values not set yet: {', '.join(unset)}. They come with B's round (the cloud "
                          f"reports them); nothing runs until they are set")
    c["_path"], c["_unset"] = os.path.abspath(path), unset
    c["prefix"] = commit[:7] if commit else None
    c["refs"] = refs
    return c


def missing(c):
    return list(c.get("_unset", []))


def summary(c):
    b, co = c["build"], c["cloud_outputs"]
    lines = [f"km_config: {c['_path']}",
             f"  candidate {c['comparison']['candidate']}, baseline {c['comparison']['baseline']}",
             f"  build B {b['commit'] or 'NOT SET'} (file prefix {c['prefix'] or 'NOT SET'}); branch {b['branch']}; "
             f"round head {b['round_head'] or 'NOT SET'}; round folder {b['round_folder'] or 'NOT SET'}",
             f"  engine/ diff from the kt build {b['kt_build'][:7]} (and the official {b['official_engine'][:7]}): players/ only, "
             f"engine/UPSTREAM.md aside (Amendment 1 (c) item 2)",
             f"  counter tool source {c['counter_tool']['source_path']} sha256 {c['counter_tool']['source_sha256']}",
             f"  km3 smoke {co['km3_smoke']['path'] or 'NOT SET'} ({co['km3_smoke']['sha256'] or 'sha256 NOT SET'})",
             f"  tool test 3 rows {co['tool_test3_rows']['path'] or 'NOT SET'}, trace {co['tool_test3_trace']['path'] or 'NOT SET'}; "
             f"test 1 stdout {co['tool_test1_stdout_sha256'] or 'NOT SET'}, games {co['tool_test1_games_sha256'] or 'NOT SET'}",
             f"  references ({c['references']['code']} both sides, {c['references']['folder']}):"]
    for g in GROUPS:
        r = c["refs"][g]
        lines.append(f"    {g:17} {r['file']:38} {r['games']:>6} games, {len(r['pairings'])} pairings x i < {r['deals']}, "
                     f"seed {r['seed_base']:,} + pairing x 10,000 + i, sha256 {r['sha256'][:16]}...")
    lines.append(f"  programs: <out>/{c['programs']['pins']} (written by part B, checked by every later part and the reader)")
    if c["_unset"]:
        lines.append(f"  NOT SET (required): {', '.join(c['_unset'])}")
    return "\n".join(lines)


def shell(c):
    b, co = c["build"], c["cloud_outputs"]
    q = shlex.quote
    kv = [("CFG_CAND", c["comparison"]["candidate"]), ("CFG_BASE", c["comparison"]["baseline"]), ("COMMIT", b["commit"]),
          ("S", c["prefix"]), ("BRANCH", b["branch"]), ("ROUND_HEAD", b["round_head"]), ("ROUND_DIR", b["round_folder"]),
          ("KT_BUILD", b["kt_build"]), ("OFFICIAL", b["official_engine"]),
          ("TOOL_SRC", c["counter_tool"]["source_path"]), ("TOOL_SRC_SHA", c["counter_tool"]["source_sha256"]),
          ("SMOKE_SRC", co["km3_smoke"]["path"]), ("SMOKE_SHA", co["km3_smoke"]["sha256"]),
          ("SMOKE_PAIRINGS", ",".join(map(str, co["km3_smoke"]["pairings"]))), ("SMOKE_DEALS", str(co["km3_smoke"]["deals"])),
          ("T3_ROWS_SRC", co["tool_test3_rows"]["path"]), ("T3_ROWS_SHA", co["tool_test3_rows"]["sha256"]),
          ("T3_TRACE_SRC", co["tool_test3_trace"]["path"]), ("T3_TRACE_SHA", co["tool_test3_trace"]["sha256"]),
          ("T1_STDOUT_SHA", co["tool_test1_stdout_sha256"]), ("T1_GAMES_SHA", co["tool_test1_games_sha256"]),
          ("PINS_NAME", c["programs"]["pins"]), ("CFG_FILE", c["_path"])]
    out = [f"{k}={q(str(v))}" for k, v in kv]
    for name, fn in (("REFS", lambda r: r["path"]), ("REFSHA", lambda r: r["sha256"]), ("REFPAIRS", lambda r: r["pairs"] or ""),
                     ("REFSEED", lambda r: str(r["seed_base"])), ("REFDEALS", lambda r: str(r["deals"])),
                     ("REFPAIRINGS", lambda r: ",".join(map(str, r["pairings"])))):
        out.append(f"declare -gA {name}=(" + " ".join(f"[{g}]={q(fn(c['refs'][g]))}" for g in GROUPS) + ")")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["check", "shell"])
    ap.add_argument("--config", default=DEFAULT)
    a = ap.parse_args()
    try:
        c = load(a.config, require=(a.cmd == "shell"))
    except ConfigError as e:
        print(f"km_config: STOP: {e}", file=sys.stderr)
        sys.exit(2)
    if a.cmd == "check":
        print(summary(c))
        if missing(c):
            print(f"km_config: the file is well formed, but {len(missing(c))} required values are not set: every script "
                  f"refuses to run until they are", file=sys.stderr)
            sys.exit(2)
        print("km_config: complete")
    else:
        print(shell(c))


if __name__ == "__main__":
    main()
