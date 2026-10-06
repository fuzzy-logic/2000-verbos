#!/usr/bin/env python3
"""
Build walking-track MP3s (+ a seek index) from data/*.tsv using edge-tts.

Per sentence the track plays:
    verb (es)  ...3s...  verb (es)  ...  verb (en)
    sentence (es, slow)  ...7s to repeat it yourself...
    sentence (en)        ...2s...
    sentence (es, full speed)
    ...gap...  next

Alongside each MP3 it writes a .json seek index giving the offset and duration of
every individual clip, so the web app can play one verb or one sentence out of the
same file instead of shipping the clips twice.

    .venv/bin/python3 audio/make_track.py --start 1 --end 200
"""
import argparse, asyncio, csv, glob, hashlib, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS = os.path.join(ROOT, 'audio', 'clips')
SIL = os.path.join(ROOT, 'audio', 'silence')
DURCACHE = os.path.join(CLIPS, '_durations.json')

try:
    import edge_tts
except ImportError:
    sys.exit("edge-tts is not installed. Run:\n"
             "  python3 -m venv .venv && .venv/bin/pip install edge-tts")

_durs = {}


def load_rows():
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'data', '*.tsv'))):
        with open(path, encoding='utf-8') as fh:
            rows.extend(csv.DictReader(fh, delimiter='\t'))
    rows.sort(key=lambda r: int(r['rank']))
    return rows


def dur(path):
    """Duration in seconds, cached on disk - ffprobe per clip would be far too slow
    across ten thousand of them."""
    key = os.path.basename(path)
    if key not in _durs:
        out = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'csv=p=0', path], capture_output=True, text=True).stdout.strip()
        _durs[key] = round(float(out or 0), 3)
    return _durs[key]


def clip_path(text, voice, rate):
    key = hashlib.sha1(f"{voice}|{rate}|{text}".encode()).hexdigest()[:16]
    return os.path.join(CLIPS, f"{key}.mp3")


TRIM = ('silenceremove=start_periods=1:start_duration=0:start_threshold=-50dB:detection=peak,'
        'areverse,'
        'silenceremove=start_periods=1:start_duration=0:start_threshold=-50dB:detection=peak,'
        'areverse')


def trim(src, dest):
    """edge-tts pads every clip with its own silence, which would stack on top of
    our gaps and make them ~1-1.6s longer than asked for. Strip both ends so the
    gap lengths in the finished track are exactly the ones requested."""
    subprocess.run(
        ['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', TRIM,
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
        subprocess.run(
            ['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi',
             '-i', 'anullsrc=r=24000:cl=mono', '-t', str(seconds),
             '-c:a', 'libmp3lame', '-q:a', '9', '-ar', '24000', '-ac', '1', dest],
            check=True)
    return dest


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', type=int, default=1)
    ap.add_argument('--end', type=int, default=200)
    ap.add_argument('--es-voice', default='es-PY-TaniaNeural')
    ap.add_argument('--en-voice', default='en-GB-SoniaNeural')
    ap.add_argument('--slow', default='-35%')
    ap.add_argument('--repeat-gap', type=float, default=7.0)
    ap.add_argument('--verb-gap', type=float, default=3.0)
    ap.add_argument('--item-gap', type=float, default=2.5)
    ap.add_argument('--outdir', default=os.path.join(ROOT, 'dist', 'audio'))
    a = ap.parse_args()

    os.makedirs(CLIPS, exist_ok=True)
    os.makedirs(SIL, exist_ok=True)
    os.makedirs(a.outdir, exist_ok=True)
    global _durs
    if os.path.exists(DURCACHE):
        _durs = json.load(open(DURCACHE))

    rows = [r for r in load_rows() if a.start <= int(r['rank']) <= a.end]
    if not rows:
        sys.exit(f"no rows in range {a.start}-{a.end}")

    jobs = []
    for r in rows:
        jobs += [
            (r['sentence_es'], a.es_voice, a.slow),
            (r['sentence_es'], a.es_voice, '+0%'),
            (r['verb_es'],     a.es_voice, '+0%'),
            (r['verb_en'],     a.en_voice, '+0%'),
            (r['sentence_en'], a.en_voice, '+0%'),
        ]
    jobs = list(dict.fromkeys(jobs))
    todo = sum(1 for j in jobs if not os.path.exists(clip_path(*j)))
    print(f"{len(rows)} sentences | {len(jobs)} clips ({todo} to synthesise)")

    sem = asyncio.Semaphore(6)
    tasks = [asyncio.create_task(synth(t, v, rt, sem)) for t, v, rt in jobs]
    done = 0
    for fut in asyncio.as_completed(tasks):
        await fut
        done += 1
        if done % 100 == 0 or done == len(tasks):
            print(f"  {done}/{len(tasks)} clips", flush=True)

    g_verb, g_rep = silence(a.verb_gap), silence(a.repeat_gap)
    g_item, g_short, g_two = silence(a.item_gap), silence(1.2), silence(2.0)

    # Lay the track out and record where every clip lands. Offsets are the running
    # sum of input durations; we re-encode in a single pass so encoder delay is a
    # one-off constant at the head rather than per-clip drift.
    seq, index, t = [], [], 0.0

    def put(path):
        nonlocal t
        seq.append(path)
        start = t
        t += dur(path)
        return round(start, 3)

    for r in rows:
        es_v = clip_path(r['verb_es'], a.es_voice, '+0%')
        en_v = clip_path(r['verb_en'], a.en_voice, '+0%')
        es_slow = clip_path(r['sentence_es'], a.es_voice, a.slow)
        en_s = clip_path(r['sentence_en'], a.en_voice, '+0%')
        es_full = clip_path(r['sentence_es'], a.es_voice, '+0%')

        entry = {'r': int(r['rank'])}
        entry['verb'] = [put(es_v), dur(es_v)]
        put(g_verb); put(es_v); put(g_short)
        entry['verbEn'] = [put(en_v), dur(en_v)]
        put(g_short)
        entry['slow'] = [put(es_slow), dur(es_slow)]
        put(g_rep)
        entry['en'] = [put(en_s), dur(en_s)]
        put(g_two)
        entry['full'] = [put(es_full), dur(es_full)]
        put(g_item)
        entry['end'] = round(t, 3)
        index.append(entry)

    json.dump(_durs, open(DURCACHE, 'w'))

    stem = f"verbos_{a.start:04d}-{a.end:04d}"
    listfile = os.path.join(ROOT, 'audio', '.concat.txt')
    with open(listfile, 'w', encoding='utf-8') as fh:
        for p in seq:
            fh.write("file '" + p.replace("'", r"'\''") + "'\n")

    out = os.path.join(a.outdir, stem + '.mp3')
    # VBR, not CBR: about two thirds of this track is deliberate silence, which at a
    # constant bitrate costs exactly as much to store as speech. VBR makes it nearly free.
    subprocess.run(
        ['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', listfile,
         '-c:a', 'libmp3lame', '-q:a', '6', '-ar', '24000', '-ac', '1',
         '-metadata', f'title=Verbos {a.start}-{a.end}',
         '-metadata', 'artist=2000 Verbos', out],
        check=True)
    os.remove(listfile)

    real = float(subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', out], capture_output=True, text=True).stdout.strip() or 0)

    json.dump({'stem': stem, 'start': a.start, 'end': a.end,
               'duration': round(real, 3), 'voice': a.es_voice,
               'sentences': index},
              open(os.path.join(a.outdir, stem + '.json'), 'w'),
              ensure_ascii=False, separators=(',', ':'))

    drift = real - t
    print(f"\n{out}\n{real/60:.0f} min | {os.path.getsize(out)/1e6:.1f} MB "
          f"| {real/len(rows):.0f}s per sentence | index drift {drift:+.3f}s")
    if abs(drift) > 0.5:
        print("WARNING: index drift over 0.5s - seeking will be noticeably off")

asyncio.run(main())
