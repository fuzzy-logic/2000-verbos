"""Respell Spanish as a pronunciation hint for an English reader.

Spanish spelling is almost perfectly phonetic, so this is deterministic:
syllabify, find the stress, then map each syllable. Paraguayan values -
seseo (c before e/i and z both sound s), v read as b, and no yeismo, so ll
and y are kept apart as "ly" and "y".
"""
import re
import unicodedata

STRONG = set('aeoáéó')
WEAK = set('iuü')
# an accent on a weak vowel breaks the diphthong (te-ní-a). The dieresis does
# not: it only cancels the silence of u after g, leaving an ordinary glide.
WEAK_ACC = set('íú')
VOWELS = STRONG | WEAK | WEAK_ACC
ACCENTED = set('áéíóú')
# consonant + l/r that never splits across a syllable boundary
CLUSTERS = {'bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr', 'kl', 'kr',
            'pl', 'pr', 'tr', 'tl'}
DIGRAPHS = {'ch', 'll', 'rr', 'qu', 'gu'}


def _plain(c):
    return unicodedata.normalize('NFD', c)[0]


def nuclei(word):
    """Vowel-group spans, splitting hiatus: le-er, te-ni-a, but tie, rui."""
    out, i = [], 0
    while i < len(word):
        if word[i] not in VOWELS:
            i += 1
            continue
        if word[i] == 'u' and i > 0 and word[i - 1] in 'qg':
            i += 1                       # silent or glided: que, gui, gua
            continue
        j = i + 1
        while j < len(word) and word[j] in VOWELS:
            a, b = word[j - 1], word[j]
            # an accented weak vowel always breaks: te-ní-a, pa-ís
            if a in WEAK_ACC or b in WEAK_ACC:
                break
            # two strong vowels are separate syllables: le-er, ca-os
            if a in STRONG and b in STRONG:
                break
            j += 1
        out.append((i, j))
        i = j
    return out


def syllables(word):
    """Split one lowercase word into syllables."""
    nu = nuclei(word)
    if not nu:
        return [word]
    cuts = []
    for k in range(len(nu) - 1):
        a, b = nu[k][1], nu[k + 1][0]
        cons = word[a:b]
        n = len(cons)
        if n == 0:
            cut = a
        elif n == 1:
            cut = a
        else:
            pair = cons[-2:]
            # qu/gu belong to the following vowel, as one unit with it
            if pair in DIGRAPHS or pair in CLUSTERS:
                cut = b - 2
            else:
                cut = b - 1
            if cut <= nu[k][0]:
                cut = a
        cuts.append(cut)
    parts, prev = [], 0
    for c in cuts:
        parts.append(word[prev:c])
        prev = c
    parts.append(word[prev:])
    return [p for p in parts if p]


def stress_index(word, syls):
    """Which syllable carries the stress."""
    for i, s in enumerate(syls):
        if any(c in ACCENTED for c in s):
            return i
    if len(syls) == 1:
        return 0
    last = word[-1]
    # a word ending in a vowel, n or s is stressed on the penultimate
    return len(syls) - 2 if (last in VOWELS or last in 'ns') else len(syls) - 1


# open syllables get a long cue, closed ones the bare letter: TEN-goh, teh-NEH
OPEN_V = {'a': 'ah', 'e': 'eh', 'i': 'ee', 'o': 'oh', 'u': 'oo'}
GLIDE_IN = {'i': 'ee', 'u': 'oo'}        # rising: tie -> tee-EH
GLIDE_OUT = {'i': 'y', 'u': 'w'}         # falling: hay -> ahy
# single consonants, where the value does not depend on what follows
CONS1 = {'z': 's', 'j': 'h', 'v': 'b', 'h': '', 'ñ': 'ny', 'x': 'ks',
         'q': 'k', 'b': 'b', 'w': 'w'}


def _onset(onset, nxt):
    """Map the consonants before the nucleus. `nxt` is the nucleus letter."""
    out, i = '', 0
    while i < len(onset):
        two = onset[i:i + 2]
        after = onset[i + 2] if i + 2 < len(onset) else nxt
        if two == 'll':
            out, i = out + 'ly', i + 2
        elif two == 'ch':
            out, i = out + 'ch', i + 2
        elif two == 'rr':
            out, i = out + 'rr', i + 2
        elif two == 'qu':
            out, i = out + 'k', i + 2
        elif two in ('gu', 'gü'):
            # silent before e/i (guerra), a glide before a/o (guaraní)
            out, i = out + ('g' if (two == 'gu' and after in 'eiéí') else 'gw'), i + 2
        else:
            c = onset[i]
            after1 = onset[i + 1] if i + 1 < len(onset) else nxt
            if c == 'c':
                out += 's' if after1 in 'eiéí' else 'k'
            elif c == 'g':
                out += 'h' if after1 in 'eiéí' else 'g'
            else:
                out += CONS1.get(c, c)
            i += 1
    return out


def _coda(coda):
    return ''.join(CONS1.get(c, c) if c in CONS1 else c
                   for c in coda).replace('ks', 'ks')


# Guaraní, not Spanish. Its vowels and the glottal stop do not exist in
# Spanish orthography, and Spanish rules mangle the words that carry them
# (Iporã, Mba'éichapa). Left exactly as written.
GUARANI = set('ãẽĩõũỹ') | set("'’ʼ")
# x between vowels is [ks] and splits across the syllable break: ek-SAH-men,
# not eh-KSAH-men. Rewriting it before syllabifying gets the break right.
_XV = re.compile(r'(?<=[aeiouáéíóú])x(?=[aeiouáéíóú])')
# Mexican x is an h-sound. Respelling it as j routes it through the normal map.
MEX = {'méxico': 'méjico', 'mexico': 'méjico', 'mexicano': 'mejicano',
       'mexicana': 'mejicana', 'mexicanos': 'mejicanos', 'mexicanas': 'mejicanas'}


def say(word, stressed=True):
    """Respell one word. stressed=False renders it without emphasis."""
    w = word.lower()
    if any(c in GUARANI for c in w):
        return word
    # the conjunction y is the vowel [i]; y is not in the vowel table
    if w == 'y':
        return 'ee' if stressed else 'ee'
    w = MEX.get(w, w)
    w = _XV.sub('ks', w)
    if not any(c in VOWELS for c in w):
        return w
    syls = syllables(w)
    si = stress_index(w, syls)
    out = []
    for i, syl in enumerate(syls):
        nu = nuclei(syl)
        if not nu:
            out.append(_onset(syl, ''))
            continue
        a, b = nu[0]
        onset, group, coda = syl[:a], syl[a:b], _coda(syl[b:])
        plain = [_plain(c) for c in group]
        head = _onset(onset, plain[0])
        glide = ''
        if len(plain) > 1 and plain[0] in 'iu' and plain[1] in 'aeo':
            glide, core = GLIDE_IN[plain[0]], plain[1]
        elif len(plain) > 1 and plain[0] in 'aeo' and plain[1] in 'iu':
            glide, core = '', plain[0]
            coda = GLIDE_OUT[plain[1]] + coda
        elif len(plain) > 1:
            glide, core = GLIDE_IN[plain[0]], plain[1]
        else:
            core = plain[0]
        # a closed syllable takes the bare vowel letter: TEN, not TEHN
        body = core if coda else OPEN_V[core]
        tail = body + coda
        if i == si and stressed:
            # a rising glide stays quiet so the nucleus stands out: tee-EH
            tail = tail.upper()
            if not glide:
                head = head.upper()
        out.append(head + glide + ('-' if glide else '') + tail)
    return '-'.join(x for x in out if x)


def phrase(text):
    """Respell a whole form, which may be several words: 'he tenido'."""
    words = re.findall(r"[^\s]+", text)
    if len(words) == 1:
        return say(words[0])
    # in a multi-word form the last word carries the phrase stress
    return ' '.join(say(w, stressed=(i == len(words) - 1))
                    for i, w in enumerate(words))


# Grammatical words, which lean on the word beside them instead of carrying a
# stress of their own. Accents keep the pairs apart by themselves: el/él,
# que/qué, si/sí, tu/tú, mi/mí, se/sé, de/dé, mas/más - only the unaccented
# member is listed, so the accented one stays stressed.
UNSTRESSED = {
    'el', 'la', 'los', 'las', 'lo', 'un', 'una', 'unos', 'unas', 'al', 'del',
    'a', 'ante', 'bajo', 'con', 'contra', 'de', 'desde', 'durante', 'en',
    'entre', 'hacia', 'hasta', 'para', 'por', 'según', 'sin', 'sobre', 'tras',
    'y', 'e', 'o', 'u', 'ni', 'que', 'si', 'como', 'cuando', 'donde', 'porque',
    'aunque', 'mientras', 'pues',
    'me', 'te', 'se', 'nos', 'os', 'le', 'les',
    'mi', 'mis', 'tu', 'tus', 'su', 'sus', 'nuestro', 'nuestra', 'cada',
}
WORD_RE = re.compile(r"[^\W\d_]+(?:['’ʼ][^\W\d_]+)*", re.UNICODE)


def sentence(text):
    """Respell a whole sentence, keeping its punctuation where it was.

    Three things separate this from phrase(), which exists for conjugated
    forms and is wrong for prose:

    - Punctuation is held aside rather than carried into the word. phrase()
      splits on whitespace, so the token is «punto.», which ends in a
      consonant and therefore takes final stress by rule - pun-TO, not
      PUN-toh.
    - Every word gets its own stress, not only the last one.
    - Grammatical words, and every word of one syllable, are left unmarked.
      The capitals say WHICH syllable is stressed, so on a word that has only
      one they add nothing and cost a lot of quiet.
    """
    out, last = [], 0
    for m in WORD_RE.finditer(text):
        out.append(text[last:m.start()])
        w = m.group(0)
        lower = w.lower()
        mark = lower not in UNSTRESSED and len(syllables(lower)) > 1
        out.append(say(w, stressed=mark))
        last = m.end()
    out.append(text[last:])
    return ''.join(out)
