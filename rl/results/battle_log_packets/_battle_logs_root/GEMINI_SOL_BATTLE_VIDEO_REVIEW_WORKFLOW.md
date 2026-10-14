# Gemini + Sol battle-video review workflow

## Purpose

This is the cost-controlled companion to `START_HERE_VIDEO_REVIEW.md`. The existing file remains the authority for claiming work, source preservation, completion, logging, and moving a video into `Reviewed`.

Use this workflow to reduce expensive repeated video inspection while preserving the requirement for a complete, evidence-backed battle review.

**Future Pause Games supplement, October 2, 2026:** When a newly requested game is to be saved in Pause Games, [PAUSE_GAMES_REVIEW_PROTOCOL.md](PAUSE_GAMES_REVIEW_PROTOCOL.md) also applies to any review route used here. Supply it and its assignment template to every worker and verifier. Draw-based, native-resolution hand captures replace fixed-grid samples as the evidence for owner turn starts. The exact deck snapshot and one-row-per-turn JSON accompany the current prose review. Do not apply this new requirement retroactively. The current coordinator's model roles in START_HERE_VIDEO_REVIEW.md remain authoritative.

The intended division of work is:

- **Local preprocessing:** create reusable timestamped visual evidence once.
- **Gemini:** produce the complete first-pass battle account and packet.
- **Sol:** independently verify the high-risk evidence and accept or reject the packet.
- **Astra:** not part of the routine workflow. Use only for a consequential ambiguity that remains unresolved after dense source inspection.

This process does not authorize restarting the paused queue. Run one measured pilot after owner approval, evaluate it, and agree on a per-video or batch limit before scaling.

## Why preprocessing is necessary

Gemini's default static video processing samples video at 1 frame per second. Google warns that this can miss rapid actions and quick changes. The Gemini API supports agentic video processing, clipping intervals, custom frame-rate sampling, and higher media resolution, but the ordinary upload experience may not expose those controls. See [Google's video-understanding documentation](https://ai.google.dev/gemini-api/docs/video-understanding).

One frame per second is not enough for this project. Important events may last less than a second:

- a selected card returning to the hand;
- the direction of a Pokémon Communication exchange;
- a short no-target system prompt;
- a bench target appearing during an attack;
- a coin result and its effect;
- damage, knockout, and point-award transitions;
- concession confirmation.

The solution is not to claim that every source frame was reviewed. The solution is to create a reproducible evidence set with enough temporal detail to account for meaningful game-state changes.

## Recommended technical foundation

No single open-source project provides a complete, trustworthy Pokémon TCG Pocket transaction transcript. Use a small pipeline built on the following components.

### Primary: FFmpeg and ffprobe

[FFmpeg](https://ffmpeg.org/) is the best base for this workflow. Its documented filters can sample at fixed rates, detect visual changes, crop important regions, overlay timestamps, and produce clips or image sequences. `ffprobe` can supply video metadata and inspect selected intervals.

Use FFmpeg for:

- exact-duration and stream metadata;
- fixed-rate source sampling;
- timestamp overlays tied to the original source time;
- short dense clips around uncertain events;
- full-resolution frame extraction for small card text;
- optional evidence reels for upload to a chat interface.

### Secondary: PySceneDetect

[PySceneDetect](https://github.com/Breakthrough/PySceneDetect) is actively maintained, open source under BSD-3-Clause, supports OpenCV and PyAV backends, and provides content, adaptive, hash, histogram, and fade detectors. It can export timestamps and frames for detected transitions.

Use it only to propose additional inspection points. Do not let scene detection define review coverage. Many card-game actions alter only a small part of an otherwise stable screen and may not register as a scene boundary.

### Not recommended as the main extractor

- [Katna](https://github.com/keplerlab/katna) selects representative or visually strong keyframes. That is useful for summaries, but the clustering and quality-selection approach can discard transient prompts and intermediate states that this review must retain.
- [TransNetV2](https://github.com/soCzech/TransNetV2) is designed for shot-boundary detection. It is more complex than needed and has the same basic limitation for a mostly stable game interface.
- Pure scene-change extraction of any kind is insufficient by itself.

## Two supported preprocessing paths

### Path A: Gemini API with controlled video sampling

This is the cleanest option if the Gemini API is available.

1. Upload the original video once.
2. Use static processing with a custom sampling rate of **5 FPS** for the measured pilot.
3. Use high media resolution when small card text or hand contents must be read.
4. If context or cost becomes excessive, use 1 FPS for orientation and 5 to 10 FPS only for clipped action windows.
5. Record the actual token usage returned by the API.

Five source frames per second provide one frame every 200 milliseconds. That should expose most short UI transactions, but it is a pilot setting, not a guarantee. Increase a specific window to 10 FPS when the state still changes between samples.

Google documents that custom FPS increases token use proportionally. The pilot must measure the real cost before this becomes the default.

### Path B: Local evidence package for a chat upload

Use this when the chat interface always samples uploaded video at about 1 FPS and does not expose custom sampling.

Create two layers:

1. **Overview layer:** one timestamped frame per source second for orientation, turn boundaries, and coarse coverage.
2. **Dense evidence layer:** five timestamped frames per source second for meaningful action windows.

For a chat interface, the dense frames may be converted into an **evidence reel**:

- sample the source at 5 FPS;
- burn the original source timestamp into every sampled frame;
- hold each sampled frame for one second in the evidence reel;
- split the source into manageable blocks, such as 60 source seconds per reel;
- retain the manifest that maps every evidence frame to its original timestamp.

The resulting reel is slower than the source. A chat system sampling the reel at 1 FPS can see approximately five original source frames per second. The burned-in timestamp prevents confusion between reel time and source time.

Do not replace the original video with the evidence reel. The reel is a derivative review aid and must remain bound to the original filename and SHA-256.

## Required preprocessor output

Create one evidence folder per source video. It should contain:

- `SOURCE.json`
  - exact filename;
  - SHA-256;
  - byte count;
  - duration;
  - frame rate and declared frame count when available;
  - resolution;
  - current path;
  - derivative relationships.
- `EVIDENCE_MANIFEST.csv` or `.json`
  - evidence filename;
  - original source timestamp;
  - sampling method;
  - reason for retention;
  - dense-window identifier, if applicable.
- `overview/`
  - one frame per source second, with the original timestamp visible.
- `dense/`
  - 5 FPS windows for action sequences;
  - 10 FPS only when 5 FPS leaves an ordering ambiguity.
- `full_resolution/`
  - selected original-resolution frames for card text, hand contents, score, HP, Energy, and system prompts.
- optional `evidence_reels/`
  - slowed, timestamped derivatives for chat upload.
- `PREPROCESS_LOG.md`
  - tool versions;
  - settings;
  - generated files;
  - warnings or decode errors.

Retain one shared evidence package. Gemini and Sol should reuse it rather than decoding and extracting the same video independently.

## Mandatory dense-review events

The evidence package or Gemini's controlled sampling must provide adequate coverage of every occurrence of the following:

- setup, coin flip, starting Active, Bench, and initial visible hand;
- turn transition and player identity;
- draw and generated Energy when visible;
- evolution, attachment, Tool, Stadium, Supporter, and Item use;
- every deck search, hand-to-deck exchange, discard, return-to-hand, and failed search;
- each coin flip and the resulting effect;
- switching, retreating, promotion, and Bench changes;
- attack selection, target, damage, weakness, resistance, and triggered effects;
- healing, status conditions, knockout, and point changes;
- Auto indicator or control-mode changes;
- concession menu, confirmation, and result screen;
- any system prompt visible for less than two seconds;
- any transition Gemini labels uncertain.

## Gemini first-pass contract

Gemini receives:

- the original video or controlled-FPS API reference;
- the evidence package or evidence reels;
- `START_HERE_VIDEO_REVIEW.md`;
- this workflow;
- the required packet template.

Gemini must produce a complete candidate packet, not a conversational summary.

For every turn, Gemini must maintain a state ledger:

| State | Required accounting |
|---|---|
| Active | Pokémon, HP, Energy, Tool, conditions |
| Bench | Pokémon, HP, Energy, Tool, changes |
| Hand | visible identities, counts, cards moving in or out |
| Deck/discard | only publicly established transactions |
| Energy Zone | type and whether generated, attached, or left unused |
| Score | before and after every knockout or award |
| Prompts | exact or carefully paraphrased visible message |
| Mode | Auto state and changes; Solo/PvP/AI only when immediately explicit, otherwise unknown without escalation |

Gemini must distinguish:

- selected versus successfully played;
- one physical card replayed versus two copies;
- card sent into the deck versus card retrieved from the deck;
- observation versus inference;
- visible deck facts versus unknown hidden contents;
- a visible future line versus a forced or unavoidable outcome.

Gemini must label unresolved evidence and give exact timestamps. It must not silently interpolate a plausible event.

The candidate remains `partial` until Sol independently accepts it.

## Sol acceptance review

Sol does not automatically repeat the whole video review. Sol receives the candidate packet and the same preserved evidence.

Sol must independently verify:

1. Source identity and full timeline coverage.
2. Setup, starting board, and Auto state. Mode/AI metadata is checked only when immediately explicit; uncertainty there alone does not justify extra review or Astra escalation.
3. Every knockout and score transition.
4. Every deck search, Pokémon Communication, return-to-hand effect, and failed search.
5. Every consequential damage, healing, weakness, triggered effect, and point-rule calculation.
6. At least one ordinary, non-decisive turn selected independently rather than chosen by Gemini.
7. The complete terminal sequence and stated outcome.
8. Every interval Gemini marked uncertain.

Sol records a timestamped PASS or FAIL for each checked claim. If a discrepancy suggests a broader state-ledger failure, Sol expands the review to the affected turn or rejects the packet for a new first pass. Sol must not repair a structurally unreliable draft by silently rewriting it.

## Completion and registration

The lead may mark the battle complete only when:

- the candidate covers setup through terminal outcome;
- all turns and meaningful actions are represented;
- HP, Energy, Bench, hand transactions, and score transitions reconcile;
- all Sol acceptance checks pass;
- unresolved facts are explicitly bounded rather than guessed;
- `SOURCE.json`, `REVIEW.md`, `COVERAGE.md`, evidence references, and reviewer/session attribution are complete.

Then follow `START_HERE_VIDEO_REVIEW.md` exactly:

1. Save the final packet in the proper Pocket Deck Lab review location.
2. Append the completion event through `Review_Log/review_log.py`.
3. Update the existing index and media-location records without overwriting newer work.
4. Move the original video to `Reviewed` only after registration.
5. Verify that the moved file retains the original filename, size, and SHA-256.

Gemini and verifying Sol remain separately attributed. The final packet must not imply that Sol performed a second full review when the work was bounded verification.

## Measured pilot and acceptance gate

Use `20260921_145205000_iOS.MP4` as the first benchmark because its corrected sequence already exposes known failure modes:

- a bench knockout that a 1 FPS pass missed;
- generated Energy attached to the Bench rather than the Active;
- the same Lucky Ice Pop returning to hand and being replayed;
- two Pokémon Communication exchanges with opposite directions;
- short no-target prompts;
- overlapping Rocky Helmet and Destiny Burst damage;
- a three-point Mega Evolution EX rule;
- a nonlethal Electro Ball versus a conditional Thunderclaw lethal line;
- a short concession sequence.

Record for the pilot:

- preprocessing time;
- number and size of derivative files;
- Gemini input/output tokens and cost when available;
- Sol input/output tokens and cost when available;
- total elapsed review time;
- number of major and minor corrections;
- which events were found only because of dense evidence.

The workflow passes the pilot only if:

- Sol finds no omitted turn, knockout, point change, search direction, terminal event, or consequential rule interaction;
- all source and packet fields are correct;
- any remaining corrections are minor wording or formatting issues;
- cost and time are materially lower than a Sol full-pass plus full rereview.

If Sol finds a missed meaningful event or a broken state transition, do not scale the queue. Adjust sampling, evidence packaging, or the Gemini contract and repeat the bounded pilot.

## Cost controls

- One video at a time until the pilot passes.
- One preserved preprocessing pass per source.
- One Gemini candidate response whenever possible.
- One bounded Sol acceptance review.
- No routine Astra image or video review.
- No claim of “all frames reviewed” unless every decoded frame was actually inspected.
- Pause and save partial status when the agreed per-video limit is reached.

## Current recommendation

Start with FFmpeg/ffprobe as the reproducible extraction layer and PySceneDetect only as a supplemental candidate detector. If Gemini API access is practical, test direct 5 FPS static processing at high media resolution before building a larger local system. It may provide the required temporal detail with less engineering work.

Do not use Katna, TransNetV2, or any representative-keyframe tool as the sole source of review coverage.

The guarded implementation for the measured API pilot is documented in `Gemini_API_Pilot/README.md`. Its default mode is local estimation only. A billable generation request requires separate explicit execution and confirmation flags.
