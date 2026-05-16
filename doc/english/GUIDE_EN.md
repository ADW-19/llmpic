# User Guide — llmpic

> Advanced usage, best practices, and troubleshooting.

---

## Table of Contents

- [Chart Types in Detail](#chart-types-in-detail)
- [Data Input Methods](#data-input-methods)
- [Style Customization](#style-customization)
- [Output Formats](#output-formats)
- [Iterative Editing](#iterative-editing)
- [Auto-Fix Mechanism](#auto-fix-mechanism)
- [Async & Batch Generation](#async--batch-generation)
- [Security Model](#security-model)
- [Multi-Language Support](#multi-language-support)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Chart Types in Detail

### plot — Line Chart

Best for trends, time series, continuous data.

```python
lp.plot("Monthly revenue trend for 2024").save("revenue.png")
lp.plot("sin(x) and cos(x) from 0 to 2π").save("trig.png")
```

LLM hint: `Line chart. Use ax.plot(). Multiple series: different colors + legend.`

### scatter — Scatter Chart

Best for correlation analysis, cluster visualization.

```python
lp.scatter("User age vs purchase amount correlation").data(df).save("scatter.png")
```

### bar — Bar Chart

Best for categorical comparison, rankings.

```python
lp.bar("Quarterly budget per department: R&D=200, Marketing=150, Sales=180, HR=100").save("budget.png")
```

### pie — Pie Chart

Best for proportions, market share.

```python
lp.pie("Market share: Product A 40%, B 25%, C 20%, Others 15%").save("market.png")
```

### hist — Histogram

Best for distributions, frequency analysis.

```python
lp.hist("Student exam score distribution, mean 70, std 15").data(scores).save("hist.png")
```

### heatmap — Heatmap

Best for correlation matrices, 2D density.

```python
lp.heatmap("Product sales correlation matrix").data(corr_df).save("heatmap.png")
```

LLM hint: `Heatmap. Use ax.imshow() or sns.heatmap(). Add colorbar and annotate cells.`

### boxplot — Boxplot

Best for statistical distribution comparison across groups.

```python
lp.boxplot("Distribution comparison across A/B/C experiment groups").save("boxplot.png")
```

### area — Area Chart

Best for stacked trends, compositional changes over time.

```python
lp.area("Revenue composition by product line 2020–2024").data(revenue_df).save("area.png")
```

LLM hint: `Area chart. Use ax.fill_between() or ax.stackplot(). Set alpha 0.3-0.7.`

### radar — Radar Chart

Best for multi-dimensional comparison, capability assessment.

```python
lp.radar("Product ratings: Performance=4, Usability=3, Reliability=5, Price=2, Support=4").save("radar.png")
```

LLM hint: `Radar chart. Use polar axes: plt.subplots(subplot_kw={'projection':'polar'}). Close the polygon loop.`

### subplots — Dashboard

Best for multi-chart composite views.

```python
lp.subplots("2x2 dashboard: sales trend line, region bar, customer scatter, growth histogram").save("dashboard.png")
```

LLM hint: `Dashboard. Use fig, axes = plt.subplots(nrows, ncols). Add fig.suptitle(). Each subplot is different.`

### custom — Auto-Detect

LLM selects the best chart type automatically.

```python
lp.custom("Analyze user retention trends and contributing factors").data(df).save("auto.png")
```

---

## Data Input Methods

### No Data — LLM Generates Demo Data

```python
lp.plot("Sine wave").save("demo.png")
# LLM auto-generates: np.linspace + np.sin
```

### DataFrame (Recommended)

```python
import pandas as pd
df = pd.DataFrame({
    "Month": ["Jan","Feb","Mar","Apr","May","Jun"],
    "Sales": [120, 135, 148, 162, 155, 180],
    "Profit": [20, 28, 30, 35, 32, 40],
})
lp.plot("Monthly sales vs profit trend").data(df).save("sales.png")
```

What the LLM receives: column names, dtypes, first 5 rows, statistical summary.

### NumPy Array

```python
import numpy as np
data = np.random.randn(1000)
lp.hist("Data distribution").data(data).save("dist.png")
```

### Dictionary

```python
lp.bar("Sales by city").data({
    "City": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen"],
    "Sales": [320, 280, 260, 240],
}).save("city.png")
```

### List / Tuple

```python
lp.plot("Temperature trend").data([22, 24, 19, 26, 28, 25, 23]).save("temp.png")
```

### Raw String

Long strings are truncated to 2000 characters.

---

## Style Customization

### Quick Color Schemes

```python
# 6 preset color schemes
lp.plot("Trend").style({"color_scheme": "blues"}).save("b.png")
lp.plot("Trend").style({"color_scheme": "warm"}).save("w.png")
lp.plot("Trend").style({"color_scheme": "cool"}).save("c.png")
lp.plot("Trend").style({"color_scheme": "pastel"}).save("p.png")
lp.plot("Trend").style({"color_scheme": "dark"}).save("d.png")
lp.plot("Trend").style({"color_scheme": "grayscale"}).save("g.png")
```

### Size & Font

```python
lp.plot("Trend").style({
    "figsize": [14, 7],         # 14" wide x 7" tall
    "title_fontsize": 18,        # Title size
    "label_fontsize": 14,        # Axis label size
    "tick_fontsize": 12,         # Tick label size
    "dpi": 200,                  # Output resolution
}).save("large.png")
```

### Grid & Background

```python
lp.plot("Trend").style({
    "grid": True,
    "grid_alpha": 0.5,           # Darker grid
    "facecolor": "#F5F5F5",      # Light gray background
    "tight_layout": True,
}).save("grid.png")

# Or turn off grid
lp.plot("Trend").style({"grid": False}).save("nogrid.png")
```

### Combined

```python
lp.bar("Sales comparison").data(df).style({
    "figsize": [12, 8],
    "color_scheme": "warm",
    "title_fontsize": 16,
    "grid": False,
    "dpi": 200,
}).save("styled.png")
```

---

## Output Formats

### PNG (Default)

```python
lp.plot("Trend").save("chart.png")
# Or explicit
lp.plot("Trend").format('png').render()
```

### SVG — Vector, ideal for web embedding

```python
# Method 1: chained
lp.plot("Trend").format('svg').save("chart.svg")

# Method 2: from existing result, extension auto-detects format
result = lp.plot("Trend").render()
result.save("chart.svg")    # → SVG

# base64 for HTML embedding
svg_uri = result.base64_svg()
# Use in HTML: <img src="{svg_uri}" />
```

### PDF — For printing and reports

```python
lp.plot("Trend").format('pdf').save("chart.pdf")
# Or
result = lp.plot("Trend").render()
result.save("chart.pdf")    # → PDF
```

### Default Save Path

```python
result = lp.plot("Trend").render()
result.save()               # → ~/llmpic_charts/chart_20250101_120000.png
```

### Jupyter Notebook Inline Display

```python
result = lp.plot("CPU trend").render()
result.show()  # Renders directly below the cell, no save() needed
```

---

## Iterative Editing

Modify charts with natural language — ideal for iterative refinement.

### Basic Usage

```python
# First version
v1 = lp.plot("Monthly sales: Jan=100, Feb=120, Mar=90, Apr=150").render()
v1.save("v1.png")

# Edit with natural language
v2 = v1.edit("Change to bar chart")
v2.save("v2.png")

v3 = v2.edit("Make bars red, title 'Q1 2025 Sales'")
v3.save("v3.png")

v4 = v3.edit("Add grid, increase title size")
v4.save("v4.png")
```

### How edit() Works

1. Sends current code + edit request to LLM
2. LLM returns modified code
3. Safety check → sandbox execution → new ChartResult

**Note**: `.edit()` returns a **new** ChartResult, never mutates the original.

---

## Auto-Fix Mechanism

### Workflow

```
Generate code → Safety check → Sandbox execution
                                 ↓ failure
                            LLM fix code
                                 ↓
                        Safety check → Sandbox execution
                                 ↓ failure again
                            LLM fix again (up to max_fix_attempts times)
```

### Configuration

```python
lp = llmPIC(
    ...,
    max_fix_attempts=2,   # default 2
)
# Set to 0 to disable
```

### When Auto-Fix Triggers

Auto-fix only triggers on **code execution failures** (e.g., `NameError`, `ValueError` from matplotlib). It does **not** trigger on:

- LLM returning no code (handled by `max_retries`)
- Safety check rejection (dangerous code is rejected outright)
- Timeout (possible infinite loop — not retried)

---

## Async & Batch Generation

### Single Async Chart

```python
import asyncio
from llmpic import AsyncllmPIC

async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="...")
    await lp.plot("CPU trend").save("cpu.png")

asyncio.run(main())
```

### Batch Concurrent Generation

```python
async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="...")

    results = await lp.batch([
        ("plot", "CPU usage trend"),
        ("bar", "Department budget comparison"),
        ("scatter", "User behavior scatter"),
        ("heatmap", "Correlation matrix"),
        ("pie", "Market share distribution"),
    ])

    # All charts generated concurrently — total time ≈ slowest single chart
    for i, r in enumerate(results):
        if r.success:
            r.save(f"batch_{i}.png")
            print(f"[{i}] OK, tokens: in={r.token_usage['input']}, out={r.token_usage['output']}")
        else:
            print(f"[{i}] FAIL: {r.error_message}")

asyncio.run(main())
```

### Mixed Formats in Batch

```python
async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="...")

    builders = [
        lp.plot("Trend").format('png'),
        lp.plot("Trend").format('svg'),
        lp.plot("Trend").format('pdf'),
    ]
    import asyncio
    results = await asyncio.gather(*[b.render() for b in builders])
    print(results)

asyncio.run(main())
```

---

## Security Model

### Dual-Layer Protection

| Layer | Mechanism | Latency | Coverage |
|-------|-----------|---------|----------|
| Layer 1 | 32 precompiled regex patterns | ~0ms | Blocks known dangerous patterns |
| Layer 2 | LLM semantic review (optional) | ~1-2s | Catches obfuscation & novel variants |

### Blocked Operations

- System commands: `os.system()`, `os.popen()`, `subprocess`
- File I/O: `open()` (generated code has no reason to access files)
- Dynamic execution: `exec()`, `eval()`, `compile()`, `__import__()`
- Network: `socket`, `urllib`, `requests`, `httpx`
- Dangerous modules: `shutil`, `ctypes`, `pickle`
- Reflection escapes: `__subclasses__()`, `__bases__`, `globals()`, `setattr()`

### Choosing Safety Level

```python
# Fast mode (default, recommended for production)
lp = llmPIC(..., safety_level="fast")

# Full mode (regex + LLM review, for maximum security)
lp = llmPIC(..., safety_level="full")
```

**Recommendation**: The sandbox already blocks all real execution paths (restricted namespace + Figure.savefig interception). Fast mode is sufficient for production. Full mode adds ~1-2s latency.

---

## Multi-Language Support

### Auto-Detection

The SDK auto-detects query language and LLM matches chart labels accordingly:

```python
lp.plot("CPU使用率趋势")       # → Chinese labels
lp.plot("CPU使用量トレンド")     # → Japanese labels
lp.plot("CPU 사용량 추세")      # → Korean labels
lp.plot("CPU usage trend")      # → English labels
```

Detection is based on Unicode range analysis of CJK characters.

### Cross-Platform Fonts

| Platform | Preferred Font |
|----------|---------------|
| Windows | Microsoft YaHei → SimHei → SimSun |
| macOS | PingFang SC → Heiti SC → STHeiti |
| Linux | WenQuanYi Micro Hei → Noto Sans CJK SC |

Font detection runs once on first execution, then cached (thread-safe).

---

## Best Practices

### 1. Use Fast Safety Mode for Production

`safety_level="fast"` halves latency. The sandbox provides sufficient isolation.

### 2. Use Async Batch for Multiple Charts

```python
# Good: 3 charts in ~2-3 seconds
results = await lp.batch([(...), (...), (...)])

# Bad: 3 charts in ~6-9 seconds
for query in queries:
    lp.plot(query).save(...)
```

### 3. Be Specific in Queries

```python
# Good — data is explicit
lp.bar("Q1 Budget: R&D=$200K, Marketing=$150K, Sales=$180K")

# Poor — too vague
lp.bar("Department budgets")
```

### 4. Provide Real Data

Pass DataFrames whenever possible — less guesswork for the LLM:

```python
lp.plot("Trend").data(df)  # Good
lp.plot("Trend")            # LLM invents demo data
```

### 5. Iterate with edit()

Don't re-describe everything for small tweaks:

```python
result = lp.plot("Sales trend").data(df).render()
result = result.edit("Increase title size")
result = result.edit("Add grid")
result = result.edit("Switch to warm colors")
result.save("final.png")
```

### 6. Set Reasonable Timeouts

Complex charts (e.g., subplot dashboards) may need more time:

```python
lp = llmPIC(..., timeout=60)  # 60s for complex charts
```

### 7. Track Token Usage

Monitor consumption with `result.token_usage`:

```python
result = lp.plot("test").render()
print(f"Input: {result.token_usage['input']}, Output: {result.token_usage['output']}")
```

---

## Troubleshooting

### Issue: Chinese characters show as boxes (□□□)

**Cause**: Missing CJK fonts on the system.

**Fix**:
- Windows: Install Microsoft YaHei or SimHei
- Linux: `sudo apt install fonts-wqy-microhei`
- macOS: Usually pre-installed; ensure `chinese_font=True`

Or set `chinese_font=False` for English-only charts.

### Issue: LLM returns "no code"

**Cause**: Query too vague.

**Fix**: Rewrite with more specific description and/or provide data.

### Issue: Code execution timeout

**Cause**: Possible infinite loop or overly complex chart.

**Fix**:
1. Increase timeout: `llmPIC(..., timeout=60)`
2. Split complex charts into simpler ones
3. Sample large datasets before passing them in

### Issue: Auto-fix not triggering

**Check**:
- `max_fix_attempts > 0` (default 2)
- Failure is a code execution error (not safety or timeout)
- Check logs for auto-fix activity

### Issue: SVG/PDF won't open

**Cause**: SVG is UTF-8 XML text; PDF is binary.

**Fix**:
- Open SVG in a browser or vector graphics editor
- Open PDF in a PDF reader
- Use `base64_svg()` for HTML preview

### Issue: `ModuleNotFoundError: No module named 'llmpic'`

**Fix**:
```bash
pip install -e .         # Dev install
# or
pip install llmpic       # Production install
```

### Issue: `RuntimeError: no running event loop` with async

**Cause**: Using `await` outside an async context.

**Fix**: Wrap with `asyncio.run()`:
```python
async def main():
    lp = AsyncllmPIC(...)
    await lp.plot("test").save("test.png")

asyncio.run(main())
```

---

← [Back to Home](./README_EN.md)
