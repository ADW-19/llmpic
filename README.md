<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <a href="https://github.com/ADW-19/llmpic"><img src="https://img.shields.io/badge/github-ADW--19%2Fllmpic-lightgrey.svg" alt="GitHub"></a>
  <img src="https://img.shields.io/badge/python-≥3.10-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/version-0.2.1-orange.svg" alt="Version">
</p>

<h1 align="center">llmpic</h1>
<p align="center"><strong>Natural Language Chart Generation Python SDK</strong></p>

<p align="center">
  <a href="./doc/chinese/README_CN.md">中文（chinese）</a>
</p>

---

```python
from llmpic import llmPIC

lp = llmPIC(api_key="sk-...", base_url="https://api.openai.com/v1")

# Describe it. Get a chart.
lp.plot("30-day CPU usage trend").show()   # Jupyter inline display
lp.plot("CPU usage trend").save()           # → ~/llmpic_charts/
```

---

## 💡 Why llmpic?

Traditionally, creating charts in Python means wrestling with matplotlib's verbose API — `plt.subplots()`, `ax.set_xticklabels()`, `fig.tight_layout()` — hundreds of functions to memorize, dozens of lines for a single chart. Data scientists spend more time googling matplotlib syntax than analyzing data.

**llmpic** brings Python charting into the **LLM era**. For data scientists, analysts, quantitative researchers — anyone who needs charts from data — just describe what you want in plain language and get production-quality matplotlib charts instantly.

| | Traditional matplotlib | llmpic |
|---|---|---|
| Lines of code | 15–40 lines | **1–3 lines** |
| API knowledge | 100+ functions | **0** (natural language) |
| Chart types | Manual selection | **11 types + auto-detect** |
| Iteration | Rewrite entire block | **`result.edit("...")`** |
| Jupyter | `plt.show()` only | **`result.show()` inline** |
| Multi-format | Separate savefig calls | **Single `save()`** |
| Error recovery | Manual debugging | **Auto-fix with LLM** |

---

## ✨ Features

- 🗣️ **Natural Language Input** — describe charts in plain English, Chinese, Japanese, or Korean
- 📊 **11 Chart Types** — Line, Scatter, Bar, Pie, Histogram, Heatmap, Boxplot, Area, Radar, Subplots, Auto-detect
- 📓 **Jupyter Inline** — `result.show()` renders charts directly below notebook cells
- ⚡ **Async Batch** — `AsyncllmPIC.batch()` generates multiple charts concurrently
- 🔧 **Auto-Fix** — failed code executions are auto-corrected by the LLM (up to 2 rounds)
- ✏️ **Iterative Editing** — `result.edit("make bars red")` refines charts with natural language
- 📦 **Multi-Format** — single `save()` with extension auto-detection (PNG/SVG/PDF), defaults to home directory
- 🌍 **Multi-Language Labels** — auto-detects query language and matches chart labels (zh/ja/ko/en)
- 🛡️ **Dual Safety** — 31 precompiled regex patterns + optional LLM semantic review
- 💻 **Cross-Platform** — Windows / Linux / macOS, automatic CJK font configuration

---

## 📦 Installation

```bash
pip install llmpic          # minimal
pip install llmpic[full]    # + pandas, seaborn, scikit-learn
```

Requires **Python ≥ 3.10** and an **OpenAI-compatible API** endpoint (OpenAI, Azure, DeepSeek, etc.).

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [API Reference](./doc/english/API_REFERENCE_EN.md) | Complete class, method, and parameter reference |
| [User Guide](./doc/english/GUIDE_EN.md) | Advanced usage, best practices, troubleshooting |
| [中文文档](./doc/chinese/README_CN.md) | Full documentation in Chinese |
| [Jupyter Demos](./notebook_examples/) | Ready-to-run Jupyter notebooks |

---

## 🚀 Quick Start

```python
from llmpic import llmPIC

lp = llmPIC(
    api_key="sk-your-key",
    base_url="https://api.openai.com/v1",
    model="gpt-4o",
)

# Basic — one line, one chart
lp.plot("12-month sales trend").save("sales.png")

# With data & style
import pandas as pd
df = pd.read_csv("sales.csv")
lp.bar("Sales by region").data(df).style({
    "color_scheme": "warm",
    "figsize": [12, 7],
}).save("bar.png")

# Jupyter inline display
lp.plot("CPU usage trend").render().show()

# SVG / PDF export
lp.plot("trend").save("chart.svg")
lp.plot("trend").save("chart.pdf")

# Iterative editing
r = lp.plot("Quarterly sales: Q1=100,Q2=150").render()
r.edit("change to bar chart, red").edit("title 'Annual Report'").show()

# Default save path (no argument → home directory)
lp.plot("simple trend").save()  # → ~/llmpic_charts/chart_{timestamp}.png
```

### Async Batch

```python
from llmpic import AsyncllmPIC
import asyncio

async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="https://api.openai.com/v1")

    results = await lp.batch([
        ("plot",     "12-month national sales trend"),
        ("bar",      "Sales comparison by region"),
        ("pie",      "Market share distribution"),
        ("scatter",  "Customer age vs spend"),
        ("heatmap",  "Correlation matrix"),
    ])

    for i, r in enumerate(results):
        r.save(f"chart_{i}.png")

asyncio.run(main())
```

---

## 📊 Chart Types

| Method | Type |
|--------|------|
| `.plot()` | Line |
| `.scatter()` | Scatter |
| `.bar()` | Bar |
| `.pie()` | Pie |
| `.hist()` | Histogram |
| `.heatmap()` | Heatmap |
| `.boxplot()` | Boxplot |
| `.area()` | Area |
| `.radar()` | Radar |
| `.subplots()` | Dashboard |
| `.custom()` | Auto-detect |

---

## 📄 License

[MIT](./LICENSE) © 2026 ADW-19
