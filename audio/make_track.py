#!/usr/bin/env python3
"""
Build walking-track MP3s from data/*.tsv using edge-tts (Paraguayan Spanish).

Per sentence the track plays:
    verb (es)  ...3s...  verb (es)  ...  verb (en)
    sentence (es, slow)  ...7s to repeat it yourself...
    sentence (en)        ...2s...
    sentence (es, full speed)
    ...gap...  next

Clips are cached in audio/clips/ so re-runs only synthesise what changed.

    python3 audio/make_track.py --start 1 --end 200
"""
import argparse, asyncio, csv, glob, hashlib, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS = os.path.join(ROOT, 'audio', 'clips')
SIL = os.path.join(ROOT, 'audio', 'silence')

try:
    import edge_tts
except ImportError:
    sys.exit("edge-tts is not installed. Run:\n"
             "  python3 -m venv .venv && .venv/bin/pip install edge-tts\n"
             "then use .venv/bin/python3 audio/make_track.py")


def load_rows():
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'data', '*.tsv'))):
        with open(path, encoding='utf-8') as fh:
            for r in csv.DictReader(fh, delimiter='\t'):
                rows.append(r)
    rows.sort(key=lambda r: int(r['rank']))
    return rows


def clip_path(text, voice, rate):
    key = hashlib.sha1(f"{voice}|{rate}|{text}".encode()).hexdigest()[:16]
    return os.path.join(CLIPS, f"{key}.mp3")


async def synth(text, voice, rate, sem, retries=4):
    """Synthesise one clip, cached. edge-tts throttles, so retry with backoff."""
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
         '-c:a', 'libmp3lame', '-b:a', '64k', '-ar', '24000', '-ac', '1', dest],
        check=True)


def silence(seconds):
    """Pre-render a silence clip matching edge-tts output (24kHz mono)."""
    dest = os.path.join(SIL, f"{seconds:.1f}.mp3")
    if not os.path.exists(dest):
        subprocess.run(
            ['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi',
             '-i', 'anullsrc=r=24000:cl=mono', '-t', str(seconds),
             '-c:a', 'libmp3lame', '-b:a', '48k', dest],
            check=True)
    return dest


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', type=int, default=1)
    ap.add_argument('--end', type=int, default=200)
    ap.add_argument('--es-voice', default='es-PY-TaniaNeural')
    ap.add_argument('--en-voice', default='en-GB-SoniaNeural')
    ap.add_argument('--slow', default='-35%', help='rate for the slow Spanish pass')
    ap.add_argument('--repeat-gap', type=float, default=7.0)
    ap.add_argument('--verb-gap', type=float, default=3.0)
    ap.add_argument('--item-gap', type=float, default=2.5)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    os.makedirs(CLIPS, exist_ok=True)
    os.makedirs(SIL, exist_ok=True)

    rows = [r for r in load_rows() if a.start <= int(r['rank']) <= a.end]
    if not rows:
        sys.exit(f"no rows in range {a.start}-{a.end}")

    # Every distinct (text, voice, rate) clip this track needs.
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

    todo = [j for j in jobs if not os.path.exists(clip_path(*j))]
    print(f"{len(rows)} sentences · {len(jobs)} clips ({len(todo)} to synthesise)")

    sem = asyncio.Semaphore(6)
    done = 0
    tasks = [asyncio.create_task(synth(t, v, rt, sem)) for t, v, rt in jobs]
    for fut in asyncio.as_completed(tasks):
        await fut
        done += 1
        if done % 25 == 0 or done == len(tasks):
            print(f"  {done}/{len(tasks)} clips", flush=True)

    g_verb = silence(a.verb_gap)
    g_rep = silence(a.repeat_gap)
    g_item = silence(a.item_gap)
    g_short = silence(1.2)
    g_two = silence(2.0)

    seq = []
    for r in rows:
        seq += [
            clip_path(r['verb_es'], a.es_voice, '+0%'), g_verb,
            clip_path(r['verb_es'], a.es_voice, '+0%'), g_short,
            clip_path(r['verb_en'], a.en_voice, '+0%'), g_short,
            clip_path(r['sentence_es'], a.es_voice, a.slow), g_rep,
            clip_path(r['sentence_en'], a.en_voice, '+0%'), g_two,
            clip_path(r['sentence_es'], a.es_voice, '+0%'), g_item,
        ]

    listfile = os.path.join(ROOT, 'audio', '.concat.txt')
    with open(listfile, 'w', encoding='utf-8') as fh:
        for p in seq:
            fh.write("file '" + p.replace("'", r"'\''") + "'\n")

    out = a.out or os.path.join(ROOT, 'audio', f"verbos_{a.start:04d}-{a.end:04d}.mp3")
    subprocess.run(
        ['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', listfile,
         '-c:a', 'libmp3lame', '-b:a', '64k', '-ar', '24000', '-ac', '1',
         '-metadata', f'title=Verbos {a.start}-{a.end}',
         '-metadata', 'artist=2000 Verbos', out],
        check=True)
    os.remove(listfile)

    dur = float(subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', out], capture_output=True, text=True).stdout.strip() or 0)
    print(f"\n{out}\n{dur/60:.0f} min · {os.path.getsize(out)/1e6:.1f} MB "
          f"· {dur/len(rows):.0f}s per sentence")

asyncio.run(main())
