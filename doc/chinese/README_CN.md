<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <a href="https://github.com/ADW-19/llmpic"><img src="https://img.shields.io/badge/github-ADW--19%2Fllmpic-lightgrey.svg" alt="GitHub"></a>
  <img src="https://img.shields.io/badge/python-≥3.10-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/version-0.2.1-orange.svg" alt="Version">
</p>

<p align="center"><img src="../../llmpic_logo.png" alt="llmpic logo" width="120"></p>

<h1 align="center">LLMPIC</h1>
<p align="center"><strong>自然语言驱动的图表生成 Python SDK</strong></p>

<p align="center">
  <a href="../../README.md">English(英语)</a>
</p>

---

```python
from llmpic import llmPIC

lp = llmPIC(api_key="sk-...", base_url="https://api.openai.com/v1")

# 说人话，出图表。
lp.plot("过去30天CPU使用率趋势").show()   # Jupyter 内联显示
lp.plot("CPU使用率趋势").save()             # → ~/llmpic_charts/
```

---

## 💡 为什么选择 llmpic？

传统 Python 画图，你需要死记硬背 matplotlib 那一大堆 API —— `plt.subplots()`、`ax.set_xticklabels()`、`fig.tight_layout()` —— 上百个函数名，一张图几十行代码。数据科学家们花在查 matplotlib 文档上的时间，比真正分析数据的时间还多。

**llmpic** 让 Python 绘图进入了**大模型时代**。面向数据科学家、数据分析师、量化研究员等所有需要用 Python 画图的用户，只需要用人话描述需求，即刻生成高质量 matplotlib 图表。

| | 传统 matplotlib 画图 | llmpic |
|---|---|---|
| 代码量 | 15–40 行 | **1–3 行** |
| API 门槛 | 100+ 函数 | **0**（自然语言） |
| 图表类型 | 手动选择 | **11 种 + 智能推荐** |
| 反复修改 | 重写大段代码 | **`result.edit("...")`** |
| Jupyter | 仅 `plt.show()` | **`result.show()` 内联** |
| 多格式导出 | 多次 savefig | **一个 `save()` 搞定** |
| 报错处理 | 人工调试 | **LLM 自动修复** |

---

## ✨ 特性

- 🗣️ **自然语言输入** — 描述需求即可生成图表，支持中、英、日、韩文
- 📊 **11 种图表类型** — 折线图、散点图、柱状图、饼图、直方图、热力图、箱线图、面积图、雷达图、子图仪表盘、智能推荐
- 📓 **Jupyter 内联显示** — `result.show()` 直接在 Notebook cell 下方渲染图表
- ⚡ **异步批量生成** — `AsyncllmPIC.batch()` 多图表并发生成
- 🔧 **自动修复** — 代码执行出错时 LLM 自动修正，最多 2 轮
- ✏️ **迭代编辑** — `result.edit("改成红色")` 用自然语言修改已有图表
- 📦 **多格式导出** — 一个 `save()` 搞定 PNG/SVG/PDF，默认保存到用户主目录
- 🌍 **多语言标签** — 自动检测查询语言，图表标题/坐标轴自动匹配
- 🛡️ **双重安全** — 31 条预编译正则 + 可选 LLM 语义审查
- 💻 **跨平台** — Windows / Linux / macOS 全兼容，中日韩字体自动配置

## 📦 安装

```bash
pip install llmpic          # 基础版
pip install llmpic[full]    # + pandas, seaborn, scikit-learn
```

需要 **Python ≥ 3.10** 和 **OpenAI 兼容 API**（支持 OpenAI、Azure、DeepSeek 等）。

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [API 参考](./API_REFERENCE_CN.md) | 所有类、方法、参数的详细说明 |
| [使用指南](./GUIDE_CN.md) | 进阶用法、最佳实践、故障排查 |
| [English Docs](../english/README_EN.md) | 完整英文文档 |
| [Jupyter 示范](../../notebook_examples/) | 开箱即用的 Jupyter Notebook |

---

## 🚀 快速入门

```python
from llmpic import llmPIC

lp = llmPIC(
    api_key="sk-your-key",
    base_url="https://api.openai.com/v1",
    model="gpt-4o",
)

# 基础 — 一句话出图
lp.plot("过去12个月月度销售趋势").save("sales.png")

# 带数据和样式
import pandas as pd
df = pd.read_csv("sales.csv")
lp.bar("各地区销售额对比").data(df).style({
    "color_scheme": "warm",
    "figsize": [12, 7],
}).save("bar.png")

# Jupyter 内联显示
lp.plot("CPU使用率趋势").render().show()

# SVG / PDF 导出
lp.plot("趋势").save("chart.svg")
lp.plot("趋势").save("chart.pdf")

# 迭代编辑
r = lp.plot("季度销售: Q1=100,Q2=150").render()
r.edit("改成柱状图，红色").edit("标题改为'年报'").show()

# 默认保存路径（不传参数 → 用户主目录）
lp.plot("简单趋势").save()  # → ~/llmpic_charts/chart_{timestamp}.png
```

### 异步批量生成

```python
from llmpic import AsyncllmPIC
import asyncio

async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="https://api.openai.com/v1")

    results = await lp.batch([
        ("plot",     "全国12个月销售趋势"),
        ("bar",      "各地区销售额对比"),
        ("pie",      "市场份额分布"),
        ("scatter",  "客户年龄vs消费金额"),
        ("heatmap",  "相关性矩阵"),
    ])

    for i, r in enumerate(results):
        r.save(f"chart_{i}.png")

asyncio.run(main())
```

---

## 📊 图表类型

| 方法 | 类型 |
|------|------|
| `.plot()` | 折线图 |
| `.scatter()` | 散点图 |
| `.bar()` | 柱状图 |
| `.pie()` | 饼图 |
| `.hist()` | 直方图 |
| `.heatmap()` | 热力图 |
| `.boxplot()` | 箱线图 |
| `.area()` | 面积图 |
| `.radar()` | 雷达图 |
| `.subplots()` | 子图仪表盘 |
| `.custom()` | 智能推荐 |

## 📮 官方联系方式

- **小红书 ID**：[ADW_AI](https://xhslink.com/m/AQw13M5WIPc)

---

## 📄 License

[MIT](../../LICENSE) © 2026 ADW-19
