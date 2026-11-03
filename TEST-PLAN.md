# Testing

What is tested, how to run it, and what is still missing.

## The two layers

| | what it covers | runs in |
|---|---|---|
| `lib/test_*.py` | the generators — conjugation engine, respeller, extra sentences | Python, no browser, < 2s |
| `test/site.mjs` | the built site in a real browser, against any URL | Chromium via Playwright, ~60s |

They answer different questions. The Python gates ask *is the data right*. The
browser suite asks *does the thing people use actually work*. A change can pass
one and fail the other, which is the point of having both.

## Running them

```sh
# data gates
python3 -I lib/test_conjugate.py
python3 -I lib/test_pron.py
python3 -I lib/check_extra.py
python3 build.py                     # fails loudly on broken references

# the live deploy
node test/site.mjs

# a local build, before pushing
cd dist && python3 -m http.server 8137 &
node test/site.mjs --base http://localhost:8137

# one suite, or watch it happen
node test/site.mjs --only wander,deck
node test/site.mjs --headed
```

Exit code is non-zero if anything failed, so either can gate a deploy.

Playwright is resolved through `require`, not imported, because it is usually
installed globally rather than as a dependency of this repo — there is no
`package.json` and no node toolchain here. Set `PLAYWRIGHT_PATH` if it lives
somewhere unusual.

## Why a plain script, not @playwright/test

The repo is Python plus one HTML file. A test runner brings a config format, a
dependency tree and a lockfile to maintain, for a suite of this size. The
harness in `site.mjs` is about thirty lines — `check`, `eq`, `atLeast`, `has`,
a suite list, and a summary that sets the exit code.

The point at which that trade flips: when the suite needs retries for flake,
parallel shards to stay fast, or trace/video capture on failure. Then move to
`@playwright/test` and keep the same suite layout.

## What the browser suite covers

| suite | checks |
|---|---|
| `delivery` | every file 200s with the right content-type; manifest parses and has name, start_url, display, icons |
| `data integrity` | pron/edges/conjugations/packs sizes; `conj.mp3` reachable and its size matches the manifest; sampled pack mp3s reachable; no empty respellings |
| `boot` | page title, first card paints, counter, six tabs, no console errors |
| `tabs` | each of the six shows its own view and hides the other five, and is marked selected |
| `listen` | next/prev, group nav, the group picker, progress marks, the Forms panel and its respellings |
| `recall` | the Spanish is blurred, the respelling hides with it, tap reveals both |
| `wander` | three doors, each labelled; taking one jumps and extends the trail; the door back is withheld; Back and New |
| `deck` | all 2,766 rows, respellings present, search narrows, a miss explains itself, clearing restores |
| `verbs` | list renders, search narrows, a verb expands to its forms with respellings |
| `basics` | 18 tables, rows render with respellings, and the Guaraní table has none |
| `settings` | sheet opens, pack list, pronunciation switch off/on and across a reload, theme toggle |
| `persistence` | tab, wander trail and position survive a reload |
| `offline` | the service worker activates, the page loads with the network cut, a card renders, pron and edges were precached |
| `responsive` | 320 / 390 / 768px: no horizontal overflow, all six tabs fit |

## Not covered, and why

- **Audio playback.** Seek offsets are verified at build time with ffmpeg, which
  is the honest test — a headless browser will report that it sought to the
  requested second whether or not the right words are there. The one end-to-end
  playback check lives in the conj pack's build notes.
- **Downloading a pack.** 29 MB against the live site, per run. The suite checks
  the manifest and that the files are reachable instead.
- **Device speech synthesis.** Headless Chromium has no Spanish voice, so the
  TTS fallback cannot be exercised here. It needs a real device.
- **Visual regression.** No screenshot baselines. Worth adding if the layout
  starts churning; today the responsive checks catch the failure that actually
  happened (six tabs overflowing a narrow phone).
- **iOS Safari.** The PWA install path and audio behaviour differ there and are
  not covered by Chromium.

## What testing the live site taught us

**You cannot see a header change take effect.** Netlify's CDN stores a
response's headers against the body's ETag. A header-only config change leaves
that ETag untouched, so revalidation returns 304 and the *stored* headers keep
being served — indefinitely, for a file whose body never changes. Four deploys
and a deliberate probe header confirmed it: file content went live in 30
seconds every time while headers never moved.

Consequences worth remembering:

- A `Content-Type` override in `netlify.toml` is not a reliable fix. The
  manifest is served from `manifest.json` instead, which gets
  `application/json` from Netlify's own MIME map. A new path is a new cache
  entry with no stored headers to go stale.
- `pron.json` and `build.json` still answer with Netlify's default
  `public, max-age=0, must-revalidate` rather than the `no-cache` and
  `no-store` in the config. This is not worth chasing: both force
  revalidation before use, so the behaviour is already what the rule asks
  for, and the explicit header will appear the next time either body changes.
- Query-string cache busters do not help — the CDN ignores them — and neither
  does a `Cache-Control: no-cache` request header.

**A deployed site needs to be able to say what it is.** Without
`dist/build.json` there was no way to tell a fresh response from a cached one
that looked identical, which made "has the fix deployed?" unanswerable. The
suite now reports the deployed build and checks the page and service worker
came from the same one.

## Next

1. Run `--base http://localhost:8137` before every push, as a pre-deploy gate.
2. Add a GitHub Action: the Python gates on every push, the browser suite
   against the Netlify deploy preview.
3. Screenshot baselines for the card, Wander and Basics, once the layout settles.
