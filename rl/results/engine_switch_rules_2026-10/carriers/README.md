Decision this informs: which lists the rules switch's carrier games use (`../PLAN.md` step 3, for step 8; main 0a68b0a). Set by the Fable coordinator via Dustin, Sept 30. The lists are committed before any carrier game. No carrier, table or identity game was played here, only the legality scan below, and no engine file changed.

Seeds: the legality scan used Claude diagnostic seeds, 20,970,000,000 + pairing × 10,000 + i. They are outside START_HERE's ranges and outside the plan's carrier block, 23,100,000,000.

# Carrier lists for the rules switch

## In plain words

- **One of the four lists exists by the rule: Garchomp Meowth.** The rule is `decklist_sources.json`'s: the most frequent exact list among top-8 finishes in the development events.
- **The other three have no top-8 development list.** So by the rule they can't be had.
  - Togekiss Meowth's only development list placed 19th of 118.
  - No Hisuian Goodra list placed in the top 8. Its three development lists have no final placing (the players dropped).
  - Mega Houndoom ex Victini's only list also dropped, after round 1.
- **The plan's fallback, as it stands:**
  - `fire_victini.txt` carries repair A (Victini) in place of the Houndoom list.
  - `coinflip_deck.txt` carries Meowth (B2 204). Meowth is already carried by the Garchomp Meowth list.
  - **None of the plan's fallback lists carries Togekiss A4 080 or Hisuian Goodra.** Without another list, those two rest on their tests, as the plan says of Bastiodon.
- **Also here, for the coordinator's or Dustin's choice (not by the rule):** the real development list for each of the three, from the same rule without the top-8 filter. They carry the cards: Togekiss A4 080 with Meowth B2 124, Hisuian Goodra, and Victini with Mega Houndoom ex. But their records are poor (5-3-0, 0-3-0, 0-1-0).
- **Every list passes its card checks.**
  - Each id is one printing, and no list has a B4b card.
  - The validator is clean. The upstream `coinflip_deck.txt` fails it only on three unpadded ids, so a padded copy is here, and the engine reads both forms the same.
  - Every card is implemented; Victini carries the status repair A addresses.
  - The legality scan found no rule findings in 560 games.

## The lists

| carrier (the plan's purpose) | by the rule | provenance | the plan's fallback | alternate, not by the rule |
|---|---|---|---|---|
| Garchomp Meowth, `garchomp-b4a-meowth-b2` (Meowth B2 124, Carefree Steps) | **`garchomp_meowth.txt`** | Shaquill10 (shaquill10, ID), 🥊 20$ BEC'S KING OF THE HILL - ANY FA PRIZE!, 95 players, 2026-09-18, 5th (4-1-0); event 6aaac3d9f1243e65f9802bad. The only top-8 development entry of the 9 development lists (placings 5, 28, 33, 56, 65 and four without one) | not needed | not needed |
| Togekiss Meowth, `togekiss-a4-meowth-b2` (Togekiss A4 080, Celestial Blessing; and Meowth) | no list: its one development list placed 19th | — | `coinflip_deck.txt` (Meowth B2 204, the other Carefree Steps printing; no Togekiss) | `alternates/togekiss_meowth.txt`: Alolan Jay (trainer4572, US), The Breakfast Club Nightly-$20, 118 players, 2026-09-07, 19th (5-3-0); event 6a9dc423ab080c8c957fc250. 2 Togekiss A4 080, 2 Meowth B2 124 |
| Hisuian Goodra, the most-played id in the development events: `dragonair-b4-hisuian-goodra-b3b`, 3 entries (then `hisuian-goodra-b3b-mantyke-a4a`, 2) (Securely Sheltered: the (a) finite cut) | no list: no top-8 entry (all three dropped) | — | none of the plan's made lists carries it | `alternates/hisuian_goodra.txt`: tommyboistreams (US), TH Event's Presents: When DX Pack?!\|5$ + FA's!, 68 players, 2026-09-23, dropped after round 3 (0-3-0); event 6ab3aa2de905c1db68748664. The same exact list is all 3 development entries (r0zey and tommyboistreams, 2026-09-21, 53 players). 2 Hisuian Goodra B3b 050 by Rare Candy from Goomy |
| Mega Houndoom ex Victini, `mega-houndoom-ex-p-b-victini-b3` (Victini B3 025, Victory Star: repair A) | no list: its one list dropped | — | `fire_victini.txt` (2 Victini B3 025, 2 Team Rocket's Moltres ex; the cloud's Victory Star smoke deck) | `alternates/houndoom_victini.txt`: foodking90 (GB), Dark League Pocket Tournament \| 20$USD Prize Pool, 118 players, 2026-09-12, dropped after round 1 (0-1-0); event 6aa17ddeab080c8c957ff0fe. 2 Victini B3 025, 2 Mega Houndoom ex P-B 080 |

- **The rule** (`select_carriers.py`, `selection.json`) is `limitless_skill_model_2026-09-25/analyze.py`'s own block, copied:
  - development events only;
  - final placing 1 to 8;
  - the decklist as an exact multiset of set and zero-padded number, totalling 20;
  - the most frequent multiset wins, with ties by best placing, largest event, earliest date, player id, then the multiset.
  - The only change is the key: the Limitless deck id, since these archetypes aren't in the archive's own mapping.
  - The alternates drop the placing filter and nothing else; an entry without a placing sorts last. The script writes an alternate only where the rule finds nothing.
- **The provenance** of every matching entry (event, player, name, country, placing, record, drop, date, URL, raw file) is in `selection.json`.
- **Garchomp Meowth rests on one entry.** Its selected list is the only top-8 development entry, so it is thin, as the archive's Garchomp list was for B2e.
- **Energy lines.** The archive's decklists carry none, so each file gets one, chosen from its Pokémon's attack costs (in `select_carriers.py`, as the B2e lists added theirs). The card lines are the source's exactly (`cards_sha256` in `selection.json`).

  | list | Energy line | from |
  |---|---|---|
  | Garchomp Meowth | Water, Fighting | Garchomp [WFC], Gabite [WF]; the same line as Dustin's deck 08 |
  | Togekiss Meowth | Psychic | Togekiss [PCC], Togetic [P], Comfey [PC] |
  | Hisuian Goodra | Water, Metal | Hisuian Goodra [WMC] |
  | Mega Houndoom ex Victini | Fire | Mega Houndoom ex [RRC], Houndour [R], Victini [RC] |

- **The fallback files** are byte-identical copies:
  - `fallback/coinflip_deck.txt` from `engine/example_decks/`;
  - `fallback/fire_victini.txt` from `../../victory_star_repair_2026-09-30/smoke/`.
  - `fallback/coinflip_deck_padded.txt` is the upstream file with its three unpadded ids written as `B1a 042`, `B1a 075`, `B2a 093`. The line endings are kept, and nothing else changed.
  - The plan's third made list (a panel list with 2 Meowth B2 124) isn't made, since the Garchomp Meowth list carries Meowth B2 124.

## The card checks (`check_carriers.sh`, `check_output.txt`)

All on the official programs, `rl/engine-2026-09-30/`, whose `SHA256SUMS` were checked first.

- **Ids** (`lib/card.py "<SET> <NNN>"`): every id in the four lists and `fire_victini.txt` is one printing with one text.
  - `coinflip_deck.txt`'s `B1a 42`, `B1a 75` and `B2a 93` resolve only padded (Mega Lopunny ex, Buneary, Mesagoza).
  - **No list has a B4b card.**
- **`lib/deck_check.py files`:** "decks clean" for all but the upstream `coinflip_deck.txt`, which fails on those three unpadded ids.
  - The padded copy is clean.
  - The engine reads both forms the same: the goldfish coverage files of the two are byte-identical.
- **Card status** (the goldfish's coverage, 0 games; `coverage/`, `coverage/summary.txt`): every card is "Fully implemented", except Victini B3 025.
  - Victini's status reads "Implemented with unverified rule boundaries … confusion and attacker-side coin gates currently bypass the reroll prompt pending Pocket rule verification". That is the official engine's own note, and the gap repair A closes.
  - The bot flags are the usual ones: Copycat unpriced; Rocky Helmet, Growl, Charm and Mach Stealth paying off on the opponent's turn.
- **Legality scan** (`scan/`): km3 on both sides.
  - Each of the seven files (the four lists, `coinflip_deck.txt` in both forms, and `fire_victini.txt`) played against the 8 panel lists, 10 games a pairing: 56 pairings, 560 games.
  - **Findings: none** (`scan_page.txt`), and every pairing's 10 games were distinct.
  - Its win percentages are a run check, not matchup numbers.

## What this leaves for the plan

- **If the coordinator keeps the rule strictly,** step 8's carriers are three lists: `garchomp_meowth.txt`, `coinflip_deck.txt` and `fire_victini.txt`. Togekiss's Celestial Blessing and Hisuian Goodra's finite cut (repair B (a)) then rest on their tests.
- **If real lists are wanted for those two,** the alternates carry them, and `alternates/houndoom_victini.txt` is a real list for repair A. Choosing them is the coordinator's or Dustin's decision, not this job's.

## Files

- `README.md`: this note.
- `select_carriers.py`, `selection.json`: the rule, and its output with provenance.
- `garchomp_meowth.txt`: the list by the rule.
- `alternates/`: `togekiss_meowth.txt`, `hisuian_goodra.txt`, `houndoom_victini.txt` (not by the rule).
- `fallback/`: `coinflip_deck.txt`, `coinflip_deck_padded.txt`, `fire_victini.txt`.
- `check_carriers.sh`, `check_output.txt`: the card checks.
- `coverage/`: the goldfish coverage per list, and `summary.txt`.
- `scan/`: `pairs.tsv`, `scan_page.txt`, `scan_stderr.txt`, `games.jsonl`.
