"""The merged corpus: the 2000 ranked sentences plus the extra forms.

build.py and the audio builders must agree exactly on what the deck contains
and on the key of every sentence, so the merge lives here rather than in both.
"""
import csv
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(root=ROOT):
    """-> list of rows, sorted, each with a unique key `k`.

    A sentence's key is its rank for the 2000 originals and <rank>x<n> for an
    extra form, because the extra forms share their verb's rank. Progress
    marks and audio indexes are keyed on it.
    """
    rows, seen = [], {}
    for path in sorted(glob.glob(os.path.join(root, 'data', 'verbs_*.tsv'))):
        name = os.path.basename(path)
        with open(path, encoding='utf-8') as fh:
            for i, r in enumerate(csv.DictReader(fh, delimiter='\t'), start=2):
                try:
                    rank = int(r['rank'])
                except (KeyError, ValueError, TypeError):
                    sys.exit(f'{name}:{i}: bad or missing rank')
                for col in ('verb_es', 'verb_en', 'sentence_es', 'sentence_en'):
                    if not (r.get(col) or '').strip():
                        sys.exit(f'{name}:{i}: empty {col}')
                if rank in seen:
                    sys.exit(f'{name}:{i}: duplicate rank {rank} '
                             f'(already in {seen[rank]})')
                seen[rank] = name
                rows.append({
                    'r': rank, 'v': r['verb_es'].strip(), 've': r['verb_en'].strip(),
                    's': r['sentence_es'].strip(), 't': r['sentence_en'].strip(),
                    'n': (r.get('note') or '').strip(),
                    'tp': (r.get('topic') or '').strip(),
                    'f': (r.get('form') or '').strip(),
                    'vt': (r.get('verb_token') or '').strip(),
                    'sq': 0, 'k': str(rank),
                })

    # Extra forms inherit their verb's rank, topic and gloss, and sort directly
    # after it, so a verb and its other tenses are read together.
    xpath = os.path.join(root, 'data', 'sentences_extra.tsv')
    extra = 0
    if os.path.exists(xpath):
        base = {}
        for r in rows:
            base.setdefault(r['v'], r)
        seq = {}
        with open(xpath, encoding='utf-8') as fh:
            for i, r in enumerate(csv.DictReader(fh, delimiter='\t'), start=2):
                verb = r['verb'].strip()
                b = base.get(verb)
                if not b:
                    sys.exit(f'sentences_extra.tsv:{i}: {verb!r} is not in the corpus')
                for col in ('form', 'sentence_es', 'sentence_en'):
                    if not (r.get(col) or '').strip():
                        sys.exit(f'sentences_extra.tsv:{i}: empty {col} for {verb}')
                seq[verb] = seq.get(verb, 0) + 1
                rows.append({
                    'r': b['r'], 'v': verb, 've': b['ve'],
                    's': r['sentence_es'].strip(), 't': r['sentence_en'].strip(),
                    'n': (r.get('note') or '').strip(),
                    'tp': b['tp'], 'f': r['form'].strip(),
                    'vt': (r.get('verb_token') or '').strip(),
                    'sq': seq[verb], 'k': f"{b['r']}x{seq[verb]}",
                })
                extra += 1

    rows.sort(key=lambda x: (x['r'], x['sq']))
    return rows, extra


def topics(root=ROOT):
    """-> ordered list of topic dicts from data/topics/_index.tsv."""
    path = os.path.join(root, 'data', 'topics', '_index.tsv')
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as fh:
        meta = sorted(csv.DictReader(fh, delimiter='\t'), key=lambda r: int(r['order']))
    return [{'slug': t['slug'], 'section': t['section'], 'title': t['title'],
             'blurb': (t.get('blurb') or '').strip()} for t in meta]
