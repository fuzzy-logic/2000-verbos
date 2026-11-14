"""Assign every verb to one of the 30 topics in data/topics/_index.tsv.

Exact lists carry the high-frequency verbs, where getting it right matters
most and where a gloss keyword is too blunt. English-gloss keywords sweep the
tail. Anything left unmatched is reported, not silently binned.
"""
import csv
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EXACT = {
'greeting-small-talk': """saludar presentar presentarse llamar llamarse conocer
    conocerse despedirse abrazar besar sonreír saludarse recibir atender
    acompañar invitar pasar (a visitar) tutear vosear chocar los cinco""",
'asking-understanding': """preguntar entender comprender repetir explicar
    significar deletrear aclarar aclarar el malentendido traducir interpretar
    confundir confundirse equivocar equivocarse dudar consultar averiguar
    enterarse sobreentenderse malinterpretar""",
'yes-no-maybe': """querer poder deber necesitar tener que hay que aceptar
    rechazar negar negarse permitir prohibir dejar impedir intentar probar
    tratar tratar de lograr conseguir atreverse animarse abstenerse""",
'being-feeling': """ser estar haber tener andar parecer quedar quedarse
    resultar existir sentir sentirse hallarse volverse permanecer valer
    tener ganas hacer falta dar lo mismo valer la pena tratarse de constar""",
'doing-handling': """hacer dar poner ponerse llevar traer sacar meter quitar
    agarrar soltar tomar (algo) dejar abrir cerrar tocar mostrar empujar tirar
    levantar bajar (algo) mover moverse girar dar vuelta juntar separar recoger
    guardar colocar acomodar apoyar sostener sujetar apretar aflojar atar
    desatar envolver desenvolver tapar destapar llenar vaciar cargar (algo)
    descargar (algo) arrojar lanzar golpear pegar romper (algo) usar utilizar
    emplear aprovechar realizar efectuar ejecutar acabar terminar (algo)
    repartir distribuir intercambiar reemplazar sustituir añadir agregar
    (algo) sumar (algo) retirar (algo) devolver (algo) prestar (algo)""",
'seeing-noticing': """ver mirar observar notar fijarse percibir divisar
    descubrir reconocer encontrar buscar perder (algo) hallar aparecer
    desaparecer asomarse espiar vigilar revisar inspeccionar examinar
    contemplar ojear atisbar distinguir confundir (dos cosas) parecerse""",
'free-time': """bailar cantar jugar leer estudiar practicar entrenar nadar
    correr (deporte) caminar (paseo) pasear dibujar pintar (un cuadro)
    tocar (un instrumento) filmar fotografiar grabar coleccionar tejer
    coser cultivar pescar cazar apostar festejar celebrar divertirse
    divertir disfrutar relajar relajarse descansar (ocio) soñar desear
    aburrirse viajar (turismo) acampar escalar remar patinar""",
'buying-paying': """comprar pagar costar cobrar gastar vender deber (plata)
    facturar abonar ahorrar devolver cambiar canjear elegir escoger llevar
    probarse reservar encargar pedir (en una tienda) entregar repartir""",
'haggling-quantities': """bajar (el precio) regatear rebajar sobrar faltar
    alcanzar pesar medir contar sumar restar multiplicar dividir calcular
    aumentar subir (el precio) descontar redondear completar agotar""",
'bank-cash-credit': """cargar sacar depositar transferir retirar prestar
    deberle fiar endeudarse invertir cotizar convertir retener (impuesto)
    declarar (impuestos) gravar acreditar""",
'ordering-eating': """comer pedir tomar probar servir servirse almorzar cenar
    desayunar merendar masticar tragar morder saborear invitar (a comer)
    atender (una mesa) ordenar (comida) compartir (la comida) repetir (el plato)
    llenarse empacharse antojarse""",
'cooking-kitchen': """cocinar hervir freír asar hornear cortar picar pelar
    mezclar batir revolver amasar sazonar salar condimentar calentar recalentar
    enfriar congelar descongelar derretir quemar quemarse guisar tostar
    rallar colar escurrir""",
'terere-drinking': """cebar convidar compartir brindar beber emborracharse
    tomar (tereré) preparar (el tereré) pasar (el mate) chupar""",
'transport-colectivo': """ir venir subir bajar parar llegar salir viajar volver
    regresar tomar (el colectivo) esperar (el colectivo) bajarse subirse
    apurarse perder (el colectivo) trasbordar embarcar despegar aterrizar
    aterrizar (forzoso) demorar atrasarse""",
'directions-places': """doblar seguir cruzar quedar pasar entrar caminar
    acercarse alejarse ubicar ubicarse perderse orientarse señalar indicar
    rodear atravesar retroceder avanzar alcanzar (un lugar) dirigirse""",
'driving-moto': """manejar conducir estacionar arrancar frenar acelerar chocar
    adelantar remolcar reparar (el auto) revisar (el auto) cargar (nafta)
    pinchar atropellar patinar volcar circular""",
'house-renting': """alquilar mudarse vivir habitar arreglar limpiar barrer
    ordenar acomodar amueblar pintar construir refaccionar desalojar
    deshabitar compartir (la casa) convivir instalarse""",
'daily-routine': """levantarse acostarse dormir dormirse despertarse bañarse
    ducharse vestirse desvestirse peinarse afeitarse cepillarse lavarse
    maquillarse descansar madrugar trasnochar estirar relajarse apurar""",
'fixing-breaking-power': """romper romperse funcionar prender apagar cortar
    cortarse enchufar desenchufar reparar fallar gotear perder (agua)
    tapar destapar ajustar aflojar atascarse trabarse desarmar armar
    reemplazar gastarse""",
'weather-heat': """llover lloviznar tronar relampaguear nevar helar granizar
    soplar refrescar amanecer anochecer secar secarse mojarse empaparse
    sudar transpirar aguantar soportar (el calor) nublarse despejarse""",
'family-friends': """visitar cuidar criar acompañar casarse separarse
    divorciarse enamorarse nacer morir fallecer crecer envejecer adoptar
    heredar parecerse llevarse (bien) apoyar ayudar proteger consentir
    malcriar extrañar""",
'conversation-opinion': """decir contar hablar conversar charlar comentar
    opinar discutir coincidir responder contestar afirmar negar (algo)
    insistir interrumpir callarse escuchar oír mencionar agregar aportar
    bromear chismear exagerar""",
'feelings-conflict': """enojarse enojar preocupar preocuparse disculpar
    disculparse perdonar molestar molestarse pelear pelearse reconciliarse
    arrepentirse quejarse reclamar gritar insultar ofender ofenderse
    avergonzarse asustar asustarse llorar reír alegrar alegrarse entristecer
    emocionar aburrir aburrirse frustrar decepcionar sorprender""",
'arranging-to-meet': """quedar avisar confirmar cancelar postergar adelantar
    (la cita) coordinar agendar citar citarse juntarse reunirse encontrarse
    (con alguien) acordar comprometerse faltar (a una cita) atrasar""",
'work-tasks': """trabajar ganar entregar encargarse ocuparse cumplir terminar
    empezar comenzar organizar planear planificar dirigir supervisar contratar
    despedir renunciar jubilarse ascender capacitar delegar rendir rendir
    (examen) presentar (un informe) evaluar revisar corregir aprobar reprobar""",
'paperwork-bureaucracy': """firmar presentar tramitar renovar sellar registrar
    registrar (marca) registrar (patrimonio) inscribir inscribirse certificar
    legalizar apostillar autorizar denegar vencer vencerse caducar completar
    (un formulario) adjuntar constar acreditar (un documento) notificar
    citar (judicial)""",
'phone-computer': """mandar enviar llamar (por teléfono) contestar (el teléfono)
    descargar subir (un archivo) conectar conectarse desconectarse borrar
    guardar imprimir escanear actualizar instalar reiniciar bloquear
    silenciar cargar (el celular) chatear escribir teclear colgar marcar
    navegar postear""",
'body-illness-pharmacy': """doler enfermar enfermarse curar curarse recetar
    mejorarse empeorar sanar toser estornudar vomitar marearse desmayarse
    inflamarse hincharse picar (un bicho) rascarse vendar operar internar
    recuperarse contagiar contagiarse hidratar desinfectar""",
'emergencies': """ayudar socorrer avisar (a la policía) robar asaltar
    lastimar lastimarse caer caerse quemar (un incendio) ahogarse
    rescatar denunciar huir escapar esconderse gritar (por ayuda)
    atender (una urgencia) trasladar""",
'thinking-knowing': """pensar creer saber suponer considerar imaginar recordar
    olvidar olvidarse acordarse reflexionar deducir concluir asumir sospechar
    desconfiar confiar comprobar constatar verificar demostrar razonar
    interpretar (un dato) prever predecir""",
'change-cause': """cambiar convertirse transformar provocar generar causar
    producir originar derivar influir afectar depender implicar conllevar
    mejorar desarrollar reducir incrementar disminuir mantener conservar
    perdurar surgir desaparecer""",
'formal-written': """establecer disponer consistir corresponder proceder
    regir derogar estipular redactar remitir adjuntar (formal) suscribir
    otorgar conferir ejercer desempeñar incurrir omitir subsanar""",
'news-institutions': """gobernar votar elegir (un gobierno) postularse
    renunciar (un cargo) asumir (un cargo) aprobar (una ley) vetar legislar
    juzgar condenar absolver apelar demandar financiar subsidiar privatizar
    estatizar inaugurar clausurar protestar manifestarse""",
}

# gloss keywords, checked in this order. Earlier topics win.
KEYWORDS = [
 ('cooking-kitchen', ['cook', 'boil', 'fry', 'roast', 'bake', 'chop', 'peel',
                      'stir', 'knead', 'season', 'grill', 'simmer', 'grate']),
 ('body-illness-pharmacy', ['ache', 'ill', 'sick', 'heal', 'cure', 'symptom',
                            'swell', 'cough', 'sneeze', 'vomit', 'faint',
                            'bandage', 'operate', 'infect', 'medicine']),
 ('emergencies', ['rescue', 'drown', 'rob', 'steal', 'mug', 'flee', 'escape',
                  'injure', 'wound', 'emergency']),
 ('weather-heat', ['rain', 'snow', 'thunder', 'hail', 'wind', 'weather',
                   'sweat', 'soak', 'dry', 'cool down', 'dawn', 'dusk']),
 ('transport-colectivo', ['travel', 'board', 'bus', 'flight', 'depart',
                          'arrive', 'get on', 'get off']),
 ('driving-moto', ['drive', 'park', 'brake', 'accelerate', 'crash', 'overtake']),
 ('directions-places', ['turn', 'cross', 'walk', 'direction', 'locate',
                        'approach', 'go round', 'go through']),
 ('phone-computer', ['download', 'upload', 'click', 'type', 'screen', 'file',
                     'online', 'internet', 'print', 'scan', 'message']),
 ('buying-paying', ['buy', 'pay', 'sell', 'cost', 'charge', 'spend', 'price',
                    'purchase', 'refund']),
 ('bank-cash-credit', ['bank', 'deposit', 'withdraw', 'lend', 'borrow',
                       'invest', 'tax', 'credit']),
 ('haggling-quantities', ['count', 'measure', 'weigh', 'add', 'subtract',
                          'multiply', 'divide', 'calculate', 'amount',
                          'increase', 'decrease', 'run out']),
 ('paperwork-bureaucracy', ['sign', 'stamp', 'register', 'certify', 'form',
                            'document', 'permit', 'licence', 'expire',
                            'notify', 'submit']),
 ('news-institutions', ['govern', 'vote', 'elect', 'law', 'court', 'judge',
                        'sentence', 'appeal', 'sue', 'fund', 'subsid',
                        'protest', 'minister', 'president']),
 ('work-tasks', ['work', 'job', 'hire', 'employ', 'manage', 'organise',
                 'deliver', 'task', 'earn', 'promote', 'resign', 'retire',
                 'supervise', 'train']),
 ('feelings-conflict', ['angry', 'annoy', 'upset', 'apolog', 'forgive',
                        'complain', 'argue', 'fight', 'cry', 'laugh', 'fear',
                        'ashamed', 'regret', 'sad', 'happy', 'worry',
                        'surprise', 'bored', 'frustrat', 'disappoint']),
 ('family-friends', ['marry', 'divorce', 'born', 'die', 'grow', 'child',
                     'family', 'care for', 'raise', 'inherit', 'miss']),
 ('conversation-opinion', ['say', 'tell', 'talk', 'speak', 'chat', 'comment',
                           'opinion', 'answer', 'reply', 'listen', 'hear',
                           'mention', 'insist', 'interrupt', 'joke']),
 ('daily-routine', ['wake', 'sleep', 'bath', 'shower', 'dress', 'comb',
                    'shave', 'brush', 'rest', 'wash']),
 ('house-renting', ['rent', 'move house', 'clean', 'sweep', 'tidy', 'furnish',
                    'paint', 'build', 'live in', 'house']),
 ('fixing-breaking-power', ['break', 'fix', 'repair', 'mend', 'plug', 'switch',
                            'leak', 'loosen', 'tighten', 'assemble', 'fail']),
 ('ordering-eating', ['eat', 'drink', 'order', 'serve', 'taste', 'chew',
                      'swallow', 'bite', 'lunch', 'dinner', 'breakfast',
                      'meal', 'hungry', 'thirst']),
 ('asking-understanding', ['ask', 'understand', 'explain', 'repeat', 'mean',
                           'translate', 'confuse', 'spell', 'clarify']),
 ('thinking-knowing', ['think', 'believe', 'know', 'suppose', 'consider',
                       'imagine', 'remember', 'forget', 'doubt', 'suspect',
                       'conclude', 'assume', 'prove', 'reason', 'expect']),
 ('change-cause', ['change', 'become', 'cause', 'produce', 'generate',
                   'affect', 'influence', 'depend', 'develop', 'reduce',
                   'increase', 'maintain', 'disappear', 'appear', 'turn into',
                   'transform', 'improve', 'worsen']),
 ('formal-written', ['establish', 'stipulat', 'draft', 'decree', 'provision',
                     'confer', 'grant', 'exercise', 'omit', 'formal']),
 ('greeting-small-talk', ['greet', 'introduce', 'welcome', 'hug', 'kiss',
                          'smile', 'invite', 'accompany', 'visit']),
 ('arranging-to-meet', ['meet', 'arrange', 'cancel', 'postpone', 'confirm',
                        'coordinate', 'appointment']),
 ('yes-no-maybe', ['want', 'can', 'able', 'must', 'need', 'allow', 'forbid',
                   'accept', 'refuse', 'reject', 'try', 'manage', 'dare']),
 ('seeing-noticing', ['see', 'look', 'watch', 'notice', 'observe', 'spot',
                      'discover', 'recognise', 'find', 'appear', 'disappear',
                      'glance', 'stare', 'inspect', 'examine']),
 ('free-time', ['dance', 'sing', 'play', 'swim', 'draw', 'paint', 'sport',
                'hobby', 'holiday', 'enjoy', 'relax', 'fun', 'dream',
                'photograph', 'film', 'record', 'fish', 'hunt', 'camp']),
 ('doing-handling', ['put', 'give', 'take', 'bring', 'carry', 'hold', 'grab',
                     'throw', 'push', 'pull', 'open', 'close', 'cover',
                     'wrap', 'tie', 'lift', 'move', 'place', 'fill', 'empty',
                     'press', 'squeeze', 'hit', 'knock', 'use', 'make', 'do',
                     'carry out', 'gather', 'separate', 'replace', 'add',
                     'remove', 'return', 'share out', 'swap']),
 ('being-feeling', ['feel', 'seem', 'remain', 'stay', 'exist', 'be worth']),
]


# Generic topics match only when the gloss IS the verb, optionally with a
# particle. Substring matching put "to take revenge" and "to make peace with"
# under handling, which is an English idiom, not a Spanish meaning.
STRICT = {'doing-handling', 'seeing-noticing', 'free-time'}
PARTICLES = {'out', 'in', 'up', 'down', 'off', 'away', 'over', 'back', 'on',
             'apart', 'together', 'round', 'through', 'about'}


def _core(gloss):
    """'to look / to watch' -> 'look'; 'to take out' -> 'take out'."""
    g = re.sub(r'\([^)]*\)', '', gloss).split('/')[0]
    return re.sub(r'^\s*to\s+', '', g.strip().lower()).strip(' .,')


def _strict_hit(core, kw):
    if core == kw:
        return True
    parts = core.split()
    return (len(parts) == 2 and parts[0] == kw and parts[1] in PARTICLES)


def _norm(s):
    return re.sub(r'\s+', ' ', s.strip().lower())


def build_exact():
    out = {}
    for slug, blob in EXACT.items():
        # entries may contain spaces inside parentheses: "cargar (nafta)"
        for item in re.findall(r'[^\s(]+(?:\s*\([^)]*\))?', blob):
            item = _norm(item)
            if item and item not in out:
                out[item] = slug
    return out


def overrides():
    """rank -> slug, for the verbs no rule should be trusted to place."""
    path = os.path.join(ROOT, 'data', 'topics', 'overrides.tsv')
    if not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as fh:
        return {r['rank']: r['topic'] for r in csv.DictReader(fh, delimiter='\t')}


def classify(verb, gloss, exact, rank=None, over=None):
    if over and rank in over:
        return over[rank], 'override'
    v = _norm(verb)
    if v in exact:
        return exact[v], 'exact'
    bare = _norm(re.sub(r'\([^)]*\)', '', verb))
    if bare in exact:
        return exact[bare], 'exact-bare'
    g = ' ' + _norm(gloss) + ' '
    core = _core(gloss)
    for slug, words in KEYWORDS:
        strict = slug in STRICT
        for w in words:
            if _strict_hit(core, w) if strict else (w in g):
                return slug, f'kw:{w}'
    return None, 'unmatched'


def rows():
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'data', 'verbs_*.tsv'))):
        with open(path, encoding='utf-8') as fh:
            for r in csv.DictReader(fh, delimiter='\t'):
                r['_file'] = path
                out.append(r)
    out.sort(key=lambda r: int(r['rank']))
    return out


def main():
    from collections import Counter
    exact = build_exact()
    over = overrides()
    data = rows()
    got, how = {}, Counter()
    for r in data:
        slug, why = classify(r['verb_es'], r['verb_en'], exact, r['rank'], over)
        got[r['rank']] = slug
        how[why.split(':')[0]] += 1
        r['_slug'] = slug
    n = sum(1 for v in got.values() if v)
    print(f'{len(data)} verbs | assigned {n} ({100*n/len(data):.1f}%) | '
          f'unmatched {len(data)-n}')
    print('by method:', dict(how))
    per = Counter(v for v in got.values() if v)
    print(f'\ntopics used: {len(per)}/30')
    order = [r['slug'] for r in csv.DictReader(
        open(os.path.join(ROOT, 'data', 'topics', '_index.tsv'), encoding='utf-8'),
        delimiter='\t')]
    for slug in order:
        print(f'   {slug:26s} {per.get(slug, 0):4d}')
    return data


if __name__ == '__main__':
    main()


def write():
    """Write the topic column into data/verbs_*.tsv."""
    exact, over = build_exact(), overrides()
    cols = ['rank', 'verb_es', 'verb_en', 'sentence_es', 'sentence_en', 'note',
            'topic', 'form', 'verb_token']
    missing = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'data', 'verbs_*.tsv'))):
        with open(path, encoding='utf-8') as fh:
            data = list(csv.DictReader(fh, delimiter='\t'))
        for r in data:
            slug, _ = classify(r['verb_es'], r['verb_en'], exact, r['rank'], over)
            if not slug:
                missing.append((r['rank'], r['verb_es']))
            r['topic'] = slug or ''
        with open(path, 'w', encoding='utf-8', newline='') as fh:
            w = csv.DictWriter(fh, cols, delimiter='\t',
                               extrasaction='ignore', lineterminator='\n')
            w.writeheader()
            for r in data:
                w.writerow({c: (r.get(c) or '') for c in cols})
    if missing:
        sys.exit(f'{len(missing)} verbs still have no topic: {missing[:10]}')
    print('topic column written')
