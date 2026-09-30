Decision this informs: whether the prepared upstream patch (`0001-Limit-Heavy-Helmet-Harden-Hide-and-Blocking-Shell-to.patch`, on main at e2ea0c4) passes upstream's format and lint checks before anyone opens it. The cloud's check, Sept 29, at the laptop's request (the laptop has no clippy). Report only: the patch was not edited, and nothing was pushed or opened anywhere.

# The upstream patch: fmt and clippy (cloud, Sept 29)

**Result: every check passes on the patched tree, as on the base. There are no warnings in the patch's lines.**

## Setup

- `git clone https://github.com/bcollazo/deckgym-core.git`, checked out at `ca4b67f41eaa514103833b8b6f6829a1f0deaa37` (upstream `main`, unchanged since Sept 28).
- `git am` of the patch from main e2ea0c4 (sha256 258d3fe8bd44cf8b276bc90db80bb1676ae47abec15bc5eac34c8cf8792f3da7).
  - It applied cleanly, as one commit (e5644bd in this clone, because the committer differs).
  - Diff: `src/hooks/core.rs`, `tests/rules.rs`, and the new `tests/rules/attack_damage_only_test.rs`; 3 files, +312 −7, as the README says.
- **The base** is a second clone at ca4b67f. Each tree has its own target folder.
- **Toolchain:** stable, rustc 1.94.1, clippy 0.1.94, rustfmt 1.8.0.

## The checks

| command | where it comes from | base (ca4b67f) | patched |
|---|---|---|---|
| `cargo fmt -- --check` | CI (`.github/workflows/ci.yml` line 28) | pass | pass |
| `cargo clippy --features tui -- -D warnings` | CONTRIBUTING.md line 71 | pass, 0 warnings | pass, 0 warnings |
| `cargo clippy --features "tui test-utils" -- -D warnings` | CI (`ci.yml` line 31) | pass, 0 warnings | pass, 0 warnings |

Each clippy log shows `Checking deckgym v0.1.0` followed by `Finished`, so the crate itself was checked, not only its dependencies. No clippy output was empty or skipped.

## One thing the two clippy commands don't cover

- Neither command passes `--all-targets`, so neither lints the integration tests under `tests/`. That includes the patch's new 283-line test file.
  - `cargo fmt -- --check` does cover `tests/`, and it passes.
- **For information only, not upstream's requirement:** `cargo clippy --all-targets --features "tui test-utils"` (no `-D warnings`) was run on both trees.
  - Both give the same one warning, in a file the patch doesn't touch: `tests/pokemon/victini_victory_star_test.rs:175`, "doc list item without indentation" (`clippy::doc_lazy_continuation`). It is already upstream.
  - **There are no warnings in `src/hooks/core.rs` or `tests/rules/attack_damage_only_test.rs`.**
  - Under `-D warnings` this pass would fail on the base as well, from that one existing line. That is why upstream's CI, which doesn't lint `tests/`, is green.

The clone and logs are in the cloud session's scratch space only. Nothing was added as a remote, pushed or opened.
