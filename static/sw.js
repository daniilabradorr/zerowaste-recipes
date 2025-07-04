self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open("zw-static-v1").then((cache) =>
      cache.addAll([
        "/static/manifest.json",
        "/static/img/icon-192.png",
        "/static/img/icon-512.png"
      ])
    )
  );
});

self.addEventListener("fetch", (e) => {
  if (e.request.url.startsWith(self.location.origin + "/static/")) {
    e.respondWith(
      caches.match(e.request).then((resp) => resp || fetch(e.request))
    );
  }
});
