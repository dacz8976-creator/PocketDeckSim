"""Validate, register and archive an independently accepted October 1 packet."""
import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from batch_rules_20261001 import ROOT, VIDEOS, read, save

def validate(name):
    packet = ROOT / 'Recording_QA' / (Path(name).stem + '_rule_sol')
    for filename in ['SOURCE.json', 'REVIEW.md', 'COVERAGE.md', 'SUMMARY.json', 'UNCERTAINTIES.json', 'LEAD_ACCEPTANCE.json']:
        assert (packet / filename).is_file(), f'Missing {filename}'
    source = read(packet / 'SOURCE.json')
    lead = read(packet / 'LEAD_ACCEPTANCE.json')
    summary = read(packet / 'SUMMARY.json')
    assert source['video_basename'] == name and lead['source_video'] == name
    assert lead['accepted'] is True and lead['coverage_checked'] is True
    assert source['ladder_eligible'] is False and lead['ladder_eligible'] is False
    assert source['sha256'] == lead['source_sha256']
    status = lead['completion_status']
    assert status in ['full_battle_review_complete', 'rule_test_review_complete']
    assert summary['complete_available_footage_review'] is True
    if status == 'full_battle_review_complete':
        assert summary['battle_complete'] is True
    assert lead['remaining_coverage_gaps'] == [] and lead['unverified_material_claims'] == []
    for ref in lead['lead_evidence']:
        path = packet / ref
        assert path.resolve().is_relative_to(packet.resolve()) and path.is_file(), ref
    for filename in ['REVIEW.md', 'COVERAGE.md']:
        prose = (packet / filename).read_text(encoding='utf-8-sig')
        assert '\u2014' not in prose, f'Em dash in {filename}'
        refs = set(re.findall(r'`([^`\n]+\.(?:jpg|png))`', prose))
        refs.update(re.findall(r'(?<![A-Za-z0-9_])((?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.*?-]+\.(?:jpg|png))(?![A-Za-z0-9_])', prose))
        for ref in refs:
            matches = list(packet.glob(ref)) if '*' in ref or '?' in ref else [packet / ref]
            if not all(path.is_file() for path in matches) and '/' not in ref and '\\' not in ref:
                matches = list(packet.rglob(ref))
                assert len(matches) == 1, ref
            assert matches and all(path.is_file() and path.resolve().is_relative_to(packet.resolve()) for path in matches), ref
    return packet, source, lead, status

def refresh(packet, source, lead, status, receipt):
    archived = ROOT / 'Reviewed' / source['video_basename']
    assert receipt['identity_match'] and receipt['sha256_before'] == receipt['sha256_after'] == source['sha256']
    assert archived.is_file() and archived.stat().st_size == source['bytes'] == receipt['bytes']
    historical = packet / 'worker_submission'
    historical.mkdir(exist_ok=True)
    for filename in ['REVIEW.md', 'COVERAGE.md', 'SUMMARY.json', 'UNCERTAINTIES.json']:
        target = historical / filename
        if not target.exists():
            shutil.copyfile(packet / filename, target)
    for filename in ['SUMMARY.json', 'UNCERTAINTIES.json']:
        path = packet / filename
        data = read(path)
        data.setdefault('worker_status_at_submission', data.get('status', 'finished_first_pass'))
        data.update({'status': status, 'current_status': status, 'lead_acceptance': 'accepted', 'lead_acceptance_pending': False, 'source_archived': True, 'source_modified': False, 'ladder_eligible': False, 'global_registration_complete': True, 'archive_receipt': f"MOVE_RECEIPT.{source['video_basename']}.json", 'archive_completion_event_id': receipt['review_event_id']})
        for flag in ['independently_accepted', 'lead_accepted', 'independent_lead_accepted']:
            if flag in data:
                data.setdefault('worker_flags_at_submission', {}).setdefault(flag, data[flag])
                data[flag] = True
        if 'acceptance_dependency' in data:
            data['acceptance_dependency'] = 'Independent lead checks and acceptance are complete. The coordinator registered completion and archived the unchanged original.'
        if 'independent_lead_acceptance_required' in data:
            data.setdefault('worker_flags_at_submission', {}).setdefault('independent_lead_acceptance_required', data['independent_lead_acceptance_required'])
            data['independent_lead_acceptance_required'] = False
        if 'independent_acceptance_pending' in data:
            data.setdefault('worker_flags_at_submission', {}).setdefault('independent_acceptance_pending', data['independent_acceptance_pending'])
            data['independent_acceptance_pending'] = False
        if 'acceptance_work_remaining' in data:
            data['acceptance_work_remaining'] = 'Independent lead checks, acceptance, registration and verified archival are complete.'
        if 'independent_lead_acceptance' in data:
            data.setdefault('worker_flags_at_submission', {}).setdefault('independent_lead_acceptance', data['independent_lead_acceptance'])
            data['independent_lead_acceptance'] = 'accepted'
        if 'independent_acceptance' in data:
            data.setdefault('worker_flags_at_submission', {}).setdefault('independent_acceptance', data['independent_acceptance'])
            data['independent_acceptance'] = 'Lead reconciliation, completion registration and verified archival are complete.'
        if 'source_moved' in data:
            data.setdefault('worker_flags_at_submission', {}).setdefault('source_moved', data['source_moved'])
            data['source_moved'] = True
        if 'worker_status' in data:
            data.setdefault('worker_status_at_submission', data['worker_status'])
            data['worker_status'] = 'Complete first pass accepted by the lead; registration and archival are complete.'
        save(path, data)
    stamp = f'**Current status: lead-accepted {status}; original archived unchanged in `Reviewed`. Excluded from Ladder Log.**'
    for filename in ['REVIEW.md', 'COVERAGE.md']:
        path = packet / filename
        prose = path.read_text(encoding='utf-8-sig').replace('Finished first pass awaiting independent lead acceptance.', 'The complete first pass and independent lead checks are accepted; registration and archival are complete.')
        prose = prose.replace('Lead must accept independently before shared completion registration or archiving.', 'The lead independently accepted this packet before completion registration and matching-hash archival; see LEAD_ACCEPTANCE.json.')
        prose = prose.replace('Lead acceptance is still required.', 'Independent lead acceptance, registration and matching-hash archival are complete.')
        prose = prose.replace('Proposed completion status is full_battle_review_complete after independent lead acceptance.', 'Completion status is full_battle_review_complete after independent lead acceptance and verified archival.')
        prose = prose.replace('Lead independent acceptance remains required.', 'Independent lead acceptance, registration and verified archival are complete.')
        prose = prose.replace('Independent lead acceptance remains required before registration or source relocation.', 'Independent lead acceptance, registration and matching-hash archival are complete.')
        prose = prose.replace('Independent lead acceptance remains pending.', 'Independent lead acceptance, registration and matching-hash archival are complete.')
        prose = prose.replace('lead acceptance is pending.', 'lead acceptance, registration and verified archival are complete.')
        prose = prose.replace('Whole-packet independent lead acceptance remains pending.', 'Whole-packet independent lead acceptance, registration and verified archival are complete.')
        prose = prose.replace('## Limits and pending independent acceptance', '## Limits and independent acceptance')
        prose = prose.replace('Independent acceptance and any requested Astra clarification remain lead work.', 'Independent acceptance is complete. Any later targeted Astra clarification is appended with its evidence and scope.')
        prose = prose.replace('No simulator edit, training ingestion, shared record edit, media move or Ladder Log write was performed.', 'The worker made no simulator edit, training ingestion, shared record edit, media move or Ladder Log write. The coordinator later registered and archived the accepted review.')
        prose = prose.replace('Proposed status:full_battle_review_complete, subject to independent lead acceptance.', 'Status:full_battle_review_complete, independently accepted, registered and archived.')
        prose = prose.replace('no simulator, training-data, shared log, or media-location changes were made.', 'the worker made no simulator, training-data, shared log, or media-location changes; the coordinator later registered and archived the accepted review.')
        prose = prose.replace('No simulator edit, fixture ingestion, source move, shared-log completion or Ladder Log write was performed.', 'The worker made no simulator edit, fixture ingestion, source move, shared-log completion or Ladder Log write. The coordinator later registered and archived the accepted review.')
        if stamp not in prose:
            title, rest = prose.split('\n', 1)
            prose = title + '\n\n' + stamp + '\n' + rest
        path.write_text(prose, encoding='utf-8')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('video', choices=VIDEOS)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    packet, source, lead, status = validate(args.video)
    if args.validate_only:
        print(f'Packet references valid: {args.video}')
        return
    receipt_path = packet / f'MOVE_RECEIPT.{args.video}.json'
    if receipt_path.exists():
        refresh(packet, source, lead, status, read(receipt_path))
        print(f'Already archived; verified metadata: {args.video}')
        return
    command = [sys.executable, str(ROOT / 'Review_Log' / 'review_log.py'), '--root', str(ROOT), 'record', '--video', args.video, '--reviewer', source['reviewer'], '--status', status, '--scope', lead['scope'], '--notes', 'Entire supplied recording reviewed by fresh Sol high worker and independently lead-checked. Owner identified rules-testing intent and excluded Ladder Log. Bound observations and limitations are in the packet.']
    for filename in ['REVIEW.md', 'COVERAGE.md', 'LEAD_ACCEPTANCE.json', 'LEAD_CLARIFICATION.md']:
        if (packet / filename).is_file():
            command += ['--evidence', str(packet / filename)]
    subprocess.run(command, check=True)
    shell = shutil.which('pwsh')
    assert shell, 'PowerShell 7 required'
    subprocess.run([shell, '-NoProfile', '-File', str(ROOT / 'Recording_QA' / 'finalize_accepted_review.ps1'), '-Video', args.video, '-Packet', str(packet.relative_to(ROOT))], check=True)
    refresh(packet, source, lead, status, read(receipt_path))
    print(f'Completed with unchanged archive identity: {args.video}', flush=True)

if __name__ == '__main__':
    main()
