# **LLMPIC**

**Natural Language → Production Charts. One line.**

[GitHub](https://github.com/ADW-19/llmpic) | [View on PyPI](https://pypi.org/project/llmpic/) | [小红书 ADW_AI](https://xhslink.com/m/AQw13M5WIPc)

---

## Quick Start

```bash
pip install llmpic
```

```python
from llmpic import llmPIC

lp = llmPIC(api_key="sk-...", base_url="https://api.openai.com/v1")

lp.plot("Monthly sales trend, 12 months").show()   # Jupyter inline
lp.bar("Sales by region").data(df).save("bar.png") # Save to file
```

## Documentation

- [Getting Started (EN)](english/GUIDE_EN.md)
- [API Reference (EN)](english/API_REFERENCE_EN.md)
- [使用指南 (中文)](chinese/GUIDE_CN.md)
- [API 参考 (中文)](chinese/API_REFERENCE_CN.md)

## Features

- 12 chart types (Line, Scatter, Bar, Pie, Histogram, Heatmap, Boxplot, Area, Radar, Map, Subplots, Auto-detect)
- Natural language input (English, Chinese, Japanese, Korean)
- Jupyter inline rendering
- Async batch generation
- Auto-fix with LLM
- Multi-format export (PNG, SVG, PDF)
- Dual-layer security

---

License [MIT](https://github.com/ADW-19/llmpic/blob/main/LICENSE) | Version 0.3.0 | Python >= 3.10