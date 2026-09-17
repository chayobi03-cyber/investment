import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const KIS_BASE = "https://openapi.koreainvestment.com:9443";
const RULE_VERSION = "market-auto-acquisition-v1";

const DEFAULT_SYMBOLS = [
  "005930", "000660", "006400", "105560", "005380",
  "000810", "096770", "034020", "035420", "207940",
];

function requireEnv(name: string): string {
  const value = Deno.env.get(name);
  if (!value) throw new Error(`Missing required secret: ${name}`);
  return value;
}

function requireSupabaseServerKey(): string {
  const grouped = Deno.env.get("SUPABASE_SECRET_KEYS");
  if (grouped) {
    try {
      const parsed = JSON.parse(grouped) as Record<string, unknown>;
      const key = parsed.default;
      if (typeof key === "string" && key) return key;
    } catch {
      // Fall through to legacy variable for backwards compatibility.
    }
  }
  return requireEnv("SUPABASE_SERVICE_ROLE_KEY");
}

function num(value: unknown): number | null {
  if (value === null || value === undefined || value === "") return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function parseSymbols(): string[] {
  const raw = Deno.env.get("KIS_SYMBOLS")?.trim();
  if (!raw) return DEFAULT_SYMBOLS;
  const symbols = raw.split(",").map((s) => s.trim()).filter(Boolean);
  return symbols.length ? symbols : DEFAULT_SYMBOLS;
}

async function issueAccessToken(appKey: string, appSecret: string): Promise<string> {
  const response = await fetch(`${KIS_BASE}/oauth2/tokenP`, {
    method: "POST",
    headers: { "content-type": "application/json; charset=utf-8" },
    body: JSON.stringify({ grant_type: "client_credentials", appkey: appKey, appsecret: appSecret }),
  });
  const body = await response.json();
  if (!response.ok || (body.rt_cd !== undefined && body.rt_cd !== "0")) {
    throw new Error(`KIS token failure: ${response.status} ${JSON.stringify(body)}`);
  }
  if (!body.access_token) throw new Error("KIS token response missing access_token");
  return body.access_token as string;
}

async function inquirePrice(token: string, appKey: string, appSecret: string, symbol: string) {
  const url = new URL(`${KIS_BASE}/uapi/domestic-stock/v1/quotations/inquire-price`);
  url.searchParams.set("FID_COND_MRKT_DIV_CODE", "UN");
  url.searchParams.set("FID_INPUT_ISCD", symbol);
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      authorization: `Bearer ${token}`,
      appKey,
      appSecret,
      tr_id: "FHKST01010100",
      custtype: "P",
    },
  });
  const body = await response.json();
  if (!response.ok || body.rt_cd !== "0") {
    throw new Error(`KIS price failure ${symbol}: ${response.status} ${JSON.stringify(body)}`);
  }
  return (body.output ?? {}) as Record<string, unknown>;
}

function observationTimestamp(output: Record<string, unknown>, fallback: Date): string {
  const date = String(output.bsop_date ?? "").trim();
  const time = String(output.stck_cntg_hour ?? "").trim();
  if (/^\d{8}$/.test(date) && /^\d{6}$/.test(time)) {
    const parsed = new Date(`${date.slice(0, 4)}-${date.slice(4, 6)}-${date.slice(6, 8)}T${time.slice(0, 2)}:${time.slice(2, 4)}:${time.slice(4, 6)}+09:00`);
    if (!Number.isNaN(parsed.getTime())) return parsed.toISOString();
  }
  return fallback.toISOString();
}

async function insertRows(rows: Record<string, unknown>[]): Promise<void> {
  const supabaseUrl = requireEnv("SUPABASE_URL");
  const serverKey = requireSupabaseServerKey();
  const response = await fetch(`${supabaseUrl}/rest/v1/market_observations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      apikey: serverKey,
      Authorization: `Bearer ${serverKey}`,
      Prefer: "return=minimal,resolution=ignore-duplicates",
    },
    body: JSON.stringify(rows),
  });
  if (!response.ok) throw new Error(`Supabase insert failure: ${response.status} ${await response.text()}`);
}

Deno.serve(async (req: Request) => {
  try {
    const expectedSecret = requireEnv("MARKET_COLLECTOR_SECRET");
    const suppliedSecret = req.headers.get("x-market-collector-secret");
    if (!suppliedSecret || suppliedSecret !== expectedSecret) {
      return new Response(JSON.stringify({ ok: false, error: "unauthorized" }), { status: 401, headers: { "content-type": "application/json" } });
    }

    const appKey = requireEnv("KIS_APP_KEY");
    const appSecret = requireEnv("KIS_APP_SECRET");
    const symbols = parseSymbols();
    const runId = crypto.randomUUID();
    const availableAt = new Date();
    const token = await issueAccessToken(appKey, appSecret);

    const rows: Record<string, unknown>[] = [];
    const failures: Record<string, string> = {};

    for (const symbol of symbols) {
      try {
        const output = await inquirePrice(token, appKey, appSecret, symbol);
        const observedAt = observationTimestamp(output, new Date());
        rows.push({
          run_id: runId,
          source_id: "KIS_OPEN_API",
          source_version: "current",
          feed: "UN",
          instrument_type: "KOREAN_EQUITY",
          symbol,
          market_session: String(output.market_cls_code ?? output.new_mkop_cls_code ?? "UNKNOWN"),
          observed_at: observedAt,
          available_at: new Date().toISOString(),
          raw_value: num(output.stck_prpr),
          price: num(output.stck_prpr),
          change_pct: num(output.prdy_ctrt),
          volume: num(output.acml_vol),
          turnover: num(output.acml_tr_pbmn),
          open_price: num(output.stck_oprc),
          high_price: num(output.stck_hgpr),
          low_price: num(output.stck_lwpr),
          vwap: num(output.wghn_avrg_stck_prc),
          bid1: num(output.bidp1),
          ask1: num(output.askp1),
          revision_status: "initial",
          rule_version: RULE_VERSION,
          raw_payload: output,
        });
      } catch (error) {
        failures[symbol] = error instanceof Error ? error.message : String(error);
      }
      await new Promise((resolve) => setTimeout(resolve, 120));
    }

    if (rows.length) await insertRows(rows);

    const success = Object.keys(failures).length === 0;
    return new Response(JSON.stringify({ ok: success, run_id: runId, rule_version: RULE_VERSION, requested: symbols.length, inserted: rows.length, failures, available_at: availableAt.toISOString() }), {
      status: success ? 200 : 207,
      headers: { "content-type": "application/json" },
    });
  } catch (error) {
    return new Response(JSON.stringify({ ok: false, error: error instanceof Error ? error.message : String(error) }), { status: 500, headers: { "content-type": "application/json" } });
  }
});
