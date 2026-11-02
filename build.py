#!/usr/bin/env python3
"""Merge data/*.tsv into src/template.html -> dist/index.html (single deployable file)."""
import csv, glob, hashlib, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'lib'))
from corpus import load, topics as load_topics          # noqa: E402

rows, extra_n = load(ROOT)

# Catch stray characters that aren't Spanish or English - a typo like "Llena"
# with a Polish hook instead of an accent would otherwise be read aloud wrong.
ALLOWED = set("áéíóúüñÁÉÍÓÚÜÑ¿¡"          # Spanish
              "ẽĩũỹÃãẼĨŨỸ\u0303"          # Guaraní nasal vowels
              "₲"                          # guaraní currency sign
              "—–’‘“”…·"                   # typographic punctuation
              "→←↔")                        # arrows, used in grammar notes
for r in rows:
    for col in ('v', 've', 's', 't', 'n'):
        for ch in r[col]:
            if ord(ch) > 127 and ch not in ALLOWED:
                sys.exit(f"rank {r['r']}: bad character {ch!r} (U+{ord(ch):04X}) in {col}: {r[col]}")

# A note admitting the entry isn't a verb means the row should never have shipped.
for r in rows:
    if 'not a verb' in r['n'].lower():
        sys.exit(f"rank {r['r']} ({r['v']}): note says it isn't a verb - replace the row")

# ---- topics (the Deck's by-topic view) ----
topics = load_topics(ROOT)
if topics:
    known_topics = {t['slug'] for t in topics}
    for r in rows:
        if not r['tp']:
            sys.exit(f"rank {r['r']} ({r['v']}): no topic assigned")
        if r['tp'] not in known_topics:
            sys.exit(f"rank {r['r']} ({r['v']}): unknown topic {r['tp']!r}")
    empty = known_topics - {r['tp'] for r in rows}
    if empty:
        sys.exit(f"topics with no verbs in them: {sorted(empty)}")

# ---- conjugation tables (the Verbs tab and the card panel) ----
conj = {}
cpath = os.path.join(ROOT, 'data', 'conjugations.tsv')
if os.path.exists(cpath):
    corpus_verbs = {r['v'] for r in rows}
    with open(cpath, encoding='utf-8') as fh:
        for i, r in enumerate(csv.DictReader(fh, delimiter='\t'), start=2):
            v = r['verb'].strip()
            if v not in corpus_verbs:
                sys.exit(f'conjugations.tsv:{i}: {v!r} is not in the corpus')
            for col in ('slot', 'form', 'pron', 'english', 'level', 'label'):
                if not (r.get(col) or '').strip():
                    sys.exit(f'conjugations.tsv:{i}: empty {col} for {v}')
            conj.setdefault(v, []).append(
                {'s': r['slot'], 'lv': r['level'], 'l': r['label'],
                 'f': r['form'], 'p': r['pron'], 'e': r['english'],
                 'n': (r.get('note') or '').strip()})
    # every conjugated verb must have a complete A1 block, or the table lies
    a1 = {c['s'] for c in next(iter(conj.values())) if c['lv'] == 'A1'}
    for v, cs in conj.items():
        have = {c['s'] for c in cs if c['lv'] == 'A1'}
        if have != a1 and v != 'haber':
            sys.exit(f'conjugations.tsv: {v} is missing A1 slots {sorted(a1-have)}')

# ---- edges (the card's sideways row) ----
edges = {}
epath = os.path.join(ROOT, 'data', 'edges.tsv')
if os.path.exists(epath):
    corpus_verbs = {r['v'] for r in rows}
    with open(epath, encoding='utf-8') as fh:
        for i, r in enumerate(csv.DictReader(fh, delimiter='\t'), start=2):
            a, b = r['from_verb'].strip(), r['to_verb'].strip()
            for v in (a, b):
                if v not in corpus_verbs:
                    sys.exit(f'edges.tsv:{i}: {v!r} is not in the corpus')
            edges.setdefault(a, []).append(
                {'to': b, 't': r['type'], 'n': (r.get('note') or '').strip()})

# ---- reference tables (the Basics tab) ----
TDIR = os.path.join(ROOT, 'data', 'tables')
tables = []
idx_path = os.path.join(TDIR, '_index.tsv')
if os.path.exists(idx_path):
    with open(idx_path, encoding='utf-8') as fh:
        meta = sorted(csv.DictReader(fh, delimiter='\t'), key=lambda r: int(r['order']))
    for m in meta:
        tpath = os.path.join(TDIR, m['slug'] + '.tsv')
        if not os.path.exists(tpath):
            sys.exit(f"_index.tsv lists {m['slug']} but {m['slug']}.tsv is missing")
        trows = []
        with open(tpath, encoding='utf-8') as fh:
            for i, r in enumerate(csv.DictReader(fh, delimiter='\t')):
                if not (r.get('spanish') or '').strip():
                    sys.exit(f"{m['slug']}.tsv row {i+2}: empty spanish")
                trows.append({'i': f"{m['slug']}#{i}",
                              's': r['spanish'].strip(),
                              'e': (r.get('english') or '').strip(),
                              'n': (r.get('note') or '').strip()})
        tables.append({'slug': m['slug'], 'section': m['section'],
                       'title': m['title'], 'blurb': m.get('blurb', '').strip(),
                       'rows': trows})
    # same charset rule as the deck
    for t in tables:
        for r in t['rows']:
            for ch in r['s'] + r['e'] + r['n']:
                if ord(ch) > 127 and ch not in ALLOWED:
                    sys.exit(f"{t['slug']}: bad character {ch!r} (U+{ord(ch):04X}) in {r['s']}")

tpl = open(os.path.join(ROOT, 'src', 'template.html'), encoding='utf-8').read()
if '/*__DATA__*/' not in tpl:
    sys.exit('template.html is missing the /*__DATA__*/ placeholder')

def inline(obj):
    # Can't let a literal </script> inside the data close the script tag early.
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

out = tpl.replace('/*__DATA__*/[]', inline(rows))
if '/*__TABLES__*/[]' not in out:
    sys.exit('template.html is missing the /*__TABLES__*/ placeholder')
out = out.replace('/*__TABLES__*/[]', inline(tables))
# Topics are small enough to inline. Conjugations and edges are not, and go
# out as separate files the app fetches when a tab or a card first needs them.
if '/*__TOPICS__*/[]' in out:
    out = out.replace('/*__TOPICS__*/[]', inline(topics))

DIST = os.path.join(ROOT, 'dist')
os.makedirs(DIST, exist_ok=True)
dest = os.path.join(DIST, 'index.html')
with open(dest, 'w', encoding='utf-8') as fh:
    fh.write(out)

# Static PWA assets alongside the page. sw.js gets the build hash stamped in so
# each deploy uses a fresh cache name and the previous one is purged.
build_id = hashlib.sha1(out.encode()).hexdigest()[:12]
for name in ('sw.js', 'manifest.webmanifest', 'icon.svg'):
    src = os.path.join(ROOT, 'src', name)
    if not os.path.exists(src):
        continue
    if name == 'sw.js':
        sw = open(src, encoding='utf-8').read()
        if '__BUILD__' not in sw:
            sys.exit('sw.js is missing the __BUILD__ placeholder')
        with open(os.path.join(DIST, name), 'w', encoding='utf-8') as fh:
            fh.write(sw.replace('__BUILD__', build_id))
    else:
        shutil.copy2(src, os.path.join(DIST, name))

# Android's install prompt wants raster icons; the SVG alone isn't reliably enough.
svg = os.path.join(DIST, 'icon.svg')
if os.path.exists(svg) and shutil.which('rsvg-convert'):
    for px in (192, 512):
        png = os.path.join(DIST, f'icon-{px}.png')
        if not os.path.exists(png) or os.path.getmtime(svg) > os.path.getmtime(png):
            subprocess.run(['rsvg-convert', '-w', str(px), '-h', str(px),
                            svg, '-o', png], check=True)

# Conjugations and edges ship as their own files so the first page load stays
# small; the service worker precaches them for offline use.
if conj:
    json.dump(conj, open(os.path.join(DIST, 'conjugations.json'), 'w'),
              separators=(',', ':'), ensure_ascii=False)
if edges:
    json.dump(edges, open(os.path.join(DIST, 'edges.json'), 'w'),
              separators=(',', ':'), ensure_ascii=False)

# packs.json: what the app offers for offline download, built from whatever
# tracks have actually been generated into dist/audio/.
adir = os.path.join(DIST, 'audio')
packs = []
order = {t['slug']: i for i, t in enumerate(topics)}
tfiles = sorted(glob.glob(os.path.join(adir, 'topic_*.json')),
                key=lambda f: order.get(
                    json.load(open(f, encoding='utf-8')).get('topic', ''), 999))
for jf in tfiles:
    meta = json.load(open(jf, encoding='utf-8'))
    mp3 = os.path.join(adir, meta['stem'] + '.mp3')
    if not os.path.exists(mp3):
        continue
    packs.append({'stem': meta['stem'], 'topic': meta['topic'],
                  'title': meta['title'], 'section': meta.get('section', ''),
                  'duration': meta['duration'],
                  'mb': round(os.path.getsize(mp3) / 1e6, 1)})

cj = os.path.join(adir, 'conj.json')
cm = os.path.join(adir, 'conj.mp3')
if os.path.exists(cj) and os.path.exists(cm):
    meta = json.load(open(cj, encoding='utf-8'))
    packs.append({'stem': 'conj', 'kind': 'conj', 'title': 'Conjugation forms',
                  'section': 'Reference',
                  'duration': meta['duration'],
                  'mb': round(os.path.getsize(cm) / 1e6, 1)})

tj = os.path.join(adir, 'tables.json')
tm = os.path.join(adir, 'tables.mp3')
if os.path.exists(tj) and os.path.exists(tm):
    meta = json.load(open(tj, encoding='utf-8'))
    packs.append({'stem': 'tables', 'kind': 'tables', 'title': 'Basics tables',
                  'section': 'Reference',
                  'duration': meta['duration'],
                  'mb': round(os.path.getsize(tm) / 1e6, 1)})
if packs:
    json.dump(packs, open(os.path.join(adir, 'packs.json'), 'w'), separators=(',', ':'))

ranks = {r['r'] for r in rows}
stale = glob.glob(os.path.join(adir, 'verbos_*.mp3'))
if stale:
    print(f"NOTE: {len(stale)} old rank-range packs are still in dist/audio. "
          f"They are no longer referenced; delete them once the topic packs are built.")

missing = [n for n in range(1, max(ranks) + 1) if n not in ranks] if ranks else []
lemmas = {}
for r in rows:
    if not r['sq']:                      # extra forms repeat their verb by design
        lemmas.setdefault(r['v'].lower(), []).append(r['r'])
repeats = {k: v for k, v in lemmas.items() if len(v) > 1}
print(f"{len(rows)} sentences ({extra_n} extra forms) -> dist/index.html ({os.path.getsize(dest)/1024:.0f} KB), build {build_id}")
if tables:
    print(f"{len(tables)} reference tables, "
          f"{sum(len(t['rows']) for t in tables)} rows")
if packs:
    tot = sum(p['mb'] for p in packs)
    print(f"{len(packs)} audio pack(s), {tot:.1f} MB total")
else:
    print("no audio packs built yet")
print(f"{len(lemmas)} distinct verbs; {len(repeats)} appear more than once")
if repeats:
    sample = sorted(repeats.items(), key=lambda kv: -len(kv[1]))[:6]
    print('  most repeated: ' + ', '.join(f"{k}×{len(v)}" for k, v in sample))
if missing:
    print(f"gaps in rank sequence: {len(missing)} missing, first few {missing[:10]}")
