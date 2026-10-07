#!/usr/bin/env python3
"""Merge data/*.tsv into src/template.html -> dist/index.html (single deployable file)."""
import csv, glob, hashlib, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
rows, seen = [], {}

for path in sorted(glob.glob(os.path.join(ROOT, 'data', '*.tsv'))):
    with open(path, encoding='utf-8') as fh:
        for i, r in enumerate(csv.DictReader(fh, delimiter='\t'), start=2):
            try:
                rank = int(r['rank'])
            except (KeyError, ValueError, TypeError):
                sys.exit(f"{os.path.basename(path)}:{i}: bad or missing rank")
            for col in ('verb_es', 'verb_en', 'sentence_es', 'sentence_en'):
                if not (r.get(col) or '').strip():
                    sys.exit(f"{os.path.basename(path)}:{i}: empty {col}")
            if rank in seen:
                sys.exit(f"{os.path.basename(path)}:{i}: duplicate rank {rank} "
                         f"(already in {seen[rank]})")
            seen[rank] = os.path.basename(path)
            rows.append({
                'r': rank,
                'v': r['verb_es'].strip(),
                've': r['verb_en'].strip(),
                's': r['sentence_es'].strip(),
                't': r['sentence_en'].strip(),
                'n': (r.get('note') or '').strip(),
            })

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

rows.sort(key=lambda x: x['r'])

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

# packs.json: what the app offers for offline download, built from whatever
# tracks have actually been generated into dist/audio/.
adir = os.path.join(DIST, 'audio')
packs = []
for jf in sorted(glob.glob(os.path.join(adir, 'verbos_*.json'))):
    meta = json.load(open(jf, encoding='utf-8'))
    mp3 = os.path.join(adir, meta['stem'] + '.mp3')
    if not os.path.exists(mp3):
        continue
    packs.append({'stem': meta['stem'], 'start': meta['start'], 'end': meta['end'],
                  'duration': meta['duration'],
                  'mb': round(os.path.getsize(mp3) / 1e6, 1)})

tj = os.path.join(adir, 'tables.json')
tm = os.path.join(adir, 'tables.mp3')
if os.path.exists(tj) and os.path.exists(tm):
    meta = json.load(open(tj, encoding='utf-8'))
    packs.append({'stem': 'tables', 'kind': 'tables',
                  'duration': meta['duration'],
                  'mb': round(os.path.getsize(tm) / 1e6, 1)})
if packs:
    json.dump(packs, open(os.path.join(adir, 'packs.json'), 'w'), separators=(',', ':'))

missing = [n for n in range(1, max(seen) + 1) if n not in seen] if seen else []
lemmas = {}
for r in rows:
    lemmas.setdefault(r['v'].lower(), []).append(r['r'])
repeats = {k: v for k, v in lemmas.items() if len(v) > 1}
print(f"{len(rows)} sentences -> dist/index.html ({os.path.getsize(dest)/1024:.0f} KB), build {build_id}")
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
