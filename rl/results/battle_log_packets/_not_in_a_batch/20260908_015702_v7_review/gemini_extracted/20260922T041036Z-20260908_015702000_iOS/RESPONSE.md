### SOURCE.json
```json
{
  "filename": "20260908_015702000_iOS.MP4",
  "source_path": "C:\\Users\\dacz8\\OneDrive\\Desktop\\Battle Logs\\20260908_015702000_iOS.MP4",
  "sha256": "3FBD29A85A17B5F4B4F7DDD3D7EE15B2177503FF3E15C56314DE9CC60EDCFB2D",
  "bytes": 507514203,
  "duration_seconds": 272.803,
  "review_status": "partial",
  "index_update_performed": false,
  "media_move_performed": false,
  "model": "gemini-3.8-flash",
  "reviewer": "Gemini 3.8 Flash API first-pass draft",
  "battle_identity": {
    "opponent_label": {
      "state": "observed",
      "value": "Opponent",
      "timestamp_seconds": 0.8,
      "observation": "Opponent nameplate shows 'Opponent'"
    },
    "opening_player": {
      "state": "observed",
      "value": "Duraludon",
      "timestamp_seconds": 0.0,
      "observation": "Player's active spot has Duraludon (100 HP)"
    },
    "opening_opponent": {
      "state": "observed",
      "value": "Team Rocket's Rattata",
      "timestamp_seconds": 0.0,
      "observation": "Opponent's active spot has Team Rocket's Rattata (40 HP)"
    },
    "outcome": {
      "state": "observed",
      "value": "player_win",
      "timestamp_seconds": 269.0,
      "observation": "Player reaches 3 points after knocking out Chien-Pao ex, screen fades to victory transition"
    },
    "result_text": {
      "state": "not_shown",
      "value": null,
      "timestamp_seconds": 272.8,
      "observation": "Video cuts to white screen before the final 'VICTORY' banner renders"
    }
  },
  "evidence_audit": {
    "version": 1,
    "opponent_label": "Opponent",
    "match_mode": {
      "value": "unknown",
      "evidence": [
        {
          "timestamp": "00:00.800",
          "observation": "Opponent label displays generic 'Opponent' nameplate"
        }
      ],
      "uncertainty_id": "U1"
    },
    "opponent_ai": {
      "value": "unknown",
      "evidence": [
        {
          "timestamp": "00:00.800",
          "observation": "Generic 'Opponent' label without explicit AI or Solo indicator tag"
        }
      ],
      "uncertainty_id": "U1"
    },
    "auto": {
      "value": "off",
      "evidence": [
        {
          "timestamp": "00:00.000",
          "observation": "Auto button visible on right side of opponent board, untoggled (white circle left/off)"
        },
        {
          "timestamp": "00:54.000",
          "observation": "Auto toggle tapped to 'On' (green checkmark)"
        }
      ],
      "uncertainty_id": null
    },
    "terminal": {
      "outcome": "player_win",
      "outcome_evidence": [
        {
          "timestamp": "04:29.000",
          "observation": "Player score circle 3 animates active; '+2 points!' popup displays over player's avatar"
        }
      ],
      "result_text": null,
      "result_text_evidence": [
        {
          "timestamp": "04:32.600",
          "observation": "Video terminates on full white screen before victory banner appears"
        }
      ],
      "last_frame": {
        "timestamp": "04:32.600",
        "observation": "Pure white screen at video end"
      },
      "uncertainty_id": null
    },
    "pokemon": [
      {
        "id": "player-1",
        "owner": "player",
        "initial": {
          "Metal": 1
        },
        "initial_evidence": {
          "timestamp": "00:00.000",
          "observation": "Active Duraludon with 1 Metal Energy attached"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "01:31.600",
          "observation": "Duraludon knocked out by Chien-Pao ex Diving Icicles and sent to discard"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-2",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:00.000",
          "observation": "Bench Axew (70 HP) with 0 Energy"
        },
        "final": {
          "Fighting": 2,
          "Metal": 1
        },
        "final_evidence": {
          "timestamp": "04:28.000",
          "observation": "Haxorus evolved from Fraxure in active spot with 2 Fighting and 1 Metal Energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-3",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:00.000",
          "observation": "Bench Dratini (60 HP) with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "03:30.000",
          "observation": "Dratini on bench knocked out by Chien-Pao ex Diving Icicles"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-4",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:43.000",
          "observation": "Second Dratini played onto bench"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "04:31.000",
          "observation": "Dragonair (evolved from Dratini) on bench with 0 Energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "player-5",
        "owner": "player",
        "initial": {},
        "initial_evidence": {
          "timestamp": "02:44.200",
          "observation": "Second Axew played onto bench"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "04:31.000",
          "observation": "Axew on bench with 0 Energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-1",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:00.000",
          "observation": "Active Team Rocket's Rattata (40 HP) with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "00:04.600",
          "observation": "Team Rocket's Rattata retreats to bench"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-2",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:00.000",
          "observation": "Bench Chien-Pao ex (130 HP) with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "04:26.600",
          "observation": "Chien-Pao ex knocked out by Haxorus Frenzied Blade and sent to discard"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-3",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:00.000",
          "observation": "Bench Corphish (60 HP) with 0 Energy"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "02:54.600",
          "observation": "Crawdaunt (evolved from Corphish) knocked out by Haxorus Frenzied Blade"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-4",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "00:00.000",
          "observation": "Second Bench Team Rocket's Rattata (40 HP) with 0 Energy"
        },
        "final": {
          "Water": 1
        },
        "final_evidence": {
          "timestamp": "04:31.000",
          "observation": "Team Rocket's Raticate ex evolved on bench with 1 Water Energy"
        },
        "uncertainty_id": null
      },
      {
        "id": "opp-5",
        "owner": "opponent",
        "initial": {},
        "initial_evidence": {
          "timestamp": "03:22.800",
          "observation": "Corphish (60 HP) played onto opponent bench"
        },
        "final": {},
        "final_evidence": {
          "timestamp": "04:31.000",
          "observation": "Corphish on bench with 0 Energy"
        },
        "uncertainty_id": null
      }
    ],
    "energy_events": [
      {
        "turn": 3,
        "pokemon_id": "opp-2",
        "kind": "manual",
        "before": {},
        "after": {
          "Water": 1
        },
        "before_evidence": {
          "timestamp": "00:06.000",
          "observation": "Chien-Pao ex in active spot with 0 Energy"
        },
        "action_evidence": {
          "timestamp": "00:07.000",
          "observation": "Water Energy moves from opponent Energy Zone to active Chien-Pao ex"
        },
        "after_evidence": {
          "timestamp": "00:07.400",
          "observation": "Chien-Pao ex has 1 Water Energy icon attached"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 4,
        "pokemon_id": "player-1",
        "kind": "manual",
        "before": {
          "Metal": 1
        },
        "after": {
          "Fighting": 1,
          "Metal": 1
        },
        "before_evidence": {
          "timestamp": "00:46.000",
          "observation": "Duraludon has 1 Metal Energy attached"
        },
        "action_evidence": {
          "timestamp": "00:47.000",
          "observation": "Fighting Energy dragged from player Energy Zone onto active Duraludon"
        },
        "after_evidence": {
          "timestamp": "00:48.200",
          "observation": "Duraludon shows 1 Fighting and 1 Metal Energy attached"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 5,
        "pokemon_id": "opp-2",
        "kind": "manual",
        "before": {
          "Water": 1
        },
        "after": {
          "Water": 2
        },
        "before_evidence": {
          "timestamp": "01:01.000",
          "observation": "Chien-Pao ex has 1 Water Energy attached"
        },
        "action_evidence": {
          "timestamp": "01:02.000",
          "observation": "Water Energy moves from opponent Energy Zone to active Chien-Pao ex"
        },
        "after_evidence": {
          "timestamp": "01:02.400",
          "observation": "Chien-Pao ex has 2 Water Energy attached"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 6,
        "pokemon_id": "player-1",
        "kind": "manual",
        "before": {
          "Fighting": 1,
          "Metal": 1
        },
        "after": {
          "Fighting": 1,
          "Metal": 2
        },
        "before_evidence": {
          "timestamp": "01:12.400",
          "observation": "Duraludon has 1 Fighting and 1 Metal Energy"
        },
        "action_evidence": {
          "timestamp": "01:13.000",
          "observation": "Metal Energy attached to Duraludon"
        },
        "after_evidence": {
          "timestamp": "01:13.400",
          "observation": "Duraludon has 1 Fighting and 2 Metal Energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 7,
        "pokemon_id": "opp-2",
        "kind": "manual",
        "before": {
          "Water": 2
        },
        "after": {
          "Water": 3
        },
        "before_evidence": {
          "timestamp": "01:20.400",
          "observation": "Chien-Pao ex has 2 Water Energy"
        },
        "action_evidence": {
          "timestamp": "01:21.000",
          "observation": "Water Energy attaches to Chien-Pao ex"
        },
        "after_evidence": {
          "timestamp": "01:21.400",
          "observation": "Chien-Pao ex has 3 Water Energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 7,
        "pokemon_id": "opp-2",
        "kind": "discard",
        "before": {
          "Water": 3
        },
        "after": {},
        "before_evidence": {
          "timestamp": "01:26.400",
          "observation": "Chien-Pao ex has 3 Water Energy"
        },
        "action_evidence": {
          "timestamp": "01:26.800",
          "observation": "Chien-Pao ex uses Diving Icicles (Discard all Water Energy)"
        },
        "after_evidence": {
          "timestamp": "01:30.000",
          "observation": "Chien-Pao ex has 0 Energy attached"
        },
        "uncertainty_id": null
      },
      {
        "turn": 7,
        "pokemon_id": "player-1",
        "kind": "discard",
        "before": {
          "Fighting": 1,
          "Metal": 2
        },
        "after": {},
        "before_evidence": {
          "timestamp": "01:28.000",
          "observation": "Duraludon has 3 Energy attached"
        },
        "action_evidence": {
          "timestamp": "01:29.400",
          "observation": "Duraludon takes 130 damage, HP drops to 0"
        },
        "after_evidence": {
          "timestamp": "01:31.400",
          "observation": "Duraludon knocked out to discard pile, energy lost"
        },
        "uncertainty_id": null
      },
      {
        "turn": 8,
        "pokemon_id": "player-3",
        "kind": "manual",
        "before": {},
        "after": {
          "Fighting": 1
        },
        "before_evidence": {
          "timestamp": "01:39.000",
          "observation": "Active Dratini has 0 Energy"
        },
        "action_evidence": {
          "timestamp": "01:48.400",
          "observation": "Fighting Energy dragged onto active Dratini"
        },
        "after_evidence": {
          "timestamp": "01:49.000",
          "observation": "Active Dratini shows 1 Fighting Energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 9,
        "pokemon_id": "opp-4",
        "kind": "manual",
        "before": {},
        "after": {
          "Water": 1
        },
        "before_evidence": {
          "timestamp": "01:58.000",
          "observation": "Bench Team Rocket's Raticate ex has 0 Energy"
        },
        "action_evidence": {
          "timestamp": "02:00.000",
          "observation": "Water Energy attaches to bench Team Rocket's Raticate ex"
        },
        "after_evidence": {
          "timestamp": "02:00.400",
          "observation": "Team Rocket's Raticate ex has 1 Water Energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 10,
        "pokemon_id": "player-2",
        "kind": "manual",
        "before": {},
        "after": {
          "Fighting": 1
        },
        "before_evidence": {
          "timestamp": "02:08.800",
          "observation": "Bench Haxorus has 0 Energy"
        },
        "action_evidence": {
          "timestamp": "02:09.400",
          "observation": "Fighting Energy attached to bench Haxorus"
        },
        "after_evidence": {
          "timestamp": "02:10.000",
          "observation": "Bench Haxorus shows 1 Fighting Energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 11,
        "pokemon_id": "opp-3",
        "kind": "manual",
        "before": {},
        "after": {
          "Water": 1
        },
        "before_evidence": {
          "timestamp": "02:12.600",
          "observation": "Crawdaunt in active spot has 0 Energy"
        },
        "action_evidence": {
          "timestamp": "02:13.200",
          "observation": "Water Energy attaches to Crawdaunt"
        },
        "after_evidence": {
          "timestamp": "02:13.600",
          "observation": "Crawdaunt shows 1 Water Energy attached"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 12,
        "pokemon_id": "player-3",
        "kind": "retreat",
        "before": {
          "Fighting": 1
        },
        "after": {},
        "before_evidence": {
          "timestamp": "02:19.400",
          "observation": "Active Dratini has 1 Fighting Energy"
        },
        "action_evidence": {
          "timestamp": "02:20.000",
          "observation": "Player retreats Dratini by paying 1 Energy"
        },
        "after_evidence": {
          "timestamp": "02:20.600",
          "observation": "Dratini moves to bench with 0 Energy"
        },
        "uncertainty_id": null
      },
      {
        "turn": 12,
        "pokemon_id": "player-2",
        "kind": "manual",
        "before": {
          "Fighting": 1
        },
        "after": {
          "Fighting": 2
        },
        "before_evidence": {
          "timestamp": "02:44.800",
          "observation": "Haxorus has 1 Fighting Energy"
        },
        "action_evidence": {
          "timestamp": "02:45.400",
          "observation": "Fighting Energy attached to active Haxorus"
        },
        "after_evidence": {
          "timestamp": "02:45.800",
          "observation": "Active Haxorus shows 2 Fighting Energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 12,
        "pokemon_id": "opp-3",
        "kind": "discard",
        "before": {
          "Water": 1
        },
        "after": {},
        "before_evidence": {
          "timestamp": "02:51.600",
          "observation": "Crawdaunt has 1 Water Energy"
        },
        "action_evidence": {
          "timestamp": "02:52.400",
          "observation": "Crawdaunt takes 170 damage from Frenzied Blade and is knocked out"
        },
        "after_evidence": {
          "timestamp": "02:54.600",
          "observation": "Crawdaunt sent to discard pile"
        },
        "uncertainty_id": null
      },
      {
        "turn": 13,
        "pokemon_id": "opp-2",
        "kind": "manual",
        "before": {},
        "after": {
          "Water": 1
        },
        "before_evidence": {
          "timestamp": "03:02.400",
          "observation": "Chien-Pao ex in active spot has 0 Energy"
        },
        "action_evidence": {
          "timestamp": "03:06.200",
          "observation": "Water Energy attaches to Chien-Pao ex"
        },
        "after_evidence": {
          "timestamp": "03:06.600",
          "observation": "Chien-Pao ex shows 1 Water Energy"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 14,
        "pokemon_id": "player-2",
        "kind": "manual",
        "before": {
          "Fighting": 2
        },
        "after": {
          "Fighting": 2,
          "Metal": 1
        },
        "before_evidence": {
          "timestamp": "03:44.800",
          "observation": "Haxorus has 2 Fighting Energy"
        },
        "action_evidence": {
          "timestamp": "03:45.200",
          "observation": "Metal Energy attached to active Haxorus"
        },
        "after_evidence": {
          "timestamp": "03:45.600",
          "observation": "Haxorus shows 2 Fighting and 1 Metal Energy attached"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 15,
        "pokemon_id": "opp-2",
        "kind": "manual",
        "before": {
          "Water": 1
        },
        "after": {
          "Water": 2
        },
        "before_evidence": {
          "timestamp": "03:53.600",
          "observation": "Chien-Pao ex has 1 Water Energy"
        },
        "action_evidence": {
          "timestamp": "03:54.400",
          "observation": "Water Energy attaches to Chien-Pao ex"
        },
        "after_evidence": {
          "timestamp": "03:54.800",
          "observation": "Chien-Pao ex shows 2 Water Energy attached"
        },
        "attachment_evidence": "movement_and_attached_icons",
        "uncertainty_id": null
      },
      {
        "turn": 16,
        "pokemon_id": "player-2",
        "kind": "effect",
        "before": {
          "Fighting": 2,
          "Metal": 1
        },
        "after": {
          "Fighting": 2,
          "Metal": 2
        },
        "before_evidence": {
          "timestamp": "04:18.200",
          "observation": "Haxorus has 2 Fighting and 1 Metal Energy"
        },
        "action_evidence": {
          "timestamp": "04:19.000",
          "observation": "Dragonair uses Ability Dragon's Blessing to attach Metal Energy from discard pile to active Haxorus"
        },
        "after_evidence": {
          "timestamp": "04:20.000",
          "observation": "Haxorus shows 2 Fighting and 2 Metal Energy attached"
        },
        "uncertainty_id": null
      },
      {
        "turn": 16,
        "pokemon_id": "opp-2",
        "kind": "discard",
        "before": {
          "Water": 2
        },
        "after": {},
        "before_evidence": {
          "timestamp": "04:24.000",
          "observation": "Chien-Pao ex has 2 Water Energy"
        },
        "action_evidence": {
          "timestamp": "04:24.400",
          "observation": "Haxorus uses Frenzied Blade for 150 damage, knocking out Chien-Pao ex"
        },
        "after_evidence": {
          "timestamp": "04:26.600",
          "observation": "Chien-Pao ex sent to discard pile"
        },
        "uncertainty_id": null
      }
    ]
  }
}
```

### COVERAGE.md
```markdown
# Coverage Log

- [x] Initial board inspection (00:00.000 - 00:01.000)
- [x] Turn 3 (Opponent): 00:00.000 - 00:13.000
  - Evidence anchors: 00:00.400 (Rattata retreat cost reduction banner), 00:04.600 (Chien-Pao ex promoted), 00:07.000 (Water Energy attached), 00:09.000 (Icicle attack declared), 00:10.400 (20 damage to Duraludon).
  - State delta: Active Rattata retreated to Bench; Chien-Pao ex promoted to Active, received 1 Water Energy; Duraludon damaged to 80/100 HP.
- [x] Turn 4 (Player): 00:13.000 - 00:54.400
  - Evidence anchors: 00:18.200 (Bench Axew evolves into Fraxure), 00:25.400 (Rainbow Cave used), 00:33.800 (Copycat played), 00:43.000 (Dratini placed on Bench), 00:47.000 (Fighting Energy attached to Duraludon), 00:51.400 (Power Beam attack), 00:53.600 (50 damage to Chien-Pao ex).
  - State delta: Bench Axew evolved to Fraxure; Dratini placed on Bench; Duraludon gained Fighting Energy; Chien-Pao ex damaged to 80/130 HP.
- [x] Turn 5 (Opponent): 00:54.400 - 01:07.200
  - Evidence anchors: 00:58.200 (Bench Corphish evolves into Crawdaunt), 00:59.400 (Unruly Claw ability triggers), 01:02.000 (Water Energy attached to Chien-Pao ex), 01:04.000 (Icicle attack declared), 01:05.400 (20 damage to Duraludon).
  - State delta: Corphish evolved into Crawdaunt; Chien-Pao ex gained Water Energy (now 2); Duraludon damaged to 60/100 HP.
- [x] Turn 6 (Player): 01:07.200 - 01:18.000
  - Evidence anchors: 01:13.000 (Metal Energy attached to Duraludon), 01:15.000 (Power Beam attack), 01:16.400 (50 damage to Chien-Pao ex).
  - State delta: Duraludon gained Metal Energy; Chien-Pao ex damaged to 30/130 HP.
- [x] Turn 7 (Opponent): 01:18.000 - 01:37.600
  - Evidence anchors: 01:21.000 (Water Energy attached to Chien-Pao ex), 01:27.000 (Diving Icicles attack), 01:28.400 (130 damage to Duraludon, KO), 01:33.400 (Opponent score 1-0), 01:37.000 (Active Dratini promoted).
  - State delta: Chien-Pao ex attached 3rd Water Energy, discarded all 3 to use Diving Icicles; Duraludon knocked out (Opponent 1 pt); Dratini promoted.
- [x] Turn 8 (Player): 01:37.600 - 01:49.400
  - Evidence anchors: 01:43.200 (Poké Ball played, fails to find target), 01:48.400 (Fighting Energy attached to active Dratini), 01:49.200 (Turn passed).
  - State delta: Poké Ball failed search; Dratini gained Fighting Energy; turn ended without attack.
- [x] Turn 9 (Opponent): 01:49.400 - 02:02.200
  - Evidence anchors: 01:53.200 (Professor's Research played), 01:57.200 (Bench Rattata evolves into Team Rocket's Raticate ex), 02:00.000 (Water Energy attached to Raticate ex), 02:01.400 (Crawdaunt switched/promoted into Active).
  - State delta: Opponent drew 2 cards; Bench Rattata evolved into Raticate ex and received Water Energy; Crawdaunt switched to Active.
- [x] Turn 10 (Player): 02:02.200 - 02:11.200
  - Evidence anchors: 02:08.200 (Bench Fraxure evolves into Haxorus), 02:09.400 (Fighting Energy attached to Haxorus), 02:11.000 (Turn passed).
  - State delta: Fraxure evolved to Haxorus; Haxorus received Fighting Energy; turn ended without attack.
- [x] Turn 11 (Opponent): 02:11.200 - 02:14.600
  - Evidence anchors: 02:13.200 (Water Energy attached to Active Crawdaunt), 02:14.400 (Turn passed).
  - State delta: Active Crawdaunt gained 1 Water Energy; turn ended without attack.
- [x] Turn 12 (Player): 02:14.600 - 03:03.800
  - Evidence anchors: 02:20.000 (Active Dratini retreats for 1 Energy), 02:20.600 (Haxorus promoted to Active), 02:44.200 (Axew placed on Bench), 02:45.400 (Fighting Energy attached to Haxorus), 02:47.400 (Iris played), 02:51.000 (Frenzied Blade attack), 02:52.400 (170 damage to Crawdaunt, KO), 02:57.600 (Player score 2-1).
  - State delta: Dratini retreated; Haxorus promoted; Axew benched; Haxorus gained 2nd Fighting Energy; Iris activated (+1 bonus point on KO); Crawdaunt knocked out; Player awarded 2 points (score 2-1); Chien-Pao ex promoted.
- [x] Turn 13 (Opponent): 03:03.800 - 03:34.800
  - Evidence anchors: 03:06.200 (Water Energy attached to Chien-Pao ex), 03:08.800 (Second Bench Rattata evolves into Team Rocket's Raticate ex), 03:14.600 (Team Rocket Grunt played; flips 2 heads, 1 tails), 03:22.800 (Corphish benched), 03:26.400 (Chien-Pao ex uses Diving Icicles targeting Bench Dratini), 03:30.000 (Bench Dratini knocked out), 03:33.400 (Opponent score 2-2).
  - State delta: Opponent evolved 2nd Raticate ex; discarded Energy from Haxorus via Grunt; played Corphish; Chien-Pao ex discarded 1 Water Energy to KO bench Dratini; Opponent score reaches 2 points.
- [x] Turn 14 (Player): 03:34.800 - 03:51.800
  - Evidence anchors: 03:40.800 (Bench Dratini evolves into Dragonair), 03:45.200 (Metal Energy attached to Haxorus), 03:47.400 (Rainbow Cave effect used), 03:51.600 (Turn passed).
  - State delta: Bench Dratini evolved into Dragonair; Metal Energy attached to Haxorus; turn ended without attack.
- [x] Turn 15 (Opponent): 03:51.800 - 04:11.200
  - Evidence anchors: 03:54.400 (Water Energy attached to Chien-Pao ex), 03:55.400 (Corphish evolves into Crawdaunt), 03:59.600 (Team Rocket Grunt played; flips 0 heads, 1 tails), 04:08.000 (Icicle attack declared), 04:09.400 (20 damage to Haxorus).
  - State delta: Chien-Pao ex gained Water Energy; Corphish evolved into Crawdaunt; Grunt failed; Haxorus damaged to 130/150 HP.
- [x] Turn 16 (Player): 04:11.200 - 04:32.600
  - Evidence anchors: 04:17.000 (Dragonair Ability Dragon's Blessing activated), 04:19.000 (Metal Energy attached from discard to active Haxorus), 04:23.000 (Frenzied Blade attack declared), 04:24.400 (150 damage dealt to Chien-Pao ex, KO), 04:29.000 (Player score reaches 3 points, '+2 points!' animation), 04:32.600 (Screen transitions to white at video end).
  - State delta: Dragonair accelerated Metal Energy to Haxorus; Haxorus attacked Chien-Pao ex for 150 damage, knocking it out; Player reached 3 points for the win.

## Required Event Audit
- `Deck searches and failed searches:` 01:43.200 Poké Ball played with message "There are no cards in the deck that can be the target of the effect" (failed search).
- `Energy attachments and acceleration:` 00:07.000 (Water to opp Chien-Pao ex), 00:47.000 (Fighting to player Duraludon), 01:02.000 (Water to opp Chien-Pao ex), 01:13.000 (Metal to player Duraludon), 01:21.000 (Water to opp Chien-Pao ex), 01:48.400 (Fighting to player Dratini), 02:00.000 (Water to opp Raticate ex), 02:09.400 (Fighting to player Haxorus), 02:13.200 (Water to opp Crawdaunt), 02:45.400 (Fighting to player Haxorus), 03:06.200 (Water to opp Chien-Pao ex), 03:45.200 (Metal to player Haxorus), 03:54.400 (Water to opp Chien-Pao ex), 04:19.000 (Metal from discard to player Haxorus via Dragon's Blessing).
- `Return-to-hand, replay, and exchange events:` 00:33.800 (Copycat played; shuffles hand into deck and redraws).
- `Knockouts and score changes:` 01:29.400 Duraludon knocked out (Opponent score 1-0 at 01:33.400); 02:52.400 Crawdaunt knocked out by Haxorus with Iris active (Player score 2-1 at 02:57.600); 03:30.000 Bench Dratini knocked out by Diving Icicles (Opponent score 2-2 at 03:33.400); 04:24.400 Chien-Pao ex knocked out by Haxorus (Player score reaches 3 points at 04:29.000).
- `Switches, retreats, and Bench changes:` 00:04.600 (Opponent Rattata retreats, Chien-Pao ex promoted); 01:37.000 (Player Dratini promoted post-KO); 02:01.400 (Opponent switches Crawdaunt to Active); 02:20.000 (Player Dratini retreats, Haxorus promoted); 03:01.400 (Opponent Chien-Pao ex promoted post-KO).
- `Terminal sequence:` 04:24.400 Haxorus knocks out Chien-Pao ex for 150 damage; 04:28.800 3rd point icon illuminates on player side; 04:29.600 '+2 points!' banner overlays player icon; 04:32.000 screen fades to white; video terminates at 04:32.600 before text banner renders.
```

### REVIEW.md
```markdown
# Battle Review: 20260908_015702000_iOS.MP4

- **Date:** 2026-09-08 (derived from filename)
- **Mode:** Match mode unknown (opponent labeled "Opponent"); Auto off initially, toggled on by player at 00:54.000.
- **Player:** Dacz8976
- **Opponent:** Opponent
- **Starting Board:**
  - Player Active: Duraludon (100 HP, 1 Metal Energy)
  - Player Bench: Axew (70 HP), Dratini (60 HP)
  - Opponent Active: Team Rocket's Rattata (40 HP)
  - Opponent Bench: Chien-Pao ex (130 HP), Corphish (60 HP), Team Rocket's Rattata (40 HP)
  - Stadium: Rainbow Cave

---

## Evidence Ledger

### Turn 3 (Opponent)
- **Observed actions:** Opponent begins turn. Team Rocket's Rattata retreats to the bench at 00:04.600; Chien-Pao ex is promoted to the active spot. Opponent attaches 1 Water Energy from the Energy Zone to Chien-Pao ex (00:07.000). Chien-Pao ex uses Icicle (00:09.000) dealing 20 damage to active Duraludon (00:10.400).
- **State delta:** Opponent active becomes Chien-Pao ex with 1 Water Energy. Duraludon HP: 80/100.
- **Evidence anchors:** 00:04.600 (retreat/promotion), 00:07.000 (Energy attachment), 00:10.400 (damage).

### Turn 4 (Player)
- **Observed actions:** Player evolves Bench Axew into Fraxure (00:18.200). Activates Rainbow Cave effect to change generated Energy (00:25.400). Plays Supporter Copycat (00:33.800), shuffling hand and drawing cards. Plays Dratini to Bench (00:43.000). Attaches Fighting Energy to Duraludon (00:47.000). Duraludon uses Power Beam (00:51.400), dealing 50 damage to Chien-Pao ex (00:53.600). Player toggles Auto on (00:54.000).
- **State delta:** Bench Axew -> Fraxure. Dratini benched. Duraludon has 1 Metal, 1 Fighting Energy. Chien-Pao ex HP: 80/130.
- **Evidence anchors:** 00:18.200 (evolution), 00:43.000 (Dratini play), 00:47.000 (attachment), 00:53.600 (50 damage).

### Turn 5 (Opponent)
- **Observed actions:** Bench Corphish evolves into Crawdaunt (00:58.200), triggering Unruly Claw ability. Water Energy attached to active Chien-Pao ex (01:02.000). Chien-Pao ex attacks with Icicle (01:04.000), dealing 20 damage to Duraludon (01:05.400).
- **State delta:** Crawdaunt on bench. Chien-Pao ex has 2 Water Energy. Duraludon HP: 60/100.
- **Evidence anchors:** 00:58.200 (evolution), 01:02.000 (attachment), 01:05.400 (damage).

### Turn 6 (Player)
- **Observed actions:** Player attaches Metal Energy to Duraludon (01:13.000). Duraludon uses Power Beam (01:15.000), dealing 50 damage to Chien-Pao ex (01:16.400).
- **State delta:** Duraludon has 1 Fighting, 2 Metal Energy. Chien-Pao ex HP: 30/130.
- **Evidence anchors:** 01:13.000 (attachment), 01:16.400 (damage).

### Turn 7 (Opponent)
- **Observed actions:** Water Energy attached to Chien-Pao ex (01:21.000). Chien-Pao ex attacks with Diving Icicles (01:27.000), discarding all Water Energy and dealing 130 damage to Duraludon (01:28.400). Duraludon is knocked out (01:29.400). Opponent gains 1 point (01:33.400). Dratini promoted to Active (01:37.000).
- **State delta:** Duraludon discarded. Opponent score: 1. Dratini Active. Chien-Pao ex has 0 Energy.
- **Evidence anchors:** 01:21.000 (attachment), 01:28.400 (130 damage/KO), 01:33.400 (point award), 01:37.000 (promotion).

### Turn 8 (Player)
- **Observed actions:** Player plays Poké Ball (01:43.200); system shows "There are no cards in the deck that can be the target of the effect". Attaches Fighting Energy to active Dratini (01:48.400). Turn passed without attacking.
- **State delta:** Dratini has 1 Fighting Energy.
- **Evidence anchors:** 01:43.200 (failed search), 01:48.400 (attachment).

### Turn 9 (Opponent)
- **Observed actions:** Opponent plays Professor's Research (01:53.200), drawing 2 cards. Bench Rattata evolves into Team Rocket's Raticate ex (01:57.200). Attaches Water Energy to Raticate ex (02:00.000). Switches Crawdaunt to Active spot (02:01.400). Turn ends.
- **State delta:** Raticate ex on bench with 1 Water Energy. Active is now Crawdaunt (100 HP, 0 Energy).
- **Evidence anchors:** 01:53.200 (supporter), 01:57.200 (evolution), 02:00.000 (attachment), 02:01.400 (switch).

### Turn 10 (Player)
- **Observed actions:** Bench Fraxure evolves into Haxorus (02:08.200). Fighting Energy attached to Haxorus (02:09.400). Turn passed.
- **State delta:** Haxorus on bench with 1 Fighting Energy.
- **Evidence anchors:** 02:08.200 (evolution), 02:09.400 (attachment).

### Turn 11 (Opponent)
- **Observed actions:** Water Energy attached to Active Crawdaunt (02:13.200). Opponent ends turn without attacking.
- **State delta:** Crawdaunt has 1 Water Energy.
- **Evidence anchors:** 02:13.200 (attachment).

### Turn 12 (Player)
- **Observed actions:** Active Dratini retreats by paying 1 Fighting Energy (02:20.000). Haxorus promoted to Active (02:20.600). Player benches Axew (02:44.200). Attaches Fighting Energy to Haxorus (02:45.400). Plays Supporter Iris (02:47.400), adding 1 extra point if opponent Active is knocked out by Haxorus this turn. Haxorus uses Frenzied Blade (02:51.000), dealing 170 damage to Crawdaunt (02:52.400). Crawdaunt is knocked out. Player earns 2 points (02:57.600). Opponent promotes Chien-Pao ex (03:01.400).
- **State delta:** Score: Player 2, Opponent 1. Active: Haxorus (150 HP, 2 Fighting Energy). Opponent Active: Chien-Pao ex (30/130 HP, 0 Energy).
- **Evidence anchors:** 02:20.000 (retreat), 02:47.400 (Iris), 02:52.400 (170 damage/KO), 02:57.600 (+2 points).

### Turn 13 (Opponent)
- **Observed actions:** Water Energy attached to active Chien-Pao ex (03:06.200). Second Bench Rattata evolves into Team Rocket's Raticate ex (03:08.800). Opponent plays Team Rocket Grunt (03:14.600), flipping 2 heads and 1 tails to discard energy. Opponent benches Corphish (03:22.800). Chien-Pao ex uses Diving Icicles (03:26.400), targeting Bench Dratini for 130 damage, knocking it out (03:30.000). Opponent gains 1 point (03:33.400).
- **State delta:** Bench Dratini discarded. Score: Player 2, Opponent 2. Chien-Pao ex has 0 Energy.
- **Evidence anchors:** 03:06.200 (attachment), 03:08.800 (evolution), 03:14.600 (Grunt), 03:30.000 (Bench KO), 03:33.400 (point award).

### Turn 14 (Player)
- **Observed actions:** Bench Dratini evolves into Dragonair (03:40.800). Metal Energy attached to Haxorus (03:45.200). Player activates Rainbow Cave (03:47.400). Turn passed without attacking.
- **State delta:** Bench Dratini -> Dragonair. Haxorus has 2 Fighting, 1 Metal Energy.
- **Evidence anchors:** 03:40.800 (evolution), 03:45.200 (attachment).

### Turn 15 (Opponent)
- **Observed actions:** Water Energy attached to Chien-Pao ex (03:54.400). Bench Corphish evolves into Crawdaunt (03:55.400). Opponent plays Team Rocket Grunt (03:59.600), flipping tails on first flip (fails). Chien-Pao ex attacks with Icicle (04:08.000), dealing 20 damage to Haxorus (04:09.400).
- **State delta:** Haxorus HP: 130/150. Chien-Pao ex has 1 Water Energy.
- **Evidence anchors:** 03:54.400 (attachment), 03:55.400 (evolution), 03:59.600 (Grunt), 04:09.400 (damage).

### Turn 16 (Player)
- **Observed actions:** Dragonair activates Ability Dragon's Blessing (04:17.000), attaching a Metal Energy from the discard pile to active Haxorus (04:19.000). Haxorus attacks with Frenzied Blade (04:23.000), dealing 150 damage to active Chien-Pao ex (04:24.400). Chien-Pao ex (having only 30 HP remaining) is knocked out. As an ex Pokémon, Chien-Pao ex yields 2 points. Player reaches 3 points (04:29.000), triggering the match-winning point sequence. Screen transitions to white at 04:32.600.
- **State delta:** Chien-Pao ex knocked out. Player points: 3 (win).
- **Evidence anchors:** 04:19.000 (Ability acceleration), 04:24.400 (150 damage/KO), 04:29.000 (Point award and win condition).

---

## Important Mechanics and Tactical Observations
- **Iris Supporter:** Iris provided +1 additional point when Haxorus knocked out Crawdaunt on Turn 12, advancing the player score from 0 to 2 points off a single 1-point Pokémon.
- **Dragonair Acceleration:** Dragonair's Dragon's Blessing ability successfully accelerated an Energy card from the discard pile on Turn 16, allowing Haxorus to execute the winning attack.
- **Outcome:** Player Win (3 points reached).

## Explicit Uncertainties
- `U1`: Exact match mode (PvP vs Solo AI) cannot be definitively confirmed without an explicit game mode screen banner, though opponent name is generic "Opponent".

Status: Partial pending independent Sol verification.
```

### UNCERTAINTIES.json
```json
[
  {
    "start_timestamp": "00:00.000",
    "end_timestamp": "00:01.000",
    "claim_or_question": "Is the match mode Solo (vs AI) or PvP?",
    "why_uncertain": "The opponent's nameplate displays the generic label 'Opponent' with standard sleeves and avatar, but the match setup screen is not shown to verify if it is an AI battle or a casual/ranked human match.",
    "consequence_if_wrong": "Metadata classification only; does not affect board state, game rules, scoring, or battle outcome.",
    "recommended_sol_check": "Confirm whether the 'Opponent' label corresponds to standard AI battle formatting in this build.",
    "id": "U1"
  }
]
```
<!-- END_BATTLE_PACKET -->