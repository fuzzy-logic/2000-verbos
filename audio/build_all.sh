#!/usr/bin/env bash
# Generate every audio pack, then rebuild the site so packs.json matches.
#
# Clips are cached by content hash, so re-running only synthesises what
# actually changed - a topic whose sentences did not move costs nothing.
#
# Concurrency 10 suits a proxied cloud container (~180 clips/min). Drop it
# to 6 on a home connection, where the service rather than the latency is
# the limit.
set -uo pipefail
cd "$(dirname "$0")/.."

CONC="${CONC:-10}"
fail=0

.venv/bin/python3 audio/make_track.py --all --concurrency "$CONC" || fail=$((fail + 1))

# The conjugation pack is keyed by verb|slot and does not depend on topics,
# so it is only rebuilt when conjugations.tsv changes. Uncomment to force it.
# .venv/bin/python3 audio/make_conj_track.py --concurrency "$CONC" || fail=$((fail + 1))

python3 build.py || fail=$((fail + 1))
echo "=== done, $fail failure(s) ==="
exit $((fail > 0))
