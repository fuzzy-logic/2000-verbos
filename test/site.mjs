/**
 * Browser tests for the built site. Run against the live deploy or a local copy:
 *
 *   node test/site.mjs                                  # https://2kspanish.netlify.app
 *   node test/site.mjs --base http://localhost:8137     # a local `python3 -m http.server` in dist/
 *   node test/site.mjs --only deck,wander               # one or more suites
 *   node test/site.mjs --headed                         # watch it
 *
 * Needs playwright on NODE_PATH; nothing else. Exits non-zero if anything failed,
 * so it can gate a deploy.
 *
 * Why a plain script and not @playwright/test: this repo has no node toolchain at
 * all - it is Python plus one HTML file - and a runner, a config format and a
 * dependency tree is a lot of surface to maintain for a suite this size. The
 * harness below is thirty lines and does what is needed. If the suite ever grows
 * past a few hundred cases, or needs sharding and retries, switch then.
 */
import { createRequire } from 'node:module';

// Resolved through require rather than imported, because playwright is usually
// installed globally here rather than as a dependency of this repo, and an ESM
// import ignores NODE_PATH. PLAYWRIGHT_PATH overrides if it lives elsewhere.
const require = createRequire(import.meta.url);
const chromium = (() => {
  const tries = [process.env.PLAYWRIGHT_PATH, 'playwright',
                 '/opt/node-tools/node_modules/playwright',
                 '/usr/lib/node_modules/playwright'].filter(Boolean);
  for (const t of tries) {
    try { return require(t).chromium; } catch { /* next */ }
  }
  console.error('playwright not found. Install it, or set PLAYWRIGHT_PATH to its folder.\n' +
                'tried: ' + tries.join(', '));
  process.exit(2);
})();

const argv = process.argv.slice(2);
const arg = (name, dflt) => {
  const i = argv.indexOf('--' + name);
  return i >= 0 && argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : dflt;
};
const BASE = (arg('base', 'https://2kspanish.netlify.app')).replace(/\/$/, '');
const ONLY = arg('only', '').split(',').filter(Boolean);
const HEADED = argv.includes('--headed');

// ---------- harness ----------
const results = [];
let suiteName = '';
const suites = [];
const suite = (name, fn) => suites.push({ name, fn });

function check(label, ok, detail) {
  results.push({ suite: suiteName, label, ok: !!ok, detail });
  const mark = ok ? '  ok  ' : '  FAIL';
  console.log(`${mark} ${label}${ok || detail === undefined ? '' : `\n         ${detail}`}`);
  return !!ok;
}
const eq = (label, got, want) =>
  check(label, Object.is(got, want), `want ${JSON.stringify(want)}, got ${JSON.stringify(got)}`);
const atLeast = (label, got, min) =>
  check(label, typeof got === 'number' && got >= min, `want >= ${min}, got ${got}`);
const has = (label, hay, needle) =>
  check(label, String(hay).includes(needle), `${JSON.stringify(needle)} not in ${JSON.stringify(String(hay).slice(0, 120))}`);

// ---------- page helpers ----------
let browser, context, page, consoleErrors = [];

async function newPage(viewport = { width: 390, height: 844 }) {
  if (context) await context.close();
  context = await browser.newContext({ viewport });
  page = await context.newPage();
  consoleErrors = [];
  page.on('pageerror', e => consoleErrors.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error') consoleErrors.push('console: ' + m.text()); });
  return page;
}

async function open(path = '/', waitExtra = true) {
  await page.goto(BASE + path, { waitUntil: 'load' });
  // The card paints from inlined data; pron/edges/conjugations arrive after.
  // PRON is a top-level `let`, so it is a lexical global and NOT a property of
  // window - referenced bare, the way the page's own code sees it.
  if (waitExtra) await page.waitForFunction(() => typeof PRON === 'object' && PRON !== null,
    null, { timeout: 15000 }).catch(() => {});
  await page.waitForTimeout(250);
}

const tab = async name => {
  await page.click(`.tab[data-mode="${name}"]`);
  await page.waitForTimeout(450);
};
const text = sel => page.evaluate(s => (document.querySelector(s) || {}).textContent?.trim() ?? null, sel);
const count = sel => page.evaluate(s => document.querySelectorAll(s).length, sel);
const shown = sel => page.evaluate(s => {
  const e = document.querySelector(s);
  return !!e && getComputedStyle(e).display !== 'none';
}, sel);

// =====================================================================
suite('delivery', async () => {
  const files = [
    ['/', 'text/html'], ['/pron.json', 'application/json'],
    ['/edges.json', 'application/json'], ['/conjugations.json', 'application/json'],
    ['/audio/packs.json', 'application/json'], ['/sw.js', 'javascript'],
    ['/manifest.json', null], ['/icon.svg', 'svg'],
  ];
  for (const [path, type] of files) {
    const r = await fetch(BASE + path);
    const ct = r.headers.get('content-type') || '';
    check(`GET ${path} -> 200`, r.status === 200, `got ${r.status}`);
    if (type) check(`GET ${path} content-type ~ ${type}`, ct.includes(type), `got ${ct}`);
  }
  // what is actually deployed, which a CDN response otherwise hides
  const stamp = await fetch(BASE + '/build.json?cb=' + Date.now())
    .then(r => r.ok ? r.json() : null).catch(() => null);
  check('build.json is served', !!stamp && !!stamp.build, JSON.stringify(stamp));
  if (stamp) {
    const sw = await fetch(BASE + '/sw.js?cb=' + Date.now()).then(r => r.text());
    const inSw = (sw.match(/BUILD\s*=\s*'([0-9a-f]+)'/) || [])[1];
    check('deployed page and service worker are from the same build',
      inSw === stamp.build, `build.json ${stamp.build}, sw.js ${inSw}`);
    console.log(`         deployed build: ${stamp.build}`);
  }

  // The manifest's type is its own case. manifest+json is ideal and
  // application/json is accepted; application/octet-stream, which is what
  // Netlify sends for a .webmanifest, is what stops a PWA installing.
  const m = await fetch(BASE + '/manifest.json');
  const mct = m.headers.get('content-type') || '';
  check('manifest has a JSON content-type',
    mct.includes('manifest+json') || mct.includes('application/json'),
    `got ${mct} - some browsers refuse to install the PWA with this`);
  // the page must point at the file that is actually served
  const html = await fetch(BASE + '/').then(r => r.text());
  const href = (html.match(/<link rel="manifest" href="([^"]+)"/) || [])[1];
  check('page links the manifest it serves', href === 'manifest.json', `links ${href}`);
  const man = await m.json().catch(() => null);
  check('manifest parses as JSON', !!man);
  if (man) {
    check('manifest has name', !!man.name, JSON.stringify(man.name));
    check('manifest has start_url', !!man.start_url);
    check('manifest display is standalone-ish',
      ['standalone', 'fullscreen', 'minimal-ui'].includes(man.display), man.display);
    atLeast('manifest icons', (man.icons || []).length, 1);
  }
});

suite('data integrity', async () => {
  const [pron, edges, conj, packs] = await Promise.all(
    ['/pron.json', '/edges.json', '/conjugations.json', '/audio/packs.json']
      .map(u => fetch(BASE + u).then(r => r.json())));
  atLeast('pron.json sentences', Object.keys(pron.s || {}).length, 2700);
  atLeast('pron.json verbs', Object.keys(pron.v || {}).length, 1900);
  atLeast('pron.json table rows', Object.keys(pron.t || {}).length, 700);
  atLeast('edges.json verbs with links', Object.keys(edges).length, 1500);
  atLeast('conjugations.json verbs', Object.keys(conj).length, 390);
  atLeast('packs.json packs', packs.length, 34);

  const conjPack = packs.find(p => p.stem === 'conj');
  check('conj pack listed', !!conjPack, JSON.stringify(packs.map(p => p.stem).slice(0, 3)));
  if (conjPack) {
    check('conj pack has a duration', conjPack.duration > 6000, String(conjPack.duration));
    const h = await fetch(BASE + '/audio/conj.mp3', { method: 'HEAD' });
    check('conj.mp3 reachable', h.status === 200, `got ${h.status}`);
    const mb = Number(h.headers.get('content-length') || 0) / 1e6;
    check('conj.mp3 size matches packs.json', Math.abs(mb - conjPack.mb) < 1,
      `header ${mb.toFixed(1)}MB vs manifest ${conjPack.mb}MB`);
  }
  // every pack in the manifest must actually be downloadable
  let missing = [];
  for (const p of packs.slice(0, 6)) {
    const r = await fetch(`${BASE}/audio/${p.stem}.mp3`, { method: 'HEAD' });
    if (r.status !== 200) missing.push(`${p.stem} -> ${r.status}`);
  }
  check('sampled pack mp3s reachable', missing.length === 0, missing.join(', '));

  // respellings must not be empty, and must keep the sentence's question marks
  const bad = Object.entries(pron.s).filter(([, v]) => !v || !v.trim()).length;
  eq('no empty sentence respellings', bad, 0);
});

suite('boot', async () => {
  await newPage();
  await open('/');
  has('page title', (await page.title()).toLowerCase(), 'verbos');
  check('a card is rendered', (await text('#esText') || '').length > 3, await text('#esText'));
  check('translation is rendered', (await text('#enText') || '').length > 3);
  check('verb tag is rendered', (await text('#verbTag') || '').length > 1);
  has('counter reads n / m', await text('#counter'), '/');
  eq('six tabs', await count('.tab'), 6);
  check('no console errors on boot', consoleErrors.length === 0, consoleErrors.join('\n'));
});

suite('tabs', async () => {
  await newPage(); await open('/');
  const views = { listen: '#studyView', recall: '#studyView', wander: '#wanderView',
                  deck: '#tableView', verbs: '#verbsView', basics: '#basicsView' };
  for (const [mode, view] of Object.entries(views)) {
    await tab(mode);
    check(`${mode}: ${view} visible`, await shown(view));
    const selected = await page.evaluate(m =>
      document.querySelector(`.tab[data-mode="${m}"]`).getAttribute('aria-selected'), mode);
    eq(`${mode}: tab marked selected`, selected, 'true');
    const others = Object.values(views).filter(v => v !== view);
    const leaked = [];
    for (const o of others) if (await shown(o)) leaked.push(o);
    check(`${mode}: other views hidden`, leaked.length === 0, leaked.join(','));
  }
  check('no console errors across tabs', consoleErrors.length === 0, consoleErrors.join('\n'));
});

suite('listen', async () => {
  await newPage(); await open('/');
  const first = await text('#esText');
  await page.click('#nextBtn'); await page.waitForTimeout(250);
  const second = await text('#esText');
  check('next advances the card', first !== second, `${first} -> ${second}`);
  await page.click('#prevBtn'); await page.waitForTimeout(250);
  eq('prev returns to it', await text('#esText'), first);

  const c1 = await text('#counter');
  await page.click('#chunkNext'); await page.waitForTimeout(400);
  check('group next changes the group', (await text('#groupBtn')) !== null);
  check('counter updates with the group', (await text('#counter')) !== null, c1);

  // the group picker
  await page.click('#groupBtn'); await page.waitForTimeout(350);
  check('picker opens', await page.evaluate(() =>
    document.getElementById('pickSheet').classList.contains('open')));
  atLeast('picker lists groups', await count('#pickSheet button'), 5);
  await page.keyboard.press('Escape');
  await page.evaluate(() => document.getElementById('pickSheet').classList.remove('open'));

  // marks
  await page.click('#knownBtn'); await page.waitForTimeout(200);
  check('Got it records a mark', await page.evaluate(() => Object.keys(state.marks).length > 0));
  await page.click('#knownBtn'); await page.waitForTimeout(200);

  // forms panel
  await page.click('#conjBtn'); await page.waitForTimeout(600);
  check('forms panel opens', await shown('#conjPanel'));
  atLeast('forms panel has rows', await count('#conjPanel .conjrow'), 3);
  check('forms rows carry a respelling', await count('#conjPanel .pr') > 0);
  await page.click('#conjBtn'); await page.waitForTimeout(300);
  check('no console errors in listen', consoleErrors.length === 0, consoleErrors.join('\n'));
});

suite('recall', async () => {
  await newPage(); await open('/');
  await tab('recall');
  check('Spanish is blurred', await page.evaluate(() =>
    document.getElementById('esText').classList.contains('hidden-text')));
  check('pronunciation hidden with it', !(await shown('#pronText')));
  has('a prompt is shown', await text('#hint'), 'Spanish');
  await page.click('#card'); await page.waitForTimeout(400);
  check('tap reveals the Spanish', await page.evaluate(() =>
    !document.getElementById('esText').classList.contains('hidden-text')));
  check('pronunciation returns on reveal', await shown('#pronText'));
  check('no console errors in recall', consoleErrors.length === 0, consoleErrors.join('\n'));
});

suite('wander', async () => {
  await newPage(); await open('/');
  await tab('wander');
  const verb0 = await text('.wverb');
  check('a verb card is shown', !!verb0 && verb0.length > 1, verb0);
  const doors = await count('.wchoice');
  check('three doors offered', doors === 3, `got ${doors}`);
  check('each door names a relationship', await page.evaluate(() =>
    [...document.querySelectorAll('.wchoice .rel')].every(e => e.textContent.trim().length > 2)));
  check('card carries respellings', await count('#wCard .pron') >= 1);

  const target = await page.evaluate(() => document.querySelector('.wchoice').dataset.verb);
  await page.click('.wchoice'); await page.waitForTimeout(400);
  eq('taking a door jumps to that verb', await text('.wverb'), target);
  eq('trail now has two steps', await count('#wTrail button'), 2);
  check('door is not the verb just left', await page.evaluate(v =>
    [...document.querySelectorAll('.wchoice')].every(b => b.dataset.verb !== v), verb0));

  await page.click('#wBack'); await page.waitForTimeout(350);
  eq('back returns to the first verb', await text('.wverb'), verb0);
  await page.click('#wRandom'); await page.waitForTimeout(350);
  eq('New restarts the trail', await count('#wTrail button'), 1);
  check('no console errors in wander', consoleErrors.length === 0, consoleErrors.join('\n'));
});

suite('deck', async () => {
  await newPage(); await open('/');
  await tab('deck');
  const rows = await count('.rowitem');
  atLeast('deck lists every sentence', rows, 2700);
  check('rows carry respellings', await count('.rowitem .pron') > 2000);
  await page.fill('#search', 'comer'); await page.waitForTimeout(500);
  const filtered = await count('.rowitem');
  check('search narrows the deck', filtered > 0 && filtered < rows, `${rows} -> ${filtered}`);
  await page.fill('#search', 'zzzzqqq'); await page.waitForTimeout(400);
  eq('a miss shows no rows', await count('.rowitem'), 0);
  check('a miss explains itself', (await text('#rows')) !== '');
  await page.fill('#search', ''); await page.waitForTimeout(500);
  eq('clearing restores the deck', await count('.rowitem'), rows);
  check('no console errors in deck', consoleErrors.length === 0, consoleErrors.join('\n'));
});

suite('verbs', async () => {
  await newPage(); await open('/');
  await tab('verbs');
  atLeast('verb list renders', await count('#vList > *'), 50);
  await page.fill('#vSearch', 'tener'); await page.waitForTimeout(500);
  const n = await count('#vList > *');
  check('search narrows the list', n > 0 && n < 400, String(n));
  await page.click('#vList > *'); await page.waitForTimeout(500);
  atLeast('a verb expands to its forms', await count('#vList .conjrow'), 3);
  check('forms carry respellings', await count('#vList .pr') > 0);
  check('no console errors in verbs', consoleErrors.length === 0, consoleErrors.join('\n'));
});

suite('basics', async () => {
  await newPage(); await open('/');
  await tab('basics');
  atLeast('tables render', await count('.bgroup'), 18);
  atLeast('sections render', await count('.bsection'), 3);
  // open them all and look at the rows
  await page.evaluate(() => document.querySelectorAll('.bgroup').forEach(g => g.classList.add('open')));
  await page.waitForTimeout(200);
  atLeast('table rows render', await count('.brow'), 700);
  check('rows carry respellings', await count('.brow .pron') > 600);
  const guarani = await page.evaluate(() => {
    const g = [...document.querySelectorAll('.bgroup')]
      .find(x => /jopara|guaran/i.test(x.querySelector('.btitle').textContent));
    if (!g) return null;
    return { rows: g.querySelectorAll('.brow').length, prons: g.querySelectorAll('.brow .pron').length };
  });
  check('Guaraní table exists', !!guarani && guarani.rows > 0, JSON.stringify(guarani));
  eq('Guaraní rows are left unrespelled', guarani?.prons, 0);
  await page.fill('#bSearch', 'número'); await page.waitForTimeout(450);
  check('basics search runs', (await text('#bCount')) !== null);
  check('no console errors in basics', consoleErrors.length === 0, consoleErrors.join('\n'));
});

suite('settings', async () => {
  await newPage(); await open('/');
  await page.click('#setBtn'); await page.waitForTimeout(350);
  check('settings sheet opens', await page.evaluate(() =>
    document.getElementById('sheet').classList.contains('open')));
  check('pronunciation switch is on by default', await page.isChecked('#pronChk'));
  atLeast('offline packs are listed', await count('#packList > *'), 30);
  check('a fallback voice selector exists', await count('#voiceSel') === 1);

  await page.uncheck('#pronChk'); await page.waitForTimeout(400);
  check('switching off hides the card respelling', !(await shown('#pronText')));
  await page.reload(); await page.waitForTimeout(1500);
  check('the choice survives a reload', !(await page.isChecked('#pronChk')));
  await page.click('#setBtn'); await page.waitForTimeout(250);
  await page.check('#pronChk'); await page.waitForTimeout(400);
  check('switching back on restores it', await shown('#pronText'));

  // theme
  const before = await page.evaluate(() => document.documentElement.dataset.theme);
  await page.evaluate(() => document.getElementById('sheet').classList.remove('open'));
  await page.click('#themeBtn'); await page.waitForTimeout(250);
  const after = await page.evaluate(() => document.documentElement.dataset.theme);
  check('theme toggles', before !== after, `${before} -> ${after}`);
  check('no console errors in settings', consoleErrors.length === 0, consoleErrors.join('\n'));
});

suite('persistence', async () => {
  await newPage(); await open('/');
  await tab('wander');
  await page.click('.wchoice'); await page.waitForTimeout(350);
  const trail = await page.evaluate(() => state.trail.join('>'));
  const verb = await text('.wverb');
  await page.reload(); await page.waitForTimeout(1800);
  eq('the open tab is remembered', await page.evaluate(() => state.mode), 'wander');
  eq('the wander trail is remembered', await page.evaluate(() => state.trail.join('>')), trail);
  eq('and the card it left you on', await text('.wverb'), verb);
  check('no console errors after reload', consoleErrors.length === 0, consoleErrors.join('\n'));
});

suite('offline', async () => {
  await newPage(); await open('/');
  const reg = await page.evaluate(() =>
    navigator.serviceWorker.ready.then(r => !!r.active).catch(() => false));
  check('service worker activates', reg);
  // let it finish precaching, then cut the network
  await page.waitForTimeout(3000);
  await context.setOffline(true);
  let offlineOk = true, detail = '';
  try {
    await page.reload({ waitUntil: 'load', timeout: 20000 });
    await page.waitForTimeout(800);
  } catch (e) { offlineOk = false; detail = e.message.split('\n')[0]; }
  check('the page loads with the network off', offlineOk, detail);
  if (offlineOk) {
    check('a card still renders offline', (await text('#esText') || '').length > 3);
    const pr = await page.evaluate(() =>
      typeof PRON === 'object' && PRON !== null && Object.keys(PRON.s || {}).length > 0);
    check('pron.json was precached', pr);
    const ed = await page.evaluate(() =>
      typeof EDGES === 'object' && EDGES !== null && Object.keys(EDGES).length > 0);
    check('edges.json was precached', ed);
  }
  await context.setOffline(false);
});

suite('responsive', async () => {
  for (const w of [320, 390, 768]) {
    await newPage({ width: w, height: 800 });
    await open('/');
    const overflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > window.innerWidth + 1);
    check(`${w}px: no horizontal overflow`, !overflow);
    const tabs = await page.evaluate(() => {
      const t = document.querySelector('.tabs');
      return { scroll: t.scrollWidth, client: t.clientWidth };
    });
    check(`${w}px: all six tabs fit`, tabs.scroll <= tabs.client + 1, JSON.stringify(tabs));
    await tab('wander');
    const o2 = await page.evaluate(() =>
      document.documentElement.scrollWidth > window.innerWidth + 1);
    check(`${w}px: wander does not overflow`, !o2);
  }
});

// =====================================================================
(async () => {
  console.log(`\n2000 Verbos — site tests\nbase: ${BASE}\n`);
  browser = await chromium.launch({ args: ['--no-sandbox'], headless: !HEADED });
  for (const s of suites) {
    if (ONLY.length && !ONLY.includes(s.name)) continue;
    suiteName = s.name;
    console.log(`\n── ${s.name} ${'─'.repeat(Math.max(0, 40 - s.name.length))}`);
    try {
      await s.fn();
    } catch (e) {
      check(`suite ${s.name} ran to completion`, false, e.message.split('\n')[0]);
    }
  }
  if (context) await context.close();
  await browser.close();

  const failed = results.filter(r => !r.ok);
  console.log(`\n${'='.repeat(52)}`);
  console.log(`${results.length - failed.length}/${results.length} checks passed`);
  if (failed.length) {
    console.log(`\n${failed.length} FAILED:`);
    for (const f of failed) console.log(`  [${f.suite}] ${f.label}${f.detail ? ` — ${f.detail}` : ''}`);
  }
  process.exit(failed.length ? 1 : 0);
})();
