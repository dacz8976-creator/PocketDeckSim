# Battle Review: 20260908_004344000_iOS.MP4

- **Date**: 2026-09-08 (established from source filename `20260908_004344000_iOS.MP4`)
- **Mode & Setting**: Solo mode against AI opponent (labeled "Opponent" with visible "AI" tag; Auto mode set to "On" at 00:09.400).
- **Player**: Dacz8976
- **Opponent**: Opponent (AI)
- **Starting Active Pokémon**:
  - Player: Team Rocket's Rattata (40 HP)
  - Opponent: Team Rocket's Koffing (60 HP)
- **Player Opening Hand**: Comfey, Team Rocket's Researcher, Team Rocket's Rattata, Professor's Research.

---

## Evidence Ledger

### Setup
- **Observed actions**: Coin flip results in player going first (`00:07.800`). Player places Team Rocket's Rattata in the Active Spot (`00:12.200`) and Comfey on the Bench (`00:14.000`). Opponent places Team Rocket's Koffing in the Active Spot (`00:16.200`).
- **State delta**: Player board has Rattata active, Comfey benched; opponent board has Koffing active.

### Turn 1 (Player)
- **Observed actions**: Turn starts (`00:20.200`). Player draws Elegant Cape (`00:22.000`). Plays Professor's Research (`00:24.200`) and draws Sightseer and Pokémon Flute (`00:26.400`). Turn ends without Energy attachment or attack (standard first-turn rules).
- **State delta**: Hand size increases; 0 energy attached.

### Turn 2 (Opponent)
- **Observed actions**: Turn starts (`00:29.400`). Opponent generates Darkness Energy. Plays Poké Ball (`00:33.200`) fetching Team Rocket's Magmar, benches it (`00:36.600`), and attaches Poison Barb to it (`00:40.400`). Plays Copycat (`00:42.200`), shuffling hand and drawing 4 cards (`00:43.800`). Plays Poké Ball (`00:48.800`) fetching Koffing, benches it (`00:52.400`). Benches Happiny (`00:53.200`). Attaches Darkness Energy to Active Koffing (`00:54.600`). Koffing attacks with Reverse Thrust (`00:56.200`), dealing 10 damage to player's Rattata (40 -> 30 HP) and switches with Happiny (`00:59.600`).
- **State delta**: Opponent Active is Happiny (30 HP); player Active Rattata at 30/40 HP. Koffing on bench with 1 Darkness Energy; Magmar on bench with Poison Barb.

### Turn 3 (Player)
- **Observed actions**: Turn starts (`01:00.600`). Player generates Psychic Energy. Draws Team Rocket's Drowzee (`01:02.400`). Plays Team Rocket's Researcher (`01:06.400`), flipping 4 heads and 1 tails (`01:10.200`–`01:13.200`), adding 2x Team Rocket's Hypno, 1x Drowzee, 1x Rattata. Benches second Rattata (`01:21.600`). Evolves Active Rattata into Team Rocket's Raticate ex (120 HP) (`01:23.000`). Benches Drowzee (`01:26.400`). Raticate ex retreats for free (0 retreat cost) and promotes Comfey (`01:27.800`). Attaches Psychic Energy to benched Drowzee (`01:30.800`). Turn ends.
- **State delta**: Active is Comfey (70 HP, 0 Energy); benched Drowzee has 1 Psychic Energy; benched Raticate ex has 0 Energy; benched Rattata has 0 Energy.

### Turn 4 (Opponent)
- **Observed actions**: Turn starts (`01:32.200`). Opponent generates Fire Energy, attaches it to benched Magmar (`01:34.800`). Plays Copycat (`01:35.800`), drawing 5 cards. Evolves benched Koffing into Team Rocket's Weezing ex (`01:43.200`). Weezing ex's Boiler Smog ability triggers (`01:46.400`), inflicting Poison and Burn onto player's Active Comfey (`01:48.000`–`01:50.000`) because Comfey lacks attached Psychic Energy to activate Flower Shield. Active Happiny retreats for free (`01:51.200`) and Magmar is promoted. Opponent attaches Poison Barb to Happiny (`01:52.800`). Magmar attacks with Derisive Roasting (`01:57.600`), dealing 110 damage (10 base + 50*2 special conditions) to Comfey. Comfey is Knocked Out (`02:01.000`). Opponent receives 1 point (`02:04.000`, score 1-0). Player promotes Drowzee (`02:07.400`).
- **State delta**: Comfey discarded; opponent score 1; Drowzee active (60 HP, 1 Psychic Energy).

### Turn 5 (Player)
- **Observed actions**: Turn starts (`02:08.400`). Player generates Psychic Energy. Draws Cyrus (`02:10.400`). Evolves Active Drowzee into Team Rocket's Hypno (`02:14.600`). Plays Sightseer (`02:17.600`), revealing top 4 cards and adding Team Rocket's Raticate ex (`02:20.800`). Evolves benched Rattata into Raticate ex (`02:24.800`); activates Thieving Incisors ability (`02:27.800`), stealing Magmar's 1 Fire Energy onto Raticate ex (`02:28.600`–`02:31.000`). Attaches Elegant Cape to Hypno (`02:33.000`), boosting max HP to 120 (`02:37.400`). Attaches Psychic Energy to Hypno (`02:38.000`, now 2 Psychic Energy). Hypno attacks with Entrap (`02:39.600`), forcing opponent's benched Weezing ex into Active (`02:44.600`) and dealing 50 damage (`02:48.600`, 140 -> 90 HP).
- **State delta**: Opponent Active is Weezing ex (90/140 HP, 1 Darkness Energy). Player Active Hypno has 120 HP, 2 Psychic Energy, Elegant Cape. Benched Raticate ex has 1 Fire Energy.

### Turn 6 (Opponent)
- **Observed actions**: Turn starts (`02:50.600`). Opponent generates Darkness Energy. Plays Professor's Research (`02:54.200`), drawing 2 cards. Evolves second benched Koffing into Weezing ex (`02:58.000`). Ability Boiler Smog triggers (`03:01.000`), inflicting Poison and Burn on player's Hypno (`03:02.800`). Plays X Speed (`03:06.800`), reducing Weezing ex's retreat cost by 1. Weezing ex retreats paying 1 Darkness Energy (`03:10.400`); Magmar promoted to Active. Attaches Darkness Energy to Active Magmar (`03:12.400`). Magmar attacks with Derisive Roasting (`03:14.000`), dealing 110 damage to Hypno (120 -> 10 HP). In Pokémon Checkup, Poison deals 10 damage to Hypno (`03:18.000`), Knocking Out Hypno. Burn check results in Tails (`03:22.400`). Hypno discarded; opponent receives 1 point (`03:26.000`, score 2-0). Player promotes Raticate ex (with 1 Fire Energy) (`03:31.000`).
- **State delta**: Opponent score 2; player Active is Raticate ex (120 HP, 1 Fire Energy).

### Turn 7 (Player)
- **Observed actions**: Turn starts (`03:32.800`). Player generates Psychic Energy. Plays Poké Ball (`03:34.600`), which fails (no Basic Pokémon in deck). Attaches Psychic Energy to Active Raticate ex (`03:36.400`). Raticate ex attacks with Boost Dash (`03:39.800`), dealing 70 damage to Magmar (70 -> 0 HP). Magmar is Knocked Out (`03:42.200`). Magmar's Poison Barb triggers (`03:43.200`), poisoning Raticate ex (`03:45.000`). Player receives 1 point (`03:49.400`, score 2-1). Opponent promotes Happiny (`03:51.400`). In Pokémon Checkup, Poison deals 10 damage to Raticate ex (120 -> 110 HP) (`03:52.400`).
- **State delta**: Score 2-1; player Active Raticate ex at 110/120 HP (Poisoned, 1 Fire, 1 Psychic Energy). Opponent Active is Happiny (30 HP, Poison Barb).

### Turn 8 (Opponent)
- **Observed actions**: Turn starts (`03:53.600`). Opponent generates Darkness Energy. Benches a new Team Rocket's Magmar (`03:56.400`). Plays Team Rocket's Master Plan (`03:58.400`), confusing Raticate ex (`04:00.000`), flipping tails (`04:04.200`), also confusing Happiny (`04:05.000`). Happiny retreats to bench for free (`04:06.600`, removing its Confusion); second Magmar is promoted. Opponent attaches Darkness Energy to Active Magmar (`04:08.800`). Magmar attacks with Derisive Roasting (`04:10.400`), hitting for 110 damage (10 base + 50*2 special conditions: Poisoned and Confused). Raticate ex is Knocked Out (`04:12.600`). Because Raticate ex is an ex Pokémon, opponent is awarded 2 points (`04:17.000`), bringing score to 3-1. Defeat banner appears (`04:18.800`).
- **State delta**: Opponent reaches winning score of 3 points; battle ends in player Defeat.

---

## Explicit Uncertainties
None reported by Gemini

- **Status**: Partial pending independent Sol verification
