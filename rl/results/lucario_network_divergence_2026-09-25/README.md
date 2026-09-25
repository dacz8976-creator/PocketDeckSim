Decision this informs: which general changes to k3 to test next. Where the Lucario network beats k3, it does three card-agnostic things k3 doesn't. It keeps a cheap Basic in the Active Spot instead of retreating it into the Pokémon it is building. It values effects that cut the opponent's damage on their next turn. And it puts energy on its main attacker on the Bench rather than on the Active in front of it. Engine commit 6a9fa90 (replay, k3 probes and play-outs; its k3 is the table's k3), network through the verified add-on 0.7.2.

Seeds: new, not table deals. Network games 22,300,000,000 + i (i < 400, Lucario in seat i % 2). Play-outs 22,400,000,000 + i × 100,000 + decision × 100 + r. k3 probes 22,500,000,000 + i × 100,000 + decision × 10 + probe. The START_HERE seed table has the row.

# Where the Lucario network beats k3 (B2c), Sept 25

**Setup.**
- The run 5 stage 1 Lucario network (`ckpt_1800k_avg_lucario.npz`, SHA-256 dabd7258…49e8) piloted Lucario through the add-on 0.7.2 wheel against k3 piloting Weezing: 400 games, every move recorded (`play_network_games.py`).
- The add-on library (0fee43ce…9101) and both deck files were checked against the checkpoint's `identity.json`. The weights file isn't listed in `project_manifest.json`, so its hash is given here.
- **The network scored 72.0%** (288 of 400; 73.5% in seat 0, 70.5% in seat 1). For comparison, k3 piloting Lucario v Weezing scores 50.4% on the table deals, and Limitless has 56.6%. Those are different deals, so this is a rough comparison, not a paired one.

**Method** (`engine/examples/net_divergence.rs`):
- Each game is replayed in this engine from its seed and recorded moves. All 400 replay in sync: every move is offered, the network's move sits where the add-on showed it, and the final score and turn match.
- At each of the network's 6,368 decisions, k3 is asked for its move from the same view of the game. It gave the same move under all 3 probe seeds at 97% of decisions.
- The network made k3's move at 48% of decisions. Another 10% differ only in move order within a turn. The remaining 42% (2,656 positions) are real differences.
- At each of those 2,656 positions, both moves were played out 8 times, with k3 piloting both decks afterwards and each pair sharing a chance seed.
- The difference is Lucario's score after the network's move minus after k3's move. It measures whether k3 itself would do better making the network's move there.

**Overall:** across the 2,656 positions, the network's move is worth **+3.0 points (± 1.0)** to Lucario.

## Grouped by mechanism

Groups are pairs of move kinds (`analyze.py`). The ones whose 95% range excludes zero:

| network | k3 | positions | network − k3, points (95%) |
|---|---|---:|---:|
| attack | retreat | 140 | +15.4 (+8.4, +22.4) |
| energy to a Benched Pokémon | energy to the Active | 68 | +13.1 (+3.1, +23.0) |
| energy to a Benched Pokémon | place a Basic | 66 | +13.1 (+2.2, +23.9) |
| attack | play a Supporter | 97 | +5.7 (+0.9, +10.4) |

About 28 groups were tested, so one or two of the smaller ones could clear zero by chance. The first three are well clear. Looking inside them:

**1. Keep the cheap Basic in front; don't retreat into the Pokémon you're building.**
- 97 of the 140 attack-vs-retreat positions are Bonsly in the Active Spot: 30 HP, free retreat, worth 1 point.
- k3 retreats it, mostly to Riolu (65), which is the Mega Lucario base, or to Mega Lucario ex (22). The network attacks with Bonsly and lets it take the hit. These are early turns (own turns 1–3) against a 140–150 HP opponent.
- By retreat target: when k3 retreats to Riolu, the network's move is worth **+23.5 (± 10.0)**. When k3 retreats to an already-evolved Mega Lucario ex, the difference is +3.5 (± 10.1), not clear.
- Card-agnostic reading: k3 spares the cheap Basic a knockout (no point given up this turn). But its search ends with its own turn, so it doesn't see that the Pokémon it brings up, the unevolved base of its main attacker, is what the opponent hits next.

**2. Effects that cut the opponent's next attack are invisible to k3.**
- Bonsly's Teary Attack does 10 damage, and the Defending Pokémon's attacks do 30 less during the opponent's next turn.
- Wherever the network used it and k3 did something else, the network's move is worth **+10.4 (± 4.8)** over 203 positions. The network used it 304 times at its decisions; k3 would have used it 134 times at the same positions.
- Card-agnostic reading: k3's clock divides HP by the opponent's best damage and ignores damage reduction, and k3 doesn't search the opponent's turn. The brew pages flag the same blind spot for Jasmine, Metal Core Barrier, Steel Wing and Rocky Helmet.

**3. Power up the main attacker on the Bench, not the Active in front of it.**
- Where the network put energy on a Benched Pokémon and k3 put it elsewhere, the network's move is worth **+6.7 (± 3.7)** over 317 positions.
- Where the network put it on the Active, the difference is +0.9 (± 1.6).
- The clear cases: the network powers Riolu or Mega Lucario ex on the Bench, while k3 powers Hitmonlee in the Active Spot or benches another Basic.
- Card-agnostic reading: k3's value function rewards the Active being ready to attack now, and its horizon doesn't reach the turn where the Active is knocked out and the Benched attacker has to take over.

All three are one habit seen from different sides. The network plays a sacrificial front Pokémon while building the real attacker behind it. k3's one-turn horizon and clock reward the opposite: don't give up a point now, and make the Active ready now.

**Where k3's move was better:**
- Choosing the new Active after a knockout (promote vs promote): −4.0 (± 7.5), 75 positions.
- Attacking before playing an Item: −3.8 (± 5.4).
- Attacking before playing a Tool: −2.4 (± 3.6).
- None of these is clearly different from zero.

## Caveats

- Each position has only 8 paired play-outs, and positions from one game aren't independent, so the ranges are a little too narrow.
- The play-outs continue with k3, so this shows what k3 would gain by making the network's move. It doesn't measure how good the network's whole plan is.
- The group totals don't add up to the network's 21-point edge. Moves interact, and the network's own continuation isn't what was played out.
- Only Lucario v Weezing was examined. The three habits should be tested as k3 changes on the whole table before anything is concluded about other decks.

## Files

- `play_network_games.py` and `games.jsonl.gz`: the 400 recorded games.
- `decisions.jsonl`: every network decision, with both moves, their kinds, the board around the decision, the k3 probes, and at differing positions the 8 + 8 play-out results.
- `analyze.py`: the grouping above. `net_divergence.txt`/`.log` and `timing.txt`: the run's summary and timing (4,130 s on 2 threads).
