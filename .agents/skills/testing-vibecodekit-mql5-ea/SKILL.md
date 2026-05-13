---
name: testing-vibecodekit-mql5-ea
description: Test the vibecodekit-mql5-ea toolkit end-to-end. Use when verifying CLI tools, preview site, or bilingual i18n changes.
---

# Testing vibecodekit-mql5-ea

## Quick Start

```bash
cd /home/ubuntu/repos/vibecodekit-mql5-ea
pip install -e ".[dev]"
pytest tests/ -q  # Expected: 148 passed, 2 skipped
```

## CLI Tool Testing

### Scaffold Generator
```bash
mql5-build --list                    # 17 presets
mql5-build --preset stdlib --stack netting --name TestEA --output /tmp/test-ea
mql5-build --preset scalping --stack hedging --name ScalpEA --output /tmp/test-ea
mql5-build --preset dca --stack hedging --name DcaEA --output /tmp/test-ea  # dca only has hedging
```

**Adversarial tests:**
- `--preset nonexistent` → should list valid presets
- `--preset dca` (default netting) → should say "Available: hedging"
- `--preset stdlib --stack nonexistent` → should list valid stacks

### Lint Checker
```bash
mql5-lint tests/fixtures/ap01_no_sl.mq5        # Should detect AP-01
mql5-lint scaffolds/stdlib/netting/template.mq5  # Should PASS (clean code)
```

### Permission Pipeline
```bash
PYTHONPATH=scripts python -c "
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
import json
result = run_permission_pipeline('tests/fixtures/ap01_no_sl.mq5', 'PERSONAL')
print(json.dumps(result, indent=2))
"
```

**Adversarial:** Invalid mode → should return error dict with valid modes listed.

## Preview Site Testing

### URL
https://vibecodekit-mql5-ea-preview-wpyifglq.devinapps.com

Deploy from: `/home/ubuntu/repos/vibecodekit-mql5-ea-preview`

### CDN Caching Workaround

After redeploying, the browser may serve a cached version of the old HTML. To force a fresh load:
1. Use a cache-busting URL parameter: `?nocache=<timestamp>`
2. Or use `curl` to verify the deployed HTML has the fix before troubleshooting browser issues
3. The JavaScript `fetch()` API with `{cache: 'no-store'}` can also bypass cache from within the page
4. Do NOT rely on Ctrl+Shift+R alone — CDN edge caches may still serve stale content

### Bilingual i18n Testing

The site uses client-side i18n via JavaScript `setLang()` function:
- Elements must have `class="i18n"` to be processed
- Language data stored in `data-vi` and `data-en` HTML attributes
- `setLang('en')` sets `innerHTML` to `data-en` value for all `.i18n` elements

**Test procedure:**
1. Load page fresh (with cache buster if recently deployed)
2. Verify default language is Vietnamese
3. Click EN → verify ALL text switches (header, nav buttons, content, footer)
4. Click VI → verify ALL text reverts
5. Check nav buttons specifically — they had a bug where `i18n` class was missing

**9 nav buttons to verify:**
- Tổng quan / Overview
- 6 Giai đoạn / 6 Phases
- Thư viện MQL5 / MQL5 Libraries
- Công cụ CLI / CLI Tools
- 17 Scaffolds / 17 Scaffolds
- Anti-Patterns / Anti-Patterns
- Kiểm thử / Tests
- Thử ngay / Try It
- Kiến trúc / Architecture

### Scaffold Generator Demo
1. Select preset from dropdown
2. Select stack
3. Enter EA name
4. Click "Generate Scaffold" → code appears in preview
5. Verify code includes correct `#include` statements

### Lint Checker Demo
1. Paste bad MQL5 code in textarea
2. Click "Run Lint Check"
3. Verify AP detections appear (AP-01, AP-15, AP-20 for default bad code)

## Phase-Specific Testing

### Phase C (Methodology)
- 6 RRI personas × 25 questions each
- 8 rri-templates
- 5 review scripts (63-88 LOC, not stubs)
- 7 permission layers with real logic

### Phase D (Tech 2024)
- onnx_export: framework detection (torch/tensorflow/sklearn)
- onnx_embed: opset validation (reject <8 or >99)
- cloud_optimize: cost gate blocks PERSONAL mode
- async_build: scaffold generation

### Phase E (Polish)
- 12 scripts (51-100 LOC)
- mt5-bridge: 10 tools
- algo-forge: 6 tools
- scan: detects .mq5 files + scaffolds
- audit: 50/50 conformance

## Cross-Phase Checks
```bash
# All 44 CLI entries registered
pip show vibecodekit-mql5-ea | grep -c "mql5-"

# No script exceeds 200 LOC
find scripts/ -name '*.py' -exec wc -l {} + | sort -n | tail -5

# No forbidden files
ls -la scripts/query_loop.py scripts/tool_executor.py scripts/intent_router.py 2>&1
# Should all say "No such file"
```

## Devin Secrets Needed

No secrets required — all testing uses local CLI tools and public preview site.
