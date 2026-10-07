#!/usr/bin/env node
// Sends a Web Push to the mobile PWA for each asset snapshot whose daily state is B3+.
// Never fails the monitor: missing secrets or dead subscriptions are logged and skipped.
//
// env: WEBPUSH_SUBSCRIPTIONS — JSON object or array copied from the app; each entry is a
//      PushSubscription plus the `vapid_private_key` it was created with.
//      VAPID_SUBJECT, PAGE_URL (optional)
// args: --snapshot <path> [--snapshot <path> ...] --state <path> [--test]

import { createECDH } from "node:crypto";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";
import webpush from "web-push";
import { decideAlert, buildMessage, parseSubscriptions, stateFor, symbolOf } from "./decide.mjs";

const arg = (name, dflt) => {
  const i = process.argv.indexOf(name);
  return i > -1 ? process.argv[i + 1] : dflt;
};
const test = process.argv.includes("--test");
const snapshotPaths = process.argv.flatMap((a, i) => (a === "--snapshot" ? [process.argv[i + 1]] : []));
if (!snapshotPaths.length) snapshotPaths.push("artifacts/crypto/live_entry.json");
const statePath = arg("--state", ".state/push_state.json");
const pageUrl = process.env.PAGE_URL || "https://chayobi03-cyber.github.io/investment/";

const subs = parseSubscriptions(process.env.WEBPUSH_SUBSCRIPTIONS);
if (!subs.length) {
  console.log("PUSH_SKIPPED=missing WEBPUSH_SUBSCRIPTIONS secret");
  process.exit(0);
}

function vapidFor(sub) {
  const ecdh = createECDH("prime256v1");
  ecdh.setPrivateKey(Buffer.from(sub.vapid_private_key, "base64url"));
  return {
    subject: process.env.VAPID_SUBJECT || pageUrl,
    publicKey: ecdh.getPublicKey().toString("base64url"),
    privateKey: sub.vapid_private_key,
  };
}

const state = existsSync(statePath) ? JSON.parse(readFileSync(statePath, "utf8")) : {};
const nextState = typeof state.decision_bar === "string" ? { BTC: state } : { ...state };
let stateChanged = false;

async function deliver(message) {
  let delivered = 0;
  for (const sub of subs) {
    try {
      const { endpoint, keys } = sub;
      await webpush.sendNotification({ endpoint, keys }, JSON.stringify(message), {
        TTL: 6 * 3600,
        vapidDetails: vapidFor(sub),
      });
      delivered++;
    } catch (e) {
      const host = (() => { try { return new URL(sub.endpoint).host; } catch { return "?"; } })();
      console.log(`PUSH_FAILED host=${host} status=${e.statusCode ?? "?"}` +
        (e.statusCode === 404 || e.statusCode === 410 ? " (subscription expired: re-subscribe in the app)" : ""));
    }
  }
  return delivered;
}

for (const [i, path] of snapshotPaths.entries()) {
  if (!existsSync(path)) {
    console.log(`PUSH_SKIPPED=${path} missing`);
    continue;
  }
  const snapshot = JSON.parse(readFileSync(path, "utf8"));
  const sym = symbolOf(snapshot);
  // --test sends one notification (first snapshot) regardless of state.
  if (test && i > 0) continue;
  const decision = test ? { send: true, reason: "manual test" } : decideAlert(snapshot, stateFor(state, sym));
  console.log(`PUSH_DECISION_${sym}=${decision.send ? "SEND" : "SKIP"} (${decision.reason})`);
  if (!decision.send) continue;

  const message = buildMessage(snapshot, pageUrl);
  if (test) message.title = `[테스트] ${message.title}`;
  const delivered = await deliver(message);
  console.log(`PUSH_DELIVERED_${sym}=${delivered}/${subs.length}`);
  if (delivered && !test) {
    nextState[sym] = {
      decision_bar: snapshot.decision_bar,
      state: snapshot.daily_core_state,
      sent_at: new Date().toISOString(),
    };
    stateChanged = true;
  }
}

if (stateChanged) {
  mkdirSync(dirname(statePath), { recursive: true });
  writeFileSync(statePath, JSON.stringify(nextState));
}
