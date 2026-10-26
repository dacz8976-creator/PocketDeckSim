#!/usr/bin/env python3
"""K21a: the freeze checks that frozen-7's `judge.py compare --allow-other-binaries` skips, restored one by one (coordinator-053, Astra via Dustin).
At judge-prompt-frozen-7 (712593a1), rl/ai_judge/judge.py lines 1000-1009, the switch skips:
  S1  the plan lister executable's sha256 = FROZEN.json plans_binary_sha256 (line 1002);
  S2  freeze_identity.check(FROZEN.json) (line 1007), which is: the prompt fingerprint; the settings (model, prompt version, order, compact threshold,
      token cap, temperature, plan-list generation limits); the judge block (provider, model, thinking level, prices, mapping); the sha256 of each
      of the 19 frozen source files (the judge, formal.py, analysis.py, providers, budget, validation, freeze_identity, the lister's source and
      Cargo.lock, the five test files, lib/card.py, the card database, pgd_patch.py, dg_patch.py, pg_pos.rs); every source being recorded; the
      engine tree (HEAD:engine) = the baseline's 70652fff; the lister executable; the baseline executable;
  S3  (line 1000 -> formal.check_rows line 363) each step-bot row's pg_pos_sha256 = the frozen baseline f35a1a99, for EVERY step bot.
It also marks the report formal: false with experiment_switches ['--allow-other-binaries'] (a label, kept: frozen-7 calls the report "experiment").
What stays on with the switch: the judge rows' frozen flag and their prompt sha re-rendered under the frozen settings (require_frozen), each row's
plan-list hash, the references and eligibility handling, and the experiment flags for any other departure (checked after the compare: the
switches must be exactly ['--allow-other-binaries']).

This script restores S1 and S2 item by item with frozen-7's own functions (judge.frozen_identity, freeze_identity.current/check) in the frozen-7
checkout, and requires freeze_identity.check to return no difference. S3 is restored per row by compare_k21.py: kx3 rows = the K21 binary's sha256
(committed in the launch line before any row; the ONLY permitted difference), km3 rows = f35a1a99.
usage: freeze_checks_k21.py OUT_JSON   (exit 0 only if every item passes)"""
import json, os, subprocess, sys

J = '/home/dacz8976/judge7_w/rl/ai_judge'
TAG_COMMIT = '712593a1b77b203ec23fb15589c158c6bddb2bf2'
FINGERPRINT = '0cb2421552661b563bdb49fca31aca53f468d0853661908fbbf7730fcb5ba762'  # frozen-7's, as K19/run 3 checked it
out = sys.argv[1]
items = []


def item(name, ok, detail=''):
    items.append({'check': name, 'pass': bool(ok), 'detail': detail})


head = subprocess.run(['git', '-C', J, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
item('the judge checkout is the frozen-7 tag commit', head == TAG_COMMIT, head)
dirty = subprocess.run(['git', '-C', J, 'status', '--porcelain', '--untracked-files=no'], capture_output=True, text=True).stdout.strip()
item('the judge checkout has no modified tracked file', dirty == '', dirty[:300])
item('PDL_DB is unset (the card texts come from the frozen lib/deckgym-database.json)', not os.environ.get('PDL_DB'))
sys.path.insert(0, J)
import judge  # noqa: E402
import freeze_identity as fi  # noqa: E402
frozen = judge.frozen_identity()
cur = fi.current()
item('FROZEN.json is frozen-7\'s', frozen.get('tag') == 'judge-prompt-frozen-7' and frozen.get('fingerprint') == FINGERPRINT, frozen.get('tag'))
# S2, item by item
item('S2 prompt fingerprint = FROZEN.json', cur['fingerprint'] == frozen['fingerprint'], cur['fingerprint'][:16])
item('S2 settings (model, prompt version, order, compact threshold, caps, plan-list limits) = FROZEN.json', cur['settings'] == frozen['settings'])
item('S2 judge block (provider gemini-vertex, model gemini-4-argon, thinking HIGH, prices, mapping) = FROZEN.json', cur['judge'] == frozen['judge'],
     json.dumps(frozen['judge'].get('settings')))
for p, hsh in sorted(frozen['source_sha256'].items()):
    item(f'S2 source {p} = FROZEN.json', cur['source_sha256'].get(p) == hsh, (cur['source_sha256'].get(p) or 'missing')[:16])
for p in fi.SOURCES:
    if p not in frozen['source_sha256']:
        item(f'S2 source {p} recorded in FROZEN.json', False)
item('S2 engine tree (HEAD:engine) = the baseline\'s 70652fff', cur['engine_tree'] == frozen['baseline']['engine_tree'] == '70652fff03af511e32a169e16209e158a998dda6', cur['engine_tree'])
# S1 and the executables (required to exist here, not only "when present")
item('S1 the plan lister executable exists and = FROZEN.json plans_binary_sha256 (bd4eeb6e)', os.path.exists(fi.PLANS_BIN) and judge.file_sha256(fi.PLANS_BIN) == frozen['plans_binary_sha256'],
     fi.PLANS_BIN)
item('S2 the baseline executable exists and = FROZEN.json baseline (f35a1a99)', os.path.exists(fi.BASELINE_BIN) and judge.file_sha256(fi.BASELINE_BIN) == frozen['baseline']['binary_sha256'],
     fi.BASELINE_BIN)
db = judge.card_database_path()
item('the card database the prompt quotes is the frozen lib/deckgym-database.json', os.path.abspath(db or '') == os.path.abspath(os.path.join(J, '..', '..', 'lib', 'deckgym-database.json')), db)
# frozen-7's own whole check, exactly as compare calls it at line 1007
diffs = fi.check(frozen)
item('S2 freeze_identity.check(FROZEN.json) returns no difference (the call compare skips)', diffs == [], '; '.join(diffs))
res = {'what': "K21a: the checks `--allow-other-binaries` skips, restored before any kx3 exam row and before the compare", 'tag_commit': TAG_COMMIT,
       'skipped_by_the_switch': {'S1': 'plan lister sha256 (judge.py 1002)', 'S2': 'freeze_identity.check (judge.py 1007)', 'S3': 'per-row baseline sha256 (judge.py 1000, formal.py 363)'},
       'restored_here': ['S1', 'S2'], 'restored_in_compare_k21': 'S3: kx3 rows = the launch line\'s K21 binary sha256; km3 rows = f35a1a99',
       'items': items, 'all_pass': all(i['pass'] for i in items)}
json.dump(res, open(out, 'w'), indent=1)
bad = [i for i in items if not i['pass']]
print(f"freeze checks: {len(items) - len(bad)}/{len(items)} pass" + ('' if not bad else ' | FAILED: ' + '; '.join(i['check'] for i in bad)))
sys.exit(0 if not bad else 1)
