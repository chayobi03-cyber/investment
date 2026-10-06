#!/usr/bin/env node
// Sends a Web Push to the mobile PWA when the live snapshot's daily state is B3+.
// Never fails the monitor: missing secrets or dead subscriptions are logged and skipped.
//
// env: WEBPUSH_SUBSCRIPTIONS — JSON object or array copied from the app; each entry is a
//      PushSubscription plus the `vapid_private_key` it was created with.
//      VAPID_SUBJECT, PAGE_URL (optional)
// args: --snapshot <path> --state <path> [--test]

import { createECDH } from "node:crypto";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";
import webpush from "web-push";
import { decideAlert, buildMessage, parseSubscriptions } from "./decide.mjs";

const arg = (name, dflt) => {
  const i = process.argv.indexOf(name);
  return i > -1 ? process.argv[i + 1] : dflt;
};
const test = process.argv.includes("--test");
const snapshotPath = arg("--snapshot", "artifacts/crypto/live_entry.json");
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

const snapshot = JSON.parse(readFileSync(snapshotPath, "utf8"));
const lastState = existsSync(statePath) ? JSON.parse(readFileSync(statePath, "utf8")) : {};
const decision = test ? { send: true, reason: "manual test" } : decideAlert(snapshot, lastState);
console.log(`PUSH_DECISION=${decision.send ? "SEND" : "SKIP"} (${decision.reason})`);
if (!decision.send) process.exit(0);

const message = buildMessage(snapshot, pageUrl);
if (test) message.title = `[테스트] ${message.title}`;

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
console.log(`PUSH_DELIVERED=${delivered}/${subs.length}`);

if (delivered && !test) {
  mkdirSync(dirname(statePath), { recursive: true });
  writeFileSync(statePath, JSON.stringify({
    decision_bar: snapshot.decision_bar,
    state: snapshot.daily_core_state,
    sent_at: new Date().toISOString(),
  }));
}
