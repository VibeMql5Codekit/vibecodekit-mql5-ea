---
name: testing-preview-site
description: Test the vibecodekit-mql5-ea preview site and CLI tools end-to-end. Use when verifying preview site UI, scaffold generator, lint checker, Prompt Architect demo, mobile layout, or CLI count changes.
---

# Testing vibecodekit-mql5-ea Preview Site

## Prerequisites

- Repo cloned at `/home/ubuntu/repos/vibecodekit-mql5-ea`.
- Install local CLI dependencies if needed: `pip install -e ".[dev]"`.
- Preview site deployed as static HTML with `deploy frontend` from the `preview/` directory.
- For browser testing, use the existing Chrome session; for scripted checks, connect Playwright to CDP at `http://localhost:29229`.

## Devin Secrets Needed

None. The preview site is public static HTML and deterministic Prompt Architect demo does not call external providers.

## Preview URL and cache

Use the current deployed preview URL from the deployment output or PR comments. Append `?nocache=<unique-label>` after preview deploys to avoid stale CDN content.

Before browser testing, verify the deployed HTML contains current markers:

```bash
python - <<'PY'
from urllib.request import urlopen
url = '<PREVIEW_URL>?nocache=<unique>'
body = urlopen(url, timeout=20).read().decode('utf-8', errors='replace')
for token in ['169', '46 Python CLI tools', 'Prompt Architect', 'runPromptArchitectDemo', 'flex-wrap']:
    print(token, token in body)
PY
```

## Browser Recording Setup

Maximize browser before recording:

```bash
sudo apt-get install -y wmctrl 2>/dev/null
wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz
```

Record UI testing and annotate major assertions.

## Core Preview Assertions

### Overview tab

1. Open `<PREVIEW_URL>?nocache=<unique>`.
2. Verify stats show exactly:
   - `169` under Tests Passing / Tests đạt.
   - `46` under CLI Commands / Lệnh CLI.
3. Verify Prompt Architect appears as a card and is marked `NEW`.
4. Fail if stale values such as `150`, `44`, or `45 CLI tools` appear in the primary current-count areas.

### CLI tab

1. Click `CLI Tools` / `Công cụ CLI`.
2. Verify intro text contains `46 Python CLI tools`.
3. Verify card `mql5-prompt-architect` is visible and marked `NEW`.

### Tests tab

1. Click `Tests` / `Kiểm thử`.
2. Verify summary contains `169 passed, 2 skipped, 0 failed` or the Vietnamese equivalent.
3. Verify table contains `Phase F: Prompt Architect`, `17 pass`, and coverage including `pipeline runner` and `LLM provider adapter`.

## Try It Demo Assertions

### Scaffold Generator

1. Click `Try It` / `Thử ngay`.
2. Type an EA name such as `DevinPhaseFProbe`.
3. Click `Generate Scaffold` / `Tạo Scaffold`.
4. Verify output contains:
   - `<EAName>.mq5`
   - `#include "CPipNormalizer.mqh"`
   - `#include "CRiskGuard.mqh"`

### Lint Checker

1. Use the default violation sample.
2. Click `Run Lint Check` / `Chạy Lint`.
3. Verify output contains:
   - `[X] AP-01`
   - `[X] AP-15`
   - `[X] AP-20`
   - `3 critical, 0 warnings`

### Prompt Architect Demo

1. Click `Run Prompt Architect Demo` / `Chạy Prompt Architect Demo`.
2. Verify JSON output contains:
   - `"recommendation": "dca/hedging"`
   - `"mode": "ENTERPRISE"`
   - Six artifacts: `prompt.md`, `vision.md`, `requirements.json`, `blueprint.md`, `rri-plan.md`, `pipeline.json`
   - Seven pipeline labels, including `validate config`, `generate scaffold`, `lint scaffold`, and `human approval before deploy`
   - `OpenAI/Gemini keys read only from server-side env; prompt-only requires no key`

## Bilingual (VI/EN) Testing

- Click `EN`; verify header/nav and Try It labels switch to English.
- Click `VI`; verify labels switch back to Vietnamese.
- Pay attention to nav buttons because missing `i18n` class on nav items is a common regression.

## Mobile Responsive Testing

### UI check

1. Resize Chrome to a narrow mobile-like size, around 375×812.
2. Verify nav buttons wrap onto multiple rows instead of clipping or requiring horizontal page scroll.
3. Verify `Try It` remains reachable by clicking the wrapped button.

### Programmatic overflow check

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:29229")
        page = browser.contexts[0].pages[0]
        await page.goto("<PREVIEW_URL>?nocache=<unique>")
        await page.set_viewport_size({"width": 375, "height": 812})
        await page.wait_for_timeout(500)
        result = await page.evaluate("""() => ({
            innerWidth: window.innerWidth,
            bodyScrollWidth: document.body.scrollWidth,
            htmlScrollWidth: document.documentElement.scrollWidth,
            hasHorizontalScroll: document.body.scrollWidth > document.body.clientWidth ||
                document.documentElement.scrollWidth > document.documentElement.clientWidth,
            activeSection: document.querySelector('section.active')?.id,
            navButtons: [...document.querySelectorAll('nav button')].map(b => b.textContent.trim())
        })""")
        print(result)
        # Expected: hasHorizontalScroll is false and navButtons includes Try It / Thử ngay.

asyncio.run(main())
```

If the browser chrome prevents exactly 375px `window.innerWidth`, still verify the effective width and `hasHorizontalScroll=false` in the result.

## CLI Regression Checks for Preview Claims

Run shell tests when preview copy advertises runtime counts:

```bash
cd /home/ubuntu/repos/vibecodekit-mql5-ea
pytest tests/ -q
# Expected locally: 169 passed, 2 skipped when Wine/MetaEditor smoke deps are unavailable

python - <<'PY'
import tomllib
with open('pyproject.toml', 'rb') as f:
    cfg = tomllib.load(f)
print(len(cfg['project']['scripts']))
PY
# Expected: 46
```

## Common Issues

- The 2 skipped tests require Wine + MetaEditor and are expected on Linux when smoke deps are unavailable.
- The preview site is purely client-side JS — no backend or API calls.
- Use `?nocache=<unique>` after every static preview deployment.
- If mobile nav overflows, check the media query for `nav .container` includes `flex-wrap: wrap`, `justify-content: center`, and `overflow-x: visible`.
- Long `<pre>` blocks can create horizontal overflow; containers should have `min-width: 0`/overflow handling and tables should use `.table-wrap`.
- New repos may have no GitHub Actions; Devin Review can still report as an optional check.
