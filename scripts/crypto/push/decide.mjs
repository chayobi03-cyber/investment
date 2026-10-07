// Pure alert decision for the B3+ push. Dedupes per asset and daily decision
// bar so a state that holds is announced at most once per completed candle.

export const ALERT_STATES = new Set(["B3", "B4"]);

export const symbolOf = (snapshot) => String(snapshot.asset || "BTCUSDT").replace(/USDT?$/, "");

export function decideAlert(snapshot, lastState = {}) {
  const state = snapshot.daily_core_state;
  const bar = snapshot.decision_bar;
  if (!ALERT_STATES.has(state)) return { send: false, reason: `state ${state} below B3` };
  if (lastState.decision_bar === bar) return { send: false, reason: `already sent for ${bar}` };
  return { send: true, reason: `${state} on ${bar}` };
}

// State file is { BTC: {decision_bar, ...}, ETH: {...} }. Files written before
// multi-asset support held a single BTC entry at the top level.
export function stateFor(state, symbol) {
  if (state && typeof state.decision_bar === "string") return symbol === "BTC" ? state : {};
  return (state && state[symbol]) || {};
}

export function formatUsd(x) {
  return x >= 1000
    ? Math.round(x).toLocaleString("en-US")
    : x.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export function buildMessage(snapshot, pageUrl) {
  const sym = symbolOf(snapshot);
  const dd = ((snapshot.live_price / snapshot.prior_high60 - 1) * 100).toFixed(1);
  const url = new URL(pageUrl);
  url.searchParams.set("asset", sym);
  return {
    title: `${sym} ${snapshot.daily_core_state} · ${snapshot.daily_zone}`,
    body: `$${formatUsd(snapshot.live_price)} (60일 고점 대비 ${dd}%) · 연구용 신호, 매수 권한 BLOCKED`,
    tag: `entry-${sym}-${snapshot.decision_bar}`,
    url: url.href,
  };
}

export function parseSubscriptions(raw) {
  if (!raw || !raw.trim()) return [];
  const parsed = JSON.parse(raw);
  return Array.isArray(parsed) ? parsed : [parsed];
}
