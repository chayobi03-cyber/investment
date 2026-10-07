// Browser port of src/investment_pipeline/crypto_entry.py (v0.2) and the
// live-zone logic in scripts/crypto/live_entry_snapshot.py.
// Pure functions only: no DOM, no network. Parity is checked by
// tests/test_mobile_entry_parity.py against the Python implementation.

export const V02_COOLDOWN_BARS = 5;
export const V02_BREAKOUT_BUFFER = 0.005;
export const V02_BREAKOUT_VOLUME_RATIO = 1.2;
export const V02_STABILIZATION_GREEN_MIN = 2;

const isNum = (x) => typeof x === "number" && Number.isFinite(x);

export function validateOhlcv(rows) {
  if (!rows.length) throw new Error("empty_frame");
  for (let i = 0; i < rows.length; i++) {
    const r = rows[i];
    for (const k of ["open", "high", "low", "close"]) {
      if (!isNum(r[k])) throw new Error("non_numeric_ohlc");
      if (r[k] <= 0) throw new Error("non_positive_ohlc");
    }
    if (i > 0) {
      if (r.timestamp === rows[i - 1].timestamp) throw new Error("duplicate_timestamps");
      if (r.timestamp < rows[i - 1].timestamp) throw new Error("timestamps_not_ascending");
    }
    if (r.high < Math.max(r.open, r.close)) throw new Error("invalid_high");
    if (r.low > Math.min(r.open, r.close)) throw new Error("invalid_low");
  }
}

// Trailing window ending at i (inclusive); NaN unless all `n` values are finite.
function rolling(values, i, n, reducer) {
  if (i + 1 < n) return NaN;
  let acc = reducer === "max" ? -Infinity : reducer === "min" ? Infinity : 0;
  for (let j = i - n + 1; j <= i; j++) {
    const v = values[j];
    if (!isNum(v)) return NaN;
    if (reducer === "max") acc = Math.max(acc, v);
    else if (reducer === "min") acc = Math.min(acc, v);
    else acc += v;
  }
  return reducer === "mean" ? acc / n : acc;
}

const gt = (a, b) => isNum(a) && isNum(b) && a > b;
const gte = (a, b) => isNum(a) && isNum(b) && a >= b;

export function addEntryFeatures(input) {
  validateOhlcv(input);
  const close = input.map((r) => r.close);
  const high = input.map((r) => r.high);
  const low = input.map((r) => r.low);
  const hasVolume = input.every((r) => "volume" in r);
  const volume = input.map((r) => (hasVolume ? Number(r.volume) : NaN));
  const green = input.map((r) => (r.close > r.open ? 1 : 0));

  return input.map((r, i) => {
    const ma20 = rolling(close, i, 20, "mean");
    const ma50 = rolling(close, i, 50, "mean");
    const ma200 = rolling(close, i, 200, "mean");
    const ret3 = i >= 3 ? close[i] / close[i - 3] - 1 : NaN;
    const ret5 = i >= 5 ? close[i] / close[i - 5] - 1 : NaN;
    const volumeMa20 = rolling(volume, i, 20, "mean");
    const volumeRatio20 = isNum(volume[i]) && isNum(volumeMa20) ? volume[i] / volumeMa20 : NaN;
    // Reference windows exclude the current decision bar.
    const priorHigh60 = i >= 1 ? rolling(high, i - 1, 60, "max") : NaN;
    const priorHigh20 = i >= 1 ? rolling(high, i - 1, 20, "max") : NaN;
    const priorLow20 = i >= 1 ? rolling(low, i - 1, 20, "min") : NaN;
    const drawdown60 = isNum(priorHigh60) ? close[i] / priorHigh60 - 1 : NaN;

    const trendOk = gt(close[i], ma200) && gt(ma20, ma50) && gt(ma50, ma200);
    const greenLast3 = rolling(green, i, 3, "sum");
    const stabilization =
      gt(ret3, 0) && gte(close[i], ma20) && trendOk && gte(greenLast3, V02_STABILIZATION_GREEN_MIN);
    const breakout =
      gte(close[i], priorHigh60 * (1 + V02_BREAKOUT_BUFFER)) &&
      gt(close[i], priorHigh60) &&
      gt(ret3, 0) &&
      gte(volumeRatio20, V02_BREAKOUT_VOLUME_RATIO) &&
      trendOk;

    let zone = "Z3";
    if (!isNum(drawdown60)) zone = "UNKNOWN";
    else if (drawdown60 > -0.05) zone = "Z0";
    else if (drawdown60 > -0.08) zone = "Z1";
    else if (drawdown60 > -0.12) zone = "Z2";

    return {
      ...r,
      ma20, ma50, ma200, ret3, ret5,
      volume_ma20: volumeMa20,
      volume_ratio20: volumeRatio20,
      prior_high60: priorHigh60,
      prior_high20: priorHigh20,
      prior_low20: priorLow20,
      drawdown60,
      trend_ok: trendOk,
      green_closes_last3: greenLast3,
      stabilization,
      breakout,
      zone,
    };
  });
}

function signal(state, zone, reasons, zoneLow = null, zoneHigh = null) {
  return { state, zone, reason_codes: reasons, zone_low: zoneLow, zone_high: zoneHigh };
}

export function signalFromRow(row) {
  const required = ["close", "ma20", "ma50", "ma200", "ret3", "prior_high60", "drawdown60"];
  if (required.some((k) => !isNum(row[k]))) return signal("B0", "UNKNOWN", ["DATA_NOT_READY"]);

  const { zone } = row;
  const h = row.prior_high60;
  const bounds = { Z1: [h * 0.92, h * 0.95], Z2: [h * 0.88, h * 0.92], Z3: [0, h * 0.88] };

  if (!row.trend_ok) return signal("B0", zone, ["TREND_NOT_READY"]);
  if (row.breakout) {
    return row.stabilization
      ? signal("B3", "BREAKOUT", ["BREAKOUT_CONFIRMED", "TREND_VALID"])
      : signal("B2", "BREAKOUT", ["BREAKOUT_WATCH", "TREND_VALID"]);
  }
  if (zone === "Z0") {
    if (row.drawdown60 >= -0.02) return signal("B1", "Z0", ["NO_CHASE", "PULLBACK_NOT_REACHED"], ...bounds.Z1);
    return signal("B0", "Z0", ["PULLBACK_NOT_REACHED"], ...bounds.Z1);
  }
  if (zone === "Z1" || zone === "Z2") {
    return row.stabilization
      ? signal("B3", zone, ["PULLBACK_STABILIZED", "TREND_VALID"], ...bounds[zone])
      : signal("B2", zone, ["PULLBACK_REACHED", "WAIT_STABILIZATION"], ...bounds[zone]);
  }
  if (zone === "Z3") {
    if (row.stabilization && row.close >= row.ma50) {
      return signal("B4", zone, ["DEEP_DISLOCATION", "STABILIZED", "MA50_RECLAIM"], ...bounds.Z3);
    }
    if (row.stabilization) return signal("B3", zone, ["DEEP_DISLOCATION", "STABILIZED"], ...bounds.Z3);
    return signal("B2", zone, ["DEEP_DISLOCATION", "WAIT_STABILIZATION"], ...bounds.Z3);
  }
  return signal("B0", zone, ["UNRESOLVED"]);
}

export function generateSignals(rows) {
  return addEntryFeatures(rows).map((row) => {
    const s = signalFromRow(row);
    return {
      ...row,
      entry_state: s.state,
      entry_reason: s.reason_codes.join("|"),
      zone_low: s.zone_low,
      zone_high: s.zone_high,
    };
  });
}

export function liveZone(livePrice, priorHigh60) {
  if (livePrice >= priorHigh60 * 1.005) return "BREAKOUT";
  if (livePrice > priorHigh60 * 0.95) return "Z0";
  if (livePrice > priorHigh60 * 0.92) return "Z1";
  if (livePrice > priorHigh60 * 0.88) return "Z2";
  return "Z3";
}

// Same fail-closed contract as scripts/crypto/live_entry_snapshot.py.
export function buildSnapshot(daily, livePrice, dataSource, asset = "BTCUSDT") {
  if (daily.length < 200) throw new Error("DATA_NOT_READY: insufficient completed daily history");
  const signals = generateSignals(daily);
  const last = signals[signals.length - 1];
  const h = last.prior_high60;
  return {
    status: "RESEARCH_ONLY_NOT_VALIDATED",
    rule_version: "crypto-market-regime-entry-v0.2",
    asset,
    data_source: dataSource,
    decision_bar: new Date(last.timestamp).toISOString(),
    decision_bar_available_at: new Date(last.available_at).toISOString(),
    live_price: livePrice,
    daily_core_state: last.entry_state,
    daily_entry_reason: last.entry_reason,
    daily_zone: last.zone,
    live_zone: liveZone(livePrice, h),
    trend_ok: last.trend_ok,
    stabilization: last.stabilization,
    prior_high60: h,
    drawdown60: last.drawdown60,
    live_drawdown60: livePrice / h - 1,
    ma: { ma20: last.ma20, ma50: last.ma50, ma200: last.ma200 },
    research_levels: {
      Z1_upper: h * 0.95,
      Z1_lower: h * 0.92,
      Z2_lower: h * 0.88,
      breakout_confirmation: h * 1.005,
    },
    promotion_gate: {
      threshold_evidence: "FAIL",
      full_buy_permission: "BLOCKED",
      automatic_order: false,
    },
    buy_allowed: false,
    action: "BLOCKED_UNVALIDATED",
    invalidation: ["P0_DATA_NOT_READY", "THRESHOLD_OOS_FAIL", "FULL_PERMISSION_LAYER_NOT_PROMOTED"],
    recent_closes: signals.slice(-90).map((r) => [r.timestamp, r.close]),
  };
}
