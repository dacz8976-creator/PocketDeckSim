# Bounded independent check

Source: `20260930_141742000_iOS.MP4`
Packet: `20260930_141742000_iOS_auto_sol`
Verifier: separate Sol agent (`sol_check_141742`), independent visual observations before reading the main review.

## Scope and evidence examined

This is a bounded check, not a second full review. Reused overview sheets 01, 04, 06 and 07, with their labeled sampled frames spanning opening 1.50-25.50 s, middle 82.50-106.50 s, late 136.50-160.50 s, and closing 163.50 s. These are sparse sampled observations, not continuous observation of those entire intervals. Other overview sheets and detail sheets were not inspected.

Extracted and visually inspected exactly nine targeted full-resolution frames in `independent_frames`: 4.50, 10.50, 89.50, 92.50, 94.50, 145.50, 148.50, 154.50 and 160.50 s. No duplicate full-video decode was performed. Targeted frames were extracted from the source named in SOURCE.json. SOURCE.json records SHA-256 `978030c0bf7cb869a52d1b24da9aeea3c47c9c83acc0711a060ae4e4693d5490`; this checker did not independently recompute that hash.

## Confirmed opening identity and mode

- 4.50 s: versus screen explicitly identifies `AI` / `Opponent` and owner `Dacz8976`.
- 7.50 s overview: owner is going first.
- 10.50 s: setup explicitly says `You are going first`; checked green `Auto` control is visible.
- 13.50-19.50 s overview: owner Torchic active, second Torchic benched by 16.50 s; opponent Celebi active at 70 HP; visible owner Fire energy and Mega Blaziken ex / Rare Candy hand core. Hand and later active card establish a Mega Blaziken ex / Torchic deck core; full deck contents are not established.
- Checked Auto remains visible in selected middle and late board frames.
- These direct observations agree with owner testimony that this is autopilot against a computer. It is excluded from Ladder Log under the owner's instruction.

## Ordinary middle sequence checked

At 85.50-88.50 s overview, opponent active Scyther has 70 HP, owner's active Mega Blaziken ex has 180 HP, and owner leads 1-0. Opponent bench includes Petilil (60), Bulbasaur (60) and Treecko (60) by 88.50 s.

At 89.50 s, Scyther attack animation is occurring; its card visibly lists `U-turn`, 10 damage, and switching with a benched Pokemon. The attack banner itself is not legible in this exact frame. At 91.50 s overview a `10` damage animation is visible on Mega Blaziken ex. At 92.50 s its HP is 170 while Scyther is still active. At 94.50 s Treecko (60) is active, Scyther (70) is benched, and Mega Blaziken ex remains at 170 HP. This observed 180-to-170 change plus switch is consistent with the visible U-turn card text. Score remains owner 1, opponent 0. This was an ordinary opponent turn, not the terminal knockout.

## Decisive late sequence and ending checked

- 139.50/142.50 s overview: opponent active Budew at 30 HP; owner active Mega Blaziken ex at 160 HP, Torchic at 60 and Castform Sunny Form at 70 benched; owner has 2 points, opponent 0.
- 145.50 s targeted frame: explicit `Mega Burning` attack animation by Mega Blaziken ex. Card text visibly lists base damage 120 and the burn effect. Budew is the active target; owner score is 2-0. Exact damage number applied was not independently captured.
- 148.50 s: Budew has 0 HP; Mega Blaziken ex remains 160 HP; opponent point circles remain empty; checked Auto is visible.
- 151.50 s overview: message `Budew is now Burned` appears, with the opponent active slot subsequently empty.
- 154.50 s: `+1 point!` awarded to `Dacz8976`, showing all three yellow points; opponent point circles are empty. This directly supports a 3-0 final point score.
- 160.50 s: explicit `Dacz8976 Victory!` screen featuring Mega Blaziken ex; `Tap to Proceed` visible.
- 163.50 s overview: pale transition/loading screen after the victory screen. No contradictory result was seen.

## Limits and comparison

No audio was inspected. Sparse samples do not establish every action, exact turn number, complete deck list, or optimal play. Burn is displayed after Budew has already reached zero in the sampled ordering; this check does not claim burn damage caused the knockout. Final outcome is independently established by zero-HP target, third-point award, and explicit owner Victory screen.

The main REVIEW.md was not present when this check was written. Comparison is pending its availability; there is no full-review acceptance claim in this note. No source, main review, coverage file, global review log/index, or Ladder Log was modified by this checker.

## Comparison after main review became available

Read REVIEW.md, COVERAGE.md, SUMMARY.json and UNCERTAINTIES.json after completing the independent visual observations above. No additional visual review was performed for this comparison.

No contradiction was found within the independently checked opening, ordinary Scyther sequence, final Budew knockout, point award or Victory. The reports agree on AI / Opponent and checked Auto; owner 180-to-170 HP and Scyther switching to Treecko in the checked ordinary sequence; final Mega Blaziken ex 160 HP; Budew 30-to-zero; third point at about 154.5 s and Victory at about 160.5 s. The review's earlier Burned-message time of about 149.5 s is compatible with its continued display in the independently observed 151.5 s overview sample. The main report correctly avoids treating burn as the knockout cause.

Nine-turn counting, the 210-to-180 initial HP change, earlier Celebi/Treecko knockouts, exact Treecko 140/Budew 120 damage animations, all Trainer actions and complete first-pass coverage are main-review claims outside this bounded independent check. They were not silently promoted to independently verified claims. Narrative, coverage table and summary state those claims consistently. The reported visible late state and result have independent support.

Evidence inventory check: seven overview sheets and detail-sheet counts 5 / 5 / 3 match COVERAGE.md. All fifteen unique explicit `evidence/t...jpg` paths in REVIEW.md exist. SOURCE.json, SUMMARY.json and UNCERTAINTIES.json parse successfully. This checks file availability and report consistency, not the truth of uninspected frames or the main reviewer's complete-coverage claim. No root-acceptance decision is made by this checker; lead acceptance remains separate. Ladder exclusion is consistently stated in all relevant reports.
