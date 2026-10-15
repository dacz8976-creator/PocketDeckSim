"""Keep October 1 written reviews and retained evidence available locally."""
import os
import subprocess
from pathlib import Path
from batch_rules_20261001 import ROOT, BATCH, VIDEOS, read, save
from free_reviewed_video_space import metadata

def main():
    attrib = str(Path(os.environ['SystemRoot']) / 'System32' / 'attrib.exe')
    folders = [ROOT / 'Recording_QA' / (Path(name).stem + '_rule_sol') for name in VIDEOS]
    checked = []
    image_count = 0
    for packet in folders:
        assert read(packet / 'LEAD_ACCEPTANCE.json')['accepted'] is True
        assert not any(path.suffix.lower() in ['.mp4', '.mov', '.mkv'] for path in packet.rglob('*') if path.is_file())
        subprocess.run([attrib, '+P', '-U', str(packet)], check=True, capture_output=True)
        subprocess.run([attrib, '+P', '-U', str(packet / '*'), '/S', '/D'], check=True, capture_output=True)
        for filename in ['REVIEW.md', 'COVERAGE.md', 'SUMMARY.json', 'UNCERTAINTIES.json']:
            state = metadata(packet / filename)
            assert state['pinned'] and state['allocated_bytes'] > 0
            checked.append({'path': str(packet / filename), **state})
        images = sorted(path for path in packet.rglob('*') if path.suffix.lower() in ['.jpg', '.png'])
        image_count += len(images)
        assert images
        sample = metadata(images[0])
        assert sample['pinned'] and sample['allocated_bytes'] > 0
    for target in [BATCH, ROOT / 'BATTLE_RULE_TESTS_2026-10-01.md', ROOT / 'READ_ME_REVIEW_STATUS.md']:
        subprocess.run([attrib, '+P', '-U', str(target)], check=True, capture_output=True)
    subprocess.run([attrib, '+P', '-U', str(BATCH / '*'), '/S', '/D'], check=True, capture_output=True)
    result = {'written_review_documents_verified_local': len(checked), 'retained_images_requested_local': image_count, 'sample_images_verified': len(folders), 'original_videos_pinned_by_this_helper': 0, 'documents': checked}
    save(BATCH / 'LOCAL_REPORT_STORAGE.json', result)
    print({key: value for key, value in result.items() if key != 'documents'}, flush=True)

if __name__ == '__main__':
    main()
