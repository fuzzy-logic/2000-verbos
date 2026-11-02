"""Generate data/conjugations.tsv - the tables the Verbs tab and the card show.

One row per verb and slot, banded A1/A2/B1. B2/C1 slots are reserved in the
schema and filled in a later pass; raising the ceiling is a data change.
"""
import csv
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from conjugate import SLOTS, forms, pattern_of, Verb      # noqa: E402
from english import parts                                 # noqa: E402
from pron import phrase                                   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPTH = 400          # how many verbs get a full table

COLS = ['verb', 'rank', 'level', 'slot', 'label', 'form', 'pron', 'english', 'note']

# Per-slot notes. The vos/tu contrast is the single most important thing on
# the table for someone living in Paraguay, so it is said on every verb.
SLOT_NOTE = {
    'pres-2s': 'voseo - this is the one you use here',
    'pres-2s-tu': 'not used in Paraguay; recognise it, do not say it',
    'going-1s': 'ir a + infinitive - how the future is usually said',
}


def verbs():
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'data', 'verbs_*.tsv'))):
        with open(path, encoding='utf-8') as fh:
            rows += list(csv.DictReader(fh, delimiter='\t'))
    rows.sort(key=lambda r: int(r['rank']))
    out, seen = [], set()
    for r in rows:
        v = r['verb_es'].strip()
        if v in seen:
            continue
        seen.add(v)
        out.append(r)
        if len(out) >= DEPTH:
            break
    return out


def main():
    rows, skipped = [], []
    for r in verbs():
        verb, rank = r['verb_es'].strip(), int(r['rank'])
        try:
            f = forms(verb)
            en = parts(r['verb_en'])
        except Exception as e:
            skipped.append((rank, verb, str(e)))
            continue
        if not en:
            skipped.append((rank, verb, 'no English gloss'))
            continue
        for slot, level, label, tpl in SLOTS:
            form = f.get(slot)
            if not form:
                continue
            note = SLOT_NOTE.get(slot, '')
            if slot == 'cmd-vos-neg' and f.get('cmd-vos-neg-voseo') != form:
                note = 'also heard: ' + f['cmd-vos-neg-voseo']
            rows.append({
                'verb': verb, 'rank': rank, 'level': level, 'slot': slot,
                'label': label, 'form': form, 'pron': phrase(form),
                'english': tpl.format(**en), 'note': note,
            })
    path = os.path.join(ROOT, 'data', 'conjugations.tsv')
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, COLS, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    nv = len({r['verb'] for r in rows})
    print(f'{len(rows)} rows for {nv} verbs -> data/conjugations.tsv')
    if skipped:
        print(f'skipped {len(skipped)}:')
        for rank, v, why in skipped:
            print(f'   r{rank:<5d} {v:<24s} {why}')


if __name__ == '__main__':
    main()
