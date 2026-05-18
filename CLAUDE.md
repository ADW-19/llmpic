# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

**llmpic** (v0.2.1, Python >= 3.10) is an LLM-powered chart generation SDK. Users describe charts in natural language (English/Chinese/Japanese/Korean) and llmpic produces matplotlib charts via OpenAI-compatible LLM endpoints. Package name on PyPI: `llmpic`.

## Common commands

```bash
# Editable install (dev)
pip install -e ".[full]"

# Build wheel + sdist
python -m build

# Documentation (from repo root)
mkdocs serve                    # serves at localhost:8000, watches doc/

# Publish to PyPI (CI does this on tag push)
pip install build && python -m build
```

There is no test suite yet. Manual verification uses the two Jupyter notebooks in `notebook_examples/`.

## Architecture

Source lives under `src/llmpic/` (src-layout, discovered by `[tool.setuptools.packages.find] where = ["src"]` in pyproject.toml). Four modules, ~950 lines total:

| Module | Purpose |
|--------|---------|
| `core.py` | PII (public API): `llmPIC`, `AsyncllmPIC`, `PlotBuilder`, `AsyncPlotBuilder`, `ChartResult` |
| `safety.py` | `CodeSafetyChecker` — 32 compiled regex patterns + optional LLM semantic review |
| `sandbox.py` | `SandboxExecutor` — executes LLM-generated code in a restricted namespace with ThreadPoolExecutor timeout |
| `templates.py` | Prompts (`SYSTEM_PROMPT`, `FIX_PROMPT`, `EDIT_PROMPT`, `SAFETY_REVIEW_PROMPT`), color schemes, `DEFAULT_STYLE`, language detection, compiled regex list |

**Pipeline per chart** (the core "loop"):
1. **LLM Code Gen** — `_build_user_prompt()` constructs a message from query + chart type hint + serialized data + style → LLM responds with JSON `{"code": "..."}` → `_extract_code()` parses it (JSON → truncated JSON → markdown fence → raw fallback)
2. **Safety Check** — `CodeSafetyChecker.check()` runs 32 precompiled regex patterns; if `safety_level="full"`, also sends code to LLM for semantic review
3. **Sandbox Execution** — `SandboxExecutor.execute()` monkey-patches `Figure.__init__` (to track created figures) and `Figure.savefig` (no-op), builds a restricted namespace (`_SAFE_BUILTINS` + `plt`/`np`/`pd`/`sns`/`Figure`), runs via `ThreadPoolExecutor` with timeout, renders the resulting figure to bytes using the *original* (unpatched) `savefig`
4. **Auto-Fix** — On execution failure, sends code + error back to LLM for correction (up to 2 rounds)
5. **Result** — `ChartResult` wraps image bytes, generated code, token usage; supports lazy format re-render (SVG/PDF), `edit()` for iterative refinement, `show()` for Jupyter inline display, `base64()` for web embedding

**Key design decisions:**
- `SandboxExecutor` serializes all executions under a **module-level `threading.Lock`** because it globally patches `Figure.__init__`/`Figure.savefig` — concurrent calls would race
- `plt.savefig()`/`plt.show()`/`plt.close()` are intercepted as no-ops via `_SafePlt` proxy; generated code must NOT call them directly
- LLM calls use JSON structured output (`response_format={"type": "json_object"}`) by default
- Retry uses exponential backoff: 1s, 2s, 4s (up to `max_retries=3`)
- `ChartResult` is immutable-ish — `.edit()` returns a **new** `ChartResult` (never mutates originals)

## CI/CD

- **GitHub Actions** (`.github/workflows/publish.yml`): push of `v*` tag → `python -m build` → PyPI via trusted publishing (OIDC, no token). Single job on ubuntu-latest, Python 3.10.

## Documentation system

- **MkDocs + Material for MkDocs** — config at `mkdocs.yml`, docs source in `doc/` (not a separate docs/ dir)
- `mkdocs.yml` sets `docs_dir: doc`, so all `.md` files in `doc/` are discovered
- Nav structure: Home → English (Getting Started, API Reference) → 中文文档 (使用指南, API 参考)
- Watch mode enabled — `mkdocs serve` hot-reloads on `doc/` changes
- Extra CSS: `official_web/stylesheets/extra.css`
