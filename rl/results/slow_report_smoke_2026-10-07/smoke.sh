#!/usr/bin/env bash
# Real-binary smoke of slow_report.py: the pinned frozen program, but the cheap pilot km3 on both seats (about a second a game; no kx3 game is played).
# The pin is a copy with pilot km3 so the headline says so. Everything else is the real path: pre-registration, the real program, the real report,
# a held-out deck's content (stage use), the km3 baseline on by default, nohup + SIGHUP, a second wrapper refused, SIGTERM in the middle and a resume.
S=/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/2007fbb0-8999-4f68-b5ad-afe643bc4e30/scratchpad/sr
exec > "$S/smoke2.log" 2>&1
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
echo "== 5. the cloud route: --program with a REBUILT copy (the pinned binary plus one trailing byte: another sha256, the same behaviour), school rule off, register only"
cp /home/dacz8976/kx/strength "$SM/rebuilt_strength"; printf 'x' >> "$SM/rebuilt_strength"; chmod +x "$SM/rebuilt_strength"
echo "rebuilt copy sha256: $(sha256sum "$SM/rebuilt_strength" | cut -c1-12) (the pinned binary is 5a8f5c83a791)"
python3 -B slow_report.py "$R/decks/events/smoke-held.txt" --repo "$R" --pin "$PIN" --out-root "$SM/runs" --date 2026-10-09 --deals 2 --program "$SM/rebuilt_strength" --school-rule off --register-only
echo "exit: $?"
D3="$SM/runs/2026-10-09_smoke-held"
echo "-- manifest: program, route, self-check sources, school choice, resume command"
python3 - "$D3/manifest.json" <<'EOF'
import json, sys
m = json.load(open(sys.argv[1]))
s = m['slow_report']
print({'program': m['program'], 'program_sha256': m['program_sha256'][:12], 'program_route': s['program_route'], 'pinned_program_sha256': s['pinned_program_sha256'][:12],
       'selfcheck_source': m['selfcheck_source'], 'school_rule': s['school_rule'], 'school_days': s['school_days'], 'harness_source_sha256': s['harness_source_sha256'][:12],
       'harness_checkout': (s['harness_source_checkout_sha256'] or '')[:12], 'engine_tree_in_checkout': s['engine_tree_in_checkout']})
print('resume_command:', s['resume_command'])
print('engine:', m['engine'][-260:])
EOF
echo "-- PREREGISTRATION.md: the slow-report lines and the Run paragraph"
grep -E "program_route|pinned_program|harness_source|school_rule|school_days|Self-check of|A slow report is run" "$D3/PREREGISTRATION.md"
echo "-- the dry run of that registered run (no school flag: the registered choice is used)"
python3 -B slow_report.py --dir "$D3" --repo "$R" --pin "$PIN" --dry-run
echo "-- the same rebuild is refused when the replay does not match: a program that prints nothing (/bin/true)"
python3 -B slow_report.py "$R/decks/events/smoke-held.txt" --repo "$R" --pin "$PIN" --out-root "$SM/runs" --date 2026-10-12 --deals 2 --program /bin/true --school-rule off --register-only
echo "exit: $?  (folder written? $(ls "$SM/runs" | grep -c 2026-10-12))"
echo "-- and without --program a program of another sha256 is refused (the pin pointing at the rebuilt copy)"
python3 - "$SM" <<'EOF'
import json, sys
p = json.load(open(sys.argv[1] + '/pin_smoke.json'))
p['program'] = sys.argv[1] + '/rebuilt_strength'
json.dump(p, open(sys.argv[1] + '/pin_moved.json', 'w'), indent=1)
EOF
python3 -B slow_report.py "$R/decks/events/smoke-held.txt" --repo "$R" --pin "$SM/pin_moved.json" --out-root "$SM/runs" --date 2026-10-13 --deals 2 --register-only
echo "exit: $?"
echo "== done; runs kept in $SM/runs"
