# Hướng dẫn sử dụng toàn diện — vibecodekit-mql5-ea

> Tài liệu đầy đủ step-by-step cho **người mới** và **dev team**.
> Hỗ trợ: **Devin AI** · **Codex CLI** · **Codex App** · **Claude Code** · **Cursor** · **Terminal**

---

## Mục lục

**Phần I — Tổng quan**
1. [Giới thiệu tool](#1-giới-thiệu-tool)
2. [Cài đặt](#2-cài-đặt)

**Phần II — Pipeline build EA**
3. [Pipeline 10 bước](#3-pipeline-10-bước-build-ea)
4. [Bước 1: Scaffold — Tạo EA skeleton](#4-scaffold--tạo-ea-skeleton)
5. [Bước 2: Code — Viết strategy logic](#5-code--viết-strategy-logic)
6. [Bước 3: Lint — Kiểm tra anti-patterns](#6-lint--kiểm-tra-anti-patterns)
7. [Bước 4-5: Pip Check & Compile](#7-pip-check--compile)
8. [Bước 6-9: Backtest → Monte Carlo → Multi-broker](#8-backtest--walkforward--monte-carlo--multi-broker)
9. [Bước 10: Permission Pipeline — Final gate](#9-permission-pipeline--final-quality-gate)

**Phần III — Chạy trên các môi trường AI**
10. [Devin AI Session](#10-devin-ai-session)
11. [Codex CLI (Terminal)](#11-codex-cli-terminal)
12. [Codex App (Desktop Window)](#12-codex-app-desktop-window)
13. [Claude Code CLI](#13-claude-code-cli)
14. [Cursor IDE](#14-cursor-ide)
15. [Terminal thuần (Manual)](#15-terminal-thuần-manual)

**Phần IV — Chức năng nâng cao**
16. [Review & Audit Tools (5 loại)](#16-review--audit-tools)
17. [ONNX & Machine Learning](#17-onnx--machine-learning)
18. [LLM Bridge (3 variants)](#18-llm-bridge)
19. [Algo Forge — Strategy iteration](#19-algo-forge--strategy-iteration)
20. [MCP Server Integration](#20-mcp-server-integration)
21. [Phase E — Polish & Ship](#21-phase-e--polish--ship)

**Phần V — Dev Team Workflow**
22. [Quy trình cho team](#22-quy-trình-cho-dev-team)
23. [Danh sách đầy đủ 45 CLI Commands](#23-danh-sách-đầy-đủ-45-cli-commands)
24. [Troubleshooting](#24-troubleshooting)
25. [Tham khảo & Links](#25-tham-khảo--links)

---

# Phần I — Tổng quan

## 1. Giới thiệu tool

**vibecodekit-mql5-ea** là bộ công cụ phát triển Expert Advisor (EA) cho MetaTrader 5, cung cấp:

| Thành phần | Số lượng | Mô tả |
|-----------|---------|-------|
| CLI Tools | 45 | Build, lint, compile, backtest, review, deploy |
| Scaffold Presets | 17 | stdlib, scalping, trend, grid, ml-onnx, hft-async, ... |
| MQL5 Libraries | 7 | CPipNormalizer, CRiskGuard, CMagicRegistry, CSpreadGuard, CMfeMaeLogger, COnnxLoader, CAsyncTradeManager |
| Tests | 154 collected | Phase 0-E acceptance tests (152 pass, 2 Wine/MetaEditor skips in local Linux smoke) |
| MCP Servers | 3 | metaeditor-bridge, mt5-bridge (10 tools), algo-forge (6 tools) |
| Review Scripts | 5 | Multi-specialist, CSO, engineering, CEO, investigation |
| RRI Personas | 6 | trader, risk-auditor, broker-engineer, strategy-architect, devops, perf-analyst |
| Reference Docs | 45 | Cheat sheets, best practices, methodology guides |

**Dành cho ai:**
- **Trader** muốn build EA theo quy trình chuyên nghiệp
- **Developer** làm MQL5 cần quality gate và automation
- **Team** cần chuẩn hóa quy trình build/review/ship EA

---

## 2. Cài đặt

### 2.1 Yêu cầu tối thiểu

| Yêu cầu | Bắt buộc | Version |
|---------|---------|---------|
| Python | Có | 3.10+ |
| Git | Có | Any |
| pip hoặc uv | Có | Any |
| Wine | Không (cho compile thật) | 8.0+ |
| MetaTrader 5 | Không (cho live trading) | Build 4000+ |
| Node.js | Không (cho Codex/Claude CLI) | 18+ |

### 2.2 Cài đặt cơ bản (2 phút)

```bash
# Bước 1: Clone repo
git clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
cd vibecodekit-mql5-ea

# Bước 2: Tạo virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# Bước 3: Cài package + dev dependencies
pip install -e ".[dev]"

# Bước 4: Verify
mql5-build --list           # → 17 presets
pytest tests/ -q            # → 152 passed, 2 skipped locally without Wine/MetaEditor
```

### 2.3 Cài Wine + MetaEditor (tùy chọn — cho compile thật)

```bash
# Ubuntu/Debian
sudo dpkg --add-architecture i386
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/$(lsb_release -cs)/winehq-$(lsb_release -cs).sources
sudo apt update && sudo apt install -y --install-recommends winehq-stable

# Setup Wine prefix + MetaEditor stub
export WINEPREFIX=~/.wine-mql5
sudo bash scripts/setup-wine-metaeditor.sh
source ~/.mql5-env
```

### 2.4 Cài AI tools (tùy chọn)

```bash
# Codex CLI
npm install -g @openai/codex

# Claude Code
npm install -g @anthropic-ai/claude-code

# Cursor: Download từ https://cursor.sh
```

---

# Phần II — Pipeline build EA

## 3. Pipeline 10 bước build EA

```
┌──────────┐   ┌──────┐   ┌────────┐   ┌─────────┐   ┌──────────┐
│ SCAFFOLD │──▶│ CODE │──▶│  LINT  │──▶│ COMPILE │──▶│ BACKTEST │
│ mql5-    │   │ edit │   │ 13 AP  │   │MetaEdit │   │ XML parse│
│ build    │   │ /AI  │   │        │   │         │   │          │
└──────────┘   └──────┘   └────────┘   └─────────┘   └──────────┘
                                                           │
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐  │
│   SHIP   │◀──│PERMISSION│◀──│MULTIBRK  │◀──│WALK-FWD │◀─┘
│ deploy   │   │ 7 layer  │   │ 3 broker │   │+ M.Carlo│
└──────────┘   └──────────┘   └──────────┘   └─────────┘
```

| # | Bước | CLI Tool | Input | Output | Bắt buộc? |
|---|------|----------|-------|--------|-----------|
| 1 | **Scaffold** | `mql5-build` | preset + stack + name | EA skeleton (.mq5 + .mqh) | Có |
| 2 | **Code** | Editor / AI | EA skeleton | Strategy logic hoàn chỉnh | Có |
| 3 | **Lint** | `mql5-lint` | .mq5 file | 0 CRITICAL = pass | Có |
| 4 | **Pip Check** | `mql5-pip-normalize` | .mq5 file | Không hardcode pip | Có |
| 5 | **Compile** | `mql5-compile` | .mq5 file | .ex5 binary | Không (cần Wine) |
| 6 | **Backtest** | `mql5-backtest` | report.xml | PF, Sharpe, DD, Win% | Không (cần MT5 data) |
| 7 | **Walk-forward** | `mql5-walkforward` | IS.xml + OOS.xml | PASS/FAIL | Không (cần backtest) |
| 8 | **Monte Carlo** | `mql5-monte-carlo` | report.xml | DD50/75/95 percentiles | Không (cần backtest) |
| 9 | **Multi-broker** | `mql5-multibroker` | 3× report.xml | CV ≤ 0.30 = stable | Không (cần 3 brokers) |
| 10 | **Permission** | `mql5-permission` | .mq5 + mode | all_pass = SHIP | Có |

> **Người mới:** Chỉ cần bước 1-4 + 10 để build EA cơ bản.
> **Production:** Cần tất cả 10 bước.

---

## 4. Scaffold — Tạo EA skeleton

### 4.1 Xem danh sách presets

```bash
mql5-build --list
```

Output:
```
Available presets:
  stdlib: netting, hedging, python-bridge
  wizard-composable: netting
  portfolio-basket: hedging, netting
  ml-onnx: python-bridge
  hft-async: netting
  trend: netting, hedging
  mean-reversion: netting
  breakout: netting
  grid: hedging
  dca: hedging
  scalping: netting
  hedging-multi: hedging
  news-trading: netting
  arbitrage-stat: netting
  indicator-only: (no stack)
  library: (no stack)
  service-llm-bridge: cloud-api, embedded-onnx-llm, self-hosted-ollama
```

### 4.2 Tạo EA mới

```bash
mql5-build --preset trend --stack netting --name TrendMasterEA --output ./output/
```

**Output:**
```
Rendered trend/netting -> ./output/TrendMasterEA
```

**Cấu trúc file tạo ra:**
```
output/TrendMasterEA/
├── TrendMasterEA.mq5       ← File EA chính
├── CPipNormalizer.mqh       ← Chuẩn hóa pip (auto-included)
├── CRiskGuard.mqh           ← Quản lý risk (auto-included)
└── CMagicRegistry.mqh       ← Magic number registry (auto-included)
```

### 4.3 Bảng 17 presets

| # | Preset | Mô tả | Stack options |
|---|--------|--------|--------------|
| 1 | `stdlib` | Standard Library EA cơ bản | netting, hedging, python-bridge |
| 2 | `wizard-composable` | MQL5 Wizard (CExpert framework) | netting |
| 3 | `portfolio-basket` | Multi-symbol portfolio/basket | hedging, netting |
| 4 | `ml-onnx` | Machine learning với ONNX inference | python-bridge |
| 5 | `hft-async` | High-frequency async trading | netting |
| 6 | `trend` | Trend-following strategy | netting, hedging |
| 7 | `mean-reversion` | Mean-reversion strategy | netting |
| 8 | `breakout` | Breakout strategy | netting |
| 9 | `grid` | Grid trading | hedging |
| 10 | `dca` | Dollar-cost averaging | hedging |
| 11 | `scalping` | Scalping strategy | netting |
| 12 | `hedging-multi` | Multi-pair hedging | hedging |
| 13 | `news-trading` | News event trading | netting |
| 14 | `arbitrage-stat` | Statistical arbitrage | netting |
| 15 | `indicator-only` | Custom indicator (không phải EA) | — |
| 16 | `library` | MQL5 library module | — |
| 17 | `service-llm-bridge` | LLM bridge service | cloud-api, embedded-onnx-llm, self-hosted-ollama |

### 4.4 Chọn preset phù hợp

| Loại strategy | Preset gợi ý | Stack |
|--------------|-------------|-------|
| EMA/MACD crossover | `trend` | netting |
| RSI/Bollinger bands | `mean-reversion` | netting |
| Breakout highs/lows | `breakout` | netting |
| Grid trading (XAUUSD) | `grid` | hedging |
| DCA (mua dần) | `dca` | hedging |
| Scalping M1/M5 | `scalping` | netting |
| Multi-pair hedge | `hedging-multi` | hedging |
| ML/AI strategy | `ml-onnx` | python-bridge |
| HFT sub-second | `hft-async` | netting |
| Standard (mới bắt đầu) | `stdlib` | netting |

---

## 5. Code — Viết strategy logic

Mở file `.mq5` và tìm phần `// --- YOUR STRATEGY LOGIC HERE ---`, thay bằng logic của bạn.

### 5.1 Ví dụ: EMA Crossover strategy

```cpp
void OnTick()
{
    if(!riskGuard.CanOpenTrade()) return;

    // === EMA CROSSOVER STRATEGY ===
    double maFast = iMA(_Symbol, PERIOD_H1, 20, 0, MODE_EMA, PRICE_CLOSE);
    double maSlow = iMA(_Symbol, PERIOD_H1, 50, 0, MODE_EMA, PRICE_CLOSE);

    double fastVal[], slowVal[];
    CopyBuffer(maFast, 0, 0, 2, fastVal);
    CopyBuffer(maSlow, 0, 0, 2, slowVal);

    bool buySignal  = fastVal[0] > slowVal[0] && fastVal[1] <= slowVal[1];
    bool sellSignal = fastVal[0] < slowVal[0] && fastVal[1] >= slowVal[1];

    if(buySignal)
    {
        double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
        double sl  = ask - pipNorm.Pips(InpSLPips);  // Dùng CPipNormalizer
        double tp  = ask + pipNorm.Pips(InpTPPips);
        double lots = pipNorm.LotForRisk(
            AccountInfoDouble(ACCOUNT_BALANCE) * InpRiskPercent / 100.0,
            InpSLPips
        );
        trade.Buy(lots, _Symbol, ask, sl, tp, "TrendMaster buy");
    }

    if(sellSignal)
    {
        double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double sl  = bid + pipNorm.Pips(InpSLPips);
        double tp  = bid - pipNorm.Pips(InpTPPips);
        double lots = pipNorm.LotForRisk(
            AccountInfoDouble(ACCOUNT_BALANCE) * InpRiskPercent / 100.0,
            InpSLPips
        );
        trade.Sell(lots, _Symbol, bid, sl, tp, "TrendMaster sell");
    }
}
```

### 5.2 Quy tắc viết code bắt buộc

| Quy tắc | Đúng | Sai |
|---------|------|-----|
| Pip calculation | `pipNorm.Pips(30)` | `_Point * 300` |
| Lot size | `pipNorm.LotForRisk(money, sl)` | `0.1` (hardcoded) |
| Order | `trade.Buy(...)` | `OrderSend(request, result)` |
| Logging | `PrintFormat("PF=%.2f", pf)` | `Print("PF=" + pf)` |
| Stop loss | Luôn có `sl != 0` | `trade.Buy(lots, sym, price, 0, tp)` |
| Parameters | Tối đa 6 input | 15 inputs (overfitting) |
| File length | ≤ 200 LOC | 500+ LOC |

---

## 6. Lint — Kiểm tra anti-patterns

### 6.1 Chạy lint

```bash
mql5-lint output/TrendMasterEA/TrendMasterEA.mq5
```

**Clean output:**
```
TrendMasterEA.mq5: PASS (0 findings)
```

**Nếu có lỗi:**
```
TrendMasterEA.mq5: FAIL
  Line 45: AP-01 CRITICAL — No stop-loss: trade.Buy() without SL parameter
  Line 62: AP-20 CRITICAL — Hardcoded pip value: _Point * 10
  Line 78: AP-07 WARNING — Print() used instead of PrintFormat()
```

### 6.2 Danh sách 13 anti-patterns

| ID | Mức | Mô tả | Cách fix |
|----|-----|--------|---------|
| AP-01 | CRITICAL | Không có stop-loss | Thêm `sl` vào `trade.Buy/Sell()` |
| AP-03 | CRITICAL | Fixed lot size (hardcoded) | Dùng `pipNorm.LotForRisk()` |
| AP-05 | CRITICAL | Quá nhiều input (>6) | Giảm input parameters |
| AP-15 | CRITICAL | Raw OrderSend | Dùng `CTrade` class |
| AP-17 | CRITICAL | WebRequest trong OnTick | Chuyển ra OnTimer hoặc background |
| AP-18 | CRITICAL | OrderSendAsync không có handler | Thêm `OnTradeTransaction()` |
| AP-20 | CRITICAL | Hardcoded pip value | Dùng `pipNorm.Pips()` |
| AP-21 | CRITICAL | JPY/XAU pip sai | Dùng `CPipNormalizer` auto-detect |
| AP-02 | WARNING | Không có take-profit | Cân nhắc thêm TP |
| AP-04 | WARNING | Không có trailing stop | Cân nhắc trailing |
| AP-06 | WARNING | Không có error retry | Thêm retry logic |
| AP-07 | WARNING | Print() thay PrintFormat() | Đổi sang `PrintFormat()` |
| AP-08 | WARNING | Không có comment trên trade | Thêm comment string |

> **CRITICAL** = block pipeline (phải fix).
> **WARNING** = cảnh báo (nên fix nhưng không bắt buộc).

---

## 7. Pip Check & Compile

### 7.1 Pip Check

```bash
mql5-pip-normalize output/TrendMasterEA/TrendMasterEA.mq5
```

Phát hiện các pattern sai:
- `_Point * 10` → sai cho JPY pairs (3 digits)
- `_Point * 100` → sai cho XAU (2 digits)
- Hardcoded `0.0001` → sai cho tất cả trừ 4-digit pairs

### 7.2 Compile (cần Wine + MetaEditor)

```bash
mql5-compile output/TrendMasterEA/TrendMasterEA.mq5 --include ./Include/
```

Output thành công:
```
Compilation successful: TrendMasterEA.ex5
0 errors, 0 warnings
```

> **Không có Wine?** Bỏ qua bước này — tool vẫn hoạt động cho scaffold/lint/review.
> MetaEditor compile chỉ cần khi muốn tạo file `.ex5` để chạy trên MT5.

---

## 8. Backtest → Walk-forward → Monte Carlo → Multi-broker

### 8.1 Backtest — Parse kết quả Strategy Tester

```bash
# Sau khi chạy Strategy Tester trong MT5, export report XML
mql5-backtest report.xml --json
```

Output:
```json
{
  "symbol": "EURUSD",
  "total_trades": 728,
  "profit_factor": 1.52,
  "sharpe_ratio": 1.34,
  "max_drawdown_pct": 10.23,
  "recovery_factor": 3.40,
  "win_rate": 53.4,
  "net_profit": 5234.56
}
```

### 8.2 Walk-forward — IS/OOS validation

```bash
mql5-walkforward is_report.xml oos_report.xml --min-pf 1.5
```

Output:
```
IS PF: 2.10  |  OOS PF: 1.80
PF ratio (OOS/IS): 0.857
IS Sharpe: 1.50  |  OOS Sharpe: 1.30
DD diff: 2.50%

Walk-forward gate: PASS
```

**PASS criteria:**
- OOS Profit Factor ≥ 1.5
- PF ratio (OOS/IS) ≥ 0.5

### 8.3 Monte Carlo — DD simulation

```bash
mql5-monte-carlo report.xml --runs 10000
```

Output:
```
Monte Carlo (10000 runs, 728 trades):
  DD 50th percentile: 8.23%
  DD 75th percentile: 11.45%
  DD 95th percentile: 15.67%
```

**Đánh giá:** DD95 nên ≤ 1.5× actual max DD.

### 8.4 Multi-broker — Stability gate

```bash
mql5-multibroker broker1.xml broker2.xml broker3.xml
```

Output:
```
Broker 1: PF=1.52  Broker 2: PF=1.48  Broker 3: PF=1.55
Mean PF: 1.517  Stdev: 0.035  CV: 0.023

Multi-broker gate: PASS (CV=0.023 ≤ 0.30)
```

**PASS criteria:** CV (coefficient of variation) ≤ 0.30

---

## 9. Permission Pipeline — Final quality gate

### 9.1 Chạy permission check

```bash
# Qua CLI tool
mql5-permission output/TrendMasterEA/TrendMasterEA.mq5 --mode PERSONAL

# Hoặc qua Python
python -c "
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
import json
result = run_permission_pipeline('output/TrendMasterEA/TrendMasterEA.mq5', 'PERSONAL')
print(json.dumps(result, indent=2))
"
```

### 9.2 Bảng 7 layers

| Layer | Tên | Kiểm tra gì | PERSONAL | TEAM | ENTERPRISE |
|-------|-----|-------------|----------|------|-----------|
| L1 | source_lint | `#property strict`, copyright, file length | ✓ | ✓ | ✓ |
| L2 | compile | MetaEditor compile (skip nếu chưa cài) | ✓ | ✓ | ✓ |
| L3 | ap_lint | 13 anti-pattern (CRITICAL = block) | ✓ | ✓ | ✓ |
| L4 | checklist | Trader-17 checklist (≥15/17 PASS) | ✓ | ✓ | ✓ |
| L5 | methodology | Required libs (CPipNorm, CRiskGuard, CMagicReg) | — | ✓ | ✓ |
| L6 | quality_matrix | 8×8 matrix scoring (avg ≥ 40%) | — | — | ✓ |
| L7 | broker_safety | Pip normalization, spread, margin | ✓ | ✓ | ✓ |

### 9.3 Chọn mode phù hợp

| Mode | Khi nào dùng | Layers | Mức nghiêm ngặt |
|------|-------------|--------|-----------------|
| `PERSONAL` | EA cho bản thân trade | L1-L4, L7 | Cơ bản |
| `TEAM` | Chia sẻ trong team dev | L1-L5, L7 | Trung bình |
| `ENTERPRISE` | Bán / phân phối EA | L1-L7 | Cao nhất |

### 9.4 Ví dụ output

```json
{
  "mode": "PERSONAL",
  "layers_run": 5,
  "all_pass": true,
  "results": {
    "L1": {"pass": true, "details": "OK"},
    "L2": {"pass": true, "details": "MetaEditor not installed — skipped"},
    "L3": {"pass": true, "details": "0 critical, 1 warning"},
    "L4": {"pass": true, "details": "16/17 PASS"},
    "L7": {"pass": true, "details": "OK"}
  }
}
```

---

# Phần III — Chạy trên các môi trường AI

## 10. Devin AI Session

### 10.1 Quick Start (3 phút)

1. Vào [app.devin.ai](https://app.devin.ai) → **New Session**
2. Paste prompt sau:

```
Clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
pip install -e ".[dev]"
pytest tests/ -q
mql5-build --list
Báo kết quả.
```

**Expected locally:** `152 passed, 2 skipped` when Wine/MetaEditor are unavailable; 17 presets.

### 10.2 Build EA hoàn chỉnh

```
Clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git

Build EA mới theo quy trình:

1. pip install -e ".[dev]"
2. mql5-build --preset trend --stack netting --name GoldTrendEA --output ./output
3. Sửa file output/GoldTrendEA/GoldTrendEA.mq5:
   - Entry: EMA 20 cross EMA 50 trên XAUUSD H1
   - SL: 300 pips (dùng CPipNormalizer)
   - TP: 600 pips
   - Risk: 1% per trade (dùng CRiskGuard)
4. mql5-lint output/GoldTrendEA/GoldTrendEA.mq5
5. Fix ALL CRITICAL findings
6. mql5-pip-normalize output/GoldTrendEA/GoldTrendEA.mq5
7. Chạy permission pipeline mode=PERSONAL
8. Báo kết quả lint + permission
```

### 10.3 Prompt template (copy-paste)

```markdown
## Build EA với vibecodekit-mql5-ea

**Repo:** https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git

**EA specs:**
- Tên: {EA_NAME}
- Symbol: {SYMBOL}
- Timeframe: {TIMEFRAME}
- Strategy: {MÔ_TẢ_STRATEGY}
- Preset: {PRESET}
- Stack: {STACK}

**Quy trình bắt buộc:**
1. `pip install -e ".[dev]"`
2. `mql5-build --preset {PRESET} --stack {STACK} --name {EA_NAME} --output ./output/`
3. Viết strategy logic vào file {EA_NAME}.mq5
4. `mql5-lint output/{EA_NAME}/{EA_NAME}.mq5` → fix ALL CRITICAL
5. `mql5-pip-normalize output/{EA_NAME}/{EA_NAME}.mq5`
6. Chạy `mql5-permission output/{EA_NAME}/{EA_NAME}.mq5 --mode PERSONAL`
7. Báo kết quả
```

### 10.4 Tips cho Devin session

- **Blueprint:** Nếu repo có blueprint, Devin sẽ auto-install dependencies
- **Chia nhỏ:** EA phức tạp → chia 2 session (build → test)
- **Test:** Dùng `pytest tests/ -q` để verify tool hoạt động
- **SKILL.md:** Devin sẽ tự đọc `.agents/skills/` nếu có

---

## 11. Codex CLI (Terminal)

### 11.1 Setup

```bash
# Cài Codex CLI
npm install -g @openai/codex

# Clone + install
git clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
cd vibecodekit-mql5-ea
pip install -e ".[dev]"
```

### 11.2 Scaffold EA

```bash
codex "Chạy mql5-build --preset scalping --stack netting --name FastScalper --output ./output
Rồi mql5-lint output/FastScalper/FastScalper.mq5
Báo kết quả."
```

### 11.3 Build EA hoàn chỉnh

```bash
codex "Dùng vibecodekit-mql5-ea:
1. mql5-build --preset trend --stack netting --name MACDTrend --output ./output/
2. Viết MACD crossover strategy vào MACDTrend.mq5:
   - Buy: MACD histogram từ âm sang dương + price > EMA(50)
   - Sell: MACD histogram từ dương sang âm + price < EMA(50)
   - Giữ nguyên SL/TP/lot calculation sẵn có
3. mql5-lint output/MACDTrend/MACDTrend.mq5 → fix nếu có lỗi
4. Chạy permission pipeline mode=PERSONAL
5. Báo kết quả"
```

### 11.4 Audit EA có sẵn

```bash
codex "Dùng vibecodekit-mql5-ea:
1. mql5-lint path/to/MyEA.mq5
2. mql5-trader-check --ea path/to/MyEA.mq5
3. Chạy permission pipeline ENTERPRISE mode
4. Tổng hợp: bao nhiêu critical, warning, trader score, permission pass/fail"
```

### 11.5 Full pipeline 1 lệnh

```bash
codex "Đọc file docs/GUIDE-BUILD-EA.md section 8 (Manual CLI) và chạy tất cả lệnh. Báo kết quả từng bước."
```

---

## 12. Codex App (Desktop Window)

OpenAI Codex App là phiên bản GUI desktop của Codex, chạy qua cửa sổ ứng dụng thay vì terminal.

### 12.1 Setup

1. Mở **Codex App** → Settings → chọn workspace folder
2. Mở terminal trong app (hoặc dùng integrated terminal)
3. Clone + install:

```
git clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
cd vibecodekit-mql5-ea
pip install -e ".[dev]"
```

### 12.2 Dùng Codex App để build EA

Trong chat window của Codex App, gõ:

```
Dùng vibecodekit-mql5-ea tool trong workspace:

1. Scaffold: mql5-build --preset stdlib --stack netting --name DemoEA --output ./output
2. Viết strategy: Bollinger Bands (20,2) — buy lower band, sell upper band
3. Lint: mql5-lint output/DemoEA/DemoEA.mq5
4. Permission: chạy mql5-permission output/DemoEA/DemoEA.mq5 --mode PERSONAL
5. Tổng hợp kết quả
```

### 12.3 Tips cho Codex App

- **File explorer:** Mở file `.mq5` để xem/sửa trực tiếp trong app
- **Terminal:** Dùng integrated terminal để chạy CLI commands
- **Context:** Codex App tự đọc file trong workspace → hiểu project structure
- **Multi-file:** Có thể yêu cầu sửa nhiều file cùng lúc (EA + Include)

---

## 13. Claude Code CLI

### 13.1 Setup

```bash
# Cài Claude Code
npm install -g @anthropic-ai/claude-code

# Clone + install
git clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
cd vibecodekit-mql5-ea
pip install -e ".[dev]"
```

### 13.2 Interactive mode

```bash
claude
```

Trong interactive session:
```
> mql5-build --list
> mql5-build --preset stdlib --stack netting --name TestEA --output /tmp/test
> mql5-lint /tmp/test/TestEA/TestEA.mq5
> mql5-permission /tmp/test/TestEA/TestEA.mq5 --mode PERSONAL
```

### 13.3 Batch mode (1 lệnh)

```bash
claude -p "Clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git,
install với pip install -e '.[dev]',
mql5-build --list,
scaffold preset 'ml-onnx' stack 'python-bridge' name 'MLTrader',
lint kết quả,
chạy permission pipeline ENTERPRISE mode,
báo summary."
```

### 13.4 Tạo CLAUDE.md cho project

Tạo file `CLAUDE.md` ở root project để Claude Code tự hiểu context:

```markdown
# vibecodekit-mql5-ea

## Quick Start
pip install -e ".[dev]"
pytest tests/ -q  # → 152 passed, 2 skipped locally without Wine/MetaEditor

## CLI Tools (top 10 dùng nhiều nhất)
- `mql5-build --preset <name> --stack <stack> --name <ea> --output <dir>`
- `mql5-lint <path>`
- `mql5-compile <path>`
- `mql5-backtest <report.xml>`
- `mql5-walkforward <is.xml> <oos.xml>`
- `mql5-monte-carlo <report.xml>`
- `mql5-multibroker <broker1.xml> <broker2.xml> <broker3.xml>`
- `mql5-trader-check --ea <path>`
- `mql5-permission <path> --mode <PERSONAL|TEAM|ENTERPRISE>`
- `mql5-review --ea <path> --mode FULL`

## Quy tắc
- PHẢI dùng CPipNormalizer cho pip calculation
- PHẢI dùng CRiskGuard cho risk management
- PHẢI dùng CMagicRegistry cho magic numbers
- KHÔNG dùng raw OrderSend → dùng CTrade
- KHÔNG hardcode lot → dùng LotForRisk()
- Max 6 input parameters
- Mỗi file ≤ 200 LOC
```

### 13.5 Build nhiều EA cùng lúc

```bash
claude -p "Build 3 EA variants cho EURUSD H1:
1. TrendEA (preset=trend, EMA crossover 20/50)
2. ScalpEA (preset=scalping, RSI 14 oversold/overbought)
3. GridEA (preset=grid, fixed grid 50 pips)

Cho mỗi EA: scaffold → viết strategy → lint → permission PERSONAL → báo bảng tổng hợp"
```

---

## 14. Cursor IDE

### 14.1 Setup workspace

1. Mở **Cursor** → `File > Open Folder` → chọn thư mục `vibecodekit-mql5-ea`
2. Mở terminal trong Cursor (`Ctrl+`` `) → cài dependencies:

```bash
pip install -e ".[dev]"
pytest tests/ -q
```

### 14.2 Cấu hình MCP Servers

Tạo file `.cursor/mcp.json` trong root project:

```json
{
  "mcpServers": {
    "metaeditor-bridge": {
      "command": "python",
      "args": ["mcp/metaeditor-bridge/server.py"],
      "cwd": "."
    },
    "algo-forge-bridge": {
      "command": "python",
      "args": ["mcp/algo-forge-bridge/server.py"],
      "cwd": "."
    }
  }
}
```

Cursor sẽ tự kết nối MCP servers → có thể gọi tools trực tiếp từ chat.

### 14.3 Dùng Cursor Chat để build EA

Trong Cursor Chat (`Ctrl+L`), gõ:

```
Dùng vibecodekit-mql5-ea:
1. Chạy mql5-build --preset trend --stack netting --name RSITrend --output ./output trong terminal
2. Mở file output/RSITrend/RSITrend.mq5
3. Viết strategy: RSI(14) < 30 buy, > 70 sell, dùng CPipNormalizer và CRiskGuard
4. Chạy mql5-lint output/RSITrend/RSITrend.mq5
5. Fix mọi CRITICAL finding
```

### 14.4 Cursor Composer cho multi-file edit

Dùng Composer (`Ctrl+Shift+I`) để sửa nhiều file cùng lúc:

```
Tạo EA mới tên "MultiPairHedge":
1. Scaffold từ preset hedging-multi
2. Sửa EA file: thêm logic trade EURUSD + GBPUSD hedge
3. Sửa Include/CRiskGuard.mqh: thêm method MaxPairsCheck()
4. Lint toàn bộ files
```

### 14.5 Tips cho Cursor

- **@file:** Tag file cụ thể để Cursor đọc context: `@output/RSITrend/RSITrend.mq5`
- **@folder:** Tag folder: `@Include` để Cursor hiểu all MQL5 libraries
- **Terminal:** Chạy CLI tools trực tiếp trong integrated terminal
- **MCP:** Nếu cấu hình MCP, Cursor có thể gọi `syntax_check`, `compile` trực tiếp
- **Rules:** Tạo `.cursorrules` với nội dung tương tự `CLAUDE.md` ở mục 13.4

### 14.6 File `.cursorrules` gợi ý

Tạo file `.cursorrules` ở root:

```
Dự án MQL5 EA development. Khi viết code MQL5:
- Dùng CPipNormalizer cho pip calculation, KHÔNG hardcode _Point * N
- Dùng CRiskGuard cho risk management
- Dùng CTrade class, KHÔNG dùng raw OrderSend
- Dùng PrintFormat(), KHÔNG dùng Print() + string concat
- Max 6 input parameters, mỗi file ≤ 200 LOC
- Có CLI tools: mql5-build, mql5-lint, mql5-compile, mql5-permission
- Test suite: pytest tests/ -q → 152 passed, 2 skipped locally without Wine/MetaEditor
```

---

## 15. Terminal thuần (Manual)

### 15.1 Quick start (5 phút)

```bash
# 1. Clone + install
git clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
cd vibecodekit-mql5-ea
pip install -e ".[dev]"

# 2. Scaffold
mql5-build --preset stdlib --stack netting --name MyEA --output ./output/

# 3. (Edit strategy logic manually — nano/vim/code)
nano output/MyEA/MyEA.mq5

# 4. Lint
mql5-lint output/MyEA/MyEA.mq5

# 5. Pip check
mql5-pip-normalize output/MyEA/MyEA.mq5

# 6. Permission check
mql5-permission output/MyEA/MyEA.mq5 --mode PERSONAL
```

### 15.2 Full pipeline với backtest data

```bash
# 1-5: Scaffold + Code + Lint + Pip Check + Compile (xem trên)

# 6. Backtest
mql5-backtest report.xml --json

# 7. Walk-forward
mql5-walkforward is_report.xml oos_report.xml

# 8. Monte Carlo
mql5-monte-carlo report.xml --runs 10000

# 9. Multi-broker
mql5-multibroker fxpro.xml exness.xml icmarkets.xml

# 10. Trader-17 checklist
mql5-trader-check --ea output/MyEA/MyEA.mq5

# 11. Permission (final)
mql5-permission output/MyEA/MyEA.mq5 --mode ENTERPRISE
```

---

# Phần IV — Chức năng nâng cao

## 16. Review & Audit Tools

### 16.1 Multi-specialist Review (7 perspectives)

```bash
mql5-review --ea MyEA.mq5 --mode TEAM
```

7 specialists: architect, security, performance, accessibility, UX, DX, risk.

### 16.2 CSO Security Audit

```bash
mql5-cso --ea MyEA.mq5
```

OWASP Top 10 + STRIDE threat model + supply-chain audit.

### 16.3 Engineering Review

```bash
mql5-eng-review --ea MyEA.mq5
```

8 invariants: state machine, ASCII diagram, data flow, error boundaries.

### 16.4 CEO Review (4 modes)

```bash
mql5-ceo-review --ea MyEA.mq5
```

| Mode | Khi nào | Mục đích |
|------|--------|---------|
| `SCOPE_EXPANSION` | Thêm features mới | Review scope creep risk |
| `SELECTIVE` | Chọn features priority | Review resource allocation |
| `HOLD` | Freeze features | Review stability + tech debt |
| `REDUCTION` | Cut features | Review what to deprecate |

### 16.5 Root-cause Investigation

```bash
mql5-investigate --ea MyEA.mq5 --symptom "EA stops trading after 3 days"
```

---

## 17. ONNX & Machine Learning

### 17.1 Export model → ONNX

```bash
# Phát hiện framework tự động
mql5-onnx-export --model model.pt      # → pytorch
mql5-onnx-export --model model.h5      # → tensorflow
mql5-onnx-export --model model.pkl     # → sklearn

# Validate opset (MQL5 hỗ trợ opset 11-20)
mql5-onnx-export --validate-opset 17   # OK
mql5-onnx-export --validate-opset 5    # REJECTED
```

### 17.2 Embed ONNX vào EA

```bash
mql5-onnx-embed --onnx model.onnx --ea MyML_EA.mq5
# Output: #resource "\\Models\\model.onnx" as uchar ExtModel[]
```

### 17.3 COnnxLoader library

Trong EA code:
```cpp
#include "COnnxLoader.mqh"
COnnxLoader onnx;

int OnInit() {
    if(!onnx.LoadFromResource("Models\\model.onnx")) return INIT_FAILED;
    return INIT_SUCCEEDED;
}
```

---

## 18. LLM Bridge

3 variants để tích hợp AI vào EA development workflow:

### 18.1 Cloud API (OpenAI/Anthropic)

```bash
mql5-llm-context --variant cloud-api --prompt "Phân tích MACD+EMA crossover cho EURUSD H1"
```

### 18.2 Self-hosted (Ollama)

```bash
mql5-llm-context --variant self-hosted --host localhost:11434 --prompt "Review EA code"
```

### 18.3 Embedded ONNX

```bash
mql5-llm-context --variant embedded-onnx --model model.onnx --prompt "Classify market regime"
```

---

## 19. Algo Forge — Strategy iteration

### 19.1 Init workspace

```bash
mql5-forge-init --ea output/MyEA/MyEA.mq5 --workspace .forge/MyEA/
```

### 19.2 Evaluate & rank candidates

```bash
# Sau khi chạy backtests với various params
mql5-forge-pr --workspace .forge/MyEA/ --json
```

Output: ranked candidates với PF, Sharpe, DD, fitness scores.

---

## 20. MCP Server Integration

3 MCP servers (JSON-RPC 2.0 over stdin/stdout) cho IDE integration:

### 20.1 metaeditor-bridge

**Tools:** `compile`, `syntax_check`, `list_includes`

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp/metaeditor-bridge/server.py
```

### 20.2 mt5-bridge (10 tools — READ-ONLY)

**Tools:** `market_info`, `account_info`, `positions`, `history`, `tick_data`, `symbol_info`, `terminal_info`, `orders_total`, `positions_total`, `history_deals`

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp/mt5-bridge/server.py
```

> **READ-ONLY:** Không có order_send — tránh accidental trade mutation.

### 20.3 algo-forge-bridge (6 tools)

**Tools:** `init_workspace`, `evaluate`, `suggest_params`, `list_candidates`, `rank`, `export_best`

### 20.4 Cấu hình cho Claude Code / Cursor

Tạo file `.claude/mcp.json` hoặc `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "metaeditor-bridge": {
      "command": "python",
      "args": ["mcp/metaeditor-bridge/server.py"],
      "cwd": "/path/to/vibecodekit-mql5-ea"
    },
    "algo-forge-bridge": {
      "command": "python",
      "args": ["mcp/algo-forge-bridge/server.py"],
      "cwd": "/path/to/vibecodekit-mql5-ea"
    }
  }
}
```

---

## 21. Phase E — Polish & Ship

### 21.1 Scan & Doctor

```bash
mql5-scan        # Quét project → 32 .mq5, 7 .mqh, 79 .py, 17 scaffolds
mql5-doctor      # Health check → 18/18 checks pass
```

### 21.2 Audit & Canary

```bash
mql5-audit                                      # 50-point conformance audit
mql5-canary --terminal-log terminal.log --ea MyEA --duration 30  # Post-deploy monitoring
```

### 21.3 Ship & Refine

```bash
mql5-ship --version 1.0.0 --dry-run     # Preview release
mql5-ship --version 1.0.0               # Create git tag + push
mql5-refine --diff "$(git diff HEAD~1)" # Classify changes
```

### 21.4 Second Opinion & Install

```bash
mql5-second-opinion --ea MyEA.mq5 --focus risk    # Generate prompt cho AI review
mql5-install --target /other/project/ --dry-run    # Install overlay
```

---

# Phần V — Dev Team Workflow

## 22. Quy trình cho dev team

### 22.1 Workflow đề xuất

```
Developer                    CI / Pipeline                  Reviewer
    │                             │                             │
    ├── 1. mql5-build scaffold    │                             │
    ├── 2. Code strategy          │                             │
    ├── 3. mql5-lint → fix        │                             │
    ├── 4. mql5-permission TEAM   │                             │
    ├── 5. git push → PR          │                             │
    │                      ┌──────┤                             │
    │                      │ pytest tests/ -q                   │
    │                      │ mql5-audit                         │
    │                      │ mql5-permission ENTERPRISE         │
    │                      └──────┤                             │
    │                             ├── CI results ──────────────▶│
    │                             │                    mql5-review FULL
    │                             │                    mql5-cso (security)
    │                             │                    mql5-eng-review
    │◀───────────────── Review comments ───────────────────────┤
    ├── 6. Fix review items       │                             │
    ├── 7. git push               │                             │
    │                             ├── CI green ────────────────▶│
    │                             │                      Approve + merge
    ├── 8. mql5-ship --version    │                             │
    └──────────────────────────────┘                             │
```

### 22.2 CI configuration (`.github/workflows/ci.yml`)

```yaml
name: EA Quality Gate
on: [push, pull_request]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install
        run: pip install -e ".[dev]"

      - name: Tests
        run: pytest tests/ -q

      - name: Audit
        run: mql5-audit
```

### 22.3 Code review checklist cho team

Trước khi approve PR:

- [ ] `mql5-lint` → 0 CRITICAL findings
- [ ] `mql5-pip-normalize` → không hardcode pip
- [ ] `mql5-permission --mode TEAM` → all_pass = true
- [ ] `mql5-trader-check` → ≥15/17 PASS
- [ ] `pytest tests/ -q` → tất cả tests pass
- [ ] Mỗi file ≤ 200 LOC
- [ ] Max 6 input parameters
- [ ] Dùng CPipNormalizer, CRiskGuard, CMagicRegistry

---

## 23. Danh sách đầy đủ 45 CLI Commands

### Phase A — Core Foundation (4 tools)

| # | Command | Mô tả | Ví dụ |
|---|---------|--------|-------|
| 1 | `mql5-build` | Scaffold EA từ 17 preset | `mql5-build --preset trend --stack netting --name MyEA --output ./out` |
| 2 | `mql5-lint` | Kiểm tra 13 anti-pattern | `mql5-lint MyEA.mq5` |
| 3 | `mql5-compile` | Compile qua MetaEditor | `mql5-compile MyEA.mq5 --include ./Include/` |
| 4 | `mql5-pip-normalize` | Quét hardcoded pip | `mql5-pip-normalize MyEA.mq5` |

### Phase B — Test & Validation (10 tools)

| # | Command | Mô tả | Ví dụ |
|---|---------|--------|-------|
| 5 | `mql5-backtest` | Parse Strategy Tester XML | `mql5-backtest report.xml --json` |
| 6 | `mql5-walkforward` | Walk-forward IS/OOS | `mql5-walkforward is.xml oos.xml` |
| 7 | `mql5-monte-carlo` | Monte Carlo DD simulation | `mql5-monte-carlo report.xml --runs 10000` |
| 8 | `mql5-multibroker` | Multi-broker stability | `mql5-multibroker b1.xml b2.xml b3.xml` |
| 9 | `mql5-trader-check` | Trader-17 checklist | `mql5-trader-check --ea MyEA.mq5` |
| 10 | `mql5-overfit-check` | IS vs OOS overfit | `mql5-overfit-check is.xml oos.xml` |
| 11 | `mql5-fitness` | 5 fitness templates | `mql5-fitness --template profit_factor --report report.xml` |
| 12 | `mql5-mfe-mae` | MFE/MAE excursion | `mql5-mfe-mae report.xml` |
| 13 | `mql5-deploy-vps` | VPS deployment helper | `mql5-deploy-vps --ea MyEA.ex5` |
| 14 | `mql5-broker-safety` | Broker safety check | `mql5-broker-safety --ea MyEA.mq5` |

### Phase C — Methodology (11 tools)

| # | Command | Mô tả | Ví dụ |
|---|---------|--------|-------|
| 15 | `mql5-rri` | Reverse Requirements Interview workflow | `mql5-rri --mode TEAM` |
| 16 | `mql5-rri-bt` | RRI backtest questions + matrix summary | `mql5-rri-bt --personas all` |
| 17 | `mql5-rri-rr` | RRI risk-reward questions | `mql5-rri-rr --persona all` |
| 18 | `mql5-rri-chart` | RRI chart/indicator analysis | `mql5-rri-chart --persona all` |
| 19 | `mql5-matrix` | 8×8 quality matrix | `mql5-matrix --html matrix.html` |
| 20 | `mql5-permission` | 7-layer permission pipeline | `mql5-permission --ea MyEA.mq5 --mode TEAM` |
| 21 | `mql5-review` | 7-specialist review | `mql5-review --ea MyEA.mq5 --mode TEAM` |
| 22 | `mql5-eng-review` | Engineering invariants | `mql5-eng-review --ea MyEA.mq5` |
| 23 | `mql5-ceo-review` | CEO review (4 modes) | `mql5-ceo-review --ea MyEA.mq5` |
| 24 | `mql5-cso` | CSO security audit | `mql5-cso --ea MyEA.mq5` |
| 25 | `mql5-investigate` | Root-cause investigation | `mql5-investigate --ea MyEA.mq5 --symptom "..."` |

### Phase D — Tech 2024-2025 (8 tools)

| # | Command | Mô tả | Ví dụ |
|---|---------|--------|-------|
| 26 | `mql5-onnx-export` | ONNX export + validate | `mql5-onnx-export --model model.pt` |
| 27 | `mql5-onnx-embed` | ONNX embed directive | `mql5-onnx-embed --onnx model.onnx --ea MyEA.mq5` |
| 28 | `mql5-async-build` | HFT scaffold | `mql5-async-build --name HFTBot --output ./out` |
| 29 | `mql5-cloud-optimize` | Cloud cost gate | `mql5-cloud-optimize --ea MyEA.mq5 --mode TEAM --budget 30` |
| 30 | `mql5-method-hiding-check` | Method hiding detection | `mql5-method-hiding-check --ea MyEA.mq5` |
| 31 | `mql5-llm-context` | LLM bridge (3 variants) | `mql5-llm-context --variant cloud-api --prompt "..."` |
| 32 | `mql5-forge-init` | Algo Forge init | `mql5-forge-init --ea MyEA.mq5 --workspace .forge/` |
| 33 | `mql5-forge-pr` | Algo Forge evaluate | `mql5-forge-pr --workspace .forge/ --json` |

### Phase E — Polish & Ship (12 tools)

| # | Command | Mô tả | Ví dụ |
|---|---------|--------|-------|
| 34 | `mql5-scan` | Project scanner | `mql5-scan` |
| 35 | `mql5-vision` | Vision document | `mql5-vision --name MyEA --goal "..."` |
| 36 | `mql5-blueprint` | Blueprint generator | `mql5-blueprint --vision vision.md` |
| 37 | `mql5-tip` | Task Instruction Pack | `mql5-tip --blueprint blueprint.md` |
| 38 | `mql5-survey` | Preset survey | `mql5-survey` |
| 39 | `mql5-doctor` | Health check (18 items) | `mql5-doctor` |
| 40 | `mql5-audit` | 50-point conformance | `mql5-audit` |
| 41 | `mql5-canary` | Post-deploy monitor | `mql5-canary --terminal-log log.txt --ea MyEA --duration 30` |
| 42 | `mql5-ship` | Git tag + push | `mql5-ship --version 1.0.0 --dry-run` |
| 43 | `mql5-refine` | Diff classifier | `mql5-refine --diff changes.diff` |
| 44 | `mql5-install` | Overlay installer | `mql5-install --target /other/ --dry-run` |
| 45 | `mql5-second-opinion` | AI review prompt | `mql5-second-opinion --ea MyEA.mq5 --focus risk` |
---

## 24. Troubleshooting

### 24.1 Lỗi thường gặp

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| `mql5-build: command not found` | Chưa install package | `pip install -e ".[dev]"` |
| `Invalid preset 'xxx'` | Preset không tồn tại | `mql5-build --list` để xem danh sách |
| `Invalid stack 'xxx' for preset 'yyy'` | Stack không khớp preset | Xem `mql5-build --list` cho stacks của preset |
| `MetaEditor not found` | Chưa cài Wine/MetaEditor | Xem [mục 2.3](#23-cài-wine--metaeditor) |
| `AP-20 CRITICAL: Hardcoded pip` | Dùng `_Point * 10` | Thay bằng `pipNorm.Pips(N)` |
| `AP-01 CRITICAL: No stop-loss` | `trade.Buy()` thiếu SL | Thêm SL `!= 0` |
| `Permission L4 FAIL` | Trader checklist < 15/17 | Review 17 items |
| `Permission L6 FAIL` | Quality matrix avg < 40% | Thêm error handling, docs, risk |
| `ModuleNotFoundError` | Package chưa install | `pip install -e ".[dev]"` |
| `FileNotFoundError: Report not found` | File XML backtest không tồn tại | Kiểm tra path file report |
| `Error: IS report not found` | Walk-forward file IS không tồn tại | Kiểm tra path file IS report |

### 24.2 FAQ

**Q: Không có MetaTrader 5, dùng được tool không?**
A: Được. Chỉ bước 5 (Compile) và 6-9 (Backtest/WF/MC/Multibroker) cần MT5 data. Scaffold/lint/review/permission hoạt động độc lập.

**Q: EA nào nên bắt đầu cho người mới?**
A: Preset `stdlib` + stack `netting` → đơn giản nhất. Strategy EMA crossover là entry-level tốt.

**Q: Làm sao test EA trên demo account?**
A: Compile file `.mq5` → `.ex5` bằng MetaEditor, copy vào `MQL5/Experts/`, restart MT5, attach vào chart.

**Q: Tool hỗ trợ Windows không?**
A: CLI tools chạy trên mọi OS (Python). MetaEditor compile cần Wine trên Linux/Mac hoặc native Windows.

---

## 25. Tham khảo & Links

### Links chính

| Tài nguyên | URL |
|-----------|-----|
| GitHub repo | https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea |
| Preview site | https://vibecodekit-mql5-ea-preview-wpyifglq.devinapps.com |
| Devin AI | https://app.devin.ai |
| Codex CLI | https://github.com/openai/codex |
| Claude Code | https://github.com/anthropic-ai/claude-code |
| Cursor IDE | https://cursor.sh |

### Docs trong repo

| File | Nội dung |
|------|---------|
| `docs/GUIDE-BUILD-EA.md` | Hướng dẫn build EA (pipeline + AI tools) |
| `docs/GUIDE-NEW-SESSION.md` | Quick start trên new session |
| `docs/GUIDE-COMPLETE.md` | Tài liệu toàn diện (file này) |
| `docs/AUDIT-REVIEW.md` | Audit report |
| `docs/PLAN-v5.md` | Architecture plan |
| `docs/references/` | 28 reference docs |
| `docs/rri-personas/` | 6 RRI persona definitions |

### MQL5 Libraries trong `Include/`

| File | Class | Mô tả |
|------|-------|--------|
| `CPipNormalizer.mqh` | `CPipNormalizer` | Chuẩn hóa pip cho mọi symbol (4/5/3/2 digits) |
| `CRiskGuard.mqh` | `CRiskGuard` | Daily-loss limit + max positions + lot sizing |
| `CMagicRegistry.mqh` | `CMagicRegistry` | File-backed magic number collision detection |
| `CSpreadGuard.mqh` | `CSpreadGuard` | Spread monitoring + max spread filter |
| `CMfeMaeLogger.mqh` | `CMfeMaeLogger` | Maximum Favorable/Adverse Excursion logging |
| `COnnxLoader.mqh` | `COnnxLoader` | ONNX model loading + inference abstraction |
| `CAsyncTradeManager.mqh` | `CAsyncTradeManager` | Async order management + request tracking |

---

*Tài liệu thuộc dự án [vibecodekit-mql5-ea](https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea) v1.0.0*
*Cập nhật: 154 tests collected (152 pass, 2 local Wine/MetaEditor skips) · 45 CLI tools · 17 scaffold presets · 3 MCP servers*
