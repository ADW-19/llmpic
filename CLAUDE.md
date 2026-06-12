# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

**llmpic** (v0.3.0, Python >= 3.10) is an LLM-powered chart generation SDK. Users describe charts in natural language (English/Chinese/Japanese/Korean) and llmpic produces matplotlib charts via OpenAI-compatible LLM endpoints. Package name on PyPI: `llmpic`.

## Common commands

```bash
# Editable install (dev) — [full] is optional; core deps already cover pandas/seaborn/scipy/scikit-learn
pip install -e .

# Build wheel + sdist
python -m build

# Documentation (from repo root)
mkdocs serve                    # serves at localhost:8000, hot-reloads doc/
mkdocs gh-deploy --force        # deploy to GitHub Pages (CI does this on push to main)

# Type stub generation (if needed)
pip install mypy && stubgen -o stubs -p llmpic
```

There is no test suite yet. Manual verification uses the two Jupyter notebooks in `notebook_examples/` (`llmpic_demo_en.ipynb`, `llmpic_demo_cn.ipynb`).

**Version bump checklist:** version is hardcoded in two places — `pyproject.toml` (`project.version`) and `src/llmpic/__init__.py` (`__version__`). Both must be updated together before a release tag.

## Architecture

Source lives under `src/llmpic/` (src-layout, discovered by `[tool.setuptools.packages.find] where = ["src"]` in pyproject.toml). Four modules, ~1,440 lines total:

| Module | Purpose |
|--------|---------|
| `core.py` | Public API: `llmPIC`, `AsyncllmPIC`, `PlotBuilder`, `AsyncPlotBuilder`, `ChartResult`. Also holds 4 shared stateless helpers: `_serialize_data()`, `_serialize_style()`, `_build_user_prompt()`, `_extract_code()`. |
| `safety.py` | `CodeSafetyChecker` — runs compiled regex patterns from `templates.COMPILED_FORBIDDEN` + optional LLM semantic review |
| `sandbox.py` | `SandboxExecutor` — restricted namespace execution with `ThreadPoolExecutor` timeout. Also holds module-level `_execl_lock`, font cache (`_font_lock`/`_font_configured`), and `_SafePlt` proxy. |
| `templates.py` | All prompts (`SYSTEM_PROMPT`, `FIX_PROMPT`, `EDIT_PROMPT`, `SAFETY_REVIEW_PROMPT`), color schemes, `DEFAULT_STYLE`, `CHART_TYPE_PROMPTS`, `LANGUAGE_HINTS`, language detection, and the 32 `COMPILED_FORBIDDEN` regex patterns (used by `safety.py`). |

**Pipeline per chart** (the core "loop"):
1. **LLM Code Gen** — `_build_user_prompt()` constructs a message from query + chart type hint + serialized data + style + language hint → LLM responds with JSON `{"code": "..."}` → `_extract_code()` parses it via 4-stage fallback:
   - Valid JSON parse → `data["code"]`
   - Truncated JSON regex (`"code"\s*:\s*"((?:[^"\\]|\\.)*)`) with JSON-escape restoration
   - Markdown fenced code block (`` ```python ... ``` ``)
   - Raw content (if it contains `plt.`/`ax.`/`fig,`)
2. **Safety Check** — `CodeSafetyChecker.check()` runs 32 precompiled regex patterns (defined in `templates.py`); if `safety_level="full"`, also sends code to LLM for semantic review (strips comments first via `tokenize`)
3. **Sandbox Execution** — `SandboxExecutor.execute()` monkey-patches `Figure.__init__` (to track created figures) and `Figure.savefig` (no-op), builds a restricted namespace (`_SAFE_BUILTINS` + proxied `plt`/`mpl`/`np`/`pd`/`sns`/`Figure`), runs via `ThreadPoolExecutor(max_workers=1)` with timeout, renders the resulting figure to bytes using the *original* (unpatched) `savefig`. Exceptions are caught and classified (SyntaxError, NameError, ValueError, TypeError, TimeoutError).
4. **Auto-Fix** — On execution failure, sends code + error back to LLM for correction (up to 2 rounds). Only the first 1200 chars of the error are sent to limit token usage.
5. **Result** — `ChartResult` wraps image bytes, generated code, token usage; supports lazy format re-render (SVG/PDF), `edit()` for iterative refinement, `show()` for Jupyter inline display, `base64()`/`base64_svg()` for web embedding

**Key design decisions:**
- `SandboxExecutor` serializes all executions under a **module-level `threading.Lock` (`_execl_lock`)** because it globally patches `Figure.__init__`/`Figure.savefig` — concurrent calls would race
- `plt.savefig()`/`plt.show()`/`plt.close()` are intercepted as no-ops via `_SafePlt` proxy (uses `__getattr__` to delegate everything else to real `plt`); generated code must NOT call them directly
- CJK font configuration is cached at module level (`_font_lock` + `_font_configured` flag) — runs once across all executor instances
- LLM calls use JSON structured output (`response_format={"type": "json_object"}`) by default; disable with `structured_output=False`
- Retry uses exponential backoff: 1s, 2s, 4s (up to `max_retries=3`)
- `ChartResult` is immutable-ish — `.edit()` returns a **new** `ChartResult` (never mutates originals); lazy format properties (`svg_bytes`, `pdf_bytes`) are cached after first access
- `AsyncllmPIC` runs sandbox execution via `loop.run_in_executor(None, ...)` to avoid blocking the event loop, but **safety checking is synchronous** (uses a sync `OpenAI` client) since it's not I/O-bound
- `AsyncllmPIC.batch()` fans out with `asyncio.gather()` — total time ≈ slowest chart, not sum of all charts
- `PlotBuilder.render()` caches the `ChartResult`; calling `render()` again returns the cached result. Mutating calls (`.data()`, `.style()`, `.format()`) invalidate the cache.
- The `[full]` extras in pyproject.toml are functionally identical to the base dependencies — pandas, seaborn, scipy, scikit-learn, cartopy are already listed in `dependencies`
- **Map support** (v0.3.0): `.map()` method generates geographic charts via `cartopy` (mandatory dependency). Uses PlateCarree projection with coastlines, borders, land/ocean shading. `DEFAULT_MAP_STYLE` provides stable, consistent defaults (PlateCarree projection, Blues colormap, fixed feature colors).

## CI/CD

Two GitHub Actions workflows in `.github/workflows/`:

- **publish.yml** — triggered by `v*` tag push → `python -m build` → PyPI via **trusted publishing** (OIDC, no API token). Single job, ubuntu-latest, Python 3.10.
- **mkdocs.yml** — triggered by push to `main` when `doc/**`, `mkdocs.yml`, or `official_web/**` change → `mkdocs gh-deploy --force` → GitHub Pages at `https://ADW-19.github.io/llmpic/`. Single job, ubuntu-latest, Python 3.10.

Both use `actions/setup-python@v5` with Python 3.10. The mkdocs workflow grants `contents: write` permission; the publish workflow grants `id-token: write`.

## Documentation system

- **MkDocs + Material for MkDocs** — config at `mkdocs.yml`, docs source in `doc/` (not a separate docs/ dir)
- `mkdocs.yml` sets `docs_dir: doc`, so all `.md` files in `doc/` are discovered
- Nav structure: Home → English (Getting Started, API Reference) → 中文文档 (使用指南, API 参考)
- Watch mode enabled — `mkdocs serve` hot-reloads on `doc/` changes
- Extra CSS: `official_web/stylesheets/extra.css`
