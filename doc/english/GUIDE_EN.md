# User Guide — llmpic

> Advanced usage, best practices, complete workflows, and troubleshooting.

---

## Getting Started

### SDK Initialization

```python
from llmpic import llmPIC

lp = llmPIC(
    api_key="sk-...",                    # Required: your API key
    base_url="https://api.openai.com/v1",# Required: API endpoint
    model="gpt-4o",                      # Model for code generation
    # Optional — shown with defaults:
    safety_level="fast",                 # "fast" (regex) or "full" (regex+LLM)
    safety_model=None,                   # Safety review model (defaults to model)
    chinese_font=True,                   # Enable CJK font support
    timeout=30,                          # Code execution timeout (seconds)
    dpi=150,                             # Default output resolution
    output_dir="~/llmpic_charts",        # Default save directory
    temperature=0.3,                     # LLM creativity (0-2)
    max_tokens=2048,                     # Max LLM output tokens
    structured_output=True,              # Use JSON structured output
    max_retries=3,                       # LLM call retries (exp backoff)
    max_fix_attempts=2,                  # Auto-fix attempts on code error
)
```

### Choosing Parameters

| Scenario | Recommended Settings |
|----------|---------------------|
| Production / speed-sensitive | `safety_level="fast"`, `model="gpt-4o-mini"` |
| Maximum security | `safety_level="full"`, keep defaults |
| Complex multi-chart dashboards | `timeout=60`, `max_tokens=4096` |
| Local models (Ollama/vLLM) | `max_retries=5`, `structured_output=False`, `max_fix_attempts=3` |
| CJK-heavy charts | `chinese_font=True` (default) |
| English-only charts, smaller images | `chinese_font=False`, `dpi=100` |
| High-res for print/publication | `dpi=300` |

---

## Chart Types in Detail

### plot — Line Chart

Best for: trends, time series, continuous data.

```python
lp.plot("Monthly revenue for 2024").save("revenue.png")
lp.plot("sin(x) and cos(x) from 0 to 2π").save("trig.png")

# With real time-series data
df = pd.read_csv("metrics.csv")  # columns: date, cpu, memory
lp.plot("CPU and memory usage over time").data(df).save("metrics.png")
```

LLM hint: `Line chart. Use ax.plot(). Multiple series: different colors + legend.`

### scatter — Scatter Chart

Best for: correlation analysis, cluster visualization, outlier detection.

```python
# With DataFrame
lp.scatter("User age vs purchase amount").data(df).save("scatter.png")

# With inline data
lp.scatter("Scatter: x=[1,2,3,4,5], y=[2,4,1,8,7]").save("simple_scatter.png")

# 3-variable scatter (color/size for 3rd dimension)
lp.scatter("Age vs income, color by education level, size by purchase frequency").data(df).save("3d_scatter.png")
```

LLM hint: `Scatter chart. Use ax.scatter(). 3rd variable → color/size.`

### bar — Bar Chart

Best for: categorical comparison, rankings, before/after contrasts.

```python
# Inline data in the prompt
lp.bar("Q1 Budget: R&D=$200K, Marketing=$150K, Sales=$180K, HR=$100K").save("budget.png")

# Horizontal bar chart
lp.bar("Top 10 cities by GDP, horizontal bars").data(city_df).save("horizontal.png")

# Grouped bar chart
lp.bar("Monthly sales by product line: Product A, B, C — grouped bars").data(sales_df).save("grouped.png")

# Stacked bar
lp.bar("Revenue composition by quarter, stacked bars").data(revenue_df).save("stacked.png")
```

LLM hint: `Bar chart. Use ax.bar() or ax.barh(). Add value labels on bars.`

### pie — Pie Chart

Best for: proportions, market share, budget allocation.

```python
# Inline ratios
lp.pie("Market share: Product A 40%, B 25%, C 20%, Others 15%").save("market.png")

# With DataFrame
lp.pie("Spending breakdown by category").data(budget_df).save("spending.png")

# Donut chart (via natural language)
lp.pie("Donut chart: Revenue by department").data(dept_df).save("donut.png")
```

LLM hint: `Pie chart. Use ax.pie() with autopct='%1.1f%%' and legend.`

### hist — Histogram

Best for: distributions, frequency analysis, normality checks.

```python
# With raw data
import numpy as np
data = np.random.randn(1000)
lp.hist("Score distribution with KDE overlay").data(data).save("hist.png")

# Specify bins in query
lp.hist("Income distribution, 50 bins").data(income_data).save("income_hist.png")

# Multiple distributions overlaid
lp.hist("Test scores: Group A vs Group B, overlaid histograms").data({
    "Group A": np.random.normal(70, 10, 500),
    "Group B": np.random.normal(75, 12, 500),
}).save("compare_hist.png")
```

LLM hint: `Histogram. Use ax.hist(). Overlay KDE via sns.kdeplot if seaborn available.`

### heatmap — Heatmap

Best for: correlation matrices, 2D density, confusion matrices.

```python
# Correlation matrix
lp.heatmap("Feature correlation matrix, annotated").data(corr_df).save("corr_heatmap.png")

# Time-based heatmap
lp.heatmap("Hourly website traffic by day of week").data(traffic_df).save("traffic_heatmap.png")
```

LLM hint: `Heatmap. Use ax.imshow() or sns.heatmap(). Add colorbar and annotate cells.`

### boxplot — Boxplot

Best for: statistical distribution comparison across groups.

```python
# Multi-group comparison
lp.boxplot("Experiment results: Control vs Treatment A vs Treatment B").save("boxplot.png")

# With DataFrame (categories in one column, values in another)
lp.boxplot("Salary distribution by department").data(hr_df).save("salary_box.png")
```

LLM hint: `Boxplot. Use ax.boxplot() or sns.boxplot(). Show outliers, add labels.`

### area — Area Chart

Best for: stacked trends, compositional changes over time.

```python
lp.area("Revenue composition by product line 2020–2024").data(revenue_df).save("area.png")
lp.area("Stacked area: user acquisition channels over time").data(channel_df).save("channels.png")
```

LLM hint: `Area chart. Use ax.fill_between() or ax.stackplot(). Set alpha 0.3-0.7.`

### radar — Radar Chart

Best for: multi-dimensional comparison, capability assessment, profile comparison.

```python
# Inline dimensions
lp.radar("Product ratings: Performance=4, Usability=3, Reliability=5, Price=2, Support=4").save("radar.png")

# Compare two profiles
lp.radar("Radar: Product A [4,3,5,2,4] vs Product B [3,4,4,3,5], categories: Speed,UI,Reliability,Cost,Support").save("radar2.png")
```

LLM hint: `Radar chart. Use polar axes: plt.subplots(subplot_kw={'projection':'polar'}). Close the polygon loop.`

### map — Geographic Map (v0.3.0)

Best for: world maps, country/regional views, choropleth, geographic scatter plots.

```python
# World map with demo data (LLM generates major world cities)
lp.map("World population by country, Blues choropleth").save("world.png")

# Map with real data (DataFrame with lat/lon columns)
lp.map("Earthquake epicenters in Japan, magnitude color scale").data(eq_df).save("japan.png")

# Specific country/region
lp.map("China major cities GDP, larger markers for bigger GDP").data(city_df).save("china.png")

# World cities scatter
lp.map("Major cities: Tokyo, NYC, London, Paris, Beijing, Sydney, marked with population size").save("cities.png")
```

LLM hint: `Geographic map. Use cartopy (ccrs, cfeature) with PlateCarree projection.`

### subplots — Dashboard

Best for: multi-chart composite views, executive summaries.

```python
# 2×2 dashboard
lp.subplots("2x2: sales trend line, region bar, customer scatter, growth histogram").save("dashboard.png")

# 1×3 dashboard
lp.subplots("1 row 3 cols: CPU trend, Memory trend, Disk trend").data(metrics_df).save("triple.png")

# Complex dashboard
lp.subplots("3x2 dashboard: revenue line, expense bar, profit margin area, "
            "customer growth bar, region pie, correlation heatmap").data(full_df).save("executive.png")
```

LLM hint: `Dashboard. Use fig, axes = plt.subplots(nrows, ncols, figsize=(w,h)). Add fig.suptitle(). Each subplot is a different chart.`

### custom — Auto-Detect

Best for: when you're not sure which chart type fits best.

```python
lp.custom("Analyze user retention trends and contributing factors").data(user_df).save("auto.png")
lp.custom("Compare feature importance from the ML model").data(feature_df).save("importance.png")
```

LLM hint: `Pick best chart type (line/bar/scatter/pie/hist/boxplot/heatmap/area/radar) for the data & query.`

---

## Data Input Methods

### No Data — LLM Generates Demo Data

When exploring or prototyping, skip `.data()` entirely:

```python
lp.plot("Sine wave from 0 to 2π").save("sine.png")
lp.bar("Fictional sales: Q1=100, Q2=150, Q3=120, Q4=180").save("demo.png")
lp.pie("Made-up market share: A=40%, B=30%, C=20%, D=10%").save("demo_pie.png")
```

The LLM uses `np.linspace`, `np.random`, etc. to generate realistic demo data.

### DataFrame (Recommended for Production)

```python
import pandas as pd

df = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "Sales": [120, 135, 148, 162, 155, 180],
    "Profit": [20, 28, 30, 35, 32, 40],
})
lp.plot("Monthly sales vs profit trend").data(df).save("sales.png")
```

**What the LLM receives for DataFrames:**
1. Shape: rows × columns
2. Column names and dtypes
3. First 5 rows (head)
4. Statistical summary (describe) if more than 5 rows

This gives the LLM enough context to write correct code without sending the entire dataset.

### NumPy Array

```python
import numpy as np

# 1D array
data = np.random.randn(1000)
lp.hist("Data distribution").data(data).save("dist.png")

# 2D array
matrix = np.random.rand(10, 10)
lp.heatmap("Random matrix").data(matrix).save("matrix.png")

# Multi-dimensional (serialized with shape, dtype, first N elements)
```

### Dictionary

```python
lp.bar("Sales by city").data({
    "City": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Hangzhou"],
    "Sales": [320, 280, 260, 240, 200],
}).save("city.png")

# Multiple series
lp.plot("Multi-line comparison").data({
    "x": [1, 2, 3, 4, 5],
    "Series A": [10, 20, 15, 25, 30],
    "Series B": [5, 15, 25, 20, 35],
    "Series C": [12, 18, 22, 28, 32],
}).save("multi.png")
```

### List / Tuple

```python
lp.plot("Temperature readings").data([22, 24, 19, 26, 28, 25, 23]).save("temp.png")
lp.bar("Scores").data((85, 92, 78, 88, 95)).save("scores.png")
```

A single list is treated as a 1D series. The LLM creates an index for the x-axis.

### Raw String

```python
csv_text = "date,value\n2024-01-01,100\n2024-01-02,105\n..."
lp.plot("CSV trend").data(csv_text).save("from_csv.png")
```

Limited to 2000 characters. For larger data, use a DataFrame or pre-aggregate.

### Passing Large Datasets

For large DataFrames, pre-aggregate or sample to keep the serialized context reasonable:

```python
# Good: pre-aggregate
lp.bar("Monthly average").data(df.groupby("month")["value"].mean().reset_index())

# Good: sample
lp.scatter("Correlation").data(df.sample(1000))

# Bad: huge raw DataFrame
lp.plot("Trend").data(huge_df)  # Only first 5 rows + stats are sent anyway
```

---

## Style Customization

### Quick Color Schemes

6 preset schemes with 5 colors each:

| Scheme | Hex Colors | Vibe |
|--------|-----------|------|
| `blues` | `#3498DB` `#5DADE2` `#87CEEB` `#2980B9` `#AED6F1` | Professional, corporate |
| `warm` | `#E74C3C` `#F39C12` `#E67E22` `#F1C40F` `#D35400` | Energetic, attention-grabbing |
| `cool` | `#1ABC9C` `#3498DB` `#9B59B6` `#2ECC71` `#16A085` | Modern, technical |
| `pastel` | `#FADBD8` `#D5F5E3` `#D6EAF8` `#F9E79F` `#E8DAEF` | Soft, readaable |
| `dark` | `#2C3E50` `#34495E` `#7F8C8D` `#95A5A6` `#BDC3C7` | Serious, dark-background |
| `grayscale` | `#333333` `#666666` `#999999` `#BBBBBB` `#DDDDDD` | Print-safe, formal |

```python
for scheme in ["blues", "warm", "cool", "pastel", "dark", "grayscale"]:
    lp.plot("Monthly trend").style({"color_scheme": scheme}).save(f"{scheme}.png")
```

### Size & Resolution

```python
lp.plot("Trend").style({
    "figsize": [14, 7],         # 14" wide × 7" tall
    "dpi": 300,                  # High resolution for print
}).save("large.png")
```

### Typography

```python
lp.plot("Trend").style({
    "title_fontsize": 20,        # Large title
    "label_fontsize": 14,        # Readable axis labels
    "tick_fontsize": 12,         # Clear tick marks
}).save("typography.png")
```

### Grid & Background

```python
# Visible grid with dark background
lp.plot("Trend").style({
    "grid": True,
    "grid_alpha": 0.6,
    "facecolor": "#F0F0F0",
}).save("grid.png")

# Clean, no grid
lp.plot("Trend").style({
    "grid": False,
    "facecolor": "white",
}).save("clean.png")

# Tight layout (default True) — disable if you want manual spacing
lp.plot("Trend").style({"tight_layout": False}).save("loose.png")
```

### Combined Styling

```python
# Journal-quality figure
lp.plot("Experiment results: control vs treatment").data(exp_df).style({
    "figsize": [8, 5],
    "dpi": 300,
    "color_scheme": "dark",
    "title_fontsize": 16,
    "label_fontsize": 14,
    "tick_fontsize": 12,
    "grid": True,
    "grid_alpha": 0.4,
}).save("journal_fig.png")

# Dashboard / presentation
lp.bar("Annual revenue by quarter").data(revenue_df).style({
    "figsize": [14, 8],
    "color_scheme": "warm",
    "title_fontsize": 24,
    "label_fontsize": 18,
    "tick_fontsize": 14,
    "grid": False,
    "facecolor": "#FAFAFA",
    "dpi": 200,
}).save("presentation.png")

# Quick exploratory — use defaults
lp.scatter("Age vs income").data(df).save("explore.png")
```

### Style as JSON String

```python
lp.plot("Trend").style('{"color_scheme":"cool","figsize":[12,8],"dpi":200}').save("trend.png")
```

---

## Output Formats

### PNG (Default)

Raster format. Good for general use, embedding, quick previews.

```python
lp.plot("Trend").save("chart.png")
result = lp.plot("Trend").format('png').render()
```

### SVG — Vector Graphics

Ideal for web embedding, PDF reports, situations requiring scaling without quality loss.

```python
# Method 1: Specify format before rendering
lp.plot("Trend").format('svg').save("chart.svg")

# Method 2: Extension auto-detection
result = lp.plot("Trend").render()    # Default: PNG
result.save("chart.svg")               # → SVG (detected from .svg extension)

# Base64 for HTML embedding
result = lp.plot("Trend").render().format('svg')  # or: after render, access svg_bytes
svg_uri = result.base64_svg()
# HTML: <img src="{svg_uri}" />
```

### PDF — For Printing and Reports

```python
lp.plot("Trend").format('pdf').save("chart.pdf")
result = lp.plot("Trend").render()
result.save("report_figure.pdf")
```

### Lazy Format Conversion

Once you have a `ChartResult`, you can access any format on demand:

```python
result = lp.plot("CPU trend").render()  # PNG in result.image_bytes

# Access SVG or PDF — re-renders from the stored code (lazy, cached)
svg_bytes = result.svg_bytes    # Re-renders as SVG on first access
pdf_bytes = result.pdf_bytes    # Re-renders as PDF on first access
svg_string = result.svg          # SVG as a Python string
```

This is powerful: generate once, export in all three formats without re-calling the LLM.

### Default Save Path

```python
result = lp.plot("Daily active users").render()
result.save()  # → ~/llmpic_charts/chart_20250101_143025.png
```

The timestamp format is `YYYYMMDD_HHMMSS`. Directory is created automatically if it doesn't exist.

### Jupyter Notebook Inline Display

```python
result = lp.plot("CPU usage trend").render()
result.show()  # Renders directly below the cell — no save() needed
```

Supports PNG, SVG, and PDF formats in Jupyter. In plain Python scripts, `show()` logs a warning.

---

## Iterative Editing

### Basic Workflow

```python
# Version 1
v1 = lp.plot("Monthly sales: Jan=100, Feb=120, Mar=90, Apr=150").render()
v1.save("v1.png")

# Version 2 — natural language edit
v2 = v1.edit("Change to bar chart")
v2.save("v2.png")

# Version 3 — multiple changes at once
v3 = v2.edit("Make bars red, title 'Q1 2025 Sales Report', add grid")
v3.save("v3.png")

# Version 4 — fine-tuning
v4 = v3.edit("Increase title font size to 18, use warm color scheme")
v4.save("v4.png")
```

### How edit() Works

```
1. Sends current code + edit description to LLM
2. LLM returns modified code
3. Safety check → sandbox execution
4. Returns NEW ChartResult (original is never mutated)
```

### Chaining Edits

```python
final = (
    lp.plot("Monthly sales: Jan=100, Feb=120, Mar=90")
    .render()
    .edit("Change to bar chart")
    .edit("Make bars red, warm colors")
    .edit("Title 'Q1 Revenue', add y-axis label 'K USD'")
    .edit("Add grid, increase title size to 18")
)
final.save("final.png")
final.show()
```

### Edit Preserves Context

The `edit()` method preserves your original data, style settings, and SDK reference. Each edit re-uses the same sandbox, safety checker, and LLM endpoint.

**Important**: `.edit()` requires the `ChartResult` to have been generated by `llmPIC` (not created manually), because it needs the `_sdk` reference for code generation.

---

## Auto-Fix Mechanism

### How It Works

```
LLM generates code → Safety check → Sandbox execution
                                          ↓ FAIL (NameError, ValueError, etc.)
                                     LLM fixes code
                                          ↓
                                  Safety check → Sandbox execution
                                          ↓ STILL FAILING
                                     LLM fixes again (up to max_fix_attempts)
                                          ↓
                               Return ChartResult (success or final error)
```

### Configuration

```python
lp = llmPIC(
    ...,
    max_fix_attempts=2,   # Default: 2 rounds of auto-fix
)
# max_fix_attempts=0  →  Disable auto-fix entirely
```

### When Auto-Fix Triggers (and When It Doesn't)

**Triggers on:**
- `NameError` — referenced undefined variable
- `ValueError` — matplotlib received bad values
- `TypeError` — wrong argument types
- `IndexError` — out-of-bounds access
- Any other Python exception from the generated code

**Does NOT trigger on:**
- LLM returns no code → handled by `max_retries` (retries the generation)
- Safety check rejection → dangerous code is rejected outright, no fix attempted
- Timeout → possible infinite loop, not retried (the same code would likely timeout again)
- Empty chart (no axes) → detected immediately, no fix (the LLM didn't produce chart code)

### Checking Auto-Fix Activity

Configure logging to see auto-fix in action:

```python
import logging
logging.basicConfig(level=logging.INFO)

# You'll see log messages like:
# INFO:llmpic.core:Auto-fix attempt 2: NameError: name 'data' is not defined...
```

---

## Async & Batch Generation

### Single Async Chart

```python
import asyncio
from llmpic import AsyncllmPIC

async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="...")
    result = await lp.plot("CPU trend").render()
    result.save("cpu.png")

asyncio.run(main())
```

### Batch — Concurrent Generation

The batch method generates all charts in parallel using `asyncio.gather`. Total time ≈ the slowest single chart.

```python
async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="...")

    results = await lp.batch([
        ("plot",     "12-month sales trend"),
        ("bar",      "Revenue by department"),
        ("scatter",  "User behavior correlation"),
        ("heatmap",  "Feature correlation matrix"),
        ("pie",      "Market share distribution"),
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

### batch() Request Format

```python
requests: List[Tuple[str, str]]
# Each tuple: (chart_type, query)
# chart_type must be one of:
#   "line" "scatter" "bar" "pie" "hist" "heatmap"
#   "boxplot" "area" "radar" "map" "subplots" "custom"
```

> Note: `batch()` uses default style and no data attachments. For custom data/style per chart, use the builder approach below.

### Batch with Data, Style, and Format

For per-chart customization, use builders with `asyncio.gather`:

```python
async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="...")

    builders = [
        lp.plot("CPU trend").format('png'),
        lp.bar("Sales").data(sales_df).style({"color_scheme": "warm"}).format('svg'),
        lp.pie("Market share").data(market_df).style({"color_scheme": "cool"}).format('pdf'),
        lp.heatmap("Correlation").data(corr_df).format('png'),
    ]

    results = await asyncio.gather(*[b.render() for b in builders])

    for r in results:
        r.save()  # Each saves to ~/llmpic_charts/ with timestamp

asyncio.run(main())
```

### Error Handling in Batch

```python
async def main():
    lp = AsyncllmPIC(...)

    results = await lp.batch(requests)

    success_count = sum(1 for r in results if r.success)
    total_tokens = sum(r.token_usage.get('input', 0) + r.token_usage.get('output', 0)
                       for r in results if r.success)

    print(f"Generated {success_count}/{len(results)} charts, {total_tokens} total tokens")

    for i, r in enumerate(results):
        if r.success:
            r.save(f"report_{i}.png")
        else:
            print(f"Chart {i} failed: {r.error_message}")

asyncio.run(main())
```

---

## Security Model

### Architecture

```
Generated Code
      │
      ├──→ Layer 1: Regex Check (32 patterns, ~0ms)
      │         ↓
      │    [FAIL] → Reject immediately
      │    [PASS] → Continue
      │
      └──→ Layer 2: LLM Semantic Review (optional, ~1-2s)
                ↓
           [FAIL] → Reject with reason
           [PASS] → Proceed to sandbox
```

### Layer 1: Regex Patterns (always active)

32 precompiled patterns block:

| Category | Patterns |
|----------|----------|
| System commands | `os.system()`, `os.popen()`, `os.exec*()`, `os.spawn*()`, `subprocess` |
| File operations | `os.remove()`, `os.unlink()`, `os.rmdir()`, `os.rename()`, `os.mkdir/makedirs()`, `os.chmod()`, `os.environ`, `open()` |
| Dynamic execution | `exec()`, `eval()`, `compile()`, `__import__()` |
| Network access | `socket`, `urllib`, `requests`, `httpx` |
| Process exit | `sys.exit()` |
| Dangerous modules | `shutil`, `ctypes`, `pickle` |
| Reflection escapes | `__subclasses__`, `__bases__`, `__mro__`, `setattr()`, `delattr()` |

### Layer 2: Sandbox Execution (always active)

- **Restricted builtins**: Only safe builtins available — no `open()`, `exec()`, etc. in namespace
- **Figure monkey-patching**: `Figure.__init__` tracked for detection; `Figure.savefig` intercepted — code cannot save files directly
- **plt interception**: `plt.show()`, `plt.savefig()`, `plt.close()` → no-ops
- **Timeout**: ThreadPoolExecutor with configurable timeout kills runaway code
- **Serialization**: Module-level mutex prevents matplotlib global state races across concurrent executions

### Choosing Safety Level

```python
# Fast mode (recommended for production)
lp = llmPIC(..., safety_level="fast")

# Full mode (adds LLM review — ~1-2s per chart)
lp = llmPIC(..., safety_level="full")
```

**Recommendation**: The sandbox already provides strong isolation. `fast` mode is production-safe. Use `full` mode for adversarial scenarios (public-facing UIs accepting arbitrary prompts).

---

## Multi-Language Support

### Auto-Detection

The SDK detects query language via Unicode range analysis:

```python
lp.plot("CPU使用率趋势")              # → Chinese labels (检测到中文)
lp.plot("CPU使用量トレンド")            # → Japanese labels (日本語を検出)
lp.plot("CPU 사용량 추세")             # → Korean labels (한국어 감지)
lp.plot("CPU usage trend")             # → English labels
```

Detection logic:
- **Chinese**: CJK Unified Ideographs (U+4E00–U+9FFF) or Extension A (U+3400–U+4DBF)
- **Japanese**: Hiragana (U+3040–U+309F), Katakana (U+30A0–U+30FF), or Katakana Extension (U+31F0–U+31FF)
- **Korean**: Hangul Syllables (U+AC00–U+D7AF)
- **English**: Default (no CJK characters detected)

The language hint is passed to the LLM in the prompt: "Use Simplified Chinese for all labels and titles."

### Cross-Platform CJK Font Support

When `chinese_font=True` (default), the SDK auto-detects and configures CJK fonts:

| Platform | Font Priority |
|----------|--------------|
| Windows | Microsoft YaHei → SimHei → SimSun |
| macOS | PingFang SC → Heiti SC → STHeiti |
| Linux | WenQuanYi Micro Hei → WenQuanYi Zen Hei → Noto Sans CJK SC → Noto Sans SC |

Font detection runs once on first execution and is cached for the process lifetime (thread-safe).

**Disable CJK font** for English-only charts:

```python
lp = llmPIC(..., chinese_font=False)
```

### Mixed-Language Charts

You can use English queries but get CJK labels by describing it in the prompt:

```python
lp.plot("Sales trend with Chinese labels: 月份 as x-axis, 销售额 as y-axis")
```

---

## Provider Setup Guide

### OpenAI

```python
lp = llmPIC(
    api_key="sk-proj-...",
    base_url="https://api.openai.com/v1",
    model="gpt-4o",          # Best quality
    # model="gpt-4o-mini",   # Cheaper (~1/10 cost), slightly less reliable code
)
```

### DeepSeek (Recommended for Chinese Users)

DeepSeek offers excellent code generation at ~1/10 OpenAI cost:

```python
lp = llmPIC(
    api_key="sk-...",
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",    # DeepSeek-V3
    # model="deepseek-reasoner",  # DeepSeek-R1 (reasoning model, may be slower)
)
```

### Azure OpenAI

```python
lp = llmPIC(
    api_key="your-azure-api-key",
    base_url="https://{your-resource}.openai.azure.com/openai/deployments/{deployment-name}",
    model="gpt-4o",          # Your deployment name
    # Note: structured_output may need to be False for some Azure configs
)
```

### Zhipu GLM (智谱)

```python
lp = llmPIC(
    api_key="your-zhipu-api-key",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model="glm-4-plus",
)
```

### Ollama (Local)

```python
lp = llmPIC(
    api_key="ollama",           # Ollama doesn't require a real key
    base_url="http://localhost:11434/v1",
    model="qwen2.5:7b",         # Or llama3, codellama, etc.
    structured_output=False,    # Some local models don't support JSON mode
    max_retries=5,              # Local models may need more retries
    max_fix_attempts=3,         # More fix attempts for less capable models
)
```

### vLLM (Self-Hosted)

```python
lp = llmPIC(
    api_key="not-needed",
    base_url="http://localhost:8000/v1",
    model="Qwen/Qwen2.5-7B-Instruct",
    structured_output=False,
    max_retries=5,
)
```

### Comparing Providers

| Provider | Cost (relative) | Code Quality | Speed | Best For |
|----------|----------------|--------------|-------|----------|
| OpenAI GPT-4o | $$$$ | ★★★★★ | ★★★★ | Complex charts, dashboards |
| OpenAI GPT-4o-mini | $$ | ★★★★ | ★★★★★ | High-volume, simple charts |
| DeepSeek-V3 | $ | ★★★★★ | ★★★★ | Best value, Chinese charts |
| GLM-4-Plus | $$ | ★★★★ | ★★★★ | Chinese-language charts |
| Local (Qwen 7B) | Free | ★★★ | ★★★ | Prototyping, offline use |

---

## Workflow Patterns & Cookbook

### Pattern 1: Quick Exploration (Jupyter)

```python
# Rapid charting — skip save(), use show()
lp = llmPIC(api_key="...", base_url="...")

lp.plot("Sales distribution").data(df).render().show()
lp.bar("Top 10 products").data(products_df).render().show()
lp.scatter("Age vs spend").data(users_df).render().show()
lp.heatmap("Correlation").data(df.corr()).render().show()
```

### Pattern 2: Presentation-Quality Report

```python
# Consistent style for all charts in a report
REPORT_STYLE = {
    "figsize": [12, 7],
    "dpi": 200,
    "color_scheme": "dark",
    "title_fontsize": 18,
    "label_fontsize": 14,
    "tick_fontsize": 12,
    "grid": True,
    "grid_alpha": 0.3,
}

lp.plot("Revenue trend").data(df).style(REPORT_STYLE).save("report_revenue.png")
lp.bar("Regional breakdown").data(df).style(REPORT_STYLE).save("report_regional.png")
lp.pie("Segment share").data(df).style(REPORT_STYLE).save("report_segments.png")
lp.scatter("Customer segments").data(df).style(REPORT_STYLE).save("report_scatter.png")
```

### Pattern 3: Build & Iterate

```python
# Start rough, refine step by step
r = lp.plot("Monthly sales").data(df).render()
r = r.edit("Add 12-month moving average line")
r = r.edit("Highlight the peak month with annotation")
r = r.edit("Title '2024 Sales Performance', subtitle 'with 12-month MA'")
r = r.edit("Use dark theme, increase resolution to 200 DPI")
r.save("final_sales_analysis.png")
```

### Pattern 4: Multi-Format Pipeline

```python
# One LLM call, all three formats
result = lp.bar("Annual revenue by category").data(df).render()

result.save("report.png")      # For embedding in Word/Google Docs
result.save("report.svg")      # For web — infinitely scalable
result.save("report.pdf")      # For printing

# Or access programmatically
png_bytes = result.image_bytes
svg_html = result.base64_svg()  # Ready for <img src="...">
pdf_bytes = result.pdf_bytes
```

### Pattern 5: Automated Reporting Pipeline

```python
import asyncio
from llmpic import AsyncllmPIC

async def generate_daily_report(date_str, metrics_df):
    lp = AsyncllmPIC(
        api_key=os.getenv("LLMPIC_API_KEY"),
        base_url=os.getenv("LLMPIC_BASE_URL"),
    )

    results = await lp.batch([
        ("plot", f"DAU trend for {date_str}"),
        ("bar", f"Top 10 features used on {date_str}"),
        ("pie", f"Traffic source breakdown for {date_str}"),
        ("heatmap", f"Hourly activity heatmap for {date_str}"),
    ])

    paths = []
    for i, r in enumerate(results):
        if r.success:
            path = f"reports/{date_str}/chart_{i}.png"
            r.save(path)
            paths.append(path)
        else:
            print(f"Chart {i} failed: {r.error_message}")

    return paths

# Run: asyncio.run(generate_daily_report("2025-01-15", df))
```

### Pattern 6: Reusable Chart Function

```python
def chart_timeseries(df, date_col, value_col, title, style=None):
    """Create a consistently styled timeseries chart."""
    base_style = {
        "figsize": [14, 6],
        "color_scheme": "blues",
        "title_fontsize": 16,
        "label_fontsize": 12,
        "dpi": 150,
    }
    if style:
        base_style.update(style)

    result = lp.plot(f"{title}: {value_col} over time").data(df).style(base_style).render()
    return result

# Usage
cpu_chart = chart_timeseries(df, "date", "cpu_usage", "Server CPU")
mem_chart = chart_timeseries(df, "date", "mem_usage", "Server Memory",
                             style={"color_scheme": "warm"})
```

### Pattern 7: A/B Test Visualization

```python
# Side-by-side comparison
lp.subplots("1 row 2 cols: Control group conversion trend, Treatment group conversion trend").data({
    "control": control_df,
    "treatment": treatment_df,
}).save("ab_test.png")

# Overlaid comparison
lp.plot("Conversion rates: Control vs Treatment over time, with confidence bands").data({
    "control": control_df["rate"],
    "treatment": treatment_df["rate"],
}).save("ab_overlay.png")
```

### Pattern 8: Debugging by Inspecting Generated Code

```python
result = lp.plot("Complex multi-series chart").data(df).render()

if not result.success:
    print(f"Error: {result.error_message}")
else:
    # Inspect the code the LLM generated
    print("=== Generated Code ===")
    print(result.code)
    print(f"\n=== Token Usage: {result.token_usage} ===")

# Tweak the generated code manually if needed (advanced)
# You can take result.code, modify it, and feed it back via a custom approach
```

---

## Cost Optimization

### 1. Choose the Right Model

```python
# Most expensive, best quality
lp = llmPIC(..., model="gpt-4o")

# ~10x cheaper, still very good for simple charts
lp = llmPIC(..., model="gpt-4o-mini")

# Very cost-effective, especially for Chinese users
lp = llmPIC(..., model="deepseek-chat", base_url="https://api.deepseek.com/v1")
```

### 2. Be Specific (Reduces Retries & Fixes)

```python
# Good: Data in the prompt → fewer follow-up calls
lp.bar("Q1 Budget: R&D=$200K, Marketing=$150K, Sales=$180K")

# Less efficient: Vague → LLM may need retries
lp.bar("Department budgets")
```

### 3. Provide Data → Fewer Fix Attempts

```python
# Good: LLM sees column names, types, first rows
lp.plot("Trend").data(df)

# Less efficient: LLM guesses data structure, may fail
lp.plot("Trend")
```

### 4. Batch with Async

```python
# 5 charts sequentially = 5 × (LLM time + sandbox time)
# 5 charts in batch = max(LLM time) + max(sandbox time)

# For 3+ charts, batch is significantly cheaper in wall-clock time
# (same token cost, but better utilization)
```

### 5. Track Token Usage

```python
total_input = 0
total_output = 0

for query in queries:
    r = lp.plot(query).render()
    if r.success:
        total_input += r.token_usage.get('input', 0)
        total_output += r.token_usage.get('output', 0)

print(f"Session: {total_input} input tokens, {total_output} output tokens")
print(f"Approximate cost (GPT-4o): ${total_input * 2.5 / 1e6 + total_output * 10 / 1e6:.4f}")
```

### 6. Cache SDK Instances

Don't create a new `llmPIC` instance for each chart — reuse the same instance.

```python
# Good: reuse
lp = llmPIC(...)
charts = [lp.plot(q).save(f"{i}.png") for i, q in enumerate(queries)]

# Bad: creates new client each time
for q in queries:
    lp = llmPIC(...)  # New sandbox, font check, etc.
    lp.plot(q).save(...)
```

---

## Integration Patterns

### Jupyter Notebook Best Practices

```python
%matplotlib inline  # Optional — llmpic handles display independently

from llmpic import llmPIC
lp = llmPIC(api_key="...", base_url="...")

# Exploratory: show() inline
lp.plot("Distribution of user ages").data(df).render().show()

# When done exploring, save for the report
lp.plot("Distribution of user ages").data(df).style({
    "figsize": [10, 6],
    "dpi": 200,
}).save("report_age_dist.png")
```

### Streamlit / Gradio Integration

```python
import streamlit as st
from llmpic import llmPIC

lp = llmPIC(
    api_key=st.secrets["LLMPIC_API_KEY"],
    base_url=st.secrets["LLMPIC_BASE_URL"],
)

st.title("AI Chart Generator")
query = st.text_input("Describe your chart:", "Monthly sales trend")

if st.button("Generate"):
    result = lp.plot(query).render()
    if result.success:
        st.image(result.image_bytes)
        st.code(result.code, language="python")
    else:
        st.error(result.error_message)
```

### FastAPI / Flask Integration

```python
from fastapi import FastAPI
from fastapi.responses import Response
from llmpic import llmPIC
import os

app = FastAPI()

lp = llmPIC(
    api_key=os.getenv("LLMPIC_API_KEY"),
    base_url=os.getenv("LLMPIC_BASE_URL"),
)

@app.post("/chart")
async def create_chart(query: str, format: str = "png"):
    result = lp.custom(query).format(format).render()
    if not result.success:
        return {"error": result.error_message}

    media_type = {"png": "image/png", "svg": "image/svg+xml", "pdf": "application/pdf"}
    return Response(content=result.image_bytes, media_type=media_type.get(format, "image/png"))
```

### Data Pipeline Integration

```python
# In a data pipeline: generate daily/weekly KPI charts
def generate_kpi_charts(date, kpi_df):
    style = {"figsize": [12, 6], "dpi": 150, "color_scheme": "dark"}

    charts = {
        "revenue": lp.plot(f"Daily revenue trend").data(kpi_df).style(style),
        "users": lp.plot(f"Daily active users").data(kpi_df).style(style),
        "conversion": lp.plot(f"Conversion rate trend").data(kpi_df).style(style),
    }

    for name, builder in charts.items():
        builder.save(f"kpi/{date}/{name}.png")
```

---

## Best Practices

### 1. Use Fast Safety Mode for Production

`safety_level="fast"` is sufficient. The sandbox provides real isolation.

### 2. Use Async Batch for Multiple Charts

```python
# Good: 3 charts in ~2-3 seconds
results = await lp.batch([(...), (...), (...)])

# Bad: 3 charts in ~6-9 seconds
for query in queries:
    lp.plot(query).save(...)
```

### 3. Be Specific in Prompts

```python
# Good — data and intent are explicit
lp.bar("Q1 Budget: R&D=$200K, Marketing=$150K, Sales=$180K, HR=$100K")

# Poor — too vague, LLM must guess
lp.bar("Department budgets")
```

### 4. Provide Real Data

Pass DataFrames whenever you have them — less guesswork, more accurate charts:

```python
lp.plot("Trend").data(df)  # Good: LLM sees actual data structure
lp.plot("Trend")            # OK: LLM invents demo data
```

### 5. Iterate with edit(), Don't Re-describe

```python
# Good: incremental refinement
result = lp.plot("Sales trend").data(df).render()
result = result.edit("Increase title size")
result = result.edit("Add grid lines")
result = result.edit("Switch to warm colors")

# Less good: re-describing everything for each tweak
lp.plot("Sales trend, large title").data(df).save("v1.png")
lp.plot("Sales trend, large title, with grid").data(df).save("v2.png")
lp.plot("Sales trend, large title, with grid, warm colors").data(df).save("v3.png")
```

### 6. Set Reasonable Timeouts

```python
# Simple charts: default timeout=30 is fine
lp.plot("Line chart").render()

# Complex dashboards: increase timeout
lp.subplots("4x4 dashboard").render()  # with timeout=60
lp = llmPIC(..., timeout=60)
```

### 7. Track Token Usage

Monitor consumption to understand costs:

```python
result = lp.plot("test").render()
print(f"Input: {result.token_usage['input']}, Output: {result.token_usage['output']}")
```

### 8. Use .custom() When Unsure

The auto-detect chart type often makes good choices:

```python
# Let the LLM decide the best visualization
lp.custom("Analyze user retention with multiple factors").data(df).save("auto.png")
```

### 9. Reuse the SDK Instance

```python
# Create once, use many times
lp = llmPIC(...)
for chart_name, query in chart_configs.items():
    lp.plot(query).save(f"{chart_name}.png")
```

### 10. Check success Before Using Results

```python
result = lp.plot("Complex chart").render()
if result.success:
    result.save("output.png")
    print(f"Generated {len(result.code)} chars of code, {result.size_kb:.1f}KB")
else:
    print(f"Failed: {result.error_message}")
    # Optionally: try with different model or simplified query
```

---

## Troubleshooting

### Chinese characters display as boxes (□□□)

**Cause**: Missing CJK fonts on the system.

**Fix**:
- **Windows**: Install "Microsoft YaHei" or "SimHei" font
- **Linux**: `sudo apt install fonts-wqy-microhei`
- **macOS**: Usually pre-installed; verify with Font Book

Or set `chinese_font=False` for English-only charts.

### LLM returns "no code" or empty result

**Cause**: Query too vague, model can't understand what chart to make.

**Fix**:
- Add more detail to the query: "line chart of monthly sales, 12 data points"
- Provide data via `.data()`
- Try a different model (e.g., `gpt-4o` instead of `gpt-4o-mini`)

### Timeout: "Code execution timed out (30s)"

**Cause**: Generated code has an infinite loop, or chart is too complex.

**Fix**:
1. Increase timeout: `llmPIC(..., timeout=60)`
2. Simplify the query — split a complex dashboard into separate charts
3. Sample large datasets before passing: `df.sample(1000)`

### Auto-fix not triggering

**Check**:
- `max_fix_attempts > 0` (default 2)
- Failure is a **code execution error** (not safety rejection or timeout)
- Enable logging to see auto-fix activity:
  ```python
  import logging
  logging.basicConfig(level=logging.INFO)
  ```

### SVG/PDF files won't open

**Cause**: Wrong program to open the file.

**Fix**:
- **SVG**: Open in a browser (Chrome/Firefox) or vector editor (Inkscape, Illustrator)
- **PDF**: Open in a PDF reader (Adobe Reader, Preview, browser)
- Use `result.base64_svg()` to embed in HTML for preview

### `ModuleNotFoundError: No module named 'llmpic'`

**Fix**:
```bash
pip install llmpic           # Production install
# or for dev:
pip install -e .             # Editable dev install from repo root
```

### `RuntimeError: no running event loop` with async

**Cause**: Using `await` outside an async context.

**Fix**:
```python
async def main():
    lp = AsyncllmPIC(...)
    await lp.plot("test").save("test.png")

asyncio.run(main())  # ← Required wrapper
```

### Chart looks different from what I described

**Cause**: Natural language is inherently ambiguous; LLMs interpret requests.

**Fix**:
- Be more specific: instead of "make it look better", say "increase title size to 18, use warm colors, add grid"
- Use `.edit()` to iteratively refine
- Provide data — charts are more accurate with actual data structure visible

### Large chart files

**Cause**: High DPI + large figsize = large PNG files.

**Fix**:
```python
# For web: lower DPI, use SVG
lp.plot("web chart").style({"dpi": 72, "figsize": [8, 5]}).format('svg').save("web.svg")

# For print: high DPI is expected
lp.plot("print chart").style({"dpi": 300}).save("print.png")
```

### pandas or seaborn not available

**Cause**: pandas / seaborn not properly installed in the environment (e.g. version conflicts).

**Fix**:
```bash
pip install llmpic --upgrade
# or install them individually
pip install pandas seaborn
```

The SDK gracefully falls back to pure matplotlib when pandas/seaborn aren't available, but some LLM-generated code may reference them.

### Rate limiting from API provider

**Cause**: Too many concurrent requests hitting rate limits.

**Fix**:
- Reduce batch size
- Add delays between batches
- Use a higher-tier API plan

```python
# Process in chunks of 3
for i in range(0, len(requests), 3):
    chunk = requests[i:i+3]
    results = await lp.batch(chunk)
    await asyncio.sleep(2)  # Respect rate limits
```

---

← [Back to Home](../index.md)
