import json, shutil
from pathlib import Path
from datetime import datetime, timezone

B = Path(__file__).resolve().parent
P = B / '20260908_012720000'
names = ['TURN_LEDGER.json', 'HAND_SUPPLEMENT.json', 'OBSERVATIONS.json',
         'ACTION_QUESTIONS.json', 'REVIEW_SUPPLEMENT.md', 'UNCERTAINTIES.json']
backup = P / 'before_independent_provenance_repair'
if not backup.exists():
    backup.mkdir()
    for name in names:
        shutil.copy2(P / name, backup / name)
else:
    assert not (P / 'PROVENANCE_REPAIR_RECEIPT.json').exists(), 'Completed repair already exists.'
    for name in names:
        shutil.copy2(backup / name, P / name)

cause = ('Inferred from the end-turn timing, refill from one to three cards, '
         'Hiking Trail in play and its printed effect; the named card identities '
         'and reveal order are directly visible. No native message explicitly '
         'attributes the Spinarak draw to the Stadium.')
locator = str(P / 'locator_scan' / 'grid_240_259.jpg')

def repair_rows(data):
    rows = data.get('turns', data.get('target_rows', []))
    if isinstance(rows, dict):
        rows = rows.values()
    for row in rows:
        n = row.get('turn_number')
        if n == 10:
            draw = row['draws_and_searches'][2]
            assert draw['kind'] == 'stadium_draw'
            draw['causal_status'] = 'inferred'
            draw['causal_basis'] = cause
            draw['limit_reason'] = 'Stadium cause inferred; card identities and order directly observed.'
        if n == 12 and 'plays_in_order' in row:
            for play in row['plays_in_order'][:2]:
                play['basis'] = 'Native identities and consumption boundaries; retained one-second locator samples support placement before Item display.'
                play['ordering_locator_path'] = locator
                play['evidence_ids'] = sorted(set(play.get('evidence_ids', []) + ['F0254.50', 'F0255.00', 'F0258.00']))
                play['timestamp_basis'] = 'Inherited action anchor, not measured PTS; ordering supported by nominal locator samples256 then257.'
                play['limit_reason'] = 'Exact action time unmeasured; input authorship uncertified. Reduced locator used for order only, not card identity.'
        if row.get('who_played') != 'opponent' or 'board_at_start' not in row:
            continue
        board = row['board_at_start']
        zone = board['opponent']['energy_zone']
        if n in [3, 7, 11]:
            zone['this_turn'] = {'type': None, 'count': 0, 'available': False}
            zone['basis'] = 'Direct native state at the preceding owner-turn ending boundary; opponent current circle is empty, Darkness is the next symbol.'
            zone['after_generation_derived'] = {'type': 'Darkness', 'count': 1, 'available': True,
                'status': 'derived_from_turn_sequence_and_inherited_attachment',
                'evidence_ids': [], 'limit_reason': 'Not a direct current-zone observation in the cited preceding-turn native boundary.'}
            zone['limit_reason'] = 'Boundary precedes opponent generation. Next Darkness symbol does not by itself establish current availability.'
            board['phase'] = 'preceding_owner_turn_end_before_opponent_generation'
            board['turn_number_displayed'] = None
            board['turn_number_basis'] = 'Assigned next opponent row; the cited preceding-turn boundary does not directly display this row number.'
        elif n == 5:
            zone['this_turn'] = {'type': None, 'count': None, 'available': None}
            zone['basis'] = 'Inherited post-promotion boundary anchor; current spendability is not directly transcribed from native evidence at this exact start.'
            zone['after_generation_derived'] = {'type': 'Darkness', 'count': 1, 'available': True,
                'status': 'derived_from_turn_sequence_and_inherited_attachment', 'evidence_ids': [],
                'limit_reason': 'Later attachment is retained from accepted prose; current-zone start observation unavailable at the inherited anchor.'}
            zone['limit_reason'] = 'Exact after-generation turn-start zone is not directly observed at this prose anchor.'
            board['phase'] = 'inherited_post_promotion_boundary'
            board['turn_number_displayed'] = None
        elif n == 9:
            zone['basis'] = 'Reused native189.0 shows large current Darkness and small next Darkness symbol; availability directly visible at this opponent-start boundary.'
        else:
            zone['basis'] = 'Native boundary current/next zone glyphs; first opponent turn has no current Energy.'
    return data

for name in names[:3]:
    data = json.loads((P / name).read_text(encoding='utf-8-sig'))
    (P / name).write_text(json.dumps(repair_rows(data), indent=2, ensure_ascii=False), encoding='utf-8')

q = json.loads((P / 'ACTION_QUESTIONS.json').read_text(encoding='utf-8-sig'))
q['questions'][1]['direct_field_value'] = 'Turn12 normal draw Quick-Grow Extract; existing Spinarak is ordinarily Benched and Quick-Grow remains in the ending hand. Spinarak was directly seen in the turn10 end refill; Hiking Trail causation is inferred.'
q['questions'][1]['causal_qualification'] = cause
q['questions'][2]['old_claim'] = 'Old turn7 prose says a second Darkness Energy was attached to Magmar; the target is ambiguous because there are two Magmar, rather than an explicit claim that Active Magmar holds two.'
q['questions'][2]['historical_difference_type'] = 'ambiguous_target_resolved_by_native_evidence'
q['questions'][3]['old_claim'] = 'Old turn11 summary records Confusion Gas but omits the preceding Bench Magmar attachment; it does not explicitly deny that attachment.'
q['questions'][3]['historical_difference_type'] = 'omission'
(P / 'ACTION_QUESTIONS.json').write_text(json.dumps(q, indent=2, ensure_ascii=False), encoding='utf-8')

text = (P / 'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8-sig')
text = text.replace('then Stadium draws X Speed and Spinarak;', 'then X Speed and Spinarak visibly refill the hand at turn end, with Hiking Trail causation inferred from timing, field presence, refill count and printed effect;')
text += '\nIndependent provenance corrections: turn7 old Magmar wording is ambiguous about the target, and the turn11 attachment was omitted rather than denied. Opponent rows3/7/11 retain the directly observed empty current Energy Zone at the preceding owner ending boundary, with after-generation Darkness availability stored separately as derived. Row5 has an inherited promotion boundary and unknown directly observed current spendability; row9 has direct Darkness availability in native189.0. Turn12 placement before X Speed is supported by the retained nominal256/257 locator views, with native254.5/255/258 supporting identities and consumption. Exact inherited256.2/257 action times are not measured PTS.\n'
(P / 'REVIEW_SUPPLEMENT.md').write_text(text, encoding='utf-8')

u = json.loads((P / 'UNCERTAINTIES.json').read_text(encoding='utf-8-sig'))
u['items'] += [{'field': 'turn10_refill_cause', 'status': 'inference', 'reason': cause},
 {'field': 'opponent_energy_zone_start', 'status': 'boundary_provenance_limit', 'reason': 'Rows3/7/11 use pre-generation native boundaries. Row5 uses an inherited promotion boundary. Observed current state and derived after-generation availability are separated.'},
 {'field': 'turn12_first_actions_timing', 'status': 'sample_timing_limit', 'reason': 'Retained locator256/257 supports Spinarak before X Speed; native boundaries verify identities. Exact inherited action timestamps are unmeasured.'}]
(P / 'UNCERTAINTIES.json').write_text(json.dumps(u, indent=2, ensure_ascii=False), encoding='utf-8')
(P / 'PROVENANCE_REPAIR_RECEIPT.json').write_text(json.dumps({'schema':'bounded-lead-provenance-repair-v1',
 'utc':datetime.now(timezone.utc).isoformat(), 'source':'20260908_012720000_iOS.MP4',
 'changed_files':names, 'prior_versions':str(backup), 'new_original_video_reads':0, 'new_frames':0,
 'scope':'Independent three required provenance corrections plus explicit retained-locator ordering basis.',
 'old_packet_unchanged':True, 'independent_recheck_pending':True}, indent=2), encoding='utf-8')
print('Repaired six supplemental files; prior versions preserved. Independent recheck required.')
