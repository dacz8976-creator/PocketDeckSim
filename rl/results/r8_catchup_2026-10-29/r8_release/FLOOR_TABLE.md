| Piece (1,920 games; run_screen 3,840) | Recorded on main-c045ede | S8 (floor2R8) | floor2.py: S8 v recorded | floor2.py: v floor2S | floorR8_recompare.sh v floor2S (R6's S, Oct 29) |
|---|---|---|---|---|---|
| B_D_victini-passive | clears the floor, 693 of 1,920 | clears the floor, 693 of 1,920 | DIFFERS | exit 0 | PASS; R6's S: clears the floor, 693 of 1,920 |
| A_brew-06 | fail, 125 of 1,920 | fail, 125 of 1,920 | DIFFERS | exit 0 | PASS; R6's S: fail, 125 of 1,920 |
| A_brew-06b | fail, 262 of 1,920 | fail, 262 of 1,920 | DIFFERS | exit 0 | PASS; R6's S: fail, 262 of 1,920 |
| A_control14_k3 | control reading, not a floor verdict (pilots k3 on the deck and k3 on the panel, not km3 on both): untrusted, 196 of 1,920 | control reading, not a floor verdict (pilots k3 on the deck and k3 on the panel, not km3 on both): untrusted, 196 of 1,920 | DIFFERS | exit 0 | PASS; R6's S: control reading, not a floor verdict (pilots k3 on the deck and k3 on the panel, not km3 on both): untrusted, 196 of 1,920 |
| A_brew-05b | clears the floor, 577 of 1,920 | clears the floor, 577 of 1,920 | DIFFERS | exit 0 | PASS; R6's S: clears the floor, 577 of 1,920 |
| A_07 | clears the floor, 1,098 of 1,920 | clears the floor, 1,098 of 1,920 | DIFFERS | exit 0 | PASS; R6's S: clears the floor, 1,098 of 1,920 |
| A_run_screen | run_screen, 20 lines | run_screen, 20 lines | SAME | SAME v recorded (not compared again) | PASS; R6's S: run_screen |
| B_12 | clears the floor, 635 of 1,920 | clears the floor, 635 of 1,920 | DIFFERS | exit 0 | PASS; R6's S: clears the floor, 635 of 1,920 |
| B_brew-07 | clears the floor, 1,168 of 1,920 | clears the floor, 1,165 of 1,920 | DIFFERS | exit 0 | PASS; R6's S: clears the floor, 1,165 of 1,920 |
| B_brew-09 | clears the floor, 837 of 1,920 | clears the floor, 824 of 1,920 | DIFFERS | exit 0 | PASS; R6's S: clears the floor, 824 of 1,920 |
| B_D_root | clears the floor, 693 of 1,920 | clears the floor, 693 of 1,920 | DIFFERS | exit 0 | PASS; R6's S: clears the floor, 693 of 1,920 |
| B_D_amended | clears the floor, 597 of 1,920 | clears the floor, 597 of 1,920 | DIFFERS | exit 0 | PASS; R6's S: clears the floor, 597 of 1,920 |

floor2.py compares each page with the recorded page of rl/results/floor_recheck_rules2_2026-10/ (main-c045ede); its DIFFERS there is the engine and coverage lines (and, for brew-07 and brew-09, games, as on main-4d48844 and R6's S), and for each it also compares with floor2S ("v floor2S: exit 0"). The acceptance rule is floorR8_recompare.sh's (tools/; output logs/floor_recheck_R8/RECOMPARE.txt): every games and coverage file byte-equal to floor2S's and each page equal apart from the engine path only. floor2S is as R6 committed it (logs/floor_recheck_R8/FLOOR2S_BASIS.txt), and R8's own goldfish gives byte-equal coverage on the 11 floor decks (GOLDFISH_R8_COVERAGE.txt): floor.py took coverage from pincand's official goldfish (rl/engine-2026-10-21), as floor2S did.
