#!/bin/bash
# Error attribution, Sept 29. Read-only on the repo except for this folder's two outputs. No games, no engine, no build.
# Needs /tmp/koh_cloud/{table,new17}_koh3.jsonl (the cloud's koh tables; sha256 of table_koh3.jsonl: c87b77f392da83b9127fd00971e7f030427c834bb31f85915c72fe0b20eb0d18).
# Without them the koh3 column is skipped by the script's own error, so keep them in place when re-running.
cd "$(dirname "$0")"
nice -n 10 python3 -B attribute.py > attribution_numbers.txt
echo "exit $?"
