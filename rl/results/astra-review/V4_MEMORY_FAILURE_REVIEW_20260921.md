# Run 4 memory failure review
September 21, 2026. Audit only. No training, resume, shutdown, source edit, package installation, settings change or identity override was performed. A separate short-lived process measured checkpoint-cache growth without playing games.

## Verdict
Do not restart the unchanged eight-worker configuration. Prefer a narrowly scoped, reviewed fix that bounds both checkpoint caches, followed by an explicitly recorded continuation from the committed 3M save. Fewer workers is an available fallback. No unseen patch is approved here.

## Crash and recovery
The log confirms OSError errno 12, Cannot allocate memory, at evaluation _net -> load_net -> np.load. It failed during the initial random-opponent evaluation of ckpt_3500k, before that checkpoint's k3 evaluation. The kernel recorded a Windows-mounted-file read allocation failure at 06:59:35, with roughly 6.59 GiB anonymous memory, 142 MiB free physical memory and 1.60 GiB free swap. This is allocation failure under memory pressure, not proof that an OOM killer terminated the trainer or that one cache caused all pressure.

No trainer, launcher or multiprocessing workers remained when checked. WSL itself was still running; quiet fans are not evidence of process termination.

The committed state is RUNNING at 3M. STATUS.txt displays INTERRUPTED; the exception handler writes that display without replacing committed state (train_v4.py:765-771). All five referenced resume files load completely, contain finite arrays, and exactly match their ckpt_3000k files. All code, add-on, seven decks and runtime identities match. Both logs match committed byte lengths: 130,000 valid evaluation rows and 3,000 sampled self-play rows, with six complete checkpoint evaluations through 3M.

All five uncommitted ckpt_3500k files also load cleanly. Their weights therefore survived, but they are not a complete committed recovery state or evaluated result. Normal recovery should still use 3M and preserve the 3.5M files under interrupted_attempt_<epoch>, as existing recover() does (626-642). Do not silently promote them to committed status. Preserve new-epoch seed allocation (806-812).

## Cache defect and actual measurement
Actors retain past[(checkpoint, deck)] without eviction (314-316), alongside five current networks. Evaluation workers retain every _E["nets"][path] indefinitely (395-402). Eight actors and eight persistent evaluators are created (824, 958-962).

Every MLP allocates weights plus two optimizer-moment arrays, and load_net restores all three even for inference (model.py:14-21; train_v4.py:164-173). Each model has 674,305 parameters: about 2.57 MiB for weights, 7.717 MiB including optimizer arrays. At the failed checkpoint, the ceiling is 35 past plus five current models per actor, and 40 per evaluator: about 4.82 GiB in those arrays alone. Replay buffers add about 808 MiB, before environments, queues, temporaries and Python. These are capacity calculations, not measured historical occupancies.

Loading the real evaluation cache in one separate process added 87.9 MiB at 10 models, 170.7 MiB at 20, 294.8 MiB at 35 and 336.2 MiB at 40. Its exit released that memory. This confirms cache growth and its scale, supporting it as a major contributor without proving sole causation.

## Options and acceptance conditions
Preferred repair: cap both in-memory caches, evicting/reloading models while leaving every historical checkpoint eligible as an opponent. Truncating the opponent pool changes training. Omitting optimizer arrays for inference is another possible saving, but skipping their load alone does not prevent MLP from allocating them; preserve full optimizer state for learners and resumes.

No-code fallback: --workers is explicitly allowed to change on resume (738, 746-747, 799-803). Two workers substantially reduce replicated memory, with an unmeasured speed cost and different asynchronous training order. Cache growth remains unbounded. The launcher hardcodes eight workers for later audit and transfer, so its training flag does not cap the whole chain. Neither option is a completion guarantee without measurement.

Before signing off a patch, require fixed-case score/action/outcome equality across repeated eviction/reload, unchanged opponent sampling and RNG use, measured memory after loading beyond cache capacity, and interrupted-event recovery in a separate test folder. An uninterrupted training trajectory is not promised by existing resume behavior.

The identity guard compares hashes; there is no automatic Astra-approval mechanism. Preserve the original identity and source and explicitly record any reviewed amendment. Do not disable the guard or overwrite history to make modified code appear unchanged. Keep engine/gameplay fixes separate from this memory repair.

Companion evidence: V4_MEMORY_FAILURE_20260921_evidence.json contains archive hashes, input-identity checks, log counts, current process/memory checks and measured cache growth.
