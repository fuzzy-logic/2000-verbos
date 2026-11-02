"""Generate data/edges.tsv - the sideways links between verbs.

Derived types only. The hand-written ones (confusable, opposite) are phase 2.

  family    prefixed derivative of another verb in the corpus, flagged with
            whether it actually inherits the base's conjugation
  pattern   conjugates like this exemplar
  reflexive the se- counterpart, where both are in the corpus
  cooccurs  another corpus verb appears in this verb's example sentence
"""
import csv
import glob
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import conjugate as C                                    # noqa: E402
from tag_forms import fold, tokens, strip_clitic         # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLS = ['from_verb', 'to_verb', 'type', 'note']


def corpus():
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'data', 'verbs_*.tsv'))):
        with open(path, encoding='utf-8') as fh:
            rows += list(csv.DictReader(fh, delimiter='\t'))
    rows.sort(key=lambda r: int(r['rank']))
    return rows


def main():
    rows = corpus()
    rank = {}
    gloss = {}
    for r in rows:
        v = r['verb_es'].strip()
        rank.setdefault(v, int(r['rank']))
        gloss.setdefault(v, r['verb_en'].strip())
    verbs = sorted(rank, key=lambda v: rank[v])
    simple = {v for v in verbs if ' ' not in v}
    edges, seen = [], set()

    def add(a, b, kind, note=''):
        key = (a, b, kind)
        if a != b and key not in seen:
            seen.add(key)
            edges.append({'from_verb': a, 'to_verb': b, 'type': kind, 'note': note})

    # --- family: prefixed derivatives, with inheritance checked, not assumed
    inherits = diverges = 0
    for v in simple:
        _, base = C.base_of(v, simple)
        if not base:
            continue
        try:
            same = C.pattern_of(v) == C.pattern_of(base)
        except Exception:
            continue
        note = ('conjugates exactly like it' if same
                else 'looks related but conjugates differently')
        inherits += same
        diverges += not same
        add(v, base, 'family', note)
        add(base, v, 'family', note)

    # --- pattern: which exemplar each verb follows
    for v in verbs:
        try:
            ex = C.pattern_of(v.split()[0])
        except Exception:
            continue
        if ex in rank and ex != v:
            add(v, ex, 'pattern', 'conjugates like ' + ex)

    # --- reflexive counterparts present in the corpus
    for v in simple:
        if v.endswith('se') and len(v) > 4 and v[-3] == 'r':
            base = v[:-2]
            if base in rank:
                add(v, base, 'reflexive', 'the plain form')
                add(base, v, 'reflexive', 'the reflexive form, often a shift in meaning')

    # --- cooccurs: another verb of the 2000 appears in this sentence
    # takes-infinitive: an infinitive following another verb. Matching whole
    # conjugated forms was abandoned - without part-of-speech tagging, nouns
    # that coincide with verb forms (casa, tarde, aumento, río) produced wrong
    # links, and a wrong "see also" on a learning card is worse than none.
    # An infinitive is unambiguous, and verb + infinitive is exactly the
    # construction worth showing: which verbs take one, and which preposition.
    NOUN_INF = {'deber', 'poder', 'placer', 'parecer', 'ser', 'haber', 'amanecer'}
    inf_of = {}
    for v in simple:
        try:
            inf = C.Verb(v).inf
        except Exception:
            continue
        # hacer and hacerse share an infinitive; a bare infinitive in a
        # sentence is the plain verb, so let that one win
        if inf not in inf_of or v == inf:
            inf_of[inf] = v
    LINKERS = {'que', 'a', 'de', 'en', 'por', 'para', 'con', 'sin'}
    for r in rows:
        mine = r['verb_es'].strip()
        head = mine.split()[0]
        toks = tokens(r['sentence_es'])
        for i, t in enumerate(toks):
            for cand, _ in strip_clitic(t):
                target = inf_of.get(cand)
                if not target or target in (mine, head) or cand in NOUN_INF:
                    continue
                # The edge only means something if THIS row's verb is the one
                # governing the infinitive. Otherwise the preposition belongs
                # to an adverbial phrase ("antes de contestar") and the link
                # is just co-occurrence, which is the noisy thing above.
                vt = (r.get('verb_token') or '').lower()
                prev = toks[i - 1] if i else ''
                prev2 = toks[i - 2] if i > 1 else ''
                if prev == vt:
                    link = ''
                elif prev in LINKERS and prev2 == vt:
                    link = ' ' + prev
                else:
                    continue
                add(mine, target, 'takes-infinitive',
                    f'{head}{link} + infinitive: «{r["sentence_es"]}»')

    path = os.path.join(ROOT, 'data', 'edges.tsv')
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, COLS, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(edges)
    from collections import Counter
    c = Counter(e['type'] for e in edges)
    print(f'{len(edges)} edges -> data/edges.tsv')
    for k, n in c.most_common():
        print(f'   {k:10s} {n:5d}')
    print(f'\nfamily inheritance: {inherits} inherit the base conjugation, '
          f'{diverges} diverge')


if __name__ == '__main__':
    main()
