"""Gate for data/classification.tsv. Run: python3 lib/check_classification.py

The round-trip check is the one that matters. A hand-added topic column was
once deleted by a generator that rewrote its file from a fixed column list,
taking 52 decisions with it, and every gate still passed - because they
checked that topics were *valid*, never that they were *the ones written*.

So this loads the corpus the way the app does and compares what came back,
sentence by sentence, against the file. If anything is eating the data, this
fails loudly instead of quietly shipping the wrong deck.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from corpus import load  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'data', 'classification.tsv')


def scenes():
    p = os.path.join(ROOT, 'data', 'topics', '_index.tsv')
    with open(p, encoding='utf-8') as fh:
        return {r['slug'] for r in csv.DictReader(fh, delimiter='\t')}


def tags_declared():
    """Known tag names: every scene doubles as a tag, plus drill:<verb>."""
    return scenes()


def main():
    if not os.path.exists(PATH):
        print('FAIL  classification.tsv is missing')
        return 1
    with open(PATH, encoding='utf-8') as fh:
        file_rows = list(csv.DictReader(fh, delimiter='\t'))
    by_key = {r['key']: r for r in file_rows}
    rows, _ = load(ROOT)
    valid = scenes()
    known = tags_declared()
    bad = 0

    # --- every sentence classified, exactly once
    if len(by_key) != len(file_rows):
        dupes = len(file_rows) - len(by_key)
        print(f'FAIL  {dupes} duplicate key(s) in classification.tsv')
        bad += dupes
    missing = [r['k'] for r in rows if r['k'] not in by_key]
    if missing:
        print(f'FAIL  {len(missing)} sentence(s) with no row: {missing[:5]}')
        bad += len(missing)
    corpus_keys = {r['k'] for r in rows}
    orphan = [k for k in by_key if k not in corpus_keys]
    if orphan:
        print(f'FAIL  {len(orphan)} row(s) for sentences that do not exist: {orphan[:5]}')
        bad += len(orphan)

    # --- scenes and tags must exist
    for r in file_rows:
        s = (r.get('scene') or '').strip()
        if not s:
            print(f"FAIL  {r['key']}: no scene")
            bad += 1
        elif s not in valid:
            print(f"FAIL  {r['key']}: scene {s!r} is not in topics/_index.tsv")
            bad += 1
        for t in (r.get('tags') or '').split(','):
            t = t.strip()
            if not t:
                continue
            if t.startswith('drill:'):
                continue
            if t not in known:
                print(f"FAIL  {r['key']}: tag {t!r} is not a known scene or drill:")
                bad += 1
            if t == s:
                print(f"FAIL  {r['key']}: tag {t!r} repeats the scene")
                bad += 1

    # --- the round trip: what the app loads must equal what the file says
    drift = 0
    for r in rows:
        want = (by_key.get(r['k'], {}).get('scene') or '').strip()
        if want and r['tp'] != want:
            if drift < 5:
                print(f"FAIL  {r['k']}: file says {want!r}, corpus loaded {r['tp']!r}")
            drift += 1
    if drift:
        print(f'FAIL  {drift} sentence(s) did not survive the round trip')
        bad += drift

    # --- no scene may end up empty
    used = {r['tp'] for r in rows}
    empty = sorted(valid - used)
    if empty:
        print(f'FAIL  scene(s) with no sentences: {empty}')
        bad += len(empty)

    n = len(rows)
    print(f'{"FAIL" if bad else "ok  "}  classification: {n - bad}/{n} '
          f'({len(used)} scenes in use)')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
