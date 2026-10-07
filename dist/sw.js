// Offline shell for 2000 Verbos.
//
// BUILD is replaced by build.py with a hash of the generated page, so every
// deploy gets its own cache and the old one is deleted on activate. Without
// that, a hardcoded cache name plus cache-first HTML means a returning visitor
// is pinned to whatever build they first loaded, forever.
const BUILD = '3cad3c6408fc';
const CACHE = 'verbos-shell-' + BUILD;
const SHELL = ['./', './index.html', './manifest.webmanifest', './icon.svg'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Audio packs are stored as Blobs in IndexedDB, not here - media elements seek
// with Range requests a cached Response can't satisfy. Never intercept them.
const isAudio = url => url.pathname.includes('/audio/');

// The document itself must be network-first or updates never land. Falling back
// to cache keeps it working offline; ignoring the query string stops every
// ?v=N variant becoming its own cache entry.
const isDocument = (req, url) =>
  req.mode === 'navigate' ||
  url.pathname === '/' ||
  url.pathname.endsWith('/index.html');

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  if (isAudio(url)) return;

  if (isDocument(req, url)) {
    e.respondWith(
      fetch(req)
        .then(res => {
          if (res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then(c => c.put('./index.html', copy));
          }
          return res;
        })
        .catch(() => caches.match('./index.html', { ignoreSearch: true }))
    );
    return;
  }

  // Everything else (icons, manifest, packs.json) is small and changes rarely:
  // serve from cache but refresh in the background.
  e.respondWith(
    caches.match(req, { ignoreSearch: true }).then(hit => {
      const net = fetch(req).then(res => {
        if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
        return res;
      }).catch(() => hit);
      return hit || net;
    })
  );
});
