#!/bin/bash
cd /home/dacz8976/blind7 || exit 1
export PATH="/home/dacz8976/.local/bin:$PATH"
eval "$(grep '^export ANTHROPIC_API_KEY=' /home/dacz8976/.bashrc | tail -n 1)"
echo "$(date -u +%FT%TZ) start" > /home/dacz8976/blind7_out/log.txt
claude -p "$(cat TASK.md)" --model sonnet --output-format json --allowedTools "Read,Write,Glob,Grep" \
    > /home/dacz8976/blind7_out/result.json 2> /home/dacz8976/blind7_out/err.txt
echo "$(date -u +%FT%TZ) end rc=$?" >> /home/dacz8976/blind7_out/log.txt
cp /home/dacz8976/blind7/READ.md /home/dacz8976/blind7_out/READ.md 2>/dev/null
