# Laptop-only scripts, committed because each was the only copy (coordinator-056, Q7; the Oct 26 storage inventory)

| File here | Original path on the laptop (WSL) | Why it matters |
|---|---|---|
| `slowpin_run_tests.sh` | `/home/dacz8976/slowpin_run_tests.sh` | The slow report's pin-test method that committed records name (`PIN_TESTS.txt`): the nine rl/strength modules, 4 at a time, nice 19 |
| `run_slowpin.sh` | `/home/dacz8976/pincand_work/release/tools_after/run_slowpin.sh` | The re-pin driver of Oct 20-21 that calls it; release step R6 reuses the method |
| `upstream_setup.sh` | `/home/dacz8976/upstream_setup.sh` | Sets up the fetch-only `upstream` remote (bcollazo/deckgym-core, push disabled) and the `~/upstream_watch` clone for release step R1 |

Copied byte for byte; paths inside are the laptop's. No secrets (read before committing).
