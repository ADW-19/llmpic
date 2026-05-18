<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <a href="https://github.com/ADW-19/llmpic"><img src="https://img.shields.io/badge/github-ADW--19%2Fllmpic-lightgrey.svg" alt="GitHub"></a>
  <img src="https://img.shields.io/badge/python-≥3.10-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/version-0.2.1-orange.svg" alt="Version">
  <img src="https://img.shields.io/badge/pypi-llmpic-blue.svg" alt="PyPI">
</p>

<p align="center"><img src="./llmpic_logo.png" alt="llmpic logo" width="120"></p>

<h1 align="center">LLMPIC</h1>
<p align="center"><strong>Natural Language → Production Charts. One line.</strong></p>

<p align="center">
  <a href="./doc/README_CN.md">中文</a> &nbsp;|&nbsp;
  <a href="https://ADW-19.github.io/llmpic/">Documentation</a> &nbsp;|&nbsp;
  <a href="./doc/english/API_REFERENCE_EN.md">API Reference</a> &nbsp;|&nbsp;
  <a href="./doc/english/GUIDE_EN.md">User Guide</a>
</p>

---

```python
from llmpic import llmPIC

lp = llmPIC(api_key="sk-...", base_url="https://api.openai.com/v1")

lp.plot("Monthly sales trend, 12 months").show()   # Jupyter inline
lp.plot("CPU usage over 30 days").save()            # → ~/llmpic_charts/
lp.bar("Sales by region").data(df).style({"color_scheme":"warm"}).save("bar.png")
```

---

## 💡 Why llmpic?

Traditional Python charting means wrestling with matplotlib's verbose API — `plt.subplots()`, `ax.set_xticklabels()`, `fig.tight_layout()`, hundreds of functions to memorize, 15–40 lines for a single chart. Data scientists spend more time googling matplotlib syntax than analyzing data.

**llmpic** brings Python visualization into the LLM era. Describe what you want in plain English, Chinese, Japanese, or Korean — get a production-quality matplotlib chart instantly.

|  | Traditional matplotlib | llmpic |
|---|---|---|
| Lines of code | 15–40 lines | **1–3 lines** |
| API knowledge | 100+ functions | **0** (natural language) |
| Chart types | Manual selection | **11 types + auto-detect** |
| Iteration | Rewrite entire block | **`result.edit("make bars red")`** |
| Jupyter | `plt.show()` only | **`result.show()` inline** |
| Multi-format | Separate savefig calls | **Single `save()` — PNG/SVG/PDF** |
| Error recovery | Manual debugging | **Auto-fix with LLM (up to 2 rounds)** |
| Concurrency | Manual threading | **`AsyncllmPIC.batch()` parallel generation** |
| Security | None | **Dual-layer: 32 regex + optional LLM review** |

### 👀 See the difference for yourself

**Task**: A grouped bar chart comparing 4 regions × 4 quarters, with value labels, custom colors, dashed grid, title, axis labels, and a legend.

<table>
<tr>
<td><strong>Traditional matplotlib</strong> — 30+ lines, 100+ API calls to memorize</td>
<td><strong>llmpic</strong> — 1 line, plain English</td>
</tr>
<tr>
<td>

```python
import matplotlib.pyplot as plt
import numpy as np

regions  = ["North", "South", "East", "West"]
quarters = ["Q1", "Q2", "Q3", "Q4"]
data = np.array([
    [120, 145, 160, 180],
    [ 95, 110, 130, 155],
    [140, 165, 180, 200],
    [ 80,  95, 110, 125],
])

x = np.arange(len(regions))
w = 0.2
colors = ["#4C72B0", "#55A868",
          "#C44E52", "#8172B2"]

fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
for i, q in enumerate(quarters):
    bars = ax.bar(x + i * w, data[:, i], w,
                  label=q, color=colors[i])
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2,
                h + 1, f"{h:.0f}",
                ha="center", va="bottom", fontsize=9)

ax.set_title("Quarterly Sales by Region (2025)",
             fontsize=14, pad=12)
ax.set_xlabel("Region")
ax.set_ylabel("Sales (K USD)")
ax.set_xticks(x + w * 1.5)
ax.set_xticklabels(regions)
ax.legend(title="Quarter", loc="upper left")
ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
plt.savefig("sales.png", dpi=150)
plt.close()
```

</td>
<td>

```python
from llmpic import llmPIC

lp = llmPIC(api_key="sk-...",
            base_url="https://api.openai.com/v1")

# Step 1: render — LLM writes matplotlib code,
# safety check + sandbox execute it for you.
result = lp.bar(
    "Quarterly sales by region 2025: "
    "North=[120,145,160,180], "
    "South=[95,110,130,155], "
    "East=[140,165,180,200], "
    "West=[80,95,110,125]. "
    "Add value labels, dashed grid, legend."
).render()

result.save("sales.png")

# Want to tweak it later? Use natural language:
v2 = result.edit("make Q4 bars red, "
                 "title 'Annual Report'")
v2.save("sales_v2.png")

# Need the underlying matplotlib code? It's right there:
print(result.code)
```

**That's it.** A chart that conveys the same insight —
*generated*, not hand-coded.

No `set_xticklabels`. No `bar.get_x() + bar.get_width()/2`.
No Stack Overflow tabs open.

</td>
</tr>
</table>

> 💥 **30+ lines of API drudgery → a few lines of plain English.** llmpic still hands you the generated matplotlib code via `result.code` if you want to fine-tune it manually. The exact rendered output depends on the LLM's code generation — if you need pixel-perfect control, `result.edit("...")` lets you iterate without rewriting from scratch.

---

## ✨ Features

- 🗣️ **Natural Language Input** — English, Chinese, Japanese, Korean
- 📊 **11 Chart Types** — Line, Scatter, Bar, Pie, Histogram, Heatmap, Boxplot, Area, Radar, Subplots, Auto-detect
- 🔗 **Fluent Builder API** — chain `.data()` → `.style()` → `.format()` → `.save()` / `.render()`
- 📓 **Jupyter Inline** — `result.show()` renders directly below notebook cells
- ⚡ **Async Batch** — `AsyncllmPIC.batch()` generates multiple charts concurrently (total time ≈ slowest one)
- 🔧 **Auto-Fix** — Failed code executions are auto-corrected by the LLM (up to 2 rounds)
- ✏️ **Iterative Editing** — `result.edit("make bars red, increase title size")` refines charts with natural language
- 📦 **Multi-Format** — PNG (raster), SVG (vector), PDF (print) from a single `save()`
- 🌍 **Multi-Language Labels** — Auto-detects query language and matches chart titles/labels
- 🛡️ **Dual Safety** — 32 precompiled regex patterns (~0ms) + optional LLM semantic review
- 💻 **Cross-Platform** — Windows / Linux / macOS, automatic CJK font configuration
- 🔄 **Exponential Retry** — LLM calls retry with backoff (1s, 2s, 4s) on transient failures
- 📊 **Structured Output** — Uses JSON mode for reliable code extraction from LLM responses

---

## 📦 Installation

```bash
pip install llmpic          # All-in-one: matplotlib, numpy, openai, pandas, seaborn, scikit-learn, scipy
```

**Requirements:**
- Python ≥ 3.10
- An OpenAI-compatible API endpoint (OpenAI, Azure, DeepSeek, GLM, Ollama, vLLM, etc.)
- For CJK charts: appropriate fonts (auto-detected on first run)

### Verify Installation

```python
from llmpic import llmPIC, AsyncllmPIC, ChartResult, PlotBuilder, AsyncPlotBuilder
import llmpic
print(llmpic.__version__)  # → "0.2.0"
```

---

## 🚀 Quick Start

### 1. Initialize the SDK

```python
from llmpic import llmPIC

# OpenAI
lp = llmPIC(
    api_key="sk-your-openai-key",
    base_url="https://api.openai.com/v1",
    model="gpt-4o",
)

# DeepSeek
lp = llmPIC(
    api_key="sk-your-deepseek-key",
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
)

# Any OpenAI-compatible endpoint (Azure, GLM, Ollama, vLLM, etc.)
lp = llmPIC(
    api_key="your-key",
    base_url="https://your-endpoint/v1",
    model="your-model",
)
```

### 2. Your First Chart

```python
# Basic — describe it, get a chart
lp.plot("12-month sales trend").save("sales.png")

# Jupyter inline display
lp.plot("CPU usage over 30 days").render().show()

# Default save path (falls through to home directory)
lp.plot("Temperature trend").save()  # → ~/llmpic_charts/chart_20250101_120000.png
```

### 3. With Real Data

```python
import pandas as pd

df = pd.read_csv("sales.csv")
lp.bar("Sales by region").data(df).style({
    "color_scheme": "warm",
    "figsize": [12, 7],
    "title_fontsize": 16,
}).save("regional_sales.png")
```

### 4. Common Patterns (30-second cookbook)

```python
# Line chart with SVG output
lp.plot("CPU trend").format('svg').save("cpu.svg")

# Scatter with DataFrame
lp.scatter("Age vs income correlation").data(df).save("scatter.png")

# Pie with inline data
lp.pie("Market share: A=40%, B=25%, C=20%, D=15%").save("pie.png")

# Heatmap correlation matrix
lp.heatmap("Feature correlation").data(corr_df).save("heatmap.png")

# Multi-chart dashboard
lp.subplots("2x2: trend line, region bar, customer scatter, growth histogram").save("dash.png")

# Let the LLM pick the best chart type
lp.custom("Analyze user retention trends").data(df).save("auto.png")

# Access generated code
result = lp.plot("Test").render()
print(result.code)           # The matplotlib code the LLM wrote
print(result.token_usage)    # {'input': 320, 'output': 180}

# Edit an existing chart
result = lp.plot("Sales: Jan=100, Feb=120").render()
result.edit("Change to bar chart, use red color").edit(
    "Title 'Q1 Revenue', add grid").save("final.png")
```

---

## 📊 Chart Types

| Method | Chart Type | Best For | LLM Hint |
|--------|-----------|----------|----------|
| `.plot()` | Line | Trends, time series, continuous data | `ax.plot()` |
| `.scatter()` | Scatter | Correlation, cluster visualization | `ax.scatter()` |
| `.bar()` | Bar / Barh | Categorical comparison, rankings | `ax.bar()` / `ax.barh()` |
| `.pie()` | Pie | Proportions, market share | `ax.pie(autopct='%1.1f%%')` |
| `.hist()` | Histogram | Distributions, frequency analysis | `ax.hist()` |
| `.heatmap()` | Heatmap | Correlation matrices, 2D density | `ax.imshow()` / `sns.heatmap()` |
| `.boxplot()` | Boxplot | Statistical distribution comparison | `ax.boxplot()` / `sns.boxplot()` |
| `.area()` | Area | Stacked trends, composition over time | `ax.fill_between()` / `ax.stackplot()` |
| `.radar()` | Radar | Multi-dim comparison, capability assessment | Polar axes |
| `.subplots()` | Dashboard | Multi-chart composite views | `plt.subplots(nrows, ncols)` |
| `.custom()` | Auto | LLM picks the best type automatically | Context-aware selection |

---

## 🔗 Core Workflow

```
  sdk.plot("query")            ← describe the chart in natural language
    → PlotBuilder
      .data(df)                ← attach real data (optional)
      .style({...})            ← customize appearance (optional)
      .format('png')           ← choose output format (optional)
      .render()                ← trigger: LLM → safety → sandbox → ChartResult
      .save("path.png")        ← trigger + save to file
```

### The Builder Pattern

```python
# All chart methods return a PlotBuilder. Builders are lazy — nothing runs
# until .render(), .save(), or accessing .image_bytes / .code.

builder = lp.plot("Monthly sales")  # Returns PlotBuilder — NOTHING generated yet
builder = builder.data(df)           # Attach data
builder = builder.style({"figsize": [12, 6]})  # Set style
builder = builder.format('svg')      # Set format

result = builder.render()  # ← NOW everything runs: LLM → safety → sandbox
result.save("chart.svg")
```

### ChartResult — Your Swiss Army Knife

```python
result = lp.plot("CPU trend").render()

# Basic info
result.success           # bool
result.code              # The matplotlib code (str)
result.token_usage       # {'input': 320, 'output': 180}
result.size_kb           # 45.2

# Save to file
result.save()            # → ~/llmpic_charts/chart_{timestamp}.png
result.save("out.png")   # PNG
result.save("out.svg")   # SVG
result.save("out.pdf")   # PDF

# Display in Jupyter
result.show()

# Base64 for web embedding
result.base64()          # data:image/png;base64,...
result.base64_svg()      # data:image/svg+xml;base64,...

# Access alternative formats (lazy — re-renders on first access)
result.svg_bytes         # SVG as bytes
result.pdf_bytes         # PDF as bytes
result.svg               # SVG as string

# Edit with natural language
v2 = result.edit("Change to bar chart, use warm colors")
v3 = v2.edit("Increase title size to 18")
```

---

## ⚡ Async & Batch

Use `AsyncllmPIC` for concurrent chart generation — total time ≈ slowest single chart.

```python
from llmpic import AsyncllmPIC
import asyncio

async def main():
    lp = AsyncllmPIC(
        api_key="sk-...",
        base_url="https://api.openai.com/v1",
        model="gpt-4o",
    )

    # Batch: 5 charts generated concurrently
    results = await lp.batch([
        ("plot",     "12-month sales trend"),
        ("bar",      "Regional sales comparison"),
        ("pie",      "Market share distribution"),
        ("scatter",  "Customer age vs spend"),
        ("heatmap",  "Feature correlation matrix"),
    ])

    for i, r in enumerate(results):
        if r.success:
            r.save(f"batch_{i}.png")
            print(f"[{i}] OK — {r.size_kb:.1f}KB, "
                  f"tokens: in={r.token_usage['input']} out={r.token_usage['output']}")
        else:
            print(f"[{i}] FAIL: {r.error_message}")

asyncio.run(main())
```

### Manual Concurrent Rendering

```python
async def main():
    lp = AsyncllmPIC(...)

    # Fine-grained control with builders
    builders = [
        lp.plot("CPU trend").format('png'),
        lp.bar("Sales").data(df).style({"color_scheme": "warm"}).format('svg'),
        lp.pie("Market share").format('pdf'),
    ]
    results = await asyncio.gather(*[b.render() for b in builders])
    # All three run concurrently

asyncio.run(main())
```

---

## ✏️ Iterative Editing

Don't rewrite prompts for small tweaks — use `edit()` to refine charts incrementally.

```python
# Start
result = lp.plot("Monthly sales: Jan=100, Feb=120, Mar=90, Apr=150").render()

# Iterate — each .edit() returns a NEW ChartResult (never mutates originals)
result = result.edit("Change to bar chart")
result = result.edit("Make bars red, use warm color scheme")
result = result.edit("Add grid lines, increase title font size to 18")
result = result.edit("Title 'Q1 2025 Sales Report', add y-axis label 'Revenue (K USD)'")

result.save("final.png")
result.show()
```

**How it works:** Each `edit()` sends the current code + your edit request to the LLM, which returns modified code. The new code passes through the same safety check → sandbox execution pipeline. Original `ChartResult` is never mutated.

---

## 📦 Output Formats

| Format | Extension | Type | Best For |
|--------|----------|------|----------|
| PNG | `.png` | Raster | General use, embedding, quick preview |
| SVG | `.svg` | Vector | Web embedding, printing, scaling |
| PDF | `.pdf` | Vector/Print | Reports, publications, sharing |

```python
# Method 1: Chain .format() before render
lp.plot("Trend").format('svg').save("chart.svg")
lp.plot("Trend").format('pdf').save("chart.pdf")

# Method 2: Extension auto-detection on save
result = lp.plot("Trend").render()     # Default: PNG
result.save("output.svg")              # → SVG (detected from extension)
result.save("output.pdf")              # → PDF

# Method 3: Access alternative format properties (lazy re-render)
result = lp.plot("Trend").render()     # PNG in image_bytes
svg_data = result.svg_bytes             # Re-renders as SVG (lazy, cached)
pdf_data = result.pdf_bytes             # Re-renders as PDF (lazy, cached)
```

---

## 🎨 Style Customization

### Preset Color Schemes (6 built-in)

```python
lp.plot("Trend").style({"color_scheme": "blues"}).save("b.png")
lp.plot("Trend").style({"color_scheme": "warm"}).save("w.png")
lp.plot("Trend").style({"color_scheme": "cool"}).save("c.png")
lp.plot("Trend").style({"color_scheme": "pastel"}).save("p.png")
lp.plot("Trend").style({"color_scheme": "dark"}).save("d.png")
lp.plot("Trend").style({"color_scheme": "grayscale"}).save("g.png")
```

### All Style Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `figsize` | `[int, int]` | `[10, 6]` | Figure size in inches (width, height) |
| `dpi` | `int` | `150` | Output resolution (dots per inch) |
| `color_scheme` | `str` | `"blues"` | One of: `blues` `warm` `cool` `pastel` `dark` `grayscale` |
| `title_fontsize` | `int` | `14` | Chart title font size |
| `label_fontsize` | `int` | `12` | Axis label font size |
| `tick_fontsize` | `int` | `10` | Tick mark label font size |
| `grid` | `bool` | `True` | Show background grid |
| `grid_alpha` | `float` | `0.3` | Grid line transparency (0–1) |
| `tight_layout` | `bool` | `True` | Auto-adjust layout to avoid clipping |
| `facecolor` | `str` | `"white"` | Figure background color (any CSS color) |

### Style Examples

```python
# Journal-quality figure
lp.plot("Experiment results").style({
    "figsize": [8, 5],
    "dpi": 300,
    "color_scheme": "dark",
    "title_fontsize": 16,
    "label_fontsize": 14,
}).save("journal.png")

# Presentation-ready
lp.bar("Q4 revenue").data(df).style({
    "figsize": [14, 8],
    "color_scheme": "warm",
    "title_fontsize": 22,
    "label_fontsize": 16,
    "tick_fontsize": 14,
    "grid": False,
    "facecolor": "#FAFAFA",
    "dpi": 200,
}).save("presentation.png")

# Style can also be passed as JSON string
lp.plot("Trend").style('{"color_scheme":"cool","figsize":[12,8]}').save("trend.png")
```

---

## 🛡️ Security

llmpic executes LLM-generated code in a **sandboxed environment** with dual-layer protection:

### Layer 1: Regex Pattern Matching (~0ms overhead)

32 precompiled regex patterns block known dangerous patterns:
- **System commands**: `os.system()`, `os.popen()`, `subprocess`
- **File I/O**: `open()` (generated code shouldn't access files)
- **Dynamic execution**: `exec()`, `eval()`, `compile()`, `__import__()`
- **Network access**: `socket`, `urllib`, `requests`, `httpx`
- **Dangerous modules**: `shutil`, `ctypes`, `pickle`
- **Reflection escapes**: `__subclasses__`, `__bases__`, `__mro__`

### Layer 2: Sandbox Execution

- **Restricted namespace**: Only safe builtins + matplotlib, numpy, pandas, seaborn
- **Figure.savefig intercepted**: Code cannot write files directly
- **plt.show() / plt.savefig() / plt.close() blocked**: All intercepted as no-ops
- **Timeout fuse**: ThreadPoolExecutor + timeout kills runaway code
- **Serialization lock**: Module-level mutex prevents matplotlib state races

### Safety Level Configuration

```python
# Fast mode (recommended for production) — regex only
lp = llmPIC(..., safety_level="fast")

# Full mode — regex + LLM semantic review (adds ~1-2s per chart)
lp = llmPIC(..., safety_level="full")
```

**Recommendation:** The sandbox already blocks all real execution paths. `fast` mode is sufficient for production use.

---

## 🌐 Provider Compatibility

llmpic works with **any OpenAI-compatible API endpoint** that supports `chat/completions` with JSON structured output:

| Provider | base_url | model (example) |
|----------|----------|-------------------|
| OpenAI | `https://api.openai.com/v1` | `gpt-5.5`, `gpt-5.5-mini` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-v4-pro` |
| Azure OpenAI | `https://{resource}.openai.azure.com/openai/deployments/{deployment}` | Your deployment name |
| GLM (Zhipu) | `https://open.bigmodel.cn/api/paas/v5` | `glm-5` |
| Ollama (local) | `http://localhost:11434/v1` | `llama3`, `qwen3.5` |
| vLLM (local) | `http://localhost:8000/v1` | Your served model |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b` |

> **Note**: For best chart quality, use a model with strong code generation capabilities (GPT-5.5, DeepSeek-V4, GLM-5, etc.). Local models may produce less reliable code — consider increasing `max_retries` and `max_fix_attempts`.

---

## 🔧 Environment Variables

Store credentials in environment variables or `.env` files for cleaner code:

```bash
# .env file or shell
export LLMPIC_API_KEY="sk-your-key"
export LLMPIC_BASE_URL="https://api.openai.com/v1"
export LLMPIC_MODEL="gpt-4o"
```

```python
import os
from llmpic import llmPIC

lp = llmPIC(
    api_key=os.getenv("LLMPIC_API_KEY"),
    base_url=os.getenv("LLMPIC_BASE_URL"),
    model=os.getenv("LLMPIC_MODEL", "gpt-4o"),
)
```

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      llmPIC / AsyncllmPIC                    │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │  .plot() │   │  .bar()  │   │  .pie()  │   │  .custom()│ │
│  │.scatter()│   │ .hist()  │   │.heatmap()│   │   ... 11  │ │
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘ │
│       └──────────────┴──────────────┴──────────────┘        │
│                          │                                   │
│                    PlotBuilder / AsyncPlotBuilder             │
│                    .data() .style() .format()                 │
│                          │                                   │
│                    .render() / .save()                        │
│                          │                                   │
│              ┌───────────┴───────────┐                      │
│              │  1. LLM Code Gen      │  OpenAI API           │
│              │     (with retry ×3)   │                      │
│              └───────────┬───────────┘                      │
│                          │                                   │
│              ┌───────────┴───────────┐                      │
│              │  2. Safety Check      │  CodeSafetyChecker    │
│              │     32 regex + LLM    │                      │
│              └───────────┬───────────┘                      │
│                          │                                   │
│              ┌───────────┴───────────┐                      │
│              │  3. Sandbox Execute   │  SandboxExecutor      │
│              │     (with auto-fix)   │  ThreadPool + timeout │
│              └───────────┬───────────┘                      │
│                          │                                   │
│                    ChartResult                               │
│         .save() .show() .edit() .base64() .svg .pdf          │
└─────────────────────────────────────────────────────────────┘
```

**Pipeline per chart:**
1. **LLM Code Generation** — Natural language → matplotlib Python code (JSON structured output, 3 retries with backoff)
2. **Safety Check** — 32 regex patterns + optional LLM semantic review
3. **Sandbox Execution** — ThreadPoolExecutor with timeout, Figure monkey-patching, restricted namespace
4. **Auto-Fix** — On execution failure, send code+error back to LLM for correction (up to 2 rounds)
5. **Result** — `ChartResult` with bytes, code, token usage, lazy format conversion

---

## 📖 Documentation

| Document | Language | Description |
|----------|----------|-------------|
| [API Reference](./doc/english/API_REFERENCE_EN.md) | EN | Complete class, method, and parameter reference |
| [API 参考](./doc/chinese/API_REFERENCE_CN.md) | 中文 | 所有类、方法、参数的详细说明 |
| [User Guide](./doc/english/GUIDE_EN.md) | EN | Advanced usage, best practices, troubleshooting |
| [使用指南](./doc/chinese/GUIDE_CN.md) | 中文 | 进阶用法、最佳实践、故障排查 |
| [Jupyter Demos](./notebook_examples/) | EN/中文 | Ready-to-run demo notebooks |
| [中文首页](./doc/README_CN.md) | 中文 | 完整中文 README |

---

## 📮 Official Contact

- **Xiaohongshu (RedNote)**: [ADW_AI](https://xhslink.com/m/AQw13M5WIPc)
- **GitHub Issues**: [github.com/ADW-19/llmpic/issues](https://github.com/ADW-19/llmpic/issues)

---

## 🙏 Acknowledgements

llmpic is built on the shoulders of these excellent open-source libraries:

- [SciPy](https://scipy.org/) — scientific computing
- [scikit-learn](https://scikit-learn.org/) — machine learning utilities
- [pandas](https://pandas.pydata.org/) — data analysis & DataFrame
- [NumPy](https://numpy.org/) — numerical computing
- [Matplotlib](https://matplotlib.org/) — chart rendering engine
- [seaborn](https://seaborn.pydata.org/) — statistical data visualization

Heartfelt thanks to all maintainers and contributors of these projects.

---

## 📄 License

[MIT](./LICENSE) © 2026 ADW-19
