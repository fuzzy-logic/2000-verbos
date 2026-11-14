# A better way to classify the sentences

Proposal. Nothing has been changed.

## 1. What you found, and why it happened

You saw these in *Bank, cash & phone credit*:

> Me he convertido en uno más del barrio.
> Me convertí en un fanático del tereré.

Both were in my sweep. Both were written correctly. Both were then **silently
deleted**, along with 50 others.

`lib/check_extra.py` owns `data/sentences_extra.tsv` and rewrites it from a
hardcoded column list:

```python
COLS = ['verb', 'form', 'sentence_es', 'sentence_en', 'note', 'verb_token']
w = csv.DictWriter(fh, COLS, delimiter='\t', extrasaction='ignore', ...)
```

`extrasaction='ignore'` means any column not in that list is dropped without a
word. I added a `topic` column to that file; the next `python3 build.py` threw
it away. No error, no warning, and the gates still passed — because the gates
check that topics are *valid*, never that they are *the ones that were written*.

52 of 329 moves are wrong on the live site right now. I can restore them in
about two minutes whenever you want; say the word and it is independent of
everything below.

**This is the third time this codebase has lost hand-made data to a generator
that rewrites a file from a fixed schema.** `data/topics/overrides.tsv` exists
because of the same failure in `assign_topics.py`. That is the real lesson
here, and the proposal is built around it.

## 2. What is actually wrong with the scheme

Beyond the bug, three things are wrong by design.

**The unit is the verb, not the sentence.** `assign_topics.py` reads a verb and
its English gloss and nothing else. Seven sentences inherit one answer. That is
the original cause of transport examples in Food, and no amount of override
patching fixes the shape of it.

**One label is forced where two are true.** Your own example proves it. "Me
convertí en un fanático del tereré" is about tereré *and* about becoming
something. Whichever single box I tick, the other reading looks like a mistake
— which is exactly what you experienced. About a fifth of the corpus is like
this.

**Two different kinds of category sit in one flat list.** *Ordering & eating*
is a situation. *Doing & handling* is a grammar drill. They answer different
questions and cannot be sorted by the same rule, which is why my last sweep
needed a special case for six of the forty.

## 3. The proposal

### One file owns the classification

A new `data/classification.tsv`, one row per sentence, keyed by the sentence
key the whole project already uses (`14`, `14x3`):

```
key     scene              tags
14      conversation-opinion
30x3    transport-colectivo
70x2    terere-drinking    change-cause
5x4     weather-heat       drill:hacer
```

Nothing generates it, nothing rewrites it, no script owns a column list that
could drop it. `verbs_*.tsv` and `sentences_extra.tsv` go back to holding only
the sentence and its grammar, which is what they are good at. The `topic`
column leaves both, so there is nothing left for `check_extra.py` to clobber.

### Two axes instead of one list

**`scene`** — one per sentence, compulsory. Where you would actually use it.
This is the partition: it drives the Deck's topic browse, the audio packs and
the walking tracks, all of which need every sentence to be in exactly one
place.

**`tags`** — zero or more. Everything else that is true about the sentence:
another scene it touches, or a grammar drill it belongs to. Tags drive search,
filtering and the card's "see also" row. They do not partition anything, so
they can overlap freely and nothing breaks.

So the tereré sentence gets `scene: terere-drinking`, `tags: change-cause`. It
appears under Tereré, where you expect it, and still surfaces when you study
*becoming*. Nobody has to be wrong.

### What happens to the six core-verb topics

*Being & feeling*, *Doing & handling*, *Yes-no-maybe*, *Seeing & noticing*,
*Thinking & knowing* and *Change & cause* stop being scenes and become
`drill:` tags. Their sentences move to the scenes they are actually about —
"Hace mucho calor" to Weather, "Hice el trámite" to Paperwork — and you can
still study all of `hacer` together by its tag, the same way the Verbs tab
already groups by verb.

This is the part worth arguing about, so it is a separate option below.

### Gates that would have caught this

1. **Round-trip gate.** Build, reload the corpus, compare every sentence's
   scene against `classification.tsv`. Any difference fails. This catches the
   exact bug that bit us, and any future one like it.
2. **`check_extra.py` stops owning the file's schema** — it preserves unknown
   columns instead of listing the ones it knows.
3. **Coverage gate.** Every sentence has a scene, every scene exists in the
   index, every tag exists, no scene is empty.

## 4. How the 2,766 would be classified

Not by keyword. My last sweep showed a keyword pass proposing a wrong answer
about a third of the time — it wanted "Me baño dos veces por día con este
calor" filed under Weather.

I would read all 2,766 and assign scene and tags by hand, in topic-sized
batches, writing them straight into `classification.tsv`. The keyword pass
survives only to order the work and to flag anything I skipped.

That is the expensive option and the only honest one. It is a one-off: the
corpus is fixed at 2,000 verbs.

## 5. Cost

| | |
|---|---|
| Restore the 52 lost moves | ~2 min, independent of all this |
| Schema change + gates | ~1 hour |
| Full hand classification of 2,766 | several hours, in batches you can interrupt |
| Rebuilding the audio packs afterwards | ~1 hour, and another ~180 MB of git unless it is folded into the shrink |

The audio point matters: scenes drive the packs, so a re-scene means a rebuild.
Worth doing that once, at the end, and ideally inside the repo shrink that is
already pending.

## 6. What I need decided

See the question I am about to ask — the shape of the taxonomy. Everything
else follows from it.
