#!/usr/bin/env bash
# Builds the strength harness against an engine tree, at nice 19, in a scratch directory (nothing is written into the repo or its engine/).
#   rl/strength/build.sh [ENGINE_REF_OR_DIR] [OUT_BINARY]
# ENGINE_REF_OR_DIR: a git ref of this repository (default origin/main; the engine/ tree of that ref is archived), or a path to an engine
#   directory (for example the experimental pilot's branch checkout's engine/). The harness knows exactly the pilot codes that engine's
#   parse_player_code knows, so the experimental pilot is built by pointing this at its branch.
# OUT_BINARY: where to put the program, a FILE path (default ./strength next to this script's scratch build); a directory is refused.
# Prints the engine tree hash (or directory), the program's sha256 and the harness source hash: put them in the pre-registration.
# Also writes OUT_BINARY.build.json, the build record that `slow_report.py --program` requires: the engine ref and the tree id of what was ARCHIVED (git's tree id computed from the
# files that were actually extracted and compiled, not read back from the ref), the harness source hash, the program sha256, the toolchain and the build paths. The program's sha256
# depends on all of them, so a rebuild that must come out byte-identical (a resume after a container restart) repeats the "rebuild_command" in that record. The record is written by
# this script itself and is not signed: it says what the builder did, it does not prove it (the replayed self-checks do).
# The build runs with the variables that change what cargo builds REMOVED from its environment (RUSTFLAGS, CARGO_PROFILE_*, RUSTC_WRAPPER, ...; the record lists the ones that were
# set), so the printed rebuild command does not depend on them; cargo's config files that would still apply are listed in the record with their sha256. What it does NOT pin: the
# toolchain beyond the rustup default (`rustc -vV` is recorded), C toolchain variables such as CC and CFLAGS, and the system libraries: the same bytes need the same machine setup.
# One build at a time per STRENGTH_BUILD_DIR and per target folder (locks, held by this script only); a failed cargo build stops the script with no program and no record.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=${STRENGTH_REPO:-$(cd "$HERE/../.." && pwd)}   # the repository whose git objects hold the engine ref
REF=${1:-origin/main}
OUT=${2:-$HOME/strength_build/strength}
W=${STRENGTH_BUILD_DIR:-$HOME/strength_build}
TARGET=${STRENGTH_TARGET_DIR:-$W/target}
if [ -d "$OUT" ]; then
    echo "build.sh: OUT_BINARY $OUT is a directory; give the path of the program file to write (for example $OUT/strength)" >&2
    exit 2
fi
# the record and the rebuild command carry absolute paths (the script changes directory below): the folder part is resolved, the file name is kept as given (a symlink named here is
# written through to its target by cp, but the record belongs beside the NAME, which is where slow_report.py --program looks for it)
OUT="$(readlink -m "$(dirname "$OUT")")/$(basename "$OUT")"
W=$(readlink -m "$W"); TARGET=$(readlink -m "$TARGET")
if [ -d "$REF" ]; then REF=$(cd "$REF" && pwd); fi
# the git of this script reads the repository it is told about, not one named by an exported GIT_DIR (a git hook, rebase --exec)
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_COMMON_DIR GIT_NAMESPACE GIT_PREFIX
# never build over the slow report's pinned (frozen) binary: a rebuild is a different file even from the same source, and the original cannot be recovered
if [ -z "${STRENGTH_SKIP_PIN_GUARD:-}" ]; then
    if [ ! -f "$HERE/slow_report_pin.json" ]; then
        echo "build.sh: cannot find slow_report_pin.json beside this script, so it cannot tell whether OUT is the slow report's pinned program; refusing (set STRENGTH_SKIP_PIN_GUARD=1 to build anyway)" >&2
        exit 2
    fi
    PIN_PROGRAM=$(python3 -c 'import json, sys
p = json.load(open(sys.argv[1], encoding="utf-8"))["program"]
if not (isinstance(p, str) and p):
    sys.exit(1)
print(p)' "$HERE/slow_report_pin.json" 2>/dev/null) || {
        echo "build.sh: cannot read the \"program\" entry of $HERE/slow_report_pin.json, so it cannot tell whether OUT is the pinned program; refusing (set STRENGTH_SKIP_PIN_GUARD=1 to build anyway)" >&2
        exit 2
    }
    if [ "$(readlink -m "$OUT")" = "$(readlink -m "$PIN_PROGRAM")" ] || [ "$OUT" -ef "$PIN_PROGRAM" ]; then  # -m: no component has to exist; -ef: a hard link too
        echo "build.sh: refusing to overwrite the slow report's pinned program $PIN_PROGRAM (slow_report_pin.json); build to another path" >&2
        exit 2
    fi
fi
if [ -L "$OUT" ] && [ ! -e "$OUT" ]; then  # cp will not write through a link to nothing: say so now, not after the compile
    echo "build.sh: OUT_BINARY $OUT is a symbolic link to nothing (it points at $(readlink "$OUT")); remove it or give a path that can be written, before a build is spent on it" >&2
    exit 2
fi
mkdir -p "$W" "$(dirname "$TARGET")"
if command -v flock >/dev/null 2>&1; then
    # one build at a time per build folder AND per target folder (two build folders sharing a target folder would swap programs); the locks end with this script (cargo gets them closed)
    exec 9>"$W/build.lock"
    flock -n 9 || { echo "build.sh: another build is using $W (STRENGTH_BUILD_DIR); wait for it or use another folder (a second build would delete the first one's source while it compiles)" >&2; exit 2; }
    exec 8>"$TARGET.lock"
    flock -n 8 || { echo "build.sh: another build is using the target folder $TARGET (STRENGTH_TARGET_DIR); wait for it or use another target folder (two builds would swap programs)" >&2; exit 2; }
else
    echo "build.sh: warning: flock is not installed, so two builds in $W at the same time are not prevented" >&2
fi
rm -rf "$W/tree" && mkdir -p "$W/tree/rl/strength" "$(dirname "$OUT")"
ENGINE_REF_RESOLVED=""
if [ -d "$REF" ]; then
    cp -r "$REF" "$W/tree/engine"; ENGINE_ID="dir:$REF"
else
    git -C "$REPO" -c core.autocrlf=false -c core.eol=lf archive "$REF" engine | tar -x -C "$W/tree"   # no end-of-line conversion from this machine's git config
    ENGINE_REF_RESOLVED=$(git -C "$REPO" rev-parse "$REF^{commit}")
    ENGINE_ID="$REF engine tree $(git -C "$REPO" rev-parse "$REF:engine")"
fi
# git's tree id of the files that were just extracted (what is about to be compiled), in a scratch repository: .gitignore patterns are overridden (-f) and nothing is converted
SCRATCH_GIT="$W/engine_tree.git"; rm -rf "$SCRATCH_GIT"
git --git-dir="$SCRATCH_GIT" init -q
# attributes are neutralised: a .gitattributes in the engine, the machine's attributes file and this repository's own would otherwise change the object stored for a file (CRLF turned to
# LF by `text`, `$Id: ... $` collapsed by `ident`, a filter) and so the id: it must be the id of the bytes that are compiled. core.fileMode=true takes the executable bit from the file system
# (a build folder on a Windows drive under WSL reports every file as executable, and the id then differs from the ref's: the record says which kind of file system, build_fs).
mkdir -p "$SCRATCH_GIT/info"
printf '* -text -eol -ident -filter -working-tree-encoding\n' > "$SCRATCH_GIT/info/attributes"
ENGINE_TREE_ARCHIVED=$(git --git-dir="$SCRATCH_GIT" --work-tree="$W/tree/engine" -c core.autocrlf=false -c core.safecrlf=false -c core.fileMode=true -c core.attributesFile=/dev/null add -A -f >/dev/null && git --git-dir="$SCRATCH_GIT" write-tree)
find "$W/tree" -type f -exec touch {} +   # git archive gives every file the same mtime: touch so cargo rebuilds what changed
cp -r "$HERE/src" "$HERE/Cargo.toml" "$W/tree/rl/strength/"
# the engine's own lock file pins every dependency; the harness adds only itself
cp "$W/tree/engine/Cargo.lock" "$W/tree/rl/strength/Cargo.lock"
cd "$W/tree/rl/strength"
# what changes the compiled program is taken out of the environment (the names that were set go in the build record), so that the printed rebuild command repeats the build
BUILD_ENV_UNSET=$(env | cut -d= -f1 | grep -E '^(RUSTFLAGS|RUSTDOCFLAGS|RUSTC|RUSTC_[A-Z_]+|RUSTUP_TOOLCHAIN|CARGO_BUILD_[A-Z_]+|CARGO_ENCODED_RUSTFLAGS|CARGO_PROFILE_[A-Za-z0-9_]+|CARGO_TARGET_[A-Za-z0-9_]+|CARGO_INCREMENTAL|CARGO_UNSTABLE_[A-Za-z0-9_]+|CARGO_PATCH_[A-Za-z0-9_]+)$' | grep -vE '^(CARGO_TARGET_DIR|CARGO_BUILD_JOBS)$' | tr '\n' ' ' || true)
UNSET_ARGS=(); for n in $BUILD_ENV_UNSET; do UNSET_ARGS+=(-u "$n"); done
[ -z "$BUILD_ENV_UNSET" ] || echo "build.sh: removed from the build environment (they change what cargo builds): $BUILD_ENV_UNSET" >&2
rm -f "$TARGET/release/strength"   # a program left by an earlier build must never be taken for this one if this build fails
CARGO_LOG="$W/cargo.log"
if ! env ${UNSET_ARGS[@]+"${UNSET_ARGS[@]}"} CARGO_TARGET_DIR="$TARGET" CARGO_BUILD_JOBS=${STRENGTH_JOBS:-8} nice -n 19 cargo build --release --offline >"$CARGO_LOG" 2>&1 9>&- 8>&-; then
    grep -E "^(error|warning: unused)|-->|^\s+\|" "$CARGO_LOG" | head -60 || true
    echo "build.sh: cargo build failed (its whole output is in $CARGO_LOG); no program was copied and no build record was written" >&2
    exit 1
fi
grep -E "^(error|warning: unused)|-->|^\s+\|" "$CARGO_LOG" | head -60 || true
cp "$TARGET/release/strength" "$OUT"
PROGRAM_SHA=$(sha256sum "$OUT" | cut -d' ' -f1)
HARNESS_SHA=$(LC_ALL=C; cat "$W"/tree/rl/strength/src/*.rs "$W/tree/rl/strength/Cargo.toml" | sha256sum | cut -d' ' -f1)   # of the copies that were compiled, not of the checkout as it is now
BUILD_FS=$(stat -f -c %T "$W" 2>/dev/null || echo unknown)
echo "engine: $ENGINE_ID"
echo "engine tree as archived: $ENGINE_TREE_ARCHIVED"
echo "program: $OUT"
echo "program sha256: $PROGRAM_SHA"
echo "harness source sha256: $HARNESS_SHA"
# the build record beside the program (JSON written by python3 from the shell's values, so nothing needs escaping)
BR_OUT="$OUT" BR_REF="$REF" BR_ENGINE_ID="$ENGINE_ID" BR_REF_RESOLVED="$ENGINE_REF_RESOLVED" BR_TREE="$ENGINE_TREE_ARCHIVED" BR_PROGRAM_SHA="$PROGRAM_SHA" BR_HARNESS="$HARNESS_SHA" \
    BR_W="$W" BR_TARGET="$TARGET" BR_JOBS="${STRENGTH_JOBS:-8}" BR_CARGO_HOME="${CARGO_HOME:-}" BR_HOME="$HOME" BR_REPO="$REPO" BR_HERE="$HERE" BR_FS="$BUILD_FS" BR_UNSET="$BUILD_ENV_UNSET" \
    BR_RUSTC="$(env ${UNSET_ARGS[@]+"${UNSET_ARGS[@]}"} rustc -vV 2>&1 || true)" BR_CARGO="$(env ${UNSET_ARGS[@]+"${UNSET_ARGS[@]}"} cargo -V 2>&1 || true)" BR_UNAME="$(uname -srm 2>&1 || true)" BR_LIBC="$( (ldd --version 2>&1 || true) | head -1)" BR_HOST="$(hostname 2>/dev/null || true)" \
    python3 - <<'EOF'
import datetime, hashlib, json, os, shlex
e = os.environ
cargo_home = e['BR_CARGO_HOME'] or os.path.join(e['BR_HOME'], '.cargo')
env_part = [f'{k}={shlex.quote(v)}' for k, v in (('HOME', e['BR_HOME']), ('CARGO_HOME', cargo_home), ('STRENGTH_BUILD_DIR', e['BR_W']),
                                                   ('STRENGTH_TARGET_DIR', e['BR_TARGET']), ('STRENGTH_JOBS', e['BR_JOBS']), ('STRENGTH_REPO', e['BR_REPO']))]


def cargo_config_files():
    """The config files cargo reads for this build: .cargo/config(.toml) in the build folder and every folder above it, and in CARGO_HOME."""
    cands, d = [], os.path.join(e['BR_W'], 'tree', 'rl', 'strength')
    while True:
        cands += [os.path.join(d, '.cargo', 'config.toml'), os.path.join(d, '.cargo', 'config')]
        if os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    cands += [os.path.join(cargo_home, 'config.toml'), os.path.join(cargo_home, 'config')]
    out, seen = [], set()
    for p in cands:
        if os.path.isfile(p) and os.path.realpath(p) not in seen:
            seen.add(os.path.realpath(p))
            try:
                with open(p, 'rb') as f:
                    out.append(dict(path=p, sha256=hashlib.sha256(f.read()).hexdigest()))
            except OSError as err:  # a file cargo may not be able to read either: the record says so, the build record is still written
                out.append(dict(path=p, sha256=None, error=str(err)))
    return out


rec = dict(schema=1, program=e['BR_OUT'], program_sha256=e['BR_PROGRAM_SHA'], engine_arg=e['BR_REF'], engine=e['BR_ENGINE_ID'], engine_ref=e['BR_REF_RESOLVED'] or None,
           engine_tree_archived=e['BR_TREE'], harness_source_sha256=e['BR_HARNESS'], rustc=e['BR_RUSTC'], cargo=e['BR_CARGO'], machine=e['BR_UNAME'], libc=e['BR_LIBC'],
           host=e['BR_HOST'], home=e['BR_HOME'], cargo_home=e['BR_CARGO_HOME'] or None, build_dir=e['BR_W'], target_dir=e['BR_TARGET'], build_fs=e['BR_FS'], jobs=e['BR_JOBS'],
           build_env_unset=sorted(e['BR_UNSET'].split()), cargo_config_files=cargo_config_files(),
           built_at=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
           rebuild_command='env ' + ' '.join(env_part) + ' bash ' + shlex.quote(os.path.join(e['BR_HERE'], 'build.sh')) + ' ' + shlex.quote(e['BR_REF']) + ' ' + shlex.quote(e['BR_OUT']))
with open(e['BR_OUT'] + '.build.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(rec, f, indent=1)
    f.write('\n')
print('build record:', e['BR_OUT'] + '.build.json')
EOF
