# Task Graph — vibecodekit-mql5-ea v5

**Date:** 2026-05-13
**Pipeline step:** 5/8
**Total TIPs:** 25 across 6 phases

---

## DAG Visualization

```
                    ┌──────────┐
                    │  START   │
                    └────┬─────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ TIP-001 │    │ TIP-002 │    │ TIP-003 │
    │ Wine    │    │ CI yml  │    │ Audit   │
    │ setup   │    │         │    │ script  │
    └────┬────┘    └────┬────┘    └────┬────┘
         │              │              │
         └──────────┬───┘              │
                    ▼                  │
              ┌─────────┐             │
              │ TIP-004 │◀────────────┘
              │ 5 smoke │
              │ tests   │
              └────┬────┘
                   │
          ═════════╪═══════════ Phase 0 done (v0.0.1) ═══
                   │
         ┌─────────┼─────────┐
         ▼         ▼         ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ TIP-005 │ │ TIP-006 │ │ TIP-007 │
    │ PipNorm │ │ Risk +  │ │ lint.py │
    │ .mqh    │ │ Magic   │ │ 8 AP    │
    └────┬────┘ └────┬────┘ └────┬────┘
         │           │           │
         └─────┬─────┘           │
               ▼                 │
         ┌─────────┐             │
         │ TIP-008 │◀────────────┘
         │ build + │
         │ compile │
         └────┬────┘
              │
              ▼
         ┌─────────┐
         │ TIP-009 │
         │ 4 scaff │
         └────┬────┘
              │
              ▼
         ┌─────────┐
         │ TIP-010 │
         │ Phase A │
         │ tests   │
         └────┬────┘
              │
     ═════════╪═══════════ Phase A done (v0.1.0) ═══
              │
    ┌─────────┼──────────────┐
    ▼         ▼              ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ TIP-011 │ │ TIP-012 │ │ TIP-014 │
│ backtest│ │ MC +    │ │ trader  │
│ + WF    │ │ overfit │ │ check   │
└────┬────┘ └────┬────┘ └────┬────┘
     │           │           │
     └─────┬─────┘           │
           ▼                 │
     ┌─────────┐             │
     │ TIP-013 │◀────────────┘
     │ multi-  │
     │ broker  │
     └────┬────┘
          │
          ▼
     ┌─────────┐
     │ TIP-015 │
     │ Phase B │
     │ tests   │
     └────┬────┘
          │
     ═════╪═══════════ Phase B done (v0.2.0) ═══
          │
    ┌─────┼──────────┐
    ▼     ▼          ▼
┌──────┐┌──────┐┌──────┐
│TIP-16││TIP-17││TIP-18│
│ RRI  ││matrix││7-lyr │
│pers  ││ 8×8  ││perm  │
└──┬───┘└──┬───┘└──┬───┘
   │       │       │
   └───┬───┘       │
       ▼           │
  ┌─────────┐      │
  │ TIP-019 │◀─────┘
  │ 13 BP   │
  │ AP+rev  │
  └────┬────┘
       │
  ═════╪═══════════ Phase C done (v0.3.0) ═══
       │
  ┌────┼────────────┐
  ▼    ▼            ▼
┌────┐┌────┐  ┌─────────┐
│T-20││T-21│  │ TIP-022 │
│ONNX││HFT │  │ 13 scaff│
│    ││+LLM│  │ +method │
└──┬─┘└──┬─┘  └────┬────┘
   │     │         │
   └──┬──┘         │
      │             │
  ════╪═════════════╪══ Phase D done (v0.5.0) ═══
      │             │
  ┌───┴─────────────┴───┐
  ▼                     ▼
┌─────────┐       ┌─────────┐
│ TIP-023 │       │ TIP-024 │
│ 3 MCP + │       │ example │
│ 26 refs │       │ +canary │
└────┬────┘       └────┬────┘
     │                 │
     └────────┬────────┘
              ▼
        ┌─────────┐
        │ TIP-025 │
        │ 70 conf │
        │ + docs  │
        └────┬────┘
             │
        ═════╪═══════ Phase E done (v1.0.0) ═══
             │
        ┌────┴────┐
        │  DONE   │
        └─────────┘
```

---

## TIP Details (JSON)

### Phase 0 — Bootstrap

#### TIP-001: Wine + MetaEditor Setup Script
```json
{
  "id": "TIP-001",
  "phase": "0",
  "title": "Setup Wine + MetaEditor installer script",
  "description": "Verify and enhance scripts/setup-wine-metaeditor.sh. Install Wine 8.0+, MetaEditor64.exe under Wine prefix, xvfb, Python venv.",
  "depends_on": [],
  "req_covered": ["REQ-AUDIT"],
  "files_touched": ["scripts/setup-wine-metaeditor.sh"],
  "acceptance": "Wine 8.0+ installed, MetaEditor64.exe found under WINEPREFIX, xvfb available",
  "effort_min": 120,
  "status": "pending"
}
```

#### TIP-002: CI Workflow
```json
{
  "id": "TIP-002",
  "phase": "0",
  "title": "GitHub Actions CI (Linux + Windows)",
  "description": "Verify .github/workflows/ci.yml runs Wine smoke tests on Linux runner and native MetaEditor on Windows runner.",
  "depends_on": [],
  "req_covered": ["REQ-AUDIT"],
  "files_touched": [".github/workflows/ci.yml"],
  "acceptance": "CI triggers on PR, both runners pass",
  "effort_min": 60,
  "status": "pending"
}
```

#### TIP-003: Audit Script Skeleton
```json
{
  "id": "TIP-003",
  "phase": "0",
  "title": "Implement audit-plan-v5.py with FORBIDDEN files/patterns",
  "description": "Full implementation of anti-drift audit: FORBIDDEN_FILES, FORBIDDEN_PATTERNS, PHASE_FILES, audit_pre_phase(), audit_post_phase().",
  "depends_on": [],
  "req_covered": ["REQ-AUDIT"],
  "files_touched": ["scripts/audit-plan-v5.py"],
  "acceptance": "audit --pre-phase=0 and --post-phase=0 both return exit 0",
  "effort_min": 90,
  "status": "pending"
}
```

#### TIP-004: 5 Smoke Tests
```json
{
  "id": "TIP-004",
  "phase": "0",
  "title": "Write 5 Phase 0 smoke tests",
  "description": "test_wine_version_8_or_above, test_metaeditor_compile_demo_mq5, test_xvfb_headless_works, test_python_venv_pytest, test_ci_workflow_yaml_valid",
  "depends_on": ["TIP-001", "TIP-002", "TIP-003"],
  "req_covered": ["REQ-AUDIT"],
  "files_touched": ["tests/gates/phase-0/test_phase_0_smoke.py"],
  "acceptance": "5/5 tests pass on Linux",
  "effort_min": 60,
  "status": "pending"
}
```

### Phase A — Core Foundation

#### TIP-005: CPipNormalizer.mqh
```json
{
  "id": "TIP-005",
  "phase": "A",
  "title": "CPipNormalizer.mqh — flagship cross-broker pip math",
  "description": "Implement Init(), Pips(), PriceToPips(), PipValue(), LotForRisk(), IsValidSLDistance(), ClampSLPips(). Truth table: pip = (digits ∈ {3,5}) ? 10*point : 1*point.",
  "depends_on": ["TIP-004"],
  "req_covered": ["REQ-PIP"],
  "files_touched": ["Include/CPipNormalizer.mqh"],
  "acceptance": "≤ 250 LOC, correct on 5d/4d/3d/2d, unit tests pass",
  "effort_min": 180,
  "status": "pending"
}
```

#### TIP-006: CRiskGuard + CMagicRegistry
```json
{
  "id": "TIP-006",
  "phase": "A",
  "title": "CRiskGuard.mqh + CMagicRegistry.mqh",
  "description": "CRiskGuard: daily-loss limit + max-positions enforcement. CMagicRegistry: file-backed unique magic number reservation per EA×symbol.",
  "depends_on": ["TIP-004"],
  "req_covered": ["REQ-RISK", "REQ-MAGIC"],
  "files_touched": ["Include/CRiskGuard.mqh", "Include/CMagicRegistry.mqh"],
  "acceptance": "CRiskGuard ≤ 150 LOC, CMagicRegistry ≤ 100 LOC",
  "effort_min": 120,
  "status": "pending"
}
```

#### TIP-007: lint.py — 8 Critical AP Detectors
```json
{
  "id": "TIP-007",
  "phase": "A",
  "title": "lint.py with 8 critical anti-pattern detectors",
  "description": "AP-1(no SL), AP-3(hardcoded lot), AP-5(overfitted), AP-15(raw OrderSend), AP-17(WebRequest OnTick), AP-18(async no handler), AP-20(hardcoded pip), AP-21(JPY/XAU broken). Exit 1 on any critical.",
  "depends_on": ["TIP-004"],
  "req_covered": ["REQ-AP8"],
  "files_touched": ["scripts/vibecodekit_mql5/__init__.py", "scripts/vibecodekit_mql5/lint.py"],
  "acceptance": "≤ 200 LOC, all 8 fixture .mq5 trigger correct AP",
  "effort_min": 120,
  "status": "pending"
}
```

#### TIP-008: build.py + compile.py + pip_normalize.py
```json
{
  "id": "TIP-008",
  "phase": "A",
  "title": "3 CLI commands: build, compile, pip-normalize",
  "description": "build.py: render scaffold to target dir. compile.py: wrap MetaEditor CLI, parse log. pip_normalize.py: auto-refactor hardcoded pip patterns to CPipNormalizer calls.",
  "depends_on": ["TIP-005", "TIP-006", "TIP-007"],
  "req_covered": ["REQ-PIP", "REQ-SCAFFOLD"],
  "files_touched": ["scripts/vibecodekit_mql5/build.py", "scripts/vibecodekit_mql5/compile.py", "scripts/vibecodekit_mql5/pip_normalize.py"],
  "acceptance": "Each ≤ 200 LOC, build renders scaffold, compile wraps MetaEditor, pip-normalize refactors fixture",
  "effort_min": 120,
  "status": "pending"
}
```

#### TIP-009: 4 Scaffolds
```json
{
  "id": "TIP-009",
  "phase": "A",
  "title": "4 scaffold templates (stdlib, wizard, portfolio, ml-onnx)",
  "description": "Each scaffold has netting/ (and optionally hedging/, python-bridge/) variants with EAName.mq5, Sets/default.set, README.md.",
  "depends_on": ["TIP-008"],
  "req_covered": ["REQ-SCAFFOLD"],
  "files_touched": ["scaffolds/stdlib/", "scaffolds/wizard-composable/", "scaffolds/portfolio-basket/", "scaffolds/ml-onnx/"],
  "acceptance": "4 presets render correctly via build.py",
  "effort_min": 120,
  "status": "pending"
}
```

#### TIP-010: Phase A Tests
```json
{
  "id": "TIP-010",
  "phase": "A",
  "title": "Phase A test suite (3 e2e + 25 unit)",
  "description": "test_pipnorm_4_digits_classes, test_lint_8_critical_AP_detects_all, test_build_compile_stdlib + 25 unit tests across 5 test files.",
  "depends_on": ["TIP-009"],
  "req_covered": ["REQ-AP8", "REQ-PIP"],
  "files_touched": ["tests/gates/phase-A/"],
  "acceptance": "28/28 tests pass",
  "effort_min": 90,
  "status": "pending"
}
```

### Phase B — Test & Validation

#### TIP-011: backtest.py + walkforward.py
```json
{
  "id": "TIP-011",
  "phase": "B",
  "title": "Backtest XML parser + walk-forward IS/OOS",
  "description": "backtest.py: parse MT5 Strategy Tester XML, extract metrics (PF, Sharpe, DD, trades). walkforward.py: Forward 1/4 mode, IS/OOS split, metric comparison.",
  "depends_on": ["TIP-010"],
  "req_covered": ["REQ-WF"],
  "files_touched": ["scripts/vibecodekit_mql5/backtest.py", "scripts/vibecodekit_mql5/walkforward.py"],
  "acceptance": "Each ≤ 200 LOC, parse 3 fixture XMLs correctly, WF OOS extraction works",
  "effort_min": 120,
  "status": "pending"
}
```

#### TIP-012: monte_carlo.py + overfit_check.py
```json
{
  "id": "TIP-012",
  "phase": "B",
  "title": "Monte Carlo bootstrap + overfit detection",
  "description": "monte_carlo.py: bootstrap trade sequences N times, report DD at 50/75/95 percentile. overfit_check.py: OOS PF / IS PF ratio, threshold.",
  "depends_on": ["TIP-010"],
  "req_covered": ["REQ-MC"],
  "files_touched": ["scripts/vibecodekit_mql5/monte_carlo.py", "scripts/vibecodekit_mql5/overfit_check.py"],
  "acceptance": "Each ≤ 200 LOC, correct percentile computation",
  "effort_min": 90,
  "status": "pending"
}
```

#### TIP-013: multibroker.py + broker_safety.py
```json
{
  "id": "TIP-013",
  "phase": "B",
  "title": "Multi-broker orchestrator + broker safety layer",
  "description": "multibroker.py: orchestrate tests across 3 brokers, compute stability metrics (PF stdev/mean, Sharpe stdev, DD diff). broker_safety.py: Layer 7 standalone check.",
  "depends_on": ["TIP-011", "TIP-012"],
  "req_covered": ["REQ-MULTI"],
  "files_touched": ["scripts/vibecodekit_mql5/multibroker.py", "scripts/vibecodekit_mql5/broker_safety.py"],
  "acceptance": "Each ≤ 200 LOC, stability tolerance enforced",
  "effort_min": 120,
  "status": "pending"
}
```

#### TIP-014: trader_check.py + deploy_vps.py
```json
{
  "id": "TIP-014",
  "phase": "B",
  "title": "Trader-17 checklist + VPS deploy",
  "description": "trader_check.py: 17-point checklist, return dict with PASS/WARN/N-A. deploy_vps.py: auto-deploy EA to MT5 VPS.",
  "depends_on": ["TIP-010"],
  "req_covered": ["REQ-T17"],
  "files_touched": ["scripts/vibecodekit_mql5/trader_check.py", "scripts/vibecodekit_mql5/deploy_vps.py"],
  "acceptance": "Each ≤ 200 LOC, 17 items checked",
  "effort_min": 90,
  "status": "pending"
}
```

#### TIP-015: Phase B Tests + Include Libs
```json
{
  "id": "TIP-015",
  "phase": "B",
  "title": "Phase B tests (6 e2e + 30 unit) + CMfeMaeLogger + CSpreadGuard",
  "description": "Include/CMfeMaeLogger.mqh, Include/CSpreadGuard.mqh + full Phase B test suite.",
  "depends_on": ["TIP-013", "TIP-014"],
  "req_covered": ["REQ-MULTI", "REQ-WF"],
  "files_touched": ["Include/CMfeMaeLogger.mqh", "Include/CSpreadGuard.mqh", "tests/gates/phase-B/"],
  "acceptance": "36/36 tests pass",
  "effort_min": 120,
  "status": "pending"
}
```

### Phase C — Methodology

#### TIP-016: RRI Personas + Workflow
```json
{
  "id": "TIP-016",
  "phase": "C",
  "title": "RRI 6 personas YAML + step_workflow.py state machine",
  "description": "6 YAML files (trader, risk-auditor, broker-engineer, strategy-architect, devops, perf-analyst) × 25 questions each. 8-step state machine.",
  "depends_on": ["TIP-015"],
  "req_covered": ["REQ-RRI"],
  "files_touched": ["docs/rri-personas/", "scripts/vibecodekit_mql5/rri/"],
  "acceptance": "6 YAMLs valid, state machine transitions correct, mode-dependent Q count",
  "effort_min": 120,
  "status": "pending"
}
```

#### TIP-017: 8×8 Quality Matrix
```json
{
  "id": "TIP-017",
  "phase": "C",
  "title": "8 dimension × 8 axis quality matrix + HTML renderer",
  "description": "matrix.py: populate 64 cells, threshold check (≥56 PASS for Enterprise), generate HTML report.",
  "depends_on": ["TIP-015"],
  "req_covered": ["REQ-MAT"],
  "files_touched": ["scripts/vibecodekit_mql5/rri/matrix.py"],
  "acceptance": "≤ 200 LOC, 64 cells, valid HTML output",
  "effort_min": 90,
  "status": "pending"
}
```

#### TIP-018: 7-Layer Permission Pipeline
```json
{
  "id": "TIP-018",
  "phase": "C",
  "title": "7 permission layer scripts + orchestrator",
  "description": "layer1_source_lint.py through layer7_broker_safety.py + orchestrator.py. Mode-dependent: PERSONAL (L1-4,7), TEAM (L1-5,7), ENTERPRISE (L1-7).",
  "depends_on": ["TIP-015"],
  "req_covered": ["REQ-PERM"],
  "files_touched": ["scripts/vibecodekit_mql5/permission/"],
  "acceptance": "Each layer < 150 LOC, orchestrator mode-switch correct",
  "effort_min": 180,
  "status": "pending"
}
```

#### TIP-019: 13 Best-Practice AP + Review Commands
```json
{
  "id": "TIP-019",
  "phase": "C",
  "title": "Extend lint.py with 13 best-practice AP + review commands",
  "description": "AP-2,4,6-14,16,19 as warnings. review.py, eng_review.py, ceo_review.py, cso.py, investigate.py.",
  "depends_on": ["TIP-016", "TIP-017", "TIP-018"],
  "req_covered": ["REQ-AP8"],
  "files_touched": ["scripts/vibecodekit_mql5/lint.py", "scripts/vibecodekit_mql5/review/"],
  "acceptance": "lint.py ≤ 200 LOC (split if needed), 21 total AP",
  "effort_min": 120,
  "status": "pending"
}
```

### Phase D — Tech 2024-2025

#### TIP-020: ONNX Pipeline
```json
{
  "id": "TIP-020",
  "phase": "D",
  "title": "ONNX export + embed + COnnxLoader.mqh",
  "description": "onnx_export.py: PyTorch → ONNX. onnx_embed.py: embed in EA. Include/COnnxLoader.mqh: MQL5 inference wrapper.",
  "depends_on": ["TIP-019"],
  "req_covered": ["REQ-ONNX"],
  "files_touched": ["scripts/vibecodekit_mql5/onnx_export.py", "scripts/vibecodekit_mql5/onnx_embed.py", "Include/COnnxLoader.mqh"],
  "acceptance": "Each ≤ 200 LOC, e2e pipeline < 10min",
  "effort_min": 180,
  "status": "pending"
}
```

#### TIP-021: HFT Async + Algo Forge + LLM Bridge
```json
{
  "id": "TIP-021",
  "phase": "D",
  "title": "CAsyncTradeManager.mqh + forge + LLM bridge",
  "description": "async_build.py, forge_init.py, forge_pr.py, llm_context.py, cloud_optimize.py + Include/CAsyncTradeManager.mqh.",
  "depends_on": ["TIP-019"],
  "req_covered": ["REQ-HFT"],
  "files_touched": ["Include/CAsyncTradeManager.mqh", "scripts/vibecodekit_mql5/async_build.py", "scripts/vibecodekit_mql5/forge_init.py", "scripts/vibecodekit_mql5/forge_pr.py", "scripts/vibecodekit_mql5/llm_context.py", "scripts/vibecodekit_mql5/cloud_optimize.py"],
  "acceptance": "Each ≤ 200 LOC, LLM has timeout + fallback",
  "effort_min": 180,
  "status": "pending"
}
```

#### TIP-022: 13 Strategy Scaffolds + Method-Hiding Linter
```json
{
  "id": "TIP-022",
  "phase": "D",
  "title": "13 strategy scaffolds + method_hiding_check.py",
  "description": "trend, mean-reversion, breakout, hedging-multi, news-trading, arbitrage-stat, scalping, library, indicator-only, grid, dca, hft-async, service-llm-bridge scaffolds. method_hiding_check.py: detect method shadowing.",
  "depends_on": ["TIP-019"],
  "req_covered": ["REQ-SCAFFOLD"],
  "files_touched": ["scaffolds/", "scripts/vibecodekit_mql5/method_hiding_check.py"],
  "acceptance": "13 scaffolds render, method-hiding FP ≤ 30%",
  "effort_min": 120,
  "status": "pending"
}
```

### Phase E — Polish & Ship

#### TIP-023: 3 MCP Servers + 26 References
```json
{
  "id": "TIP-023",
  "phase": "E",
  "title": "3 MCP servers + 26 reference docs",
  "description": "mcp/metaeditor-bridge, mcp/mt5-bridge (READ-ONLY), mcp/algo-forge-bridge. docs/references/50-79.md (26 files).",
  "depends_on": ["TIP-020", "TIP-021", "TIP-022"],
  "req_covered": ["REQ-MCP", "REQ-REF"],
  "files_touched": ["mcp/", "docs/references/"],
  "acceptance": "3 servers handshake, mt5 READ-ONLY, 26 refs with valid frontmatter",
  "effort_min": 180,
  "status": "pending"
}
```

#### TIP-024: Worked Example + Canary + Final Commands
```json
{
  "id": "TIP-024",
  "phase": "E",
  "title": "EA Wizard MACD+SAR worked example + canary + utility commands",
  "description": "examples/ea-wizard-macd-sar-eurusd-h1-portfolio/ full walkthrough. canary.py, doctor.py, install.py, audit.py, ship.py, etc.",
  "depends_on": ["TIP-020", "TIP-021", "TIP-022"],
  "req_covered": ["REQ-CANARY"],
  "files_touched": ["examples/", "scripts/vibecodekit_mql5/canary.py", "scripts/vibecodekit_mql5/doctor.py", "scripts/vibecodekit_mql5/ship.py"],
  "acceptance": "Worked example complete, canary 30min check, ~30 commands catalog",
  "effort_min": 180,
  "status": "pending"
}
```

#### TIP-025: 70 Conformance Suite + Final Docs
```json
{
  "id": "TIP-025",
  "phase": "E",
  "title": "70 conformance tests + COMMANDS.md + QUICKSTART.md",
  "description": "10 e2e external + 60 internal probes. COMMANDS.md (all ~30 commands). QUICKSTART.md. MIGRATE-VPS.md.",
  "depends_on": ["TIP-023", "TIP-024"],
  "req_covered": ["REQ-AUDIT"],
  "files_touched": ["tests/", "docs/COMMANDS.md", "docs/QUICKSTART.md"],
  "acceptance": "70/70 pass, all docs complete, v1.0.0 ready",
  "effort_min": 120,
  "status": "pending"
}
```

---

## Critical Path

```
TIP-001/002/003 → TIP-004 → TIP-005/006/007 → TIP-008 → TIP-009 → TIP-010
→ TIP-011/012 → TIP-013 → TIP-015 → TIP-016/017/018 → TIP-019
→ TIP-020/021/022 → TIP-023/024 → TIP-025 → DONE
```

**Critical path length:** 15 sequential steps
**Parallelizable:** TIP-001/002/003 (Phase 0), TIP-005/006/007 (Phase A start), TIP-011/012/014 (Phase B start), TIP-016/017/018 (Phase C start), TIP-020/021/022 (Phase D), TIP-023/024 (Phase E start)

---

## Execution Priority for Current Session

**Focus on Phase 0 + Phase A** (TIP-001 → TIP-010) as they form the foundation. Wine/MetaEditor setup (TIP-001) is the critical first step but may not be fully achievable on this VM — fallback to mock/stub compile for CI.

Phases B-E can be structured/scaffolded now but will need separate sessions for full implementation (per HANDOFF-README.md recommendation).

---

**TASK GRAPH COMPLETE.** Ready for Step 6 — BUILD.
