# Hướng dẫn Build EA 100% với vibecodekit-mql5-ea

> Step-by-step guide — từ ý tưởng chiến lược → EA hoàn chỉnh đã qua kiểm định
> Hỗ trợ: **Devin AI** · **Codex CLI** · **Claude Code** · **Manual CLI**

---

## Mục lục

1. [Tổng quan pipeline](#1-tổng-quan-pipeline)
2. [Yêu cầu hệ thống](#2-yêu-cầu-hệ-thống)
3. [Cài đặt](#3-cài-đặt)
4. [Pipeline 10 bước build EA](#4-pipeline-10-bước-build-ea)
5. [Chạy trên Devin AI Session](#5-chạy-trên-devin-ai-session)
6. [Chạy với Codex CLI](#6-chạy-với-codex-cli)
7. [Chạy với Claude Code](#7-chạy-với-claude-code)
8. [Chạy Manual CLI](#8-chạy-manual-cli)
9. [Permission Pipeline & Quality Gate](#9-permission-pipeline--quality-gate)
10. [MCP Server Integration](#10-mcp-server-integration)
11. [Troubleshooting](#11-troubleshooting)
12. [Tham khảo](#12-tham-khảo)

---

## 1. Tổng quan pipeline

```
┌─────────┐    ┌──────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐
│ SCAFFOLD │───▶│ CODE │───▶│   LINT  │───▶│ COMPILE  │───▶│ BACKTEST │
│ (build)  │    │(edit)│    │(13 AP)  │    │(MetaEdit)│    │(XML parse)│
└─────────┘    └──────┘    └─────────┘    └──────────┘    └──────────┘
                                                               │
                ┌──────────┐    ┌──────────┐    ┌──────────┐   │
                │   SHIP   │◀───│PERMISSION│◀───│MULTIBRK  │◀──┘
                │(deploy)  │    │(7 layer) │    │(3 broker) │
                └──────────┘    └──────────┘    └──────────┘
```

**10 bước:**

| # | Bước | Tool | Mô tả |
|---|------|------|--------|
| 1 | **Scaffold** | `mql5-build` | Tạo EA skeleton từ 17 preset × 3 stack |
| 2 | **Code** | Editor / AI | Viết strategy logic (entry/exit/filters) |
| 3 | **Lint** | `mql5-lint` | Kiểm tra 13 anti-pattern (8 critical + 5 warning) |
| 4 | **Pip Check** | `mql5-pip-normalize` | Xác minh không hardcode pip value |
| 5 | **Compile** | `mql5-compile` | Compile qua MetaEditor (Wine trên Linux) |
| 6 | **Backtest** | `mql5-backtest` | Parse kết quả Strategy Tester XML |
| 7 | **Walk-forward** | Python script | IS/OOS split validation |
| 8 | **Monte Carlo** | Python script | DD95 simulation (10,000 runs) |
| 9 | **Multi-broker** | Python script | Stability gate (CV ≤ 0.30) |
| 10 | **Permission** | orchestrator.py | 7-layer quality gate → SHIP |

---

## 2. Yêu cầu hệ thống

### Bắt buộc
- **Python 3.10+** (tested: 3.12)
- **pip** hoặc **uv** package manager
- **Git**

### Tùy chọn (để compile + backtest thật)
- **Wine 8+** (Linux) hoặc **MetaTrader 5** (Windows)
- **MetaEditor 64-bit** (qua Wine hoặc native Windows)
- **MetaTrader 5 Python package** (`pip install MetaTrader5`, chỉ Windows)

### Cho AI-assisted development
- **Devin AI** account (https://app.devin.ai)
- **Codex CLI** (`npm install -g @openai/codex`)
- **Claude Code** (`npm install -g @anthropic-ai/claude-code`)

---

## 3. Cài đặt

### 3.1 Clone repo

```bash
git clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
cd vibecodekit-mql5-ea
```

### 3.2 Cài dependencies

```bash
# Tạo virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# Cài package
pip install -e ".[dev]"

# Hoặc dùng uv (nhanh hơn)
uv pip install -e ".[dev]"
```

### 3.3 Verify cài đặt

```bash
# Kiểm tra tools available
mql5-build --list
mql5-lint --help

# Chạy test suite
pytest tests/ -q
# Expected: 107 passed, 2 skipped
```

### 3.4 Cài Wine + MetaEditor (tùy chọn, cho compile thật)

```bash
# Ubuntu/Debian
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install -y wine64 wine32 xvfb

# Cài MetaEditor vào Wine prefix
export WINEPREFIX=~/.wine-mql5
wineboot --init
# Download MetaTrader 5 installer và chạy:
# wine mt5setup.exe
```

---

## 4. Pipeline 10 bước build EA

### Bước 1: Scaffold — Tạo EA skeleton

```bash
# Xem danh sách presets
mql5-build --list
```

Output:
```
  stdlib: netting, hedging, python-bridge
  wizard-composable: netting
  portfolio-basket: hedging, netting
  ml-onnx: python-bridge
  hft-async: netting
  trend: netting, hedging
  mean-reversion: netting
  breakout: netting
  grid: netting
  dca: netting
  scalping: netting
  ...
```

```bash
# Tạo EA mới
mql5-build --preset stdlib --stack netting --name TrendMaster --output ./my-ea/

# Output structure:
# my-ea/TrendMaster/
# ├── TrendMaster.mq5          ← Main EA file
# ├── CPipNormalizer.mqh        ← Pip normalization (auto-included)
# ├── CRiskGuard.mqh            ← Risk management (auto-included)
# └── CMagicRegistry.mqh        ← Magic number registry (auto-included)
```

**17 presets có sẵn:**

| Preset | Mô tả | Stack options |
|--------|--------|--------------|
| `stdlib` | Standard Library EA cơ bản | netting, hedging, python-bridge |
| `wizard-composable` | MQL5 Wizard (CExpert framework) | netting |
| `portfolio-basket` | Multi-symbol portfolio/basket | hedging, netting |
| `ml-onnx` | Machine learning với ONNX inference | python-bridge |
| `hft-async` | High-frequency async trading | netting |
| `trend` | Trend-following strategy | netting, hedging |
| `mean-reversion` | Mean-reversion strategy | netting |
| `breakout` | Breakout strategy | netting |
| `grid` | Grid trading | netting |
| `dca` | Dollar-cost averaging | netting |
| `scalping` | Scalping strategy | netting |
| `hedging-multi` | Multi-pair hedging | hedging |
| `news-trading` | News event trading | netting |
| `arbitrage-stat` | Statistical arbitrage | netting |
| `indicator-only` | Custom indicator (không phải EA) | — |
| `library` | MQL5 library module | — |
| `service-llm-bridge` | LLM bridge service | cloud-api, embedded-onnx-llm, self-hosted-ollama |

### Bước 2: Code — Viết strategy logic

Mở file `TrendMaster.mq5` và thay phần `// --- YOUR STRATEGY LOGIC HERE ---`:

```cpp
void OnTick()
{
    if(!riskGuard.CanOpenTrade()) return;

    // === YOUR STRATEGY LOGIC ===
    double maFast = iMA(_Symbol, PERIOD_H1, 20, 0, MODE_EMA, PRICE_CLOSE);
    double maSlow = iMA(_Symbol, PERIOD_H1, 50, 0, MODE_EMA, PRICE_CLOSE);

    double fastVal[], slowVal[];
    CopyBuffer(maFast, 0, 0, 2, fastVal);
    CopyBuffer(maSlow, 0, 0, 2, slowVal);

    bool buySignal  = fastVal[0] > slowVal[0] && fastVal[1] <= slowVal[1];
    bool sellSignal = fastVal[0] < slowVal[0] && fastVal[1] >= slowVal[1];
    // === END STRATEGY LOGIC ===

    if(buySignal)
    {
        double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
        double sl  = ask - pipNorm.Pips(InpSLPips);
        double tp  = ask + pipNorm.Pips(InpTPPips);
        double risk_money = AccountInfoDouble(ACCOUNT_BALANCE)
                            * InpRiskPercent / 100.0;
        double lots = pipNorm.LotForRisk(risk_money, InpSLPips);

        trade.Buy(lots, _Symbol, ask, sl, tp, "TrendMaster buy");
    }

    if(sellSignal)
    {
        double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double sl  = bid + pipNorm.Pips(InpSLPips);
        double tp  = bid - pipNorm.Pips(InpTPPips);
        double risk_money = AccountInfoDouble(ACCOUNT_BALANCE)
                            * InpRiskPercent / 100.0;
        double lots = pipNorm.LotForRisk(risk_money, InpSLPips);

        trade.Sell(lots, _Symbol, bid, sl, tp, "TrendMaster sell");
    }
}
```

### Bước 3: Lint — Kiểm tra anti-patterns

```bash
mql5-lint my-ea/TrendMaster/TrendMaster.mq5
```

**Expected output (clean EA):**
```
TrendMaster.mq5: PASS (0 findings)
```

**Nếu có lỗi:**
```
TrendMaster.mq5: FAIL
  Line 45: AP-01 CRITICAL — No stop-loss: trade.Buy() without SL parameter
  Line 62: AP-07 WARNING — Print() used instead of PrintFormat()
```

**13 anti-patterns được kiểm tra:**

| ID | Severity | Mô tả |
|----|----------|--------|
| AP-01 | CRITICAL | Không có stop-loss |
| AP-03 | CRITICAL | Fixed lot size (hardcoded) |
| AP-05 | CRITICAL | Quá nhiều input (>6 = overfitting) |
| AP-15 | CRITICAL | Raw OrderSend (không dùng CTrade) |
| AP-17 | CRITICAL | WebRequest trong OnTick |
| AP-18 | CRITICAL | OrderSendAsync không có OnTradeTransaction |
| AP-20 | CRITICAL | Hardcoded pip value |
| AP-21 | CRITICAL | JPY/XAU pip calculation sai |
| AP-02 | WARNING | Không có take-profit |
| AP-04 | WARNING | Không có trailing stop |
| AP-06 | WARNING | Không có error retry |
| AP-07 | WARNING | Print() thay vì PrintFormat() |
| AP-08 | WARNING | Không có comment trên trade |

### Bước 4: Pip Check — Xác minh broker-agnostic

```bash
mql5-pip-normalize my-ea/TrendMaster/TrendMaster.mq5
```

**Expected:** Không tìm thấy hardcoded pip value.

### Bước 5: Compile — MetaEditor compilation

```bash
# Compile (cần Wine + MetaEditor)
mql5-compile my-ea/TrendMaster/TrendMaster.mq5 --include ./Include/

# Nếu không có MetaEditor, dùng syntax check thay thế:
python -c "
import sys; sys.path.insert(0, 'mcp/metaeditor-bridge')
from tools import handle_syntax_check
r = handle_syntax_check({'file': 'my-ea/TrendMaster/TrendMaster.mq5'})
print(r)
"
```

### Bước 6: Backtest — Parse kết quả

Sau khi chạy Strategy Tester trong MetaTrader 5, export report XML:

```bash
mql5-backtest path/to/report.xml --json
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
  "win_rate": 53.4
}
```

### Bước 7: Walk-forward — IS/OOS validation

```bash
python -m vibecodekit_mql5.walkforward is_report.xml oos_report.xml
```

**PASS criteria:** OOS Profit Factor ≥ 1.5, PF efficiency ≥ 70%

### Bước 8: Monte Carlo — Drawdown simulation

```bash
python -m vibecodekit_mql5.monte_carlo report.xml --simulations 10000
```

**PASS criteria:** DD95/actual ≤ 1.5

### Bước 9: Multi-broker — Stability gate

```bash
python -m vibecodekit_mql5.multibroker broker1.xml broker2.xml broker3.xml
```

**PASS criteria:** PF coefficient of variation (CV) ≤ 0.30

### Bước 10: Permission Pipeline — Final quality gate

```bash
python -c "
import sys; sys.path.insert(0, 'scripts')
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
result = run_permission_pipeline('my-ea/TrendMaster/TrendMaster.mq5', mode='TEAM')
import json; print(json.dumps(result, indent=2))
"
```

**7 layers kiểm tra:**

| Layer | Tên | Kiểm tra |
|-------|-----|----------|
| L1 | source_lint | `#property strict`, copyright, file length, mixed tabs/spaces |
| L2 | compile | MetaEditor compile (skip nếu không cài Wine) |
| L3 | ap_lint | 13 anti-pattern (CRITICAL = block) |
| L4 | checklist | Trader-17 checklist (≥10/17 PASS) |
| L5 | methodology | Required libs (CPipNormalizer, CRiskGuard, CMagicRegistry) |
| L6 | quality_matrix | 8×8 matrix scoring (avg ≥ 40%) |
| L7 | broker_safety | Pip normalization, spread checks, margin modes |

**3 modes:**

| Mode | Layers | Khi nào dùng |
|------|--------|-------------|
| `PERSONAL` | L1, L2, L3, L4, L7 | EA cho bản thân |
| `TEAM` | L1, L2, L3, L4, L5, L7 | Chia sẻ trong team |
| `ENTERPRISE` | L1–L7 (tất cả) | Distribution / bán |

---

## 5. Chạy trên Devin AI Session

### 5.1 Tạo session mới

1. Vào https://app.devin.ai
2. Tạo session mới với prompt:

```
Clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git

Build EA mới tên "GoldScalper" cho XAU/USD M15 với strategy:
- Entry: RSI(14) < 30 (buy) hoặc > 70 (sell)
- SL: 200 pips, TP: 400 pips
- Risk: 1% per trade
- Max 2 positions

Quy trình:
1. mql5-build --preset scalping --stack netting --name GoldScalper
2. Viết strategy logic theo mô tả trên
3. mql5-lint GoldScalper.mq5 (fix tất cả CRITICAL)
4. mql5-pip-normalize GoldScalper.mq5
5. Chạy permission pipeline mode=PERSONAL
6. Push PR
```

### 5.2 Prompt template cho Devin

```markdown
## Build EA với vibecodekit-mql5-ea

**Repo:** https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git

**EA specs:**
- Tên: {EA_NAME}
- Symbol: {SYMBOL} (vd: EURUSD, XAUUSD)
- Timeframe: {TIMEFRAME} (vd: H1, M15)
- Strategy: {MÔ_TẢ_STRATEGY}
- Preset: {PRESET} (stdlib / trend / scalping / ml-onnx / ...)
- Stack: {STACK} (netting / hedging)

**Quy trình bắt buộc:**
1. `pip install -e ".[dev]"` trong thư mục repo
2. `mql5-build --preset {PRESET} --stack {STACK} --name {EA_NAME} --output ./output/`
3. Viết strategy logic vào file {EA_NAME}.mq5
4. `mql5-lint output/{EA_NAME}/{EA_NAME}.mq5` → fix ALL critical
5. `mql5-pip-normalize output/{EA_NAME}/{EA_NAME}.mq5` → verify no hardcoded pip
6. Chạy permission pipeline:
   ```python
   from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
   result = run_permission_pipeline('output/{EA_NAME}/{EA_NAME}.mq5', mode='PERSONAL')
   ```
7. `pytest tests/ -q` → verify tất cả tests pass
8. Push PR với kết quả lint + permission
```

### 5.3 Tips cho Devin session

- **Chia nhỏ:** Nếu EA phức tạp, chia thành 2 session (scaffold+code → test+ship)
- **Fixture test:** Yêu cầu Devin tạo test fixture `.mq5` để verify lint
- **Permission mode:** Dùng `PERSONAL` cho prototype, `TEAM` cho production

---

## 6. Chạy với Codex CLI

### 6.1 Cài Codex CLI

```bash
npm install -g @openai/codex
```

### 6.2 Setup workspace

```bash
git clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
cd vibecodekit-mql5-ea
pip install -e ".[dev]"
```

### 6.3 Scaffold + code EA

```bash
# Bước 1: Scaffold
mql5-build --preset trend --stack netting --name SwingTrader --output ./output/

# Bước 2: Dùng Codex để viết strategy
codex "
Trong file output/SwingTrader/SwingTrader.mq5, thay phần
'YOUR STRATEGY LOGIC HERE' bằng:
- Buy khi MACD histogram chuyển từ âm sang dương VÀ price trên EMA(50)
- Sell khi MACD histogram chuyển từ dương sang âm VÀ price dưới EMA(50)
- Giữ nguyên SL/TP/lot calculation đã có sẵn
- KHÔNG thay đổi OnInit, OnDeinit, includes
- KHÔNG dùng Print(), dùng PrintFormat()
"
```

### 6.4 Lint + fix

```bash
# Bước 3: Lint
mql5-lint output/SwingTrader/SwingTrader.mq5

# Nếu có lỗi, dùng Codex fix:
codex "
Fix lỗi lint trong output/SwingTrader/SwingTrader.mq5:
$(mql5-lint output/SwingTrader/SwingTrader.mq5 2>&1)

Quy tắc:
- AP-01: Mọi trade.Buy()/Sell() phải có SL != 0
- AP-03: Dùng pipNorm.LotForRisk(), KHÔNG hardcode lot
- AP-07: Dùng PrintFormat() thay Print() + string concat
- AP-15: Dùng trade.Buy()/Sell(), KHÔNG dùng OrderSend()
- AP-20: Dùng pipNorm.Pips(), KHÔNG nhân _Point * 10
"
```

### 6.5 Permission check

```bash
# Bước 4: Permission pipeline
python -c "
import sys; sys.path.insert(0, 'scripts')
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
import json
r = run_permission_pipeline('output/SwingTrader/SwingTrader.mq5', mode='PERSONAL')
print(json.dumps(r, indent=2))
"
```

### 6.6 Full Codex workflow (1 command)

```bash
codex "
Tôi muốn build EA tên MACDTrend cho EURUSD H1:
1. cd vibecodekit-mql5-ea && pip install -e '.[dev]'
2. mql5-build --preset trend --stack netting --name MACDTrend --output ./output/
3. Viết MACD crossover strategy vào MACDTrend.mq5
4. mql5-lint output/MACDTrend/MACDTrend.mq5 → fix nếu có lỗi
5. Chạy permission pipeline mode=PERSONAL
6. Report kết quả
"
```

---

## 7. Chạy với Claude Code

### 7.1 Cài Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

### 7.2 Setup project

```bash
git clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
cd vibecodekit-mql5-ea
pip install -e ".[dev]"
```

### 7.3 Interactive build

```bash
claude-code
```

Trong Claude Code session:

```
> Tôi muốn build EA mới. Hãy:
> 1. Chạy `mql5-build --list` để xem presets
> 2. Tôi chọn preset "stdlib", stack "netting", tên "BollingerEA"
> 3. Scaffold: `mql5-build --preset stdlib --stack netting --name BollingerEA --output ./output/`
> 4. Viết strategy: Bollinger Bands (20,2) — buy khi price chạm lower band, sell khi chạm upper
> 5. Lint: `mql5-lint output/BollingerEA/BollingerEA.mq5`
> 6. Permission: chạy orchestrator mode=PERSONAL
> 7. Report all results
```

### 7.4 Claude Code với CLAUDE.md project context

Tạo file `CLAUDE.md` trong thư mục project:

```markdown
# Project: vibecodekit-mql5-ea

## Available CLI tools
- `mql5-build --preset <preset> --stack <stack> --name <name> --output <dir>`
- `mql5-lint <file.mq5>` — 13 anti-pattern check
- `mql5-pip-normalize <file.mq5>` — pip hardcode check
- `mql5-compile <file.mq5> --include ./Include/` — MetaEditor compile

## Build workflow
1. Scaffold → 2. Code → 3. Lint → 4. Permission → 5. Ship

## Rules
- PHẢI dùng CPipNormalizer cho mọi pip calculation
- PHẢI dùng CRiskGuard cho risk management
- PHẢI dùng CMagicRegistry cho magic numbers
- KHÔNG dùng Print() + string concat → dùng PrintFormat()
- KHÔNG dùng raw OrderSend → dùng CTrade
- KHÔNG hardcode lot size → dùng pipNorm.LotForRisk()
- Max 6 input parameters (anti-overfit)
- Mỗi file ≤ 200 LOC
```

### 7.5 Batch processing với Claude Code

```bash
# Build nhiều EA cùng lúc
claude-code --print "
Build 3 EA variants cho EURUSD H1:
1. TrendEA (preset=trend, strategy=EMA crossover 20/50)
2. ScalpEA (preset=scalping, strategy=RSI 14 oversold/overbought)
3. GridEA (preset=grid, strategy=fixed grid 50 pips)

Cho mỗi EA:
- mql5-build scaffold
- Viết strategy logic
- mql5-lint verify
- Permission pipeline mode=PERSONAL
- Report kết quả từng EA
"
```

---

## 8. Chạy Manual CLI

### 8.1 Quick start (5 phút)

```bash
# 1. Clone + install
git clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
cd vibecodekit-mql5-ea
pip install -e ".[dev]"

# 2. Scaffold
mql5-build --preset stdlib --stack netting --name MyEA --output ./output/

# 3. (Edit strategy logic manually)

# 4. Lint
mql5-lint output/MyEA/MyEA.mq5

# 5. Permission check
python -c "
import sys; sys.path.insert(0, 'scripts')
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
import json
r = run_permission_pipeline('output/MyEA/MyEA.mq5', mode='PERSONAL')
print(json.dumps(r, indent=2))
print('VERDICT:', 'PASS' if r['all_pass'] else 'FAIL')
"
```

### 8.2 Full pipeline với backtest

```bash
# 1-4: Scaffold + Code + Lint + Pip Check (xem trên)

# 5. Compile (cần Wine + MetaEditor)
mql5-compile output/MyEA/MyEA.mq5 --include ./Include/

# 6. Backtest (sau khi chạy Strategy Tester)
python -m vibecodekit_mql5.backtest report.xml --json > results/backtest.json

# 7. Walk-forward
python -m vibecodekit_mql5.walkforward is.xml oos.xml

# 8. Monte Carlo
python -m vibecodekit_mql5.monte_carlo report.xml --simulations 10000

# 9. Multi-broker (chạy trên 3 broker khác nhau)
python -m vibecodekit_mql5.multibroker fxpro.xml exness.xml icmarkets.xml

# 10. Trader-17 checklist
python -m vibecodekit_mql5.trader_check --ea output/MyEA/MyEA.mq5

# 11. Permission pipeline (final gate)
python -c "
import sys; sys.path.insert(0, 'scripts')
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
import json
r = run_permission_pipeline('output/MyEA/MyEA.mq5', mode='ENTERPRISE')
print(json.dumps(r, indent=2))
"
```

### 8.3 Algo Forge — Automated strategy iteration

```bash
# Initialize forge workspace
python -m vibecodekit_mql5.forge_init \
  --ea output/MyEA/MyEA.mq5 \
  --workspace .forge/MyEA/

# (Chạy backtests với different params, save kết quả vào .forge/MyEA/results/)

# Evaluate and rank candidates
python -m vibecodekit_mql5.forge_pr \
  --workspace .forge/MyEA/ \
  --json
```

### 8.4 LLM Bridge — AI-assisted analysis

```bash
# Cloud API (cần OPENAI_API_KEY)
export OPENAI_API_KEY=sk-...
python -m vibecodekit_mql5.llm_context \
  --variant cloud-api \
  --api-key "$OPENAI_API_KEY" \
  --prompt "Phân tích strategy MACD+EMA crossover cho EURUSD H1, điểm mạnh/yếu?"

# Self-hosted Ollama (cần Ollama đang chạy)
python -m vibecodekit_mql5.llm_context \
  --variant self-hosted \
  --host localhost:11434 \
  --prompt "Review EA code cho potential issues"

# Embedded ONNX (cần model file)
python -m vibecodekit_mql5.llm_context \
  --variant embedded-onnx \
  --model path/to/model.onnx \
  --prompt "Classify market regime"
```

---

## 9. Permission Pipeline & Quality Gate

### 9.1 Cách hoạt động

Permission pipeline chạy **tuần tự** — fail ở layer nào thì dừng ngay (fail-fast).

```
EA.mq5 → L1(source) → L2(compile) → L3(AP) → L4(checklist) → L5(method) → L6(matrix) → L7(broker)
                                                                                            ↓
                                                                                     PASS → SHIP
```

### 9.2 Quality Matrix (Layer 6) — 8×8 = 64 cells

```
              error_handling  resource_mgmt  input_valid  code_struct  docs  config  broker  risk
reliability        ✓              ✓                                                          ✓
performance                       ✓                         ✓
security                                        ✓                                            ✓
maintainability                                              ✓          ✓
testability                                                                    ✓
portability                                                                    ✓      ✓
usability                                                                ✓
compliance                                       ✓                                    ✓      ✓
```

**Scoring:** Mỗi cell kiểm tra regex pattern trong EA code. Weight = 0.5 hoặc 1.0.
**PASS criteria:** Average ≥ 40% VÀ mỗi dimension ≥ 20%.

### 9.3 Ví dụ output

```json
{
  "mode": "ENTERPRISE",
  "layers_run": 7,
  "all_pass": true,
  "results": {
    "L1": {"pass": true, "details": "OK"},
    "L2": {"pass": true, "details": "MetaEditor not installed — skipped"},
    "L3": {"pass": true, "details": "0 critical, 2 warnings"},
    "L4": {"pass": true, "details": "14/17 PASS"},
    "L5": {"pass": true, "details": "OK"},
    "L6": {"pass": true, "scores": {"reliability": 100, "performance": 50, ...}, "average": 68},
    "L7": {"pass": true, "details": "OK"}
  }
}
```

---

## 10. MCP Server Integration

3 MCP servers cho IDE/AI integration (JSON-RPC 2.0 over stdin/stdout):

### 10.1 metaeditor-bridge

```bash
# List tools
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp/metaeditor-bridge/server.py

# Syntax check
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"syntax_check","arguments":{"file":"output/MyEA/MyEA.mq5"}}}' | python mcp/metaeditor-bridge/server.py

# List includes
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"list_includes","arguments":{"file":"output/MyEA/MyEA.mq5"}}}' | python mcp/metaeditor-bridge/server.py
```

**Tools:** `compile`, `syntax_check`, `list_includes`

### 10.2 mt5-bridge (READ-ONLY)

```bash
# Get market info (cần MetaTrader5 Python package)
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"market_info","arguments":{"symbol":"EURUSD"}}}' | python mcp/mt5-bridge/server.py
```

**Tools:** `market_info`, `account_info`, `positions`, `history`

> ⚠️ **READ-ONLY:** mt5-bridge KHÔNG có order_send, order_close, position_modify — intentionally để tránh accidental trade mutation.

### 10.3 algo-forge-bridge

```bash
# Init workspace
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"init_workspace","arguments":{"ea_path":"output/MyEA/MyEA.mq5","workspace":".forge/MyEA"}}}' | python mcp/algo-forge-bridge/server.py
```

**Tools:** `init_workspace`, `evaluate`, `suggest_params`

### 10.4 Cấu hình MCP trong Claude Code / Cursor

Thêm vào `.claude/mcp.json` hoặc `.cursor/mcp.json`:

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

## 11. Troubleshooting

### Lỗi thường gặp

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| `mql5-build: command not found` | Chưa install package | `pip install -e ".[dev]"` |
| `MetaEditor not found` | Chưa cài Wine/MetaEditor | Xem [mục 3.4](#34-cài-wine--metaeditor-tùy-chọn-cho-compile-thật) |
| `AP-20 CRITICAL: Hardcoded pip` | Dùng `_Point * 10` | Thay bằng `pipNorm.Pips(N)` |
| `AP-01 CRITICAL: No stop-loss` | `trade.Buy()` thiếu SL | Thêm SL parameter `!= 0` |
| `Permission L6 FAIL: avg < 40%` | EA thiếu nhiều best practices | Thêm error handling, documentation, risk control |
| `Permission L4 FAIL: <10/17` | Trader checklist thiếu | Review 17 items trong `docs/references/59-trader-checklist.md` |
| `ModuleNotFoundError` | PYTHONPATH chưa set | `export PYTHONPATH=scripts` hoặc `pip install -e .` |

### Lint false positives

- **AP-05 trên scaffolds:** Scaffolds có > 6 inputs là expected (template placeholder)
- **AP-20 trong Include/:** Doc comments chứa `_Point` text không phải code

---

## 12. Tham khảo

### Reference docs (28 files trong `docs/references/`)

| File | Chủ đề |
|------|--------|
| `50-survey.md` | Platform overview |
| `54-stl-cheatsheet.md` | Standard Library cheat sheet |
| `59-trader-checklist.md` | 17-point pre-deploy checklist |
| `60-wizard-cexpert.md` | MQL5 Wizard framework |
| `65-multi-broker.md` | Multi-broker testing |
| `70-algo-forge.md` | Algo Forge methodology |
| `71-onnx-mql5.md` | ONNX in MQL5 |
| `76-llm-patterns.md` | LLM integration patterns |
| `77-async-hft.md` | Async/HFT patterns |
| `79-pip-norm.md` | CPipNormalizer reference |

### Worked example

Xem `examples/ea-wizard-macd-sar-eurusd-h1-portfolio/` cho ví dụ hoàn chỉnh:
- `EAName.mq5` — Source code
- `results/backtest-summary.json` — Backtest metrics
- `results/walkforward.json` — Walk-forward results
- `results/monte-carlo.json` — Monte Carlo simulation
- `results/multibroker.json` — Multi-broker stability

### RRI Personas (6 files trong `docs/rri-personas/`)

| Persona | Focus |
|---------|-------|
| `trader.yaml` | Risk, drawdown, profitability |
| `risk-auditor.yaml` | Anti-patterns, compliance |
| `broker-engineer.yaml` | Broker compatibility, digits |
| `strategy-architect.yaml` | Strategy design, optimization |
| `devops.yaml` | CI/CD, deployment |
| `perf-analyst.yaml` | Performance metrics, statistics |

---

## Checklist tổng kết

Trước khi ship EA, verify:

- [ ] `mql5-lint` → 0 CRITICAL findings
- [ ] `mql5-pip-normalize` → không hardcode pip
- [ ] Permission pipeline → `all_pass: true`
- [ ] `pytest tests/ -q` → tất cả tests pass
- [ ] Walk-forward OOS PF ≥ 1.5 (nếu có backtest data)
- [ ] Monte Carlo DD95 ≤ 1.5× actual DD (nếu có)
- [ ] Multi-broker CV ≤ 0.30 (nếu test 3+ brokers)
- [ ] Trader-17 ≥ 10/17 PASS
- [ ] Mỗi file ≤ 200 LOC
- [ ] Max 6 input parameters

---

*Tài liệu này thuộc dự án [vibecodekit-mql5-ea](https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea) v1.0.0*
