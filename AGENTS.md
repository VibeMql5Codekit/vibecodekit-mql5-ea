# AGENTS.md — Contract for AI coding agents

This document is the canonical, machine-readable-friendly contract for AI
coding agents (Devin, Claude Code, Cursor, Codex, Continue, Aider, etc.) working
in this repo. Human contributors should read [`README.md`](README.md) and
[`docs/QUICKSTART.md`](docs/QUICKSTART.md) instead.

> **Honest disclaimer.** Trader-17, the 8×8 quality matrix, the AP-XX
> anti-pattern IDs, the 7-layer permission pipeline, and the RRI personas are
> **project-defined heuristics** designed by this kit. They are opinionated
> guardrails — not industry standards, not certifications, and not substitutes
> for live-account validation. Treat them as such.

---

## 1. Scope and intent

`vibecodekit-mql5-ea` is a Python-based methodology kit for generating,
validating, and gating MQL5 Expert Advisors (EAs) for MetaTrader 5.

The kit is **CLI-first** and **fail-closed**:

- Every check has an exit code (0 = pass, non-zero = fail).
- Most checks support `--json` for structured output.
- No CLI silently bypasses a gate; layers in the permission pipeline fail-fast.

An agent's job is usually one of:

1. Generate a scaffold (`mql5-build`).
2. Edit the scaffold's strategy logic in `OnTick`.
3. Run the gates (lint → trader-check → permission → matrix).
4. Iterate until gates pass at the target mode (`PERSONAL` / `TEAM` / `ENTERPRISE`).
5. Open a PR.

---

## 2. Setup

```bash
pip install -e ".[dev]"
pytest tests/ -q
# Expected: 169 passed, 2 skipped (Wine/MetaEditor-dependent smoke tests)
```

System tools (Wine + `metaeditor64.exe`) are optional — when missing, the
compile layer reports `MetaEditor not found — skipped (non-blocking)` and the
permission pipeline continues.

---

## 3. Filesystem contract

Agents **may write** to:

| Path | Purpose |
|---|---|
| `runtime/` | Generated artefacts (scan reports, vision, blueprint, tasks, reference EAs). Gitignored where appropriate. |
| `output/`, `out/`, `dist/` | Scaffold targets — agents pass these via `--output`. |
| `tmp/`, `/tmp/` | Throwaway artefacts (matrix HTML, pipeline JSON, lint reports). |
| `examples/` | New worked examples, when the user explicitly asks. |
| `docs/QUICKSTART*.md` and `docs/reference-ea/` | Generated user-facing snapshots. |

Agents **must not write to** without explicit user instruction:

| Path | Why |
|---|---|
| `Include/*.mqh` | Shared MQL5 libraries (`CPipNormalizer`, `CRiskGuard`, `CMagicRegistry`, …). Changes affect every downstream EA. |
| `scaffolds/**` | Templates consumed by `mql5-build`. Edits touch every future generated EA. |
| `scripts/vibecodekit_mql5/permission/**` | Gate semantics — changes invalidate the contract this document advertises. |
| `tests/fixtures/**` | Canonical inputs for acceptance tests. |
| `docs/phase-*-spec.md`, `docs/PLAN-v5.md`, `docs/AUDIT-REVIEW.md` | Internal sprint specs. Stable references. |
| `pyproject.toml` (script entries) | Adding CLIs requires PR review by maintainers. |

Agents **may read everything**.

---

## 4. CLI surface

### 4.1 Core build & quality

| Command | Purpose | Exit |
|---|---|---|
| `mql5-build --list` | List presets and stacks | 0 always |
| `mql5-build --preset <p> --stack <s> --name <ea> --output <dir>` | Render scaffold; replaces `EAName` | 0 ok, 1 bad preset/stack |
| `mql5-lint <file-or-dir>` | Anti-pattern detection (8 critical, 5 warnings) | 0 if 0 critical, 1 otherwise |
| `mql5-compile <file.mq5>` | Compile via MetaEditor/Wine when available | 0 ok, 1 fail, exit-skip when no compiler |
| `mql5-pip-normalize <paths> [--fix]` | Detect/fix hardcoded pip math | 0 ok, 1 if findings without `--fix` |

### 4.2 Validation & deployment gates

| Command | Purpose | Exit |
|---|---|---|
| `mql5-backtest <report.xml>` | Parse MT5 Strategy Tester XML | 0 ok, 1 parse error |
| `mql5-walkforward <is.xml> <oos.xml>` | IS/OOS degradation check | 0 ok, 1 degrade |
| `mql5-monte-carlo <report.xml>` | DD95 simulation | 0 ok, 1 bust |
| `mql5-multibroker <reports...>` | Cross-broker variance check | 0 ok, 1 fail |
| `mql5-trader-check --ea <file.mq5>` | Trader-17 (≥ 15 / 17 PASS) | 0 ok, 1 fail |
| `mql5-permission --ea <file.mq5> --mode <PERSONAL\|TEAM\|ENTERPRISE>` | Run fail-fast permission pipeline | 0 ok, 1 fail |
| `mql5-broker-safety --ea <file.mq5>` | Permission layer 7 standalone | 0 ok, 1 fail |
| `mql5-matrix --mode <mode> [--html out.html]` | 8×8 cell summary (defaults to N-A without evidence) | 0 ok, 1 below threshold |

### 4.3 Methodology (RRI & Prompt Architect)

| Command | Purpose | Exit |
|---|---|---|
| `mql5-rri --mode <m> [--persona <p>] [--json]` | RRI questionnaire | 0 always |
| `mql5-rri-bt --mode <m> --personas <list> [--report f] [--json]` | RRI backtest review + matrix evidence | 0 ok, 1 fail |
| `mql5-rri-rr` / `mql5-rri-chart` | RRI risk-review / chart-review | 0 ok |
| `mql5-prompt-architect --config <c> --validate --recommend-preset [...]` | Deterministic EA intake → scaffold recommendation | 0 ok, 1 invalid |
| `mql5-prompt-architect --run-pipeline <plan.json> --from-step N --to-step M` | Validate + (optionally execute) a pipeline plan | 0 ok, 1 invalid |

The Prompt Architect pipeline executor (`prompt_architect.pipeline_runner`)
allow-lists exactly these tools: `mql5-prompt-architect`, `mql5-build`,
`mql5-lint`, `mql5-compile`, `mql5-permission`, `mql5-matrix`. The pipeline
must contain exactly the 7 steps:

1. `validate_prompt_config`
2. `generate_planning_artifacts`
3. `build_scaffold`
4. `lint`
5. `compile`
6. `permission_gate`
7. `quality_matrix`

### 4.4 Reviews and project hygiene

`mql5-review`, `mql5-eng-review`, `mql5-ceo-review`, `mql5-cso`,
`mql5-investigate`, `mql5-scan`, `mql5-vision`, `mql5-blueprint`,
`mql5-survey`, `mql5-tip`, `mql5-doctor`, `mql5-audit`, `mql5-canary`,
`mql5-ship`, `mql5-refine`, `mql5-install`, `mql5-second-opinion`,
`mql5-fitness`, `mql5-mfe-mae`, `mql5-deploy-vps`, `mql5-overfit-check`,
`mql5-llm-context`, `mql5-onnx-export`, `mql5-onnx-embed`,
`mql5-async-build`, `mql5-cloud-optimize`, `mql5-method-hiding-check`,
`mql5-forge-init`, `mql5-forge-pr`.

> **Honest note on this list.** These are auxiliary heuristics, regex-based
> classifiers, and template generators — not deep static analysers. They are
> useful for nudges in a structured workflow but agents should not treat
> their outputs as load-bearing evidence on their own.

A complete enumeration is available via:

```bash
python -c "import tomllib, pathlib; print('\n'.join(sorted(tomllib.loads(pathlib.Path('pyproject.toml').read_text())['project']['scripts'])))"
```

---

## 5. Output schema convention

CLIs that support `--json` emit one of two shapes:

### 5.1 Gate result (lint, permission layer, trader-check, matrix)

```json
{
  "pass": true,
  "layer": 3,
  "name": "ap_lint",
  "details": "0 critical, 4 warnings",
  "criticals": 0,
  "warnings": 4
}
```

### 5.2 Pipeline result (permission orchestrator, prompt-architect)

```json
{
  "mode": "TEAM",
  "layers_run": 4,
  "all_pass": false,
  "results": {
    "L1": { "pass": true,  "layer": 1, "name": "source_lint",   "details": "OK" },
    "L2": { "pass": true,  "layer": 2, "name": "compile",       "details": "MetaEditor not found — skipped (non-blocking)" },
    "L3": { "pass": true,  "layer": 3, "name": "ap_lint",       "details": "0 critical, 4 warnings", "criticals": 0, "warnings": 4 },
    "L4": { "pass": false, "layer": 4, "name": "checklist",     "details": "Trader-17: 11/17 PASS, 0 WARN", "passed": 11, "warns": 0 }
  }
}
```

### 5.3 Convention notes

- `pass` is always boolean.
- `details` is a single-line human string suitable for terminal logs.
- Numeric fields (`criticals`, `passed`, `warned`, `failed`, `total_cells`) are integers.
- `name` matches the layer / step identifier, e.g. `source_lint`, `compile`,
  `ap_lint`, `checklist`, `methodology`, `quality_matrix`, `broker_safety`.

Agents may rely on the keys listed in this section. Other keys are
implementation detail and may change without notice.

---

## 6. Gate semantics

- **Exit codes.** `0` means the gate passed (or was a non-blocking skip). Any
  non-zero exit means the gate did not pass. Use this for shell pipelines.
- **Fail-fast.** `mql5-permission` runs layers in order and stops at the first
  failure. Later layers will not appear in the JSON `results` map.
- **Mode layers.**
  - `PERSONAL` → layers `1, 2, 3, 4, 7`
  - `TEAM` → layers `1, 2, 3, 4, 5, 7`
  - `ENTERPRISE` → layers `1, 2, 3, 4, 5, 6, 7`
- **Threshold semantics.** `mql5-trader-check` requires `≥ 15 / 17 PASS`.
  `mql5-matrix` thresholds: PERSONAL `32`, TEAM `48`, ENTERPRISE `56` (out of
  `64` cells).
- **Compile skip is non-blocking.** When MetaEditor is unavailable, layer 2
  returns `pass: true` with `details: "MetaEditor not found — skipped
  (non-blocking)"`. Agents should not treat this as a real compile.
- **No silent bypass.** There is intentionally **no** `--ignore` / `--force`
  flag on the gate CLIs. If a finding is wrong, fix the finding or update the
  rule via PR — do not work around it.

For a real example of these numbers on a freshly scaffolded EA, see
[`docs/reference-ea/REPORT.md`](docs/reference-ea/REPORT.md). Regenerate it
with `bash scripts/tools/build_reference_report.sh`.

---

## 7. Rule ID → documentation table

### 7.1 Anti-patterns (AP-XX) — emitted by `mql5-lint`

| Rule | Severity | Description | See |
|---|---|---|---|
| AP-01 | CRITICAL | Trade opened without stop-loss | `docs/GUIDE-BUILD-EA.md` |
| AP-03 | CRITICAL | Fixed lot size (hardcoded numeric literal) | `docs/GUIDE-BUILD-EA.md` |
| AP-05 | CRITICAL | Too many `input`/`extern` parameters (> 6) | `docs/GUIDE-BUILD-EA.md` |
| AP-15 | CRITICAL | Raw `OrderSend()` — use `CTrade` | `docs/GUIDE-BUILD-EA.md` |
| AP-17 | CRITICAL | `WebRequest` in `OnTick` | `docs/GUIDE-BUILD-EA.md` |
| AP-18 | CRITICAL | `OrderSendAsync` without `OnTradeTransaction` handler | `docs/GUIDE-BUILD-EA.md` |
| AP-20 | CRITICAL | Hardcoded pip value | `docs/references/79-pip-norm.md` |
| AP-21 | CRITICAL | JPY / XAU pip math broken | `docs/references/79-pip-norm.md` |
| AP-02 | WARNING | Trade without take-profit | `docs/GUIDE-BUILD-EA.md` |
| AP-04 | WARNING | No trailing stop | `docs/GUIDE-BUILD-EA.md` |
| AP-06 | WARNING | No retry on trade errors | `docs/GUIDE-BUILD-EA.md` |
| AP-07 | WARNING | `Print()` instead of `PrintFormat()` | `docs/GUIDE-BUILD-EA.md` |
| AP-08 | WARNING | No comment on trade operation | `docs/GUIDE-BUILD-EA.md` |

> **Honest note.** AP-05's "> 6 inputs = overfit" rule is a project default,
> not an industry threshold. Grid / portfolio / DCA EAs legitimately need
> more. Override only by changing the rule in `scripts/vibecodekit_mql5/lint.py`
> via PR (no per-file disable mechanism exists today).

### 7.2 Prompt-architect rules (PA-XXX) — emitted by `prompt-architect --validate`

| Rule | Severity | Description |
|---|---|---|
| PA-001 | critical | `risk.lot_mode = percent_risk` requires `risk.risk_percent` |
| PA-002 | critical | `risk.lot_mode = fixed` requires `risk.fixed_lot` |
| PA-003 | critical | Grid / DCA / Martingale requires `max_orders`, `distance_points`, `max_drawdown_percent` |
| PA-004 | critical | `filters.avoid_news` requires a news source policy |
| PA-005 | warning  | Prop-firm accounts should declare daily loss + drawdown limits |
| PA-006 | critical | `custom_indicator` requires explicit indicator conditions |
| PA-007 | warning  | ONNX strategies should define confidence threshold + fallback |
| PA-008 | critical | Live / prop-firm EAs require a stop policy (`sltp.mode != none`) |
| PA-009 | critical | Telegram, license, API, and broker secrets must not be in config |
| PA-010 | warning  | Unknown `broker_mode` requires broker-engineer RRI review |

Source of truth: `docs/prompt-architect/conflict-rules.yaml`.

### 7.3 Trader-17 checklist (T01–T17) — emitted by `mql5-trader-check`

See `docs/references/59-trader-checklist.md` for the full list. The gate
requires ≥ 15 / 17 PASS. Items T08–T11 are `N-A` until you supply external
evidence (walk-forward / Monte Carlo / multi-broker / overfit reports).

---

## 8. Reference numbers (honest empirical snapshot)

When this kit's gates run against a **freshly scaffolded EA** (no strategy
written yet), the kit reports:

| Gate | Result |
|---|---|
| `mql5-lint` | `0 critical, 4 warnings` (template artefacts: AP-04, AP-06, AP-08 × 2) |
| `mql5-trader-check` | `11 / 17 PASS`, 0 WARN, 6 N-A → **FAIL** (gate ≥ 15) |
| `mql5-permission --mode PERSONAL` | **FAIL** at layer 4 (Trader-17) |
| `mql5-permission --mode TEAM` | **FAIL** at layer 4 (fail-fast: L5–L7 not run) |
| `mql5-permission --mode ENTERPRISE` | **FAIL** at layer 4 (fail-fast: L5–L7 not run) |
| `mql5-matrix` (standalone, no evidence) | `0 / 64 PASS` — CLI floor, not a measurement |
| `mql5-rri-bt` (no `--report`) | `56 / 64 PASS` — structural maximum, not a measurement |

A bare scaffold is **expected to fail** the permission gate — the gate has
teeth and demands real evidence (working strategy + walk-forward + multi-broker
+ Monte Carlo + overfit check) before passing. See
[`docs/reference-ea/REPORT.md`](docs/reference-ea/REPORT.md) for the raw
outputs.

---

## 9. Tests and CI

```bash
# Full suite (Wine-independent on most systems)
pytest tests/ -q
# Expected: 169 passed, 2 skipped

# Single phase
pytest tests/gates/phase-A -q

# Single test file
pytest tests/gates/phase-F/test_prompt_architect_acceptance.py -q
```

`tests/gates/phase-*` are acceptance tests for the kit's own development
milestones. They are **not** user-facing — agents should not rely on their
existence as a stable feature surface. Treat them as regression tests.

---

## 10. Conventions for agent-authored changes

- **Lint and typecheck before opening a PR.** The toolchain uses `ruff`
  (`ruff check scripts/ tests/`) and Python ≥ 3.10 type hints.
- **No new top-level CLIs without maintainer sign-off.** The CLI surface is
  intentionally large already; adding more without removing equivalents
  worsens the agent UX.
- **No silent rule bypass.** If a check is wrong, fix the rule via PR.
- **Honest reporting.** When a number is a default / structural maximum / not
  an actual measurement, say so in the same paragraph it appears in.
- **MQL5 code stays inside scaffolds, `Include/`, and generated EAs.** Do not
  inline-author MQL5 in Python strings.
- **Prefer JSON output in shell pipelines.** Pass `--json` and parse the
  fields documented in section 5.

---

## 11. Useful one-liners

```bash
# Discover scaffolds
mql5-build --list

# Generate an EA and lint it in one shot
mql5-build --preset stdlib --stack netting --name MyEA --output ./out/ \
  && mql5-lint ./out/MyEA/MyEA.mq5

# Run permission gate, machine-readable
mql5-permission --ea ./out/MyEA/MyEA.mq5 --mode TEAM --json | jq

# Regenerate the honest reference-EA report
bash scripts/tools/build_reference_report.sh
```

---

## 12. Where to look for context

| Topic | File |
|---|---|
| Human-friendly quickstart (EN) | `docs/QUICKSTART.md` |
| Quickstart in Vietnamese | `docs/QUICKSTART.vi.md` |
| Full user guide | `docs/GUIDE-COMPLETE.md` |
| Anti-pattern explanations | `docs/GUIDE-BUILD-EA.md` (table at AP-01..AP-21) |
| Pip normalization rationale | `docs/references/79-pip-norm.md` |
| Trader-17 details | `docs/references/59-trader-checklist.md` |
| Prompt Architect schema | `docs/prompt-architect/ea-settings.schema.json` |
| Internal sprint specs (contributors only) | `docs/PLAN-v5.md`, `docs/phase-*-spec.md` |

When the user asks "what does this kit do?", point them at
[`README.md`](README.md) and [`docs/QUICKSTART.md`](docs/QUICKSTART.md), not at
the phase specs.
