# Multi-Asset Research Sub-Agent Architecture V0.1

Date: 2026-09-26
Status: RESEARCH-ONLY CONTROL PLANE

## Scope

The investment system uses deterministic sub-agents for control, evidence and decomposition.

Supported asset classes:
- EQUITY
- GOLD
- CRYPTO

No sub-agent may create an executable order. `BUY_ALLOWED=false` and `EXECUTION_ALLOWED=false` remain global hard locks.

## Agent boundaries

### Data PIT Agent
Validates required PIT observations, availability, provenance and look-ahead.

### Regime Agent
Computes the common 0-100 Market Score and R1-R6 regime from already validated PIT axis scores.

### Permission Agent
Adds macro, liquidity, derivatives, regulation/market-structure and geopolitical blockers as an overlay. It does not rewrite the asset signal.

### Signal Decomposition Agent
Separates the existing signal into:
- regime R1-R6;
- B2/B3/B4;
- breakout vs pullback;
- zone.

It is a research-labeling agent only. It must not tune thresholds or alter signal states.

### Risk Agent
Evaluates supplied MDD, MAE, stress-loss and concentration inputs. Missing risk inputs are DATA_NOT_READY.

### Evidence / Source Agents
Trace claims to source records, classify source quality, and keep conflicting evidence visible.

### Hallucination Guard
Verifies claim type, PIT eligibility, calculation consistency, inference support, and conflict state. It is a hard gate for promotion.

### Decision Agent
Combines the agent results into a decision contract. It is a gate, not an optimizer or forecaster.

## Equity / Gold / Crypto

The common control plane is asset-agnostic. Asset-specific signal engines remain the source of truth:

- Equity: existing Stock Score / BuyStrength contract.
- Gold: separate gold entry rule must be preregistered before any threshold or live signal is introduced.
- Crypto: `crypto-market-regime-entry-v0.2` is frozen for research, with PIT permission overlay.

This prevents one asset class from silently inheriting another asset's thresholds.

## Why there is no development agent

A code-writing/development agent is not part of the production decision plane.

Development work can be performed by the engineering workflow outside the decision path, while the repository retains deterministic control/evidence agents. This removes a failure mode in which a code-generation component could modify thresholds or bypass a gate during an investment decision.

## Frozen-rule discipline

1. Thresholds are read-only during decomposition.
2. Permission is an overlay.
3. Regime is sourced from the permission layer; missing history stays DATA_NOT_READY.
4. OOS and walk-forward use chronological splits.
5. A PASS from one sub-agent cannot override a hard blocker from another.
6. Promotion remains blocked until full PIT evidence and stress/risk review pass.

## Current implementation

The current repository contains:
- common multi-asset orchestration;
- dedicated hallucination guard;
- dedicated signal decomposition agent;
- crypto PIT permission overlay;
- frozen crypto threshold contract.

The next data work is historical permission evidence, not threshold optimization.
