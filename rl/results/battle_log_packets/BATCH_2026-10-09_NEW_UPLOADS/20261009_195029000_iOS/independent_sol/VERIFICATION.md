# Independent bounded verification

Reviewer: Sol verifier `verify_195029`, model `gpt-6-sol`, reasoning effort `high`.
Decision: **ACCEPT.** The corrected primary packet establishes one complete computer battle and its defeat result. The lead added the two opponent turn-2 Poké Ball uses that this independent check found missing from the first pass. No required changes remain.

Source: `20261009_195029000_iOS.MP4`, 345,987,192 bytes, 190.976009 seconds, 1170 x 2532. I independently hashed the source as SHA-256 `8b069aade34fbba5615a4f500ab0aa5a150ae8c823be6aa23ca18d5f0a9ddc48`. All times are source-local elapsed seconds. The primary `frames_1s`, `dense`, and overview sheets are scaled review aids. The selected frames in [`native`](native) were freshly extracted from the original at 1170 x 2532. This was a bounded independent check, not a second full transcription.

| Check | Independent finding and source evidence |
| --- | --- |
| Setup and mode | Opponent marked AI at about 00:05 in the overview; Auto is visibly checked at 00:11 (`native/t_11.jpg`). Hitmonchan ex faces Iron Thorns, and the owner goes first. This is a computer battle. Auto's visible state does not identify who made each owner choice. |
| Ordinary turn and searches | On owner turn 1, Copycat resolves around 00:22-00:27; Timburr, Professor's Research and Poké Ball are revealed afterward. Two owner Poké Ball uses reveal Sandshrew and Timburr around 00:32-00:43 (`sheet_020.jpg`, `sheet_040.jpg`, `native/t_30.jpg`, `t_37.jpg`, `t_42.jpg`). On opponent turn 2, Poké Ball is used twice around 00:54-01:04, followed by benching a second Iron Thorns and Magnemite (`native/t_54.5.jpg`, `t_58.75.jpg`, `t_60.jpg`, `t_64.5.jpg`). The opponent's search returns are face-down, so the source does not establish which search supplied which card. |
| Turo and damage | Professor Turo at about 01:25 has the Future text "Shuffle 1 of your Future Pokémon in play into your deck" (`native/t_85.5.jpg`). The damaged original Iron Thorns leaves play; the fresh benched Iron Thorns becomes Active. Binary Thunder then changes Hitmonchan ex from 130 to 50 HP (`sheet_080.jpg`). |
| Owner turn 5 | Fighting Energy is on the benched Sandshrew by 02:05 (`native/t_125.5.jpg` also retains the icon after promotion). Lucky Ice Pop heals Hitmonchan ex from 50 to 70 HP; the coin shows tails at about 01:48 (`sheet_100.jpg`, `native/t_106.7.jpg`). Quick Straight deals 50 to the fresh Iron Thorns. |
| First KO | Binary Thunder hits the 70-HP Hitmonchan ex for 80 around 02:05-02:06; the opponent receives two ex points by 02:11 (`native/t_125.5.jpg`, `t_131.jpg`). Sandshrew is promoted. |
| Owner turn 7 | Conkeldurr in hand is the 150-HP Guts and Mega Punch 80 version (`native/t_140.jpg`), not a played evolution. A Fighting Energy moves to the right benched Timburr around 02:22-02:23 (`native/t_142.8.jpg`, `sheet_140.jpg`). Sandshrew's Double Scratch shows two heads, then 60 damage after Iron Thorns' Fighting Weakness, for one owner point (`sheet_140.jpg`, `native/t_146.8.jpg`, `t_150.5.jpg`, `t_155.jpg`). |
| Final KO and result | Magneton uses Volt Charge, evolves into Magnezone ex (180 HP), and Storm Blade deals 130 to Sandshrew for the last one-point KO (`sheet_160.jpg`, `native/t_167.5.jpg`, `t_173.jpg`, `t_179.jpg`). The result screen shows Defeat against Miraidon ex Deck (Deluxe Pack: Mega), eight turns, owner 1 point, opponent 3, and owner damage 160 (`sheet_180.jpg`, original `intake_frames/3_189.976s.jpg`). |

I reconciled the full-turn coverage table against the 1-second overview and checked the selected ordinary and decisive sequences above. No missing turn or different battle boundary appeared. Hidden hands, complete deck lists and exact small Energy counts remain unknown. This source belongs in the local computer-battle review and should not enter Ladder Log or the human-only Pause Games log.

## Primary files read and reconciled

| Primary file | SHA-256 of final file | Reconciliation |
| --- | --- | --- |
| `REVIEW.md` | `6c80905e8e7a4ca3cc27f9be7578495a2b365fd09196f3e4a1a585bdef7dc4fd` | Eight turns, two opponent turn-2 Poké Ball uses, face-down return qualification, and the result match. |
| `COVERAGE.md` | `e7a3483892b98f81775500bf3f07295624843d19d28d04c86a912864bf87bf43` | Its intervals cover the supplied video and point progression matches. |
| `FINDINGS.json` | `7e7d33600c13dd62397f4717450fc17b9f7d847cb18c69a62db78892ecdcd074` | Outcome, decisive events and the qualified opponent searches match. |
