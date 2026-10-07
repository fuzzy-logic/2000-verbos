#!/usr/bin/env python3
"""
Build one MP3 of every reference-table phrase, plus a seek index.

Unlike the verb walking tracks there's no teaching structure here - these rows
are only ever played one at a time by tapping, so it's just each Spanish phrase
in order with a short gap, and a map from row id to (offset, duration).

Clip caching is shared with make_track.py via the same hash scheme, so phrases
already spoken in the deck are not re-synthesised.

    .venv/bin/python3 audio/make_tables_track.py
"""
import argparse, asyncio, csv, glob, hashlib, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS = os.path.join(ROOT, 'audio', 'clips')
SIL = os.path.join(ROOT, 'audio', 'silence')
DURCACHE = os.path.join(CLIPS, '_durations.json')

try:
    import edge_tts
except ImportError:
    sys.exit("edge-tts is not installed: .venv/bin/pip install edge-tts")

_durs = {}

TRIM = ('silenceremove=start_periods=1:start_duration=0:start_threshold=-50dB:detection=peak,'
        'areverse,'
        'silenceremove=start_periods=1:start_duration=0:start_threshold=-50dB:detection=peak,'
        'areverse')


def dur(path):
    key = os.path.basename(path)
    if key not in _durs:
        out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                              '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip()
        _durs[key] = round(float(out or 0), 3)
    return _durs[key]


def clip_path(text, voice, rate):
    key = hashlib.sha1(f"{voice}|{rate}|{text}".encode()).hexdigest()[:16]
    return os.path.join(CLIPS, f"{key}.mp3")


def trim(src, dest):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', TRIM,
                    '-c:a', 'libmp3lame', '-q:a', '6', '-ar', '24000', '-ac', '1', dest],
                   check=True)


async def synth(text, voice, rate, sem, retries=4):
    dest = clip_path(text, voice, rate)
    if os.path.exists(dest) and os.path.getsize(dest) > 512:
        return dest
    async with sem:
        for attempt in range(retries):
            try:
                tmp = dest + '.part'
                await edge_tts.Communicate(text, voice, rate=rate).save(tmp)
                if os.path.getsize(tmp) < 512:
                    raise RuntimeError('empty audio')
                trim(tmp, dest)
                os.remove(tmp)
                return dest
            except Exception as exc:
                if attempt == retries - 1:
                    raise RuntimeError(f"failed: {text[:40]!r} -> {exc}")
                await asyncio.sleep(1.5 * (attempt + 1))
    return dest


def silence(seconds):
    dest = os.path.join(SIL, f"{seconds:.1f}.mp3")
    if not os.path.exists(dest):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi',
                        '-i', 'anullsrc=r=24000:cl=mono', '-t', str(seconds),
                        '-c:a', 'libmp3lame', '-q:a', '9', '-ar', '24000', '-ac', '1', dest],
                       check=True)
    return dest


def load_table_rows():
    tdir = os.path.join(ROOT, 'data', 'tables')
    idx = os.path.join(tdir, '_index.tsv')
    meta = sorted(csv.DictReader(open(idx, encoding='utf-8'), delimiter='\t'),
                  key=lambda r: int(r['order']))
    rows = []
    for m in meta:
        path = os.path.join(tdir, m['slug'] + '.tsv')
        for i, r in enumerate(csv.DictReader(open(path, encoding='utf-8'), delimiter='\t')):
            text = (r.get('spanish') or '').strip()
            if text:
                rows.append((f"{m['slug']}#{i}", text))
    return rows


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--es-voice', default='es-PY-TaniaNeural')
    ap.add_argument('--gap', type=float, default=0.6)
    ap.add_argument('--outdir', default=os.path.join(ROOT, 'dist', 'audio'))
    a = ap.parse_args()

    os.makedirs(CLIPS, exist_ok=True); os.makedirs(SIL, exist_ok=True)
    os.makedirs(a.outdir, exist_ok=True)
    global _durs
    if os.path.exists(DURCACHE):
        _durs = json.load(open(DURCACHE))

    rows = load_table_rows()
    texts = list(dict.fromkeys(t for _, t in rows))
    todo = sum(1 for t in texts if not os.path.exists(clip_path(t, a.es_voice, '+0%')))
    print(f"{len(rows)} rows | {len(texts)} distinct phrases ({todo} to synthesise)")

    sem = asyncio.Semaphore(6)
    tasks = [asyncio.create_task(synth(t, a.es_voice, '+0%', sem)) for t in texts]
    done = 0
    for fut in asyncio.as_completed(tasks):
        await fut
        done += 1
        if done % 100 == 0 or done == len(tasks):
            print(f"  {done}/{len(tasks)} clips", flush=True)

    gap = silence(a.gap)
    seq, mapping, t = [], {}, 0.0
    for rid, text in rows:
        c = clip_path(text, a.es_voice, '+0%')
        mapping[rid] = [round(t, 3), dur(c)]
        seq.append(c); t += dur(c)
        seq.append(gap); t += dur(gap)
    json.dump(_durs, open(DURCACHE, 'w'))

    listfile = os.path.join(ROOT, 'audio', '.concat-tables.txt')
    with open(listfile, 'w', encoding='utf-8') as fh:
        for p in seq:
            fh.write("file '" + p.replace("'", r"'\''") + "'\n")
    out = os.path.join(a.outdir, 'tables.mp3')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', listfile,
                    '-c:a', 'libmp3lame', '-q:a', '6', '-ar', '24000', '-ac', '1',
                    '-metadata', 'title=Basics tables', '-metadata', 'artist=2000 Verbos', out],
                   check=True)
    os.remove(listfile)

    real = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                 '-of', 'csv=p=0', out], capture_output=True, text=True).stdout.strip() or 0)
    json.dump({'stem': 'tables', 'duration': round(real, 3), 'voice': a.es_voice, 'map': mapping},
              open(os.path.join(a.outdir, 'tables.json'), 'w'),
              ensure_ascii=False, separators=(',', ':'))
    drift = real - t
    print(f"\n{out}\n{real/60:.0f} min | {os.path.getsize(out)/1e6:.1f} MB | "
          f"{len(mapping)} indexed rows | drift {drift:+.3f}s")
    if abs(drift) > 0.5:
        print('WARNING: drift over 0.5s - seeking will be off')

asyncio.run(main())
