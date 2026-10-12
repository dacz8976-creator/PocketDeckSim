#!/usr/bin/env bash
# Real-binary smoke of slow_report.py: the pinned frozen program, but the cheap pilot km3 on both seats (about a second a game; no kx3 game is played).
# The pin is a copy with pilot km3 so the headline says so. Everything else is the real path: pre-registration, the real program, the real report,
# a held-out deck's content (stage use), the km3 baseline on by default, nohup + SIGHUP, a second wrapper refused, SIGTERM in the middle and a resume.
S=/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/2007fbb0-8999-4f68-b5ad-afe643bc4e30/scratchpad/sr
exec > "$S/smoke4.log" 2>&1
R="$S/work/repo"
cd "$R/rl/strength"
SM=$HOME/slow_smoke2
rm -rf "$SM"; mkdir -p "$SM"
python3 - "$SM" <<'EOF'
import json, sys
p = json.load(open('slow_report_pin.json'))
p['pilot'] = 'km3'; p['pilot_label'] = 'km3 (smoke, not kx3)'
p['reference'] = 'km3'; p['reference_label'] = 'km3'
p['seed_reserved'] = []  # the real pin reserves the slots THESE smoke runs take (684-686); the smoke's own copy must not skip them
json.dump(p, open(sys.argv[1] + '/pin_smoke.json', 'w'), indent=1)
print('pin program sha:', p['program_sha256'][:12], 'program', p['program'])
EOF
mkdir -p "$R/decks/events"
cp "$R/decks/dustin/07-skarmory-stall.txt" "$R/decks/events/smoke-held.txt"
PIN="$SM/pin_smoke.json"
export SLOW_REPORT_ALLOW_UNCOMMITTED_PIN=1  # test only: this pin is a copy, not the committed one
echo "== 1. dry run"
python3 -B slow_report.py "$R/decks/events/smoke-held.txt" --repo "$R" --pin "$PIN" --out-root "$SM/runs" --date 2026-10-07 --deals 2 --dry-run
echo "exit: $?"; ls "$SM/runs" 2>&1 | head -2

echo "== 2. real run under nohup, SIGHUP sent in the middle, a second wrapper refused meanwhile"
nohup python3 -B slow_report.py "$R/decks/events/smoke-held.txt" --repo "$R" --pin "$PIN" --out-root "$SM/runs" --date 2026-10-07 --deals 2 --school-rule off --threads 2 > "$SM/run1.out" 2>&1 &
W=$!
D="$SM/runs/2026-10-07_smoke-held"
for i in $(seq 1 100); do [ -f "$D/games.jsonl" ] && break; sleep 0.1; done
sleep 1
kill -HUP "$W"
sleep 1
if kill -0 "$W" 2>/dev/null; then echo "wrapper still alive after SIGHUP (nohup honoured)"; else echo "WRAPPER DIED ON SIGHUP"; fi
python3 -B slow_report.py --dir "$D" --repo "$R" --pin "$PIN" --school-rule off 2>&1 | tail -2
echo "second wrapper exit: ${PIPESTATUS[0]}"
wait "$W"; echo "first wrapper exit: $?"
echo "games: $(wc -l < "$D/games.jsonl") (planned 64)"
ls -la "$D"
echo "== log"; cat "$D/slow_report_log.jsonl"
echo "== SLOW_REPORT.md"; cat "$D/SLOW_REPORT.md"

echo "== 3. a second run, SIGTERM in the middle, then resume"
nohup python3 -B slow_report.py "$R/decks/events/smoke-held.txt" --repo "$R" --pin "$PIN" --out-root "$SM/runs" --date 2026-10-08 --deals 2 --school-rule off --threads 2 > "$SM/run2.out" 2>&1 &
W=$!
D2="$SM/runs/2026-10-08_smoke-held"
for i in $(seq 1 200); do n=$(wc -l < "$D2/games.jsonl" 2>/dev/null || echo 0); [ "${n:-0}" -ge 6 ] && break; sleep 0.1; done
kill -TERM "$W"
wait "$W"; echo "wrapper exit after SIGTERM: $? (143 expected)"
echo "games after SIGTERM: $(wc -l < "$D2/games.jsonl")"
sleep 1
echo "program processes left running: $(pgrep -f "$D2/manifest.json" | wc -l) (0 expected)"
ls "$D2" | tr '\n' ' '; echo
python3 -B slow_report.py --dir "$D2" --repo "$R" --pin "$PIN" --school-rule off 2>&1 | tail -4
echo "games after resume: $(wc -l < "$D2/games.jsonl")"
python3 - "$D2/games.jsonl" <<'EOF'
import json, sys
keys = [json.loads(l)['key'] for l in open(sys.argv[1])]
print('distinct keys', len(set(keys)), 'of', len(keys), 'lines')
EOF
echo "== 4. manifest keys of interest"
python3 - "$D/manifest.json" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
print({k: m[k] for k in ('stage','heldout_decks','heldout_registry','heldout_in_run','heldout_locked','planned_games','seed_base','selfcheck_source')})
print('paired:', m['slow_report']['paired'], 'resume_command:', m['slow_report']['resume_command'])
EOF
echo "== 5. the cloud route with a REAL rebuild: rl/strength/build.sh builds the pinned source (engine ref d513e37b) to a path of its own and writes the build record beside it"
MAINREPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"   # only read: git archive / rev-parse of the pinned commit
mkdir -p "$SM/rebuilt"
build_it() {  # build_it BUILD_DIR TARGET_DIR
    env STRENGTH_REPO="$MAINREPO" STRENGTH_BUILD_DIR="$1" STRENGTH_TARGET_DIR="$2" CARGO_HOME="${CARGO_HOME:-$HOME/.cargo}" bash "$R/rl/strength/build.sh" d513e37b473f2819075e1eb2439075a8a1e65c42 "$SM/rebuilt/strength"
}
time build_it "$SM/build1" "$SM/target1" 2>&1 | tail -8
echo "-- build record (selected)"
python3 - "$SM/rebuilt/strength.build.json" <<'EOF'
import json, sys
r = json.load(open(sys.argv[1]))
pin = json.load(open('slow_report_pin.json'))
print({k: (r[k][:12] if isinstance(r[k], str) and len(r[k]) > 30 else r[k]) for k in ('schema', 'engine_arg', 'engine_ref', 'engine_tree_archived', 'harness_source_sha256', 'program_sha256', 'jobs', 'built_at')})
print('rustc:', r['rustc'].splitlines()[0], '| cargo:', r['cargo'], '| machine:', r['machine'], '| host:', r['host'])
print('pin engine_tree', pin['engine_tree'][:12], 'equal:', r['engine_tree_archived'] == pin['engine_tree'], '| pin harness equal:', r['harness_source_sha256'] == pin['harness_source_sha256'], '| program is the pinned sha:', r['program_sha256'] == pin['program_sha256'])
print('rebuild_command:', r['rebuild_command'])
EOF
echo "-- registering with --program (the rebuild), school rule off, register only; the pin is the smoke copy, not the committed one: refused first, then with the test-only variable"
unset SLOW_REPORT_ALLOW_UNCOMMITTED_PIN
python3 -B slow_report.py "$R/decks/events/smoke-held.txt" --repo "$R" --pin "$PIN" --out-root "$SM/runs" --date 2026-10-09 --deals 2 --program "$SM/rebuilt/strength" --school-rule off --register-only
echo "exit: $? (refused: the pin is not the committed one)"
export SLOW_REPORT_ALLOW_UNCOMMITTED_PIN=1
python3 -B slow_report.py "$R/decks/events/smoke-held.txt" --repo "$R" --pin "$PIN" --out-root "$SM/runs" --date 2026-10-09 --deals 2 --program "$SM/rebuilt/strength" --school-rule off --register-only
echo "exit: $?"
D3="$SM/runs/2026-10-09_smoke-held"
echo "-- manifest: program, route, pin state, self-check sources, school choice, resume command, build record"
python3 - "$D3/manifest.json" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
s = m['slow_report']
print({'program': m['program'], 'program_sha256': m['program_sha256'][:12], 'program_route': s['program_route'], 'pinned_program_sha256': s['pinned_program_sha256'][:12],
       'pin_committed': s['pin_committed'], 'registered_on': s['registered_on'], 'selfcheck_source': m['selfcheck_source'], 'school_rule': s['school_rule'], 'school_days': s['school_days'],
       'harness_source_sha256': s['harness_source_sha256'][:12], 'harness_checkout': (s['harness_source_checkout_sha256'] or '')[:12],
       'build_record': {k: (v[:12] if isinstance(v, str) and len(v) > 30 else v) for k, v in s['build_record'].items() if k in ('record_sha256', 'engine_tree_archived', 'harness_source_sha256', 'program_sha256', 'host', 'built_at')}})
print('resume_command:', s['resume_command'])
print('engine:', m['engine'][-420:])
EOF
echo "-- PREREGISTRATION.md: the slow-report lines and the Run paragraph"
grep -E "program_route|pinned_program|harness_source|pin_committed|registered_on|school_rule|school_days|Self-check of|A slow report is run" "$D3/PREREGISTRATION.md" | cut -c1-330
echo "-- the dry run of that registered run (no school flag: the registered choice is used)"
python3 -B slow_report.py --dir "$D3" --repo "$R" --pin "$PIN" --dry-run

echo "== 6. a restart: the same build command in OTHER build folders (to the same output path), then the resume"
cp "$SM/rebuilt/strength" "$SM/rebuilt/strength.first"; cp "$SM/rebuilt/strength.build.json" "$SM/rebuilt/strength.build.json.first"
time build_it "$SM/build2" "$SM/target2" 2>&1 | tail -3
echo "first build sha256:  $(sha256sum "$SM/rebuilt/strength.first" | cut -c1-12)"
echo "second build sha256: $(sha256sum "$SM/rebuilt/strength" | cut -c1-12)  (registered: $(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['program_sha256'][:12])" "$D3/manifest.json"))"
echo "-- dry run of the resume"
python3 -B slow_report.py --dir "$D3" --repo "$R" --pin "$PIN" --dry-run
echo "-- the resume itself, a slice of 8 games"
python3 -B slow_report.py --dir "$D3" --repo "$R" --pin "$PIN" --max-games 8 2>&1 | cut -c1-400
echo "exit: $?"
echo "-- the log: the sitting call and, if the bytes changed, the program_changed event"
python3 - "$D3/slow_report_log.jsonl" <<'EOF'
import json, sys
for l in open(sys.argv[1]):
    r = json.loads(l)
    print(r['at'], r['event'], {k: (v[:12] if isinstance(v, str) and len(v) > 30 else v) for k, v in r.items() if k in ('old_sha256', 'new_sha256', 'school_rule', 'school_choice_overridden', 'max_games', 'new_games', 'selfcheck', 'replayed_on')})
EOF
echo "-- the page says what happened to the program"
grep -E "program changed|Build record|REBUILD|Pin \`" "$D3/SLOW_REPORT.md" | cut -c1-500

echo "== 6b. the SAME build command again, from scratch (build and target folders removed): are the bytes the first build's?"
rm -rf "$SM/build1" "$SM/target1"
CMD=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['rebuild_command'])" "$SM/rebuilt/strength.build.json.first")
CMD="${CMD%/rebuilt/strength}/rebuilt/strength.third"
# the record names the main checkout's build.sh (the smoke built with STRENGTH_REPO pointing at it, only to read the pinned commit); run the build.sh under test instead, everything else as recorded
CMD=$(printf '%s' "$CMD" | sed "s#bash '[^']*build.sh'#bash $R/rl/strength/build.sh#")
echo "command: $CMD"
time eval "$CMD" 2>&1 | tail -6
echo "first build sha256:  $(sha256sum "$SM/rebuilt/strength.first" | cut -c1-16)"
echo "third build sha256:  $(sha256sum "$SM/rebuilt/strength.third" | cut -c1-16)  (same command, same folders, built again from scratch)"
[ "$(sha256sum "$SM/rebuilt/strength.first" | cut -d' ' -f1)" = "$(sha256sum "$SM/rebuilt/strength.third" | cut -d' ' -f1)" ] && echo "IDENTICAL BYTES" || echo "DIFFERENT BYTES"
python3 - "$SM/rebuilt/strength.build.json.first" "$SM/rebuilt/strength.third.build.json" <<'EOF'
import json, sys
a, b = (json.load(open(p)) for p in sys.argv[1:3])
print('records differ in:', sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k)))
EOF

echo "== 7. refusals, each with nothing written"
echo "-- a program with no build record (/bin/true)"
python3 -B slow_report.py "$R/decks/events/smoke-held.txt" --repo "$R" --pin "$PIN" --out-root "$SM/runs" --date 2026-10-12 --deals 2 --program /bin/true --school-rule off --register-only 2>&1 | cut -c1-300
echo "exit: ${PIPESTATUS[0]}  (folder written? $(ls "$SM/runs" | grep -c 2026-10-12))"
echo "-- the rebuild with a build record whose engine tree is not the pinned one"
mkdir -p "$SM/forged"; cp "$SM/rebuilt/strength" "$SM/forged/strength"
python3 - "$SM" <<'EOF'
import json, sys
r = json.load(open(sys.argv[1] + '/rebuilt/strength.build.json'))
r['program'] = sys.argv[1] + '/forged/strength'; r['engine_tree_archived'] = '0' * 40
json.dump(r, open(sys.argv[1] + '/forged/strength.build.json', 'w'), indent=1)
EOF
python3 -B slow_report.py "$R/decks/events/smoke-held.txt" --repo "$R" --pin "$PIN" --out-root "$SM/runs" --date 2026-10-13 --deals 2 --program "$SM/forged/strength" --school-rule off --register-only 2>&1 | cut -c1-400
echo "exit: ${PIPESTATUS[0]}"
echo "-- a pin that points at the rebuilt copy, without --program"
python3 - "$SM" <<'EOF'
import json, sys
p = json.load(open(sys.argv[1] + '/pin_smoke.json'))
p['program'] = sys.argv[1] + '/rebuilt/strength'
json.dump(p, open(sys.argv[1] + '/pin_moved.json', 'w'), indent=1)
EOF
python3 -B slow_report.py "$R/decks/events/smoke-held.txt" --repo "$R" --pin "$SM/pin_moved.json" --out-root "$SM/runs" --date 2026-10-14 --deals 2 --register-only 2>&1 | cut -c1-300
echo "exit: ${PIPESTATUS[0]}"
echo "== done; runs kept in $SM/runs"
