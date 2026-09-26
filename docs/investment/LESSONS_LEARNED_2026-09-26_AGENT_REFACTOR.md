# Lesson Learned — 2026-09-26 Agent Refactor

## Findings

1. The crypto threshold contract was already frozen correctly. The main risk was not the threshold values but accidental mutation or indirect redefinition during decomposition.
2. Regime decomposition belongs in a dedicated deterministic sub-agent. The price signal must remain unchanged; permission-derived regime is attached only after the PIT join.
3. PIT validation must be deterministic. A validator that compares `available_at` with the machine's current wall clock makes historical datasets time-dependent. Historical validation now accepts an explicit `as_of` cutoff instead.
4. Equity, Gold and Crypto can share one control plane, but their asset-specific signal engines must remain separate. In particular, Gold must not inherit crypto thresholds.
5. A development/code-generation agent should stay outside the investment decision plane. Control-plane agents should be deterministic and incapable of changing thresholds or issuing orders.
6. Hallucination prevention is a control gate, not an analysis engine. Unsupported facts, look-ahead claims, unverified calculations and unsupported inference chains remain blocking states.

## Rule revisions

- Keep `BUY_ALLOWED=false` and `EXECUTION_ALLOWED=false` as immutable global controls until promotion gates are satisfied.
- Permission is an overlay; never recompute or rewrite the frozen signal from permission data.
- Regime labels used for historical decomposition must originate from PIT permission evidence. Missing evidence remains `DATA_NOT_READY`.
- Every threshold experiment must run behind an explicit freeze test.
- Historical PIT validators must use explicit decision/as-of clocks rather than the current machine time.
- Development automation is not a decision-plane sub-agent.

## Next engineering boundary

The next work item is historical permission evidence acquisition and validation for:
macro/liquidity, derivatives, cross-asset spot, regulation/market structure, geopolitical transmission, and provenance/availability metadata.

Threshold tuning remains out of scope until that evidence is available and the frozen OOS/walk-forward evaluation is complete.
