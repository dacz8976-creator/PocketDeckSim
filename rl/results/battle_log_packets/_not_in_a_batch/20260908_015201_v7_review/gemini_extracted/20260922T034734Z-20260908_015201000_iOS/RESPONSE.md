### SOURCE.json
```json
{
  "filename": "20260908_015201000_iOS.MP4",
  "source_path": "C:\\Users\\dacz8\\OneDrive\\Desktop\\Battle Logs\\20260908_015201000_iOS.MP4",
  "sha256": "65B404F8EC8CB712EF9D19FA5BC87E051EDC80050067BC179E8387AE404CE258",
  "bytes": 127098167,
  "duration_seconds": 68.12,
  "review_status": "partial",
  "index_update_performed": false,
  "media_move_performed": false,
  "recording_type": "incomplete_battle",
  "relationships": [],
  "model": "gemini-3.8-flash",
  "review_method": "static video processing at 5 source frames per second with high media resolution",
  "reviewer_attribution": "Gemini 3.8 Flash API first-pass draft",
  "outcome": "unknown",
  "battle_identity": {
    "opponent_label": {
      "state": "observed",
      "value": "Opponent",
      "timestamp_seconds": 4.2,
      "observation": "Opponent matchup banner shows label Opponent with AI badge"
    },
    "opening_player": {
      "state": "observed",
      "value": "Duraludon",
      "timestamp_seconds": 14.4,
      "observation": "Player puts Duraludon into the Active Spot"
    },
    "opening_opponent": {
      "state": "observed",
      "value": "Team Rocket's Rattata",
      "timestamp_seconds": 19.4,
      "observation": "Opponent opening Active card revealed as Team Rocket's Rattata"
    },
    "outcome": {
      "state": "unknown",
      "value": null,
      "timestamp_seconds": 68.12,
      "observation": "Video ends prematurely at 01:08.000 during turn 3"
    },
    "result_text": {
      "state": "not_shown",
      "value": null,
      "timestamp_seconds": 68.12,
      "observation": "No terminal result banner appears before recording cutoff"
    }
  },
  "evidence_audit": {
    "version": 1,
    "opponent_label": "Opponent",
    "match_mode": {
      "value": "solo",
      "evidence": [
        {
          "timestamp": "00:04.200",
          "observation": "AI badge displayed above generic Opponent label"
        }
      ],
      "uncertainty_id": null
    },
    "opponent_ai": {
      "value": "yes",
      "evidence": [
        {
          "timestamp": "00:04.200",
          "observation": "Explicit AI tag displayed above Opponent name"
        }
      ],
      "uncertainty_id": null
    },
    "auto": {
      "value": "off",
      "evidence": [
        {
          "timestamp": "00:08.800",
          "observation": "Auto toggle switch is in the off position"
        }
      ],
      "uncertainty_id": null
    },
    "terminal": {
      "outcome": "unknown",
      "outcome_evidence": [
        {
          "timestamp": "01:08.000",
          "observation": "Recording terminates mid-battle during turn 3 with score 0-0"
        }
      ],
      "result_text": null,
      "result_text_evidence": [
        {
          "timestamp": "01:08.000",
          "observation": "No victory or defeat banner shown before video ends"
        }
      ],
      "last_frame": {
        "timestamp": "01:08.000",
        "observation": "Opponent's turn 3 begins; board remains active as video cuts off"
      },
      "uncertainty_id": "U1"
    },
    "pokemon": [
      {
        "id": "player-1",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:14.400",
          "observation": "Duraludon placed in Active Spot with 0 Energy"
        },
        "final": {
          "Metal": 1
        },
        "final_evidence": {
          "timestamp": "01:05.000",
          "observation": "Duraludon has 1 Metal Energy attached"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-2",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:34.000",
          "observation": "Dratini placed onto player's Bench with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "01:08.000",
          "observation": "Dratini remains on Bench with 0 Energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-3",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:51.400",
          "observation": "Axew placed onto player's Bench with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "01:08.000",
          "observation": "Axew remains on Bench with 0 Energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-1",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:19.400",
          "observation": "Opponent reveals Team Rocket's Rattata in Active Spot with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "01:08.000",
          "observation": "Team Rocket's Rattata remains Active with 0 Energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-2",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:20.600",
          "observation": "Opponent reveals Corphish on Bench with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "01:08.000",
          "observation": "Corphish remains on Bench with 0 Energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-3",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:20.000",
          "observation": "Opponent reveals Team Rocket's Rattata on Bench with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "01:08.000",
          "observation": "Bench Team Rocket's Rattata remains with 0 Energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-4",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:27.800",
          "observation": "Opponent plays Chien-Pao ex onto Bench with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "01:08.000",
          "observation": "Chien-Pao ex remains on Bench with 0 Energy"
        },
        "uncertainty_id": null
      }
    ],
    "energy_events": [
      {
        "turn": 2,
        "pokemon_id": "player-1",
        "kind": "manual",
        "attachment_evidence": "movement_and_attached_icons",
        "before": {},
        "after": {
          "Metal": 1
        },
        "before_evidence": {
          "timestamp": "00:21.000",
          "observation": "Duraludon in Active Spot has no Energy attached"
        },
        "action_evidence": {
          "timestamp": "01:04.000",
          "observation": "Metal Energy dragged from Energy Zone to Active Duraludon"
        },
        "after_evidence": {
          "timestamp": "01:05.000",
          "observation": "Duraludon shows 1 attached Metal Energy icon"
        }
      }
    ]
  }
}
```

### COVERAGE.md
```markdown
# Battle Recording Coverage

## Setup Interval
- **00:00.000 - 00:05.400**: Loading and match introduction. Matchup: AI Opponent vs. Dacz8976.
- **00:05.600 - 00:08.200**: Coin flip. Result is black coin / "Going second" for player.
- **00:08.800 - 00:17.000**: Initial setup. Both players draw 5 cards. Player puts Duraludon in Active Spot. Opponent places 1 Active and 2 Benched cards face down.
- **00:19.200 - 00:22.800**: Cards revealed:
  - Opponent Active: Team Rocket's Rattata (HP 40).
  - Opponent Bench: Corphish (HP 60), Team Rocket's Rattata (HP 40).
  - Player Active: Duraludon (HP 100).

## Turn-by-Turn Phases
- **Turn 1 (Opponent)** [00:23.400 - 00:29.200]:
  - Evidence anchors: `00:23.400` (turn banner), `00:27.000` (Chien-Pao ex played to Bench), `00:29.000` (turn end).
  - State delta: Opponent plays Chien-Pao ex onto Bench. No Energy attached. No attack. Score: 0-0.
- **Turn 2 (Player)** [00:29.400 - 01:06.400]:
  - Evidence anchors: `00:29.400` (turn banner), `00:31.200` (draws Dratini), `00:33.800` (Dratini played to Bench), `00:39.400` (plays Professor's Research), `00:41.800` (draws Poké Ball and Axew), `00:46.400` (plays Poké Ball), `00:48.000` (finds Axew), `00:51.400` (Axew played to Bench), `00:56.200` (plays Rainbow Cave stadium), `01:00.000` (uses Rainbow Cave effect: discards Fighting Energy, generates Metal Energy), `01:04.000` (attaches Metal Energy to Duraludon), `01:06.200` (taps End Turn).
  - State delta: Hand updated; Bench gains Dratini and Axew; Rainbow Cave in play; Duraludon gains 1 Metal Energy. Score: 0-0.
- **Turn 3 (Opponent)** [01:06.600 - 01:08.000]:
  - Evidence anchors: `01:06.600` (Opponent's turn 3 banner), `01:08.000` (video truncates).
  - State delta: Turn 3 begins; video cuts off. Score: 0-0.

## Terminal Sequence
- Recording ends prematurely at `01:08.000`. Battle outcome is unknown.

## Reviewed Items
- [x] Setup and starting hands/positions
- [x] Turn 1 full execution
- [x] Turn 2 full execution and card sequencing
- [x] Truncated Turn 3 start

## Unresolved Intervals
- `01:08.000 - end of match`: Recording ends mid-turn during Opponent Turn 3. What is the terminal outcome and final score? (Tracked in U1).

## Required Event Audit
- `Deck searches and failed searches:` 00:46.400 - 00:48.200 (Poké Ball successfully searches deck and puts Basic Pokémon Axew into hand).
- `Energy attachments and acceleration:` 01:00.000 - 01:03.000 (Rainbow Cave discards generated Fighting Energy, produces Metal Energy); 01:03.800 - 01:05.000 (Manual attachment: 1 Metal Energy attached from Energy Zone to player's Active Duraludon).
- `Return-to-hand, replay, and exchange events:` none observed.
- `Knockouts and score changes:` none observed (Score remains 0-0).
- `Switches, retreats, and Bench changes:` 00:27.000 (Opponent benches Chien-Pao ex); 00:33.800 (Player benches Dratini); 00:51.400 (Player benches Axew).
- `Terminal sequence:` unknown (U1; video cuts off at 01:08.000 without showing conclusion).
```

### REVIEW.md
```markdown
# Battle Review: Dacz8976 vs. Opponent (AI)

- **Date**: Unknown (source filename suggests 2026-09-08, not verified in video).
- **Match Mode**: Solo (explicit `AI` badge displayed above Opponent name).
- **Auto State**: Off.
- **Players**: Player (`Dacz8976`) vs. Opponent (`AI`).
- **Starting Board**:
  - Player Active: Duraludon (HP 100, Dragon/Metal, 0 Energy).
  - Player Opening Hand: Rainbow Cave, Iris, Copycat, Professor's Research, Duraludon (placed Active).
  - Opponent Active: Team Rocket's Rattata (HP 40, 0 Energy).
  - Opponent Bench: Corphish (HP 60, 0 Energy), Team Rocket's Rattata (HP 40, 0 Energy).

---

## Timeline & Evidence Ledger

### Setup (00:00.000 - 00:22.800)
- Coin flip: Black coin / Going second.
- Both sides draw starting hands. Player places Duraludon as Active.
- Opponent reveals Active Team Rocket's Rattata, Bench Corphish and Team Rocket's Rattata.

### Turn 1: Opponent (00:23.400 - 00:29.200)
- **Observed actions**: Opponent plays Chien-Pao ex (HP 130) onto the Bench. No Energy attached (first-turn rule). Opponent passes.
- **State delta**: Opponent Bench has Corphish, Team Rocket's Rattata, and Chien-Pao ex.
- **Evidence anchors**:
  - `00:23.400`: Opponent turn banner.
  - `00:27.000`: Chien-Pao ex card played to Bench.
  - `00:29.000`: Turn transitions to player.

### Turn 2: Player (00:29.400 - 01:06.400)
- **Observed actions**:
  - Player draws Dratini (HP 60) for turn. Fighting Energy generated in Energy Zone.
  - Player plays Dratini onto the Bench.
  - Player plays Supporter Professor's Research, drawing Poké Ball and Axew (HP 70).
  - Player plays Item Poké Ball, searching and drawing an Axew.
  - Player plays Axew onto the Bench.
  - Player plays Stadium Rainbow Cave.
  - Prompt: "Use the effect of Rainbow Cave?". Player selects "Yes". The generated Fighting Energy is discarded and replaced with Metal Energy.
  - Player manually attaches Metal Energy to Active Duraludon.
  - Player ends turn without attacking.
- **State delta**:
  - Player Active: Duraludon (HP 100, 1 Metal Energy attached).
  - Player Bench: Dratini (HP 60, 0 Energy), Axew (HP 70, 0 Energy).
  - Stadium: Rainbow Cave active.
  - Player Hand: Iris, Copycat, Axew.
- **Evidence anchors**:
  - `00:31.200`: Dratini drawn.
  - `00:33.800`: Dratini placed on Bench.
  - `00:39.400`: Professor's Research played.
  - `00:41.800`: Poké Ball and Axew drawn.
  - `00:46.400`: Poké Ball played.
  - `00:48.000`: Axew revealed from deck into hand.
  - `00:51.400`: Axew benched.
  - `00:56.200`: Rainbow Cave played.
  - `01:00.000`: Rainbow Cave activated (Fighting Energy discarded -> Metal Energy produced).
  - `01:04.000` - `01:05.000`: Metal Energy attached to Duraludon.
  - `01:06.200`: Turn ended.

### Turn 3: Opponent (01:06.600 - 01:08.000)
- **Observed actions**: Opponent's turn starts. Video truncates at 01:08.000.
- **State delta**: None observed.
- **Evidence anchors**:
  - `01:06.600`: Turn 3 banner displayed.
  - `01:08.000`: Video ends.

---

## HP, Energy, Bench, Hand, and Score Reconciliation
- **Score**: 0 - 0 (no knockouts occurred).
- **Player Active Duraludon**: 100/100 HP, 1 Metal Energy attached.
- **Player Bench**: Dratini (60/60 HP, 0 Energy), Axew (70/70 HP, 0 Energy).
- **Opponent Active Team Rocket's Rattata**: 40/40 HP, 0 Energy.
- **Opponent Bench**: Corphish (60/60 HP, 0 Energy), Team Rocket's Rattata (40/40 HP, 0 Energy), Chien-Pao ex (130/130 HP, 0 Energy).

## Mechanics & Tactical Observations
- Player utilized Rainbow Cave's effect on Turn 2 to convert unusable Fighting Energy into Metal Energy, enabling the first Energy attachment required for Duraludon's Power Beam (which requires Metal + Fighting).

## Outcome
- Unknown. Recording is incomplete and terminates at 01:08.000.

## Explicit Uncertainties
- See UNCERTAINTIES.json entry U1 regarding the truncated recording and unresolved match outcome.

---
*Status: Partial pending independent Sol verification*
```

### UNCERTAINTIES.json
```json
[
  {
    "id": "U1",
    "start_timestamp": "01:08.000",
    "end_timestamp": "01:08.000",
    "claim_or_question": "What is the final match outcome and score?",
    "why_uncertain": "The video recording abruptly terminates at 01:08.000 as Opponent Turn 3 begins, before any attacks, knockouts, or victory conditions are resolved.",
    "consequence_if_wrong": "The battle outcome would be falsely marked as a win, loss, or draw instead of remaining accurately classified as unknown.",
    "recommended_sol_check": "Verify whether a longer capture exists for this match to determine the final terminal result."
  }
]
```
<!-- END_BATTLE_PACKET -->