# Battle Review: 20260908_021327000_iOS.MP4

- **Date:** September 8, 2026 (established from source filename `20260908_021327000_iOS.MP4`)
- **Mode:** PvP (Online Match vs human opponent `たか`)
- **Auto State:** Unknown (no Auto UI element rendered in PvP mode)
- **Status:** Partial pending independent Sol verification

## Board & Opening Hand Setup
- **Player Board (Active):** Oddish (60 HP, 0 Energy)
- **Player Bench:** Bulbasaur (70 HP, 0 Energy)
- **Player Starting Hand:** Poké Ball, Gloom, Erika, Bulbasaur, Ivysaur (5 cards total)
- **Opponent Board (Active):** Zubat (60 HP, 0 Energy)
- **Opponent Bench:** Grimer (70 HP, 0 Energy)

---

## Evidence Ledger

### Setup (00:00.000 - 00:31.999)
- **Observed actions:** VS splash reveals opponent `たか`. Player places Oddish Active and Bulbasaur Bench. Opponent places Zubat Active and Grimer Bench.
- **State delta:** Player: Oddish Active (60 HP), Bulbasaur Bench (70 HP). Opponent: Zubat Active (60 HP), Grimer Bench (70 HP).
- **Evidence anchors:** 00:12.400 (VS screen), 00:25.000 (board placement), 00:30.000 (stable starting board).

### Turn 1: Player (00:32.000 - 00:51.999)
- **Observed actions:** Player plays Poké Ball, searches deck, reveals and draws Bulbasaur. Player plays Bulbasaur to Bench.
- **State delta:** Hand: 5 -> 4 cards. Bench: added Bulbasaur (player-3, 70 HP). No Energy attached.
- **Evidence anchors:** 00:32.000 (turn start), 00:38.200 (Poké Ball), 00:43.000 (Bulbasaur revealed), 00:46.000 (Bulbasaur benched), 00:50.000 (turn end).

### Turn 2: Opponent (00:52.000 - 01:17.999)
- **Observed actions:** Darkness Energy generated and manually attached to Active Zubat. Opponent plays Poké Ball, searches deck, reveals and draws Koffing. Opponent plays Koffing to Bench. Zubat attacks with Bite.
- **State delta:** Zubat attached Energy: 0 -> 1 Darkness. Opponent bench: added Koffing (opp-3, 60 HP). Active Oddish takes 10 damage (60 -> 50 HP).
- **Evidence anchors:** 00:52.000 (turn start), 01:00.000 (Darkness attachment), 01:03.000 (Poké Ball), 01:06.000 (Koffing search), 01:10.000 (Koffing benched), 01:13.000 (Bite attack).

### Turn 3: Player (01:18.000 - 01:45.999)
- **Observed actions:** Grass Energy generated. Player evolves Benched Bulbasaur (player-2) into Ivysaur. Player evolves Active Oddish (player-1) into Gloom. Player manually attaches Grass Energy to Active Gloom. Player passes turn.
- **State delta:** Bench: Bulbasaur evolves to Ivysaur (90 HP max). Active: Oddish evolves to Gloom (80 HP max, 70 current HP, 1 Grass Energy).
- **Evidence anchors:** 01:18.000 (turn start), 01:23.000 (Ivysaur evolution), 01:27.000 (Gloom evolution), 01:32.000 (Grass attachment), 01:40.000 (turn pass).

### Turn 4: Opponent (01:46.000 - 02:21.999)
- **Observed actions:** Darkness Energy generated. Opponent evolves Active Zubat into Golbat. Golbat's Ability "Swoop" activates, dealing 10 damage to Active Gloom. Opponent manually attaches Darkness Energy to Benched Grimer. Golbat attacks with Leech Life.
- **State delta:** Active: Zubat evolves to Golbat (80 HP, 1 Darkness Energy). Gloom takes 10 damage from Swoop (70 -> 60 HP). Grimer gains 1 Darkness Energy. Gloom takes 20 damage from Leech Life (60 -> 40 HP). Golbat full HP.
- **Evidence anchors:** 01:46.000 (turn start), 01:52.000 (Golbat evolution), 01:54.000 (Swoop ability), 02:00.000 (Darkness attachment to Grimer), 02:04.000 (Leech Life attack).

### Turn 5: Player (02:22.000 - 03:00.999)
- **Observed actions:** Grass Energy generated. Player draws Venusaur ex. Player plays Erika, targeting Active Gloom and healing 50 HP. Player manually attaches Grass Energy to Active Gloom. Player evolves Benched Ivysaur into Venusaur ex. Gloom attacks Golbat with Drool.
- **State delta:** Gloom healed to 80/80 HP. Gloom Energy: 1 -> 2 Grass. Bench Ivysaur evolves to Venusaur ex (160 HP). Golbat takes 40 damage (80 -> 40 HP).
- **Evidence anchors:** 02:22.000 (turn start), 02:30.000 (Erika play and heal), 02:36.000 (Grass attachment), 02:40.000 (Venusaur ex evolution), 02:46.000 (Drool attack).

### Turn 6: Opponent (03:01.000 - 03:41.999)
- **Observed actions:** Darkness Energy generated. Opponent evolves Benched Koffing into Weezing. Opponent retreats Active Golbat, paying 1 Darkness Energy discard. Weezing promoted to Active Spot. Opponent activates Weezing's Ability "Gas Leak", poisoning Active Gloom. Opponent attaches Darkness Energy to Active Weezing. Turn passes.
- **State delta:** Golbat retreats to bench (40 HP, 0 Energy). Weezing promoted to Active Spot (110 HP, 1 Darkness Energy). Gloom is Poisoned. Pokémon Checkup: Gloom takes 10 Poison damage (80 -> 70 HP).
- **Evidence anchors:** 03:01.000 (turn start), 03:08.000 (Weezing evolution), 03:15.000 (Golbat retreat and discard), 03:18.000 (Weezing promotion), 03:22.000 (Gas Leak ability), 03:26.000 (Darkness attachment), 03:38.000 (Poison damage tick).

### Turn 7: Player (03:42.000 - 04:30.999)
- **Observed actions:** Grass Energy generated. Player manually attaches Grass Energy to Benched Venusaur ex. Player evolves Active Gloom into Vileplume (Poison cured on evolution). Player plays Erika, healing 50 HP on Vileplume. Vileplume attacks Weezing with Mega Drain.
- **State delta:** Venusaur ex attached Energy: 0 -> 1 Grass. Vileplume evolves (130 max HP), clears Poison (120 HP), healed by Erika to 130/130 HP. Active Weezing takes 80 damage from Mega Drain (110 -> 30 HP).
- **Evidence anchors:** 03:42.000 (turn start), 03:48.000 (Grass attachment to Venusaur ex), 03:52.000 (Vileplume evolution and status cure), 03:58.000 (Erika heal), 04:08.000 (Mega Drain attack).

### Turn 8: Opponent (04:31.000 - 05:08.999)
- **Observed actions:** Darkness Energy generated. Opponent manually attaches Darkness Energy to Active Weezing. Opponent plays Supporter Koga, returning Active Weezing line to hand and discarding both attached Darkness Energy. Opponent promotes Benched Grimer. Opponent plays Koffing to Bench and evolves it to Weezing. Opponent evolves Active Grimer into Muk. Muk attacks with Venoshock.
- **State delta:** Weezing scooped to hand via Koga; 2 Darkness Energy discarded. Grimer promoted. Koffing played and evolved to Weezing on bench. Active Grimer evolves to Muk (130 HP, 1 Darkness Energy). Muk attacks Vileplume for 30 damage (130 -> 100 HP) and inflicts Poison. Pokémon Checkup: Vileplume takes 10 Poison damage (100 -> 90 HP).
- **Evidence anchors:** 04:31.000 (turn start), 04:38.000 (Darkness attachment to Weezing), 04:44.000 (Koga played), 04:46.000 (scoop and energy discard), 04:48.000 (Grimer promoted), 04:52.000 (Koffing benched), 04:55.000 (Weezing evolution), 04:58.000 (Muk evolution), 05:01.000 (Venoshock attack), 05:07.000 (Poison tick).

### Turn 9: Player (05:09.000 - 05:55.999)
- **Observed actions:** Grass Energy generated. Player manually attaches Grass Energy to Benched Venusaur ex. Vileplume attacks Muk with Mega Drain.
- **State delta:** Venusaur ex attached Energy: 1 -> 2 Grass. Mega Drain deals 80 damage to Muk (130 -> 50 HP) and heals Vileplume 30 HP (90 -> 120 HP). Pokémon Checkup: Vileplume takes 10 Poison damage (120 -> 110 HP).
- **Evidence anchors:** 05:09.000 (turn start), 05:18.000 (Grass attachment to Venusaur ex), 05:32.000 (Mega Drain attack), 05:52.000 (Poison tick).

### Turn 10: Opponent (05:56.000 - 06:21.999)
- **Observed actions:** Darkness Energy generated. Opponent manually attaches Darkness Energy to Active Muk. Muk attacks Vileplume with Venoshock.
- **State delta:** Muk attached Energy: 1 -> 2 Darkness. Muk attacks Vileplume for 30 damage (110 -> 80 HP). Pokémon Checkup: Vileplume takes 10 Poison damage (80 -> 70 HP).
- **Evidence anchors:** 05:56.000 (turn start), 06:02.000 (Darkness attachment to Muk), 06:12.000 (Venoshock attack), 06:18.000 (Poison tick).

### Turn 11: Player (06:22.000 - 06:45.000)
- **Observed actions:** Grass Energy generated. Player manually attaches Grass Energy to Benched Venusaur ex. Vileplume attacks Muk with Mega Drain. Muk takes 80 damage and is knocked out. Muk and attached Energy discarded. Player awarded 1 point. Opponent surrenders immediately.
- **State delta:** Venusaur ex attached Energy: 2 -> 3 Grass. Muk HP drops to 0 (KO). Score becomes 1-0. Opponent concedes.
- **Evidence anchors:** 06:22.000 (turn start), 06:28.000 (Grass attachment to Venusaur ex), 06:32.000 (Mega Drain attack), 06:35.000 (Muk KO and discard), 06:37.000 (Score 1-0), 06:39.200 (Opponent surrendered prompt), 06:42.000 (VICTORY banner).

---

## Tactical & Mechanical Observations
- Evolution naturally removes all Special Conditions: Gloom's Poison from Gas Leak was cleanly cured upon evolving into Vileplume at Turn 7.
- Koga's scoop effect in Pokémon TCG Pocket returns the Pokémon evolution line to the hand but discards any attached Energy cards; opponent correctly lost the 2 attached Darkness Energy upon scooping Weezing.
- Vileplume's Mega Drain (80 damage, heal 30) combined with Erika effectively nullified the opponent's chip damage strategy from Golbat and Muk.

## Outcome
- **Winner:** Player (`player_win`)
- **Visible Banner:** `VICTORY`
- **Method:** Opponent concession following Muk's knockout (score 1-0).

## Explicit Uncertainties
- **U1:** Auto state is listed as `unknown` because the online PvP interface does not display an Auto control toggle.
