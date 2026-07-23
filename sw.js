const CACHE_NAME = 'greens-vip-v1';
const assets = [
  'painel.html',
  'manifest.json',
  'bot_espn_logo.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(assets))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});