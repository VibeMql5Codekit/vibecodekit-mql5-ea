---
name: testing-vibecodekit-mql5-ea
description: Test the vibecodekit-mql5-ea toolkit end-to-end. Use when verifying CLI tools, preview site, scaffold templates, or bilingual i18n changes.
---

# Testing vibecodekit-mql5-ea

## Setup
```bash
cd /home/ubuntu/repos/vibecodekit-mql5-ea
pip install -e ".[dev]"
```

## Quick Smoke Test
```bash
pytest tests/ -q  # expect 150 passed
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
