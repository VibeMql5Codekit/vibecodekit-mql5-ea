# XAUUSD H4 Hedging Scalper — Worked Example

> **Deep test demo** — toàn bộ pipeline 10 bước + review tools + Phase D/E tools
> trên XAUUSD H4 hedging mode với chiến lược EMA 9/21 crossover + RSI(14) filter.

---

## EA Specs

| Thông số | Giá trị |
|---------|---------|
| **EA Name** | XauScalperEA |
| **Symbol** | XAUUSD |
| **Timeframe** | H4 |
| **Mode** | Hedging |
| **Strategy** | EMA 9/21 crossover + RSI(14) filter (30-70 range) |
| **SL** | 300 pips (via CPipNormalizer) |
| **TP** | 600 pips (via CPipNormalizer) |
| **Risk** | 1% per trade (via CRiskGuard) |
| **Preset** | `scalping` |
| **Stack** | `hedging` |

---

## Pipeline Results

### Bước 1-5: Build & Validate

| Bước | Tool | Kết quả |
|------|------|---------|
| 1. Scaffold | `mql5-build --preset scalping --stack hedging` | XauScalperEA.mq5 (95 LOC) |
| 2. Code | Manual strategy | EMA 9/21 + RSI(14) + hedging buy/sell |
| 3. Lint | `mql5-lint` | 0 CRITICAL, 4 warnings (AP-04, AP-06, AP-08×2) |
| 4. Pip Check | `mql5-pip-normalize` | 0 hardcoded pip patterns |
| 5. Compile | `mql5-compile` | SUCCESS (0 errors, 1 warning) |

### Bước 6-9: Backtest & Validation

| Bước | Tool | Kết quả | Gate |
|------|------|---------|------|
| 6. Backtest | `mql5-backtest` | PF=1.87, Sharpe=1.62, DD=8.45%, 412 trades | — |
| 7. Walk-forward | `mql5-walkforward` | IS PF=2.10 → OOS PF=1.72, ratio=0.819 | **PASS** |
| 8. Monte Carlo | `mql5-monte-carlo` | DD95=13.67%, ratio=1.62 | **WARN** (>1.5) |
| 9. Multi-broker | `mql5-multibroker` | PF CV=0.022, 3 brokers | **PASS** |

### Bước 10: Permission Pipeline

| Mode | Layers | Result | Blocked at |
|------|--------|--------|-----------|
| PERSONAL | L1-L4, L7 | **FAIL** | L4 (9/17 < 15 required) |
| TEAM | L1-L5, L7 | **FAIL** | L4 |
| ENTERPRISE | L1-L7 | **FAIL** | L4 |

**Action items để pass L4:**
- Thêm spread check trước entry (T04)
- Thêm slippage protection (T05)
- Thêm session/news guard (T06)
- Reference multi-broker test (T08)
- Reference walk-forward validation (T09)
- Reference Monte Carlo simulation (T10)

---

## Review Results

| Tool | Kết quả |
|------|---------|
| `mql5-review` (7 specialists) | 5 patterns found, 0 warnings |
| `mql5-cso` (security) | 9/10 pass, 1 FAIL (S09: array bounds) |
| `mql5-eng-review` (8 invariants) | 7/8 pass, 1 warning (error_handling) |
| `mql5-ceo-review` (HOLD mode) | No issues (95 LOC, 4 inputs) |
| `mql5-investigate` (root cause) | 2 patterns: magic_collision, no_error_check |

---

## Phase D Tools

| Tool | Kết quả |
|------|---------|
| `mql5-cloud-optimize` (PERSONAL) | **BLOCKED** — dùng local optimization |
| `mql5-cloud-optimize` (TEAM, $30) | OK — 64 agents |
| `mql5-method-hiding-check` | 0 issues |
| `mql5-async-build` | XauHFT scaffold tạo thành công |
| `mql5-forge-init` | Workspace tạo, 4 parameters extracted |
| `mql5-forge-pr` | [] (chưa có backtest candidates) |

---

## Phase E Tools

| Tool | Kết quả |
|------|---------|
| `mql5-scan` | 33 .mq5, 7 .mqh, 1003 .py, 17 scaffolds |
| `mql5-doctor` | 18/18 checks pass |
| `mql5-audit` | 50/50 PASS |
| `mql5-ship` (dry-run) | v1.0.0 tag (dry-run OK) |
| `mql5-survey` | 17 presets categorized |
| `mql5-vision` | KPIs: PF≥1.87, DD≤8.45%, Sharpe≥1.62 |
| `mql5-blueprint` | 8 sections generated |
| `mql5-tip` | 10 TIPs, ~1350 min total |
| `mql5-second-opinion` | 3685-char prompt generated |
| `mql5-deploy-vps` | Deployed (30min canary window) |
| `mql5-trader-check` | 9/17 PASS, 2 WARN, 6 N-A |
| `mql5-overfit-check` | PF ratio 0.819, drop 18.1% — HEALTHY |
| `mql5-fitness` (profit_factor) | Score: 1.87 |
| `mql5-broker-safety` | PASS |

---

## File Structure

```
examples/xauusd-hedging-scalper-4h/
├── README.md                    ← This file
├── XauScalperEA/
│   ├── XauScalperEA.mq5         ← EA source code (95 LOC)
│   ├── README.md                ← Scaffold readme
│   └── Sets/
│       └── default.set          ← Optimization parameters
├── fixtures/
│   ├── backtest-xauusd-h4.xml   ← Backtest report (412 trades)
│   ├── is-report.xml            ← In-Sample report (280 trades)
│   ├── oos-report.xml           ← Out-of-Sample report (132 trades)
│   ├── broker-exness.xml        ← Exness broker report
│   ├── broker-icmarkets.xml     ← ICMarkets broker report
│   └── broker-fxpro.xml         ← FxPro broker report
├── results/
│   ├── backtest-summary.json    ← Parsed backtest metrics
│   ├── walkforward.json         ← Walk-forward IS/OOS results
│   ├── monte-carlo.json         ← Monte Carlo DD simulation
│   ├── multibroker.json         ← Multi-broker stability
│   ├── permission-personal.json ← Permission pipeline results
│   └── review-summary.json      ← All review tool results
└── .forge/
    └── forge-config.json        ← Algo Forge workspace
```

---

## Kết luận

Pipeline hoạt động đúng — phát hiện EA **chưa đạt** Trader-17 checklist (9/17 < 15 required).
Để pass permission gate, cần thêm:
1. Spread filter (CSpreadGuard)
2. Slippage protection (trade deviation)
3. Session/news guard
4. Error retry logic
5. Trailing stop implementation
6. Max positions check enhancements

**Tổng cộng 44 CLI tools đã chạy thành công trong demo này.**
