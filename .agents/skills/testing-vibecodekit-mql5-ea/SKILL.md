---
name: testing-vibecodekit-mql5-ea
description: Test the vibecodekit-mql5-ea toolkit end-to-end. Use when verifying CLI tools, preview site, scaffold templates, RRI methodology commands, Prompt Architect flows, or bilingual i18n changes.
---

# Testing vibecodekit-mql5-ea

## Setup

```bash
cd /home/ubuntu/repos/vibecodekit-mql5-ea
pip install -e ".[dev]"
```

## Devin Secrets Needed

No secrets required for local CLI tests, deterministic Prompt Architect tests, or the public preview site. Optional provider-backed LLM adapter tests require provider API keys, but prompt-only validation does not.

## Quick Smoke Test

```bash
pytest tests/ -q
# Expected locally: 169 passed, 2 skipped when Wine/MetaEditor smoke deps are unavailable
```

## CLI-Only Testing Evidence

For CLI/runtime changes, use shell commands and attach command output or a markdown report. Do not start a screen recording when all testing is shell-only because the recording will only show an idle desktop.

## Runtime CLI Count Check

When README/docs claim the CLI count, verify against `pyproject.toml`:

```bash
python - <<'PY'
import tomllib
from pathlib import Path
scripts = tomllib.loads(Path('pyproject.toml').read_text())['project']['scripts']
print(len(scripts))
for name in ['mql5-rri', 'mql5-rri-bt', 'mql5-rri-rr', 'mql5-rri-chart', 'mql5-matrix', 'mql5-prompt-architect']:
    print(name, scripts[name])
PY
# Expected: 46 total scripts; RRI/matrix names map to vibecodekit_mql5.rri.* modules; Prompt Architect maps to prompt_architect.cli
```

Smoke every entry point with `--help` after changing CLI packaging:

```bash
python - <<'PY'
import subprocess, tomllib
from pathlib import Path
scripts = tomllib.loads(Path('pyproject.toml').read_text())['project']['scripts']
failures = []
for name in scripts:
    result = subprocess.run([name, '--help'], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if result.returncode != 0 or 'usage:' not in result.stdout.lower():
        failures.append((name, result.returncode, result.stdout[:300]))
print(f'checked={len(scripts)} failures={failures}')
raise SystemExit(1 if failures else 0)
PY
```

## RRI CLI End-to-End Test

Use this flow when verifying RRI/persona/matrix changes:

```bash
# Single-persona enterprise session: exact persona question count and workflow wiring
mql5-rri --mode ENTERPRISE --persona trader --json
# Expected: exit 0, mode ENTERPRISE, total_questions 25, one trader interview, workflow has 8 steps

# Team session across all six personas
mql5-rri --mode TEAM --json
# Expected: exit 0, 6 interviews, total_questions 72 (6 personas × 12 TEAM questions)

# Standalone matrix with no evidence intentionally fails closed
mql5-matrix --mode ENTERPRISE --html /home/ubuntu/matrix-empty.html
# Expected: exit 1, stdout contains "Matrix: 0/64 PASS (threshold: 56, gate: FAIL)", HTML contains a <table>

# RRI backtest flow supplies passable evidence for the matrix
mql5-rri-bt --mode TEAM --personas all --json
# Expected: exit 0, matrix.total_cells 64, passed 56, warned 8, failed 0, gate_pass true

mql5-rri-rr --mode TEAM --persona all --json
# Expected: exit 0, 6 reviews, total_questions > 0

mql5-rri-chart --mode TEAM --persona all --json
# Expected: exit 0, 6 reviews, total_questions > 0
```

## Prompt Architect Deterministic Test

Use explicit artifact output paths; the CLI does not have `--output-dir`, `--steps`, or `--dry-run` flags.

```bash
OUT=/home/ubuntu/prompt-architect-e2e
rm -rf "$OUT" && mkdir -p "$OUT"
mql5-prompt-architect \
  --config examples/prompt-architect/dca-grid-propfirm.yaml \
  --validate --recommend-preset \
  --render-prompt "$OUT/prompt.md" \
  --vision "$OUT/vision.md" \
  --requirements "$OUT/requirements.json" \
  --blueprint "$OUT/blueprint.md" \
  --rri-plan "$OUT/rri-plan.md" \
  --pipeline "$OUT/pipeline.json" \
  --json
# Expected: exit 0, valid=true, recommendation dca/hedging, all 6 artifacts written

mql5-prompt-architect --run-pipeline "$OUT/pipeline.json" --from-step 3 --to-step 4 --json
# Expected: exit 0, valid=true, execute=false, steps_run=2, step names build_scaffold and lint
```

## Scaffold Deep Test (All 17 Presets / 22 Combos)

`mql5-build --list` prints lines like `  preset: stack, stack`; parse this format, not bullet lines.

```bash
mql5-build --list
# Expected: 17 presets / 22 preset×stack combos

# Test each combo: scaffold + lint
# mql5-build --preset <preset> --stack <stack> --name TestEA --output /tmp/test
# mql5-lint /tmp/test/TestEA/TestEA.mq5
# Expected per combo: rendered .mq5 exists and lint reports 0 critical findings
```

### Key Checks per Scaffold

1. **AP-05 (input count)**: `grep -c "^input " file.mq5` should be ≤ 6 for strict scaffolds.
2. **EventSetTimer/EventKillTimer pairs**: If `OnTimer()` exists, both `EventSetTimer()` and `EventKillTimer()` should exist.
3. **ArraySetAsSeries before CopyBuffer**: If `CopyBuffer`/`CopyClose` etc. are used, `ArraySetAsSeries` should be called first.
4. **Lint 0 criticals**: `mql5-lint` should show 0 critical; warnings are acceptable for some scaffolds.

### Presets with Multiple Stacks

- `portfolio-basket`: hedging, netting
- `stdlib`: hedging, netting, python-bridge
- `service-llm-bridge`: cloud-api, embedded-onnx-llm, self-hosted-ollama

## Lint Testing

```bash
# Real criticals/warnings use bracket markers
rg "^\[X\]" lint.log | wc -l
rg "^\[!\]" lint.log | wc -l
# Do not use: grep -c "critical" — it matches "0 critical" summary text.
```

## Preview Site Testing

- Add `?nocache=<label>` to bust CDN cache after deploy.
- Verify key current counts: Overview `169` tests, `46` CLI commands; footer `169 tests passing, 2 skipped • 46 CLI commands`.
- Verify Prompt Architect is represented in Overview, CLI, Tests, and Try It.
- Test VI/EN language toggle on all primary tabs.
- Mobile viewport: test at about 375×812 for overflow issues.
- Check all nav buttons switch language and remain reachable.

## Permission Pipeline Testing

```bash
PYTHONPATH=scripts python - <<'PY'
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
import json
result = run_permission_pipeline('path/to/EA.mq5', 'PERSONAL')
print(json.dumps(result, indent=2))
PY
```
