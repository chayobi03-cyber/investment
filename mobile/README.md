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

## Local test

```bash
python3 -m http.server 8765 -d mobile   # then open http://<pc-ip>:8765 on the phone (same Wi-Fi)
PYTHONPATH=. python -m pytest tests/test_mobile_entry_parity.py -q
```

Note: the service worker (offline shell / install prompt) only activates over HTTPS
or on `localhost`; plain LAN HTTP still works as a normal web page.
