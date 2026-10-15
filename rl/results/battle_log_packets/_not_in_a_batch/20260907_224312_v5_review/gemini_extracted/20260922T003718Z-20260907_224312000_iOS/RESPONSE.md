### SOURCE.json
```json
{
  "filename": "20260907_224312000_iOS.MP4",
  "source_path": "/home/dacz8976/20260907_224312000_iOS.MP4",
  "sha256": "6F5BD2F13E548F8B5856132F7FAAB690641FD9A6F10F45D173802E09C9708593",
  "bytes": 456674333,
  "duration_seconds": 249.807,
  "review_status": "partial",
  "reviewer_attribution": "Gemini 3.8 Flash API first-pass draft",
  "index_update_performed": false,
  "media_move_performed": false,
  "evidence_audit": {
    "version": 1,
    "opponent_label": "Opponent",
    "match_mode": {
      "value": "solo",
      "evidence": [
        {
          "timestamp": "04:08.000",
          "observation": "End screen displays 'vs. Random Battle (Expert)'"
        }
      ],
      "uncertainty_id": null
    },
    "opponent_ai": {
      "value": "yes",
      "evidence": [
        {
          "timestamp": "00:02.800",
          "observation": "Opponent banner displays 'AI' badge above 'Opponent'"
        }
      ],
      "uncertainty_id": null
    },
    "auto": {
      "value": "on",
      "evidence": [
        {
          "timestamp": "00:07.400",
          "observation": "Auto toggle checked and highlighted green"
        }
      ],
      "uncertainty_id": null
    },
    "terminal": {
      "outcome": "opponent_win",
      "outcome_evidence": [
        {
          "timestamp": "04:00.400",
          "observation": "Opponent reaches 3 points after Gabite knocked out"
        }
      ],
      "result_text": "Defeat",
      "result_text_evidence": [
        {
          "timestamp": "04:03.000",
          "observation": "'Defeat' banner displayed on screen"
        }
      ],
      "last_frame": {
        "timestamp": "04:09.600",
        "observation": "Summary screen showing 'Defeat...', Card of the Game Gabite, and stats"
      },
      "uncertainty_id": null
    },
    "pokemon": [
      {
        "id": "player-1",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:10.000",
          "observation": "Gible placed in Active Spot with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "03:57.800",
          "observation": "Gabite knocked out and removed from play"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-2",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:24.400",
          "observation": "Munchlax benched with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "01:31.600",
          "observation": "Munchlax knocked out and removed from play"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-3",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "01:54.000",
          "observation": "Garchomp in Active Spot (evolved from Gabite) with 1 Fighting Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "03:15.600",
          "observation": "Garchomp knocked out and removed from play"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-4",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "02:28.600",
          "observation": "Second Gible benched with 0 Energy"
        },
        "final": {
          "Water": 1,
          "Fighting": 1
        },
        "final_evidence": {
          "timestamp": "03:44.200",
          "observation": "Gabite in Active Spot with 1 Water and 1 Fighting attached"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-5",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "03:25.400",
          "observation": "Celebi benched with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "04:02.600",
          "observation": "Celebi on Bench with 0 Energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-1",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:11.400",
          "observation": "Deino in Active Spot with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "03:39.400",
          "observation": "Hydreigon knocked out and removed from play"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-2",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "01:11.400",
          "observation": "Bombirdier placed onto opponent Bench"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "04:02.600",
          "observation": "Bombirdier on Bench with 0 Energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-3",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "01:24.400",
          "observation": "Mega Sableye ex placed onto opponent Bench"
        },
        "final": {
          "Darkness": 2
        },
        "final_evidence": {
          "timestamp": "04:02.600",
          "observation": "Mega Sableye ex in Active Spot with 2 Darkness Energy attached"
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
          "timestamp": "00:28.600",
          "observation": "Deino has 0 Energy"
        },
        "action_evidence": {
          "timestamp": "00:32.600",
          "observation": "Darkness Energy generated and moves to Deino"
        },
        "after_evidence": {
          "timestamp": "00:34.000",
          "observation": "Deino has 1 Darkness Energy attached"
        }
      },
      {
        "turn": 3,
        "pokemon_id": "player-1",
        "kind": "manual",
        "before": {},
        "after": {
          "Fighting": 1
        },
        "before_evidence": {
          "timestamp": "00:41.400",
          "observation": "Gible has 0 Energy"
        },
        "action_evidence": {
          "timestamp": "00:42.600",
          "observation": "Fighting Energy attached from Energy Zone to Gible"
        },
        "after_evidence": {
          "timestamp": "00:43.000",
          "observation": "Gible has 1 Fighting Energy attached"
        }
      },
      {
        "turn": 4,
        "pokemon_id": "opp-1",
        "kind": "manual",
        "before": {
          "Darkness": 1
        },
        "after": {
          "Darkness": 2
        },
        "before_evidence": {
          "timestamp": "00:58.600",
          "observation": "Deino has 1 Darkness Energy"
        },
        "action_evidence": {
          "timestamp": "01:00.600",
          "observation": "Darkness Energy generated and attached to Active"
        },
        "after_evidence": {
          "timestamp": "01:04.000",
          "observation": "Hydreigon has 2 Darkness Energy attached"
        }
      },
      {
        "turn": 4,
        "pokemon_id": "opp-1",
        "kind": "effect",
        "before": {
          "Darkness": 2
        },
        "after": {
          "Darkness": 4
        },
        "before_evidence": {
          "timestamp": "01:13.200",
          "observation": "Hydreigon has 2 Darkness Energy"
        },
        "action_evidence": {
          "timestamp": "01:13.600",
          "observation": "Hydreigon uses Roar in Unison ability to attach 2 Darkness Energy"
        },
        "after_evidence": {
          "timestamp": "01:16.800",
          "observation": "Hydreigon has 4 Darkness Energy attached"
        }
      },
      {
        "turn": 4,
        "pokemon_id": "opp-1",
        "kind": "discard",
        "before": {
          "Darkness": 4
        },
        "after": {
          "Darkness": 3
        },
        "before_evidence": {
          "timestamp": "01:27.400",
          "observation": "Hydreigon has 4 Darkness Energy before attack"
        },
        "action_evidence": {
          "timestamp": "01:28.000",
          "observation": "Hyper Ray discards 1 Darkness Energy"
        },
        "after_evidence": {
          "timestamp": "01:36.400",
          "observation": "Hydreigon has 3 Darkness Energy attached"
        }
      },
      {
        "turn": 5,
        "pokemon_id": "player-1",
        "kind": "manual",
        "before": {
          "Fighting": 1
        },
        "after": {
          "Fighting": 1
        },
        "before_evidence": {
          "timestamp": "01:39.400",
          "observation": "Gabite has 1 Fighting Energy"
        },
        "action_evidence": {
          "timestamp": "01:42.200",
          "observation": "Water Energy generated in Energy Zone, not attached"
        },
        "after_evidence": {
          "timestamp": "01:54.000",
          "observation": "Garchomp active with 1 Fighting Energy"
        }
      },
      {
        "turn": 6,
        "pokemon_id": "opp-1",
        "kind": "manual",
        "before": {
          "Darkness": 3
        },
        "after": {
          "Darkness": 3
        },
        "before_evidence": {
          "timestamp": "02:04.000",
          "observation": "Hydreigon has 3 Darkness Energy"
        },
        "action_evidence": {
          "timestamp": "02:04.600",
          "observation": "Darkness Energy generated in opponent Energy Zone"
        },
        "after_evidence": {
          "timestamp": "02:07.400",
          "observation": "Hydreigon has 3 Darkness Energy attached"
        }
      },
      {
        "turn": 6,
        "pokemon_id": "opp-1",
        "kind": "discard",
        "before": {
          "Darkness": 3
        },
        "after": {
          "Darkness": 2
        },
        "before_evidence": {
          "timestamp": "02:11.600",
          "observation": "Hydreigon has 3 Darkness Energy"
        },
        "action_evidence": {
          "timestamp": "02:12.000",
          "observation": "Hyper Ray discards 1 Darkness Energy"
        },
        "after_evidence": {
          "timestamp": "02:16.800",
          "observation": "Hydreigon has 2 Darkness Energy attached"
        }
      },
      {
        "turn": 7,
        "pokemon_id": "player-4",
        "kind": "manual",
        "before": {},
        "after": {
          "Fighting": 1
        },
        "before_evidence": {
          "timestamp": "02:29.000",
          "observation": "Benched Gible has 0 Energy"
        },
        "action_evidence": {
          "timestamp": "02:30.000",
          "observation": "Fighting Energy attached to benched Gible"
        },
        "after_evidence": {
          "timestamp": "02:30.400",
          "observation": "Benched Gible has 1 Fighting Energy attached"
        }
      },
      {
        "turn": 8,
        "pokemon_id": "opp-1",
        "kind": "manual",
        "before": {
          "Darkness": 2
        },
        "after": {
          "Darkness": 3
        },
        "before_evidence": {
          "timestamp": "03:00.200",
          "observation": "Hydreigon has 2 Darkness Energy"
        },
        "action_evidence": {
          "timestamp": "03:01.000",
          "observation": "Darkness Energy attached to Hydreigon"
        },
        "after_evidence": {
          "timestamp": "03:04.000",
          "observation": "Hydreigon has 3 Darkness Energy"
        }
      },
      {
        "turn": 8,
        "pokemon_id": "opp-1",
        "kind": "effect",
        "before": {
          "Darkness": 3
        },
        "after": {
          "Darkness": 4
        },
        "before_evidence": {
          "timestamp": "03:04.400",
          "observation": "Hydreigon has 3 Darkness Energy"
        },
        "action_evidence": {
          "timestamp": "03:05.000",
          "observation": "Hydreigon uses Roar in Unison to attach Darkness Energy"
        },
        "after_evidence": {
          "timestamp": "03:07.400",
          "observation": "Hydreigon has 4 Darkness Energy attached"
        }
      },
      {
        "turn": 8,
        "pokemon_id": "opp-1",
        "kind": "discard",
        "before": {
          "Darkness": 4
        },
        "after": {
          "Darkness": 3
        },
        "before_evidence": {
          "timestamp": "03:11.400",
          "observation": "Hydreigon has 4 Darkness Energy"
        },
        "action_evidence": {
          "timestamp": "03:12.000",
          "observation": "Hyper Ray discards 1 Darkness Energy"
        },
        "after_evidence": {
          "timestamp": "03:16.800",
          "observation": "Hydreigon has 3 Darkness Energy attached"
        }
      },
      {
        "turn": 8,
        "pokemon_id": "player-3",
        "kind": "discard",
        "before": {
          "Fighting": 1
        },
        "after": {},
        "before_evidence": {
          "timestamp": "03:11.400",
          "observation": "Garchomp has 1 Fighting Energy"
        },
        "action_evidence": {
          "timestamp": "03:13.800",
          "observation": "Garchomp knocked out"
        },
        "after_evidence": {
          "timestamp": "03:15.600",
          "observation": "Garchomp removed from play"
        }
      },
      {
        "turn": 9,
        "pokemon_id": "player-4",
        "kind": "manual",
        "before": {
          "Fighting": 1
        },
        "after": {
          "Fighting": 1,
          "Water": 1
        },
        "before_evidence": {
          "timestamp": "03:22.200",
          "observation": "Active Gible has 1 Fighting Energy"
        },
        "action_evidence": {
          "timestamp": "03:29.600",
          "observation": "Water Energy attached to Active Gabite (evolved)"
        },
        "after_evidence": {
          "timestamp": "03:30.000",
          "observation": "Gabite has 1 Water and 1 Fighting Energy attached"
        }
      },
      {
        "turn": 9,
        "pokemon_id": "opp-1",
        "kind": "discard",
        "before": {
          "Darkness": 3
        },
        "after": {},
        "before_evidence": {
          "timestamp": "03:30.000",
          "observation": "Hydreigon has 3 Darkness Energy"
        },
        "action_evidence": {
          "timestamp": "03:34.200",
          "observation": "Hydreigon knocked out by Gabite's Linear Attack"
        },
        "after_evidence": {
          "timestamp": "03:39.400",
          "observation": "Hydreigon removed to discard"
        }
      },
      {
        "turn": 10,
        "pokemon_id": "opp-3",
        "kind": "manual",
        "before": {},
        "after": {
          "Darkness": 1
        },
        "before_evidence": {
          "timestamp": "03:46.400",
          "observation": "Mega Sableye ex has 0 Energy"
        },
        "action_evidence": {
          "timestamp": "03:51.400",
          "observation": "Darkness Energy attached to Mega Sableye ex"
        },
        "after_evidence": {
          "timestamp": "03:52.000",
          "observation": "Mega Sableye ex has 1 Darkness Energy attached"
        }
      },
      {
        "turn": 10,
        "pokemon_id": "player-4",
        "kind": "discard",
        "before": {
          "Fighting": 1,
          "Water": 1
        },
        "after": {},
        "before_evidence": {
          "timestamp": "03:52.000",
          "observation": "Gabite has 2 Energy attached"
        },
        "action_evidence": {
          "timestamp": "03:55.600",
          "observation": "Gabite knocked out by Cursed Jewel"
        },
        "after_evidence": {
          "timestamp": "03:57.800",
          "observation": "Gabite removed from play"
        }
      }
    ]
  }
}
```

### COVERAGE.md
```markdown
# Battle Coverage

## Setup Interval
- **00:00.000 - 00:14.000**: Match intro against AI "Opponent". Coin flip determines player goes first. Player places Gible (player-1) into the Active Spot. Opponent places Deino (opp-1) into the Active Spot.

## Turn Timeline
- **Turn 1 (Player)** [00:14.000 - 00:25.400]
  - *Evidence anchors*: 00:14.200 (Turn 1 start), 00:18.400 (Poké Ball played), 00:20.400 (Munchlax drawn), 00:24.400 (Munchlax benched), 00:25.400 (Turn end).
  - *State delta*: Munchlax placed on Bench. No Energy attached (going first rule).
- **Turn 2 (Opponent)** [00:25.400 - 00:37.000]
  - *Evidence anchors*: 00:25.600 (Turn 2 start), 00:29.400 (Rocky Helmet attached to Deino), 00:32.600 (Darkness Energy attached to Deino), 00:33.800 (Headbutt declared), 00:36.000 (Gible takes 20 damage, HP 40/60).
  - *State delta*: Deino attached Rocky Helmet and 1 Darkness Energy; dealt 20 damage to Gible.
- **Turn 3 (Player)** [00:37.000 - 00:57.200]
  - *Evidence anchors*: 00:37.000 (Turn 3 start), 00:42.600 (Fighting Energy attached to Gible), 00:45.400 (Gible switched/retreated, Munchlax promoted), 00:47.400 (Gible evolved to Gabite on Bench), 00:48.400 (Munchlax uses Hungrily Draw), 00:49.800 (Deino takes 10 damage, HP 50/60; Munchlax takes 20 damage from Rocky Helmet, HP 30/50).
  - *State delta*: Gible retreated/switched, Gabite evolved on Bench, Munchlax attacks Deino for 10, Munchlax takes 20 recoil from Rocky Helmet.
- **Turn 4 (Opponent)** [00:57.200 - 01:38.200]
  - *Evidence anchors*: 00:57.400 (Turn 4 start), 01:01.000 (Rare Candy played), 01:03.000 (Deino evolves directly into Hydreigon), 01:05.400 (Copycat played), 01:11.400 (Bombirdier benched), 01:13.400 (Hydreigon uses Roar in Unison), 01:17.600 (Hydreigon takes 30 damage from ability, HP 110/140), 01:19.400 (Poké Ball played), 01:23.600 (Mega Sableye ex benched), 01:28.000 (Hyper Ray declared), 01:30.000 (Munchlax takes 130 damage, knocked out), 01:34.000 (Opponent awarded 1st point).
  - *State delta*: Deino evolves to Hydreigon via Rare Candy; Bombirdier and Mega Sableye ex benched; Munchlax KO'd; Opponent score: 1.
- **Turn 5 (Player)** [01:38.200 - 02:02.000]
  - *Evidence anchors*: 01:38.400 (Gabite promoted, Turn 5 start), 01:46.400 (Lucky Ice Pop played, heals 20, coin flip Heads), 01:53.600 (Gabite evolves into Garchomp), 01:56.200 (Mesagoza Stadium played), 02:01.000 (Mesagoza coin flip Tails).
  - *State delta*: Gabite healed to 80/80, evolves to Garchomp (150 HP), Mesagoza enters play, turn passed without attack.
- **Turn 6 (Opponent)** [02:02.000 - 02:15.800]
  - *Evidence anchors*: 02:02.200 (Turn 6 start), 02:05.200 (Hydreigon uses Roar in Unison, takes 30 damage, HP 80/140), 02:12.000 (Hyper Ray attack), 02:14.400 (Garchomp takes 130 damage, HP 20/150).
  - *State delta*: Hydreigon damages itself to 80 HP, hits Garchomp for 130 damage.
- **Turn 7 (Player)** [02:15.800 - 02:58.200]
  - *Evidence anchors*: 02:16.000 (Turn 7 start), 02:28.600 (Gible benched), 02:30.000 (Fighting Energy to benched Gible), 02:32.000 (Rainbow Cave replaces Mesagoza), 02:36.400 (Lucky Ice Pop played, heals Garchomp 20, coin flip Heads), 02:44.200 (Lucky Ice Pop played again, heals Garchomp 20, coin flip Heads), 02:52.000 (Lucky Ice Pop played 3rd time, heals Garchomp 20 to 80 HP, coin flip Tails).
  - *State delta*: Second Gible benched with 1 Energy; Garchomp healed from 20 to 80 HP; Stadium replaced with Rainbow Cave.
- **Turn 8 (Opponent)** [02:58.200 - 03:22.400]
  - *Evidence anchors*: 02:58.400 (Turn 8 start), 03:02.000 (Professor's Research played), 03:05.000 (Roar in Unison used, Hydreigon takes 30 damage, HP 50/140), 03:12.000 (Hyper Ray attack), 03:13.800 (Garchomp knocked out), 03:18.000 (Opponent awarded 2nd point).
  - *State delta*: Hydreigon damages itself to 50 HP; Garchomp KO'd; Opponent score: 2.
- **Turn 9 (Player)** [03:22.400 - 03:48.200]
  - *Evidence anchors*: 03:22.400 (Gible promoted, Turn 9 start), 03:25.400 (Celebi benched), 03:28.400 (Gible evolves into Gabite), 03:29.600 (Water Energy attached to Gabite), 03:32.000 (Linear Attack declared against Hydreigon), 03:34.200 (Hydreigon takes 50 damage, HP 0/140, KO'd), 03:36.600 (Rocky Helmet deals 20 recoil to Gabite, HP 60/80), 03:41.400 (Player awarded 1st point).
  - *State delta*: Celebi benched; Gabite attacks and KOs Hydreigon; Gabite takes 20 recoil; Player score: 1.
- **Turn 10 (Opponent)** [03:48.200 - 04:02.800]
  - *Evidence anchors*: 03:46.000 (Mega Sableye ex promoted), 03:48.400 (Turn 10 start), 03:51.400 (Darkness Energy attached to Mega Sableye ex), 03:53.000 (Cursed Jewel declared), 03:55.600 (Gabite takes 80 damage, knocked out), 04:00.400 (Opponent awarded 3rd point).
  - *State delta*: Gabite knocked out by Mega Sableye ex; Opponent score: 3.

## Terminal Sequence
- **04:00.400 - 04:09.600**: Opponent reaches 3 points, triggering match end. Defeat banner displayed at 04:03.000, followed by defeat screen at 04:08.200.

## Required Event Audit
- `Deck searches and failed searches:` Turn 1 Poké Ball at 00:18.400 (draws Munchlax); Turn 4 Poké Ball at 01:19.400 (opponent draws Mega Sableye ex); Turn 5 Mesagoza at 01:58.800 (coin flip Tails, no search).
- `Energy attachments and acceleration:` Turn 2 manual Darkness to Deino (00:32.600); Turn 3 manual Fighting to Gible (00:42.600); Turn 4 manual Darkness to Hydreigon (01:00.600) & Roar in Unison +2 Darkness (01:13.600); Turn 6 Roar in Unison (02:05.200); Turn 7 manual Fighting to benched Gible (02:30.000); Turn 8 manual Darkness to Hydreigon (03:01.000) & Roar in Unison (03:05.000); Turn 9 manual Water to Gabite (03:29.600); Turn 10 manual Darkness to Mega Sableye ex (03:51.400).
- `Return-to-hand, replay, and exchange events:` Turn 4 Copycat shuffles opponent hand and redraws (01:05.400); Turn 5 Lucky Ice Pop returned to hand on Heads (01:50.000); Turn 7 Lucky Ice Pop replayed and returned on Heads twice (02:41.600, 02:49.400), then discarded on Tails (02:57.000).
- `Knockouts and score changes:` Turn 4 Munchlax KO'd (01:30.000), opponent score 0 -> 1 (01:34.000); Turn 8 Garchomp KO'd (03:13.800), opponent score 1 -> 2 (03:18.000); Turn 9 Hydreigon KO'd (03:34.200), player score 0 -> 1 (03:41.400); Turn 10 Gabite KO'd (03:55.600), opponent score 2 -> 3 (04:00.400).
- `Switches, retreats, and Bench changes:` Turn 3 Gible retreats/switches, Munchlax promoted (00:45.400); Turn 5 Gabite promoted after Munchlax KO (01:38.400); Turn 9 Gible promoted after Garchomp KO (03:22.400); Turn 10 Mega Sableye ex promoted after Hydreigon KO (03:46.000).
- `Terminal sequence:` Opponent scores 3rd point at 04:00.400, "Defeat" banner displayed at 04:03.000.
```

### REVIEW.md
```markdown
# Battle Review

- **Date**: Unknown (timestamp inferred from metadata 2026-09-07)
- **Mode**: Solo (vs. Random Battle Expert)
- **Auto State**: On throughout the match
- **Opponent**: AI ("Opponent")
- **Player**: Dacz8976

## Starting Board & Visible Opening Hand
- **Active Spot**: Gible (Player), Deino (Opponent)
- **Player Hand**: Lucky Ice Pop, Poké Ball, Gabite, Garchomp

## Timeline & Evidence Ledger

### Turn 1 (Player)
- **Observed actions**: Auto-play activates Poké Ball, finding Munchlax. Munchlax is placed onto the Bench. Turn ends without energy attachment (turn 1 rules).
- **State delta**: Munchlax to Bench. Hand: Gabite, Garchomp, Lucky Ice Pop.
- **Evidence anchors**: Poké Ball played at 00:18.400; Munchlax revealed at 00:20.400; Munchlax placed on Bench at 00:24.400.

### Turn 2 (Opponent)
- **Observed actions**: Opponent attaches Rocky Helmet to Deino. Darkness Energy attached to Deino. Deino attacks with Headbutt for 20 damage.
- **State delta**: Gible HP 40/60. Deino attached 1 Darkness Energy, 1 Rocky Helmet.
- **Evidence anchors**: Rocky Helmet at 00:29.400; Darkness Energy at 00:32.600; Headbutt at 00:33.800; Damage at 00:35.000.

### Turn 3 (Player)
- **Observed actions**: Fighting Energy attached to Gible. Gible switches with Munchlax. Gible evolves into Gabite on the Bench. Munchlax attacks with Hungrily Draw (10 damage, draws Rainbow Cave). Deino takes 10 damage; Munchlax takes 20 recoil from Rocky Helmet.
- **State delta**: Munchlax Active (HP 30/50). Deino HP 50/60. Gabite on Bench (HP 40/80, 1 Fighting Energy).
- **Evidence anchors**: Fighting Energy to Gible at 00:42.600; Munchlax promoted at 00:45.400; Gabite evolved at 00:47.400; Hungrily Draw at 00:48.400; Recoil at 00:55.400.

### Turn 4 (Opponent)
- **Observed actions**: Deino evolves directly to Hydreigon via Rare Candy. Opponent plays Copycat. Opponent benches Bombirdier. Hydreigon uses Roar in Unison (+2 Energy, takes 30 damage). Opponent plays Poké Ball, benches Mega Sableye ex. Hydreigon uses Hyper Ray, discarding 1 Energy and knocking out Munchlax for 130 damage.
- **State delta**: Hydreigon Active (HP 110/140, 3 Darkness Energy, Rocky Helmet). Munchlax KO'd. Opponent score: 1.
- **Evidence anchors**: Rare Candy / Hydreigon at 01:01.000 - 01:03.000; Copycat at 01:05.400; Roar in Unison at 01:13.400; Hyper Ray at 01:28.000; Knockout at 01:30.000; Opponent point 1 at 01:34.000.

### Turn 5 (Player)
- **Observed actions**: Gabite promoted. Lucky Ice Pop played: heals 20 (HP 60 -> 80), flips Heads (returned to hand). Gabite evolves into Garchomp. Mesagoza Stadium played. Mesagoza flipped: Tails. Turn passed.
- **State delta**: Garchomp Active (HP 150/150, 1 Fighting Energy). Mesagoza in play.
- **Evidence anchors**: Gabite promoted at 01:38.400; Lucky Ice Pop at 01:44.200 (Heads at 01:50.000); Garchomp evolved at 01:53.600; Mesagoza at 01:56.200 (Tails at 02:01.000).

### Turn 6 (Opponent)
- **Observed actions**: Hydreigon uses Roar in Unison (takes 30 damage, HP 80/140). Hydreigon attacks with Hyper Ray (discards 1 Energy), dealing 130 damage to Garchomp.
- **State delta**: Hydreigon HP 80/140 (2 Darkness Energy). Garchomp HP 20/150.
- **Evidence anchors**: Roar in Unison at 02:05.200; Hyper Ray at 02:12.000; Garchomp damaged at 02:14.400.

### Turn 7 (Player)
- **Observed actions**: Second Gible benched. Fighting Energy attached to benched Gible. Rainbow Cave replaces Mesagoza. Lucky Ice Pop used 3 times: 1st heals 20 (HP 40), Heads; 2nd heals 20 (HP 60), Heads; 3rd heals 20 (HP 80), Tails (discarded). Turn ends.
- **State delta**: Garchomp HP 80/150. Benched Gible with 1 Fighting Energy. Rainbow Cave active.
- **Evidence anchors**: Gible benched at 02:28.600; Energy attached at 02:30.000; Rainbow Cave at 02:32.000; Lucky Ice Pop sequence at 02:36.000 - 02:57.000.

### Turn 8 (Opponent)
- **Observed actions**: Opponent plays Professor's Research. Manual attachment to Hydreigon. Hydreigon uses Roar in Unison (takes 30 damage, HP 50/140). Hydreigon uses Hyper Ray, dealing 130 damage and knocking out Garchomp.
- **State delta**: Garchomp KO'd. Hydreigon HP 50/140 (3 Darkness Energy). Opponent score: 2.
- **Evidence anchors**: Professor's Research at 03:02.000; Roar in Unison at 03:05.000; Hyper Ray at 03:12.000; Garchomp KO at 03:13.800; Opponent point 2 at 03:18.000.

### Turn 9 (Player)
- **Observed actions**: Benched Gible promoted. Celebi benched. Gible evolves into Gabite. Water Energy attached to Gabite. Gabite uses Linear Attack on Hydreigon for 50 damage, knocking it out. Gabite takes 20 recoil from Rocky Helmet (HP 60/80).
- **State delta**: Hydreigon KO'd. Gabite HP 60/80. Player score: 1.
- **Evidence anchors**: Gible promoted at 03:22.400; Celebi benched at 03:25.400; Gabite evolved at 03:28.400; Water Energy at 03:29.600; Linear Attack at 03:32.000; Hydreigon KO at 03:34.200; Recoil at 03:36.600; Player point 1 at 03:41.400.

### Turn 10 (Opponent)
- **Observed actions**: Mega Sableye ex promoted. Manual Darkness Energy attached to Mega Sableye ex. Mega Sableye ex uses Cursed Jewel for 80 damage, knocking out Gabite.
- **State delta**: Gabite KO'd. Opponent score: 3.
- **Evidence anchors**: Mega Sableye promoted at 03:46.000; Darkness Energy at 03:51.400; Cursed Jewel at 03:53.000; Gabite KO at 03:55.600; Opponent point 3 at 04:00.400.

## Outcome
- **Opponent Victory** (Defeat for Player). The match concludes when opponent scores their 3rd point.

## Explicit Uncertainties
None reported by Gemini

## Review Status
Partial pending independent Sol verification
```

### UNCERTAINTIES.json
```json
[]
```
<!-- END_BATTLE_PACKET -->