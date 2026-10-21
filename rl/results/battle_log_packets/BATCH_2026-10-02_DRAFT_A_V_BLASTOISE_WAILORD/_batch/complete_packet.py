"""Register and archive one accepted computer review, preserving its first pass."""
import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from validate_packet import BATCH, CORE, local, read, sha, validate

ROOT = BATCH.parent.parent

def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def accept(packet):
    lead = read(packet/'LEAD_ACCEPTANCE.json')
    assert lead['accepted'] is True and lead['coverage_checked'] is True
    assert lead['completion_status'] == 'full_battle_review_complete'
    assert lead['ranked_ladder_eligible'] is False
    assert not lead['remaining_coverage_gaps'] and not lead['unverified_material_claims']
    source = read(packet/'SOURCE.json')
    assignment = read(packet/'ASSIGNMENT.json')
    assert lead['source_video'] == source['video_basename']
    assert lead['source_sha256'] == source['sha256']
    routing = read(packet/'ROUTING.json')
    assert routing['actual_destination'] == 'local_review_batch_and_BATTLE_REVIEW_INDEX'
    assert routing['online_game_entry_requested'] is False and routing['human_pause_games_eligible'] is False
    assert lead['actual_destination'] == routing['actual_destination'] and lead['requested_log'] is None
    assert assignment['reviewer'] != lead['independent_reviewer']
    structural = validate(packet, lead.get('submission_manifest', 'SUBMISSION.json'))
    check_path = local(packet, lead['independent_check'])
    assert sha(check_path) == lead['independent_check_sha256']
    check = read(check_path)
    if normalization := check.get('format_normalization'):
        assert sha(local(packet, normalization['original_check'])) == normalization['original_check_sha256']
    assert check['accepted'] is True
    assert check['full_review_coverage_checked'] is True and check['pause_contract_checked'] is True
    assert check['source_video'] == source['video_basename'] and check['source_sha256'] == source['sha256']
    assert check['reviewer'] == lead['independent_reviewer']
    assert not check['remaining_coverage_gaps'] and not check['unverified_material_claims']
    assert check['checked_submission_manifest_sha256'] == structural['submission_manifest_sha256']
    submission = read(packet/structural['submission_manifest'])
    assert check['checked_submission_files'] == submission['files']
    guide = read(packet/'GUIDE_UPDATE_ACCEPTANCE.json')
    assert guide['accepted'] is True and guide['guide_update_checked'] is True
    assert guide['source_video'] == source['video_basename'] and guide['source_sha256'] == source['sha256']
    assert not guide['remaining_coverage_gaps'] and not guide['unverified_material_claims']
    guide_check = local(packet, guide['independent_check'])
    assert sha(guide_check) == guide['independent_check_sha256']
    if normalization := read(guide_check).get('format_normalization'):
        assert sha(local(packet, normalization['original_check'])) == normalization['original_check_sha256']
    for name, expected in guide['accepted_files'].items():
        assert sha(local(packet, name)) == expected, 'Accepted guide file changed: '+name
    for ref in lead['lead_evidence']:
        local(packet, ref)
    save(packet/'ROOT_STRUCTURAL_CHECK.json', structural)
    return source, assignment, lead, structural

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('packet')
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    packet = Path(args.packet).resolve()
    assert packet.parent == BATCH
    source, assignment, lead, structural = accept(packet)
    if args.validate_only:
        print('Independent acceptance and frozen packet valid: '+source['video_basename'])
        return
    receipt_path = packet/f"MOVE_RECEIPT.{source['video_basename']}.json"
    if not receipt_path.exists():
        events = [read(p) for p in (ROOT/'Review_Log/events').glob('*.json')]
        latest = max((e for e in events if e.get('video_basename')==source['video_basename']), key=lambda e:e['logged_at_utc'])
        if latest['status'] != 'full_battle_review_complete':
            assert latest['status'] == 'in_progress' and latest['reviewer'] == assignment['reviewer']
            command = [sys.executable, str(ROOT/'Review_Log/review_log.py'), '--root', str(ROOT), 'record',
                       '--video', source['video_basename'], '--reviewer', assignment['reviewer'],
                       '--status', 'full_battle_review_complete', '--scope', lead['scope'],
                       '--notes', 'Eight-game owner-authorized local Draft A computer comparison. Full Sol first pass, independent Sol acceptance, full Pause Games capture supplement. Advanced Step-Up category. Original Misty-containing list. Computer battle excluded from both ladder and human Pause Games; no external game entry. Original submitted files and guarded repair history are preserved.']
            guide = read(packet/'GUIDE_UPDATE_ACCEPTANCE.json')
            extras = ['LEAD_ACCEPTANCE.json', 'ROUTING.json', lead['independent_check'],
                      'GUIDE_UPDATE_ACCEPTANCE.json', guide['independent_check']]
            extras += list(guide['accepted_files'])
            for check_ref in [lead['independent_check'], guide['independent_check']]:
                if normalization := read(local(packet, check_ref)).get('format_normalization'):
                    extras.append(normalization['original_check'])
            for name in list(dict.fromkeys(CORE + extras)):
                command += ['--evidence', str(local(packet, name))]
            subprocess.run(command, check=True)
        else:
            assert latest['video_sha256'] == source['sha256'], 'Existing completion identity differs'
        shell = shutil.which('pwsh')
        assert shell, 'PowerShell 7 required by the established archive finalizer'
        subprocess.run([shell, '-NoProfile', '-File', str(ROOT/'Recording_QA/finalize_accepted_review.ps1'),
                        '-Video', source['video_basename'], '-Packet', str(packet.relative_to(ROOT))], check=True)
    receipt = read(receipt_path)
    assert receipt['identity_match'] is True
    assert receipt['sha256_before'] == receipt['sha256_after'] == source['sha256']
    assert receipt['bytes'] == source['bytes']
    assert (ROOT/'Reviewed'/source['video_basename']).stat().st_size == source['bytes']
    # Integrity verification reads only retained evidence; it does not rehydrate
    # the archived original after the OneDrive space-release request.
    validate(packet, lead.get('submission_manifest', 'SUBMISSION.json'))
    save(packet/'COMPLETION_RECEIPT.json', {
        'completed_utc': datetime.now(timezone.utc).isoformat(),
        'source_video': source['video_basename'], 'source_sha256': source['sha256'],
        'review_status': 'full_battle_review_complete', 'capture_status': read(packet/'PAUSE_GAME.json')['capture_status'],
        'accepted': True, 'reviewer': assignment['reviewer'], 'independent_reviewer': lead['independent_reviewer'],
        'latest_guide_additions_accepted': True,
        'guide_acceptance_sha256': sha(packet/'GUIDE_UPDATE_ACCEPTANCE.json'),
        'completion_event_id': receipt['review_event_id'], 'archive_receipt': receipt_path.name,
        'original_bytes_preserved': True, 'submitted_packet_files_preserved': True,
        'frozen_submission_manifest': structural['submission_manifest'],
        'frozen_submission_sha256': structural['submission_manifest_sha256'],
        'classification': 'computer_battle', 'ranked_ladder_eligible': False,
        'actual_destination': routing['actual_destination'] if (routing := read(packet/'ROUTING.json')) else None,
        'requested_log': None, 'human_pause_games_eligible': False,
        'external_log_status': 'Not requested. Owner explicitly requires local batch and index only. No external game entry.',
        'storage_status': 'Separate cloud metadata receipt required; space release may still be pending.'
    })
    subprocess.run(['attrib', '+P', '-U', str(packet/'*'), '/S', '/D'], check=True, capture_output=True)
    print('Accepted, registered and archived unchanged: '+source['video_basename'], flush=True)

if __name__ == '__main__':
    main()
