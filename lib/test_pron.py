"""Checks for the respeller. Run: python3 lib/test_pron.py

Spanish spelling is almost perfectly phonetic, so every one of these is a
fact, not a judgement call - except where the respelling style itself makes a
choice (open syllables take a long cue: TEN-goh but teh-NEH), and those are
grouped under style().

One case per behaviour the engine has to get right, not one per word.
"""
import csv
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pron import say, sentence, syllables, stress_index  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WORDS = {
    # --- the three stress classes
    'hablo': 'AH-bloh',            # vowel-final: penultimate
    'hablar': 'ah-BLAR',           # consonant-final: last
    'hablás': 'ah-BLAS',           # written accent wins
    'joven': 'HOH-ben',            # n-final: penultimate
    'jóvenes': 'HOH-beh-nes',      # accent wins over the n rule
    'crisis': 'KREE-sis',          # s-final: penultimate
    'reloj': 'reh-LOH',            # j-final: last
    'árbol': 'AR-bol',             # accent on the antepenult-by-rule
    'teléfono': 'teh-LEH-foh-noh',
    # say() always marks; it is sentence() that leaves one-syllable words
    # alone, which the sentence cases below cover.
    'sol': 'SOL',
    'soy': 'SOY',
    # --- diphthong and hiatus
    'tiene': 'tee-EH-neh',         # rising glide
    'cuando': 'koo-AN-doh',
    'hay': 'AY',                   # falling glide
    'veinte': 'BEYN-teh',
    'leer': 'leh-ER',              # two strong vowels break
    'tenía': 'teh-NEE-ah',         # accented weak vowel breaks
    'país': 'pah-IS',          # closed syllable takes the bare letter
    'reír': 'reh-IR',
    'construir': 'kons-troo-IR',
    'oí': 'oh-EE',
    # --- the Paraguayan values
    'calle': 'KAH-lyeh',           # no yeismo: ll is not y
    'yo': 'YOH',
    'cien': 'see-EN',              # seseo: c before e/i is s
    'zapato': 'sah-PAH-toh',       # seseo: z is s
    'vivir': 'bee-BIR',            # v read as b
    'vergüenza': 'ber-goo-EN-sah',
    'bicicleta': 'bee-see-KLEH-tah',
    # --- spelling rules
    'que': 'KEH',                  # qu is k, the u silent
    'guerra': 'GEH-rrah',          # gu before e: g, u silent
    'guaraní': 'gwah-rah-NEE',     # gu before a: gw
    'pingüino': 'pin-goo-EE-noh',  # dieresis restores the u it would silence
    'hola': 'OH-lah',              # h is silent
    'ahora': 'ah-OH-rah',
    'gente': 'HEN-teh',            # g before e: h
    'gato': 'GAH-toh',
    'jugá': 'hoo-GAH',             # j is h
    'ñandutí': 'nyan-doo-TEE',     # ñ is ny
    'perro': 'PEH-rroh',           # rr held
    'extranjero': 'eks-tran-HEH-roh',
    'examen': 'ek-SAH-men',        # x between vowels splits: ek-SAH, not eh-KSAH
    'taxi': 'TAK-see',
    'méxico': 'MEH-hee-koh',       # Mexican x is an h-sound
    # --- enclitics drag the stress along
    'perdoname': 'per-doh-NAH-meh',
    'decime': 'deh-SEE-meh',
    'dámelo': 'DAH-meh-loh',
    # --- y is the vowel [i], and is not in the vowel table
    'y': 'ee',
    # --- Guarani is left exactly as written
    'Iporã': 'Iporã',
    "Mba'éichapa": "Mba'éichapa",
}

SENTENCES = {
    # punctuation is held aside, not carried into the word
    'Almorzamos a mediodía en punto.':
        'al-mor-SAH-mos ah meh-dee-oh-DEE-ah en PUN-toh.',
    'Lleva una camisa blanca.':
        'LYEH-bah oo-nah kah-MEE-sah BLAN-kah.',
    # opening marks stay where they were
    '¿Cenamos afuera esta noche?':
        '¿seh-NAH-mos ah-foo-EH-rah ES-tah NOH-cheh?',
    # commas, and an enclitic command
    'No pude venir, perdoname.':
        'noh POO-deh beh-NIR, per-doh-NAH-meh.',
    # every word carries its own stress, not just the last
    'Soy de Inglaterra pero ahora vivo acá.':
        'soy deh in-glah-TEH-rrah PEH-roh ah-OH-rah BEE-boh ah-KAH.',
    # grammatical words stay unmarked; content words do not
    'Hay que beber mucha agua acá.':
        'ay keh beh-BER MOO-chah AH-gwah ah-KAH.',
    'Encendé el ventilador, por favor.':
        'en-sen-DEH el ben-tee-lah-DOR, por fah-BOR.',
    # a Guarani word sitting inside a Spanish sentence is left alone
    'Tomamos tereré con Iporã.':
        'toh-MAH-mos teh-reh-REH kon Iporã.',
    # digits are passed through rather than half-expanded
    'Hay 20 personas.':
        'ay 20 per-SOH-nas.',
}

# Accent pairs where the plain word is grammatical and the accented one is
# not. Only polysyllables can show this: el and él are the same sounds, and
# one syllable is left unmarked either way, so the pair cannot be told apart
# in a respelling - correctly, since there is nothing to tell apart.
PAIRS = [('como', 'cómo'), ('cuando', 'cuándo'), ('donde', 'dónde'),
         ('porque', 'porqué')]


def words():
    bad = 0
    for w, want in WORDS.items():
        got = say(w)
        if got != want:
            print(f'  {w:16s} want {want:22s} got {got}')
            bad += 1
    return bad, len(WORDS)


def sentences():
    bad = 0
    for s, want in SENTENCES.items():
        got = sentence(s)
        if got != want:
            print(f'  {s}\n      want {want}\n      got  {got}')
            bad += 1
    return bad, len(SENTENCES)


def pairs():
    """The accented member carries a stress mark in a sentence; the plain
    member, being grammatical, does not."""
    bad = 0
    for plain, accented in PAIRS:
        flat = sentence(f'Es {plain} parece.').split()[1]
        marked = sentence(f'Es {accented} parece.').split()[1]
        if any(c.isupper() for c in flat):
            print(f'  {plain!r} should be unmarked, got {flat}')
            bad += 1
        if not any(c.isupper() for c in marked):
            print(f'  {accented!r} should be marked, got {marked}')
            bad += 1
    return bad, len(PAIRS) * 2


def corpus():
    """Nothing in the corpus may crash the respeller or come back empty."""
    texts = []
    for p in sorted(glob.glob(os.path.join(ROOT, 'data', 'verbs_*.tsv'))):
        with open(p, encoding='utf-8') as fh:
            texts += [r['sentence_es'] for r in csv.DictReader(fh, delimiter='\t')]
    extra = os.path.join(ROOT, 'data', 'sentences_extra.tsv')
    if os.path.exists(extra):
        with open(extra, encoding='utf-8') as fh:
            texts += [r['sentence_es'] for r in csv.DictReader(fh, delimiter='\t')
                      if r.get('sentence_es')]
    bad = 0
    for t in texts:
        try:
            got = sentence(t)
        except Exception as e:                                  # noqa: BLE001
            print(f'  {t[:50]!r} raised {e}')
            bad += 1
            continue
        if not got.strip():
            print(f'  {t[:50]!r} respelled to nothing')
            bad += 1
        # the respelling must keep the sentence's punctuation
        for mark in '¿?¡!.,':
            if t.count(mark) != got.count(mark):
                print(f'  {t[:50]!r} lost {mark!r}: {got[:50]!r}')
                bad += 1
                break
    return bad, len(texts)


def syllable_sanity():
    """Syllables must concatenate back to the word, and the stress must exist."""
    words_seen = set()
    for p in sorted(glob.glob(os.path.join(ROOT, 'data', 'verbs_*.tsv'))):
        with open(p, encoding='utf-8') as fh:
            for r in csv.DictReader(fh, delimiter='\t'):
                words_seen.add(r['verb_es'].split()[0])
    bad = 0
    for w in sorted(words_seen):
        syls = syllables(w)
        if ''.join(syls) != w:
            print(f'  {w}: syllables {syls} do not rejoin')
            bad += 1
            continue
        si = stress_index(w, syls)
        if not 0 <= si < len(syls):
            print(f'  {w}: stress index {si} outside {len(syls)} syllables')
            bad += 1
    return bad, len(words_seen)


if __name__ == '__main__':
    total = 0
    for name, fn in (('hand-checked words', words),
                     ('hand-checked sentences', sentences),
                     ('accent pairs', pairs),
                     ('syllables rejoin', syllable_sanity),
                     ('whole corpus', corpus)):
        n_bad, n = fn()
        total += n_bad
        print(f'{"FAIL" if n_bad else "ok  "}  {name}: {n - n_bad}/{n}')
    sys.exit(1 if total else 0)
