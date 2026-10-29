#!/usr/bin/env python3
"""Test bot: replies with a seeded random valid index to its first two decides, then misbehaves. Usage: test_bad_bot.py --mode M
Modes: garbage, range, sleep, exit, nohello."""
import argparse
import json
import random
import sys
import time


def send(message):
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["garbage", "range", "sleep", "exit", "nohello"])
    args = parser.parse_args()
    decides = 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if args.mode == "nohello":
            continue
        message = json.loads(line)
        kind = message.get("type")
        if kind == "hello":
            send({"type": "hello", "name": "test_bad_bot.py"})
        elif kind == "decide":
            decides += 1
            if decides < 3:
                send({"i": random.Random(message["ply"]).randrange(len(message["actions"]))})
            elif args.mode == "garbage":
                sys.stdout.write("not json\n")
                sys.stdout.flush()
            elif args.mode == "range":
                send({"i": len(message["actions"])})
            elif args.mode == "sleep":
                time.sleep(60)
            elif args.mode == "exit":
                sys.exit(3)


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt, BrokenPipeError):
        pass
