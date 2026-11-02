"""Find which token in each sentence is the verb, and what form it is in.

Writes the `form` column the by-tense view needs, and - as a side effect -
reports rows whose sentence does not actually contain their verb, which is how
corpus bugs surface.
"""
import csv
import glob
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from conjugate import Verb, paradigm  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Object and reflexive pronouns that attach to the end of a word.
CLITICS = ['melo', 'mela', 'telo', 'tela', 'selo', 'sela', 'selos', 'selas',
           'noslo', 'nosla', 'me', 'te', 'se', 'lo', 'la', 'le', 'nos',
           'los', 'las', 'les']

PAST = re.compile(r'\b(ayer|anoche|anteayer|antes|hace|pasad[oa]s?|'
                  r'anteanoche|ya|recién|una vez|aquella vez|de chico|'
                  r'cuando era|el otro día)\b', re.I)
FUTURE = re.compile(r'\b(mañana|luego|después|pronto|más tarde|la semana que '
                    r'viene|el año que viene|algún día)\b', re.I)

# When one surface form fits several slots, prefer in this order. -ar verbs
# make pres-1p and pret-1p identical (hablamos), which no amount of
# cleverness resolves without reading the sentence.
PREF = ['pres-3s', 'pres-1s', 'pres-2s', 'pres-3p', 'pres-1p', 'pres-2s-tu',
        'cmd-vos', 'cmd-tu', 'ger', 'part', 'pret-3s', 'pret-1s', 'pret-3p',
        'pret-2s', 'pret-1p', 'imperf-3s', 'imperf-1s', 'imperf-3p',
        'imperf-1p', 'imperf-2s', 'fut-3s', 'fut-1s', 'fut-3p', 'fut-2s',
        'fut-1p', 'cond-1s', 'cond-3s', 'cond-3p', 'cond-2s', 'cond-1p',
        'subj-3s', 'subj-1s', 'subj-3p', 'subj-2s', 'subj-1p', 'subj-2s-voseo',
        'subjimp-1s', 'subjimp-3s', 'subjimp-3p', 'subjimp-1p', 'subjimp-2s',
        'cmd-ud', 'cmd-uds']


def _agree(participle):
    """A participle used as an adjective agrees: deshabitado/-a/-os/-as."""
    base = fold(participle)
    return {base, base[:-1] + 'a', base + 's', base[:-1] + 'as'} if base.endswith('o') else {base}


def fold(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower())
                   if unicodedata.category(c) != 'Mn')


def tokens(sentence):
    return re.findall(r"[a-záéíóúüñ]+", sentence.lower())


# Spanish attaches an enclitic only to an imperative, an infinitive or a
# gerund - never to a finite verb. So "estirate" is the vos command estirá
# plus te, and cannot be the present estira.
ENCLITIC_OK = {'cmd-vos', 'cmd-tu', 'cmd-ud', 'cmd-uds', 'inf', 'ger'}


def strip_clitic(tok):
    """-> [(form, had_clitic)]. ayudarme -> ayudar, levantate -> levanta."""
    out = [(tok, False)]
    for c in CLITICS:
        if tok.endswith(c) and len(tok) - len(c) >= 2:
            out.append((tok[:-len(c)], True))
    return out


def index(verb):
    """surface form -> [slots], for one headword including its phrase tail."""
    head = verb.strip().split()[0]
    try:
        par = paradigm(head)
    except Exception:
        return None, None
    fwd = {}
    for slot, form in par.items():
        fwd.setdefault(form.split()[0].lower(), []).append(slot)
    try:
        inf = Verb(head).inf
    except Exception:
        inf = head
    fwd.setdefault(inf, []).append('inf')
    return fwd, par


def identify(verb, sentence):
    """-> (token, slot, how) or (None, None, reason)."""
    fwd, par = index(verb)
    if fwd is None:
        return None, None, 'cannot conjugate'
    toks = tokens(sentence)
    folded = {fold(k): v for k, v in fwd.items()}

    # compound tenses first: they are two tokens and the second one, the
    # participle or gerund, is what identifies the verb
    part, ger = par.get('part'), par.get('ger')
    for i, t in enumerate(toks):
        prev = toks[i - 1] if i else ''
        if part and fold(t) in _agree(part) and i:
            if prev in ('he', 'has', 'ha', 'hemos', 'han'):
                return t, 'perf', 'compound'
            if prev.startswith(('hab',)) and prev not in ('hablar',):
                return t, 'pluperf', 'compound'
        if ger and fold(t) == fold(ger) and i:
            if prev in ('estoy', 'estás', 'está', 'estamos', 'están',
                        'estaba', 'estabas', 'estábamos', 'estaban'):
                return t, 'prog', 'compound'

    if part:
        ag = _agree(part)
        for t in toks:
            if fold(t) in ag and fold(t) != fold(par.get('pres-1s', '')):
                return t, 'part', 'participle'

    for exact in (True, False):
        best = None
        for t in toks:
            for cand, clitic in strip_clitic(t):
                # an enclitic drags the written accent off the vos command
                # (estirá + te = estirate), so a stripped stem is matched
                # accent-blind
                hits = (folded.get(fold(cand)) if (clitic or not exact)
                        else fwd.get(cand))
                if not hits:
                    continue
                for slot in hits:
                    if clitic and slot not in ENCLITIC_OK:
                        continue
                    rank = PREF.index(slot) if slot in PREF else len(PREF)
                    if best is None or rank < best[0]:
                        best = (rank, t, slot)
        if best:
            return best[1], best[2], 'exact' if exact else 'unaccented'
    return None, None, 'verb not found in sentence'


def disambiguate(slot, sentence):
    """hablamos is both present and preterite; the sentence usually says."""
    if slot == 'pres-1p' and PAST.search(sentence):
        return 'pret-1p'
    if slot.startswith('pres-') and FUTURE.search(sentence) and 'ir' not in slot:
        return slot
    return slot


def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'data', 'verbs_*.tsv'))):
        with open(path, encoding='utf-8') as fh:
            for r in csv.DictReader(fh, delimiter='\t'):
                r['_file'] = os.path.basename(path)
                rows.append(r)
    rows.sort(key=lambda r: int(r['rank']))

    from collections import Counter
    counts, how = Counter(), Counter()
    misses = []
    for r in rows:
        tok, slot, note = identify(r['verb_es'], r['sentence_es'])
        if slot:
            slot = disambiguate(slot, r['sentence_es'])
            r['_tok'], r['_form'] = tok, slot
            counts[slot] += 1
            how[note] += 1
        else:
            misses.append(r)
            how[note] += 1

    print(f'{len(rows)} rows | matched {sum(counts.values())} '
          f'({100*sum(counts.values())/len(rows):.1f}%) | unmatched {len(misses)}')
    print('\nhow matched:', dict(how))
    print('\nform distribution (top 25):')
    for slot, n in counts.most_common(25):
        print(f'   {slot:16s} {n:5d}')
    if misses:
        print(f'\nrows whose sentence does not contain their verb ({len(misses)}):')
        for r in misses[:40]:
            print(f"   r{r['rank']:<5s} {r['verb_es']:<24s} {r['sentence_es']}")
    return misses


if __name__ == '__main__':
    main()


COLS = ['rank', 'verb_es', 'verb_en', 'sentence_es', 'sentence_en', 'note',
        'topic', 'form', 'verb_token']


def write():
    """Add/refresh the form and verb_token columns in data/verbs_*.tsv."""
    total = 0
    for path in sorted(glob.glob(os.path.join(ROOT, 'data', 'verbs_*.tsv'))):
        with open(path, encoding='utf-8') as fh:
            rows = list(csv.DictReader(fh, delimiter='\t'))
        for r in rows:
            tok, slot, _ = identify(r['verb_es'], r['sentence_es'])
            if not slot:
                sys.exit(f"rank {r['rank']}: {r['verb_es']} not found in its "
                         f"sentence - fix the data before tagging")
            r['form'] = disambiguate(slot, r['sentence_es'])
            r['verb_token'] = tok
            r.setdefault('topic', '')
            total += 1
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            w = csv.DictWriter(fh, COLS, delimiter='\t', extrasaction='ignore',
                               lineterminator='\n')
            w.writeheader()
            for r in rows:
                w.writerow({c: (r.get(c) or '') for c in COLS})
        print(f'  {os.path.basename(path):24s} {len(rows):4d} rows')
    print(f'{total} rows tagged')
