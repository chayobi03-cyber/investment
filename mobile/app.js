import { buildSnapshot } from "./entry.js";
import { getDaily, getLivePrice } from "./data.js";

const CACHE_KEY = "crypto-entry-v0.2:last-snapshot";
const AUTO_REFRESH_MS = 15 * 60 * 1000; // same cadence as the GitHub Actions monitor
const $ = (id) => document.getElementById(id);

const STATE_TEXT = {
  B0: "관망 — 진입 조건 없음",
  B1: "추격 금지 — 고점 부근",
  B2: "관찰 — 조정/돌파 도달, 안정화 대기",
  B3: "후보 — 안정화 확인",
  B4: "강한 후보 — 깊은 조정 + MA50 회복",
};
const ZONE_TEXT = {
  BREAKOUT: "60일 고점 돌파",
  Z0: "고점 대비 -5% 이내",
  Z1: "-5% ~ -8% 조정",
  Z2: "-8% ~ -12% 조정",
  Z3: "-12% 초과 급락",
  UNKNOWN: "데이터 부족",
};

const usd = (x) => (x == null ? "—" : "$" + Math.round(x).toLocaleString("en-US"));
const pct = (x) => (x == null ? "—" : (x >= 0 ? "+" : "") + (x * 100).toFixed(2) + "%");
const when = (iso) => new Date(iso).toLocaleString("ko-KR", { hour12: false });

function loadCached() {
  try {
    return JSON.parse(localStorage.getItem(CACHE_KEY));
  } catch {
    return null;
  }
}

function saveCached(snap) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(snap));
  } catch {
    /* storage unavailable: still render */
  }
}

function sparkline(points, levels) {
  if (!points?.length) return "";
  const W = 320, H = 90, P = 4;
  const vals = points.map((p) => p[1]);
  const lv = Object.values(levels).filter((v) => v > Math.min(...vals) * 0.9);
  const lo = Math.min(...vals, ...lv), hi = Math.max(...vals, ...lv);
  const x = (i) => P + (i / (points.length - 1)) * (W - 2 * P);
  const y = (v) => H - P - ((v - lo) / (hi - lo || 1)) * (H - 2 * P);
  const path = vals.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join("");
  const guides = Object.entries(levels)
    .filter(([, v]) => v >= lo && v <= hi)
    .map(([k, v]) => `<line x1="0" x2="${W}" y1="${y(v)}" y2="${y(v)}" class="guide"><title>${k}</title></line>`)
    .join("");
  return `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" role="img" aria-label="최근 90일 종가">${guides}<path d="${path}" class="line"/></svg>`;
}

function render(snap, { stale = false, error = null } = {}) {
  $("status").textContent = error
    ? `오프라인/오류 — 마지막 저장값 표시 (${error})`
    : stale
      ? "저장된 스냅샷"
      : "최신";
  $("status").className = "status " + (error ? "bad" : stale ? "warn" : "ok");
  if (!snap) {
    $("main").hidden = true;
    return;
  }
  $("main").hidden = false;
  $("price").textContent = usd(snap.live_price);
  $("liveDd").textContent = `60일 고점 대비 ${pct(snap.live_drawdown60)}`;
  $("state").textContent = snap.daily_core_state;
  $("state").dataset.state = snap.daily_core_state;
  $("stateText").textContent = STATE_TEXT[snap.daily_core_state] ?? "";
  $("reason").textContent = snap.daily_entry_reason ?? "";
  $("liveZone").textContent = snap.live_zone;
  $("liveZoneText").textContent = ZONE_TEXT[snap.live_zone] ?? "";
  $("dailyZone").textContent = snap.daily_zone;
  $("trend").textContent = snap.trend_ok ? "충족" : "미충족";
  $("stab").textContent = snap.stabilization ? "충족" : "미충족";
  $("high60").textContent = usd(snap.prior_high60);
  $("ma").textContent = `${usd(snap.ma.ma20)} / ${usd(snap.ma.ma50)} / ${usd(snap.ma.ma200)}`;
  const L = snap.research_levels;
  $("lvBreak").textContent = usd(L.breakout_confirmation);
  $("lvZ1u").textContent = usd(L.Z1_upper);
  $("lvZ1l").textContent = usd(L.Z1_lower);
  $("lvZ2l").textContent = usd(L.Z2_lower);
  $("chart").innerHTML = sparkline(snap.recent_closes, L);
  $("action").textContent = `${snap.action} · 매수허용 ${snap.buy_allowed ? "예" : "아니오"} · 자동주문 없음`;
  $("bar").textContent = `기준 일봉 ${when(snap.decision_bar)} · 조회 ${when(snap.fetched_at)}`;
}

let busy = false;
async function refresh() {
  if (busy) return;
  busy = true;
  $("refresh").disabled = true;
  $("status").textContent = "불러오는 중…";
  $("status").className = "status";
  try {
    const [daily, live] = await Promise.all([getDaily(365), getLivePrice()]);
    const snap = buildSnapshot(daily, live, "Coinbase BTC-USD public API (browser)");
    snap.fetched_at = new Date().toISOString();
    saveCached(snap);
    render(snap);
  } catch (e) {
    render(loadCached(), { error: e.message || String(e) });
  } finally {
    busy = false;
    $("refresh").disabled = false;
  }
}

$("refresh").addEventListener("click", refresh);
document.addEventListener("visibilitychange", () => {
  const snap = loadCached();
  const age = snap ? Date.now() - Date.parse(snap.fetched_at) : Infinity;
  if (document.visibilityState === "visible" && age > 60 * 1000) refresh();
});
setInterval(() => document.visibilityState === "visible" && refresh(), AUTO_REFRESH_MS);

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("./sw.js").catch(() => {});
}

render(loadCached(), { stale: true });
refresh();
