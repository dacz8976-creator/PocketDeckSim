#!/usr/bin/env python3
"""DRY RUN ONLY: judge.py with the API call replaced by a fixed fake reply, so the whole pipeline (rows, formal checks, analysis) can be exercised
without any API call or cost. Every row it writes says MOCK in its reply; such rows must never be mixed with a real run (the run script keeps
dry runs in their own folder and passes --tag MOCK_DRY_RUN). Run from rl/ai_judge with judge.py's own arguments."""
import os, sys

sys.path.insert(0, os.getcwd())
import judge  # noqa: E402


def fake_call(system, user, model=judge.MODEL, max_tokens=judge.MAX_TOKENS, temperature=None, timeout=300):
    text = 'PLAN: 1\nREASON: MOCK reply for the dry run; no API call was made.'
    usage = {'input_tokens': (len(system) + len(user)) // 3, 'output_tokens': 20}
    return text, usage, 0.0, model, {'stop_reason': 'end_turn', 'content_types': ['text']}


def no_key():
    raise SystemExit('mock_judge: the API key must never be read in a dry run')


judge.call_claude = fake_call
judge.load_key = no_key
sys.exit(judge.main(sys.argv[1:]))
