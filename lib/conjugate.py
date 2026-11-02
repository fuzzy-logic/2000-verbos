"""Spanish conjugation for Paraguayan voseo.

Generates the forms the app needs from an infinitive. Rules do the regular
work; two curated tables carry what no rule can predict - which verbs change
their stem, and which are genuinely irregular. Prefixed derivatives inherit
from their base verb (detener from tener), which is how 182 of the 2000 verbs
get their conjugation for free.

Slots are banded by CEFR level so the app can show A1 only and raise the
ceiling later without a rebuild.
"""

VOWELS = 'aeiou'
ACCENT = {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú'}
UNACCENT = {v: k for k, v in ACCENT.items()}

# Slot -> (level, label, english template). Order here is display order.
SLOTS = [
    ('pres-1s',     'A1', 'yo',                 'I {p1s}'),
    ('pres-2s',     'A1', 'vos',                'you {p2s}'),
    ('pres-2s-tu',  'A1', 'tú',                 'you {p2s}'),
    ('pres-3s',     'A1', 'usted / él / ella',  'you / he / she {third}'),
    ('pres-1p',     'A1', 'nosotros',           'we {p1p}'),
    ('pres-3p',     'A1', 'ustedes / ellos',    'you all / they {p3p}'),
    ('cmd-vos',     'A1', 'command (vos)',      '{base}!'),
    ('going-1s',    'A1', 'going to',           "I'm going to {base}"),
    ('ger',         'A1', '-ing',               '{ing}'),
    ('pret-1s',     'A2', 'preterite (yo)',     'I {past} (once)'),
    ('imp-1s',      'A2', 'imperfect (yo)',     'I used to {base}'),
    ('perf-1s',     'A2', 'perfect (yo)',       'I have {part}'),
    ('cmd-vos-neg', 'A2', 'negative command',   "don't {base}"),
    ('fut-1s',      'B1', 'future (yo)',        'I will {base}'),
    ('cond-1s',     'B1', 'conditional (yo)',   'I would {base}'),
    ('subj-1s',     'B1', 'subjunctive (yo)',   '(that) I {p1s}'),
]
LEVELS = ['A1', 'A2', 'B1']          # B2/C1 slots reserved, not yet filled

# Verbs whose stem changes under stress. Values: the change, applied to the
# LAST stressable vowel of the stem. Unpredictable from spelling - curated.
STEM = {
    'ie': """acertar acordarse_X advertir alentar apretar arrendar ascender
        adherir adherirse arrepentirse atender atravesar calentar cegar cerrar
        comenzar concertar confesar sosegar tener venir
        consentir convertir defender descender despertar despertarse divertir
        divertirse empezar encender encerrar encomendar entender enterrar
        extender fregar gobernar helar herir hervir invertir manifestar mentir
        merendar negar nevar pensar perder preferir quebrar querer recomendar
        referir regar remendar sembrar sentar sentarse sentir sugerir temblar
        tender tentar transferir tropezar verter advertirse""",
    'ue': """absolver acordar acostar acostarse almorzar aprobar apostar
        avergonzar colar colgar comprobar concordar consolar contar costar
        demoler demostrar desaprobar descolgar descontar devolver disolver
        doler dormir encontrar envolver esforzarse forzar llover moler morder
        morir mostrar mover poblar poder probar promover recordar remover
        renovar resolver resonar revolver rodar rogar soler soltar sonar soñar
        tostar tronar volar volcar volver oler""",
    'i': """decir regir rendir rendirse competir concebir conseguir corregir
        derretir despedir despedirse
        elegir freír gemir impedir medir pedir perseguir reír reñir repetir
        seguir servir sonreír teñir vestir vestirse""",
    'ue-u': 'jugar',
}
# -iar verbs that accent the i under stress: envío, not *envio. Closed list;
# every other -iar verb is regular (cambio, estudio, limpio).
ACCENT_IAR = set("""enviar confiar desconfiar fiar vaciar enfriar resfriar guiar
    criar variar espiar ampliar liar desviar extraviar rociar averiar esquiar
    piar chirriar fotografiar telegrafiar contrariar ataviar expatriar
    repatriar aliar ampliar arriar""".split())
# Verbs that accent a u or i outside the -iar/-uar pattern.
ACCENT_OTHER = set('reunir rehusar prohibir aunar aislar reunirse'.split())

STEM_OF = {}
for _change, _list in STEM.items():
    for _v in _list.split():
        STEM_OF[_v.rstrip('_X')] = 'ue' if _change == 'ue-u' else _change

# Genuinely irregular verbs. Only the unpredictable parts are listed; every
# unlisted slot still comes from the rules. Prefixed verbs inherit these.
IRREG = {
    'ser': dict(pres=['soy', 'sos', 'eres', 'es', 'somos', 'son'],
                pret_stem='fu', pret=['fui', 'fuiste', 'fue', 'fuimos', 'fueron'],
                imperf=['era', 'eras', 'era', 'éramos', 'eran'],
                subj_stem='se', cmd='sé'),
    'estar': dict(pres=['estoy', 'estás', 'estás', 'está', 'estamos', 'están'],
                  pret_stem='estuv', subj=['esté', 'estés', 'estés', 'esté', 'estemos', 'estén']),
    'haber': dict(pres=['he', 'has', 'has', 'ha', 'hemos', 'han'],
                  pret_stem='hub', fut_stem='habr', subj_stem='hay', cmd='',
                  extra={'impersonal': 'hay'}),
    'ir': dict(pres=['voy', 'vas', 'vas', 'va', 'vamos', 'van'],
               pret=['fui', 'fuiste', 'fue', 'fuimos', 'fueron'],
               imperf=['iba', 'ibas', 'iba', 'íbamos', 'iban'],
               ger='yendo', subj_stem='vay', cmd='andá'),
    'tener': dict(yo='tengo', pret_stem='tuv', fut_stem='tendr'),
    'hacer': dict(yo='hago', pret_stem='hic', pret_3s='hizo', fut_stem='har', part='hecho'),
    'poder': dict(pret_stem='pud', fut_stem='podr', ger='pudiendo'),
    'decir': dict(yo='digo', pret_stem='dij', pret_3p='dijeron', fut_stem='dir',
                  part='dicho', ger='diciendo'),
    'ver': dict(pres=['veo', 'ves', 'ves', 've', 'vemos', 'ven'], cmd='ve', yo='veo',
                pret=['vi', 'viste', 'vio', 'vimos', 'vieron'],
                imperf=['veía', 'veías', 'veía', 'veíamos', 'veían'], part='visto'),
    'dar': dict(pres=['doy', 'das', 'das', 'da', 'damos', 'dan'], cmd='da',
                pret=['di', 'diste', 'dio', 'dimos', 'dieron'],
                subj=['dé', 'des', 'des', 'dé', 'demos', 'den']),
    'saber': dict(yo='sé', pret_stem='sup', fut_stem='sabr', subj_stem='sep'),
    'querer': dict(pret_stem='quis', fut_stem='querr'),
    'poner': dict(yo='pongo', pret_stem='pus', fut_stem='pondr', part='puesto'),
    'venir': dict(yo='vengo', pret_stem='vin', fut_stem='vendr', ger='viniendo'),
    'salir': dict(yo='salgo', fut_stem='saldr'),
    'traer': dict(yo='traigo', pret_stem='traj', pret_3p='trajeron', ger='trayendo'),
    'caer': dict(yo='caigo', ger='cayendo', pret_3s='cayó', pret_3p='cayeron'),
    'oír': dict(yo='oigo', pres_2s_tu='oyes', pres_3s='oye', pres_3p='oyen',
                ger='oyendo', pret_3s='oyó', pret_3p='oyeron'),
    'valer': dict(yo='valgo', fut_stem='valdr'),
    'caber': dict(yo='quepo', pret_stem='cup', fut_stem='cabr'),
    'andar': dict(pret_stem='anduv'),
    'escribir': dict(part='escrito'),
    'volver': dict(part='vuelto'),
    'morir': dict(part='muerto'),
    'romper': dict(part='roto'),
    'abrir': dict(part='abierto'),
    'cubrir': dict(part='cubierto'),
    'resolver': dict(part='resuelto'),
    'freír': dict(part='frito'),
    'imprimir': dict(part='impreso'),
    'conducir': dict(pret_stem='conduj', pret_3p='condujeron'),
    'reír': dict(pres=['río', 'reís', 'ríes', 'ríe', 'reímos', 'ríen'],
                 pret=['reí', 'reíste', 'rio', 'reímos', 'rieron'],
                 ger='riendo', part='reído', subj_stem='rí', cmd='reí'),
    'freír': dict(pres=['frío', 'freís', 'fríes', 'fríe', 'freímos', 'fríen'],
                  pret=['freí', 'freíste', 'frio', 'freímos', 'frieron'],
                  ger='friendo', part='frito', subj_stem='frí', cmd='freí'),
}

# Prefixed verbs that do NOT inherit their base verb's irregularity.
NO_INHERIT = {'compensar', 'contestar', 'prestar', 'molestar', 'protestar',
              'repasar', 'traspasar', 'retomar', 'contratar', 'exterminar',
              # look derived from a stem-changer but are regular. Note that
              # presentir IS e->ie: presiento (I sense) against presento
              # (I present) is a real pair, not a bug.
              'presentar', 'presentarse', 'representar', 'intentar',
              'pretender', 'conjugar', 'derogar', 'derogarse'}
# Prefixed verbs that inherit some of it but keep a regular future.
REGULAR_FUTURE = {'predecir', 'bendecir', 'maldecir'}
# bendecir/maldecir keep a regular participle in modern use: bendecido, not
# *bendicho (bendito survives only as an adjective).
REGULAR_PART = {'bendecir', 'maldecir'}


def strip_accents(w):
    return ''.join(UNACCENT.get(c, c) for c in w)


def _last_vowel_index(stem):
    for i in range(len(stem) - 1, -1, -1):
        if stem[i] in VOWELS:
            if stem[i] == 'u' and i > 0 and stem[i - 1] in 'gq':
                continue          # silent u: segu-ir changes the e, not the u
            return i
    return -1


def accent_syllable(word, target):
    """Write an accent on the vowel group containing index `target`."""
    i = target
    if i > 0 and word[i - 1] in 'iu' and word[i] in 'aeo':
        pass
    return word[:i] + ACCENT.get(word[i], word[i]) + word[i + 1:]


def base_of(inf, known, _depth=0):
    """The verb `inf` is derived from, if any: detener -> tener. Strips
    repeatedly, so indisponer finds poner through disponer."""
    for p in ('des', 'contra', 'entre', 'sobre', 'ante', 'tras', 'super',
              'con', 'com', 'pre', 'pro', 'per', 'pos', 'sos', 'sub', 'su', 'son',
              'ben', 'mal', 'dis', 'abs',
              're', 'de', 'ob', 'ex', 'en', 'in', 'im', 'a', 'man', 'co'):
        if inf.startswith(p) and len(inf) > len(p) + 3:
            cand = inf[len(p):]
            if cand in known:
                return p, cand
            if _depth < 2:
                p2, base = base_of(cand, known, _depth + 1)
                if base:
                    return p + p2, base
    return None, None


class Verb:
    def __init__(self, inf):
        self.given = inf
        self.reflexive = inf.endswith('se') and len(inf) >= 4 and inf[-3] == 'r'
        self.inf = inf[:-2] if self.reflexive else inf
        self.ending = self.inf[-2:]
        self.stem = self.inf[:-2]
        if self.ending not in ('ar', 'er', 'ir', 'ír'):
            raise ValueError(f'not an infinitive: {inf}')
        self.ar = self.ending == 'ar'
        self.er = self.ending == 'er'
        self.ir = self.ending in ('ir', 'ír')
        self.irr = self._irregular()
        self.change = STEM_OF.get(self.inf) or STEM_OF.get(inf)
        if not self.change and self.inf not in NO_INHERIT:
            _, _base = base_of(self.inf, STEM_OF)
            if _base:
                self.change = STEM_OF[_base]
        if not self.change and (
                self.inf in ACCENT_IAR or self.inf in ACCENT_OTHER
                or (self.inf.endswith('uar') and not self.inf.endswith('guar'))):
            self.change = 'accent'

    def _irregular(self):
        if self.inf in IRREG:
            return dict(IRREG[self.inf])
        if self.inf in NO_INHERIT:
            return {}
        pre, base = base_of(self.inf, IRREG)
        if not base:
            return {}
        d = {}
        for k, v in IRREG[base].items():
            if isinstance(v, str):
                d[k] = (pre + v if k.endswith('stem')
                        or k in ('yo', 'part', 'ger', 'cmd', 'pret_3s', 'pret_3p')
                        else v)
            elif isinstance(v, list):
                d[k] = [pre + x for x in v]
        if self.inf in REGULAR_FUTURE:
            d.pop('fut_stem', None)
        if self.inf in REGULAR_PART:
            d.pop('part', None)
        # inherited participles/gerunds keep the base's shape: compuesto, predicho
        return d

    # ---- stems -------------------------------------------------------

    def stressed_stem(self):
        """The stem as it appears under stress: pens- -> piens-."""
        if not self.change:
            return self.stem
        i = _last_vowel_index(self.stem)
        if i < 0:
            return self.stem
        v, ch = self.stem[i], self.change
        if ch == 'ie' and v == 'e':
            return self.stem[:i] + 'ie' + self.stem[i + 1:]
        if ch == 'ue' and v == 'o':
            return self.stem[:i] + 'ue' + self.stem[i + 1:]
        if ch == 'ue' and v == 'u':          # jugar -> juego
            return self.stem[:i] + 'ue' + self.stem[i + 1:]
        if ch == 'i' and v == 'e':
            return self.stem[:i] + 'i' + self.stem[i + 1:]
        if ch == 'accent':
            return self.stem[:i] + ACCENT[v] + self.stem[i + 1:]
        return self.stem

    def _h_rule(self, s):
        return 'h' + s if s.startswith('ue') else s

    def stressed(self):
        return self._h_rule(self.stressed_stem())

    def weak_stem(self):
        """-ir verbs raise e->i / o->u in the gerund and 3rd preterite."""
        i = _last_vowel_index(self.stem)
        if i < 0 or not self.ir or not self.change or self.change == 'accent':
            return self.stem
        v = self.stem[i]
        if v == 'e':
            return self.stem[:i] + 'i' + self.stem[i + 1:]
        if v == 'o':
            return self.stem[:i] + 'u' + self.stem[i + 1:]
        return self.stem

    def spell(self, s, before_e=False):
        """Spelling shifts a stem needs before the ending that follows it."""
        inf = self.inf
        if inf.endswith(('ger', 'gir')):
            return s[:-1] + 'j'
        if inf.endswith('guir'):
            return s[:-2] + 'g'
        if inf.endswith(('cer', 'cir')):
            return s[:-1] + ('zc' if s[-2:-1] in VOWELS else 'z')
        if inf.endswith('uir') and not inf.endswith(('guir', 'quir')):
            return s + 'y'
        if self.ar and before_e:
            if s.endswith('c'):
                return s[:-1] + 'qu'
            if s.endswith('g'):
                return s + 'u'
            if s.endswith('z'):
                return s[:-1] + 'c'
        return s

    def yo_stem(self):
        return self.spell(self.stressed())

    def subj_stem(self, stressed):
        """Subjunctive stem. Unstressed - the vos ending carries the stress -
        means -ar/-er verbs drop their stem change and -ir verbs weaken it:
        no pensés, no volvás, but no pidás and no durmás."""
        if stressed:
            return self.spell(self.stressed(), self.ar)
        return self.spell(self.weak_stem() if self.ir else self.stem, self.ar)

    # ---- forms -------------------------------------------------------

    def present(self):
        if 'pres' in self.irr:
            p = self.irr['pres']
            return p if len(p) == 6 else [p[0], p[1], p[1], p[2], p[3], p[4]]
        e = (['o', 'ás', 'as', 'a', 'amos', 'an'] if self.ar else
             ['o', 'és', 'es', 'e', 'emos', 'en'] if self.er else
             ['o', 'ís', 'es', 'e', 'imos', 'en'])
        st, un = self.stressed(), self.stem
        yo = self.irr.get('yo') or self.yo_stem() + e[0]
        ystem = self.yo_stem() if self.inf.endswith('uir') and not self.inf.endswith(('guir', 'quir')) else st
        f = [yo, un + e[1], ystem + e[2], ystem + e[3], un + e[4], ystem + e[5]]
        for k, i in (('pres_2s_tu', 2), ('pres_3s', 3), ('pres_3p', 5)):
            if k in self.irr:
                f[i] = self.irr[k]
        return f

    def ducir_stem(self):
        return self.inf[:-3] + 'j' if self.inf.endswith('ducir') else None

    def preterite_1s(self):
        d = self.ducir_stem()
        if d and 'pret' not in self.irr and 'pret_stem' not in self.irr:
            return d + 'e'
        if 'pret' in self.irr:
            return self.irr['pret'][0]
        if 'pret_stem' in self.irr:
            return self.irr['pret_stem'] + 'e'
        if self.ar:
            s = self.stem
            if self.inf.endswith('car'):
                s = s[:-1] + 'qu'
            elif self.inf.endswith('gar'):
                s = s + 'u'
            elif self.inf.endswith('zar'):
                s = s[:-1] + 'c'
            return s + 'é'
        return self.stem + 'í'

    def imperfect_1s(self):
        if 'imperf' in self.irr:
            return self.irr['imperf'][0]
        return self.stem + ('aba' if self.ar else 'ía')

    def participle(self):
        if 'part' in self.irr:
            return self.irr['part']
        if self.ar:
            return self.stem + 'ado'
        if self.inf.endswith(('aer', 'eer', 'oír', 'aír')):
            return self.stem + 'ído'
        return self.stem + 'ido'

    def gerund(self):
        if 'ger' in self.irr:
            return self.irr['ger']
        if self.ar:
            return self.stem + 'ando'
        s = self.weak_stem()
        if (s and s[-1] in 'aeiou' and self.inf.endswith(('aer', 'eer', 'oír', 'uir', 'aír'))
                and not self.inf.endswith(('guir', 'quir'))):
            return s + 'yendo'
        if s and s[-1] in 'ñll' or s.endswith('ll'):
            return s + 'endo'
        return s + 'iendo'

    def future_stem(self):
        return self.irr.get('fut_stem') or strip_accents(self.inf)

    def subjunctive_1s(self):
        if 'subj' in self.irr:
            return self.irr['subj'][0]
        if 'subj_stem' in self.irr:
            return self.irr['subj_stem'] + ('e' if self.ar else 'a')
        yo = self.irr.get('yo')
        if yo and yo.endswith('o'):
            return self.spell(yo[:-1], self.ar) + ('e' if self.ar else 'a')
        return self.subj_stem(True) + ('e' if self.ar else 'a')

    def command_vos(self):
        if 'cmd' in self.irr:
            return self.irr['cmd']
        body = self.inf[:-1]
        return accent_syllable(body, len(body) - 1)

    def command_vos_negative(self):
        """The safer written form, built on the tú subjunctive: no tengas.

        Sources disagree on Paraguay specifically - several state the
        subjunctive there simply takes the tú forms, while the voseo
        subjunctive (no tengás) is widely heard in Rioplatense speech. Both
        are generated; this one leads and the other is shown as a variant,
        because the learner needs to recognise the spoken form but should
        write the standard one."""
        if self.inf == 'dar':
            return 'des'
        return self.subjunctive_1s() + 's'

    def command_vos_negative_voseo(self):
        """The spoken Rioplatense variant: no tengás, no pensés, no pidás.
        The vos ending carries the stress, so -ar/-er verbs lose their stem
        change while -ir verbs weaken theirs."""
        if self.inf == 'dar':
            return 'des'
        if 'subj' in self.irr or 'subj_stem' in self.irr:
            return strip_accents(self.subjunctive_1s()[:-1]) + ('és' if self.ar else 'ás')
        yo = self.irr.get('yo')
        stem = self.spell(yo[:-1], self.ar) if yo and yo.endswith('o') else self.subj_stem(False)
        return stem + ('és' if self.ar else 'ás')


def _enclitic(word, pron, imperative=False):
    """Attach a pronoun, moving the written accent as the stress shifts."""
    for a, b in (('ando', 'ándo'), ('iendo', 'iéndo'), ('yendo', 'yéndo')):
        if word.endswith(a):
            return word[:-len(a)] + b + pron
    if imperative:
        # levantá + te -> levantate (now stressed on the penultimate syllable)
        return strip_accents(word) + pron if len(strip_accents(word)) > 2 else word + pron
    return word + pron


def forms(inf):
    """Every slot for one infinitive, as {slot: form}.

    Multi-word entries conjugate at the head verb: prestar atención ->
    presto atención, prestá atención."""
    if ' ' in inf.strip():
        head, _, tail = inf.strip().partition(' ')
        f = forms(head)
        return {k: (v + ' ' + tail if v else v) for k, v in f.items()}
    v = Verb(inf)
    p = v.present()
    r = v.reflexive
    me, te, se, nos = ('me ', 'te ', 'se ', 'nos ') if r else ('', '', '', '')
    f = {
        'pres-1s':    me + p[0],
        'pres-2s':    te + p[1],
        'pres-2s-tu': te + p[2],
        'pres-3s':    se + p[3],
        'pres-1p':    nos + p[4],
        'pres-3p':    se + p[5],
        'cmd-vos':    _enclitic(v.command_vos(), 'te', True) if r else v.command_vos(),
        'going-1s':   'voy a ' + (v.inf + 'me' if r else v.inf),
        'ger':        _enclitic(v.gerund(), 'me') if r else v.gerund(),
        'pret-1s':    me + v.preterite_1s(),
        'imp-1s':     me + v.imperfect_1s(),
        'perf-1s':    (me + 'he ' if r else 'he ') + v.participle(),
        'cmd-vos-neg': ('no te ' if r else 'no ') + v.command_vos_negative(),
        'cmd-vos-neg-voseo': ('no te ' if r else 'no ') + v.command_vos_negative_voseo(),
        'fut-1s':     me + v.future_stem() + 'é',
        'cond-1s':    me + v.future_stem() + 'ía',
        'subj-1s':    me + v.subjunctive_1s(),
    }
    return f


def pattern_of(inf):
    """Which exemplar this verb conjugates like."""
    v = Verb(inf)
    if v.irr:
        pre, base = base_of(v.inf, IRREG)
        return base if base else (v.inf if v.inf in IRREG else 'irregular')
    if v.change:
        return {'ie': 'pensar', 'ue': 'volver', 'i': 'pedir'}[v.change]
    return 'hablar' if v.ar else 'comer' if v.er else 'vivir'


# ---------------------------------------------------------------------------
# Full paradigms. The app displays 16 slots; identifying which form a sentence
# actually uses needs every person of every tense.
# ---------------------------------------------------------------------------

PERSONS = ['1s', '2s', '2s-tu', '3s', '1p', '3p']
# Irregular tú imperatives. Every other verb's is its 3s present, and every
# vos imperative is regular, which is one of voseo's small mercies.
CMD_TU = {'tener': 'ten', 'venir': 'ven', 'poner': 'pon', 'salir': 'sal',
          'hacer': 'haz', 'decir': 'di', 'ser': 'sé', 'ir': 've', 'ver': 've',
          'dar': 'da', 'estar': 'está', 'saber': 'sabe'}


def _expand5(a):
    """[1s, 2s, 3s, 1p, 3p] -> the six-person shape (vos takes the tú form)."""
    return [a[0], a[1], a[1], a[2], a[3], a[4]]


class _Para:
    """Full paradigm for a simple (single-word, non-reflexive) infinitive."""

    def __init__(self, v):
        self.v = v

    def present(self):
        return self.v.present()

    def preterite(self):
        v, irr = self.v, self.v.irr
        if 'pret' in irr:
            return _expand5(irr['pret'])
        strong = irr.get('pret_stem') or v.ducir_stem()
        if strong:
            f = [strong + 'e', strong + 'iste', strong + 'iste', strong + 'o',
                 strong + 'imos', strong + ('eron' if strong.endswith('j') else 'ieron')]
        elif v.ar:
            st = v.stem
            f = [v.spell(st, True) + 'é', st + 'aste', st + 'aste', st + 'ó',
                 st + 'amos', st + 'aron']
        else:
            st, w = v.stem, v.weak_stem()
            # a vowel before the ending turns i into y: leyó, construyó, oyó
            y = (st and st[-1] in 'aeiou'
                 and not v.inf.endswith(('guir', 'quir', 'ñir', 'llir')))
            h = 'í' if (st and st[-1] in 'aeo') else 'i'   # hiatus accent
            f = [st + 'í', st + h + 'ste', st + h + 'ste',
                 w + ('yó' if y else 'ió'), st + h + 'mos',
                 w + ('yeron' if y else 'ieron')]
        for k, i in (('pret_3s', 3), ('pret_3p', 5)):
            if k in irr:
                f[i] = irr[k]
        return f

    def imperfect(self):
        v, irr = self.v, self.v.irr
        if 'imperf' in irr:
            return _expand5(irr['imperf'])
        if v.ar:
            e = ['aba', 'abas', 'abas', 'aba', 'ábamos', 'aban']
        else:
            e = ['ía', 'ías', 'ías', 'ía', 'íamos', 'ían']
        return [v.stem + x for x in e]

    def future(self):
        st = self.v.future_stem()
        return [st + x for x in ('é', 'ás', 'ás', 'á', 'emos', 'án')]

    def conditional(self):
        st = self.v.future_stem()
        return [st + x for x in ('ía', 'ías', 'ías', 'ía', 'íamos', 'ían')]

    def subjunctive(self):
        v, irr = self.v, self.v.irr
        if 'subj' in irr and len(irr['subj']) == 6:
            return list(irr['subj'])
        one = v.subjunctive_1s()
        base = one[:-1]
        weak = v.subj_stem(False)
        e = 'e' if v.ar else 'a'
        # the stem change survives where the stem is stressed, and 1p is not
        return [one, base + e + 's', base + e + 's', one,
                weak + e + 'mos', base + e + 'n']

    def subjunctive_voseo(self):
        """no hablés / que vos hablés - the spoken Rioplatense variant."""
        return self.v.command_vos_negative_voseo()

    def subjunctive_imperfect(self):
        st = self.preterite()[5]
        if st.endswith('ron'):
            st = st[:-3]
        out = [st + x for x in ('ra', 'ras', 'ras', 'ra', 'ramos', 'ran')]
        i = _last_vowel_index(st)
        if i >= 0:
            out[4] = accent_syllable(st, i) + 'ramos'
        return out

    def imperatives(self):
        v = self.v
        return {'cmd-vos': v.command_vos(),
                'cmd-tu': CMD_TU.get(v.inf) or self.present()[3],
                'cmd-ud': self.subjunctive()[3],
                'cmd-uds': self.subjunctive()[5]}


def paradigm(inf):
    """Every form of one verb, as {label: form}. Labels are tense-person,
    e.g. pres-3s, pret-1p, plus the non-finite and imperative forms."""
    if ' ' in inf.strip():
        head, _, tail = inf.strip().partition(' ')
        return {k: f'{x} {tail}' for k, x in paradigm(head).items() if x}
    v = Verb(inf)
    p = _Para(v)
    out = {}
    for tense, vals in (('pres', p.present()), ('pret', p.preterite()),
                        ('imperf', p.imperfect()), ('fut', p.future()),
                        ('cond', p.conditional()), ('subj', p.subjunctive()),
                        ('subjimp', p.subjunctive_imperfect())):
        for person, form in zip(PERSONS, vals):
            out[f'{tense}-{person}'] = form
    out.update(p.imperatives())
    out.update(v.irr.get('extra') or {})
    out['subj-2s-voseo'] = p.subjunctive_voseo()
    out['ger'] = v.gerund()
    out['part'] = v.participle()
    return {k: x for k, x in out.items() if x}
