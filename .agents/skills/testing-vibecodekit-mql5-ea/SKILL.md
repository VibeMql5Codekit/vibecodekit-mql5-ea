---
name: testing-vibecodekit-mql5-ea
description: Test the vibecodekit-mql5-ea toolkit end-to-end. Use when verifying CLI tools, preview site, scaffold templates, RRI methodology commands, or bilingual i18n changes.
---

# Testing vibecodekit-mql5-ea

## Setup
```bash
cd /home/ubuntu/repos/vibecodekit-mql5-ea
pip install -e ".[dev]"
```

## Quick Smoke Test
```bash
pytest tests/ -q
# Expected locally: 163 passed, 2 skipped when Wine/MetaEditor smoke deps are unavailable
```

## CLI-Only Testing Evidence

For CLI/runtime changes, use shell commands and attach command output or a markdown report. Do not start a screen recording when all testing is shell-only because the recording will only show an idle desktop.

## RRI CLI End-to-End Test

Use this flow when verifying RRI/persona/matrix changes:

```bash
# Single-persona enterprise session: exact persona question count and workflow wiring
mql5-rri --mode ENTERPRISE --persona trader --json
# Expected: exit 0, mode ENTERPRISE, total_questions 25, one trader interview, workflow has 8 steps, step 2 is RRI/pending

# Team session across all six personas
mql5-rri --mode TEAM --json
# Expected: exit 0, 6 interviews, total_questions 72 (6 personas × 12 TEAM questions)

# Specialized RRI reviews
mql5-rri-bt --mode TEAM --personas all --json
# Expected: exit 0, matrix.total_cells 64, passed 56, warned 8, failed 0, gate_pass true

mql5-rri-rr --mode TEAM --persona all --json
# Expected: exit 0, 6 reviews, total_questions > 0

mql5-rri-chart --mode TEAM --persona all --json
# Expected: exit 0, 6 reviews, total_questions > 0

# Matrix output and HTML artifact
mql5-matrix --mode ENTERPRISE --html /home/ubuntu/matrix-e2e.html
# Expected: exit 0, stdout contains "Matrix: 64/64 PASS (threshold: 56, gate: PASS)", HTML file contains a <table>
```

## Runtime CLI Count Check

When README/docs claim the CLI count, verify against `pyproject.toml`:

```bash
python - <<'PY'
import tomllib
from pathlib import Path
scripts = tomllib.loads(Path('pyproject.toml').read_text())['project']['scripts']
print(len(scripts))
for name in ['mql5-rri', 'mql5-rri-bt', 'mql5-rri-rr', 'mql5-rri-chart', 'mql5-matrix']:
    print(name, scripts[name])
PY
# Expected: 45 total scripts; RRI/matrix names map to vibecodekit_mql5.rri.* modules
```

## Scaffold Deep Test (All 17 Presets)

When testing scaffold template changes, test ALL 22 preset×stack combos:

```bash
# List all presets and stacks
mql5-build --list

# Test each combo: scaffold + lint
for each preset/stack combo:
  mql5-build --preset <preset> --stack <stack> --name TestEA --output /tmp/test
  mql5-lint /tmp/test/TestEA/TestEA.mq5
```

### Key Checks per Scaffold
1. **AP-05 (input count)**: `grep -c "^input " file.mq5` must be ≤ 6
2. **EventSetTimer/EventKillTimer pairs**: If `OnTimer()` exists, both `EventSetTimer()` and `EventKillTimer()` must exist
3. **ArraySetAsSeries before CopyBuffer**: If `CopyBuffer`/`CopyClose` etc. used, `ArraySetAsSeries` must be called first
4. **Lint 0 criticals**: `mql5-lint` must show 0 critical (warnings are OK for scaffolds)

### Presets with Multiple Stacks
- `portfolio-basket`: hedging, netting
- `stdlib`: hedging, netting, python-bridge
- `service-llm-bridge`: cloud-api, embedded-onnx-llm, self-hosted-ollama

### Common AP-05 Fix Pattern
When a scaffold has >6 inputs, convert rarely-changed params to `const`:
```mql5
// Before (7 inputs — AP-05 critical)
input double InpDailyLoss = 5.0;

// After (const — not counted as optimizer input)
const double DailyLossLimit = 5.0;
```

## Lint Testing
```bash
# Real criticals (not false positives from grep)
grep "^\[X\]" lint.log | wc -l   # count real criticals
grep "^\[!\]" lint.log | wc -l   # count real warnings
# Do NOT use: grep -c "critical" — matches "0 critical" text!
```

## Preview Site Testing
- URL: https://vibecodekit-mql5-ea-preview-wpyifglq.devinapps.com
- Add `?nocache=<label>` to bust CDN cache after deploy
- Test VI/EN language toggle on all tabs
- Mobile viewport: test at 375×812 (iPhone) for overflow issues
- Check all nav buttons switch language (need class `i18n`)

## Permission Pipeline Testing
```bash
PYTHONPATH=scripts python -c "
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
import json
result = run_permission_pipeline('path/to/EA.mq5', 'PERSONAL')
print(json.dumps(result, indent=2))
"
```

## Devin Secrets Needed
No secrets required — all testing is local CLI + public preview site.
