# Prompt Architect integration spec

Prompt Architect is the intake layer for `vibecodekit-mql5-ea`: it turns a trader's idea into a normalized EA configuration, then into RRI questions, requirements, blueprint, scaffold recommendation, and verification commands.

The core tool remains CLI-first and gate-driven. Prompt Architect must not bypass `mql5-lint`, `mql5-compile`, `mql5-permission`, or the 8×8 quality matrix.

## Non-goals

- Do not expose Gemini/OpenAI/API keys in browser bundles or committed files.
- Do not treat raw LLM-generated MQL5 as production-ready.
- Do not make the preview UI the source of truth; the schema and CLI are the source of truth.
- Do not replace deterministic gates with "mental simulation" or chat output.

## Data flow

```text
idea/chat/config
  -> ea-settings.schema.json
  -> feature-map.yaml
  -> conflict-rules.yaml
  -> RRI/persona questions
  -> vision.md + requirements.yaml
  -> blueprint.md
  -> preset-map.yaml recommendation
  -> mql5-build scaffold
  -> lint/compile/backtest/permission/matrix
```

## Files in this spec

| File | Purpose |
|---|---|
| `ea-settings.schema.json` | Canonical JSON schema for normalized EA configuration |
| `feature-map.yaml` | Mapping from user language and feature flags to normalized schema fields |
| `preset-map.yaml` | Mapping from strategy signals to existing scaffold presets/stacks |
| `conflict-rules.yaml` | Fail-closed validation rules for missing/conflicting requirements |
| `templates/` | Deterministic output templates for prompt, vision, requirements, blueprint, and optional codegen |

## Security boundary

LLM providers are optional adapters. Keys may only be read from server-side environment variables, Devin/org secrets, or local-only untracked files. Generated prompts, logs, examples, and reports must never include real provider keys, Telegram tokens, broker credentials, license secrets, or account identifiers.

## Required outputs

A valid Prompt Architect run should be able to produce:

- normalized `ea-settings.json`
- RRI checklist grouped by persona
- `vision.md`
- `requirements.yaml` with `REQ-*` traceability
- `blueprint.md`
- `pipeline.json` with recommended next CLI commands
- pipeline dry-run/execution summary for handoff into scaffold and gates
- recommended `mql5-build` preset/stack
- next verification commands
- optional LLM codegen prompt/response, gated by server-side provider credentials

## Definition of ready

A configuration is ready for implementation only when:

1. schema validation passes
2. no critical conflict rules fire
3. risk, execution, broker, and exit constraints are explicit
4. RRI critical questions for the selected mode are answered
5. a preset/stack is selected by recommendation or user override
6. generated scaffold passes the normal vibecodekit gates

## CLI target

The planned CLI is:

```bash
mql5-prompt-architect --config ea-settings.json --validate --json
mql5-prompt-architect --config ea-settings.json --render-prompt prompt.md
mql5-prompt-architect --config ea-settings.json --recommend-preset --json
mql5-prompt-architect --config ea-settings.json --rri-plan rri-plan.md --vision vision.md --requirements requirements.yaml --blueprint blueprint.md --pipeline pipeline.json
mql5-prompt-architect --config ea-settings.json --llm-provider prompt-only --llm-output codegen-prompt.md
mql5-prompt-architect --config ea-settings.json --llm-provider openai --llm-output draft.md
mql5-prompt-architect --run-pipeline pipeline.json
mql5-prompt-architect --run-pipeline pipeline.json --execute --from-step 1 --to-step 3
```

Provider-backed generation is optional. `prompt-only` never calls a network service. Cloud
providers read credentials only from server-side environment variables such as `OPENAI_API_KEY`
or `GEMINI_API_KEY`; provider keys must not be passed through browser bundles, generated prompts,
examples, logs, or committed files.
