// Pure alert decision for the B3+ push. Dedupes per daily decision bar so a
// state that holds is announced at most once per completed daily candle.

export const ALERT_STATES = new Set(["B3", "B4"]);

export function decideAlert(snapshot, lastState = {}) {
  const state = snapshot.daily_core_state;
  const bar = snapshot.decision_bar;
  if (!ALERT_STATES.has(state)) return { send: false, reason: `state ${state} below B3` };
  if (lastState.decision_bar === bar) return { send: false, reason: `already sent for ${bar}` };
  return { send: true, reason: `${state} on ${bar}` };
}

export function buildMessage(snapshot, pageUrl) {
  const price = Math.round(snapshot.live_price).toLocaleString("en-US");
  const dd = ((snapshot.live_price / snapshot.prior_high60 - 1) * 100).toFixed(1);
  return {
    title: `BTC ${snapshot.daily_core_state} · ${snapshot.daily_zone}`,
    body: `$${price} (60일 고점 대비 ${dd}%) · 연구용 신호, 매수 권한 BLOCKED`,
    tag: `btc-entry-${snapshot.decision_bar}`,
    url: pageUrl,
  };
}

export function parseSubscriptions(raw) {
  if (!raw || !raw.trim()) return [];
  const parsed = JSON.parse(raw);
  return Array.isArray(parsed) ? parsed : [parsed];
}
