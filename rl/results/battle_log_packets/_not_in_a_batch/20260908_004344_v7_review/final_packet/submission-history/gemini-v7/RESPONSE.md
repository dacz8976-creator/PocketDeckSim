### SOURCE.json
```json
{
  "filename": "20260908_004344000_iOS.MP4",
  "source_path": "C:\\Users\\dacz8\\OneDrive\\Desktop\\Battle Logs\\20260908_004344000_iOS.MP4",
  "sha256": "0B248F4D8B67F9D907B1142EC23949F806267E21B36FA4C2E460AD5FC92B85F2",
  "bytes": 483433381,
  "duration_seconds": 258.978,
  "review_status": "partial",
  "reviewer_attribution": "Gemini 3.8 Flash API first-pass draft",
  "recording_type": "screen_recording",
  "relationships": [],
  "index_update_performed": false,
  "media_move_performed": false,
  "battle_identity": {
    "opponent_label": {
      "state": "observed",
      "value": "Opponent",
      "timestamp_seconds": 4.8,
      "observation": "Opponent nameplate displays 'Opponent' with an AI badge directly above it"
    },
    "opening_player": {
      "state": "observed",
      "value": "Team Rocket's Rattata",
      "timestamp_seconds": 12.2,
      "observation": "Player places Team Rocket's Rattata into the Active Spot during setup"
    },
    "opening_opponent": {
      "state": "observed",
      "value": "Team Rocket's Koffing",
      "timestamp_seconds": 16.2,
      "observation": "Opponent reveals Team Rocket's Koffing in the Active Spot"
    },
    "outcome": {
      "state": "observed",
      "value": "opponent_win",
      "timestamp_seconds": 257.0,
      "observation": "Opponent reaches 3 points after knocking out player's Team Rocket's Raticate ex"
    },
    "result_text": {
      "state": "observed",
      "value": "Defeat",
      "timestamp_seconds": 258.8,
      "observation": "'Defeat' banner is displayed across the center of the screen"
    }
  },
  "evidence_audit": {
    "version": 1,
    "opponent_label": "Opponent",
    "match_mode": {
      "value": "solo",
      "evidence": [
        {
          "timestamp": "00:04.800",
          "observation": "Opponent nameplate shows 'AI' pill badge above the name 'Opponent'"
        }
      ],
      "uncertainty_id": null
    },
    "opponent_ai": {
      "value": "yes",
      "evidence": [
        {
          "timestamp": "00:04.800",
          "observation": "Visible 'AI' tag displayed above Opponent name"
        }
      ],
      "uncertainty_id": null
    },
    "auto": {
      "value": "on",
      "evidence": [
        {
          "timestamp": "00:09.400",
          "observation": "Auto toggle button is highlighted green with a checkmark"
        }
      ],
      "uncertainty_id": null
    },
    "terminal": {
      "outcome": "opponent_win",
      "outcome_evidence": [
        {
          "timestamp": "04:17.000",
          "observation": "Opponent score indicator increments to 3 points (+2 points animation)"
        }
      ],
      "result_text": "Defeat",
      "result_text_evidence": [
        {
          "timestamp": "04:18.800",
          "observation": "Red defeat banner reading 'Defeat' appears over darkened board"
        }
      ],
      "last_frame": {
        "timestamp": "04:18.800",
        "observation": "Final frame showing Defeat banner"
      },
      "uncertainty_id": null
    },
    "pokemon": [
      {
        "id": "player-1",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:12.200",
          "observation": "Team Rocket's Rattata placed into Active Spot with 0 attached energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "04:18.800",
          "observation": "Team Rocket's Raticate ex remains on the player's bench with 0 attached energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-2",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:14.000",
          "observation": "Comfey placed onto player's bench with 0 attached energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "02:01.000",
          "observation": "Comfey is knocked out and moved to the discard pile"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-3",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "01:21.600",
          "observation": "Second Team Rocket's Rattata benched with 0 attached energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "04:14.000",
          "observation": "Team Rocket's Raticate ex is knocked out and sent to the discard pile"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-4",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "01:26.400",
          "observation": "Team Rocket's Drowzee benched with 0 attached energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "03:23.400",
          "observation": "Team Rocket's Hypno is knocked out by Poison and moved to discard"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-1",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:16.200",
          "observation": "Opponent reveals Team Rocket's Koffing in Active Spot with 0 attached energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "04:18.800",
          "observation": "Team Rocket's Weezing ex sits on opponent bench with 0 attached energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-2",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:36.600",
          "observation": "Team Rocket's Magmar placed on opponent bench with 0 attached energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "03:46.400",
          "observation": "Team Rocket's Magmar is knocked out and sent to the discard pile"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-3",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:52.400",
          "observation": "Second Team Rocket's Koffing placed on opponent bench with 0 attached energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "04:18.800",
          "observation": "Second Team Rocket's Weezing ex remains on opponent bench with 0 attached energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-4",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:53.200",
          "observation": "Happiny placed on opponent bench with 0 attached energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "04:18.800",
          "observation": "Happiny remains on opponent bench with 0 attached energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-5",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "03:56.400",
          "observation": "Second Team Rocket's Magmar benched with 0 attached energy"
        },
        "final": {
          "Darkness": 1
        },
        "final_evidence": {
          "timestamp": "04:18.800",
          "observation": "Second Team Rocket's Magmar active with 1 Darkness Energy attached"
        },
        "uncertainty_id": null
      }
    ],
    "energy_events": [
      {
        "turn": 2,
        "pokemon_id": "opp-1",
        "kind": "manual",
        "attachment_evidence": "movement_and_attached_icons",
        "before": {},
        "after": {
          "Darkness": 1
        },
        "before_evidence": {
          "timestamp": "00:54.000",
          "observation": "Active Koffing has no attached energy"
        },
        "action_evidence": {
          "timestamp": "00:54.600",
          "observation": "Darkness energy moves from zone to active Koffing"
        },
        "after_evidence": {
          "timestamp": "00:55.200",
          "observation": "Active Koffing shows 1 Darkness energy attached"
        },
        "uncertainty_id": null
      },
      {
        "turn": 3,
        "pokemon_id": "player-4",
        "kind": "manual",
        "attachment_evidence": "movement_and_attached_icons",
        "before": {},
        "after": {
          "Psychic": 1
        },
        "before_evidence": {
          "timestamp": "01:29.600",
          "observation": "Benched Drowzee has no attached energy"
        },
        "action_evidence": {
          "timestamp": "01:30.800",
          "observation": "Psychic energy moves from player zone to benched Drowzee"
        },
        "after_evidence": {
          "timestamp": "01:31.200",
          "observation": "Benched Drowzee displays 1 Psychic energy attached"
        },
        "uncertainty_id": null
      },
      {
        "turn": 4,
        "pokemon_id": "opp-2",
        "kind": "manual",
        "attachment_evidence": "movement_and_attached_icons",
        "before": {},
        "after": {
          "Fire": 1
        },
        "before_evidence": {
          "timestamp": "01:34.000",
          "observation": "Benched Magmar has no attached energy"
        },
        "action_evidence": {
          "timestamp": "01:34.800",
          "observation": "Fire energy moves from opponent zone to benched Magmar"
        },
        "after_evidence": {
          "timestamp": "01:35.200",
          "observation": "Benched Magmar displays 1 Fire energy attached"
        },
        "uncertainty_id": null
      },
      {
        "turn": 5,
        "pokemon_id": "opp-2",
        "kind": "effect",
        "before": {
          "Fire": 1
        },
        "after": {},
        "before_evidence": {
          "timestamp": "02:27.400",
          "observation": "Active Magmar has 1 Fire energy"
        },
        "action_evidence": {
          "timestamp": "02:28.600",
          "observation": "Raticate ex Thieving Incisors ability moves Fire energy from Magmar"
        },
        "after_evidence": {
          "timestamp": "02:31.200",
          "observation": "Active Magmar now has 0 energy attached"
        },
        "uncertainty_id": null
      },
      {
        "turn": 5,
        "pokemon_id": "player-3",
        "kind": "effect",
        "before": {},
        "after": {
          "Fire": 1
        },
        "before_evidence": {
          "timestamp": "02:27.400",
          "observation": "Benched Raticate ex has 0 energy attached"
        },
        "action_evidence": {
          "timestamp": "02:28.600",
          "observation": "Thieving Incisors ability moves Fire energy to this Raticate ex"
        },
        "after_evidence": {
          "timestamp": "02:31.200",
          "observation": "Benched Raticate ex displays 1 Fire energy attached"
        },
        "uncertainty_id": null
      },
      {
        "turn": 5,
        "pokemon_id": "player-4",
        "kind": "manual",
        "attachment_evidence": "movement_and_attached_icons",
        "before": {
          "Psychic": 1
        },
        "after": {
          "Psychic": 2
        },
        "before_evidence": {
          "timestamp": "02:37.000",
          "observation": "Active Hypno has 1 Psychic energy attached"
        },
        "action_evidence": {
          "timestamp": "02:38.000",
          "observation": "Psychic energy moves from zone to active Hypno"
        },
        "after_evidence": {
          "timestamp": "02:38.600",
          "observation": "Active Hypno displays 2 Psychic energy attached"
        },
        "uncertainty_id": null
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
          "timestamp": "03:09.800",
          "observation": "Active Weezing ex has 1 Darkness energy attached"
        },
        "action_evidence": {
          "timestamp": "03:10.400",
          "observation": "Weezing ex pays 1 Darkness energy (reduced by X Speed) to retreat to bench"
        },
        "after_evidence": {
          "timestamp": "03:11.000",
          "observation": "Weezing ex on bench now has 0 attached energy"
        },
        "uncertainty_id": null
      },
      {
        "turn": 6,
        "pokemon_id": "opp-2",
        "kind": "manual",
        "attachment_evidence": "movement_and_attached_icons",
        "before": {},
        "after": {
          "Darkness": 1
        },
        "before_evidence": {
          "timestamp": "03:11.800",
          "observation": "Active Magmar has 0 energy attached"
        },
        "action_evidence": {
          "timestamp": "03:12.400",
          "observation": "Darkness energy moves from zone to active Magmar"
        },
        "after_evidence": {
          "timestamp": "03:12.800",
          "observation": "Active Magmar displays 1 Darkness energy attached"
        },
        "uncertainty_id": null
      },
      {
        "turn": 6,
        "pokemon_id": "player-4",
        "kind": "discard",
        "before": {
          "Psychic": 2
        },
        "after": {},
        "before_evidence": {
          "timestamp": "03:18.000",
          "observation": "Active Hypno has 2 Psychic energy attached before KO"
        },
        "action_evidence": {
          "timestamp": "03:23.400",
          "observation": "Hypno is knocked out by Poison and moved to discard pile"
        },
        "after_evidence": {
          "timestamp": "03:24.000",
          "observation": "Hypno is in discard pile with 0 energy remaining on field"
        },
        "uncertainty_id": null
      },
      {
        "turn": 7,
        "pokemon_id": "player-3",
        "kind": "manual",
        "attachment_evidence": "movement_and_attached_icons",
        "before": {
          "Fire": 1
        },
        "after": {
          "Fire": 1,
          "Psychic": 1
        },
        "before_evidence": {
          "timestamp": "03:36.000",
          "observation": "Active Raticate ex has 1 Fire energy attached"
        },
        "action_evidence": {
          "timestamp": "03:36.400",
          "observation": "Psychic energy moves from zone to active Raticate ex"
        },
        "after_evidence": {
          "timestamp": "03:37.200",
          "observation": "Active Raticate ex displays 1 Fire and 1 Psychic energy attached"
        },
        "uncertainty_id": null
      },
      {
        "turn": 7,
        "pokemon_id": "opp-2",
        "kind": "discard",
        "before": {
          "Darkness": 1
        },
        "after": {},
        "before_evidence": {
          "timestamp": "03:41.000",
          "observation": "Active Magmar has 1 Darkness energy before KO"
        },
        "action_evidence": {
          "timestamp": "03:46.400",
          "observation": "Magmar is knocked out by Boost Dash and discarded"
        },
        "after_evidence": {
          "timestamp": "03:47.000",
          "observation": "Magmar is in discard pile with 0 attached energy"
        },
        "uncertainty_id": null
      },
      {
        "turn": 8,
        "pokemon_id": "opp-5",
        "kind": "manual",
        "attachment_evidence": "movement_and_attached_icons",
        "before": {},
        "after": {
          "Darkness": 1
        },
        "before_evidence": {
          "timestamp": "04:08.000",
          "observation": "Active second Magmar has 0 energy attached"
        },
        "action_evidence": {
          "timestamp": "04:08.800",
          "observation": "Darkness energy moves from zone to active Magmar"
        },
        "after_evidence": {
          "timestamp": "04:09.200",
          "observation": "Active Magmar displays 1 Darkness energy attached"
        },
        "uncertainty_id": null
      },
      {
        "turn": 8,
        "pokemon_id": "player-3",
        "kind": "discard",
        "before": {
          "Fire": 1,
          "Psychic": 1
        },
        "after": {},
        "before_evidence": {
          "timestamp": "04:10.000",
          "observation": "Active Raticate ex has 1 Fire and 1 Psychic energy"
        },
        "action_evidence": {
          "timestamp": "04:13.400",
          "observation": "Raticate ex is knocked out and discarded"
        },
        "after_evidence": {
          "timestamp": "04:14.200",
          "observation": "Raticate ex is removed from the field"
        },
        "uncertainty_id": null
      }
    ]
  }
}
```

### COVERAGE.md
```markdown
# Coverage Ledger

- **Setup Interval**: 00:00.000 – 00:20.000
- **Turn 1 (Player)**: 00:20.200 – 00:29.200
  - Evidence anchors: `00:20.200` (turn start), `00:24.200` (Professor's Research played), `00:28.400` (turn end)
  - State delta: Player draws 2 cards via Professor's Research; no energy or attack on first turn.
- **Turn 2 (Opponent)**: 00:29.400 – 01:00.400
  - Evidence anchors: `00:29.400` (turn start), `00:33.200` (Poké Ball), `00:36.600` (Magmar benched), `00:38.400` (Poison Barb attached to Magmar), `00:42.200` (Copycat played), `00:48.800` (Poké Ball), `00:52.400` (Koffing benched), `00:53.200` (Happiny benched), `00:54.600` (Darkness Energy attached to Koffing), `00:56.200` (Reverse Thrust attack, 10 damage to Rattata, switches to Happiny)
  - State delta: Opponent benches Magmar, Koffing, Happiny; attacks with Koffing for 10 damage and switches Happiny to Active.
- **Turn 3 (Player)**: 01:00.600 – 01:32.000
  - Evidence anchors: `01:00.600` (turn start), `01:06.400` (Team Rocket's Researcher played, 4 heads), `01:21.600` (second Rattata benched), `01:23.000` (Raticate ex evolved), `01:26.400` (Drowzee benched), `01:27.800` (Raticate ex free retreats, Comfey promoted), `01:30.800` (Psychic Energy attached to Drowzee)
  - State delta: Player searches 4 Team Rocket cards; evolves Active Rattata to Raticate ex; free retreats Raticate ex to bench and promotes Comfey; benches second Rattata and Drowzee; attaches 1 Psychic energy to Drowzee.
- **Turn 4 (Opponent)**: 01:32.200 – 02:08.200
  - Evidence anchors: `01:32.200` (turn start), `01:34.800` (Fire Energy to Magmar), `01:35.800` (Copycat played), `01:43.200` (Weezing ex evolved on bench, Boiler Smog poisons/burns Comfey), `01:51.200` (Happiny free retreats, Magmar promoted), `01:52.800` (Poison Barb to Happiny), `01:57.600` (Derisive Roasting attack, 110 damage), `02:01.000` (Comfey KO'd), `02:04.000` (Opponent +1 point, score 1-0), `02:07.400` (Drowzee promoted)
  - State delta: Comfey knocked out; opponent scores 1 point; player promotes Drowzee.
- **Turn 5 (Player)**: 02:08.400 – 02:50.400
  - Evidence anchors: `02:08.400` (turn start), `02:14.600` (Hypno evolved), `02:17.600` (Sightseer played, gets Raticate ex), `02:24.800` (Raticate ex evolved on bench, Thieving Incisors steals Fire Energy from Magmar), `02:33.000` (Elegant Cape attached to Hypno, HP 90->120), `02:38.000` (Psychic Energy attached to Hypno), `02:39.600` (Entrap attack, pulls Weezing ex, deals 50 damage)
  - State delta: Hypno evolves, gains Cape and second Psychic energy; bench Raticate ex steals active Magmar's Fire energy; Hypno attacks Weezing ex for 50 damage and traps it active.
- **Turn 6 (Opponent)**: 02:50.600 – 03:32.600
  - Evidence anchors: `02:50.600` (turn start), `02:54.200` (Professor's Research played), `02:58.000` (second Weezing ex evolved on bench, Boiler Smog poisons/burns Hypno), `03:06.800` (X Speed played), `03:10.400` (Weezing ex retreats paying 1 Darkness, Magmar promoted), `03:12.400` (Darkness Energy attached to Magmar), `03:14.000` (Derisive Roasting attack, 110 damage to Hypno), `03:18.000` (Hypno KO'd by Poison in Checkup), `03:26.000` (Opponent +1 point, score 2-0), `03:31.000` (Raticate ex promoted)
  - State delta: Active Hypno survives attack with 10 HP, knocked out during Checkup by Poison; opponent scores 1 point (2-0); player promotes Raticate ex.
- **Turn 7 (Player)**: 03:32.800 – 03:53.400
  - Evidence anchors: `03:32.800` (turn start), `03:34.600` (Poké Ball played, fails/no basic), `03:36.400` (Psychic Energy attached to Raticate ex), `03:39.800` (Boost Dash attack, 70 damage), `03:42.200` (Magmar KO'd), `03:44.800` (Poison Barb poisons Raticate ex), `03:49.400` (Player +1 point, score 2-1), `03:51.400` (Happiny promoted)
  - State delta: Opponent's Active Magmar knocked out; player scores 1 point; Raticate ex takes Poison from Poison Barb; Happiny promoted.
- **Turn 8 (Opponent)**: 03:53.600 – 04:18.800
  - Evidence anchors: `03:53.600` (turn start), `03:56.400` (second Magmar benched), `03:58.400` (Team Rocket's Master Plan played, Confuses Raticate ex and Happiny), `04:06.600` (Happiny free retreats, second Magmar promoted), `04:08.800` (Darkness Energy attached to Magmar), `04:10.400` (Derisive Roasting attack, 110 damage), `04:12.600` (Raticate ex KO'd), `04:17.000` (Opponent +2 points, score 2-1 -> 3-1), `04:18.800` (Defeat screen)
  - State delta: Raticate ex knocked out; opponent awarded 2 points reaching winning condition; battle concludes.
- **Terminal Sequence**: 04:16.000 – 04:18.978
  - Score reaches opponent win threshold; Defeat banner displayed.

## Required Event Audit
- `Deck searches and failed searches:` 00:33.200 (Poké Ball -> Magmar), 00:48.800 (Poké Ball -> Koffing), 01:06.400 (Team Rocket's Researcher -> 4 Rocket cards), 02:17.600 (Sightseer -> Raticate ex), 03:34.600 (Poké Ball -> failed, no basic).
- `Energy attachments and acceleration:` 00:54.600 (Darkness to opp Koffing), 01:30.800 (Psychic to player Drowzee), 01:34.800 (Fire to opp Magmar), 02:28.600 (Thieving Incisors steals Fire from Magmar to Raticate ex), 02:38.000 (Psychic to player Hypno), 03:10.400 (1 Darkness paid to retreat Weezing ex), 03:12.400 (Darkness to opp Magmar), 03:23.400 (Hypno KO discards 2 Psychic), 03:36.400 (Psychic to player Raticate ex), 03:46.400 (Magmar KO discards 1 Darkness), 04:08.800 (Darkness to opp second Magmar), 04:13.400 (Raticate ex KO discards 1 Fire and 1 Psychic).
- `Return-to-hand, replay, and exchange events:` 00:42.200 (Copycat shuffles hand into deck, draws 4), 01:35.800 (Copycat shuffles hand into deck, draws 5).
- `Knockouts and score changes:` 02:01.000 (Comfey KO, opp 1 point, 02:04.000), 03:18.000 (Hypno KO by poison, opp 1 point, 03:26.000), 03:42.200 (Magmar KO, player 1 point, 03:49.400), 04:12.600 (Raticate ex KO, opp 2 points, 04:17.000).
- `Switches, retreats, and Bench changes:` 00:56.200 (Koffing Reverse Thrust switches Happiny in), 01:27.800 (Raticate ex free retreats, Comfey promoted), 01:51.200 (Happiny free retreats, Magmar promoted), 02:44.600 (Hypno Entrap forces Weezing ex in), 03:10.400 (Weezing ex retreats, Magmar promoted), 03:31.000 (Raticate ex promoted after Hypno KO), 03:51.400 (Happiny promoted after Magmar KO), 04:06.600 (Happiny free retreats, second Magmar promoted).
- `Terminal sequence:` 04:17.000 (+2 points awarded to opponent, reaching match limit), 04:18.800 ('Defeat' banner displayed).
```

### REVIEW.md
```markdown
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
```

### UNCERTAINTIES.json
```json
[]
```
<!-- END_BATTLE_PACKET -->