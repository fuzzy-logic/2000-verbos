"""Checks for the conjugation engine. Run: python3 lib/test_conjugate.py

The gate that matters most is reference(): every yo/vos pair hand-written in
data/tables/top-verbs-voseo.tsv must come back out of the engine unchanged.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from conjugate import SLOTS, forms  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# verb -> slot -> expected. Hand-checked, one case per behaviour the engine
# has to get right rather than one case per verb.
CASES = {
    # regular models
    'hablar': {'pres-1s': 'hablo', 'pres-2s': 'hablás', 'cmd-vos': 'hablá',
               'pret-1s': 'hablé', 'subj-1s': 'hable', 'ger': 'hablando'},
    'comer': {'pres-2s': 'comés', 'cmd-vos': 'comé', 'pret-1s': 'comí'},
    'vivir': {'pres-2s': 'vivís', 'cmd-vos': 'viví', 'ger': 'viviendo'},
    # stem changes: present yes, vos no - the whole point of voseo
    'pensar': {'pres-1s': 'pienso', 'pres-2s': 'pensás', 'pres-1p': 'pensamos',
               'cmd-vos-neg': 'no pienses', 'cmd-vos-neg-voseo': 'no pensés'},
    'volver': {'pres-1s': 'vuelvo', 'pres-2s': 'volvés', 'perf-1s': 'he vuelto'},
    'pedir': {'pres-1s': 'pido', 'pres-2s': 'pedís', 'ger': 'pidiendo',
              'cmd-vos-neg-voseo': 'no pidás'},
    'dormir': {'pres-1s': 'duermo', 'ger': 'durmiendo',
               'cmd-vos-neg-voseo': 'no durmás'},
    'jugar': {'pres-1s': 'juego', 'pret-1s': 'jugué', 'subj-1s': 'juegue'},
    # spelling shifts happen before -e, never before the yo -o
    'buscar': {'pres-1s': 'busco', 'pret-1s': 'busqué', 'subj-1s': 'busque'},
    'llegar': {'pres-1s': 'llego', 'pret-1s': 'llegué', 'subj-1s': 'llegue'},
    'empezar': {'pres-1s': 'empiezo', 'pret-1s': 'empecé', 'subj-1s': 'empiece'},
    'conocer': {'pres-1s': 'conozco', 'subj-1s': 'conozca'},
    'vencer': {'pres-1s': 'venzo'},
    'elegir': {'pres-1s': 'elijo', 'ger': 'eligiendo'},
    'seguir': {'pres-1s': 'sigo', 'ger': 'siguiendo', 'subj-1s': 'siga'},
    'construir': {'pres-1s': 'construyo', 'ger': 'construyendo'},
    'leer': {'ger': 'leyendo', 'perf-1s': 'he leído'},
    # irregulars
    'ser': {'pres-1s': 'soy', 'pres-2s': 'sos', 'pret-1s': 'fui',
            'imp-1s': 'era', 'cmd-vos': 'sé'},
    'ir': {'pres-1s': 'voy', 'pret-1s': 'fui', 'imp-1s': 'iba',
           'ger': 'yendo', 'cmd-vos': 'andá', 'subj-1s': 'vaya'},
    'tener': {'pres-1s': 'tengo', 'pres-2s': 'tenés', 'pret-1s': 'tuve',
              'fut-1s': 'tendré', 'subj-1s': 'tenga', 'cmd-vos': 'tené'},
    'hacer': {'pres-1s': 'hago', 'pret-1s': 'hice', 'fut-1s': 'haré',
              'perf-1s': 'he hecho'},
    'ver': {'pres-1s': 'veo', 'pres-2s': 'ves', 'cmd-vos': 've',
            'pret-1s': 'vi', 'subj-1s': 'vea', 'perf-1s': 'he visto'},
    'dar': {'pres-1s': 'doy', 'pres-2s': 'das', 'cmd-vos': 'da',
            'subj-1s': 'dé', 'cmd-vos-neg': 'no des'},
    'decir': {'pres-1s': 'digo', 'pret-1s': 'dije', 'ger': 'diciendo',
              'perf-1s': 'he dicho'},
    'saber': {'pres-1s': 'sé', 'pret-1s': 'supe', 'subj-1s': 'sepa'},
    'haber': {'pres-1s': 'he', 'pret-1s': 'hube', 'subj-1s': 'haya'},
    # inherited by prefix - 182 verbs rely on this
    'detener': {'pres-1s': 'detengo', 'pret-1s': 'detuve', 'fut-1s': 'detendré'},
    'componer': {'pres-1s': 'compongo', 'pret-1s': 'compuse',
                 'perf-1s': 'he compuesto'},
    'devolver': {'pres-1s': 'devuelvo', 'perf-1s': 'he devuelto'},
    'suponer': {'pres-1s': 'supongo', 'pret-1s': 'supuse'},
    'sonreír': {'pres-1s': 'sonrío', 'subj-1s': 'sonría'},
    # inheritance that must NOT happen
    'compensar': {'pres-1s': 'compenso'},     # not *compienso, despite pensar
    'contestar': {'pres-1s': 'contesto'},     # not *contestoy, despite estar
    'predecir': {'pres-1s': 'predigo', 'fut-1s': 'predeciré'},   # not *prediré
    'bendecir': {'pres-1s': 'bendigo', 'perf-1s': 'he bendecido'},
    # -ducir takes a -duj- preterite
    'producir': {'pres-1s': 'produzco', 'pret-1s': 'produje'},
    'traducir': {'pret-1s': 'traduje'},
    # the accent classes
    'enviar': {'pres-1s': 'envío', 'pres-2s': 'enviás'},
    'cambiar': {'pres-1s': 'cambio'},         # -iar without the accent
    'continuar': {'pres-1s': 'continúo', 'pres-2s': 'continuás'},
    'averiguar': {'pres-1s': 'averiguo', 'pret-1s': 'averigué'},
    'reunir': {'pres-1s': 'reúno', 'pres-2s': 'reunís'},
    # reflexives: pronoun placement and the accent it drags around
    'levantarse': {'pres-1s': 'me levanto', 'pres-2s': 'te levantás',
                   'cmd-vos': 'levantate', 'ger': 'levantándome',
                   'perf-1s': 'me he levantado'},
    'irse': {'pres-1s': 'me voy', 'cmd-vos': 'andate', 'ger': 'yéndome'},
    'ponerse': {'pres-1s': 'me pongo', 'cmd-vos': 'ponete', 'pret-1s': 'me puse'},
    # multi-word entries conjugate at the head
    'darse cuenta': {'pres-1s': 'me doy cuenta', 'cmd-vos': 'date cuenta'},
    'tener ganas': {'pres-1s': 'tengo ganas', 'pres-2s': 'tenés ganas'},
    'volver a': {'pres-1s': 'vuelvo a', 'pret-1s': 'volví a'},
}


def cases():
    bad = 0
    for verb, want in CASES.items():
        got = forms(verb)
        for slot, expected in want.items():
            if got.get(slot) != expected:
                print(f'  {verb:16s} {slot:18s} want {expected!r}  got {got.get(slot)!r}')
                bad += 1
    return bad, sum(len(v) for v in CASES.values())


def reference():
    """Every yo/vos pair in the hand-written voseo table must round-trip."""
    bad = n = 0
    path = os.path.join(ROOT, 'data', 'tables', 'top-verbs-voseo.tsv')
    for line in open(path):
        if line.startswith('spanish') or not line.strip():
            continue
        m = re.match(r'^(\S+) — (.+)$', line.split('\t')[0].strip())
        if not m:
            continue
        parts = [x.strip() for x in m.group(2).split(',')]
        if len(parts) < 2:
            continue                      # hay / me gusta: single-form rows
        f = forms(m.group(1))
        n += 1
        if (f['pres-1s'], f['pres-2s']) != (parts[0], parts[1]):
            print(f'  {m.group(1):16s} want {parts[0]}/{parts[1]}  '
                  f'got {f["pres-1s"]}/{f["pres-2s"]}')
            bad += 1
    return bad, n


def corpus():
    """Every verb in the corpus must conjugate, with no empty slots."""
    bad = n = 0
    import glob
    seen = set()
    for path in glob.glob(os.path.join(ROOT, 'data', 'verbs_*.tsv')):
        for line in open(path):
            if line.startswith('rank') or not line.strip():
                continue
            verb = line.split('\t')[1]
            if verb in seen:
                continue
            seen.add(verb)
            n += 1
            try:
                f = forms(verb)
            except Exception as e:
                print(f'  {verb:24s} {e}')
                bad += 1
                continue
            for slot in (s[0] for s in SLOTS):
                if not f.get(slot) and not verb.startswith('haber'):
                    print(f'  {verb:24s} empty slot {slot}')
                    bad += 1
    return bad, n


if __name__ == '__main__':
    total = 0
    for name, fn in (('hand-checked cases', cases),
                     ('voseo reference table', reference),
                     ('whole corpus', corpus)):
        bad, n = fn()
        total += bad
        print(f'{"FAIL" if bad else "ok  "}  {name}: {n - bad}/{n}')
    sys.exit(1 if total else 0)
