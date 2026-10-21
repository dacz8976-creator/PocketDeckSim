### SOURCE.json
```json
{
  "filename": "20260908_021327000_iOS.MP4",
  "source_path": "C:\\Users\\dacz8\\OneDrive\\Desktop\\Battle Logs\\20260908_021327000_iOS.MP4",
  "sha256": "95DF14AF59472EC02A077B5A5804F1A44E6C02048179952934B68C56EEE1E387",
  "bytes": 767232143,
  "duration_seconds": 410.492,
  "model": "gemini-3.8-flash",
  "review_method": "static video processing at 5 source frames per second with high media resolution",
  "reviewer_attribution": "Gemini 3.8 Flash API first-pass draft",
  "review_status": "partial",
  "index_update_performed": false,
  "media_move_performed": false,
  "battle_identity": {
    "opponent_label": {
      "state": "observed",
      "value": "たか",
      "timestamp_seconds": 12.0,
      "observation": "Opponent username 'たか' displayed on VS splash screen and top-left player card."
    },
    "opening_player": {
      "state": "observed",
      "value": "Oddish",
      "timestamp_seconds": 32.0,
      "observation": "Player starts with Oddish (60 HP) in Active Spot."
    },
    "opening_opponent": {
      "state": "observed",
      "value": "Zubat",
      "timestamp_seconds": 32.0,
      "observation": "Opponent starts with Zubat (60 HP) in Active Spot."
    },
    "outcome": {
      "state": "observed",
      "value": "player_win",
      "timestamp_seconds": 402.0,
      "observation": "Muk knocked out, score reaches 1-0, opponent surrenders and VICTORY banner appears."
    },
    "result_text": {
      "state": "observed",
      "value": "VICTORY",
      "timestamp_seconds": 402.0,
      "observation": "Large VICTORY banner displayed across screen."
    }
  },
  "evidence_audit": {
    "version": 1,
    "opponent_label": "たか",
    "match_mode": {
      "value": "pvp",
      "evidence": [
        {
          "timestamp": "00:12.400",
          "observation": "Matchmaking splash screen displays human opponent profile and emblems."
        },
        {
          "timestamp": "06:39.200",
          "observation": "Opponent surrendered notification indicates human concession."
        }
      ],
      "uncertainty_id": null
    },
    "opponent_ai": {
      "value": "no",
      "evidence": [
        {
          "timestamp": "06:39.200",
          "observation": "Human player concession prompt displayed."
        }
      ],
      "uncertainty_id": null
    },
    "auto": {
      "value": "unknown",
      "evidence": [
        {
          "timestamp": "00:32.000",
          "observation": "PvP battle interface does not render an Auto control toggle."
        }
      ],
      "uncertainty_id": "U1"
    },
    "terminal": {
      "outcome": "player_win",
      "outcome_evidence": [
        {
          "timestamp": "06:39.200",
          "observation": "Opponent surrendered prompt."
        },
        {
          "timestamp": "06:42.000",
          "observation": "VICTORY banner displayed."
        }
      ],
      "result_text": "VICTORY",
      "result_text_evidence": [
        {
          "timestamp": "06:42.000",
          "observation": "Large gold VICTORY banner rendered."
        }
      ],
      "last_frame": {
        "timestamp": "06:50.400",
        "observation": "Final reward and victory transition screen."
      },
      "uncertainty_id": null
    },
    "pokemon": [
      {
        "id": "player-1",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:32.000",
          "observation": "Oddish active with 0 attached Energy."
        },
        "final": {
          "Grass": 2
        },
        "final_evidence": {
          "timestamp": "06:35.000",
          "observation": "Vileplume active with 2 Grass Energy attached."
        },
        "uncertainty_id": null
      },
      {
        "id": "player-2",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:32.000",
          "observation": "Bulbasaur on bench with 0 attached Energy."
        },
        "final": {
          "Grass": 3
        },
        "final_evidence": {
          "timestamp": "06:35.000",
          "observation": "Venusaur ex on bench with 3 Grass Energy attached."
        },
        "uncertainty_id": null
      },
      {
        "id": "player-3",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:46.000",
          "observation": "Second Bulbasaur played to bench with 0 attached Energy."
        },
        "final": {},
        "final_evidence": {
          "timestamp": "06:35.000",
          "observation": "Bulbasaur remains on bench with 0 attached Energy."
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-1",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:32.000",
          "observation": "Zubat active with 0 attached Energy."
        },
        "final": {},
        "final_evidence": {
          "timestamp": "06:35.000",
          "observation": "Golbat on bench with 0 attached Energy."
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-2",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:32.000",
          "observation": "Grimer on bench with 0 attached Energy."
        },
        "final": {},
        "final_evidence": {
          "timestamp": "06:35.000",
          "observation": "Muk knocked out and sent to discard with 0 attached Energy."
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-3",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "01:10.000",
          "observation": "Koffing played to bench with 0 attached Energy."
        },
        "final": {},
        "final_evidence": {
          "timestamp": "06:35.000",
          "observation": "Weezing on bench with 0 attached Energy."
        },
        "uncertainty_id": null
      }
    ],
    "energy_events": [
      {
        "turn": 2,
        "pokemon_id": "opp-1",
        "kind": "manual",
        "before": {},
        "after": {
          "Darkness": 1
        },
        "before_evidence": {
          "timestamp": "00:58.000",
          "observation": "Zubat has 0 Energy attached."
        },
        "action_evidence": {
          "timestamp": "01:00.000",
          "observation": "Opponent moves Darkness Energy to Active Zubat."
        },
        "after_evidence": {
          "timestamp": "01:02.000",
          "observation": "Zubat displays 1 Darkness Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons"
      },
      {
        "turn": 3,
        "pokemon_id": "player-1",
        "kind": "manual",
        "before": {},
        "after": {
          "Grass": 1
        },
        "before_evidence": {
          "timestamp": "01:30.000",
          "observation": "Gloom has 0 Energy attached."
        },
        "action_evidence": {
          "timestamp": "01:32.000",
          "observation": "Player attaches Grass Energy to Active Gloom."
        },
        "after_evidence": {
          "timestamp": "01:34.000",
          "observation": "Gloom displays 1 Grass Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons"
      },
      {
        "turn": 4,
        "pokemon_id": "opp-2",
        "kind": "manual",
        "before": {},
        "after": {
          "Darkness": 1
        },
        "before_evidence": {
          "timestamp": "01:58.000",
          "observation": "Benched Grimer has 0 Energy attached."
        },
        "action_evidence": {
          "timestamp": "02:00.000",
          "observation": "Opponent attaches Darkness Energy to Benched Grimer."
        },
        "after_evidence": {
          "timestamp": "02:02.000",
          "observation": "Grimer displays 1 Darkness Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons"
      },
      {
        "turn": 5,
        "pokemon_id": "player-1",
        "kind": "manual",
        "before": {
          "Grass": 1
        },
        "after": {
          "Grass": 2
        },
        "before_evidence": {
          "timestamp": "02:34.000",
          "observation": "Gloom has 1 Grass Energy attached."
        },
        "action_evidence": {
          "timestamp": "02:36.000",
          "observation": "Player attaches Grass Energy to Active Gloom."
        },
        "after_evidence": {
          "timestamp": "02:38.000",
          "observation": "Gloom displays 2 Grass Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons"
      },
      {
        "turn": 6,
        "pokemon_id": "opp-1",
        "kind": "retreat",
        "before": {
          "Darkness": 1
        },
        "after": {},
        "before_evidence": {
          "timestamp": "03:14.000",
          "observation": "Golbat has 1 Darkness Energy attached."
        },
        "action_evidence": {
          "timestamp": "03:15.000",
          "observation": "Golbat retreats, paying 1 Darkness Energy."
        },
        "after_evidence": {
          "timestamp": "03:17.000",
          "observation": "Golbat moves to bench with 0 Energy attached."
        }
      },
      {
        "turn": 6,
        "pokemon_id": "opp-3",
        "kind": "manual",
        "before": {},
        "after": {
          "Darkness": 1
        },
        "before_evidence": {
          "timestamp": "03:24.000",
          "observation": "Active Weezing has 0 Energy attached."
        },
        "action_evidence": {
          "timestamp": "03:26.000",
          "observation": "Opponent attaches Darkness Energy to Active Weezing."
        },
        "after_evidence": {
          "timestamp": "03:28.000",
          "observation": "Weezing displays 1 Darkness Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons"
      },
      {
        "turn": 7,
        "pokemon_id": "player-2",
        "kind": "manual",
        "before": {},
        "after": {
          "Grass": 1
        },
        "before_evidence": {
          "timestamp": "03:46.000",
          "observation": "Venusaur ex has 0 Energy attached."
        },
        "action_evidence": {
          "timestamp": "03:48.000",
          "observation": "Player attaches Grass Energy to Benched Venusaur ex."
        },
        "after_evidence": {
          "timestamp": "03:50.000",
          "observation": "Venusaur ex displays 1 Grass Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons"
      },
      {
        "turn": 8,
        "pokemon_id": "opp-3",
        "kind": "manual",
        "before": {
          "Darkness": 1
        },
        "after": {
          "Darkness": 2
        },
        "before_evidence": {
          "timestamp": "04:36.000",
          "observation": "Weezing has 1 Darkness Energy attached."
        },
        "action_evidence": {
          "timestamp": "04:38.000",
          "observation": "Opponent attaches Darkness Energy to Active Weezing."
        },
        "after_evidence": {
          "timestamp": "04:40.000",
          "observation": "Weezing displays 2 Darkness Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons"
      },
      {
        "turn": 8,
        "pokemon_id": "opp-3",
        "kind": "discard",
        "before": {
          "Darkness": 2
        },
        "after": {},
        "before_evidence": {
          "timestamp": "04:43.000",
          "observation": "Weezing has 2 Darkness Energy attached before Koga is played."
        },
        "action_evidence": {
          "timestamp": "04:46.000",
          "observation": "Koga returns Weezing line to hand; attached Energy is discarded."
        },
        "after_evidence": {
          "timestamp": "04:52.000",
          "observation": "Koffing replayed to bench with 0 Energy."
        }
      },
      {
        "turn": 9,
        "pokemon_id": "player-2",
        "kind": "manual",
        "before": {
          "Grass": 1
        },
        "after": {
          "Grass": 2
        },
        "before_evidence": {
          "timestamp": "05:16.000",
          "observation": "Venusaur ex has 1 Grass Energy attached."
        },
        "action_evidence": {
          "timestamp": "05:18.000",
          "observation": "Player attaches Grass Energy to Venusaur ex."
        },
        "after_evidence": {
          "timestamp": "05:20.000",
          "observation": "Venusaur ex displays 2 Grass Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons"
      },
      {
        "turn": 10,
        "pokemon_id": "opp-2",
        "kind": "manual",
        "before": {
          "Darkness": 1
        },
        "after": {
          "Darkness": 2
        },
        "before_evidence": {
          "timestamp": "06:00.000",
          "observation": "Active Muk has 1 Darkness Energy attached."
        },
        "action_evidence": {
          "timestamp": "06:02.000",
          "observation": "Opponent attaches Darkness Energy to Active Muk."
        },
        "after_evidence": {
          "timestamp": "06:04.000",
          "observation": "Muk displays 2 Darkness Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons"
      },
      {
        "turn": 11,
        "pokemon_id": "player-2",
        "kind": "manual",
        "before": {
          "Grass": 2
        },
        "after": {
          "Grass": 3
        },
        "before_evidence": {
          "timestamp": "06:26.000",
          "observation": "Venusaur ex has 2 Grass Energy attached."
        },
        "action_evidence": {
          "timestamp": "06:28.000",
          "observation": "Player attaches Grass Energy to Venusaur ex."
        },
        "after_evidence": {
          "timestamp": "06:30.000",
          "observation": "Venusaur ex displays 3 Grass Energy attached."
        },
        "attachment_evidence": "movement_and_attached_icons"
      },
      {
        "turn": 11,
        "pokemon_id": "opp-2",
        "kind": "discard",
        "before": {
          "Darkness": 2
        },
        "after": {},
        "before_evidence": {
          "timestamp": "06:32.000",
          "observation": "Muk has 2 Darkness Energy attached before knockout."
        },
        "action_evidence": {
          "timestamp": "06:35.000",
          "observation": "Muk is knocked out by Mega Drain; attached Energy discarded."
        },
        "after_evidence": {
          "timestamp": "06:37.000",
          "observation": "Muk removed from field; score updates to 1-0."
        }
      }
    ]
  }
}
```

### COVERAGE.md
```markdown
# Battle Coverage: 20260908_021327000_iOS.MP4

## Match Overview
- Matchup: Grass (Oddish / Gloom / Vileplume / Venusaur ex) vs Darkness (Zubat / Golbat / Koffing / Weezing / Grimer / Muk)
- Player: lower board (`Dacz`)
- Opponent: upper board (`たか`)
- Duration reviewed: 00:00.000 - 06:50.492

## Turn and Interval Breakdown

- **Setup (00:00.000 - 00:31.999)**
  - Evidence anchors: Match VS splash at 00:12.400; starting Pokemon placed at 00:25.000; stable board ready at 00:30.000.
  - State delta: Player opens Active Oddish (60 HP) and Bench Bulbasaur (70 HP). Opponent opens Active Zubat (60 HP) and Bench Grimer (70 HP). Hand sizes: 5 cards each.

- **Turn 1: Player (00:32.000 - 00:51.999)**
  - Evidence anchors: Turn banner at 00:32.000; Poké Ball played at 00:38.200; Bulbasaur drawn at 00:43.000; benched at 00:46.000; turn pass at 00:50.000.
  - State delta: Player searches deck and benches Bulbasaur. Hand count: 5 -> 4. No Energy attached (going first).

- **Turn 2: Opponent (00:52.000 - 01:17.999)**
  - Evidence anchors: Turn banner at 00:52.000; Darkness attachment to Zubat at 01:00.000; Poké Ball at 01:03.000 finding Koffing at 01:06.000; Koffing benched at 01:10.000; Bite attack at 01:13.000.
  - State delta: Zubat gains 1 Darkness Energy; Koffing benched; Active Oddish takes 10 damage (60 -> 50 HP).

- **Turn 3: Player (01:18.000 - 01:45.999)**
  - Evidence anchors: Turn banner at 01:18.000; Bulbasaur evolves to Ivysaur at 01:23.000; Oddish evolves to Gloom at 01:27.000; Grass attachment to Gloom at 01:32.000; turn pass at 01:40.000.
  - State delta: Bench Bulbasaur evolves to Ivysaur (90 HP); Active Oddish evolves to Gloom (80 HP max, 70 HP current); Gloom gains 1 Grass Energy.

- **Turn 4: Opponent (01:46.000 - 02:21.999)**
  - Evidence anchors: Turn banner at 01:46.000; Zubat evolves to Golbat at 01:52.000; Swoop ability triggers at 01:54.000 (10 dmg); Darkness attachment to Grimer at 02:00.000; Leech Life attack at 02:04.000 (20 dmg).
  - State delta: Golbat Swoop does 10 damage to Gloom (70 -> 60 HP); Grimer gains 1 Darkness Energy; Leech Life deals 20 damage to Gloom (60 -> 40 HP).

- **Turn 5: Player (02:22.000 - 03:00.999)**
  - Evidence anchors: Turn banner at 02:22.000; Erika played at 02:30.000; Grass attachment to Gloom at 02:36.000; Ivysaur evolves to Venusaur ex at 02:40.000; Drool attack at 02:46.000.
  - State delta: Erika heals Gloom 50 HP (40 -> 80/80 HP); Gloom gains 1 Grass Energy (now 2); Venusaur ex evolves on bench; Gloom attacks Golbat for 40 damage (80 -> 40 HP).

- **Turn 6: Opponent (03:01.000 - 03:41.999)**
  - Evidence anchors: Turn banner at 03:01.000; Koffing evolves to Weezing at 03:08.000; Golbat retreats at 03:15.000 (discards 1 Darkness); Weezing promoted at 03:18.000; Gas Leak ability triggers at 03:22.000; Darkness attachment to Weezing at 03:26.000; Poison checkup at 03:38.000.
  - State delta: Golbat pays 1 Darkness Energy to retreat to bench; Weezing active; Gloom poisoned by Gas Leak; Weezing gains 1 Darkness Energy; Gloom takes 10 Poison damage (80 -> 70 HP).

- **Turn 7: Player (03:42.000 - 04:30.999)**
  - Evidence anchors: Turn banner at 03:42.000; Grass attachment to Venusaur ex at 03:48.000; Gloom evolves to Vileplume at 03:52.000; Erika played at 03:58.000; Mega Drain attack at 04:08.000.
  - State delta: Venusaur ex gains 1 Grass Energy; Gloom evolves to Vileplume (130 max HP, heals Poison, HP 120/130); Erika heals Vileplume to 130/130; Mega Drain deals 80 damage to Weezing (110 -> 30 HP).

- **Turn 8: Opponent (04:31.000 - 05:08.999)**
  - Evidence anchors: Turn banner at 04:31.000; Darkness attachment to Weezing at 04:38.000; Koga played at 04:44.000; Grimer promoted at 04:48.000; Koffing replayed at 04:52.000; Weezing evolved at 04:55.000; Grimer evolves to Muk at 04:58.000; Venoshock attack at 05:01.000; Poison checkup at 05:07.000.
  - State delta: Active Weezing returned to hand via Koga (2 attached Darkness discarded); Grimer promoted; Koffing replayed and evolved to Weezing on bench; Active Grimer evolves to Muk (130 HP); Muk attacks Vileplume for 30 damage (130 -> 100 HP) and poisons it; Poison tick deals 10 damage (100 -> 90 HP).

- **Turn 9: Player (05:09.000 - 05:55.999)**
  - Evidence anchors: Turn banner at 05:09.000; Grass attachment to Venusaur ex at 05:18.000; Mega Drain attack at 05:32.000; Poison checkup at 05:52.000.
  - State delta: Venusaur ex gains 1 Grass Energy (now 2); Mega Drain deals 80 damage to Muk (130 -> 50 HP) and heals Vileplume 30 HP (90 -> 120 HP); Poison tick deals 10 damage (120 -> 110 HP).

- **Turn 10: Opponent (05:56.000 - 06:21.999)**
  - Evidence anchors: Turn banner at 05:56.000; Darkness attachment to Muk at 06:02.000; Venoshock attack at 06:12.000; Poison checkup at 06:18.000.
  - State delta: Muk gains 1 Darkness Energy (now 2); Muk attacks for 30 damage (110 -> 80 HP); Poison tick deals 10 damage (80 -> 70 HP).

- **Turn 11: Player (06:22.000 - 06:45.000)**
  - Evidence anchors: Turn banner at 06:22.000; Grass attachment to Venusaur ex at 06:28.000; Mega Drain attack at 06:32.000; Muk knockout at 06:35.000; score update at 06:37.000; surrender prompt at 06:39.200; VICTORY banner at 06:42.000.
  - State delta: Venusaur ex gains 1 Grass Energy (now 3); Mega Drain deals 80 damage, knocking out Muk (50 -> 0 HP); Muk and 2 Darkness Energy discarded; Player score increases from 0 to 1; Opponent surrenders; Player wins.

- **Terminal Sequence (06:45.001 - 06:50.492)**
  - Evidence anchors: VICTORY presentation and transition to match rewards screen at 06:46.000 - 06:50.400.

## Required Event Audit
- `Deck searches and failed searches:` 00:38.200 (Player plays Poké Ball, successfully retrieves Bulbasaur at 00:43.000); 01:03.000 (Opponent plays Poké Ball, successfully retrieves Koffing at 01:06.000).
- `Energy attachments and acceleration:` 01:00.000 (Opponent Darkness to Zubat); 01:32.000 (Player Grass to Gloom); 02:00.000 (Opponent Darkness to Grimer); 02:36.000 (Player Grass to Gloom); 03:26.000 (Opponent Darkness to Weezing); 03:48.000 (Player Grass to Venusaur ex); 04:38.000 (Opponent Darkness to Weezing); 05:18.000 (Player Grass to Venusaur ex); 06:02.000 (Opponent Darkness to Muk); 06:28.000 (Player Grass to Venusaur ex).
- `Return-to-hand, replay, and exchange events:` 04:44.000 (Opponent plays Koga, returning Active Weezing line to hand and discarding 2 Darkness Energy); 04:52.000 (Opponent replays Koffing from hand to bench).
- `Knockouts and score changes:` 06:35.000 (Opponent Muk knocked out by Vileplume's Mega Drain); 06:37.000 (Score changes from 0-0 to 1-0 in Player's favor).
- `Switches, retreats, and Bench changes:` 00:25.000 (Setup: Player benches Bulbasaur, Opponent benches Grimer); 00:46.000 (Player benches Bulbasaur); 01:10.000 (Opponent benches Koffing); 03:15.000 (Opponent retreats Golbat to bench, discarding 1 Darkness Energy, promotes Weezing at 03:18.000); 04:48.000 (Opponent promotes Grimer after Koga scoops Weezing).
- `Terminal sequence:` 06:35.000 (Muk KO); 06:37.000 (Score 1-0); 06:39.200 (Opponent surrendered); 06:42.000 (VICTORY banner displayed); 06:50.400 (Final frame of victory reward transition).

## Unresolved Intervals
- None observed. The full match sequence is uninterrupted and all actions reconcile completely.
```

### REVIEW.md
```markdown
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
```

### UNCERTAINTIES.json
```json
[
  {
    "id": "U1",
    "start_timestamp": "00:00.000",
    "end_timestamp": "06:50.492",
    "claim_or_question": "Is Auto mode enabled or disabled during this match?",
    "why_uncertain": "The battle is conducted in PvP matchmaking where the Auto toggle button is not displayed on the screen interface.",
    "consequence_if_wrong": "None for gameplay, rules reconciliation, or match outcome; metadata classification only.",
    "recommended_sol_check": "Confirm that PvP mode inherently disables Auto and verify whether protocol requires marking Auto as 'off' or 'unknown'."
  }
]
```
<!-- END_BATTLE_PACKET -->