#!/usr/bin/env bash
# Second reader: the laptop's copy of the kpr3 table used for the mixed-row replay check, hashed.
sha256sum /home/dacz8976/engine-kpr-e09fb46/kpr3_500_cloud.jsonl
cat /home/dacz8976/engine-kpr-e09fb46/COMMIT 2>/dev/null
sha256sum /home/dacz8976/engine-kpr-e09fb46/legality_scan_e09fb46 2>/dev/null
