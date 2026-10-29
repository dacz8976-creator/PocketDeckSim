#!/usr/bin/env python3
"""Base protocol, no opt-in: always plays action 0."""
import json
import sys


def send(message):
    sys.stdout.write(json.dumps(message) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        message = json.loads(line)
        kind = message.get("type")
        if kind == "hello":
            send({"type": "hello", "name": "first_legal_bot.py"})
        elif kind == "decide":
            send({"i": 0})


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt, BrokenPipeError):
        pass
