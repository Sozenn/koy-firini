// Köy Fırını servis çalışanı: oyunu önbelleğe alır, internet yokken de açılır.
// Oyun sayfası önce internetten istenir (güncelleme hemen gelsin), internet yoksa önbellekten açılır.
const SURUM = 'koy-firini-v14';
const DOSYALAR = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './maskable-512.png', './apple-touch-icon.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(SURUM).then(c => c.addAll(DOSYALAR.map(url => new Request(url, {cache: 'reload'})))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('koy-firini-') && k !== SURUM).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  const sayfa = req.mode === 'navigate' || new URL(req.url).pathname.endsWith('/index.html');
  if (sayfa) {
    e.respondWith(fetch(req, {cache: 'no-store'}).then(res => { if (!res.ok) throw new Error('Sayfa alınamadı'); const k = res.clone(); e.waitUntil(caches.open(SURUM).then(c => c.put('./index.html', k))); return res; })
      .catch(() => caches.match('./index.html')));
  } else {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => { const k = res.clone(); caches.open(SURUM).then(c => c.put(req, k)); return res; })));
  }
});

