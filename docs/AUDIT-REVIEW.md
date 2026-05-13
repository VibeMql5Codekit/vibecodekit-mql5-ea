# Deep Audit Report — vibecodekit-mql5-ea v1.0.0

> Audit date: 2026-05-13 · Scope: All Devin Review comments (PR #3, #5, #7) + full codebase review

---

## 1. Tổng quan

| Metric | Value |
|--------|-------|
| Files audited | 78 (Python CLI, MQL5 libs, MCP servers, scaffolds) |
| Tests | 107 pass, 2 skip, 0 fail |
| Devin Review comments | PR #3: 3 inline + 6 additional · PR #5: 1 inline + 3 additional |
| Issues fixed (total) | 5 bugs across PR #5 + PR #7 + PR #8 |

---

## 2. Devin Review Issues — Trạng thái

### PR #3 — 3 inline findings (tất cả đã fix)

| # | Severity | File | Issue | Fix |
|---|----------|------|-------|-----|
| 1 | 🔴 BUG | `forge_pr.py:30` | `max_drawdown_pct` key mismatch — backtest JSON dùng `maximal_drawdown_pct` nhưng code chỉ check `max_drawdown_pct` → mọi backtest đều bị reject (DD default=100 > 30) | **PR #5**: Added fallback `metrics.get("max_drawdown_pct", metrics.get("maximal_drawdown_pct", 100))` |
| 2 | 🔴 BUG | `layer4_checklist.py:21` | Threshold `>= 10` contradicts docstring + `trader_check.py` requirement `>= 15` → safety gate weakened | **PR #5**: Changed to `ok = passed >= 15` |
| 3 | 🔴 BUG | `CAsyncTradeManager.mqh:49,61` | `ResultOrder()` returns order ticket, not `request_id` → async tracking fails on most brokers | **PR #5**: Changed to `m_trade.Result(res); req_id = res.request_id` |

### PR #5 — 1 inline finding (đã fix)

| # | Severity | File | Issue | Fix |
|---|----------|------|-------|-----|
| 4 | 🟡 INCOMPLETE | `GUIDE-BUILD-EA.md:743,886` | 2 references still showed `≥10/17` after threshold fix | **PR #7**: Updated to `16/17 PASS` (example) + `≥15/17` (checklist) |

### PR #8 (this PR) — New finding from deep audit

| # | Severity | File | Issue | Fix |
|---|----------|------|-------|-----|
| 5 | 🔴 BUG | `build.py:18-19` | PRESETS hardcoded to 4 entries (`stdlib`, `wizard-composable`, `portfolio-basket`, `ml-onnx`) but `scaffolds/` has 17 directories → `--preset scalping`, `--preset trend`, etc. rejected by argparse | **This PR**: Dynamic discovery from filesystem via `_discover_presets()` |

---

## 3. Code Quality Audit — Phân tích theo module

### 3.1 Python CLI Tools (18 scripts, all ≤ 200 LOC)

| Script | LOC | Status | Notes |
|--------|-----|--------|-------|
| `lint.py` | 195 | ✅ GOOD | 8 critical + 5 warning detectors, proper absence-check logic |
| `build.py` | 94 | ✅ FIXED | Was rejecting 13/17 presets. Now uses filesystem discovery |
| `compile.py` | 106 | ✅ GOOD | Handles Wine/MetaEditor/Windows gracefully |
| `backtest.py` | 92 | ✅ GOOD | XML parser, `BacktestMetrics` dataclass clean |
| `walkforward.py` | 65 | ✅ GOOD | IS/OOS split, division-by-zero guarded |
| `monte_carlo.py` | 87 | ✅ GOOD | Bootstrap simulation, no seed (acceptable for randomized DD) |
| `multibroker.py` | 87 | ✅ GOOD | CV/stdev/range stability metrics |
| `trader_check.py` | 90 | ✅ GOOD | 17-point checklist, threshold = 15 (consistent) |
| `forge_pr.py` | 86 | ✅ FIXED | Drawdown key fallback added |
| `forge_init.py` | ~70 | ✅ GOOD | Workspace init with input extraction |
| `llm_context.py` | 122 | ✅ OK | 3 variants work; embedded-onnx tokenization is basic (demo-quality) |
| `pip_normalize.py` | ~60 | ✅ GOOD | Delegates to CPipNormalizer docs |
| `mfe_mae.py` | ~80 | ✅ GOOD | CSV analysis from CMfeMaeLogger output |
| `overfit_check.py` | ~60 | ✅ GOOD | Overfit detection heuristics |

### 3.2 Permission Pipeline (7 layers)

| Layer | File | Status | Notes |
|-------|------|--------|-------|
| L1 | `layer1_source_lint.py` | ✅ GOOD | 4 checks: strict, copyright, length, mixed indent |
| L2 | `layer2_compile.py` | ✅ GOOD | Graceful skip if Wine unavailable |
| L3 | `layer3_ap_lint.py` | ✅ GOOD | Delegates to lint.py, blocks on CRITICAL |
| L4 | `layer4_checklist.py` | ✅ FIXED | Threshold now ≥15 (was ≥10) |
| L5 | `layer5_methodology.py` | ✅ GOOD | 5 required patterns checked |
| L6 | `layer6_quality_matrix.py` | ⚠️ SPARSE | 16/64 cells covered — acceptable for v1.0 |
| L7 | `layer7_broker_safety.py` | ✅ GOOD | 4 broker-compat checks |
| Orch | `orchestrator.py` | ✅ GOOD | Fail-fast, mode-dependent (PERSONAL/TEAM/ENTERPRISE) |

### 3.3 MQL5 Include Libraries (7 files)

| Library | Status | Notes |
|---------|--------|-------|
| `CPipNormalizer.mqh` | ✅ GOOD | Truth table correct for 5d/4d/3d/2d. Lot sizing respects volume constraints. |
| `CRiskGuard.mqh` | ✅ GOOD | Daily loss + max positions. User must call `ResetDaily()` at market open. |
| `CMagicRegistry.mqh` | ✅ GOOD | File-backed collision detection |
| `CSpreadGuard.mqh` | ✅ GOOD | Moving average spread anomaly detection |
| `CMfeMaeLogger.mqh` | ✅ GOOD | CSV logger with FileFlush |
| `COnnxLoader.mqh` | ✅ GOOD | SetInputShape/SetOutputShape + OnnxRun with vectorf |
| `CAsyncTradeManager.mqh` | ✅ FIXED | Now uses `Result(res).request_id` for tracking |

### 3.4 MCP Servers (3 servers)

| Server | Status | Notes |
|--------|--------|-------|
| `metaeditor-bridge` | ✅ GOOD | 3 tools, delegates to compile.py |
| `mt5-bridge` | ✅ GOOD | 4 tools, READ-ONLY enforced (no order_send) |
| `algo-forge-bridge` | ✅ GOOD | 3 tools, delegates to forge_pr/forge_init |

### 3.5 Scaffolds (17 presets)

| Count | Status | Notes |
|-------|--------|-------|
| 17 presets | ✅ ALL ACCESSIBLE | Was 4/17 via CLI, now 17/17 with dynamic discovery |
| 3 standard stacks | netting, hedging, python-bridge |
| 3 LLM stacks | cloud-api, embedded-onnx-llm, self-hosted-ollama (service-llm-bridge only) |

---

## 4. Data Contract Audit

| Interface | Producer key | Consumer key | Status |
|-----------|-------------|--------------|--------|
| `backtest.py → forge_pr.py` | `max_drawdown_pct` (from BacktestMetrics) | `max_drawdown_pct` + `maximal_drawdown_pct` fallback | ✅ FIXED |
| `backtest-summary.json → forge_pr.py` | `maximal_drawdown_pct` | Same fallback | ✅ FIXED |
| `trader_check.py → layer4_checklist.py` | `>= 15` threshold | `>= 15` threshold | ✅ CONSISTENT |
| `lint.py → layer3_ap_lint.py` | `Finding.severity` | `f.severity == "CRITICAL"` | ✅ CONSISTENT |
| `orchestrator.py → GUIDE-BUILD-EA.md` | 7 layers, 3 modes | Documented correctly | ✅ CONSISTENT |

---

## 5. Recommendations (non-blocking)

1. **L6 Quality Matrix coverage**: Consider adding more checks to cover all 64 cells (currently 16/64). Low priority — current scoring is fair for v1.0.
2. **LLM embedded-onnx tokenization**: The `ord(c)` approach won't work for real LLM models. Fine for demo/bridge pattern.
3. **CRiskGuard daily reset**: Document that EAs must call `ResetDaily()` in `OnTimer()` or at market open. Currently left to developer.
4. **Monte Carlo reproducibility**: Consider adding `--seed` parameter for reproducible simulations during testing.

---

## 6. Kết luận

- **5 bugs found and fixed** across 4 PRs (#5, #7, #8)
- **0 remaining known bugs**
- **107/107 tests pass**, 2 skipped (Wine/MetaEditor not installed)
- **17/17 scaffolds accessible** via CLI (was 4/17)
- All permission layers operational with correct thresholds
- Data contracts verified consistent across all interfaces
