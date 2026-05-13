# Blueprint — vibecodekit-mql5-ea v5

> Pipeline step: 4/8 — Fill every section. Empty sections block release gate.

---

## 1. Problem statement (≤ 200 words)

EA developers trên MetaTrader 5 hiện tại phải:
- Tự xử lý 5-digit/3-digit/2-digit broker differences → bug pip calculation
- Không có lint tool → anti-patterns (no SL, hardcoded lot, raw OrderSend) lọt vào production
- Không có walk-forward/multi-broker validation → overfitted EA deploy live
- Không có scaffolding → mỗi EA viết từ scratch, lặp lại boilerplate

**vibecodekit-mql5-ea** giải quyết bằng bộ ~30 CLI commands: scaffold → lint → compile → backtest → walk-forward → multi-broker → ship. Broker-agnostic by construction via CPipNormalizer. Mỗi command gọi trực tiếp, không qua router. Plan v5 (1089 dòng) spec đầy đủ 6 phases.

---

## 2. Scope

**In scope:**
- Phase 0: Wine + MetaEditor + CI + audit script + 5 smoke tests
- Phase A: CPipNormalizer.mqh + CRiskGuard.mqh + CMagicRegistry.mqh + 4 commands (build, lint, compile, pip-normalize) + 4 scaffolds + 8 critical AP linter
- Phase B: Backtest + walk-forward + monte-carlo + multi-broker + Trader-17 + VPS deploy
- Phase C: RRI 6 personas + 8×8 matrix + 7-layer permission + 13 best-practice AP
- Phase D: ONNX + HFT async + Algo Forge + LLM bridge + 13 strategy scaffolds
- Phase E: 26 references + 3 MCP servers + worked example + canary + final commands

**Out of scope:**
- Master `/mql5` router command
- `query_loop.py`, `tool_executor.py`, `intent_router.py`, `pipeline_router.py`
- Real-money trading execution
- 33 hook events / approval contract / 3-tier memory hierarchy
- Self-referential conformance (replaced by 10 e2e + 60 internal)

---

## 3. Success metrics

| Metric | Current | Target | How measured |
|--------|---------|--------|--------------|
| Multi-broker PF stdev/mean | N/A | ≤ 0.30 | `/mql5-multibroker` across 3 brokers |
| Critical AP caught | N/A | 8/8 | `/mql5-lint` on fixture .mq5 files |
| Conformance tests | 0 | 70/70 | `/mql5-audit` (10 e2e + 60 internal) |
| Phase smoke tests | 0 | 5/5 | `pytest tests/gates/phase-0/` |
| Script LOC ceiling | N/A | < 200 each | `audit-plan-v5.py` post-phase |
| Walk-forward OOS PF | N/A | ≥ 1.5 | `/mql5-walkforward` output |
| Trader-17 checklist | N/A | ≥ 15/17 | `/mql5-trader-check` |

---

## 4. Entities & data flows

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER (EA Developer)                          │
│  Describes strategy → chooses scaffold → edits logic            │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────┐     ┌─────────────────────┐
│  /mql5-build       │────▶│  scaffolds/          │
│  (build.py)        │     │  16 × 3 templates    │
└────────┬───────────┘     └─────────────────────┘
         │ generates .mq5
         ▼
┌────────────────────┐     ┌─────────────────────┐
│  /mql5-lint        │────▶│  tests/fixtures/     │
│  (lint.py)         │     │  8 AP .mq5 samples   │
│  22 AP detectors   │     └─────────────────────┘
└────────┬───────────┘
         │ PASS (0 critical)
         ▼
┌────────────────────┐     ┌─────────────────────┐
│  /mql5-compile     │────▶│  MetaEditor64.exe    │
│  (compile.py)      │     │  (Wine / native)     │
└────────┬───────────┘     └─────────────────────┘
         │ 0 errors
         ▼
┌────────────────────┐     ┌─────────────────────────────────┐
│  /mql5-backtest    │────▶│  MT5 Strategy Tester             │
│  (backtest.py)     │     │  XML report → parse metrics      │
└────────┬───────────┘     └─────────────────────────────────┘
         │
    ┌────┴────┬─────────────┐
    ▼         ▼             ▼
┌──────┐  ┌──────────┐  ┌──────────┐
│ WF   │  │ MC       │  │ Overfit  │
│(walk │  │(monte    │  │(check)   │
│ fwd) │  │ carlo)   │  │          │
└──┬───┘  └────┬─────┘  └────┬─────┘
   │           │              │
   └─────┬─────┴──────────────┘
         ▼
┌────────────────────┐     ┌─────────────────────────────────┐
│  /mql5-multibroker │────▶│  3 brokers: FxPro, Exness,      │
│  (multibroker.py)  │     │  ICMarkets (demo accounts)      │
└────────┬───────────┘     └─────────────────────────────────┘
         │ stability gate PASS
         ▼
┌────────────────────┐     ┌─────────────────────────────────┐
│  7-layer permission│────▶│  L1-L7 sequential check         │
│  (orchestrator.py) │     │  All must PASS for mode          │
└────────┬───────────┘     └─────────────────────────────────┘
         │
         ▼
┌────────────────────┐     ┌─────────────────────────────────┐
│  /mql5-ship        │────▶│  VPS deploy + canary 30min       │
│  (ship.py)         │     │  → git tag + release             │
└────────────────────┘     └─────────────────────────────────┘
```

### MQL5 Include library dependency graph

```
CPipNormalizer.mqh ◀── (all EAs, all scaffolds)
       │
CRiskGuard.mqh ◀── (all EAs with risk management)
       │
CMagicRegistry.mqh ◀── (portfolio EAs)
       │
CMfeMaeLogger.mqh ◀── (Phase B, per-trade analysis)
       │
CSpreadGuard.mqh ◀── (Phase B, spread check)
       │
COnnxLoader.mqh ◀── (Phase D, ML EAs only)
       │
CAsyncTradeManager.mqh ◀── (Phase D, HFT EAs only)
```

---

## 4a. RRI Requirements matrix

| REQ-ID | Requirement | Blueprint section | Source (RRI) | Acceptance criteria |
|--------|-------------|-------------------|-------------|---------------------|
| REQ-PIP | CPipNormalizer handles 5d/4d/3d/2d | §4 Include libs | Trader-Q2, Broker-Q1 | Init() auto-detect, Pips() correct on EURUSD/XAUUSD/USDJPY |
| REQ-RISK | CRiskGuard daily-loss + max-positions | §4 Include libs | Trader-Q3,Q9, Risk-Q11 | Disable EA when daily loss > threshold |
| REQ-MAGIC | CMagicRegistry unique per EA×symbol | §4 Include libs | Trader-Q10, Broker-Q5 | File-backed, collision-free |
| REQ-AP8 | 8 critical AP block merge | §4 lint.py | Risk-Q2, Broker-Q3 | lint.py exit 1 on any critical AP |
| REQ-MULTI | Multi-broker stability gate | §4 multibroker.py | Trader-Q2, Risk-Q9, Perf-Q5 | PF stdev/mean ≤ 0.30, DD diff ≤ 5% |
| REQ-WF | Walk-forward OOS validation | §4 walkforward.py | Perf-Q2, Arch-Q5 | PF ≥ 1.5 on 30% OOS data |
| REQ-MC | Monte Carlo DD percentiles | §4 monte_carlo.py | Risk-Q10, Perf-Q4 | DD95 ≤ 1.5× actual DD |
| REQ-T17 | Trader-17 checklist ≥ 15/17 | §4 trader_check.py | Risk-Q3(L4), Perf-Q7 | Dict output PASS/WARN/N-A |
| REQ-PERM | 7-layer permission pipeline | §4 permission/ | Risk-Q3, DevOps-Q1 | Mode-dependent (PERSONAL: L1-4,7) |
| REQ-RRI | RRI 6 personas × 25 questions | §4 rri/ | Risk-Q12, Arch-Q12 | YAML files, mode-dependent count |
| REQ-MAT | 8×8 quality matrix | §4 matrix.py | Perf-Q6 | 64 cells, ≥ 56 PASS for Enterprise |
| REQ-ONNX | ONNX inference in EA | §4 COnnxLoader | Trader-Q11, Arch-Q4 | PyTorch → ONNX → .mqh, e2e < 10min |
| REQ-HFT | OrderSendAsync + handler | §4 CAsyncTradeManager | Broker-Q3, Arch-Q7 | AP-18 enforced |
| REQ-MCP | 3 MCP servers (E) | §4 mcp/ | DevOps-Q8 | mt5-bridge READ-ONLY |
| REQ-AUDIT | Anti-drift audit pre/post | §4 audit-plan-v5.py | Risk-Q4, DevOps-Q10 | FORBIDDEN files/patterns detected |
| REQ-SCAFFOLD | 16 scaffolds × 3 stacks | §4 scaffolds/ | Arch-Q1 | Render correct .mq5 + .set + README |
| REQ-REF | 26 reference docs | §4 docs/references/ | Risk-Q12, DevOps-Q12 | Frontmatter validated by test |
| REQ-CANARY | 30min post-deploy canary | §4 canary.py | DevOps-Q4, Perf-Q9 | Log trades, spread, connection |

---

## 4b. Task decomposition preview

```
Estimated tasks: 25 TIPs
Estimated effort: ~2400 min total (across 6 phases)

Phase 0 (Bootstrap) — 4 TIPs
├── TIP-001: Setup Wine + MetaEditor installer script        (~120 min)
├── TIP-002: Create CI workflow (Linux + Windows)            (~60 min)
├── TIP-003: Implement audit-plan-v5.py skeleton             (~90 min)
└── TIP-004: Write 5 smoke tests                             (~60 min)

Phase A (Core) — 6 TIPs
├── TIP-005: CPipNormalizer.mqh (≤ 250 LOC)                  (~180 min)
├── TIP-006: CRiskGuard.mqh + CMagicRegistry.mqh             (~120 min)
├── TIP-007: lint.py — 8 critical AP detectors               (~120 min)
├── TIP-008: build.py + compile.py + pip_normalize.py        (~120 min)
├── TIP-009: 4 scaffolds (stdlib, wizard, portfolio, ml-onnx)  (~120 min)
└── TIP-010: Phase A tests (3 e2e + 25 unit)                 (~90 min)

Phase B (Test) — 5 TIPs
├── TIP-011: backtest.py + walkforward.py                    (~120 min)
├── TIP-012: monte_carlo.py + overfit_check.py               (~90 min)
├── TIP-013: multibroker.py + broker_safety.py               (~120 min)
├── TIP-014: trader_check.py (17-point) + deploy_vps.py      (~90 min)
└── TIP-015: Phase B tests (6 e2e + 30 unit) + Include libs  (~120 min)

Phase C (Methodology) — 4 TIPs
├── TIP-016: RRI 6 personas YAML + step_workflow.py          (~120 min)
├── TIP-017: 8×8 matrix.py + HTML renderer                   (~90 min)
├── TIP-018: 7-layer permission (7 scripts + orchestrator)   (~180 min)
└── TIP-019: 13 best-practice AP + review commands           (~120 min)

Phase D (Tech 2024) — 3 TIPs
├── TIP-020: ONNX pipeline (export + embed + COnnxLoader)    (~180 min)
├── TIP-021: HFT async + Algo Forge + LLM bridge             (~180 min)
└── TIP-022: 13 strategy scaffolds + method-hiding linter    (~120 min)

Phase E (Polish) — 3 TIPs
├── TIP-023: 3 MCP servers + 26 reference docs               (~180 min)
├── TIP-024: Worked example + canary + final commands         (~180 min)
└── TIP-025: 70 conformance suite + COMMANDS.md + QUICKSTART  (~120 min)
```

| TIP-ID | Title | REQ covered | Effort | Phase |
|--------|-------|-------------|--------|-------|
| TIP-001 | Wine + MetaEditor setup | REQ-AUDIT | 120 min | 0 |
| TIP-002 | CI workflow | REQ-AUDIT | 60 min | 0 |
| TIP-003 | Audit script skeleton | REQ-AUDIT | 90 min | 0 |
| TIP-004 | 5 smoke tests | REQ-AUDIT | 60 min | 0 |
| TIP-005 | CPipNormalizer.mqh | REQ-PIP | 180 min | A |
| TIP-006 | CRiskGuard + CMagicRegistry | REQ-RISK, REQ-MAGIC | 120 min | A |
| TIP-007 | lint.py 8 critical AP | REQ-AP8 | 120 min | A |
| TIP-008 | build + compile + pip-normalize | REQ-PIP, REQ-SCAFFOLD | 120 min | A |
| TIP-009 | 4 scaffolds | REQ-SCAFFOLD | 120 min | A |
| TIP-010 | Phase A tests | REQ-AP8, REQ-PIP | 90 min | A |
| TIP-011 | backtest + walkforward | REQ-WF | 120 min | B |
| TIP-012 | monte-carlo + overfit | REQ-MC | 90 min | B |
| TIP-013 | multibroker + broker-safety | REQ-MULTI | 120 min | B |
| TIP-014 | trader-check + deploy-vps | REQ-T17 | 90 min | B |
| TIP-015 | Phase B tests + Include libs | REQ-MULTI, REQ-WF | 120 min | B |
| TIP-016 | RRI personas + workflow | REQ-RRI | 120 min | C |
| TIP-017 | 8×8 matrix | REQ-MAT | 90 min | C |
| TIP-018 | 7-layer permission | REQ-PERM | 180 min | C |
| TIP-019 | 13 best-practice AP + review | REQ-AP8 | 120 min | C |
| TIP-020 | ONNX pipeline | REQ-ONNX | 180 min | D |
| TIP-021 | HFT + Forge + LLM | REQ-HFT | 180 min | D |
| TIP-022 | 13 strategy scaffolds | REQ-SCAFFOLD | 120 min | D |
| TIP-023 | 3 MCP + 26 references | REQ-MCP, REQ-REF | 180 min | E |
| TIP-024 | Worked example + canary | REQ-CANARY | 180 min | E |
| TIP-025 | 70 conformance + docs | REQ-AUDIT | 120 min | E |

---

## 5. Invariants (must always hold)

1. **No forbidden files** — `query_loop.py`, `tool_executor.py`, `intent_router.py`, `pipeline_router.py`, `master_command.py` never exist
2. **No forbidden patterns** — `def run_plan(`, `class IntentRouter`, `class PipelineRouter`, `class ToolExecutor` never appear
3. **LOC ceiling** — every Python script < 200 LOC, CPipNormalizer.mqh < 250 LOC
4. **Single responsibility** — each module has exactly 1 purpose, no god modules
5. **No master router** — no `/mql5` master command, user invokes individual commands
6. **mt5-bridge READ-ONLY** — no `order_send`, `order_close`, `position_modify`, `position_close` in mt5-bridge
7. **Critical AP = gate** — AP-1,3,5,15,17,18,20,21 always block merge (exit 1)
8. **Pip truth table** — `pip = (digits ∈ {3,5}) ? 10*point : 1*point` — never hardcoded
9. **Audit pre/post** — `audit-plan-v5.py` runs before AND after each phase
10. **No secrets in code** — broker creds via secrets tool, `.gitignore` excludes sensitive files

---

## 6. Risks & mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|-----------|
| Wine/MetaEditor setup fails on CI | HIGH | HIGH | Idempotent script, xvfb, retry 3x, Windows runner fallback |
| Broker demo creds expire mid-test | MEDIUM | MEDIUM | User-provided, session-scoped, request fresh if needed |
| Script size creep > 200 LOC | MEDIUM | LOW | audit-plan-v5.py enforces, PR blocked |
| mt5-bridge accidental trade method | LOW | HIGH | grep-based test, explicit READ-ONLY policy, code review |
| CPipNormalizer edge case on exotic broker | MEDIUM | HIGH | Multi-broker gate with 3 different broker types |
| ONNX/PyTorch CI timeout | MEDIUM | LOW | 10min budget, optional `[phase-d]` extras |
| Method-hiding false positives > 30% | MEDIUM | LOW | `// vck-mql5: hiding-ok` opt-out comment |
| MQL5 compiler version breaking change | LOW | MEDIUM | Pin MetaEditor version, CI catch regression |

---

## 7. Decision log

| Date | Decision | Rationale | Alternatives rejected |
|------|----------|-----------|----------------------|
| 2026-05-13 | Drop query_loop + tool_executor | Dead code per user audit | Keep for backwards compat |
| 2026-05-13 | Drop intent_router + pipeline_router | Router pattern user rejected | Keep with simplified routing |
| 2026-05-13 | No master `/mql5` command | Anti-pattern; direct invocation clearer | Single entry point like VCK-HU `/vibe` |
| 2026-05-13 | 10 e2e + 60 internal (not 97 self-probes) | Avoid self-referential testing | Port VCK-HU 97-probe style |
| 2026-05-13 | 7-layer permission mode-dependent | PERSONAL doesn't need methodology gate | Same layers for all modes |
| 2026-05-13 | Each script < 200 LOC | Prevent god module anti-pattern | Allow up to 500 LOC |
| 2026-05-13 | TEAM mode for this RRI | Balanced depth for initial build | PERSONAL (too shallow) / ENTERPRISE (too heavy) |

---

## 8. Rollback plan

- **Per-phase rollback:** `git revert` the phase branch merge commit → audit-plan-v5.py verifies clean state
- **Per-feature rollback:** Each TIP is a separate commit → `git revert <commit>` for individual feature
- **Version tags:** v0.0.1 → v0.1.0 → ... → v1.0.0 — checkout any tag for known-good state
- **No database migrations** — pure filesystem project, no state to undo
- **Wine prefix isolation** — WINEPREFIX separate from system, can delete and re-setup

---

## 9. Sign-off

- Architect: Devin (VibecodeKit pipeline) — 2026-05-13
- Implementation Lead: Devin — 2026-05-13
- Security Auditor: Pending (Phase C: 7-layer permission)
- Compliance Steward: Pending (Phase E: 70 conformance)

---

**BLUEPRINT COMPLETE.** Ready for Step 5 — TASK GRAPH.
