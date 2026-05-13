# Hướng dẫn Demo & Test Tool trên New Devin Session

> Dành cho người dùng muốn **nhanh chóng test/demo** vibecodekit-mql5-ea trên một Devin session mới
> hoặc dùng CLI tools (Codex, Claude Code) để build EA project.

---

## Mục lục

1. [Quick Start trên Devin (5 phút)](#1-quick-start-trên-devin-5-phút)
2. [Demo: Build EA từ 0 → Production-ready](#2-demo-build-ea-từ-0--production-ready)
3. [Test Tool trên Codex CLI](#3-test-tool-trên-codex-cli)
4. [Test Tool trên Claude Code](#4-test-tool-trên-claude-code)
5. [Checklist xác nhận tool hoạt động](#5-checklist-xác-nhận-tool-hoạt-động)
6. [Tham khảo prompt templates](#6-tham-khảo-prompt-templates)

---

## 1. Quick Start trên Devin (5 phút)

### Bước 1: Tạo session mới

Vào [app.devin.ai](https://app.devin.ai) → New Session → paste prompt:

```
Clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
và chạy test suite để xác nhận tool hoạt động:

1. cd vibecodekit-mql5-ea
2. pip install -e ".[dev]"
3. pytest tests/ -q
4. mql5-build --list
5. Báo kết quả
```

**Expected output:**
```
150 passed
17 presets available
```

### Bước 2: Test scaffold generator

Paste tiếp vào session:

```
Chạy lần lượt các lệnh sau và báo kết quả:

1. mql5-build --preset stdlib --stack netting --name DemoEA --output /tmp/demo
2. mql5-lint /tmp/demo/DemoEA/DemoEA.mq5
3. cat /tmp/demo/DemoEA/DemoEA.mq5 | head -30
```

**Expected:**
- Scaffold tạo thành công, file chứa `DemoEA` thay vì `EAName`
- Lint pass (0 critical trên clean scaffold)

### Bước 3: Test permission pipeline

```
PYTHONPATH=scripts python -c "
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
result = run_permission_pipeline('/tmp/demo/DemoEA/DemoEA.mq5', 'PERSONAL')
import json; print(json.dumps(result, indent=2))
"
```

**Expected:** JSON output với `L1`→`L7` results, `all_pass` = true hoặc false tùy scaffold.

---

## 2. Demo: Build EA từ 0 → Production-ready

### 2.1 Prompt cho Devin session (full pipeline)

Tạo session mới, paste prompt sau:

```
Tôi muốn build một Trend Following EA cho EURUSD H1.

Dùng vibecodekit-mql5-ea tool:
1. Clone repo: https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
2. pip install -e ".[dev]"
3. mql5-build --preset trend --stack netting --name TrendFollowerEA --output ./output
4. Mở file output/TrendFollowerEA/TrendFollowerEA.mq5 và thêm strategy logic:
   - Entry: EMA 20 cross EMA 50
   - SL: 30 pips (dùng CPipNormalizer)
   - TP: 60 pips
   - Risk: 1% per trade (dùng CRiskGuard)
5. mql5-lint output/TrendFollowerEA/TrendFollowerEA.mq5
6. Chạy permission pipeline mode PERSONAL
7. Fix bất kỳ CRITICAL nào lint báo
8. Báo kết quả cuối cùng
```

### 2.2 Prompt cho Devin session (với backtest data)

```
Dùng vibecodekit-mql5-ea tool:
1. Clone repo + install
2. Analyze worked example:
   python -c "
   import json
   data = json.load(open('examples/ea-wizard-macd-sar-eurusd-h1-portfolio/results/backtest-summary.json'))
   print(f'PF: {data[\"profit_factor\"]}, DD: {data[\"maximal_drawdown_pct\"]}%, Trades: {data[\"total_trades\"]}')
   "
3. Chạy Monte Carlo simulation trên worked example
4. Chạy walk-forward analysis (dùng fixture IS/OOS reports)
5. Chạy permission pipeline ENTERPRISE mode trên worked example EA
6. Tổng hợp kết quả dạng bảng
```

### 2.3 Prompt cho Devin session (scaffold tất cả presets)

```
Dùng vibecodekit-mql5-ea:
1. Clone repo + install
2. Scaffold tất cả 17 presets, mỗi preset dùng stack đầu tiên available:
   mql5-build --list  (để xem presets + stacks)
   Rồi loop: mql5-build --preset <name> --stack <first-stack> --name Test<Name> --output /tmp/all-scaffolds
3. Lint tất cả scaffolded EAs
4. Báo bảng tổng hợp: preset | stack | lint_result | critical_count
```

---

## 3. Test Tool trên Codex CLI

### 3.1 Setup

```bash
# Cài Codex CLI
npm install -g @openai/codex

# Clone repo
git clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
cd vibecodekit-mql5-ea
pip install -e ".[dev]"
```

### 3.2 Chạy test suite

```bash
codex "Chạy pytest tests/ -q và báo kết quả. Nếu fail thì giải thích tại sao."
```

### 3.3 Build EA

```bash
codex "Dùng mql5-build để tạo scalping EA:
  mql5-build --preset scalping --stack hedging --name ScalpEA --output ./output
Rồi lint file output:
  mql5-lint output/ScalpEA/ScalpEA.mq5
Báo kết quả lint."
```

### 3.4 Full pipeline

```bash
codex "Đọc file docs/GUIDE-BUILD-EA.md section 8 (Manual CLI) và chạy
tất cả lệnh trong đó. Báo kết quả từng bước."
```

---

## 4. Test Tool trên Claude Code

### 4.1 Setup

```bash
# Cài Claude Code
npm install -g @anthropic-ai/claude-code

# Clone repo
git clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
cd vibecodekit-mql5-ea
pip install -e ".[dev]"
```

### 4.2 Interactive mode

```bash
claude

# Trong interactive session:
> Chạy test suite: pytest tests/ -q
> Scaffold EA: mql5-build --preset stdlib --name TestEA --output /tmp/test
> Lint: mql5-lint /tmp/test/TestEA/TestEA.mq5
> Permission pipeline: PYTHONPATH=scripts python -c "from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline; import json; print(json.dumps(run_permission_pipeline('/tmp/test/TestEA/TestEA.mq5', 'TEAM'), indent=2))"
```

### 4.3 Batch mode

```bash
claude -p "Clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git,
install với pip install -e '.[dev]',
chạy mql5-build --list để liệt kê presets,
scaffold preset 'ml-onnx' stack 'python-bridge' name 'MLTrader',
lint kết quả,
chạy permission pipeline ENTERPRISE mode,
báo summary."
```

### 4.4 Tạo CLAUDE.md cho project

Nếu muốn Claude Code tự hiểu project, tạo file `CLAUDE.md` ở root:

```bash
cat > CLAUDE.md << 'EOF'
# vibecodekit-mql5-ea

## Quick Start
```
pip install -e ".[dev]"
pytest tests/ -q
```

## CLI Tools
- `mql5-build --preset <name> --stack <stack> --name <ea> --output <dir>`
- `mql5-lint <path>`
- `mql5-compile <path>`
- `mql5-backtest <report.xml>`
- `mql5-trader-check --ea <path>`

## Test
```
PYTHONPATH=scripts pytest tests/ -q
```

## Permission Pipeline
```python
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
result = run_permission_pipeline("path/to/ea.mq5", "TEAM")
```

## Scaffolds
17 presets: stdlib, trend, scalping, ml-onnx, wizard-composable, portfolio-basket,
grid, dca, mean-reversion, breakout, hedging-multi, hft-async, arbitrage-stat,
news-trading, indicator-only, library, service-llm-bridge
EOF
```

---

## 5. Checklist xác nhận tool hoạt động

Chạy các lệnh sau trên bất kỳ environment nào (Devin, Codex, Claude Code, local):

```bash
# 1. Install
git clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
cd vibecodekit-mql5-ea
pip install -e ".[dev]"

# 2. Test suite
PYTHONPATH=scripts pytest tests/ -q
# ✓ Expected: 150 passed

# 3. List presets
mql5-build --list
# ✓ Expected: 17 presets listed

# 4. Scaffold
mql5-build --preset stdlib --stack netting --name CheckEA --output /tmp/check
# ✓ Expected: "Rendered stdlib/netting -> /tmp/check/CheckEA"

# 5. Lint
mql5-lint /tmp/check/CheckEA/CheckEA.mq5
# ✓ Expected: 0 critical (may have warnings)

# 6. Permission (PERSONAL mode)
PYTHONPATH=scripts python -c "
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
import json
r = run_permission_pipeline('/tmp/check/CheckEA/CheckEA.mq5', 'PERSONAL')
print(json.dumps(r, indent=2))
"
# ✓ Expected: JSON with layer results

# 7. Trader-17 checklist
PYTHONPATH=scripts python -m vibecodekit_mql5.trader_check --ea /tmp/check/CheckEA/CheckEA.mq5
# ✓ Expected: 17-item checklist with PASS/WARN/N-A

# 8. Worked example analysis
python -c "
import json
data = json.load(open('examples/ea-wizard-macd-sar-eurusd-h1-portfolio/results/backtest-summary.json'))
print(f'EA: {data[\"ea_name\"]}')
print(f'PF: {data[\"profit_factor\"]} | Sharpe: {data[\"sharpe_ratio\"]}')
print(f'DD: {data[\"maximal_drawdown_pct\"]}% | Trades: {data[\"total_trades\"]}')
"
# ✓ Expected: PF=1.52, Sharpe=1.34, DD=10.23%, Trades=728
```

**Tất cả 8 bước pass = tool hoạt động 100%.**

---

## 6. Tham khảo prompt templates

### 6.1 Template: Build EA cơ bản (cho Devin)

```
Repo: https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea

Yêu cầu:
1. Clone repo + pip install -e ".[dev]"
2. mql5-build --preset {PRESET} --stack {STACK} --name {EA_NAME} --output ./output
3. Sửa file output/{EA_NAME}/{EA_NAME}.mq5:
   - Entry logic: {MÔ TẢ ENTRY}
   - Exit logic: {MÔ TẢ EXIT}
   - SL: {SL_PIPS} pips (dùng CPipNormalizer)
   - TP: {TP_PIPS} pips
   - Risk: {RISK_PCT}% per trade (dùng CRiskGuard)
4. mql5-lint output/{EA_NAME}/{EA_NAME}.mq5
5. Fix mọi CRITICAL findings
6. Chạy permission pipeline mode PERSONAL
7. Báo kết quả
```

Thay `{...}` bằng giá trị thực tế. Ví dụ:
- `{PRESET}` = `trend`
- `{STACK}` = `netting`
- `{EA_NAME}` = `EmaScalper`
- `{MÔ TẢ ENTRY}` = `EMA 9 cross EMA 21`
- `{SL_PIPS}` = `20`
- `{TP_PIPS}` = `40`
- `{RISK_PCT}` = `1`

### 6.2 Template: Audit EA có sẵn (cho Codex/Claude Code)

```bash
codex "Dùng vibecodekit-mql5-ea tool:
1. pip install -e '.[dev]' (từ repo vibecodekit-mql5-ea)
2. mql5-lint {PATH_TO_EA}
3. PYTHONPATH=scripts python -m vibecodekit_mql5.trader_check --ea {PATH_TO_EA}
4. Chạy permission pipeline ENTERPRISE mode
5. Tổng hợp: bao nhiêu critical, bao nhiêu warning, trader-check score, permission pass/fail
6. Đề xuất fix cho mỗi issue tìm thấy"
```

### 6.3 Template: So sánh multi-broker

```
Dùng vibecodekit-mql5-ea:
1. Clone + install
2. Xem worked example multi-broker results:
   cat examples/ea-wizard-macd-sar-eurusd-h1-portfolio/results/multibroker.json
3. Giải thích ý nghĩa CV, stdev, DD range
4. Với CV = {VALUE}, EA đủ stable cho production không? Tại sao?
```

### 6.4 Template: Full pipeline với MCP servers

```
Dùng vibecodekit-mql5-ea:
1. Clone + install
2. Test MCP server metaeditor-bridge:
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp/metaeditor-bridge/server.py
3. Test MCP server algo-forge-bridge:
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp/algo-forge-bridge/server.py
4. Scaffold EA + init forge workspace:
   echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"init_workspace","arguments":{"ea_path":"output/MyEA/MyEA.mq5"}}}' | python mcp/algo-forge-bridge/server.py
5. Báo tools available từ mỗi server
```

---

## Lưu ý quan trọng

1. **Wine/MetaEditor không bắt buộc** — Tool vẫn hoạt động đầy đủ trên Linux/Mac mà không cần compile. Bước compile sẽ auto-skip nếu không tìm thấy MetaEditor.

2. **17 presets có sẵn** — Dùng `mql5-build --list` để xem danh sách đầy đủ. Mỗi preset phù hợp với loại strategy khác nhau:
   - `stdlib` — EA cơ bản, đa năng
   - `trend` — Trend following (EMA, MACD)
   - `scalping` — Scalping (hedging account)
   - `ml-onnx` — Machine learning với ONNX
   - `hft-async` — High-frequency, async execution
   - `grid` / `dca` — Grid/DCA strategies
   - `wizard-composable` — MQL5 Wizard framework

3. **Permission modes:**
   - `PERSONAL` — L1,2,3,4,7 (cho cá nhân, 5 layers)
   - `TEAM` — L1,2,3,4,5,7 (cho team, 6 layers)
   - `ENTERPRISE` — L1,2,3,4,5,6,7 (đầy đủ 7 layers + quality matrix)

---

*Tài liệu này thuộc dự án [vibecodekit-mql5-ea](https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea) v1.0.0*
