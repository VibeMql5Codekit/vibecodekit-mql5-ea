---
name: testing-vibecodekit-mql5-ea
description: Test the vibecodekit-mql5-ea preview site and CLI tools end-to-end. Use when verifying preview site UI, scaffold generator, lint checker, or CLI tool changes.
---

# Testing vibecodekit-mql5-ea

## Prerequisites

- Python 3 with pytest installed
- Preview site deployed to devinapps.com (static HTML, no backend)
- Repo cloned at `/home/ubuntu/repos/vibecodekit-mql5-ea`

## Devin Secrets Needed

None — no secrets required for testing. The preview site is public and CLI tools run locally.

## Preview Site URL

The preview site is deployed as a static frontend. Check for the deployment URL in PR comments or use the `deploy` tool with `command="frontend"` pointing to the preview directory.

## Test Procedure

### 1. CLI Tools (Shell — No Recording Needed)

Run these from the repo root:

```bash
cd /home/ubuntu/repos/vibecodekit-mql5-ea

# Full test suite
python -m pytest tests/ -v
# Expected: 81 passed, 2 skipped (Wine/MetaEditor deps), 0 failed

# Anti-drift audit
python scripts/audit-plan-v5.py --post-phase=A
# Expected: ✓ Post-phase A PASSED

# Lint CLI on fixture
PYTHONPATH=scripts python -m vibecodekit_mql5.lint tests/fixtures/ap_01_no_sl.mq5
# Expected: AP-01 detected, exit code 1

# Build presets count
PYTHONPATH=scripts python -c "from vibecodekit_mql5.build import list_presets; print(len(list_presets()))"
# Expected: 17
```

### 2. Preview Site (Browser — Record This)

Maximize browser before recording:
```bash
sudo apt-get install -y wmctrl 2>/dev/null
wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz
```

#### Navigation Test
- Click each of the 9 tabs: Overview, 6 Phases, MQL5 Libraries, CLI Tools, 19 Scaffolds, Anti-Patterns, Tests, Try It, Architecture
- Verify each tab switches content correctly (JS `show()` function toggles section visibility)

#### Overview Stats
- Verify 6 stat cards show correct values (these may change as project grows)
- Current expected: 145 Files, 5785 LOC, 81 Tests, 19 Scaffolds, 7 Libraries, 18 CLI Commands

#### Scaffold Generator ("Try It" tab)
1. Select preset (e.g., "stdlib"), stack (e.g., "netting"), type EA name
2. Click "Generate Scaffold"
3. Verify output contains:
   - EA name in header (`{name}.mq5 — {preset} EA ({stack})`)
   - 3 includes: CPipNormalizer.mqh, CRiskGuard.mqh, CMagicRegistry.mqh
   - Strategy placeholder: `YOUR {PRESET_UPPER} STRATEGY LOGIC HERE`
   - EA name used in copyright, riskGuard.Init, magicReg.Reserve
4. Change preset and regenerate — verify output updates

#### Lint Checker ("Try It" tab)
1. Default code has 3 violations: `trade.Buy(0.1, ...)` (no SL), `50 * 0.0001` (hardcoded pip), `OrderSend(req, res)` (raw OrderSend)
2. Click "Run Lint Check"
3. Verify output: AP-01 (No stop-loss), AP-15 (Raw OrderSend), AP-20 (Hardcoded pip), "3 critical, 0 warnings"
4. Replace with clean code (e.g., `void OnTick() { Print("hello"); }`)
5. Click "Run Lint Check" again
6. Verify output: `0 critical, 0 warnings — PASS`

## Common Issues

- The 2 skipped tests require Wine + MetaEditor (Windows environment) — this is expected on Linux
- Scaffold AP-05 warnings (> 6 inputs) are expected for templates
- The preview site is purely client-side JS — no API calls, no backend
- `PYTHONPATH=scripts` is required when running CLI tools as Python modules
- No CI runners may be configured on new repos — check Settings → Actions
