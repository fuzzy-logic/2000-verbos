# History

The commit history up to 2026-11-14, kept as text because the repository was
squashed to a single commit at that point to drop 260 MB of superseded audio
blobs. 59 commits, oldest first. The reasoning is here; the diffs are gone.

---

## 2026-10-06 — Add 2000-verbos trainer: single-file app, build pipeline, first 100 verbs

- src/template.html: mobile-first trainer implementing the two-wave method
  (read-while-listening, then EN->ES active recall), Web Speech API, voseo data
- build.py: merges data/*.tsv into a single deployable dist/index.html
- data/verbs_001-100.tsv: top 100 verbs, Paraguayan Spanish (voseo)
- blur applies instantly in recall mode so advancing never flashes the answer

## 2026-10-06 — Add walking-track audio generator and verbs 101-400

- audio/make_track.py: edge-tts (es-PY-TaniaNeural) + ffmpeg, builds the
  verb x2 / English / slow sentence / repeat gap / English / full-speed format
- clips are trimmed of edge-tts padding so gap lengths are exact, and cached
  so re-runs only synthesise what changed
- build.py: reports distinct verbs, rejects non-Spanish characters
- data: 400 verbs, 359 distinct

## 2026-10-06 — Make the trainer an installable PWA with offline Paraguayan audio

- audio/make_track.py emits a seek index per track, so one downloaded MP3 serves
  both the walking track and every per-sentence speak button (verified: 0 clips
  land in a gap, index drift 0.006s)
- audio stored as Blobs in IndexedDB, not Cache Storage: media elements seek via
  Range requests that a cached Response won't satisfy without hand-rolled 206s
- walking mode plays one continuous media element so it survives screen-off;
  a JS-driven speech sequence gets throttled to a halt when backgrounded
- VBR encode: the track is ~65% deliberate silence, which CBR charged full price
  for. 100 verbs = 40 min of audio in 6.1 MB
- sw.js, manifest, icons, netlify.toml; build.py assembles the whole dist/ folder
- fix: init block had been injected into the chunk-size slider callback, so
  loadPacks() only ran when that slider moved
- fix: service worker registration missed when 'load' had already fired

## 2026-10-06 — Stop tracking the regenerable TTS clip cache

These are intermediate artefacts keyed by content hash; dist/audio holds the
finished tracks. Keeping them would roughly double the repo for no benefit.

## 2026-10-06 — Add public README, Paraguayan Spanish guide and licence

## 2026-10-06 — Add verbs 401-1000

Weather, body/health, admin and legal, trades, tech, arts, reflexives and
pronominal verbs, food and cooking. Paraguayan vocabulary throughout:
lapacho, Chaco, ñandutí, chipa, cocido, canilla, lavandina, remera, pieza,
intendente, Caacupé, dengue.

## 2026-10-06 — Add verbs 1001-1800

Also replaces four rows that were adjectives or non-words, and adds a build
guard that fails if a note admits the entry is not a verb.

## 2026-10-06 — Complete the deck: verbs 1801-2000

2000 sentences, 1925 distinct verbs. The tail includes River Plate and
Paraguayan colloquialisms (zafar, bancar, changuear, chamuyar, acriollarse)
alongside the formal and legal register.

## 2026-10-06 — Add all 20 audio packs: 2000 sentences, ~13 hours, 126 MB

Generated with es-PY-TaniaNeural via edge-tts. Verified: 0 failed chunks,
index drift under 6ms on every pack, 180 sampled clips all land on speech
rather than in a gap, all 2000 ranks covered exactly once.

## 2026-10-06 — Table: show the whole deck, not just the current chunk

The Table view rendered current(), which is the active 100-verb chunk, while
the chunk selector is hidden in that view - so 1900 of the 2000 verbs had no
way to be reached, and search only matched within a chunk.

Now renders all 2000 rows in one fragment and searches the full deck.
Measured at mobile width: 8.4ms first render, 1.1ms search, 9.4ms re-render,
14k DOM nodes - no pagination or virtualisation needed.

## 2026-10-06 — Block prev/next navigation, and keep the infinitive visible in Recall

- replaces the chunk dropdown with prev/next buttons, disabled at either end
  rather than wrapping; label shows the current range
- the infinitive was hidden in Recall mode, which is where it is most needed:
  with only the English sentence shown you cannot tell which verb is being
  asked for. It is a cue, not part of the answer, so it now shows in all modes

## 2026-10-06 — Fix service worker pinning users to the build they first loaded

The shell cache name was hardcoded and the document was served cache-first, so
a returning visitor kept their original index.html forever - no pushed change
could ever reach them. Observed live: a cached 76 KB page (the 400-verb build)
still being served while the deploy was 281 KB.

- build.py stamps a hash of the generated page into sw.js, so each deploy gets
  its own cache and activate deletes the previous one
- the document is now network-first with a cache fallback, keeping offline use
  while guaranteeing updates land
- cache lookups ignore the query string, so ?v=N variants stop accumulating as
  separate entries
- the page reloads once when a new worker claims it, so an already-open tab
  heals itself instead of running stale HTML

Verified by seeding a stale v1 cache: old cache purged, fresh page served,
blur active in Recall, full 2000-verb deck loaded.

## 2026-10-06 — Hide the Recall answer two independent ways

Hiding relied entirely on filter:blur. Where that is unsupported, disabled or
stripped, the answer rendered fully readable and the exercise broke silently
with no visible error. Transparent text plus a shadow obscures it with no
filter support at all; the blur is now a light extra rather than the mechanism.

## 2026-10-06 — Never transition filter to the 'none' keyword

Chrome can fail to interpolate filter to or from 'none', leaving the property
stuck at its previous value. Observed in the user's Chrome on the live site:
after revealing a Recall card the class was correctly 'es' and the colour was
restored, but filter stayed at blur(3px) permanently. The same failure in the
opposite direction is why the blur appeared not to apply at all back when
filter was the only hiding mechanism.

Resting state is now blur(0) so both ends are interpolable.

## 2026-10-07 — Add the Basics tab: 18 reference tables, 745 rows, with es-PY audio

Reference material the deck assumes you already have: question words, pronouns,
numbers and money, time, a yo/vos conjugation table, topic vocabulary, the glue
words, and a jopara/Guaraní table. Written for Paraguay specifically rather than
generic Spanish - sopa paraguaya is cornbread not soup, heladera not refrigerador,
prices in tens of thousands.

- data/tables/: _index.tsv for order and titles, one TSV per table
- the old 'Table' tab is renamed 'Deck'; saved mode key migrates table -> deck
- sections collapse by default; searching auto-opens every group that matched
- audio/make_tables_track.py builds a 4.2 MB pack with an id -> offset map, so
  each row plays the real es-PY recording (verified: Aguyje indexed at 1043.119s,
  playback landed there; 745/745 rows indexed, 9ms drift)
- charset allowlist widened for Guaraní nasals, the guaraní sign and arrows

## 2026-11-02 — Add the reorganisation proposal: topics, conjugations, verb graph

Replaces the arbitrary 1-100 rank blocks with two organising views, by
topic and by tense, and gives the top 400 verbs a full conjugation table
banded A1/A2/B1 with the higher bands reserved in the schema.

Also settles the graph question: verbs form a real graph (182 of the 2000
are prefix derivatives of another verb in the list, and most inherit its
whole conjugation), tenses do not, and the value is in navigation rather
than in a force-directed picture.

## 2026-11-02 — Add the conjugation engine

Rules plus two curated tables - which verbs change their stem, and which are
genuinely irregular. Prefixed verbs inherit from their base (detener from
tener), which is how 182 of the 2000 get conjugated for free, with an
explicit exclusion list for the ones that look derived but are not
(compensar is regular where pensar is not).

Verified: 140 hand-checked forms, and all 41 yo/vos pairs already written by
hand in data/tables/top-verbs-voseo.tsv come back out unchanged.

Negative commands generate both forms. Sources disagree on Paraguay - several
say the subjunctive there simply takes the tu forms, while the voseo
subjunctive is widely heard in Rioplatense speech - so the tu-subjunctive
"no tengas" leads and the voseo "no tengás" is shown as the spoken variant.

Also fixes nine corpus headwords the engine rejected: clitics and
parenthesised reflexives in the verb column (deberle, empapar(se)), and
"huelga (hacer)", which was a noun. The sentences were fine and are kept; the
clitic patterns move into the note column.

## 2026-11-02 — Tag every sentence with the verb form it uses

Adds the form and verb_token columns by matching each sentence against the
full paradigm of its verb. 2000 of 2000 rows now match, which also settles
the old question of which token in a sentence IS the verb - the card can
highlight it.

Three constraints make the matching trustworthy rather than merely
confident: accented forms are matched exactly first, because collapsing
accents would merge hablo with habló and lose the very distinction being
recorded; an enclitic can only attach to an imperative, infinitive or gerund,
so "Estirate" is read as the vos command rather than the present; and a
participle used adjectivally is allowed to agree ("Quedó deshabitada").

The tagger found twelve defects that the unit tests could not. Nine were in
the engine: tener, venir and decir were missing from the stem-change table
and the hand-checked slots (yo, vos) are right without it - only 3s exposes
them. Prefixed verbs now inherit a stem change from their base, with five
exclusions where that inference is wrong (presentar is regular, though
presentir really is presiento). Three were in the corpus: rank 260 paired
cargar with a sentence about descargar, rank 881 used enorgullecerse under
the headword orgullecerse, and rank 1808 had "Pilotié", which is not a form
of pilotear.

## 2026-11-02 — Generate the 400 conjugation tables

Three pieces: full paradigms from the engine, a pronunciation respeller, and
just enough English morphology to gloss each row.

The respeller is deterministic because Spanish spelling is - syllabify, find
the stress, map each syllable - with Paraguayan values: seseo, v read as b,
and no yeismo, so ll and y stay apart as "ly" and "y". It reproduces all 14
pronunciations hand-written in the tener table in the proposal, so the output
matches the style that was approved rather than inventing its own.

English needed irregular pasts (a closed list of ~130) and, more awkwardly,
consonant doubling, which depends on stress that spelling does not record:
admit doubles and visit does not. Those are listed too, plus the British rule
that a final -l doubles regardless (travelled, cancelled).

6399 rows for 400 verbs, banded A1/A2/B1. Each row carries its form,
pronunciation, English and a note; the vos/tu contrast is restated on every
verb because it is the thing that matters most here.

## 2026-11-02 — Group all 2000 verbs by topic

Replaces the arbitrary rank blocks with 33 topics in 9 sections, ordered by
what you need first in Asunción rather than by frequency. Frequency survives
as the sort order inside each topic, so within "Buying & paying" you still
meet comprar before regatear.

Three topics beyond the approved 30. The data forced them: the very highest
frequency verbs - hacer, dar, poner, ver, mirar, encontrar - are
general-purpose and fit no scenario at all, and there was nowhere for leisure
(bailar, cantar, jugar, leer), which for someone at risk of an expat bubble is
not a minor category. Hence Doing & handling things, Seeing/hearing/noticing,
and Free time & interests.

Assignment is 651 by exact verb list, 1048 by hand, 301 by gloss keyword. The
keyword sweep needed two rounds of correction because English idioms contain
handling verbs: "to take revenge", "to make peace with" and "to pay attention"
were all being filed under handling or shopping. Generic topics now match only
when the gloss IS the verb, optionally with a particle, and an audit of every
multi-word gloss caught the rest.

Distribution: median 52 verbs per topic, range 8 (Tereré, which is narrow but
culturally load-bearing) to 123 (News & institutions).

## 2026-11-02 — Add the verb edge table and ingest the new data in the build

Edges are derived types only, as agreed: family (378 - prefixed derivatives,
with inheritance checked rather than assumed, 183 inherit and 6 diverge),
pattern (1845), reflexive (524) and takes-infinitive (79).

takes-infinitive replaces the co-occurrence edge from the plan. Matching
conjugated forms in sentences did not survive review: folding accents merged
"este" with "esté" and the pronoun "se" with saber's "sé", and even with exact
matching, nouns that coincide with verb forms (casa, tarde, aumento, río)
produced wrong links. A wrong "see also" on a learning card is worse than
none. An infinitive is unambiguous, and verb + infinitive is the more useful
relation anyway: it shows which verbs take one and which preposition they
take it with - tardar EN llegar, obligar A ir, quedar EN vernos.

The build now validates all of it and fails loudly: every verb must have a
topic that exists, no topic may be empty, every conjugated verb must have a
complete A1 block, and both ends of every edge must be in the corpus.

Conjugations (729 KB) and edges (199 KB) ship as separate files rather than
inline, so first load stays at 450 KB. The service worker caches them
best-effort - addAll rejects atomically, so a missing data file would
otherwise fail the whole install and take offline support for the page with it.

## 2026-11-02 — Reorganise the app around topics and tenses

The rank blocks are gone. In their place a group picker shared by Listen,
Recall and Deck, with two views you toggle between: by topic (33 groups in 9
sections, ordered by what you need first here) and by tense (21 groups in 6
sections, labelled with a model verb so the shape is visible - "vos —
hablás", "ellos — hablaron"). Frequency survives as the sort order inside
every group.

Each card now names the form its sentence uses, and "Forms" unfolds the full
conjugation table with that form highlighted - the card-to-table link. A level
switch raises the table from A1 to A2 or B1. Tapping any row speaks it.

Below the sentence, a sideways row of up to four typed links: what the verb
conjugates like, its reflexive twin, its family, and what it takes after it.
Tapping one follows it to that verb inside the current view.

A fifth tab, Verbs, browses all 400 tables. Its search matches conjugated
forms too, so "tuve" finds tener - and also estar, for estuve.

Deck rows carry their topic and form as chips; tapping either opens that
group in the study view, positioned on that card. Both are searchable, so
"preterite" narrows the deck to 993 rows the same way a Spanish word does.

English morphology needed one more special case: "I be" is not English, and
`be` is the gloss of ser, estar and every "to be able/worth/born" phrase, so
the present now reads I am / you are / he is.

Verified in the browser at 375px: all five tabs render, 2000 cards across 33
topic groups, the tener table matches the approved design row for row, the
level switch goes 9 rows to 16, no console errors, and the Recall blur still
holds.

## 2026-11-02 — Add 766 more sentences so every verb appears across its tenses

The top 150 verbs each gain the forms they were missing, so the by-tense view
has something to show: Commands goes from 195 cards to 285, Imperfect (yo)
from 0 to 124, Perfect from 0 to 145. They sit directly after their base verb
inside whichever group is open, so ser's six forms are read together.

Every one is checked by lib/check_extra.py, which asserts that the sentence
really contains the form it claims, using the conjugation engine rather than
my judgement. It caught fifteen errors: seven sentences where I wrote a
negative command and labelled it a positive imperative ("No te preocupés" is
the voseo subjunctive, not an imperative), "¿Cómo se dice?" filed as a vos
form when it is third person, and - the one I would not have spotted - a ver
imperative written as "Mirá", which is a form of mirar.

Where a verb has no honest first person or imperative the slot is left empty
rather than filled: existir and ocurrir get third-person sentences, gustar,
faltar and valer get the backwards construction they actually use, and ver
gets no vos command at all, because Paraguayans reach for mirá instead.

Two labels the picker was missing are added (imperfect yo, perfect yo), so
nothing falls into the catch-all group any more.

## 2026-11-02 — Build audio per topic instead of per rank range

The pack boundary follows the deck: one walking track per topic, ordered as
the topic is, and including the extra forms. Index entries are keyed by the
sentence key rather than the rank, because the extra forms share their verb's
rank. A separate pack holds every conjugated form, so tapping a row of a
conjugation table plays the real Paraguayan recording rather than the device
voice.

build.py and the audio builders now share lib/corpus.py, because they have to
agree exactly on what the deck contains and on the key of every sentence.
Verified the extraction by diffing dist/index.html before and after: byte
identical.

Packs already on a device are keyed by rank range and point at files that no
longer exist. Rather than let them fail silently at play time, the app now
detects them, says so plainly, and offers to clear them - so the one-off
re-download is a stated cost rather than a mystery.

edge-tts needed upgrading from 7.2.8 to 7.3.1 first: Microsoft rotated the
Sec-MS-GEC token in October 2026 and every synthesis was returning 403. The
previous version is recorded so the change can be reversed.

## 2026-11-02 — Document the reorganisation and fix the stale-pack notice

README now explains why the deck is cut by topic and tense rather than by
rank block, records that negative commands show the tu-subjunctive with the
voseo form named as the spoken variant, and lists the lib/ tools and the
regeneration order. It also states the edge-tts floor: 7.3.1, because anything
older 403s since Microsoft rotated the token.

The stale-pack notice said "1 saved pack is ... and no longer play", and its
button was unstyled.

## 2026-11-02 — Version-stamp the audio packs so immutable caching stays honest

The year-long immutable cache header was written when a pack was a rank range
and genuinely never changed in place. A topic pack does change in place the
moment a sentence inside it is corrected, which would have left every device
holding the old bytes for a year with no way to notice.

Each pack now carries a hash of its index, the app fetches it with ?v=<hash>,
and a saved pack whose published version has moved on shows Update instead of
Saved. A pack saved before versioning existed has no version to compare, so it
is left alone rather than nagged about.

conjugations.json and edges.json get no-cache: the service worker precaches
them at install, so a stale browser copy would be baked into the new cache.

## 2026-11-02 — Replace the 20 rank packs with 33 topic packs

One walking track per topic, in the topic's own order, including the 766
extra forms. 174 MB and 18.9 hours of es-PY audio.

Verified rather than assumed: all 2766 sentences are indexed exactly once
across the 33 packs, every entry carries all five clip offsets, index drift is
within 16 ms on every pack, and sampled offsets across six packs all land on
speech at -18 to -24 dB mean - silence would read about -91.

The old rank packs are deleted. They are unreachable now: the index is keyed
by sentence key, and a pack is found by asking which one contains the key.

## 2026-11-02 — Fix the walking track still looking up clips by rank

play() was converted to the sentence key but playTrack() was not, so the
walking track - the thing that runs with the screen off, which is where most
of the listening hours go - could not find any of the 766 extra forms, and
would have silently fallen through to no audio.

The lock screen now shows the topic as the album rather than the app name,
which is more use when the phone is in a pocket.

Verified: on an extra-form card (key 38x1) the track seeks to its indexed
26.483s and plays.

## 2026-11-02 — Add the hand-written confusable and opposite edges

The derived edges only ever said what a rule could work out - what a verb
conjugates like, its reflexive twin, its prefix family. None of that is the
thing a beginner actually gets wrong, which is choosing ser over estar, or
pedir over preguntar.

These 116 pairs are hand-written and live in data/edges-manual.tsv, merged by
make_edges.py so regenerating the derived edges never clobbers them. One line
per pair, with note_back for the reverse direction, because the useful thing
to say about estar from ser is not the same sentence read backwards.

Nine drafted pairs named verbs outside the 2000 (encontrarse, llamarse,
sentarse, cambiarse, callar, unir, cansarse, desnudar, coger) and were
dropped; build.py fails loudly on a reference to a verb that is not there.

On the card, confusable and opposite now sort ahead of the derived kinds and
the row is capped at four, since mixing up ser and estar costs more than not
knowing which exemplar a verb follows.

## 2026-11-02 — Ignore Python bytecode caches

Running the lib/ scripts leaves lib/__pycache__ behind; it is build output,
not source.

## 2026-11-02 — Write down how to resume the conjugation audio build

The pack is the one outstanding build, and three things about it have each
cost an hour to rediscover: edge-tts below 7.3.1 returns 403 on every
request, ffmpeg's volumedetect reports at info level so -v error hides the
check, and in a cloud container edge-tts pins certifi's CA bundle so the
proxy CA has to be appended to it.

Also records that audio/clips is container-local and does not travel, the
gates, and the work still open.

## 2026-11-03 — Add Wander, a sixth tab that walks the verbs by how they relate

The deck moves through the verbs by rank or by topic. Nothing moved through
them by meaning, though the edges to do it have been sitting in edges.json
since the sideways row was added.

Each card shows one verb and offers three doors out, labelled with what the
link actually is - easily mixed up, the opposite, reflexive twin, same
family, conjugates like, takes an infinitive. The trail along the top is
every verb you have been through and each step is clickable, so a wrong turn
costs one tap. 1-3 take a door, backspace steps back, space plays.

Two things the data forced:

The graph is thinner than three doors a card. Only 179 of 1919 verbs have
three distinct links, and half the commonest verbs have one - ser links to
estar and to nothing else, because its conjugation is its own exemplar and
it heads no family. Inverting the pattern edges does not help: there are 24
exemplars and hablar has 1357 followers, so "a verb that conjugates like
this one" is a random regular verb, which is not a connection worth
offering. Instead a card short of doors tops up from its own topic, then
from the neighbouring ranks.

The back-link is usually the highest-priority door, so the first choice
bounced between two verbs - pensar, creer, pensar. The verb just left is now
held back unless there is nothing else.

Six tabs no longer fit a 360px phone at the old size, so the tab type shrinks
below 380px. Checked down to 320.

## 2026-11-03 — Build the conjugation audio pack, and concatenate by stream copy

conj.mp3 is every one of the 6,399 forms in conjugations.tsv read by the
Paraguayan voice - 116 minutes, 29 MB - with a verb|slot seek index. Tapping
a row of a conjugation table has played the device voice until now; it plays
this instead once the pack is downloaded, and still falls back when it is not.

The first build came out with twelve minutes of index drift. Re-encoding on
concat decodes each input, and the decoder honours the LAME gapless tags, so
every input loses a frame - 0.048s at 24kHz, which over 12,798 clips and gaps
came to -757s. The committed topic packs do not show this because they were
built on a machine whose ffmpeg did not trim; on ffmpeg 6.1 here, the same
script drifts. Stream copy concatenates the frames untouched: drift is now
-0.000s, the audio keeps its first generation rather than being re-encoded a
second time, and the join takes seconds instead of minutes. make_track.py
gets the same fix so the topic packs stay correct wherever they are rebuilt.
The existing packs are unaffected and were not rebuilt.

Verified: all 6,399 rows indexed, no gaps in the map, every sampled offset
lands on speech at about -21 dB with silence between, the Xing header
survives the copy so browsers seek accurately, and in Chromium the pack
downloads and plays - including the last form, at 6932s.

## 2026-11-03 — Update the notes now the audio packs are all built

Records the gapless-trim trap in full, since it cost a 35-minute render: on
ffmpeg 6.1 a re-encoding concat drops a frame per input, so both builders
stream-copy instead.

Wander is done; more hand-written edges takes its place on the open list,
since the graph is still thin enough that Wander tops up from the topic.

## 2026-11-03 — Propose pronunciation on every card

Plan only, for approval. lib/pron.py already respells Spanish and already
feeds the Forms panel and the Verbs tab; what is missing is the cards.

The substantive finding is that phrase() cannot be pointed at a sentence as
it stands. It stresses only the last word by design, which is right for a
conjugated form and wrong for a sentence, and it splits on whitespace, so the
token is "punto." - a word ending in a consonant, which takes final stress by
rule, giving pun-TO instead of PUN-toh. Nothing shipped is affected, since
conjugated forms carry no punctuation.

## 2026-11-03 — Show a pronunciation respelling under every Spanish line

lib/pron.py already respelled Spanish, and already fed the Forms panel and
the Verbs tab. It now reaches the cards: the Listen and Recall sentence, both
lines of a Wander card, every Deck row, and the Basics tables.

phrase() could not be pointed at prose. It stresses only the last word, which
is right for a conjugated form and wrong for a sentence, and it splits on
whitespace, so the token was «punto.» - a word ending in a consonant, which
takes final stress by rule, giving pun-TO instead of PUN-toh. sentence() holds
the punctuation aside, stresses every word, and leaves grammatical words and
every one-syllable word unmarked, since the capitals say WHICH syllable is
stressed and on a word with one syllable they only add noise.

  al-mor-SAH-mos ah meh-dee-oh-DEE-ah en PUN-toh.

Three engine bugs found while testing it:

- ü was treated as a silent u after g, which is backwards - the dieresis
  exists precisely to say the u is pronounced. pingüino read ping-UI-noh.
- x between vowels did not split across the syllable break: eh-KSAH-men for
  examen, where it should be ek-SAH-men. Fixed by rewriting it to ks before
  syllabifying, which also fixes taxi. 32 conjugation rows change, all for
  the better (exigir, existir).
- The conjunction y produced nothing, having no vowel in the table.

Mexican x is now read as an h, and Guaraní is left exactly as written - its
vowels and glottal stop do not exist in Spanish orthography and Spanish rules
mangle them, so the jopara-guaraní table is skipped and any word carrying ã,
ĩ, õ, ũ, ẽ, ỹ or an apostrophe is passed through untouched.

Generated at build time into dist/pron.json (214 KB, 64 KB over the wire),
fetched with the other extras and precached, rather than reimplemented in
JavaScript: one respeller behind one gate beats two that drift apart.

lib/test_pron.py is that gate - 49 hand-checked words, 9 sentences, the
accent pairs, and the whole corpus for crashes, empty output and lost
punctuation.

In Recall the line hides with the Spanish and returns when you reveal it,
and a Settings switch turns it off for good. Default on.

## 2026-11-03 — Note the respeller gate and that there is only one respeller

## 2026-11-03 — Add a browser test suite, and fix what it found

test/site.mjs drives the built site in Chromium against any URL - the live
deploy by default, or a local http.server before pushing. 133 checks across
14 suites: delivery and content types, data integrity, boot, the six tabs,
Listen, Recall, Wander, Deck, Verbs, Basics, settings, persistence, offline,
and three viewport widths. Non-zero exit on failure, so it can gate a deploy.

It is a plain script rather than @playwright/test because this repo has no
node toolchain at all; TEST-PLAN.md records when that trade flips.

Two real faults on the live site, both in netlify.toml:

- pron.json had no no-cache header. The rule above it exists because the
  service worker precaches these files at install, so a stale browser copy
  gets baked into the new cache - exactly the trap pron.json was walking into
  from the day it was added.
- manifest.webmanifest was served as application/octet-stream. Some browsers
  refuse to install a PWA whose manifest does not carry its own type.

Two further failures were the suite's own: the title assertion was
case-sensitive, and the offline check looked for window.PRON. PRON is a
top-level let, which is a lexical global and not a property of window, so it
has to be referenced bare the way the page's own code sees it.

## 2026-11-03 — Point the notes at the browser suite

## 2026-11-03 — Stamp the build so the deployed site can be asked what it is

A CDN serves a cached response that looks exactly like a fresh one, so there
was no way to tell from outside whether the live site matched the repo. While
checking whether a netlify.toml change had deployed, that turned out to be
unanswerable - which is a gap in a suite whose whole job is testing the live
site.

build.py now writes dist/build.json holding the same hash it stamps into
sw.js, and the suite reads it, prints what is deployed, and checks the page
and the service worker came from one build. The stamp is served no-store; a
cached answer to "what is live" is worse than none.

## 2026-11-03 — Probe whether new netlify.toml header rules are applied at all

## 2026-11-03 — Serve the manifest as manifest.json so the PWA can install

Netlify has no MIME mapping for .webmanifest and sends it as
application/octet-stream, which some browsers refuse to install a PWA from.

A Content-Type override in netlify.toml does not reliably fix it. The CDN
stores a response's headers against the body's ETag, and a header-only config
change leaves that ETag untouched - so revalidation returns 304 and the old
headers keep being served. Four deploys and a probe header confirmed it: the
file content went live in 30 seconds each time while the headers never moved.

The .json extension sidesteps the whole problem. It gets application/json
from Netlify's own map, which browsers accept for a manifest, and a new path
is a new cache entry with no stored headers to go stale. build.json on this
same site already proved the type is right.

The suite now checks the served type is JSON of some kind, and that the page
links the manifest it actually serves.

## 2026-11-03 — Record what testing the live site taught us about the CDN

Netlify stores response headers against the body's ETag, so a header-only
config change is invisible: revalidation returns 304 and the old headers keep
being served, for as long as the body does not change. That is why the
manifest moved to a .json path rather than being fixed with a Content-Type
override, and why pron.json still answers with the default - which is not
worth chasing, since max-age=0 with must-revalidate already forces the
revalidation the no-cache rule was asking for.

## 2026-11-14 — Propose re-sorting every example into the category it belongs in

Proposal only - no data is changed. topic-moves-proposed.tsv holds all 329
moves, one row per sentence, with its current topic, the proposed one and why.

The cause of transport examples in Food is that the topic belongs to the verb,
not the sentence: assign_topics.py reads the verb and its English gloss and
nothing else, and all seven of that verb's sentences inherit the answer. tomar
is filed under Ordering & eating, which is fair for the verb and wrong for
"Tomé el colectivo equivocado". Some verbs are misfiled outright - crear, whose
sentences are about creating accounts and documents, sits in Food.

The proposal splits the topics in two. Situation topics are re-sorted strictly.
The six core-verb topics are left alone, because they exist to drill one verb
across many situations and sorting them by content would scatter hacer across
four topics. That choice is the open question in the write-up.

Seven new categories, each a cluster that already exists and is currently
scattered - studying is spread over 19 topics today.

Method: a word-boundary pass over all 2,766 sentences flagged 384 naming
another domain, of which about a third were rejected on reading; a keyword pass
cannot see a verb that is wrong but names nothing, so the head sentence of
every verb in the situation topics was read as well.

## 2026-11-14 — Record that questions go one at a time, as multiple choice

## 2026-11-14 — Re-sort every example into the category it is actually about

329 sentences move: 265 head sentences and 64 extras, 12% of the corpus. The
list, with a reason per row, is topic-moves-proposed.tsv.

The topic used to belong to the verb, not the sentence. assign_topics.py reads
the verb and its English gloss and nothing else, so all seven of a verb's
sentences inherited one answer - tomar under Ordering & eating dragged "Tomé el
colectivo equivocado" and "He tomado mucho sol hoy" along with it, and crear
sat in Food while its sentences talked about accounts and documents.

sentences_extra.tsv gains a topic column so a sentence can finally sit
somewhere other than with its verb. It is empty for the 702 extras that should
keep inheriting; only the 64 that wandered carry their own. The 265 head moves
also go into overrides.tsv, so regenerating the derived topics cannot quietly
undo the hand work.

Seven new topics, each a cluster that already existed and was scattered -
studying was spread over 19 topics:

  Studying & learning            39
  Building & construction        26
  Cleaning & chores              19
  Moving country & settling in   19
  Travel & staying away          17
  The campo: farming & animals    9
  Celebrations, church & rites    7

The six core-verb topics are untouched. Being & feeling, Doing & handling and
the rest exist to drill one verb across many situations, so "Hace mucho calor"
and "Hice el trámite" belong together under hacer. Sorting those by content
would scatter hacer across four topics and destroy what they teach. 133
sentences a strict reading would have moved are deliberately left alone.

Terere nearly triples, 8 to 20, which is the clearest sign the old scheme was
wrong: "Tomamos tereré todas las tardes" was filed under Ordering & eating
because tomar is a verb about consuming things.

Gates and the 136-check browser suite pass. The audio packs are built per
topic and have not been rebuilt, so 353 sentences' audio still sits in their
old topic's pack and the seven new topics have no walking track yet. Nothing
is orphaned - every sentence still has audio somewhere - and playback falls
back to the device voice.

## 2026-11-14 — Record the topic model and what the repo shrink now has to do

The sweep is applied, so the notes explain the model it left: the topic
belongs to the sentence, not the verb, and six core-verb topics must not be
re-sorted by content.

The shrink now has a second job. Rebuilding the per-topic audio packs was
deferred into it deliberately, so the packs are rebuilt onto the slimmed repo
rather than adding 180 MB that the rewrite then has to undo.

## 2026-11-14 — Let the topic builder take a concurrency, and fix build_all.sh

make_track.py was pinned at 6 parallel TTS requests. Through the agent proxy
latency rather than the service is the limit, where 10 runs at about 180
clips a minute against 56 - the difference between one hour and four on a
full rebuild. Same flag make_conj_track.py already had.

build_all.sh still looped `--start/--end` over 100-verb rank packs, which
stopped existing when the deck was reorganised by topic twenty commits ago.
It now builds every topic and rebuilds the site so packs.json matches.

## 2026-11-14 — Rebuild the first 29 topic packs for the re-sorted deck

Partial, because the build is still running. These 29 are the packs the log
confirms finished; the remaining 11 follow when they are written, along with
the regenerated packs.json. dist/audio is internally inconsistent until then,
which is why packs.json is deliberately not touched in this commit.

Every pack reports drift -0.000s, including the new topics. This is the first
time the topic builder has run on ffmpeg 6.1, where a re-encoding concat would
have dropped a frame per input; the stream-copy fix holds.

## 2026-11-14 — Rebuild the remaining 11 topic packs, and the pack manifest

All 40 topic packs now match the re-sorted deck exactly: no sentence sits in
a pack it no longer belongs to, and none is missing from its own topic's
pack. Both were non-zero before this - 353 sentences' audio was stranded in
their old topic, and the seven new topics had no walking track at all.

Every pack reports drift -0.000s, and sampled offsets across the new topics
land on speech at about -20 dB. packs.json goes in with them, so the version
hashes the app caches on match what is actually served.

42 packs, 214 MB. The repo grows by roughly the 180 MB of topic audio, which
is the cost that was weighed when this was deferred and then asked for.

## 2026-11-14 — Update the notes now every topic pack is rebuilt

42 packs, the build_all.sh entry point, and the trap that caused this work:
moving sentences between topics strands their audio in the old topic's pack
and leaves the new topic's walking track short. build.py does not catch it.

The deferred-rebuild item is gone from Still open; the repo shrink stays, now
at ~355 MB and with two generations of dead pack blobs to drop.

## 2026-11-14 — Give the classification its own file, and a gate that cannot be fooled

You found two sentences in Bank, cash & phone credit that had been moved out
of it: "Me he convertido en uno más del barrio" and "Me convertí en un
fanático del tereré". Both moves were written correctly and then silently
deleted, along with 50 others.

check_extra.py rewrote data/sentences_extra.tsv from a hardcoded column list
with extrasaction='ignore'. The topic column added for the re-sort was not in
that list, so running the gate deleted it - the documented check destroyed
the data it was meant to protect. No error, and every gate still passed,
because they checked that topics were valid and never that they were the ones
written.

This is the third time a generator rewriting a file from a fixed schema has
eaten hand-made data here; overrides.tsv exists because of the same failure in
assign_topics.py. So:

- data/classification.tsv is now the single owner of what a sentence is
  about, keyed by sentence key, hand-made, generated by nothing. Scene is the
  one category a sentence browses under; tags are everything else that is
  also true, so "Me convertí en un fanático del tereré" can be tereré and
  becoming at once instead of being wrong either way.
- check_extra.py reads the columns from the file instead of dictating them.
  A generator that owns a file must not own its schema.
- lib/check_classification.py round-trips: it loads the corpus the way the app
  does and compares every sentence against the file, so anything eating the
  data fails loudly. It also catches missing rows, unknown scenes and unknown
  tags; negative-tested against all three.
- build.py runs it. A check you have to remember to run is not a guarantee.

The 52 lost moves are restored. Tags are seeded empty - the hand pass over all
2,766 sentences comes next, under the approved scene+tags model.

## 2026-11-14 — Re-scene the being-feeling drills (1/6)

95 sentences move from the being-feeling topic to the scene each is actually
about, carrying drill:being-feeling so ser, estar, hacer and quedar can still
be studied as a set. hacer now spreads across Weather, Studying, Free time,
Paperwork, Feelings and Work, which is where its sentences were always
pointing.

being-feeling is removed from topics/_index.tsv now that no sentence uses it
as a scene. The gate caught that it had emptied, which is what it is for.

## 2026-11-14 — Re-scene seeing-noticing, yes-no-maybe and thinking-knowing (4/6)

295 more sentences move to the scene they are about, each carrying its
drill: tag. Those three scenes are now empty and leave _index.tsv.

390 of the 707 core-verb sentences are done. doing-handling and change-cause
remain.

## 2026-11-14 — Re-scene doing-handling and change-cause, finishing the core-verb pass (6/6)

317 more sentences, and the last two core-verb scenes leave _index.tsv. All
707 are done: every sentence now sits in the scene it is about and carries a
drill: tag naming the family it came from, so hacer, poner, llevar and the
rest can still be studied as sets.

34 scenes, down from 40, because the six that were grammar drills rather than
situations are now tags. Sections stay contiguous. Nothing is empty.

Gates and the 136-check browser suite pass.

## 2026-11-14 — Tag the sentences that genuinely sit in two scenes

125 cross-scene tags, on top of the 707 drill tags. 832 of 2,766 sentences
now carry one.

Not all 2,059 remaining sentences got a tag, because most do not deserve one -
a tag is for a sentence with two real readings, not a box to fill. The noun
detector offered 146 candidates and about a seventh were incidental mentions
rather than dual membership: "Te banco en lo que decidas" is not about money,
"Encalló en el banco de arena" is not about a bank, and a sentence that merely
waits half an hour is not about tereré.

The pass also caught a misfile the scene sweep had missed: "Subí al colectivo
equivocado" was in The house & renting, inherited from subir's "Subí al segundo
piso". It is in Transport now.

The commonest second reading is the heat, which is the right answer for this
country - it turns up in sleep, health, food spoiling, metal bending and
whether you go running.

## 2026-11-14 — Drop the six dead scene packs, rebuild the first scenes

Partial: the rebuild is still running. The six packs removed here are for
scenes that no longer exist - being-feeling, doing-handling, yes-no-maybe,
seeing-noticing, thinking-knowing and change-cause became drill: tags, so
nothing browses them and nothing should carry their audio.

The remaining packs and packs.json follow when the build finishes.

## 2026-11-14 — Rebuild every scene pack for the new classification

34 packs for 34 scenes. No sentence's audio sits in a pack it does not
belong to, none is missing from its own, and no pack survives for a scene
that no longer exists - all three were non-zero before this, because the
core-verb pass moved 707 sentences and dissolved six scenes.

Drift is 0.000s on every pack and sampled offsets land on speech at about
-20 dB. 36 packs in all with conj and tables, 213.8 MB.

This is the single rebuild the classification work was sequenced to need:
scenes were finished first, so the audio is built once against final scenes
rather than twice.

## 2026-11-14 — Update the notes for the scene/tag model

Records what classification.tsv is, that the six core-verb families are tags
rather than scenes, and the rule the whole episode turned on: never let a
generator own a file's schema.

Adds surfacing the tags to Still open - they are correct but invisible - and
marks the repo shrink at 470 MB with three generations of pack blobs.

