// Direct browser fetches from Coinbase's public API (CORS-enabled, no key).
// Mirrors get_daily()/get_live_price() in scripts/crypto/live_entry_snapshot.py.

const BASE = "https://api.exchange.coinbase.com/products/BTC-USD";
const DAY_MS = 86400 * 1000;

async function getJson(url, timeoutMs) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const resp = await fetch(url, { signal: ctrl.signal, cache: "no-store" });
    if (!resp.ok) throw new Error(`HTTP ${resp.status} ${url}`);
    return await resp.json();
  } finally {
    clearTimeout(timer);
  }
}

export async function getDaily(days = 365, now = Date.now()) {
  const end = Math.floor(now / DAY_MS) * DAY_MS;
  const start = end - (days + 2) * DAY_MS;
  const byTs = new Map();
  let cursor = end;

  while (cursor > start) {
    const batchStart = Math.max(start, cursor - 300 * DAY_MS);
    const params = new URLSearchParams({
      granularity: "86400",
      start: new Date(batchStart).toISOString(),
      end: new Date(cursor).toISOString(),
    });
    const batch = await getJson(`${BASE}/candles?${params}`, 30000);
    if (!batch.length) break;
    for (const [t, low, high, open, close, volume] of batch) {
      byTs.set(t * 1000, { low, high, open, close, volume });
    }
    cursor = batchStart - 1000;
  }

  return [...byTs.entries()]
    .map(([timestamp, c]) => ({
      timestamp,
      available_at: timestamp + DAY_MS,
      open: Number(c.open),
      high: Number(c.high),
      low: Number(c.low),
      close: Number(c.close),
      volume: Number(c.volume),
    }))
    .filter((r) => r.available_at <= now)
    .sort((a, b) => a.timestamp - b.timestamp)
    .slice(-days);
}

export async function getLivePrice() {
  const t = await getJson(`${BASE}/ticker`, 15000);
  return Number(t.price);
}
