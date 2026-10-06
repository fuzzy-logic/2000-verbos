#!/usr/bin/env python3
"""Merge data/*.tsv into src/template.html -> dist/index.html (single deployable file)."""
import csv, glob, json, os, sys

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

rows.sort(key=lambda x: x['r'])

tpl = open(os.path.join(ROOT, 'src', 'template.html'), encoding='utf-8').read()
if '/*__DATA__*/' not in tpl:
    sys.exit('template.html is missing the /*__DATA__*/ placeholder')

payload = json.dumps(rows, ensure_ascii=False, separators=(',', ':'))
# Can't let a literal </script> inside the data close the script tag early.
payload = payload.replace('</', '<\\/')
out = tpl.replace('/*__DATA__*/[]', payload)

os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
dest = os.path.join(ROOT, 'dist', 'index.html')
with open(dest, 'w', encoding='utf-8') as fh:
    fh.write(out)

missing = [n for n in range(1, max(seen) + 1) if n not in seen] if seen else []
print(f"{len(rows)} sentences -> dist/index.html ({os.path.getsize(dest)/1024:.0f} KB)")
if missing:
    print(f"gaps in rank sequence: {len(missing)} missing, first few {missing[:10]}")
