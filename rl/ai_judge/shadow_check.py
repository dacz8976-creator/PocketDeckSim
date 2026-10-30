"""A protocol bot that relays decides to the kx3 shadow (A1 RUN3 and RUN4 only)."""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import game_shadow  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--protocol-bot', required=True)
    ap.add_argument('--mode', required=True)
    ap.add_argument('--shadow-log')
    a = ap.parse_args()
    if a.mode == 'relay':
        every = 1
    elif a.mode.startswith('sample:'):
        every = int(a.mode.split(':', 1)[1])
    else:
        sys.exit(2)
    shadow = None
    try:
        for line in sys.stdin:
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            t = msg.get('type') if isinstance(msg, dict) else None
            if t == 'hello':
                shadow = game_shadow.Kx3Shadow(a.protocol_bot, game_shadow.shadow_env(os.environ), a.shadow_log, 'check')
                shadow.start()
                print(json.dumps({'type': 'hello', 'name': 'shadow-check', 'pdl_observation': True, 'pdl_events': True}), flush=True)
            elif t == 'new_game':
                shadow.new_game(line)
            elif t == 'decide':
                ply = msg['ply']
                if ply % every == 0:
                    k, _ = shadow.ask(line, time.monotonic() + 2400, len(msg['actions']), ply)
                else:
                    k = 0
                print(json.dumps({'i': k}), flush=True)
    except game_shadow.ShadowError:
        if shadow:
            shadow.close()
        sys.exit(3)
    if shadow:
        shadow.close()
    sys.exit(0)


main()
