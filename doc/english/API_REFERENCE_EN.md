# API Reference — llmpic

> Complete reference for all classes, methods, parameters, and return types.

---

## Table of Contents

- [llmPIC (Sync SDK)](#llmpic-sync-sdk)
- [AsyncllmPIC (Async SDK)](#asyncllmpic-async-sdk)
- [PlotBuilder (Sync Builder)](#plotbuilder-sync-builder)
- [AsyncPlotBuilder (Async Builder)](#asyncplotbuilder-async-builder)
- [ChartResult (Result Object)](#chartresult-result-object)
- [SandboxExecutor](#sandboxexecutor)
- [CodeSafetyChecker](#codesafetychecker)
- [Config Constants](#config-constants)
- [Common Patterns](#common-patterns)

---

## llmPIC (Sync SDK)

`llmPIC` is the main entry point for synchronous chart generation. It manages the LLM client, safety checker, and sandbox executor.

### Constructor

```python
llmPIC(
    api_key: str,
    base_url: str,
    model: str = "gpt-4o",
    *,
    safety_model: str | None = None,
    safety_level: str = "fast",
    chinese_font: bool = True,
    timeout: int = 30,
    dpi: int = 150,
    output_dir: str = "~/llmpic_charts",
    temperature: float = 0.3,
    max_tokens: int = 2048,
    structured_output: bool = True,
    max_retries: int = 3,
    max_fix_attempts: int = 2,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | **required** | OpenAI-compatible API key. Use `"ollama"` or `"not-needed"` for local endpoints. |
| `base_url` | `str` | **required** | API endpoint URL. Must end with the path prefix (e.g., `.../v1`). |
| `model` | `str` | `"gpt-4o"` | Model name for code generation. Must support JSON structured output for best results. |
| `safety_model` | `str \| None` | `None` | Model for LLM safety review. Defaults to `model` when `None`. Only used when `safety_level="full"`. |
| `safety_level` | `str` | `"fast"` | `"fast"` — regex only (~0ms). `"full"` — regex + LLM semantic review (~1-2s extra). |
| `chinese_font` | `bool` | `True` | Auto-detect and configure CJK fonts. Set `False` for English-only charts (slightly faster startup). |
| `timeout` | `int` | `30` | Code execution timeout in seconds. Complex dashboards may need 60+. |
| `dpi` | `int` | `150` | Default output resolution. Override per-chart via `.style({"dpi": ...})`. |
| `output_dir` | `str` | `"~/llmpic_charts"` | Default save directory when `save()` is called without a path. Supports `~` (home directory), relative, and absolute paths. |
| `temperature` | `float` | `0.3` | LLM sampling temperature (0–2). Lower = more deterministic, higher = more varied. |
| `max_tokens` | `int` | `2048` | Maximum output tokens. Increase for complex dashboards (e.g., 4096). |
| `structured_output` | `bool` | `True` | Use `response_format={"type": "json_object"}` for reliable code extraction. Disable for models without JSON mode support. |
| `max_retries` | `int` | `3` | LLM call retries with exponential backoff: 1s → 2s → 4s. Includes both transient API errors and unparseable responses. |
| `max_fix_attempts` | `int` | `2` | Auto-fix rounds when code execution fails. Each fix sends the error + code back to the LLM. Set to `0` to disable. |

### Chart Type Methods

All chart methods return a `PlotBuilder` for fluent chaining. Nothing runs until `.render()`, `.save()`, or accessing `.image_bytes` / `.code`.

```python
plot(query: str)      -> PlotBuilder   # Line chart
scatter(query: str)   -> PlotBuilder   # Scatter chart
bar(query: str)       -> PlotBuilder   # Bar chart (vertical or horizontal)
pie(query: str)       -> PlotBuilder   # Pie chart (or donut)
hist(query: str)      -> PlotBuilder   # Histogram
heatmap(query: str)   -> PlotBuilder   # Heatmap
boxplot(query: str)   -> PlotBuilder   # Boxplot
area(query: str)      -> PlotBuilder   # Area chart
radar(query: str)     -> PlotBuilder   # Radar / spider chart
subplots(query: str)  -> PlotBuilder   # Multi-chart dashboard
custom(query: str)    -> PlotBuilder   # Auto-detect best chart type
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | Natural language chart description. Supports English, Chinese, Japanese, Korean. |

**Example:**

```python
lp = llmPIC(api_key="sk-...", base_url="https://api.openai.com/v1")

# Each returns a PlotBuilder — nothing runs yet
builder = lp.plot("Monthly sales trend")   # PlotBuilder
builder = lp.bar("Revenue by region")      # PlotBuilder
builder = lp.custom("Auto-detect best")    # PlotBuilder

# Trigger generation
result = builder.render()
```

### Internal Methods (not part of public API)

| Method | Signature | Purpose |
|--------|-----------|---------|
| `_generate_code` | `(user_prompt: str, system_prompt: str = None) -> Tuple[Optional[str], dict]` | Calls LLM, retries on failure, returns (code, token_usage) |
| `_fix_code` | `(code: str, error: str, query: str) -> Tuple[Optional[str], dict]` | Asks LLM to fix failed code |

---

## AsyncllmPIC (Async SDK)

Async counterpart of `llmPIC`. Identical constructor and chart type methods, plus `batch()` for concurrent generation.

### Constructor

Identical parameters to `llmPIC`. Uses `AsyncOpenAI` client internally.

```python
AsyncllmPIC(
    api_key: str,
    base_url: str,
    model: str = "gpt-4o",
    *,
    safety_model: str | None = None,
    safety_level: str = "fast",
    chinese_font: bool = True,
    timeout: int = 30,
    dpi: int = 150,
    output_dir: str = "~/llmpic_charts",
    temperature: float = 0.3,
    max_tokens: int = 2048,
    structured_output: bool = True,
    max_retries: int = 3,
    max_fix_attempts: int = 2,
)
```

### Chart Type Methods

Same 11 methods as `llmPIC`, each returning an `AsyncPlotBuilder`. Key methods require `await`.

```python
lp = AsyncllmPIC(api_key="sk-...", base_url="...")

builder = lp.plot("CPU trend")     # AsyncPlotBuilder — NOTHING runs yet
result = await builder.render()     # ← triggers generation
```

### async batch()

```python
async def batch(
    self,
    requests: List[Tuple[str, str]]
) -> List[ChartResult]
```

Generates multiple charts concurrently using `asyncio.gather`. Total time ≈ the slowest single chart.

| Parameter | Type | Description |
|-----------|------|-------------|
| `requests` | `List[Tuple[str, str]]` | List of `(chart_type, query)` pairs |

**Valid chart_type values:**
`"line"` `"scatter"` `"bar"` `"pie"` `"hist"` `"heatmap"` `"boxplot"` `"area"` `"radar"` `"subplots"` `"custom"`

**Returns:** `List[ChartResult]` in the same order as the input requests.

**Example:**

```python
async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="https://api.openai.com/v1")

    results = await lp.batch([
        ("plot", "12-month sales trend"),
        ("bar", "Revenue by department"),
        ("scatter", "User behavior correlation"),
    ])

    for i, r in enumerate(results):
        if r.success:
            r.save(f"batch_{i}.png")

asyncio.run(main())
```

**Note:** `batch()` uses default style and does not support per-chart data attachments. For per-chart customization, use builders with `asyncio.gather()` directly (see User Guide).

---

## PlotBuilder (Sync Builder)

Fluent builder returned by all `llmPIC` chart methods. **Lazy execution** — no LLM call, safety check, or sandbox execution occurs until `.render()`, `.save()`, or accessing `.image_bytes` / `.code`.

### Constructor (not called directly)

```python
# Created by llmPIC chart methods:
builder = lp.plot("query")   # Returns PlotBuilder
```

### .data(data) → PlotBuilder

Attach data for the chart. When not called, the LLM generates realistic demo data using numpy.

```python
def data(self, data) -> PlotBuilder
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `pandas.DataFrame` \| `pandas.Series` \| `numpy.ndarray` \| `dict` \| `list` \| `tuple` \| `str` | Chart data. Serialized and passed to LLM as context (not sent as raw bytes). |

**Data serialization behavior:**

| Input Type | What the LLM receives |
|------------|----------------------|
| `DataFrame` | Shape, column names, dtypes, first 5 rows, statistical summary (if >5 rows) |
| `Series` | Name, dtype, first 10 values |
| `ndarray` (1D) | Shape, dtype, first 10 elements |
| `ndarray` (ND) | Shape, dtype, first 5 rows |
| `dict` | Keys list + values (truncated to 150 chars each) |
| `list` / `tuple` | Length + first 15 elements |
| `str` | Raw text, truncated to 2000 characters |

### .style(style_spec) → PlotBuilder

Set visual style. Merged on top of `DEFAULT_STYLE` (see Config Constants).

```python
def style(self, style_spec: dict | str) -> PlotBuilder
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `style_spec` | `dict` or `str` (JSON) | Style configuration dictionary or JSON string |

**Supported style keys:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `figsize` | `[int, int]` | `[10, 6]` | Figure size in inches: `[width, height]` |
| `dpi` | `int` | `150` | Output resolution (dots per inch) |
| `color_scheme` | `str` | `"blues"` | One of: `"blues"`, `"warm"`, `"cool"`, `"pastel"`, `"dark"`, `"grayscale"` |
| `title_fontsize` | `int` | `14` | Chart title font size in points |
| `label_fontsize` | `int` | `12` | Axis label font size in points |
| `tick_fontsize` | `int` | `10` | Tick mark label font size in points |
| `grid` | `bool` | `True` | Show background grid lines |
| `grid_alpha` | `float` | `0.3` | Grid line transparency (0 = invisible, 1 = opaque) |
| `tight_layout` | `bool` | `True` | Apply `bbox_inches='tight'` when rendering |
| `facecolor` | `str` | `"white"` | Figure background color (any CSS color name or hex) |

### .format(fmt) → PlotBuilder

Set output format for rendering.

```python
def format(self, fmt: str) -> PlotBuilder
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `fmt` | `str` | `"png"`, `"svg"`, or `"pdf"`. Raises `ValueError` for invalid values. |

### .render() → ChartResult

Trigger chart generation. This is where everything runs:
1. Build user prompt → call LLM (with retries)
2. Safety check (regex + optional LLM)
3. Sandbox execution (with auto-fix on failure)

```python
def render(self) -> ChartResult
```

Calling `.render()` multiple times returns the cached result — it doesn't re-run the pipeline. To force re-generation, call `.data()`, `.style()`, or `.format()` first (which invalidate the cache).

### .save(path: str = None) → str

Convenience: calls `.render()` then `.save()` on the result.

```python
def save(self, path: str = None) -> str
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` or `None` | File path. Format auto-detected from extension (.png/.svg/.pdf). If `None`, saves to `output_dir/chart_{timestamp}.png`. |

**Returns:** The absolute path where the file was saved.

### .image_bytes (property) → bytes

Triggers generation, returns the primary format image bytes.

```python
@property
def image_bytes(self) -> bytes
```

### .code (property) → str

Triggers generation, returns the matplotlib code the LLM wrote.

```python
@property
def code(self) -> str
```

---

## AsyncPlotBuilder (Async Builder)

Async version of `PlotBuilder`. Same builder API, but `render()` and `save()` are async coroutines.

| Method | Requires `await` | Signature |
|--------|-----------------|-----------|
| `.data(data)` | No | `(data) -> AsyncPlotBuilder` |
| `.style(spec)` | No | `(style_spec: dict \| str) -> AsyncPlotBuilder` |
| `.format(fmt)` | No | `(fmt: str) -> AsyncPlotBuilder` |
| `await .render()` | **Yes** | `async () -> ChartResult` |
| `await .save(path=None)` | **Yes** | `async (path: str = None) -> str` |

**Example:**

```python
async def main():
    lp = AsyncllmPIC(...)
    result = await lp.plot("CPU trend").data(df).style({"color_scheme":"warm"}).render()
    result.show()

asyncio.run(main())
```

---

## ChartResult (Result Object)

Encapsulates a completed chart generation. Returned by `PlotBuilder.render()` and `AsyncPlotBuilder.render()`.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `success` | `bool` | Whether chart generation succeeded |
| `image_bytes` | `bytes \| None` | Primary format image bytes (default PNG). `None` if failed. |
| `error_message` | `str \| None` | Error description. `None` if successful. |
| `code` | `str \| None` | Generated matplotlib Python code. `None` if failed. |
| `token_usage` | `dict` | Token usage: `{"input": N, "output": M}`. Empty dict if failed. |
| `size_kb` | `float` | Image size in kilobytes. `0.0` if no image. |
| `svg_bytes` | `bytes` | SVG format bytes. Lazy — re-renders from stored code on first access, then cached. |
| `pdf_bytes` | `bytes` | PDF format bytes. Lazy — re-renders from stored code on first access, then cached. |
| `svg` | `str` | SVG as a UTF-8 string. Delegates to `svg_bytes.decode('utf-8')`. |

**Note about lazy format properties:** `svg_bytes` and `pdf_bytes` work by re-executing the stored matplotlib code in the sandbox with a different format. This means:
- They're available even if the original render was PNG
- They require the `ChartResult` to have been created by an SDK instance (needs `_sdk` reference)
- Results are cached after first access — subsequent accesses return instantly

### Methods

#### .save(path: str = None) → str

Save chart to file. Format auto-detected from extension.

```python
def save(self, path: str = None) -> str
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str \| None` | Output file path. If `None`, saves to `~/llmpic_charts/chart_{YYYYMMDD_HHMMSS}.png`. |

| Extension | Format | How it works |
|-----------|--------|-------------|
| `.png` | PNG | Uses `image_bytes` directly |
| `.svg` | SVG | Uses `svg_bytes` (lazy re-render) |
| `.pdf` | PDF | Uses `pdf_bytes` (lazy re-render) |

**Returns:** The absolute path where the file was saved.

**Raises:** `RuntimeError` if `success` is `False`.

```python
result.save()                        # → ~/llmpic_charts/chart_20250101_120000.png
result.save("chart.png")             # PNG
result.save("chart.svg")             # SVG (lazy re-render if original was PNG)
result.save("chart.pdf")             # PDF (lazy re-render if original was PNG)
result.save("/abs/path/chart.png")   # Absolute path
```

#### .show()

Display chart inline in Jupyter Notebook or IPython.

```python
def show(self) -> None
```

- In Jupyter/IPython: renders the chart directly below the cell
- In plain Python: logs a warning (no error raised)
- Supports PNG, SVG, and PDF formats
- Raises `RuntimeError` if `success` is `False`

```python
result = lp.plot("CPU trend").render()
result.show()  # Appears below the cell in Jupyter
```

#### .base64() → str

Returns PNG as a base64 data URI.

```python
def base64(self) -> str
```

Returns: `"data:image/png;base64,{base64_encoded_bytes}"`

Use for embedding in HTML, Markdown, or APIs:
```html
<img src="{result.base64()}" />
```

#### .base64_svg() → str

Returns SVG as a base64 data URI.

```python
def base64_svg(self) -> str
```

Returns: `"data:image/svg+xml;base64,{base64_encoded_bytes}"`

#### .edit(edit_query: str) → ChartResult

Modify the chart using natural language. Returns a **new** `ChartResult` — the original is never mutated.

```python
def edit(self, edit_query: str) -> ChartResult
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `edit_query` | `str` | Natural language edit description. Examples: `"make bars red"`, `"change to line chart, add grid"`, `"increase title size to 18, use warm colors"` |

**Returns:** A new `ChartResult` with the modified chart.

**Pipeline:** Sends current code + edit request → LLM returns modified code → safety check → sandbox execution → new ChartResult.

**Requirements:**
- The `ChartResult` must have `success == True`
- The `ChartResult` must have been created by an SDK instance (has `_sdk` reference)

**Example:**

```python
v1 = lp.plot("Monthly sales: Jan=100").render()

# Edit never mutates v1
v2 = v1.edit("Change to bar chart, red color")
v3 = v2.edit("Title 'Q1 Report', add grid")
v4 = v3.edit("Increase title size to 18")

v4.save("final.png")

# v1, v2, v3 still available if you need to backtrack
v1.save("v1_original.png")
```

#### .__repr__() → str

```python
def __repr__(self) -> str
```

Returns:
- Success: `"ChartResult(ok, {size_kb:.1f}KB, {format})"`
- Failure: `"ChartResult(fail, {error_message!r})"`

---

## SandboxExecutor

Executes matplotlib code in a restricted sandboxed environment. Used internally by `llmPIC` — most users won't interact with this class directly.

### Constructor

```python
SandboxExecutor(
    chinese_font: bool = True,
    timeout: int = 30,
    dpi: int = 150,
    output_dir: str = "~/llmpic_charts",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `chinese_font` | `bool` | `True` | Enable CJK font auto-detection on construction |
| `timeout` | `int` | `30` | Code execution timeout in seconds |
| `dpi` | `int` | `150` | Default rendering DPI |
| `output_dir` | `str` | `"~/llmpic_charts"` | Output directory (created if not exists) |

### execute()

```python
def execute(
    self,
    code: str,
    style: dict = None,
    format: str = 'png',
) -> Tuple[bytes | None, str | None]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `code` | `str` | **required** | Matplotlib Python code to execute |
| `style` | `dict` | `{}` | Style dictionary (figsize, dpi, facecolor, tight_layout) |
| `format` | `str` | `"png"` | Output format: `"png"`, `"svg"`, or `"pdf"` |

**Returns:** `(image_bytes, error_message)` tuple. Exactly one will be `None`.

### Sandbox Guarantees

The sandbox provides the following guarantees:

1. **Restricted namespace** — only safe builtins + `mpl` (matplotlib), `plt` (proxied), `np` (numpy), `pd` (pandas, if available), `sns` (seaborn, if available), `Figure`
2. **plt interception** — `plt.show()`, `plt.savefig()`, `plt.close()` are all no-ops
3. **Figure.savefig intercepted** — code cannot write files directly; the sandbox handles rendering
4. **Figure.__init__ tracked** — the sandbox detects which figure was created by the code
5. **Timeout fuse** — execution runs in a `ThreadPoolExecutor` with configurable timeout
6. **Serialization lock** — module-level `threading.Lock` prevents matplotlib state races between concurrent executions
7. **Font caching** — CJK font detection runs once at module level and is cached

### Internal Architecture (for understanding, not usage)

```
execute()
  │
  ├─ _ensure_font()           ← Module-level, cached
  │
  ├─ _execl_lock (mutex)      ← Prevents matplotlib races
  │
  └─ _execute()               ← ThreadPoolExecutor + timeout
       │
       ├─ Monkey-patch Figure.__init__ / Figure.savefig
       ├─ Build safe namespace
       ├─ exec(code, namespace)         ← In thread pool
       ├─ Detect created figure
       ├─ Render via original Figure.savefig
       └─ Restore Figure patches
```

---

## CodeSafetyChecker

Dual-layer code safety verification. Used internally by `llmPIC` — most users won't interact with this class directly.

### Constructor

```python
CodeSafetyChecker(
    client: OpenAI,
    model: str,
    level: str = "fast",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `client` | `OpenAI` | **required** | OpenAI client instance (used for LLM review in `full` mode) |
| `model` | `str` | **required** | Model name for LLM safety review |
| `level` | `str` | `"fast"` | `"fast"` — regex only. `"full"` — regex + LLM semantic review. |

### check()

```python
def check(
    self,
    code: str,
    llm_review: bool = None,
) -> Tuple[bool, str]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `code` | `str` | **required** | Python code to check |
| `llm_review` | `bool \| None` | `None` | Override the safety level: `True` = LLM review, `False` = regex only, `None` = use instance default |

**Returns:** `(is_safe: bool, reason: str)`
- `(True, "")` — code passes all checks
- `(False, "Forbidden operations:\n  - os.system()\n  - ...")` — regex violations found
- `(False, "LLM review: code attempts to access files")` — LLM review flagged the code

### regex_check()

```python
def regex_check(self, code: str) -> List[str]
```

**Returns:** List of violation labels (empty list = safe).

32 precompiled patterns covering:

| Category | Violation Labels |
|----------|-----------------|
| System commands | `os.system()`, `os.popen()`, `os.exec*()`, `os.spawn*()`, `subprocess` |
| File operations | `os.remove()`, `os.unlink()`, `os.rmdir()`, `os.rename()`, `os.mkdir/makedirs()`, `os.chmod()`, `os.environ`, `open()` |
| Dynamic execution | `exec()`, `eval()`, `compile()`, `__import__()` |
| Network access | `socket`, `urllib`, `requests`, `httpx`, `curl` |
| Process exit | `sys.exit()` |
| Dangerous modules | `shutil`, `ctypes`, `pickle` |
| Reflection escapes | `setattr()`, `delattr()`, `__subclasses__`, `__bases__`, `__mro__` |

### llm_review()

```python
def llm_review(self, code: str) -> Tuple[bool, str]
```

Sends the code (with comments stripped) to the LLM for semantic safety review. Uses `temperature=0` and JSON structured output.

**Returns:** `(is_safe: bool, reason: str)`

### _strip_comments() (static method)

```python
@staticmethod
def _strip_comments(code: str) -> str
```

Removes Python comments using `tokenize`, preserving string literals. Used before LLM review to prevent comment-based prompt injection.

---

## Config Constants

Available in `llmpic.templates`:

```python
from llmpic.templates import DEFAULT_STYLE, COLOR_SCHEMES, LANGUAGE_HINTS
```

### DEFAULT_STYLE

```python
DEFAULT_STYLE = {
    "figsize": [10, 6],
    "dpi": 150,
    "color_scheme": "blues",
    "title_fontsize": 14,
    "label_fontsize": 12,
    "tick_fontsize": 10,
    "grid": True,
    "grid_alpha": 0.3,
    "tight_layout": True,
    "facecolor": "white",
}
```

All keys can be overridden via `.style()`. Unspecified keys use these defaults.

### COLOR_SCHEMES

```python
COLOR_SCHEMES: dict[str, list[str]] = {
    "blues":     ["#3498DB", "#5DADE2", "#87CEEB", "#2980B9", "#AED6F1"],
    "warm":      ["#E74C3C", "#F39C12", "#E67E22", "#F1C40F", "#D35400"],
    "cool":      ["#1ABC9C", "#3498DB", "#9B59B6", "#2ECC71", "#16A085"],
    "pastel":    ["#FADBD8", "#D5F5E3", "#D6EAF8", "#F9E79F", "#E8DAEF"],
    "dark":      ["#2C3E50", "#34495E", "#7F8C8D", "#95A5A6", "#BDC3C7"],
    "grayscale": ["#333333", "#666666", "#999999", "#BBBBBB", "#DDDDDD"],
}
```

Each scheme has 5 colors. The LLM uses these as a palette for chart elements.

### LANGUAGE_HINTS

```python
LANGUAGE_HINTS = {
    'en': 'Use English for all labels and titles.',
    'zh': 'Use Simplified Chinese (简体中文) for all labels and titles.',
    'ja': 'Use Japanese (日本語) for all labels and titles.',
    'ko': 'Use Korean (한국어) for all labels and titles.',
}
```

Language is auto-detected from the query text by `detect_language()` in `templates.py`.

### detect_language()

```python
from llmpic.templates import detect_language

def detect_language(text: str) -> str
```

Returns one of: `'zh'`, `'ja'`, `'ko'`, `'en'`.

Detection logic:
- **`'zh'`**: CJK Unified Ideographs (U+4E00–U+9FFF) or Extension A (U+3400–U+4DBF)
- **`'ja'`**: Hiragana/Katakana (U+3040–U+30FF) or Katakana Extension (U+31F0–U+31FF)
- **`'ko'`**: Hangul Syllables (U+AC00–U+D7AF)
- **`'en'`**: Default (no CJK characters detected)

---

## Common Patterns

### Pattern 1: Quick One-Liner

```python
llmPIC(api_key="...", base_url="...").plot("Sales trend").save("chart.png")
```

### Pattern 2: Standard Workflow

```python
lp = llmPIC(api_key="...", base_url="...")

result = (lp.plot("Sales trend")
           .data(df)
           .style({"color_scheme": "warm", "dpi": 200})
           .render())

if result.success:
    result.save("chart.png")
    print(f"OK: {result.size_kb:.1f}KB")
else:
    print(f"Failed: {result.error_message}")
```

### Pattern 3: All Three Formats

```python
result = lp.bar("Revenue by region").data(df).render()

result.save("chart.png")   # PNG
result.save("chart.svg")   # SVG (lazy re-render)
result.save("chart.pdf")   # PDF (lazy re-render)
```

### Pattern 4: Inspect and Edit

```python
result = lp.plot("Sales").render()
print(result.code)  # See what the LLM wrote
print(result.token_usage)

# Iterative refinement
result = result.edit("Change to bar chart")
result = result.edit("Make bars red, title 'Q1 Revenue'")
result.save("final.png")
```

### Pattern 5: Error Handling

```python
result = lp.plot("Complex chart").data(df).render()

if not result.success:
    if "Safety rejected" in (result.error_message or ""):
        print("LLM generated unsafe code — try rephrasing")
    elif "timed out" in (result.error_message or ""):
        print("Chart too complex — increase timeout or simplify")
    elif "no code" in (result.error_message or ""):
        print("LLM didn't understand — be more specific or provide data")
    else:
        print(f"Unknown error: {result.error_message}")
```

### Pattern 6: Jupyter Workflow

```python
# Cell 1: Setup
from llmpic import llmPIC
lp = llmPIC(api_key="...", base_url="...")

# Cell 2: Quick exploration
lp.plot("Sales distribution").data(df).render().show()

# Cell 3: Refine
result = lp.plot("Sales distribution").data(df).render()
result = result.edit("Add KDE curve overlay, use dark scheme")
result.show()

# Cell 4: Export
result.save("final_distribution.png")
```

### Pattern 7: Async Batch with Logging

```python
import asyncio, logging
from llmpic import AsyncllmPIC

logging.basicConfig(level=logging.INFO)

async def main():
    lp = AsyncllmPIC(api_key="...", base_url="...")
    results = await lp.batch(requests)

    for i, r in enumerate(results):
        status = "OK" if r.success else "FAIL"
        print(f"[{i}] {status}: {r}")
        if r.success:
            r.save(f"out_{i}.png")

asyncio.run(main())
```

---

← [Back to Home](../../README.md)
