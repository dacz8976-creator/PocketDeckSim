#!/usr/bin/env python3
"""Base protocol, no opt-in: reproducible random choice. Usage: seeded_random_bot.py --seed N"""
import argparse
import json
import random
import sys


def send(message):
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        message = json.loads(line)
        kind = message.get("type")
        if kind == "hello":
            send({"type": "hello", "name": "seeded_random_bot.py"})
        elif kind == "decide":
            actions = message["actions"]
            i = random.Random(args.seed * 1000003 + message["ply"]).randrange(len(actions))
            send({"i": i})


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt, BrokenPipeError):
        pass
