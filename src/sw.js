// Offline shell for 2000 Verbos.
// Audio packs are deliberately NOT cached here - they live as Blobs in IndexedDB,
// because a media element seeks via Range requests that a cached Response won't
// satisfy without hand-rolling 206 replies. This only covers the app itself.
const CACHE = 'verbos-shell-v1';
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

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  // Let audio downloads go straight to the network; they're stored in IndexedDB,
  // and duplicating 150 MB into the cache would be wasteful.
  if (url.pathname.includes('/audio/')) return;

  // Network-first for packs.json so a newly published pack shows up; cache-first
  // for everything else so the app opens instantly and works offline.
  if (url.pathname.endsWith('packs.json')) {
    e.respondWith(fetch(req).catch(() => caches.match(req)));
    return;
  }
  e.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(res => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      return res;
    }).catch(() => caches.match('./index.html')))
  );
});
