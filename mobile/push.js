// Opt-in for B3+ push alerts. The VAPID key pair is generated on this phone and
// never committed: the copied secret entry carries the subscription together
// with its private key, which only the monitor workflow (repo secret) can read.

const KEY_STORE = "crypto-entry-v0.2:vapid";
const $ = (id) => document.getElementById(id);
const b64url = (buf) =>
  btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const fromB64url = (s) =>
  Uint8Array.from(atob(s.replace(/-/g, "+").replace(/_/g, "/") + "=".repeat((4 - (s.length % 4)) % 4)), (c) =>
    c.charCodeAt(0));

const isStandalone = () =>
  window.matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;

async function vapidKeys() {
  try {
    const saved = JSON.parse(localStorage.getItem(KEY_STORE));
    if (saved?.publicKey && saved?.privateKey) return saved;
  } catch {
    /* fall through and generate */
  }
  const pair = await crypto.subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign"]);
  const keys = {
    publicKey: b64url(await crypto.subtle.exportKey("raw", pair.publicKey)),
    privateKey: (await crypto.subtle.exportKey("jwk", pair.privateKey)).d,
  };
  try {
    localStorage.setItem(KEY_STORE, JSON.stringify(keys));
  } catch {
    /* without storage a later visit just re-subscribes with a new key */
  }
  return keys;
}

function show(sub, keys) {
  $("pushOut").hidden = false;
  $("pushJson").value = JSON.stringify({ ...sub.toJSON(), vapid_private_key: keys.privateKey });
}

async function enable() {
  $("pushMsg").textContent = "";
  try {
    if (!("serviceWorker" in navigator) || !("PushManager" in window)) {
      throw new Error(
        isStandalone()
          ? "이 브라우저는 웹 푸시를 지원하지 않습니다."
          : "아이폰은 홈 화면에 추가한 앱에서 열어야 알림을 켤 수 있습니다.",
      );
    }
    if ((await Notification.requestPermission()) !== "granted") {
      throw new Error("알림 권한이 거부되었습니다. 설정에서 허용해 주세요.");
    }
    const keys = await vapidKeys();
    const reg = await navigator.serviceWorker.ready;
    let sub = await reg.pushManager.getSubscription();
    const own = sub && b64url(sub.options.applicationServerKey) === keys.publicKey;
    if (sub && !own) await sub.unsubscribe();
    if (!own) {
      sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: fromB64url(keys.publicKey),
      });
    }
    show(sub, keys);
    $("pushMsg").textContent = "아래 값을 복사해 GitHub 시크릿 WEBPUSH_SUBSCRIPTIONS에 넣으세요. 비밀번호처럼 다루세요.";
  } catch (e) {
    $("pushMsg").textContent = e.message || String(e);
  }
}

async function copy() {
  try {
    await navigator.clipboard.writeText($("pushJson").value);
    $("pushMsg").textContent = "복사됨";
  } catch {
    $("pushJson").select();
  }
}

$("pushOn").addEventListener("click", enable);
$("pushCopy").addEventListener("click", copy);
