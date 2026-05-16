# API Reference — llmpic

> Complete reference for all classes, methods, and parameters.

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

---

## llmPIC (Sync SDK)

Main entry point for synchronous chart generation.

### Constructor

```python
llmPIC(
    api_key: str,
    base_url: str,
    model: str = "gpt-4o",
    *,
    safety_model: str = None,
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
| `api_key` | `str` | **required** | OpenAI-compatible API key |
| `base_url` | `str` | **required** | API endpoint, e.g. `https://api.openai.com/v1` |
| `model` | `str` | `"gpt-4o"` | Model for code generation |
| `safety_model` | `str` | `None` | Model for safety review (defaults to `model`) |
| `safety_level` | `str` | `"fast"` | Safety level: `"fast"` regex only, `"full"` regex + LLM |
| `chinese_font` | `bool` | `True` | Enable CJK font support |
| `timeout` | `int` | `30` | Code execution timeout in seconds |
| `dpi` | `int` | `150` | Default output DPI |
| `output_dir` | `str` | `"~/llmpic_charts"` | Default output directory (home dir, supports relative/absolute) |
| `temperature` | `float` | `0.3` | LLM generation temperature (0–2) |
| `max_tokens` | `int` | `2048` | Max output tokens from LLM |
| `structured_output` | `bool` | `True` | Use JSON structured output mode |
| `max_retries` | `int` | `3` | LLM call retries with exponential backoff (1s, 2s, 4s) |
| `max_fix_attempts` | `int` | `2` | Auto-fix attempts on code execution failure |

### Chart Type Methods

All return a `PlotBuilder` for fluent chaining.

| Method | Returns | Description |
|--------|---------|-------------|
| `.plot(query)` | `PlotBuilder` | Line chart |
| `.scatter(query)` | `PlotBuilder` | Scatter chart |
| `.bar(query)` | `PlotBuilder` | Bar chart |
| `.pie(query)` | `PlotBuilder` | Pie chart |
| `.hist(query)` | `PlotBuilder` | Histogram |
| `.heatmap(query)` | `PlotBuilder` | Heatmap |
| `.boxplot(query)` | `PlotBuilder` | Boxplot |
| `.area(query)` | `PlotBuilder` | Area chart |
| `.radar(query)` | `PlotBuilder` | Radar chart |
| `.subplots(query)` | `PlotBuilder` | Subplots dashboard |
| `.custom(query)` | `PlotBuilder` | Auto-detect best type |

Parameter `query: str` — natural language chart description.

---

## AsyncllmPIC (Async SDK)

Async counterpart. Same constructor parameters as `llmPIC`, plus batch generation.

### Constructor

Identical parameters to `llmPIC`.

### Chart Type Methods

Same 11 methods as `llmPIC`, returning `AsyncPlotBuilder`.

### async batch()

```python
async def batch(
    requests: List[Tuple[str, str]]
) -> List[ChartResult]
```

Generates multiple charts concurrently.

| Parameter | Type | Description |
|-----------|------|-------------|
| `requests` | `List[Tuple[str, str]]` | Pairs of `(chart_type, query)` |

Chart types: `"line"` `"scatter"` `"bar"` `"pie"` `"hist"` `"heatmap"` `"boxplot"` `"area"` `"radar"` `"subplots"` `"custom"`

Returns: `List[ChartResult]` in the same order as requests.

```python
results = await lp.batch([
    ("plot", "CPU trend"),
    ("bar", "Sales by region"),
    ("scatter", "Correlation analysis"),
])
```

---

## PlotBuilder (Sync Builder)

Fluent builder. **Lazy**: nothing runs until `.render()` / `.save()` or accessing `.image_bytes` / `.code`.

### Methods

#### .data(data)

Attach data for the chart.

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `DataFrame` / `ndarray` / `dict` / `list` / `str` | Chart data. If not called, LLM generates demo data. |

#### .style(style_spec)

Set visual style.

| Parameter | Type | Description |
|-----------|------|-------------|
| `style_spec` | `dict` or `str` (JSON) | Style configuration |

**Supported style keys:**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `figsize` | `[int, int]` | `[10, 6]` | Figure size (inches) |
| `dpi` | `int` | `150` | Output resolution |
| `color_scheme` | `str` | `"blues"` | Color scheme: `blues` `warm` `cool` `pastel` `dark` `grayscale` |
| `title_fontsize` | `int` | `14` | Title font size |
| `label_fontsize` | `int` | `12` | Axis label font size |
| `tick_fontsize` | `int` | `10` | Tick label font size |
| `grid` | `bool` | `True` | Show grid |
| `grid_alpha` | `float` | `0.3` | Grid line transparency |
| `tight_layout` | `bool` | `True` | Use tight layout |
| `facecolor` | `str` | `"white"` | Figure background |

#### .format(fmt)

Set output format.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fmt` | `str` | `"png"` | One of `"png"` `"svg"` `"pdf"` |

#### .render() → ChartResult

Triggers chart generation.

#### .save(path=None) → str

Generates and saves to file. Format determined by extension. Path is optional (defaults to `~/llmpic_charts/`).

#### .image_bytes (property) → bytes

Triggers generation, returns PNG bytes.

#### .code (property) → str

Triggers generation, returns generated matplotlib code.

---

## AsyncPlotBuilder (Async Builder)

Async fluent builder. Same API as `PlotBuilder`, but key methods require `await`.

| Method | Async | Description |
|--------|-------|-------------|
| `.data(data)` | No | Attach data |
| `.style(spec)` | No | Set style |
| `.format(fmt)` | No | Set output format |
| `await .render()` | **Yes** | Trigger generation |
| `await .save(path=None)` | **Yes** | Generate and save, path optional |

---

## ChartResult (Result Object)

Encapsulates a chart generation result.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `success` | `bool` | Whether generation succeeded |
| `image_bytes` | `bytes` | Primary format bytes (default PNG) |
| `error_message` | `str` or `None` | Error description |
| `code` | `str` or `None` | Generated matplotlib code |
| `token_usage` | `dict` | Token usage: `{"input": N, "output": M}` |
| `size_kb` | `float` | Image size in KB |
| `svg_bytes` | `bytes` | SVG bytes (lazy, re-renders on first access) |
| `pdf_bytes` | `bytes` | PDF bytes (lazy) |
| `svg` | `str` | SVG as a string |

### Methods

#### .save(path=None)

Save chart to file. Format auto-detected from extension. Path is optional.

```python
result.save()                    # → ~/llmpic_charts/chart_20250101_120000.png
result.save("chart.png")        # PNG
result.save("chart.svg")        # SVG
result.save("chart.pdf")        # PDF
result.save("/abs/path/ch.png") # Absolute path
```

#### .show()

Display chart inline in Jupyter Notebook / IPython.

```python
result.show()  # Renders directly below the cell
```

#### .base64() → str

Returns PNG base64 data URI: `data:image/png;base64,...`

#### .base64_svg() → str

Returns SVG base64 data URI: `data:image/svg+xml;base64,...`

#### .edit(edit_query) → ChartResult

Modify the chart using natural language. Returns a new `ChartResult`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `edit_query` | `str` | Edit description, e.g. `"make bars red, increase title size"` |

```python
v1 = lp.plot("Monthly sales").render()
v2 = v1.edit("Change to bar chart, use red color")
v2.save("v2.png")
```

---

## SandboxExecutor

Executes matplotlib code in a restricted sandbox.

### Constructor

```python
SandboxExecutor(
    chinese_font: bool = True,
    timeout: int = 30,
    dpi: int = 150,
    output_dir: str = "~/llmpic_charts",
)
```

### execute()

```python
def execute(
    code: str,
    style: dict = None,
    format: str = 'png',
) -> tuple  # (image_bytes | None, error_message | None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `code` | `str` | **required** | Matplotlib Python code |
| `style` | `dict` | `{}` | Style dictionary |
| `format` | `str` | `"png"` | Output format: `"png"` `"svg"` `"pdf"` |

Sandbox guarantees:
- `plt.show()` / `plt.savefig()` / `plt.close()` intercepted → no-op
- File I/O, system commands, network, dynamic execution blocked
- Thread-executed with timeout fuse
- Module-level execution lock prevents matplotlib state races

---

## CodeSafetyChecker

Dual-layer code safety: compiled regex patterns + optional LLM semantic review.

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
| `client` | `OpenAI` | **required** | OpenAI client |
| `model` | `str` | **required** | Review model |
| `level` | `str` | `"fast"` | `"fast"` regex only, `"full"` regex + LLM |

### check()

```python
def check(
    code: str,
    llm_review: bool = None,
) -> tuple  # (is_safe: bool, reason: str)
```

### regex_check()

```python
def regex_check(code: str) -> list  # violation labels
```

32 precompiled patterns covering: system commands, file operations, dynamic execution, network access, dangerous modules, reflection escapes.

---

## Config Constants

### Color Schemes

| Name | Colors |
|------|--------|
| `blues` | `#3498DB` `#5DADE2` `#87CEEB` `#2980B9` `#AED6F1` |
| `warm` | `#E74C3C` `#F39C12` `#E67E22` `#F1C40F` `#D35400` |
| `cool` | `#1ABC9C` `#3498DB` `#9B59B6` `#2ECC71` `#16A085` |
| `pastel` | `#FADBD8` `#D5F5E3` `#D6EAF8` `#F9E79F` `#E8DAEF` |
| `dark` | `#2C3E50` `#34495E` `#7F8C8D` `#95A5A6` `#BDC3C7` |
| `grayscale` | `#333333` `#666666` `#999999` `#BBBBBB` `#DDDDDD` |

### Default Style

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

---

← [Back to Home](./README_EN.md)

```
