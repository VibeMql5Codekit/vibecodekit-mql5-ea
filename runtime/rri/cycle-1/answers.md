# RRI Cycle 1 — vibecodekit-mql5-ea v5
## Reverse Requirements Interview

**Date:** 2026-05-13
**Mode:** TEAM (12 questions/persona × 6 personas = 72 questions synthesized)
**Pipeline step:** 2/8

---

## Persona 1: TRADER (End-user)

### Q1: Max acceptable drawdown? (critical)
**A:** Max DD ≤ 20% equity cho PERSONAL mode, ≤ 15% cho ENTERPRISE. CRiskGuard.mqh enforce daily-loss limit (configurable input). Walk-forward OOS verify.

### Q2: EA phải chạy trên bao nhiêu broker?
**A:** Minimum 3 brokers: FxPro (5d), Exness (3d XAUUSD), ICMarkets (2d). CPipNormalizer.mqh normalize tất cả sang pip-based math. Multi-broker stability gate: PF stdev/mean ≤ 0.30.

### Q3: Trader có cần can thiệp manual hay full auto?
**A:** Full auto với kill-switch. CRiskGuard.mqh auto-disable EA khi daily loss > threshold. Trader chỉ cần set inputs + monitor.

### Q4: Kỳ vọng profit factor bao nhiêu?
**A:** PF ≥ 1.5 trên walk-forward OOS (30% data). Monte Carlo DD95 ≤ 1.5× actual DD.

### Q5: Time frame nào hỗ trợ?
**A:** H1 primary (worked example), H4/D1 secondary. M1-M15 cho HFT async scaffold (Phase D). Set files per TF.

### Q6: Symbols nào mandatory?
**A:** EURUSD (baseline), XAUUSD (gold 3d/2d test), USDJPY (JPY pair test). All phải pass CPipNormalizer.

### Q7: Trader workflow từ A→Z?
**A:** `/mql5-build` scaffold → edit strategy → `/mql5-lint` → `/mql5-compile` → `/mql5-backtest` → `/mql5-walkforward` → `/mql5-multibroker` → `/mql5-ship`. Mỗi step output file `.md`.

### Q8: Có cần VPS deployment?
**A:** Yes, Phase B. `/mql5-deploy-vps` auto-deploy EA lên MetaTrader VPS. Canary monitoring 30min post-deploy.

### Q9: Risk per trade?
**A:** Configurable, default 1-2% equity. `LotForRisk()` trong CPipNormalizer compute lot size. RiskGuard cap max positions.

### Q10: Có cần multi-currency portfolio?
**A:** Yes, `portfolio-basket` scaffold hỗ trợ. CMagicRegistry.mqh manage magic number per EA/symbol pair.

### Q11: Muốn integrate AI/ML signals?
**A:** Phase D: ONNX inference (`COnnxLoader.mqh`), LLM bridge (WebRequest + fallback rule-based). Optional, not mandatory.

### Q12: Spread protection?
**A:** CSpreadGuard.mqh check spread < threshold trước khi OrderSend. AP-17 detect WebRequest trong OnTick (block).

---

## Persona 2: RISK AUDITOR

### Q1: Audit trail cho mọi trade?
**A:** CMfeMaeLogger.mqh log MFE/MAE CSV per-trade. Magic registry traceable. Backtest XML preserved.

### Q2: Forbidden patterns enforcement?
**A:** 8 critical AP + 13 best-practice AP = 21 anti-patterns. `lint.py` regex/AST detect. Gate blocks PR merge.

### Q3: Permission model?
**A:** 7-layer permission pipeline:
- L1: Source lint (format + syntax)
- L2: Compile (0 errors)
- L3: AP lint (8 critical)
- L4: Trader-17 checklist (≥15/17)
- L5: RRI methodology done (Team/Enterprise)
- L6: Quality matrix (≥56/64 cells, Enterprise)
- L7: Multi-broker safety + pip normalize

### Q4: Anti-drift mechanism?
**A:** `audit-plan-v5.py` runs PRE/POST each phase. FORBIDDEN_FILES list. FORBIDDEN_PATTERNS regex. Any violation = merge block.

### Q5: Code size governance?
**A:** Strict LOC ceiling: 250 (CPipNormalizer), 200 (scripts), 150 (layers). audit-plan-v5.py verify.

### Q6: Sensitive data protection?
**A:** No secrets in code. Broker credentials via Devin secrets tool. `.gitignore` excludes Wine prefix, `.env`, credentials.

### Q7: Compliance với MQL5 platform rules?
**A:** Method-hiding linter (build ≥ 5260). AP-15: no raw OrderSend (use CTrade). AP-18: async + OnTradeTransaction mandatory.

### Q8: Dead code policy?
**A:** Explicit FORBIDDEN: query_loop, tool_executor, intent_router, pipeline_router. audit-plan-v5.py auto-detect.

### Q9: Cross-broker risk parity?
**A:** Multi-broker stability tolerance: PF stdev/mean ≤ 0.30, Sharpe stdev ≤ 0.20, DD diff ≤ 5%. Mandatory gate.

### Q10: Overfit protection?
**A:** `/mql5-overfit-check`: OOS PF / IS PF ratio. `/mql5-monte-carlo`: bootstrap DD percentiles. AP-5: detect overfitted tester-set (> 6 inputs + > 100k passes).

### Q11: Disaster recovery?
**A:** CRiskGuard daily-loss kill switch. Canary 30min post-deploy monitoring. VPS auto-redeploy.

### Q12: Documentation completeness?
**A:** 26 reference docs covering all domain knowledge. Each with frontmatter validation. COMMANDS.md full catalog.

---

## Persona 3: BROKER ENGINEER

### Q1: 5-digit vs 3-digit vs 2-digit handling?
**A:** CPipNormalizer.mqh FLAGSHIP: `pip = (digits ∈ {3,5}) ? 10*point : 1*point`. Init() auto-detect. All math pip-based.

### Q2: MetaEditor compile compatibility?
**A:** compile.py wraps `wine metaeditor64.exe /compile:file.mq5`. Parse log for errors/warnings. CI runs both Linux (Wine) + Windows (native).

### Q3: OrderSend vs CTrade standardization?
**A:** AP-15 CRITICAL: no raw `OrderSend(`. Must use CTrade.Buy/Sell. AP-18: OrderSendAsync requires OnTradeTransaction handler.

### Q4: Spread anomaly protection?
**A:** CSpreadGuard.mqh: check current spread vs N-bar average. Block trade if spread > 2× average. Configurable threshold.

### Q5: Multi-symbol infrastructure?
**A:** CMagicRegistry.mqh: file-backed unique magic per EA×symbol. Prevents magic collision in portfolio mode.

### Q6: Strategy Tester integration?
**A:** backtest.py: parse XML, generate .ini for batch runs. walkforward.py: IS/OOS split, forward 1/4 mode. fitness.py: 5 fitness function templates.

### Q7: VPS compatibility?
**A:** deploy_vps.py: auto-deploy EA to MT5 VPS. Works with all MQL5 VPS providers.

### Q8: History data requirements?
**A:** Multi-broker test needs synchronized history across 3 brokers. Strategy Tester period must cover test range.

### Q9: Build system for MQL5?
**A:** build.py renders scaffold → compile.py wraps MetaEditor → lint.py checks AP. No separate build tool needed (MetaEditor IS the compiler).

### Q10: Cloud Network optimization?
**A:** cloud_optimize.py (Phase D): MQL5 Cloud Network for heavy optimization. Budget cap enforcement. Cost calculator.

### Q11: Symbol normalization edge cases?
**A:** XAUUSD 3-digit (Exness) vs 2-digit (ICMarkets). USDJPY 3-digit. CPipNormalizer handles all via Digits() + SymbolInfoDouble.

### Q12: Method hiding (build 5260+)?
**A:** method_hiding_check.py: detect derived class method shadowing without `using`. Warn < 5260, Error ≥ 5260. False positive ≤ 30%.

---

## Persona 4: STRATEGY ARCHITECT

### Q1: Strategy taxonomy coverage?
**A:** 16 scaffolds × 3 stack modes: stdlib, wizard-composable, portfolio-basket, ml-onnx (Phase A) + trend, mean-reversion, breakout, hedging-multi, news-trading, arbitrage-stat, scalping, library, indicator-only, grid, dca, hft-async, service-llm-bridge (Phase D).

### Q2: Wizard framework support?
**A:** wizard-composable scaffold: CExpert-based. Mashnin Advanced book approach. Signal + Money + Trailing composable modules.

### Q3: Portfolio/basket strategy?
**A:** portfolio-basket scaffold: multi-symbol, hedging/netting variants. CMagicRegistry per symbol. CRiskGuard portfolio-level daily loss.

### Q4: ONNX/ML integration?
**A:** ml-onnx scaffold + python-bridge: train.py (PyTorch LSTM) → export_onnx.py → COnnxLoader.mqh inference. E2e < 10min.

### Q5: Walk-forward methodology?
**A:** walkforward.py: Forward 1/4 (25% OOS). Extract IS/OOS from XML. Compare PF/Sharpe/DD metrics. Must pass multi-broker.

### Q6: Fitness function templates?
**A:** 5 templates: max_profit, min_dd, sharpe_ratio, profit_factor, custom_weighted. Each < 50 LOC.

### Q7: HFT async pattern?
**A:** hft-async scaffold: OrderSendAsync + CAsyncTradeManager.mqh + OnTradeTransaction handler. AP-18 enforced.

### Q8: LLM-assisted strategy?
**A:** service-llm-bridge scaffold: 3 variants (cloud-api, self-hosted-ollama, embedded-onnx-llm). Mandatory timeout + fallback to rule-based.

### Q9: Backtesting automation?
**A:** backtest.py: batch .ini generation, XML result parsing, metrics extraction (PF, Sharpe, DD, trades count).

### Q10: Signal composability?
**A:** Wizard framework CExpert allows composing signals (MACD+SAR+RSI etc.) + money management + trailing stop modules.

### Q11: Monte Carlo validation?
**A:** monte_carlo.py: bootstrap trade sequence N times. Report DD at 50/75/95 percentile. Mandatory for ENTERPRISE mode.

### Q12: Worked example available?
**A:** Phase E: EA Wizard MACD+SAR EURUSD H1 portfolio. Full 8-step walkthrough. Results: backtest.xml, multibroker.csv, canary.log, matrix-64-cell.html.

---

## Persona 5: DEVOPS

### Q1: CI/CD pipeline?
**A:** GitHub Actions: Linux runner (Wine + MetaEditor) + Windows runner (native). Per-phase test gates. audit-plan-v5.py pre/post.

### Q2: Deployment target?
**A:** VPS (MT5 VPS). Canary 30min post-deploy. Auto-rollback if DD > threshold.

### Q3: Dependency management?
**A:** pyproject.toml with optional extras: `[dev]` for testing, `[phase-d]` for ONNX/PyTorch. Minimal base deps.

### Q4: Monitoring?
**A:** canary.py: 30min observation window post-deploy. Log trades, spread, connection stability. Alert on anomaly.

### Q5: Environment reproducibility?
**A:** setup-wine-metaeditor.sh idempotent. Wine prefix isolated. Python venv. CI matrix covers Linux + Windows.

### Q6: Secret management?
**A:** Broker demo credentials via Devin secrets tool (session-scoped). No secrets in code. `.gitignore` patterns.

### Q7: Version strategy?
**A:** Semantic: v0.0.1 (Phase 0) → v0.1.0 (A) → v0.2.0 (B) → v0.3.0 (C) → v0.5.0 (D) → v1.0.0 (E).

### Q8: MCP server deployment?
**A:** 3 MCP servers (Phase E): metaeditor-bridge, mt5-bridge (READ-ONLY), algo-forge-bridge. JSON-RPC 2.0. Each < 200 LOC.

### Q9: Build artifact management?
**A:** Compiled .ex5 NOT committed. Wine prefix in .gitignore. Only source .mq5/.mqh committed.

### Q10: Rollback strategy?
**A:** Git tag per phase. Clean revert possible. audit-plan-v5.py verify state at any point.

### Q11: Performance requirements?
**A:** ONNX e2e < 10min. Compile < 30s. Backtest single pair < 5min. CI full suite < 15min.

### Q12: Documentation as code?
**A:** All specs in `docs/`. 26 references in `docs/references/`. Frontmatter validated by test. COMMANDS.md auto-generated.

---

## Persona 6: PERFORMANCE ANALYST

### Q1: Key performance metrics?
**A:** Profit Factor, Sharpe Ratio, Max Drawdown, Recovery Factor, Win Rate, Average Win/Loss ratio, Expected Payoff.

### Q2: Benchmark baselines?
**A:** Walk-forward OOS: PF ≥ 1.5, Sharpe ≥ 1.0, DD ≤ 20%. Monte Carlo DD95 ≤ 1.5× actual. Multi-broker PF stdev ≤ 0.30.

### Q3: MFE/MAE analysis?
**A:** CMfeMaeLogger.mqh: per-trade max favorable/adverse excursion CSV. mfe_mae.py analyzer: edge ratio, optimal exit/SL.

### Q4: Overfit detection metrics?
**A:** OOS PF / IS PF ratio. Tester-set complexity (inputs × passes). AP-5 gate: > 6 inputs + > 100k passes = WARN.

### Q5: Cross-broker stability metrics?
**A:** PF stdev/mean, Sharpe stdev, DD diff (max-min). Tolerance: 0.30, 0.20, 5% respectively.

### Q6: Quality matrix (8×8)?
**A:** 8 dimensions × 8 stress axes = 64 cells. Each PASS/FAIL/N-A. Enterprise: ≥ 56 PASS. HTML report output.

### Q7: Trader-17 checklist coverage?
**A:** 17 checkpoint items. ≥ 15 PASS required (all modes). Dict output with PASS/WARN/N-A per item.

### Q8: Conformance test budget?
**A:** 70 total: 10 e2e external (real compile + tester) + 60 internal probes. All 70 must pass for v1.0.0.

### Q9: Canary monitoring metrics?
**A:** 30min window: trades executed, spread stability, connection uptime, DD delta. Alert threshold configurable.

### Q10: Latency requirements?
**A:** HFT async: OrderSendAsync response < 100ms. ONNX inference < 50ms per tick. LLM bridge: 5s timeout.

### Q11: Cost optimization?
**A:** Cloud Network: cost calculator before submission. Budget cap enforcement. Mode gate (only ENTERPRISE can use cloud).

### Q12: Regression testing strategy?
**A:** audit-plan-v5.py per-phase. 70 conformance tests as regression guard. CI on every PR. No regression = no merge.

---

## RRI Summary

| Category | Count | Status |
|----------|-------|--------|
| Total questions synthesized | 72 (12 × 6 personas) |Done |
| Critical requirements identified | 18 |  |
| Risks flagged | 8 |  |
| Integration points | 12 |  |

### Top 5 Critical Requirements (REQ-*)
1. **REQ-PIP**: CPipNormalizer must handle 5d/4d/3d/2d correctly across all brokers
2. **REQ-RISK**: CRiskGuard daily-loss + max-positions enforcement on every trade
3. **REQ-AP8**: 8 critical anti-patterns must block merge (not just warn)
4. **REQ-MULTI**: Multi-broker stability gate (3 brokers, tolerance thresholds)
5. **REQ-AUDIT**: Anti-drift audit runs pre/post every phase, zero tolerance

### Top 5 Risks
1. **RISK-WINE**: Wine + MetaEditor setup fragile on CI (mitigate: xvfb, retry)
2. **RISK-BROKER**: Demo account credentials expire (mitigate: user-provided, session-scoped)
3. **RISK-ONNX**: PyTorch/ONNX heavy deps may break CI (mitigate: optional extras)
4. **RISK-LOC**: Script size creep past 200 LOC (mitigate: audit enforcement)
5. **RISK-MCP**: mt5-bridge accidental trade mutation (mitigate: grep-based test, READ-ONLY policy)

---

**RRI CYCLE 1 COMPLETE.** Ready for Step 3 — VISION.
