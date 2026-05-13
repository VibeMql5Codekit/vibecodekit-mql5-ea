# VISION — vibecodekit-mql5-ea v5

**Date:** 2026-05-13
**Pipeline step:** 3/8
**Status:** PROPOSED → awaiting APPROVED / ADJUST / REJECT

---

## 1-line Goal

> **Bộ công cụ methodology-driven cho MQL5 EA development trên MetaTrader 5 — từ scaffold → lint → compile → backtest → walk-forward → multi-broker → ship — broker-agnostic by construction, mỗi command gọi trực tiếp, không qua router.**

---

## 3 KPIs

| # | KPI | Target | Measure |
|---|-----|--------|---------|
| 1 | **Broker-agnostic reliability** | CPipNormalizer xử lý đúng 100% trên 5d/4d/3d/2d brokers | Multi-broker stability gate: PF stdev/mean ≤ 0.30, DD diff ≤ 5% across FxPro + Exness + ICMarkets |
| 2 | **Code quality enforcement** | 0 critical AP lọt qua merge | 8 critical anti-patterns (AP-1,3,5,15,17,18,20,21) block PR merge via lint.py + CI gate |
| 3 | **Conformance coverage** | 70/70 tests pass at v1.0.0 | 10 e2e external (real MetaEditor compile + tester) + 60 internal probes. All 70 PASS required for release |

---

## Non-goals (explicitly OUT of scope)

| # | Non-goal | Reason |
|---|----------|--------|
| 1 | Master `/mql5` router command | Anti-pattern #5 — user gọi individual commands trực tiếp |
| 2 | Port `query_loop.py` / `tool_executor.py` | Dead code per user audit — Devin executes plans natively |
| 3 | Port `intent_router.py` / `pipeline_router.py` | Router pattern user rejected — discoverability via `/mql5-doctor` |
| 4 | 33 hook events / approval contract / 3-tier memory | VCK-HU over-engineering — EA domain không cần |
| 5 | Real-money trading automation | Kit = development tool. Trading execution là user responsibility |
| 6 | Self-referential 97-probe audit | Replace with 10 real e2e + 60 functional internal probes |

---

## Project type

**Developer toolkit / CLI tool suite** (not SaaS, not web app)

- Domain: Algorithmic trading (MQL5 Expert Advisors on MetaTrader 5)
- Platform: Linux (Wine + MetaEditor) + Windows (native MetaEditor)
- Language: Python (CLI tools, < 200 LOC each) + MQL5 (Include libraries)
- Users: EA developers (personal → team → enterprise)

---

## Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| CLI tools | Python 3.10+ | Each script < 200 LOC, 1 responsibility |
| MQL5 libraries | MQL5 (.mqh) | CPipNormalizer, CRiskGuard, CMagicRegistry, COnnxLoader, CAsyncTradeManager, CMfeMaeLogger, CSpreadGuard |
| Compiler | MetaEditor 64-bit | Via Wine on Linux, native on Windows |
| Testing | pytest 7.4+ | Per-phase gate tests |
| CI/CD | GitHub Actions | Linux (Wine) + Windows (native) runners |
| MCP servers | Python JSON-RPC 2.0 | 3 servers (Phase E): metaeditor-bridge, mt5-bridge (READ-ONLY), algo-forge-bridge |
| ML/AI (optional) | PyTorch + ONNX | Phase D, optional `[phase-d]` extras |

---

## Style direction

- **Functional, no-frills CLI** — mỗi command output `.md` report hoặc return code
- **Domain-first naming** — `/mql5-build`, `/mql5-lint`, `/mql5-compile` (not generic names)
- **Fail-fast, fail-loud** — critical AP violations = exit 1, not warnings
- **Report-driven** — every step produces readable markdown artifact in `runtime/`

---

## Delivery phases

| Phase | Tag | Key deliverables |
|-------|-----|-----------------|
| 0 — Bootstrap | v0.0.1 | Wine + MetaEditor + CI + 5 smoke tests |
| A — Core | v0.1.0 | CPipNormalizer + 4 commands + 4 scaffolds + 8 AP linter |
| B — Test | v0.2.0 | Backtest + walk-forward + monte-carlo + multi-broker + Trader-17 |
| C — Methodology | v0.3.0 | RRI 6 personas + 8×8 matrix + 7-layer permission + 13 BP AP |
| D — Tech 2024 | v0.5.0 | ONNX + HFT async + Algo Forge + LLM bridge + 13 strategy scaffolds |
| E — Polish | v1.0.0 | 26 references + 3 MCP + worked example + canary + 70 conformance |

---

## Risk summary (from RRI)

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Wine/MetaEditor CI fragile | HIGH | xvfb, retry, idempotent setup script |
| Broker demo creds expire | MEDIUM | User-provided, session-scoped secrets |
| Script size creep > 200 LOC | MEDIUM | audit-plan-v5.py post-phase check |
| mt5-bridge trade mutation | HIGH | READ-ONLY policy, grep-based test |
| ONNX/PyTorch heavy deps | LOW | Optional `[phase-d]` extras |

---

**VISION PROPOSED.** Awaiting confirmation to proceed to Step 4 — BLUEPRINT.
