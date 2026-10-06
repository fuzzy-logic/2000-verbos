#!/usr/bin/env bash
# Generate every 100-verb audio pack. Clips are cached by content hash, so
# re-running only synthesises what actually changed.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0
for start in $(seq 1 100 2000); do
  end=$((start + 99))
  printf '=== %04d-%04d ===\n' "$start" "$end"
  if ! .venv/bin/python3 audio/make_track.py --start "$start" --end "$end"; then
    echo "FAILED: $start-$end"
    fail=$((fail + 1))
  fi
done
echo "=== done, $fail failed chunk(s) ==="
python3 build.py
