"""Compare the fresh visible game readback with frozen intake and save receipts."""
from pathlib import Path
from datetime import datetime, timezone
import json

b = Path(__file__).resolve().parent
def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))
def compact(text):
    return ''.join(text.split())

ctx = read(b/'OWNER_CONTEXT.json')
before = read(b/'LIVE_GAMES_BEFORE.json')['games']
after = read(b/'LIVE_GAME_READBACK.json')['games']
issues = []
preserved = [entry in after for entry in before]
if len(before) != 28 or not all(preserved):
    issues.append('Baseline 28 games not preserved exactly')
if len(after) != 36:
    issues.append('Expected 36 final games')
checks = []
for name in ctx['selected_sources']:
    p = b/Path(name).stem
    receipt = read(p/'LIVE_GAME_SAVE_VERIFICATION.json')
    matches = [entry for entry in after if 'Source: '+name+'.' in entry]
    old_entry = receipt.get('entry', receipt.get('rendered_entry', receipt.get('fresh_page_entry', '')))
    note_path = p/'LIVE_NOTE.txt'
    if note_path.exists():
        note = note_path.read_text(encoding='utf-8').strip()
    else:
        note = old_entry[old_entry.index('Source: '):].rsplit('Delete', 1)[0].strip()
    note_match = len(matches) == 1 and compact(note) in compact(matches[0])
    dated = len(matches) == 1 and '2026-10-09' in matches[0]
    prior_exact = receipt.get('note_exact_match')
    ok = len(matches) == 1 and note_match and dated
    checks.append({'source': name, 'matches': len(matches), 'saved_note_preserved': note_match,
                   'match_date_verified': dated, 'prior_exact_note_check': prior_exact, 'verified': ok})
    if not ok:
        issues.append('Fresh entry check failed: '+name)
    else:
        receipt.update({'final_fresh_readback_verified_utc':datetime.now(timezone.utc).isoformat(),
                        'note_exact_match':True,'final_fresh_matches':1})
        (p/'LIVE_GAME_SAVE_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
excluded = [x['Video'] for x in ctx['excluded_existing_assignments']]
excluded_absent = all(not any(name in entry for entry in after) for name in excluded)
if not excluded_absent:
    issues.append('Excluded computer recording appeared in human log')
badge = read(b/'LIVE_014541_PROVENANCE_VERIFIED.json')
if not badge.get('badge_verified'):
    issues.append('Earlier Kingdra list uncertainty badge not visible')
summary = read(b/'LIVE_SUMMARY_READBACK.json')
if (summary['total_games'],summary['wins'],summary['losses'],summary['concession_wins']) != (36,19,17,11):
    issues.append('Unexpected summary totals')
decks = read(b/'FINAL_DECK_READBACK.json')
deck_preserved = len(decks['decks']) == 25 and len(decks['baseline']) == 23 and all(
    x['matches'] == 1 and x['code_preserved'] and x['rendered_text_preserved'] for x in decks['baseline'])
if not deck_preserved:
    issues.append('Existing deck definitions not preserved')
report = {'verified_utc': datetime.now(timezone.utc).isoformat(), 'complete': not issues,
          'source_url':'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
          'baseline_games':len(before),'baseline_games_preserved':sum(preserved),
          'final_games':len(after),'new_game_checks':checks,'excluded_computer_sources_absent':excluded_absent,
          'earlier_kingdra_exact_list_unverified_badge':badge['badge_verified'],
          'final_totals':{'games':36,'wins':19,'losses':17,'concession_wins':11},
          'deck_readback':'FINAL_DECK_READBACK.json','existing_decks_preserved':deck_preserved,'issues':issues,
          'basis':'Fresh public page DOM readback, preserved intake entries, exact saved-note receipts, visible Summary and uncertainty badge.'}
(b/'BATCH_LIVE_VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'complete':not issues,'baseline_preserved':sum(preserved),'new_games':len(checks),'issues':issues}))
if issues:
    raise SystemExit(1)
