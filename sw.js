// Köy Fırını servis çalışanı: oyunu önbelleğe alır, internet yokken de açılır.
// Oyun sayfası önce internetten istenir (güncelleme hemen gelsin), internet yoksa önbellekten açılır.
// Görseller ve sesler ilk kullanıldıklarında önbelleğe girer; dosya adlarındaki ?v= sürümü değişince yenisi iner.
const SURUM = 'koy-firini-v23';
const DOSYALAR = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './maskable-512.png', './apple-touch-icon.png',
  './assets/items.png?v=21', './assets/logo.png?v=21', './assets/fonts/baloo2-600.woff2?v=21', './assets/fonts/baloo2-800.woff2?v=21'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(SURUM).then(c => c.addAll(DOSYALAR.map(url => new Request(url, {cache: 'reload'})))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('koy-firini-') && k !== SURUM).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  const url = new URL(req.url);
  const root = new URL('./', self.registration.scope);
  // Ayrı oyun sayfaları fırının çevrimdışı kopyasının üzerine yazılamaz.
  const bakery = url.pathname === root.pathname || url.pathname === root.pathname + 'index.html';
  const sayfa = req.mode === 'navigate' || url.pathname.endsWith('.html');
  const pageKey = bakery ? './index.html' : url.origin + url.pathname;
  if (sayfa) {
    e.respondWith(fetch(req, {cache: 'no-store'}).then(res => { if (!res.ok) throw new Error('Sayfa alınamadı'); const k = res.clone(); e.waitUntil(caches.open(SURUM).then(c => c.put(pageKey, k))); return res; })
      .catch(async () => (await caches.match(pageKey)) || Response.error()));
  } else {
    // Yalnızca başarılı ve tam yanıtlar saklanır (ses dosyalarının kısmi 206 yanıtları önbelleğe girmez).
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => { if (res.ok && res.status === 200) { const k = res.clone(); caches.open(SURUM).then(c => c.put(req, k)); } return res; })));
  }
});
