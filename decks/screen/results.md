# Quick screen results

k3 bot both sides, rules4 engine (sha256 e6593ed8…), 60 games per matchup split across seats, seed 7100.
Panel: the 8 tournament lists in `opponents/`. One line per run; newest at the bottom.

## 2026-09-24 — calibration (Claude, Opus)

| Deck | vs panel | Worst matchups | Ladder |
|---|---|---|---|
| Brew 6 Payback (Psychic) | 8% | Blaziken 3%, Sceptile 3%, Weezing 5% | 0–3 |
| Brew 6b Payback (Grass) | 16% | Sceptile 3%, Blaziken 8%, Suicune 13% | 0–3 |
| Brew 1 Meowstic/Hatterene/Comfey (brew-05b) | 28% | Weezing 13%, Hydreigon 15%, Sceptile 15% (best: Lucario 67%, Altaria 48%) | 3–3 |
| Deck 07 Skarmory stall | 57% | Blaziken 23%, Sceptile 35%, Lucario 40% | 3–1 |
| T-lucario (meta list) | 52% | Sceptile 45%, mirror 47% | Limitless ~50% |
| T-altaria (meta list) | 46% | Sceptile 33%, Suicune 33% | Limitless ~53% |

Read: the two decks that went 0–6 scored 8% and 16%; everything that has worked scored 28% or more.
The bar is under 20% = broken. Brew 1 at 28% is the reason the bar isn't higher: on the ladder it
beat homebrews and lost to meta-style decks (Weezing/Darkrai, Lucario, Darkrai/Espeon), which is
roughly what the screen says too. Anchors are thin (2 bad, 4 working); brew-01 and brew-03a (both
1–3) would be the next ones to add.

## 2026-09-24 — new brews (Claude, Opus)

Search: ~20 lists quick-screened at 16 games per matchup; finalists at 60. Handed over:

| Brew | vs panel | Worst / best matchups | Source |
|---|---|---|---|
| 07 Hoopa ex / Darkrai ex / Mega Sableye ex | 62% | Sceptile 32% · Altaria 83%, Hydreigon 85% | Seedax's 1st-place Hoopa/Absol list (Limitless), Mega Absol ex → Mega Sableye ex (base list scored 53% quick) |
| 08 Entei ex (Rainbow Cave + Flame Patch) | 56% | Suicune 38%, Blaziken 42% · Hydreigon 83% | amilaz's 5th-place Entei ex list, unchanged (a +1 Blacephalon ex version scored 46%) |
| 09 Mega Sableye ex / Galarian Obstagoon | 47% | Sceptile 28%, Suicune 30% · Altaria 68% | Claude's design |
| 10 Mega Diancie ex / Giratina ex battery | 45% | Suicune 17%, Weezing 32% · Vespiquen 58% | Claude's design |

Not handed over (full screen): Entei + Blacephalon for Sabrina 44%, Skarmory ex / Mega Mawile ex 38%,
Hitmonchan ex / Great Tusk 38%. Quick screen only: Tinkaton lock 24%, Obstagoon/Absol 30%,
Luxray/Oricorio 30%, Diancie/TR Mewtwo 34%, Walrein 2%, Hoopa/Obstagoon 35%, Greninja/Scyther (Grass) 27%.
Limitless bases, quick: Entei 59, Hoopa/Absol 53, Greninja/Oricorio 46, Indeedee/Giratina 39,
Miraidon/Magnezone 38, Diancie/Carbink 37, Luxray/Sylveon 34, Espeon/Giratina 33, Scizor/Revavroom 27.
Pattern: the lists that pass run few Pokémon (2–6), high-HP Basics, and a sustain package
(Starting Plains, Giant Cape, Lucky Ice Pop, Pokémon Center Lady).
