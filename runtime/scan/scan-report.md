# SCAN Report — vibecodekit-mql5-ea v5

**Date:** 2026-05-13
**Scanner:** VibecodeKit Hybrid Ultra v0.26.0 + Devin manual scan

---

## 1. Project identity

| Field | Value |
|-------|-------|
| Name | vibecodekit-mql5-ea |
| Version | 0.0.1 (Phase 0 — Bootstrap) |
| License | MIT |
| Python requires | >= 3.10 |
| Domain | MQL5 Expert Advisor development kit for MetaTrader 5 |
| Target v1.0.0 | 14–17 weeks (6 phases: 0 → A → B → C → D → E) |

## 2. Repository layout (30 files, ~3066 LOC)

```
vibecodekit-mql5-ea/
├── .github/workflows/ci.yml          (143 LOC) — CI Linux + Windows
├── .gitignore
├── LICENSE (MIT)
├── README.md                         (52 LOC)
├── VERSION                           → 0.0.1
├── pyproject.toml                    (52 LOC)
├── docs/
│   ├── PLAN-v5.md                    (1089 LOC) — Master plan
│   ├── anti-patterns-AVOID.md        (137 LOC) — 5 anti-patterns to avoid
│   ├── phase-{0,A,B,C,D,E}-spec.md  — Per-phase strict specs
├── scripts/
│   ├── setup-wine-metaeditor.sh      (163 LOC) — Wine + MT5 installer
│   └── audit-plan-v5.py              (359 LOC) — Anti-drift audit
├── tests/
│   ├── fixtures/                     — 8 AP .mq5 + 3 .xml tester reports + 1 demo_smoke.mq5
│   └── gates/phase-0/               — 5 smoke tests
├── Include/                          (empty — Phase A populates)
└── scaffolds/                        (empty — Phase A populates)
```

## 3. VibecodeKit Doctor results

```json
{
  "skill_repo": false,
  "advisory_missing": [".claw.json", "CLAUDE.md", ".claude/commands", ...],
  "runtime_exists": false,
  "package_importable": true,
  "exit_code": 0
}
```

**Note:** advisory items are expected missing — this is a domain project, not a VCK-HU skill repo.

## 4. Dependencies

| Dependency | Type | Phase |
|------------|------|-------|
| pytest >= 7.4 | dev | 0 |
| pytest-cov >= 4.1 | dev | 0 |
| pyyaml >= 6.0 | dev | 0 |
| ruff >= 0.1 | dev | 0 |
| onnx >= 1.14 | phase-d | D |
| torch >= 2.0 | phase-d | D |
| MetaTrader5 >= 5.0.45 | phase-d | D |

## 5. Phase rollout plan

| Phase | Goal | Tag | Tests | Weeks |
|-------|------|-----|-------|-------|
| 0 | Bootstrap (Wine + MetaEditor + CI) | v0.0.1 | 5 smoke | 1 |
| A | Core (CPipNormalizer + 4 cmd + 4 scaffolds + 8 AP linter) | v0.1.0 | 3 e2e + 25 unit | 3 |
| B | Test (Tester + walk-forward + multi-broker) | v0.2.0 | 6 e2e + 30 unit | 3 |
| C | Methodology (RRI + 8×8 matrix + 7-layer permission) | v0.3.0 | 0 e2e + 25 unit | 3 |
| D | Tech 2024-2025 (ONNX + HFT + Algo Forge + LLM) | v0.5.0 | 1 e2e + 25 unit | 3-4 |
| E | Polish (26 refs + 3 MCP + worked example + canary) | v1.0.0 | 10 int + 30 docs | 2-3 |

## 6. Anti-patterns EXPLICITLY FORBIDDEN

1. **Dead code** — DO NOT port `query_loop.py`, `tool_executor.py` from VCK-HU
2. **Router pattern** — DO NOT port `intent_router.py`, `pipeline_router.py`
3. **Master command** — NO `/mql5` master router; user invokes individual commands
4. **God module** — Each Python script < 200 LOC, 1 responsibility
5. **Self-referential conformance** — Use 10 e2e external + 60 internal probes

## 7. Key domain artifacts (from fixtures)

- 8 anti-pattern fixture `.mq5` files (AP-1,3,5,15,17,18,20,21)
- 3 Strategy Tester XML reports (EURUSD H1, USDJPY H1, XAUUSD H1 3d)
- 1 demo smoke `.mq5` for compile verification

## 8. Risks identified

| Risk | Mitigation |
|------|-----------|
| Wine + MetaEditor setup may fail on CI | Retry mechanism in `setup-wine-metaeditor.sh` + xvfb fallback |
| Multi-broker tests need demo credentials (Phase B) | User provides FxPro/Exness/ICMarkets demo accounts |
| Python script size creep | `audit-plan-v5.py` enforces < 200 LOC ceiling per module |
| ONNX/PyTorch heavy deps (Phase D) | Optional `[phase-d]` extra, not required for core |

---

**SCAN COMPLETE.** Ready for Step 2 — RRI (Reverse Requirements Interview).
