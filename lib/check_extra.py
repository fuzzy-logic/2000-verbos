"""Verify data/sentences_extra.tsv: each sentence must really be in the form
it claims, checked by the same matcher that tagged the main corpus."""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tag_forms import fold, identify, strip_clitic, tokens  # noqa: E402
from conjugate import Verb, paradigm  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Compound forms are two words and get tagged by the auxiliary.
COMPOUND = {'perf-1s': 'part', 'prog-1s': 'ger'}


def main():
    path = os.path.join(ROOT, 'data', 'sentences_extra.tsv')
    rows = list(csv.DictReader(open(path, encoding='utf-8'), delimiter='\t'))
    bad = []
    for i, r in enumerate(rows, start=2):
        want, verb = r['form'].strip(), r['verb'].strip()
        try:
            par = paradigm(verb.split()[0])
        except Exception as e:
            bad.append((i, verb, want, f'cannot conjugate: {e}', '', r['sentence_es']))
            continue
        if want == 'inf':
            target = Verb(verb.split()[0]).inf
        else:
            target = par.get(COMPOUND.get(want, want))
        if not target:
            bad.append((i, verb, want, 'no such slot', '', r['sentence_es']))
            continue
        # the claimed form, or any clitic-carrying variant of it, must appear
        want_f = fold(target.split()[-1])
        found = None
        for tk in tokens(r['sentence_es']):
            for cand, _ in strip_clitic(tk):
                if fold(cand) == want_f:
                    found = tk
                    break
            if found:
                break
        if found:
            continue
        tok, got, _ = identify(verb, r['sentence_es'])
        bad.append((i, verb, want, got, tok, r['sentence_es']))
    print(f'{len(rows)} extra sentences | {len(rows)-len(bad)} verified | {len(bad)} wrong')
    for i, v, want, got, tok, s in bad:
        print(f'   line {i:<4d} {v:<12s} claims {want:<11s} '
              f'(not present; reads {str(got)} [{tok}])  {s}')
    return len(bad)


COLS = ['verb', 'form', 'sentence_es', 'sentence_en', 'note', 'verb_token']


def write():
    """Fill in verb_token, so the card can highlight the verb in the sentence."""
    path = os.path.join(ROOT, 'data', 'sentences_extra.tsv')
    rows = list(csv.DictReader(open(path, encoding='utf-8'), delimiter='\t'))
    for r in rows:
        tok, _, _ = identify(r['verb'].strip(), r['sentence_es'])
        r['verb_token'] = tok or ''
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, COLS, delimiter='\t', extrasaction='ignore',
                           lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({k: (r.get(k) or '') for k in COLS})
    print(f'{len(rows)} rows, verb_token written')


if __name__ == '__main__':
    bad = main()
    if not bad:
        write()
    sys.exit(1 if bad else 0)
