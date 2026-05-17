# 使用指南 — llmpic

> 进阶用法、完整工作流、最佳实践、故障排查。

---

## 目录

- [快速上手](#快速上手)
- [图表类型详解](#图表类型详解)
- [数据输入方式](#数据输入方式)
- [样式定制](#样式定制)
- [输出格式](#输出格式)
- [迭代编辑](#迭代编辑)
- [自动修复机制](#自动修复机制)
- [异步与批量生成](#异步与批量生成)
- [安全模型](#安全模型)
- [多语言支持](#多语言支持)
- [各大模型服务商配置](#各大模型服务商配置)
- [实战工作流与代码模板](#实战工作流与代码模板)
- [成本优化](#成本优化)
- [系统集成方案](#系统集成方案)
- [最佳实践](#最佳实践)
- [故障排查](#故障排查)

---

## 快速上手

### SDK 初始化

```python
from llmpic import llmPIC

lp = llmPIC(
    api_key="sk-...",                    # 必填：API 密钥
    base_url="https://api.openai.com/v1",# 必填：API 地址
    model="gpt-4o",                      # 代码生成模型
    # 以下为可选参数（附默认值）：
    safety_level="fast",                 # 安全级别："fast"(仅正则) 或 "full"(正则+LLM)
    safety_model=None,                   # 安全审查模型（默认与 model 一致）
    chinese_font=True,                   # 启用中文字体支持
    timeout=30,                          # 代码执行超时（秒）
    dpi=150,                             # 默认输出分辨率
    output_dir="~/llmpic_charts",        # 默认保存目录
    temperature=0.3,                     # LLM 生成温度（0-2）
    max_tokens=2048,                     # LLM 最大输出 token 数
    structured_output=True,              # 使用 JSON 结构化输出
    max_retries=3,                       # LLM 调用失败重试次数（指数退避）
    max_fix_attempts=2,                  # 代码执行失败自动修复次数
)
```

### 参数选择指南

| 场景 | 推荐配置 |
|------|---------|
| 生产环境 / 追求速度 | `safety_level="fast"`, `model="gpt-4o-mini"` |
| 最高安全要求 | `safety_level="full"`，其他保持默认 |
| 复杂的多图仪表盘 | `timeout=60`, `max_tokens=4096` |
| 本地模型（Ollama/vLLM） | `max_retries=5`, `structured_output=False`, `max_fix_attempts=3` |
| 中文图表为主 | `chinese_font=True`（默认即可） |
| 纯英文图表、追求小体积 | `chinese_font=False`, `dpi=100` |
| 印刷/论文出版 | `dpi=300` |

---

## 图表类型详解

### plot — 折线图

适用场景：趋势分析、时间序列、连续数据。

```python
lp.plot("2024年全年营收变化趋势").save("revenue.png")
lp.plot("sin(x) 和 cos(x) 在 0 到 2π 的函数图像").save("trig.png")

# 传入真实时序数据
df = pd.read_csv("metrics.csv")  # 列：date, cpu, memory
lp.plot("CPU和内存使用量随时间变化趋势").data(df).save("metrics.png")
```

LLM 提示词：`Line chart (折线图). Use ax.plot(). Multiple series: different colors + legend.`

### scatter — 散点图

适用场景：相关性分析、聚类可视化、异常值检测。

```python
# 传入 DataFrame
lp.scatter("用户年龄与消费金额的分布关系").data(df).save("scatter.png")

# 内联数据
lp.scatter("散点图: x=[1,2,3,4,5], y=[2,4,1,8,7]").save("simple_scatter.png")

# 三维散点图（颜色/大小作为第三维）
lp.scatter("年龄vs收入，颜色按学历分组，点大小按购买频率").data(df).save("3d_scatter.png")
```

LLM 提示词：`Scatter chart (散点图). Use ax.scatter(). 3rd variable → color/size.`

### bar — 柱状图

适用场景：分类数据对比、排名、前后对比。

```python
# 描述中直接内嵌数据
lp.bar("各部门Q1预算: 研发=200万, 市场=150万, 销售=180万, 人事=100万").save("budget.png")

# 横向柱状图
lp.bar("全国GDP前十城市，横向排列").data(city_df).save("horizontal.png")

# 分组柱状图
lp.bar("各产品线月度销售额，分组柱状图").data(sales_df).save("grouped.png")

# 堆叠柱状图
lp.bar("各季度收入构成，堆叠柱状图").data(revenue_df).save("stacked.png")
```

LLM 提示词：`Bar chart (柱状图). Use ax.bar() or ax.barh(). Add value labels on bars.`

### pie — 饼图

适用场景：占比分布、市场份额、预算分配。

```python
# 内联比例
lp.pie("市场份额: A产品40%, B产品25%, C产品20%, 其他15%").save("market.png")

# 传入 DataFrame
lp.bar("各类别支出占比").data(budget_df).save("spending.png")

# 环形图（通过自然语言描述即可）
lp.pie("环形图：各部门营收占比").data(dept_df).save("donut.png")
```

LLM 提示词：`Pie chart (饼图). Use ax.pie() with autopct='%1.1f%%' and legend.`

### hist — 直方图

适用场景：数据分布、频率统计、正态性检验。

```python
# 传入原始数据
import numpy as np
data = np.random.randn(1000)
lp.hist("考试成绩分布，叠加KDE密度曲线").data(data).save("hist.png")

# 指定分箱数
lp.hist("居民收入分布，50个区间").data(income_data).save("income_hist.png")

# 多组对比
lp.hist("测试成绩: A组 vs B组，叠加直方图").data({
    "A组": np.random.normal(70, 10, 500),
    "B组": np.random.normal(75, 12, 500),
}).save("compare_hist.png")
```

LLM 提示词：`Histogram (直方图). Use ax.hist(). Overlay KDE via sns.kdeplot if seaborn available.`

### heatmap — 热力图

适用场景：相关性矩阵、二维密度、混淆矩阵。

```python
# 相关性矩阵
lp.heatmap("多特征相关性矩阵，标注数值").data(corr_df).save("corr_heatmap.png")

# 时间维度热力图
lp.heatmap("按星期几和小时统计的网站流量热力图").data(traffic_df).save("traffic_heatmap.png")
```

LLM 提示词：`Heatmap (热力图). Use ax.imshow() or sns.heatmap(). Add colorbar and annotate cells.`

### boxplot — 箱线图

适用场景：多组数据统计分布对比。

```python
# 多组对比
lp.boxplot("实验结果: 对照组 vs 实验组A vs 实验组B 的分布对比").save("boxplot.png")

# 传入 DataFrame（一列为分组，一列为数值）
lp.boxplot("各部门薪资分布对比").data(hr_df).save("salary_box.png")
```

LLM 提示词：`Boxplot (箱线图). Use ax.boxplot() or sns.boxplot(). Show outliers, add labels.`

### area — 面积图

适用场景：堆积趋势、成分随时间变化。

```python
lp.area("2020-2024年各产品线收入占比变化").data(revenue_df).save("area.png")
lp.area("堆积面积图：用户获取渠道随时间变化").data(channel_df).save("channels.png")
```

LLM 提示词：`Area chart (面积图). Use ax.fill_between() or ax.stackplot(). Set alpha 0.3-0.7.`

### radar — 雷达图

适用场景：多维指标对比、能力评估、产品对比。

```python
# 内联数据
lp.radar("产品评分: 性能=4, 易用性=3, 稳定性=5, 价格=2, 售后=4").save("radar.png")

# 双产品对比
lp.radar("雷达图: 产品A [4,3,5,2,4] vs 产品B [3,4,4,3,5], 维度: 速度,界面,稳定性,价格,服务").save("radar2.png")
```

LLM 提示词：`Radar chart (雷达图). Use polar axes: plt.subplots(subplot_kw={'projection':'polar'}). Close the polygon loop.`

### subplots — 综合仪表盘

适用场景：多图综合展示、高管汇报。

```python
# 2×2 仪表盘
lp.subplots("2x2看板: 销售额趋势折线图, 地区对比柱状图, 客户分布散点图, 月度增长直方图").save("dashboard.png")

# 1×3 仪表盘
lp.subplots("1行3列: CPU趋势, 内存趋势, 磁盘趋势").data(metrics_df).save("triple.png")

# 复杂仪表盘
lp.subplots("3x2综合看板: 营收折线, 支出对比柱状图, 利润率面积图, "
            "客户增长柱状图, 地区占比饼图, 相关性热力图").data(full_df).save("executive.png")
```

LLM 提示词：`Dashboard (子图仪表盘). Use fig, axes = plt.subplots(nrows, ncols, figsize=(w,h)). Add fig.suptitle(). Each subplot is a different chart.`

### custom — 智能推荐

适用场景：不确定该用哪种图表时。

```python
lp.custom("分析用户留存率变化趋势和影响因素").data(user_df).save("auto.png")
lp.custom("对比各特征在ML模型中的重要性").data(feature_df).save("importance.png")
```

LLM 提示词：`Pick best chart type (line/bar/scatter/pie/hist/boxplot/heatmap/area/radar) for the data & query.`

---

## 数据输入方式

### 不传数据 —— LLM 自动生成演示数据

快速探索或原型验证时，跳过 `.data()`：

```python
lp.plot("从0到2π的正弦波曲线").save("sine.png")
lp.bar("虚拟销售数据: Q1=100, Q2=150, Q3=120, Q4=180").save("demo.png")
lp.pie("虚拟市场份额: A=40%, B=30%, C=20%, D=10%").save("demo_pie.png")
```

LLM 会自动用 `np.linspace`、`np.random` 等方式生成合理的演示数据。

### DataFrame（生产环境推荐）

```python
import pandas as pd

df = pd.DataFrame({
    "月份": ["1月", "2月", "3月", "4月", "5月", "6月"],
    "销售额": [120, 135, 148, 162, 155, 180],
    "利润": [20, 28, 30, 35, 32, 40],
})
lp.plot("月度销售额与利润趋势对比").data(df).save("sales.png")
```

**传给 LLM 的信息（不传输全部数据）：**
1. 形状：行数 × 列数
2. 列名及数据类型
3. 前 5 行样本
4. 统计摘要（数据多于 5 行时）

这足以让 LLM 写出正确的代码，而无需发送全部数据。

### NumPy 数组

```python
import numpy as np

# 一维数组
data = np.random.randn(1000)
lp.hist("数据分布直方图").data(data).save("dist.png")

# 二维数组
matrix = np.random.rand(10, 10)
lp.heatmap("随机矩阵热力图").data(matrix).save("matrix.png")
```

### 字典

```python
lp.bar("各城市销量对比").data({
    "城市": ["北京", "上海", "广州", "深圳", "杭州"],
    "销量": [320, 280, 260, 240, 200],
}).save("city.png")

# 多系列数据
lp.plot("多系列折线对比").data({
    "x": [1, 2, 3, 4, 5],
    "系列A": [10, 20, 15, 25, 30],
    "系列B": [5, 15, 25, 20, 35],
    "系列C": [12, 18, 22, 28, 32],
}).save("multi.png")
```

### 列表 / 元组

```python
lp.plot("每日温度记录").data([22, 24, 19, 26, 28, 25, 23]).save("temp.png")
lp.bar("成绩分布").data((85, 92, 78, 88, 95)).save("scores.png")
```

单列表被视作一维序列，LLM 自动为 X 轴创建索引。

### 纯文本

```python
csv_text = "日期,数值\n2024-01-01,100\n2024-01-02,105\n..."
lp.plot("CSV数据趋势").data(csv_text).save("from_csv.png")
```

文本上限 2000 字符。更大的数据请用 DataFrame 或预先聚合。

### 处理大数据集

对于超大 DataFrame，提前聚合或采样以控制传给 LLM 的上下文大小：

```python
# 好：提前聚合
lp.bar("月均值对比").data(df.groupby("月份")["数值"].mean().reset_index())

# 好：采样
lp.scatter("相关性散点").data(df.sample(1000))

# 无妨：大 DataFrame 也只会传前5行+统计摘要
lp.plot("趋势图").data(huge_df)
```

---

## 样式定制

### 6 种预设配色方案

| 方案名称 | 色值 | 风格定位 |
|---------|------|---------|
| `blues` | `#3498DB` `#5DADE2` `#87CEEB` `#2980B9` `#AED6F1` | 专业、企业风 |
| `warm` | `#E74C3C` `#F39C12` `#E67E22` `#F1C40F` `#D35400` | 活力、醒目 |
| `cool` | `#1ABC9C` `#3498DB` `#9B59B6` `#2ECC71` `#16A085` | 现代、科技感 |
| `pastel` | `#FADBD8` `#D5F5E3` `#D6EAF8` `#F9E79F` `#E8DAEF` | 柔和、适合阅读 |
| `dark` | `#2C3E50` `#34495E` `#7F8C8D` `#95A5A6` `#BDC3C7` | 深沉、暗色背景 |
| `grayscale` | `#333333` `#666666` `#999999` `#BBBBBB` `#DDDDDD` | 印刷友好、正式 |

```python
for scheme in ["blues", "warm", "cool", "pastel", "dark", "grayscale"]:
    lp.plot("月度趋势").style({"color_scheme": scheme}).save(f"{scheme}.png")
```

### 尺寸与分辨率

```python
lp.plot("趋势").style({
    "figsize": [14, 7],         # 宽14英寸 × 高7英寸
    "dpi": 300,                  # 高分辨率（适合打印）
}).save("large.png")
```

### 字体排版

```python
lp.plot("趋势").style({
    "title_fontsize": 20,        # 大标题
    "label_fontsize": 14,        # 清晰的轴标签
    "tick_fontsize": 12,         # 刻度值清晰
}).save("typography.png")
```

### 网格与背景

```python
# 可见网格 + 深色背景
lp.plot("趋势").style({
    "grid": True,
    "grid_alpha": 0.6,
    "facecolor": "#F0F0F0",
}).save("grid.png")

# 清爽无网格
lp.plot("趋势").style({
    "grid": False,
    "facecolor": "white",
}).save("clean.png")

# 禁用紧凑布局（默认开启），手动留白
lp.plot("趋势").style({"tight_layout": False}).save("loose.png")
```

### 完整样式组合

```python
# 学术论文级别
lp.plot("实验结果: 对照组 vs 实验组").data(exp_df).style({
    "figsize": [8, 5],
    "dpi": 300,
    "color_scheme": "dark",
    "title_fontsize": 16,
    "label_fontsize": 14,
    "tick_fontsize": 12,
    "grid": True,
    "grid_alpha": 0.4,
}).save("paper.png")

# PPT 汇报专用
lp.bar("全年各季度营收").data(revenue_df).style({
    "figsize": [14, 8],
    "color_scheme": "warm",
    "title_fontsize": 24,
    "label_fontsize": 18,
    "tick_fontsize": 14,
    "grid": False,
    "facecolor": "#FAFAFA",
    "dpi": 200,
}).save("ppt.png")

# 快速探索 —— 使用默认样式即可
lp.scatter("年龄vs收入").data(df).save("explore.png")
```

### JSON 字符串传样式

```python
lp.plot("趋势").style('{"color_scheme":"cool","figsize":[12,8],"dpi":200}').save("trend.png")
```

---

## 输出格式

### PNG（默认）

位图格式。适用于通用场景、嵌入文档、快速预览。

```python
lp.plot("趋势").save("chart.png")
result = lp.plot("趋势").format('png').render()
```

### SVG — 矢量图

适合网页嵌入、无限缩放、需要保持清晰度的场景。

```python
# 方式一：渲染前用 .format() 指定
lp.plot("趋势").format('svg').save("chart.svg")

# 方式二：根据扩展名自动检测
result = lp.plot("趋势").render()    # 默认 PNG
result.save("chart.svg")              # → SVG（根据 .svg 扩展名自动检测）

# Base64 编码用于 HTML 嵌入
result = lp.plot("趋势").render()
svg_uri = result.base64_svg()
# HTML: <img src="{svg_uri}" />
```

### PDF — 打印和报告

```python
lp.plot("趋势").format('pdf').save("chart.pdf")
result = lp.plot("趋势").render()
result.save("报告附图.pdf")
```

### 懒加载格式转换

得到 `ChartResult` 后，可按需访问任意格式：

```python
result = lp.plot("CPU使用率趋势").render()  # image_bytes 为 PNG

# 访问 SVG 或 PDF —— 根据存储的代码重新渲染（懒加载，首次访问后缓存）
svg_bytes = result.svg_bytes    # 首次访问时重新渲染为 SVG（并缓存）
pdf_bytes = result.pdf_bytes    # 首次访问时重新渲染为 PDF（并缓存）
svg_string = result.svg          # SVG 字符串
```

这个特性很强大：一次 LLM 调用，三种格式都可以导出，无需重复调用。

### 默认保存路径

```python
result = lp.plot("日活跃用户趋势").render()
result.save()  # → ~/llmpic_charts/chart_20250101_143025.png
```

时间戳格式为 `YYYYMMDD_HHMMSS`。目录不存在时会自动创建。

### Jupyter Notebook 内联显示

```python
result = lp.plot("CPU使用率趋势").render()
result.show()  # cell 下方直接渲染图表，无需 save()
```

支持 PNG、SVG、PDF 格式。在普通 Python 脚本中调用 `show()` 会记录一条警告，不会报错。

---

## 迭代编辑

### 基本用法

```python
# 第一版
v1 = lp.plot("月度销售: 1月=100, 2月=120, 3月=90, 4月=150").render()
v1.save("v1.png")

# 第二版 —— 自然语言修改
v2 = v1.edit("换成柱状图")
v2.save("v2.png")

# 第三版 —— 一次提出多个修改
v3 = v2.edit("柱子颜色改为红色，标题改为'2025年Q1销售报告'，添加网格")
v3.save("v3.png")

# 第四版 —— 精细微调
v4 = v3.edit("标题字号加大到18，使用暖色系配色")
v4.save("v4.png")
```

### edit() 工作原理

```
1. 将当前代码 + 修改描述发给 LLM
2. LLM 返回修改后的代码
3. 安全检查 → 沙箱执行
4. 返回新的 ChartResult（原对象不受影响）
```

### 链式编辑

```python
final = (
    lp.plot("月度销售: 1月=100, 2月=120, 3月=90")
    .render()
    .edit("换成柱状图")
    .edit("柱子颜色改红色，暖色系")
    .edit("标题改为'Q1营收'，Y轴加标签'万元'")
    .edit("加网格线，标题字号加大到18")
)
final.save("final.png")
final.show()
```

### edit() 保留上下文

`edit()` 方法保留原始数据、样式设置和 SDK 引用。每次 edit 复用相同的沙箱、安全审查器和 LLM 端点。

**重要提示**：`.edit()` 要求 `ChartResult` 是由 `llmPIC` 生成的（而非手动创建），因为它需要内部的 `_sdk` 引用来生成代码。

---

## 自动修复机制

### 工作流程

```
LLM 生成代码 → 安全审查 → 沙箱执行
                              ↓ 失败（NameError、ValueError等）
                         LLM 修复代码
                              ↓
                      安全审查 → 沙箱执行
                              ↓ 再次失败
                         LLM 再次修复（最多 max_fix_attempts 轮）
                              ↓
                   返回 ChartResult（成功或最终错误）
```

### 配置

```python
lp = llmPIC(
    ...,
    max_fix_attempts=2,   # 默认 2 轮自动修复
)
# max_fix_attempts=0  →  关闭自动修复
```

### 触发条件

**会触发：**
- `NameError` — 引用了未定义的变量
- `ValueError` — matplotlib 收到非法参数
- `TypeError` — 参数类型错误
- `IndexError` — 越界访问
- 其他生成代码中的 Python 异常

**不会触发：**
- LLM 返回空代码 → 由 `max_retries` 处理（重试生成）
- 安全检查未通过 → 危险代码直接拒绝，不修复
- 超时 → 可能的死循环，不重试（同样代码大概率再次超时）
- 空白图表（无 Axes）→ 立即检测并返回错误，不修复

### 查看自动修复日志

```python
import logging
logging.basicConfig(level=logging.INFO)

# 你将在控制台看到类似以下日志：
# INFO:llmpic.core:Auto-fix attempt 2: NameError: name 'data' is not defined...
```

---

## 异步与批量生成

### 异步单图表

```python
import asyncio
from llmpic import AsyncllmPIC

async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="...")
    result = await lp.plot("CPU使用率趋势").render()
    result.save("cpu.png")

asyncio.run(main())
```

### 批量并发生成（推荐）

`batch()` 方法使用 `asyncio.gather` 并发生成所有图表。总耗时 ≈ 最慢的那张图。

```python
async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="...")

    results = await lp.batch([
        ("plot",     "过去12个月销售趋势"),
        ("bar",      "各部门营收对比"),
        ("scatter",  "用户行为相关性分析"),
        ("heatmap",  "多特征相关性矩阵"),
        ("pie",      "市场份额分布"),
    ])

    for i, r in enumerate(results):
        if r.success:
            r.save(f"batch_{i}.png")
            print(f"[{i}] 成功 — {r.size_kb:.1f}KB, "
                  f"Token: 输入={r.token_usage['input']} 输出={r.token_usage['output']}")
        else:
            print(f"[{i}] 失败: {r.error_message}")

asyncio.run(main())
```

### batch() 请求格式

```python
requests: List[Tuple[str, str]]
# 每个元组: (图表类型, 查询描述)
# 图表类型必须为以下之一：
#   "line" "scatter" "bar" "pie" "hist" "heatmap"
#   "boxplot" "area" "radar" "subplots" "custom"
```

> 注意：`batch()` 使用默认样式，且不支持为每张图绑定不同数据。如需为每张图自定义数据/样式/格式，请用下面的 Builder 方式。

### 为每张图自定义数据、样式和格式

```python
async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="...")

    builders = [
        lp.plot("CPU趋势").format('png'),
        lp.bar("销售对比").data(sales_df).style({"color_scheme": "warm"}).format('svg'),
        lp.pie("市场份额").data(market_df).style({"color_scheme": "cool"}).format('pdf'),
        lp.heatmap("相关性矩阵").data(corr_df).format('png'),
    ]

    results = await asyncio.gather(*[b.render() for b in builders])

    for r in results:
        r.save()  # 每张图保存在 ~/llmpic_charts/ 下，含时间戳

asyncio.run(main())
```

### 批量任务中的错误处理

```python
async def main():
    lp = AsyncllmPIC(...)

    results = await lp.batch(requests)

    success_count = sum(1 for r in results if r.success)
    total_tokens = sum(
        r.token_usage.get('input', 0) + r.token_usage.get('output', 0)
        for r in results if r.success
    )

    print(f"成功 {success_count}/{len(results)} 张图，共消耗 {total_tokens} tokens")

    for i, r in enumerate(results):
        if r.success:
            r.save(f"report_{i}.png")
        else:
            print(f"第 {i} 张图生成失败: {r.error_message}")

asyncio.run(main())
```

---

## 安全模型

### 架构

```
LLM生成的代码
      │
      ├──→ 第一层：正则审查（32条规则，~0ms）
      │         ↓
      │    [不通过] → 立即拒绝
      │    [通过] → 继续
      │
      └──→ 第二层：LLM 语义审查（可选，~1-2秒）
                ↓
           [不通过] → 拒绝并说明理由
           [通过] → 进入沙箱执行
```

### 第一层：正则模式（始终启用）

32 条预编译正则阻止：

| 类别 | 拦截内容 |
|------|---------|
| 系统命令 | `os.system()`, `os.popen()`, `os.exec*()`, `os.spawn*()`, `subprocess` |
| 文件操作 | `os.remove()`, `os.unlink()`, `os.rmdir()`, `os.rename()`, `os.mkdir/makedirs()`, `os.chmod()`, `os.environ`, `open()` |
| 动态执行 | `exec()`, `eval()`, `compile()`, `__import__()` |
| 网络访问 | `socket`, `urllib`, `requests`, `httpx` |
| 进程退出 | `sys.exit()` |
| 危险模块 | `shutil`, `ctypes`, `pickle` |
| 反射逃逸 | `__subclasses__`, `__bases__`, `__mro__`, `setattr()`, `delattr()` |

### 第二层：沙箱执行（始终启用）

- **受限内置函数**：命名空间中仅包含安全的内置函数，没有 `open()`、`exec()` 等
- **Figure 猴子补丁**：`Figure.__init__` 被追踪用于检测；`Figure.savefig` 被拦截，代码无法直接保存文件
- **plt 拦截**：`plt.show()`, `plt.savefig()`, `plt.close()` → 空操作
- **超时熔断**：ThreadPoolExecutor + 可配置超时机制终止失控代码
- **全局互斥锁**：模块级锁防止并发生成时的 matplotlib 全局状态冲突

### 安全级别选择

```python
# 快速模式（推荐生产环境）
lp = llmPIC(..., safety_level="fast")

# 完整模式（增加 LLM 语义审查，每张图多 1-2 秒）
lp = llmPIC(..., safety_level="full")
```

**建议**：沙箱本身提供了足够强的隔离能力，`fast` 模式在生产环境安全可靠。`full` 模式适用于面向公众的对抗性场景。

---

## 多语言支持

### 自动语言检测

SDK 通过 Unicode 范围分析检测查询语言：

```python
lp.plot("CPU使用率趋势")              # → 中文标题/标签
lp.plot("CPU使用量トレンド")            # → 日文标题/标签
lp.plot("CPU 사용량 추세")             # → 韩文标题/标签
lp.plot("CPU usage trend")             # → 英文标题/标签
```

检测逻辑：
- **中文**：CJK 统一表意文字（U+4E00–U+9FFF）或扩展 A 区（U+3400–U+4DBF）
- **日文**：平假名（U+3040–U+309F）、片假名（U+30A0–U+30FF）或片假名扩展（U+31F0–U+31FF）
- **韩文**：谚文音节（U+AC00–U+D7AF）
- **英文**：默认（未检测到 CJK 字符）

语言提示会传给 LLM 作为 prompt 的一部分："图表中的所有标签和标题请使用简体中文。"

### 跨平台 CJK 字体支持

当 `chinese_font=True`（默认），SDK 自动检测并配置中日韩字体：

| 平台 | 字体优先级 |
|------|-----------|
| Windows | Microsoft YaHei（微软雅黑）→ SimHei（黑体）→ SimSun（宋体） |
| macOS | PingFang SC（苹方）→ Heiti SC（黑体）→ STHeiti（华文黑体） |
| Linux | WenQuanYi Micro Hei（文泉驿微米黑）→ WenQuanYi Zen Hei → Noto Sans CJK SC → Noto Sans SC |

字体检测仅在首次执行时运行一次，之后缓存（线程安全）。

**禁用 CJK 字体**（纯英文图表）：

```python
lp = llmPIC(..., chinese_font=False)
```

### 混合语言图表

你可以用英文查询但通过 prompt 描述来获得中文标签：

```python
lp.plot("Sales trend with Chinese labels: 月份 as x-axis, 销售额 as y-axis")
```

---

## 各大模型服务商配置

### OpenAI

```python
lp = llmPIC(
    api_key="sk-proj-...",
    base_url="https://api.openai.com/v1",
    model="gpt-4o",          # 最佳质量
    # model="gpt-4o-mini",   # 约 1/10 价格，简单图表质量也很高
)
```

### DeepSeek（国内用户推荐，性价比高）

DeepSeek 提供优秀的代码生成能力，成本约为 OpenAI 的十分之一：

```python
lp = llmPIC(
    api_key="sk-...",
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",        # DeepSeek-V3
    # model="deepseek-reasoner",  # DeepSeek-R1（推理模型，可能较慢）
)
```

### Azure OpenAI

```python
lp = llmPIC(
    api_key="your-azure-api-key",
    base_url="https://{your-resource}.openai.azure.com/openai/deployments/{deployment-name}",
    model="gpt-4o",          # 你的部署名称
    # 注意：部分 Azure 配置可能需要 structured_output=False
)
```

### 智谱 GLM

```python
lp = llmPIC(
    api_key="your-zhipu-api-key",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model="glm-4-plus",
)
```

### 月之暗面 Moonshot

```python
lp = llmPIC(
    api_key="your-moonshot-key",
    base_url="https://api.moonshot.cn/v1",
    model="moonshot-v1-8k",
)
```

### 阿里通义千问

```python
lp = llmPIC(
    api_key="your-dashscope-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus",
)
```

### 百度文心一言

```python
lp = llmPIC(
    api_key="your-qianfan-key",
    base_url="https://qianfan.baidubce.com/v2",
    model="ernie-4.0-turbo-8k",
)
```

### Ollama（本地部署）

```python
lp = llmPIC(
    api_key="ollama",           # Ollama 不需要真实的 API key
    base_url="http://localhost:11434/v1",
    model="qwen2.5:7b",         # 也支持 llama3, codellama 等
    structured_output=False,    # 部分本地模型不支持 JSON mode
    max_retries=5,              # 本地模型可能需要更多重试
    max_fix_attempts=3,         # 能力较弱的模型需要更多修复尝试
)
```

### vLLM（自部署）

```python
lp = llmPIC(
    api_key="not-needed",
    base_url="http://localhost:8000/v1",
    model="Qwen/Qwen2.5-7B-Instruct",
    structured_output=False,
    max_retries=5,
)
```

### 各服务商对比

| 服务商 | 成本（相对） | 代码质量 | 速度 | 推荐场景 |
|--------|-----------|---------|------|---------|
| OpenAI GPT-4o | $$$$ | ★★★★★ | ★★★★ | 复杂图表、仪表盘 |
| OpenAI GPT-4o-mini | $$ | ★★★★ | ★★★★★ | 大批量、简单图表 |
| DeepSeek-V3 | $ | ★★★★★ | ★★★★ | 性价比最优、中文图表 |
| 智谱 GLM-4-Plus | $$ | ★★★★ | ★★★★ | 中文图表 |
| 本地 Qwen 7B | 免费 | ★★★ | ★★★ | 原型开发、离线使用 |

---

## 实战工作流与代码模板

### 模板一：快速探索（Jupyter）

```python
# 快速出图，跳过 save()，用 show() 直接看
lp = llmPIC(api_key="...", base_url="...")

lp.plot("销售额分布").data(df).render().show()
lp.bar("Top 10 热销产品").data(products_df).render().show()
lp.scatter("年龄 vs 消费").data(users_df).render().show()
lp.heatmap("相关性矩阵").data(df.corr()).render().show()
```

### 模板二：统一风格的报告

```python
# 为报告中所有图表定义统一风格
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

lp.plot("营收趋势").data(df).style(REPORT_STYLE).save("report_revenue.png")
lp.bar("区域对比").data(df).style(REPORT_STYLE).save("report_regional.png")
lp.pie("板块占比").data(df).style(REPORT_STYLE).save("report_segments.png")
lp.scatter("用户分群").data(df).style(REPORT_STYLE).save("report_scatter.png")
```

### 模板三：先粗后精迭代

```python
# 从粗略到精细，一步步修改
r = lp.plot("月度销售额").data(df).render()
r = r.edit("添加12个月移动平均线")
r = r.edit("高亮标记峰值月份")
r = r.edit("标题改为'2024销售业绩分析'，副标题'含12个月移动平均'")
r = r.edit("使用暗色主题，分辨率提升到200 DPI")
r.save("final_sales_analysis.png")
```

### 模板四：一次调用，三格式导出

```python
# 一次 LLM 调用，输出三种格式
result = lp.bar("各部门年度营收").data(df).render()

result.save("report.png")      # 嵌入 Word/PPT
result.save("report.svg")      # 网页展示、无限缩放
result.save("report.pdf")      # 打印输出

# 或者程序化获取
png_bytes = result.image_bytes
svg_html = result.base64_svg()  # 可直接 <img src="...">
pdf_bytes = result.pdf_bytes
```

### 模板五：自动化日报生成

```python
import asyncio
from llmpic import AsyncllmPIC

async def generate_daily_report(date_str, metrics_df):
    lp = AsyncllmPIC(
        api_key=os.getenv("LLMPIC_API_KEY"),
        base_url=os.getenv("LLMPIC_BASE_URL"),
    )

    results = await lp.batch([
        ("plot", f"{date_str} 日活跃用户趋势"),
        ("bar", f"{date_str} Top 10 功能使用量"),
        ("pie", f"{date_str} 流量来源分布"),
        ("heatmap", f"{date_str} 24小时活跃度热力图"),
    ])

    paths = []
    for i, r in enumerate(results):
        if r.success:
            path = f"reports/{date_str}/chart_{i}.png"
            r.save(path)
            paths.append(path)
        else:
            print(f"图表 {i} 失败: {r.error_message}")

    return paths

# 运行: asyncio.run(generate_daily_report("2025-01-15", df))
```

### 模板六：可复用图表函数

```python
def chart_timeseries(df, date_col, value_col, title, style=None):
    """创建风格统一的时序图表。"""
    base_style = {
        "figsize": [14, 6],
        "color_scheme": "blues",
        "title_fontsize": 16,
        "label_fontsize": 12,
        "dpi": 150,
    }
    if style:
        base_style.update(style)

    result = lp.plot(f"{title}: {value_col} 随时间变化").data(df).style(base_style).render()
    return result

# 使用
cpu_chart = chart_timeseries(df, "date", "cpu_usage", "服务器CPU")
mem_chart = chart_timeseries(df, "date", "mem_usage", "服务器内存",
                             style={"color_scheme": "warm"})
```

### 模板七：A/B 测试可视化

```python
# 并排对比
lp.subplots("1行2列: 对照组转化率趋势, 实验组转化率趋势").data({
    "control": control_df,
    "treatment": treatment_df,
}).save("ab_test.png")

# 叠加对比
lp.plot("转化率曲线: 对照组 vs 实验组，带置信区间").data({
    "control": control_df["rate"],
    "treatment": treatment_df["rate"],
}).save("ab_overlay.png")
```

### 模板八：检查生成的代码（调试用）

```python
result = lp.plot("复杂的多系列图表").data(df).render()

if not result.success:
    print(f"错误: {result.error_message}")
else:
    # 查看 LLM 生成的代码
    print("=== 生成的 Matplotlib 代码 ===")
    print(result.code)
    print(f"\n=== Token 用量: {result.token_usage} ===")

# 高级用法：手动修改生成的代码
# 取 result.code，修改后可以通过自定义方式执行
```

---

## 成本优化

### 1. 选择合适的模型

```python
# 最贵、质量最高
lp = llmPIC(..., model="gpt-4o")

# 约便宜 10 倍，简单图表质量依然很好
lp = llmPIC(..., model="gpt-4o-mini")

# 性价比最高（国内用户推荐）
lp = llmPIC(..., model="deepseek-chat", base_url="https://api.deepseek.com/v1")
```

### 2. 描述具体（减少重试和修复）

```python
# 好：在 prompt 中明确给出数据
lp.bar("Q1预算: 研发=200万, 市场=150万, 销售=180万")

# 差：太模糊，LLM 可能多次重试
lp.bar("各部门预算")
```

### 3. 提供数据减少猜测

```python
# 好：LLM 看到列名、类型、样本数据
lp.plot("趋势").data(df)

# 差：LLM 只能猜测数据结构
lp.plot("趋势")
```

### 4. 用异步批量生成

```python
# 5张图顺序生成 = 5 × (LLM时间 + 沙箱时间)
# 5张图批量生成 = max(LLM时间) + max(沙箱时间)
# 虽然 token 消耗相同，但总耗时可减少 3-5 倍
```

### 5. 追踪 Token 用量

```python
total_input = 0
total_output = 0

for query in queries:
    r = lp.plot(query).render()
    if r.success:
        total_input += r.token_usage.get('input', 0)
        total_output += r.token_usage.get('output', 0)

print(f"本次会话: 输入 {total_input} tokens, 输出 {total_output} tokens")
```

### 6. 复用 SDK 实例

不要每次画图都新建 `llmPIC` 实例，一个实例可以反复使用：

```python
# 好：复用
lp = llmPIC(...)
charts = [lp.plot(q).save(f"{i}.png") for i, q in enumerate(queries)]

# 差：每次都创建新实例
for q in queries:
    lp = llmPIC(...)  # 每次都重建 sandbox、做字体检测等
    lp.plot(q).save(...)
```

---

## 系统集成方案

### Jupyter Notebook 最佳实践

```python
%matplotlib inline  # 可选 —— llmpic 独立处理显示

from llmpic import llmPIC
lp = llmPIC(api_key="...", base_url="...")

# 探索阶段：show() 内联查看
lp.plot("用户年龄分布").data(df).render().show()

# 确认后：save() 保存到报告
lp.plot("用户年龄分布").data(df).style({
    "figsize": [10, 6],
    "dpi": 200,
}).save("report_age_dist.png")
```

### Streamlit / Gradio 集成

```python
import streamlit as st
from llmpic import llmPIC

lp = llmPIC(
    api_key=st.secrets["LLMPIC_API_KEY"],
    base_url=st.secrets["LLMPIC_BASE_URL"],
)

st.title("AI 图表生成器")
query = st.text_input("描述你想要的图表：", "过去12个月销售趋势")

if st.button("生成图表"):
    result = lp.plot(query).render()
    if result.success:
        st.image(result.image_bytes)
        st.code(result.code, language="python")
    else:
        st.error(result.error_message)
```

### FastAPI / Flask 集成

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

### 数据管道集成

```python
# 在数据管道中：自动生成每日/每周 KPI 图表
def generate_kpi_charts(date, kpi_df):
    style = {"figsize": [12, 6], "dpi": 150, "color_scheme": "dark"}

    charts = {
        "revenue": lp.plot(f"每日营收趋势").data(kpi_df).style(style),
        "users": lp.plot(f"每日活跃用户").data(kpi_df).style(style),
        "conversion": lp.plot(f"转化率趋势").data(kpi_df).style(style),
    }

    for name, builder in charts.items():
        builder.save(f"kpi/{date}/{name}.png")
```

---

## 最佳实践

### 1. 生产环境使用 fast 安全模式

`safety_level="fast"` 足够安全，沙箱已提供真正隔离。`full` 模式每张图多花 1-2 秒。

### 2. 批量任务用异步 `batch()`

多张图表用 `AsyncllmPIC.batch()` 并发生成，总耗时接近单张：
```python
# 好：3张图约 2-3 秒
results = await lp.batch([(...), (...), (...)])

# 差：3张图约 6-9 秒
for query in queries:
    lp.plot(query).save(...)
```

### 3. 描述尽量具体

```python
# 好：数据和意图明确
lp.bar("Q1预算: 研发=200万, 市场=150万, 销售=180万, 人事=100万")

# 差：太模糊
lp.bar("各部门预算")
```

### 4. 有真实数据就传进去

```python
lp.plot("趋势").data(df)   # 好：LLM 看到真实数据结构
lp.plot("趋势")             # 次优：LLM 编造演示数据
```

### 5. 用 `edit()` 迭代，不要重复描述

```python
# 好：增量修改
result = lp.plot("销售趋势").data(df).render()
result = result.edit("标题字号加大")
result = result.edit("添加网格线")
result = result.edit("换成暖色系")

# 差：每次微调都重写全部描述
lp.plot("销售趋势，大标题").data(df).save("v1.png")
lp.plot("销售趋势，大标题，有网格").data(df).save("v2.png")
lp.plot("销售趋势，大标题，有网格，暖色").data(df).save("v3.png")
```

### 6. 合理设置超时时间

```python
# 简单图表：默认 30 秒足够
lp.plot("折线图").render()

# 复杂仪表盘：加大超时
lp.subplots("4x4 综合看板").render()   # timeout=60
lp = llmPIC(..., timeout=60)
```

### 7. 追踪 Token 用量

```python
result = lp.plot("test").render()
print(f"输入: {result.token_usage['input']}, 输出: {result.token_usage['output']}")
```

### 8. 不确定用什么图表时用 `.custom()`

```python
# 让 LLM 自动判断最佳可视化方式
lp.custom("分析用户留存率的多维影响因素").data(df).save("auto.png")
```

### 9. 只创建一次 SDK 实例

```python
# 创建一次，反复使用
lp = llmPIC(...)
for chart_name, query in chart_configs.items():
    lp.plot(query).save(f"{chart_name}.png")
```

### 10. 先检查成功再使用结果

```python
result = lp.plot("复杂图表").render()
if result.success:
    result.save("output.png")
    print(f"成功生成 {len(result.code)} 字符代码, {result.size_kb:.1f}KB")
else:
    print(f"生成失败: {result.error_message}")
    # 可选：换模型重试，或简化查询
```

---

## 故障排查

### 生成的图表中文显示为方框 (□□□)

**原因**：系统缺少中文字体。

**解决**：
- Windows：安装 "Microsoft YaHei"（微软雅黑）或 "SimHei"（黑体）
- Linux：`sudo apt install fonts-wqy-microhei`
- macOS：通常已内置中文字体

或将 `chinese_font=False` 仅使用英文标签。

### LLM 返回"无代码"或空白结果

**原因**：查询描述过于模糊，模型无法理解需求。

**解决**：
- 添加更多细节："折线图，12个数据点，展示月度销售额趋势"
- 通过 `.data()` 传入实际数据
- 尝试更强的模型（如 `gpt-4o` 替代 `gpt-4o-mini`）

### 超时："Code execution timed out (30s)"

**原因**：生成的代码中有死循环，或图表过于复杂。

**解决**：
1. 增加超时时间：`llmPIC(..., timeout=60)`
2. 简化查询 —— 将复杂仪表盘拆分为多个独立图表
3. 对大数据集采样：`df.sample(1000)`

### 自动修复没有触发

**检查**：
- `max_fix_attempts > 0`（默认 2）
- 失败类型是**代码执行错误**（不是安全违规或超时）
- 启用日志查看自动修复活动：
  ```python
  import logging
  logging.basicConfig(level=logging.INFO)
  ```

### SVG/PDF 保存后无法打开

**原因**：使用了错误的程序打开文件。

**解决**：
- SVG：用浏览器（Chrome/Firefox）或矢量编辑软件打开
- PDF：用 PDF 阅读器打开
- 用 `result.base64_svg()` 嵌入 HTML 预览

### `ModuleNotFoundError: No module named 'llmpic'`

**解决**：
```bash
pip install llmpic           # 正式安装
# 或开发模式：
pip install -e .             # 从仓库根目录可编辑安装
```

### 异步报错 `RuntimeError: no running event loop`

**原因**：在非异步环境中直接使用了 `await`。

**解决**：用 `asyncio.run()` 包装：
```python
async def main():
    lp = AsyncllmPIC(...)
    await lp.plot("test").save("test.png")

asyncio.run(main())  # ← 必须
```

### 生成的图表和我描述的不一样

**原因**：自然语言本身存在歧义；LLM 会根据理解生成代码。

**解决**：
- 描述更具体：不说"好看一点"，而说"标题字号改为18，用暖色系，加网格线"
- 用 `.edit()` 迭代修改
- 提供数据 —— 有了真实数据结构，图表会更准确

### 图片文件太大

**原因**：高 DPI + 大尺寸 = 大文件。

**解决**：
```python
# 网页用：降低 DPI，用 SVG
lp.plot("网页图表").style({"dpi": 72, "figsize": [8, 5]}).format('svg').save("web.svg")

# 打印用：高 DPI 是正常的
lp.plot("打印图表").style({"dpi": 300}).save("print.png")
```

### pandas 或 seaborn 不可用

**原因**：安装时没有包含 `[full]` 额外依赖。

**解决**：
```bash
pip install llmpic[full]
```

SDK 会自动降级为纯 matplotlib，但部分 LLM 生成的代码可能会引用 pandas/seaborn，导致执行失败。

### API 频率限制

**原因**：并发请求过多触发了 API 提供商的频率限制。

**解决**：
- 减少批量大小
- 批次之间加延迟
- 升级 API 套餐

```python
# 分批处理，每批 3 张图
for i in range(0, len(requests), 3):
    chunk = requests[i:i+3]
    results = await lp.batch(chunk)
    await asyncio.sleep(2)  # 遵守频率限制
```

---

← [返回首页](./README_CN.md)
