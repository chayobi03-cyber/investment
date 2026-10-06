# BTC Entry Monitor — mobile PWA

Runs `crypto-market-regime-entry-v0.2` (the same logic as
`scripts/crypto/live_entry_snapshot.py`) entirely in the phone's browser.
No server, no API key, no GitHub Actions run needed.

- `entry.js` — pure JS port of `src/investment_pipeline/crypto_entry.py`.
  `tests/test_mobile_entry_parity.py` asserts row-by-row equality with Python.
- `data.js` — fetches 365 completed daily candles + live ticker straight from
  Coinbase's public API (CORS-enabled). Only bars whose `available_at` has passed are used.
- `app.js` — renders the snapshot, refreshes every 15 min while open and on return
  to the app, and keeps the last snapshot in `localStorage` for offline viewing.
- `sw.js` — caches the app shell so the installed app opens without network.

Fail-closed contract is unchanged: `buy_allowed=false`, `action=BLOCKED_UNVALIDATED`,
no orders are ever placed.

## Install on a phone

1. Deployed by `.github/workflows/mobile-pwa.yml` to GitHub Pages on every push to `main`
   (one-time: repo Settings → Pages → Source: **GitHub Actions**).
   URL: `https://chayobi03-cyber.github.io/investment/`
2. Open the URL on the phone.
   - iPhone (Safari): Share → **Add to Home Screen**
   - Android (Chrome): ⋮ → **Install app** / Add to Home screen
3. Launch from the home-screen icon; it runs full-screen as a standalone app.

## B3+ push alerts

The phone app can't run while closed, so the alert is sent by the existing
`crypto-entry-live-monitor` workflow (`scripts/crypto/push/send_entry_push.mjs`):
when the daily state is B3 or B4 it sends one Web Push per completed daily bar.
The message is research-only: `buy_allowed` stays false.

Setup (once per phone):

1. Open the installed app (iPhone: must be launched from the home-screen icon, iOS 16.4+)
   → **알림 켜기** → allow → **구독 정보 복사**.
2. Repo Settings → Secrets and variables → Actions → add:
   - `VAPID_PRIVATE_KEY` — private half of the key in `mobile/push-config.js`
   - `WEBPUSH_SUBSCRIPTIONS` — the copied JSON (for several phones: a JSON array of them)
3. Actions → crypto-entry-live-monitor → Run workflow with **test_push** checked
   to receive a test notification.

Missing secrets or expired subscriptions are logged and skipped; they never fail the monitor.
GitHub runs the `*/15` schedule only a few times a day, so an alert can arrive hours
after the daily close.

## Local test

```bash
python3 -m http.server 8765 -d mobile   # then open http://<pc-ip>:8765 on the phone (same Wi-Fi)
PYTHONPATH=. python -m pytest tests/test_mobile_entry_parity.py -q
```

Note: the service worker (offline shell / install prompt) only activates over HTTPS
or on `localhost`; plain LAN HTTP still works as a normal web page.
