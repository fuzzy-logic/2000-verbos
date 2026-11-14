"""Minimal English morphology, for glossing each row of a conjugation table.

Only what the table needs: base, 3rd singular, -ing, past and past participle.
Irregulars are a closed list; everything else takes the regular rules.
"""
import re

# base: (past, past participle). Participle omitted means it equals the past.
IRREGULAR = {
    'be': ('was', 'been'), 'have': ('had',), 'do': ('did', 'done'),
    'say': ('said',), 'go': ('went', 'gone'), 'see': ('saw', 'seen'),
    'give': ('gave', 'given'), 'know': ('knew', 'known'), 'come': ('came', 'come'),
    'think': ('thought',), 'take': ('took', 'taken'), 'find': ('found',),
    'leave': ('left',), 'put': ('put',), 'get': ('got', 'got'),
    'make': ('made',), 'speak': ('spoke', 'spoken'), 'write': ('wrote', 'written'),
    'lose': ('lost',), 'understand': ('understood',), 'hear': ('heard',),
    'feel': ('felt',), 'buy': ('bought',), 'bring': ('brought',),
    'pay': ('paid',), 'send': ('sent',), 'sleep': ('slept',),
    'drink': ('drank', 'drunk'), 'eat': ('ate', 'eaten'), 'run': ('ran', 'run'),
    'win': ('won',), 'keep': ('kept',), 'hold': ('held',),
    'break': ('broke', 'broken'), 'choose': ('chose', 'chosen'),
    'forget': ('forgot', 'forgotten'), 'meet': ('met',), 'read': ('read',),
    'sell': ('sold',), 'sit': ('sat',), 'stand': ('stood',),
    'teach': ('taught',), 'tell': ('told',), 'wear': ('wore', 'worn'),
    'begin': ('began', 'begun'), 'build': ('built',), 'catch': ('caught',),
    'cost': ('cost',), 'cut': ('cut',), 'draw': ('drew', 'drawn'),
    'drive': ('drove', 'driven'), 'fall': ('fell', 'fallen'),
    'fight': ('fought',), 'fly': ('flew', 'flown'),
    'forgive': ('forgave', 'forgiven'), 'grow': ('grew', 'grown'),
    'hide': ('hid', 'hidden'), 'hurt': ('hurt',), 'lend': ('lent',),
    'let': ('let',), 'lie': ('lay', 'lain'), 'light': ('lit',),
    'mean': ('meant',), 'ride': ('rode', 'ridden'), 'ring': ('rang', 'rung'),
    'rise': ('rose', 'risen'), 'seek': ('sought',), 'shake': ('shook', 'shaken'),
    'shine': ('shone',), 'shoot': ('shot',), 'show': ('showed', 'shown'),
    'shut': ('shut',), 'sing': ('sang', 'sung'), 'sink': ('sank', 'sunk'),
    'spend': ('spent',), 'spread': ('spread',), 'swim': ('swam', 'swum'),
    'throw': ('threw', 'thrown'), 'wake': ('woke', 'woken'),
    'become': ('became', 'become'), 'bear': ('bore', 'borne'),
    'bet': ('bet',), 'bite': ('bit', 'bitten'), 'blow': ('blew', 'blown'),
    'deal': ('dealt',), 'dig': ('dug',), 'feed': ('fed',),
    'flee': ('fled',), 'freeze': ('froze', 'frozen'), 'hang': ('hung',),
    'lay': ('laid',), 'lead': ('led',), 'mistake': ('mistook', 'mistaken'),
    'overcome': ('overcame', 'overcome'), 'quit': ('quit',), 'rid': ('rid',),
    'set': ('set',), 'shed': ('shed',), 'slide': ('slid',),
    'split': ('split',), 'strike': ('struck',), 'swear': ('swore', 'sworn'),
    'sweep': ('swept',), 'tear': ('tore', 'torn'), 'wet': ('wet',),
    'wind': ('wound',), 'withdraw': ('withdrew', 'withdrawn'),
    'arise': ('arose', 'arisen'), 'awake': ('awoke', 'awoken'),
    'hit': ('hit',), 'burst': ('burst',), 'cast': ('cast',),
    'creep': ('crept',), 'kneel': ('knelt',), 'lean': ('leant',),
    'leap': ('leapt',), 'learn': ('learnt',), 'spill': ('spilt',),
    'spoil': ('spoilt',), 'stick': ('stuck',), 'sting': ('stung',),
    'strive': ('strove', 'striven'), 'undergo': ('underwent', 'undergone'),
    'undertake': ('undertook', 'undertaken'), 'uphold': ('upheld',),
    'weep': ('wept',), 'withhold': ('withheld',),
    'forbid': ('forbade', 'forbidden'), 'forgo': ('forwent', 'forgone'),
    'mislead': ('misled',), 'oversee': ('oversaw', 'overseen'),
    'foresee': ('foresaw', 'foreseen'), 'rewrite': ('rewrote', 'rewritten'),
    'swell': ('swelled', 'swollen'), 'weave': ('wove', 'woven'),
}
# Two-syllable verbs stressed on the final syllable, which therefore double
# their last consonant: admit -> admitted, against visit -> visited. Spelling
# alone cannot tell these apart, so they are listed.
DOUBLE = set("""admit permit commit submit omit transmit emit acquit occur
    refer prefer transfer infer confer deter incur concur control patrol
    compel rebel repel expel propel impel excel regret forget upset equip
    kidnap outfit begin fulfil instil enrol annul rebut allot""".split())
VOWELS = 'aeiou'
# never doubled, and -w -x -y never double either
NO_DOUBLE = set('wxy')


def split_gloss(verb_en):
    """'to know (people/places)' -> ('know', ''); 'to look for' -> ('look', 'for')."""
    g = re.sub(r'\([^)]*\)', '', verb_en)      # drop parentheticals FIRST,
    g = g.split('/')[0]                        # or the slash inside them splits
    g = re.sub(r'^\s*to\s+', '', g.strip()).strip(' .,')
    if not g:
        return '', ''
    parts = g.split()
    return parts[0], ' '.join(parts[1:])


def _double(base):
    """run -> running, but visit -> visiting (the stress is not on -sit)."""
    if len(base) < 3 or base[-1] in NO_DOUBLE:
        return False
    if base in DOUBLE:
        return True
    # British English doubles a final -l after a single vowel whatever the
    # stress: travel -> travelled, cancel -> cancelled
    if (base.endswith('l') and len(base) > 2 and base[-2] in VOWELS
            and base[-3] not in VOWELS):
        return True
    if base[-1] in VOWELS or base[-2] not in VOWELS or base[-3] in VOWELS:
        return False
    return len(re.findall(r'[aeiouy]+', base)) == 1      # single syllable only


def third(base):
    if base == 'be':
        return 'is'
    if base == 'have':
        return 'has'
    if base == 'do':
        return 'does'
    if base == 'go':
        return 'goes'
    if base.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return base + 'es'
    if base.endswith('y') and base[-2:-1] not in VOWELS:
        return base[:-1] + 'ies'
    return base + 's'


def ing(base):
    if base == 'be':
        return 'being'
    if base.endswith('ie'):
        return base[:-2] + 'ying'               # lie -> lying
    if base.endswith('e') and not base.endswith(('ee', 'oe', 'ye')):
        return base[:-1] + 'ing'
    if _double(base):
        return base + base[-1] + 'ing'
    return base + 'ing'


def past(base):
    if base in IRREGULAR:
        return IRREGULAR[base][0]
    if base.endswith('e'):
        return base + 'd'
    if base.endswith('y') and base[-2:-1] not in VOWELS:
        return base[:-1] + 'ied'
    if _double(base):
        return base + base[-1] + 'ed'
    return base + 'ed'


def participle(base):
    if base in IRREGULAR:
        f = IRREGULAR[base]
        return f[1] if len(f) > 1 else f[0]
    return past(base)


# "I be" is not English. Only `be` has distinct person forms in the present,
# and it is the gloss of ser, estar, and every "to be able/worth/born" phrase,
# so it is worth the special case.
BE = {'1s': 'am', '2s': 'are', '1p': 'are', '3p': 'are'}


def person(base, slot):
    return BE[slot] if base == 'be' else base


def parts(verb_en):
    """-> dict of the forms needed to gloss a conjugation table."""
    base, rest = split_gloss(verb_en)
    if not base:
        return None
    tail = (' ' + rest) if rest else ''
    return {'base': base + tail, 'third': third(base) + tail,
            'ing': ing(base) + tail, 'past': past(base) + tail,
            'part': participle(base) + tail,
            'p1s': person(base, '1s') + tail, 'p2s': person(base, '2s') + tail,
            'p1p': person(base, '1p') + tail, 'p3p': person(base, '3p') + tail}
