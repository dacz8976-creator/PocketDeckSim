# Video review trial, Oct 25-26, 2026 (Claude v Codex)

Dustin asked whether Claude could take over video reviews from Codex on the API credits. Three of his ranked games were reviewed:
- g1 = ScreenRecording_10-24-2026 15-29-43 (12 turns);
- g2 = 12-51-31 (6 turns);
- g3 = 13-24-53 (15 turns).

Each was reviewed by confined `claude -p` jobs, checked by Opus against the frames, and compared with Codex's accepted review. Disagreements were settled from the frames.

The summary is in the coordinator's memory (pocketdecksim-video-review-trial-oct25):
- Sonnet reading 54-s pieces is the best first pass.
- The Opus check is the main cost, $1.4-4.5 a game.
- On his Max plan, one game is about 2-3% of the weekly limit.
- The trial spent about $37 of API credit.

Contents:
- `prep.sh` cuts the frames with ffmpeg.
- `run_*.sh` are the job runners.
- `briefs/` holds the job briefs.
- `results/` holds each job's text outputs and `costs.jsonl`.

The frames (about 600 MB) were deleted after this was saved, per Dustin's storage rule. The videos are on Google Drive, so `prep.sh` can make them again.
