// App-shell cache so the installed app opens offline. Market data is never
// cached here: app.js keeps the last computed snapshot in localStorage instead.
const SHELL = "btc-entry-shell-v2";
const FILES = [
  "./", "./index.html", "./style.css", "./app.js", "./entry.js", "./data.js", "./push.js", "./push-config.js",
  "./manifest.webmanifest", "./icons/icon-180.png", "./icons/icon-192.png", "./icons/icon-512.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(SHELL).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== SHELL).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return; // live API calls go straight to network
  // Network first so updates land; fall back to the shell cache offline.
  e.respondWith(
    fetch(e.request)
      .then((resp) => {
        const copy = resp.clone();
        caches.open(SHELL).then((c) => c.put(e.request, copy));
        return resp;
      })
      .catch(() => caches.match(e.request, { ignoreSearch: true })),
  );
});

self.addEventListener("push", (e) => {
  let msg = {};
  try {
    msg = e.data ? e.data.json() : {};
  } catch {
    msg = { body: e.data && e.data.text() };
  }
  e.waitUntil(
    self.registration.showNotification(msg.title || "BTC 진입 모니터", {
      body: msg.body || "",
      tag: msg.tag || "btc-entry",
      icon: "icons/icon-192.png",
      badge: "icons/icon-192.png",
      data: { url: msg.url || "./" },
    }),
  );
});

self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  const target = new URL(e.notification.data?.url || "./", self.registration.scope).href;
  e.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((list) => {
      const open = list.find((c) => c.url.startsWith(self.registration.scope));
      return open ? open.focus() : self.clients.openWindow(target);
    }),
  );
});
