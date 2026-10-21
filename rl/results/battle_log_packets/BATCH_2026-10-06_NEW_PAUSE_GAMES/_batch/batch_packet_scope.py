"""Source and per-game paths for the requested batch, including multi-game sources."""
import json
from pathlib import Path

def game_packets(source_packet):
    source_packet = Path(source_packet).resolve()
    manifest = source_packet / 'RELATED_GAME_PACKETS.json'
    if not manifest.exists():
        return [source_packet]
    data = json.loads(manifest.read_text(encoding='utf-8'))
    entries = data['game_packets']
    assert entries and len({e['path'] for e in entries}) == len(entries)
    paths = [(source_packet / e['path']).resolve() for e in entries]
    assert paths[0] == source_packet
    assert all(p == source_packet or source_packet in p.parents for p in paths)
    assert len(paths) == data['game_count']
    return paths

def result_value(summary):
    value = summary.get('outcome', summary.get('owner_result', summary.get('result')))
    if value is None and len(summary.get('games', [])) == 1:
        return result_value(summary['games'][0])
    if isinstance(value, dict):
        value = value.get('owner_result', value.get('result'))
    if value == 'owner_win':
        return 'win'
    if value == 'owner_loss':
        return 'loss'
    if isinstance(value, str) and value.startswith('win'):
        return 'win'
    if isinstance(value, str) and value.startswith('loss'):
        return 'loss'
    return value
