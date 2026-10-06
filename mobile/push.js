import { VAPID_PUBLIC_KEY } from "./push-config.js";

const $ = (id) => document.getElementById(id);

function urlBase64ToUint8Array(s) {
  const pad = "=".repeat((4 - (s.length % 4)) % 4);
  const raw = atob((s + pad).replace(/-/g, "+").replace(/_/g, "/"));
  return Uint8Array.from(raw, (c) => c.charCodeAt(0));
}

const isStandalone = () =>
  window.matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;

function show(sub) {
  $("pushOut").hidden = false;
  $("pushJson").value = JSON.stringify(sub);
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
    const reg = await navigator.serviceWorker.ready;
    const sub =
      (await reg.pushManager.getSubscription()) ||
      (await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      }));
    show(sub);
    $("pushMsg").textContent = "아래 구독 정보를 복사해 GitHub 시크릿 WEBPUSH_SUBSCRIPTIONS에 넣으세요.";
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

// Reflect an existing subscription without prompting.
if ("serviceWorker" in navigator && "PushManager" in window && Notification.permission === "granted") {
  navigator.serviceWorker.ready
    .then((reg) => reg.pushManager.getSubscription())
    .then((sub) => sub && show(sub))
    .catch(() => {});
}
