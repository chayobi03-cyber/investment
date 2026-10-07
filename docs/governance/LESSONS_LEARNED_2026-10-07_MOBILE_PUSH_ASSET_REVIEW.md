# Lessons Learned — 2026-10-07 Mobile PWA, Push Alerts, Asset Review, CI Repair

Date: 2026-10-06 → 2026-10-07
Merged: #16, #17, #18, #19, #20, #21. The live rule, thresholds and fail-closed state did not change: `BUY_ALLOWED=false`, `BLOCKED_UNVALIDATED`, no orders.

## What was delivered

| PR | Change |
|---|---|
| #16 | Standalone phone PWA (`mobile/`, GitHub Pages): JS port of `crypto_entry.py` v0.2, Coinbase direct fetch, offline cache. Also fixed the stale `test_live_market_review_adapter` assertion. |
| #17 | B3+ Web Push from `crypto-entry-live-monitor`; VAPID key generated on the phone; one `WEBPUSH_SUBSCRIPTIONS` secret; per-bar dedupe in Actions cache. |
| #18 | ETH/SOL added (app tabs, `--product` snapshot, per-asset push dedupe, `?asset=` deep links). |
| #19 | `pd.Timedelta(days=…)` → `datetime.timedelta` (numpy 2.5 deprecation); preregistered per-asset review + coin screen (`config/crypto_asset_review_v0.1.json`, weekly workflow). |
| #20 | Four stale tests updated to current contracts; decomposition `KeyError: 'year'` fixed. |
| #21 | Binance Vision rows tagged with the registered source id. |

## Findings

1. **A port must be proven against its source, row by row.** The JS entry logic is only trusted because `test_mobile_entry_parity.py` compares it with `generate_signals` on several regime-switching series. Change either side and that test must keep passing.
2. **GitHub cron is not a schedule.** `*/15 * * * *` ran about 3 times a day. That is acceptable for a daily-bar signal, but any alert's latency must be stated from observed runs, not from the cron string.
3. **Secrets don't belong in a public repo or in chat.** VAPID keys are now generated on the device, and the copied secret carries the subscription plus its private key. Nothing secret is committed, and several devices work without sharing a key.
4. **A red step can hide a later red step.** The p0–p6 job failed at the stale decomposition test, which masked a real `KeyError: 'year'` in the next step. Fixing a test isn't done until the full job is green.
5. **Push-only workflows don't validate PRs.** `multi-asset-subagents-ci`, `crypto-permission-layer-ci` and `crypto-market-regime-p0-p6-v0-2` only run on `main`, so all three had been red since 2026-09-26 unnoticed. Dispatch them on the branch before merging changes they cover.
6. **When a test and the code disagree, decide from history which one is stale.** In #20 the code had changed deliberately each time (refactor `11b0b25`, #13, #15), so the tests moved. The one exception was the PIT test, which expected a lookahead to PASS. There the code was right and the test was wrong; the PIT rule was never relaxed.
7. **Dependency deprecations must be reproduced at CI's exact versions.** With pandas 3 locally there was no warning; pandas 2.3.3 + numpy 2.5 (CI) showed it. A venv pinned to CI versions plus `-W error::DeprecationWarning` reproduced and verified the fix.
8. **BTC thresholds don't transfer by assumption.** On real data (first `crypto-asset-review` run): ETH passed 6/7 gate checks, better than BTC's 4/7. SOL passed 4/7, and volatility-scaled zones made it worse (1/7). No asset passed, because every per-asset OOS window holds fewer than 20 primary events.
9. **Self-calibration was tested, not assumed.** Scaling zone depths by σ(asset)/σ(BTC), measured on development data only, never beat the frozen rule. The frozen rule stays for all three assets.
10. **Venue liquidity matters for a Coinbase-only monitor.** LINK and BCH had the best candidate rule fit but only $12M / $2M of Coinbase volume. XRP's relisting cut its history to 1,182 days. No candidate was added.
11. **Provenance ids must match the registry.** The collector tagged `BINANCE_VISION_METRICS` while every registry said `BINANCE_VISION_DERIVATIVES_ARCHIVE`. A test now ties collected rows to the registry's PRIMARY id.

## Rule revisions

- Any duplicated logic (Python ↔ JS) ships with a parity test in CI.
- Before merging, dispatch every push-only workflow that covers the changed files on the PR branch.
- A CI fix is verified on the full job (all later steps and artifact assertions), not just the failing step.
- Reproduce dependency warnings and errors with CI's pinned versions; keep the suite clean under `-W error::DeprecationWarning`.
- Use `datetime.timedelta` (or `pd.to_timedelta(n, unit=…)`) for date arithmetic, never `pd.Timedelta(days=…)`.
- Stale tests are updated only when history shows the code change was intentional. A PIT/lookahead expectation is never relaxed to make a test pass.
- Per-asset decisions use the preregistered asset review. Thresholds are not changed per asset unless a variant passes the 7-condition gate, and adding a coin to the monitor is an explicit decision.
- Alert latency claims cite observed workflow runs.
- Secrets are generated where they are used (device or CI secret store), never in the repo, logs or chat.

## Open items / next boundary

- The per-asset gate is underpowered (OOS events < 20 for every asset). Options, each needing its own preregistration: a pooled cross-asset OOS gate, or waiting for more history. Do not lower the 20-event minimum after seeing results.
- `r01-provenance.yml` has failed on every `main` push since at least 2026-09-26 (fails instantly). Not investigated in this session.
- The weekly `crypto-asset-review` (Mon 02:17 UTC) is the trigger to revisit ETH promotion or a new coin.
- Coinbase volume is a venue proxy. If the monitor ever trades elsewhere, the liquidity screen must use that venue.

## Operating notes

- App: `https://chayobi03-cyber.github.io/investment/`. Push secret: `WEBPUSH_SUBSCRIPTIONS` (JSON object or array). Test with `crypto-entry-live-monitor` → Run workflow → `test_push`.
- A re-installed app or new phone invalidates its subscription (`PUSH_FAILED … expired`): re-subscribe in the app and replace the secret value.
