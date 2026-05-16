# 使用指南 — llmpic

> 进阶用法、最佳实践、常见问题。

---

## 目录

- [图表类型详解](#图表类型详解)
- [数据输入方式](#数据输入方式)
- [样式定制](#样式定制)
- [输出格式](#输出格式)
- [迭代编辑](#迭代编辑)
- [自动修复机制](#自动修复机制)
- [异步与批量生成](#异步与批量生成)
- [安全模型](#安全模型)
- [多语言支持](#多语言支持)
- [最佳实践](#最佳实践)
- [故障排查](#故障排查)

---


## 图表类型详解

### plot — 折线图

适用场景：趋势分析、时间序列、连续数据。

```python
lp.plot("2024年每月营收变化趋势").save("revenue.png")
lp.plot("sin(x) and cos(x) from 0 to 2π").save("trig.png")
```

LLM 提示词：`Line chart (折线图). Use ax.plot(). Multiple series: different colors + legend.`

### scatter — 散点图

适用场景：相关性分析、聚类可视化。

```python
lp.scatter("用户年龄 vs 消费金额的分布关系").data(df).save("scatter.png")
```

LLM 提示词：`Scatter chart (散点图). Use ax.scatter(). 3rd variable → color/size.`

### bar — 柱状图

适用场景：分类数据对比、排名。

```python
lp.bar("各部门季度预算: 研发=200, 市场=150, 销售=180, 人事=100").save("budget.png")
```

### pie — 饼图

适用场景：占比分布、市场份额。

```python
lp.pie("市场份额: A产品40%, B产品25%, C产品20%, 其他15%").save("market.png")
```

### hist — 直方图

适用场景：数据分布、频率统计。

```python
lp.hist("学生考试成绩分布，均值70，标准差15").data(scores).save("hist.png")
```

### heatmap — 热力图

适用场景：相关性矩阵、二维密度。

```python
lp.heatmap("各产品之间的销售相关性热力图").data(corr_df).save("heatmap.png")
```

LLM 提示词：`Heatmap (热力图). Use ax.imshow() or sns.heatmap(). Add colorbar and annotate cells.`

### boxplot — 箱线图

适用场景：多组数据统计分布对比。

```python
lp.boxplot("A/B/C三组实验结果的分布对比").save("boxplot.png")
```

### area — 面积图

适用场景：堆积趋势、成分变化。

```python
lp.area("2020-2024年各产品线收入占比变化").data(revenue_df).save("area.png")
```

LLM 提示词：`Area chart (面积图). Use ax.fill_between() or ax.stackplot(). Set alpha 0.3-0.7.`

### radar — 雷达图

适用场景：多维指标对比、能力评估。

```python
lp.radar("产品评分: 性能4, 易用性3, 稳定性5, 价格2, 售后4").save("radar.png")
```

LLM 提示词：`Radar chart (雷达图). Use polar axes: plt.subplots(subplot_kw={'projection':'polar'}). Close the polygon loop.`

### subplots — 子图仪表盘

适用场景：多图表综合展示。

```python
lp.subplots("2x2综合看板: 销售额趋势折线图, 地区对比柱状图, 客户分布散点图, 月度增长直方图").save("dashboard.png")
```

LLM 提示词：`Dashboard (子图仪表盘). Use fig, axes = plt.subplots(nrows, ncols, figsize=(w,h)). Add fig.suptitle(). Each subplot is a different chart.`

### custom — 智能推荐

LLM 自动判断最佳图表类型。

```python
lp.custom("分析用户留存率变化趋势和影响因素").data(df).save("auto.png")
```

---


## 数据输入方式

### 不传数据 — LLM 自动生成演示数据

```python
lp.plot("正弦波曲线").save("demo.png")
# LLM 自动用 np.linspace + np.sin 生成数据
```

### DataFrame（推荐）

```python
import pandas as pd
df = pd.DataFrame({
    "月份": ["1月","2月","3月","4月","5月","6月"],
    "销售额": [120, 135, 148, 162, 155, 180],
    "利润": [20, 28, 30, 35, 32, 40],
})
lp.plot("月度销售与利润趋势").data(df).save("sales.png")
```

序列化后传给 LLM 的内容：列名、数据类型、前 5 行样本、统计摘要。

### NumPy 数组

```python
import numpy as np
data = np.random.randn(1000)
lp.hist("数据分布").data(data).save("dist.png")
```

### 字典

```python
lp.bar("各城市销量").data({
    "城市": ["北京", "上海", "广州", "深圳", "杭州"],
    "销量": [320, 280, 260, 240, 200],
}).save("city.png")
```

### 列表 / 元组

```python
lp.plot("温度变化").data([22, 24, 19, 26, 28, 25, 23]).save("temp.png")
```

### 纯文本

大段文本会被截断到 2000 字符。

---


## 样式定制

### 快速配色

```python
# 6 种预设配色方案
lp.plot("趋势").style({"color_scheme": "blues"}).save("b.png")
lp.plot("趋势").style({"color_scheme": "warm"}).save("w.png")
lp.plot("趋势").style({"color_scheme": "cool"}).save("c.png")
lp.plot("趋势").style({"color_scheme": "pastel"}).save("p.png")
lp.plot("趋势").style({"color_scheme": "dark"}).save("d.png")
lp.plot("趋势").style({"color_scheme": "grayscale"}).save("g.png")
```

### 尺寸与字体

```python
lp.plot("趋势").style({
    "figsize": [14, 7],        # 宽 14 英寸，高 7 英寸
    "title_fontsize": 18,       # 标题字号
    "label_fontsize": 14,       # 坐标轴标签字号
    "tick_fontsize": 12,        # 刻度字号
    "dpi": 200,                 # 输出分辨率
}).save("large.png")
```

### 网格与背景

```python
lp.plot("趋势").style({
    "grid": True,
    "grid_alpha": 0.5,          # 网格更深
    "facecolor": "#F5F5F5",     # 浅灰背景
    "tight_layout": True,       # 紧凑布局
}).save("grid.png")

# 或关掉网格
lp.plot("趋势").style({"grid": False}).save("nogrid.png")
```

### 多属性组合

```python
lp.bar("销售对比").data(df).style({
    "figsize": [12, 8],
    "color_scheme": "warm",
    "title_fontsize": 16,
    "grid": False,
    "dpi": 200,
}).save("styled.png")
```

---


## 输出格式

### PNG（默认）

```python
lp.plot("趋势").save("chart.png")
# 或显式指定
lp.plot("趋势").format('png').render()
```

### SVG — 前端嵌入、矢量无损

```python
# 方式一：链式设置
lp.plot("趋势").format('svg').save("chart.svg")

# 方式二：已生成的结果懒加载，扩展名自动决定格式
result = lp.plot("趋势").render()
result.save("chart.svg")    # → SVG

# base64 嵌入 HTML
svg_uri = result.base64_svg()
# 可在 HTML 中: <img src="{svg_uri}" />
```

### PDF — 打印、报告

```python
lp.plot("趋势").format('pdf').save("chart.pdf")
# 或
result = lp.plot("趋势").render()
result.save("chart.pdf")    # → PDF
```

### 默认保存路径

```python
result = lp.plot("趋势").render()
result.save()               # → ~/llmpic_charts/chart_20250101_120000.png
```

### Jupyter Notebook 内联显示

```python
result = lp.plot("CPU趋势").render()
result.show()  # cell 下方直接渲染图表，无需调用 save()
```

---


## 迭代编辑

在已有图表基础上用自然语言修改，适合反复调试。

### 基础用法

```python
# 第一版
v1 = lp.plot("月度销售趋势: 1月=100, 2月=120, 3月=90, 4月=150").render()
v1.save("v1.png")

# 不满意的部分直接说话修改
v2 = v1.edit("把折线改成柱状图")
v2.save("v2.png")

v3 = v2.edit("柱子颜色换成红色系，标题改为'2025年Q1销售'")
v3.save("v3.png")

v4 = v3.edit("添加网格，增大标题字号")
v4.save("v4.png")
```

### edit() 工作原理

1. 将当前代码 + 修改描述发给 LLM
2. LLM 返回修改后的代码
3. 安全检查 → 沙箱执行 → 返回新 ChartResult

**注意**：`.edit()` 不修改原 ChartResult，而是返回一个新的。

---


## 自动修复机制

### 工作流程

```
生成代码 → 安全审查 → 沙箱执行
                        ↓ 失败
                  LLM 修复代码
                        ↓
              安全审查 → 沙箱执行
                        ↓ 再失败
                  LLM 再次修复（最多 max_fix_attempts 次）
```

### 配置

```python
lp = llmPIC(
    ...,
    max_fix_attempts=2,   # 默认 2 次
)
# 设为 0 关闭自动修复
```

### 触发条件

自动修复仅在**代码执行阶段**失败时触发（如 `NameError`、`ValueError` 等 matplotlib/数据错误），不会触发的场景：

- LLM 返回无代码（这由 `max_retries` 处理）
- 安全检查未通过（安全违规不修正，直接拒绝）
- 超时（可能是死循环，不重试）

---


## 异步与批量生成

### 异步单图表

```python
import asyncio
from llmpic import AsyncllmPIC

async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="...")
    await lp.plot("CPU趋势").save("cpu.png")

asyncio.run(main())
```

### 批量并发生成（最大加速）

```python
async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="...")

    results = await lp.batch([
        ("plot", "CPU使用率趋势"),
        ("bar", "各部门预算对比"),
        ("scatter", "用户行为散点图"),
        ("heatmap", "相关性矩阵"),
        ("pie", "市场份额分布"),
    ])

    # 所有图表并发生成，总耗时 ≈ 最慢那张
    for i, r in enumerate(results):
        if r.success:
            r.save(f"batch_{i}.png")
            print(f"[{i}] OK, tokens: in={r.token_usage['input']}, out={r.token_usage['output']}")
        else:
            print(f"[{i}] FAIL: {r.error_message}")

asyncio.run(main())
```

### 混合格式批量

```python
async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="...")

    # 注意：format 需要在 builder 上设置
    builders = [
        lp.plot("趋势").format('png'),
        lp.plot("趋势").format('svg'),
        lp.plot("趋势").format('pdf'),
    ]
    # 并发渲染
    import asyncio
    results = await asyncio.gather(*[b.render() for b in builders])
    for r in results:
        print(r)

asyncio.run(main())
```

---


## 安全模型

### 双层防护

| 层级   | 机制                 | 耗时  | 覆盖率           |
| ------ | -------------------- | ----- | ---------------- |
| 第一层 | 32 条预编译正则      | ~0ms  | 阻止已知危险模式 |
| 第二层 | LLM 语义审查（可选） | ~1-2s | 捕捉绕过和变种   |

### 被阻止的操作

- 系统命令：`os.system()`, `os.popen()`, `subprocess`
- 文件操作：`open()`（沙箱内 LLM 不应当直接读写文件）
- 动态执行：`exec()`, `eval()`, `compile()`, `__import__()`
- 网络访问：`socket`, `urllib`, `requests`, `httpx`
- 危险模块：`shutil`, `ctypes`, `pickle`
- 反射逃逸：`__subclasses__()`, `__bases__`, `globals()`, `setattr()`

### 安全级别选择

```python
# 快速模式（默认，推荐生产环境）
lp = llmPIC(..., safety_level="fast")

# 完整模式（在沙箱基础上再做 LLM 语义审查，适合对安全性要求极高的场景）
lp = llmPIC(..., safety_level="full")
```

**推荐**：沙箱本身已经阻止所有实际执行路径（受限命名空间 + Figure.savefig 拦截），fast 模式在生产环境中足够安全。full 模式仅作为额外防御层，但会增加 ~1-2 秒延迟。

---


## 多语言支持

### 自动检测

SDK 自动检测查询语言，LLM 会自动匹配图表标签语言：

```python
lp.plot("CPU使用率趋势")     # → 中文标题/标签
lp.plot("CPU使用量トレンド")   # → 日文标题/标签
lp.plot("CPU 사용량 추세")    # → 韩文标题/标签
lp.plot("CPU usage trend")    # → 英文标题/标签
```

检测逻辑基于 Unicode 范围判断 CJK 字符，精确到中文（`一-鿿`）、日文（`぀-ヿ`）、韩文（`가-힯`）。

### 跨平台字体

| 平台    | 首选字体                                                     |
| ------- | ------------------------------------------------------------ |
| Windows | Microsoft YaHei (微软雅黑) → SimHei (黑体) → SimSun (宋体) |
| macOS   | PingFang SC (苹方) → Heiti SC (黑体) → STHeiti (华文黑体)  |
| Linux   | WenQuanYi Micro Hei (文泉驿微米黑) → Noto Sans CJK SC       |

字体检测首次执行时运行一次，之后缓存复用（线程安全）。

---


## 最佳实践

### 1. 使用 fast 安全模式

生产环境推荐 `safety_level="fast"`，可减少约一半延迟。沙箱本身已提供足够的安全隔离。

### 2. 批量任务用异步

多张图表用 `AsyncllmPIC.batch()` 并发生成，总耗时接近单张：

```python
# 好：3 张图表约 2-3 秒
results = await lp.batch([(...), (...), (...)])

# 差：3 张图表约 6-9 秒
for query in queries:
    lp.plot(query).save(...)
```

### 3. 描述尽量具体

```python
# 好 — 数据明确
lp.bar("各部门Q1预算: 研发=200万, 市场=150万, 销售=180万")

# 差 — 太模糊
lp.bar("各部门预算")
```

### 4. 提供真实数据

有 DataFrame 就传进去，减少 LLM 对数据的猜测，图表更准确：

```python
lp.plot("趋势").data(df)  # 好
lp.plot("趋势")            # LLM 会编造演示数据
```

### 5. 用 edit() 迭代

不要为小修改重新描述整个需求：

```python
result = lp.plot("销售额趋势").data(df).render()
result = result.edit("标题改大一点")
result = result.edit("加网格")
result = result.edit("颜色换暖色系")
result.save("final.png")
```

### 6. 合理设置超时

复杂图表（如 subplots 仪表盘）可能需要更多时间：

```python
lp = llmPIC(..., timeout=60)  # 复杂图表给 60 秒
```

### 7. Token 用量追踪

关注 `result.token_usage` 了解每次调用的消耗：

```python
result = lp.plot("test").render()
print(f"Input: {result.token_usage['input']}, Output: {result.token_usage['output']}")
```

---


## 故障排查

### 问题：生成的图表中文显示为方块

**原因**：系统无中文字体。

**解决**：

- Windows：安装 Microsoft YaHei 或 SimHei 字体
- Linux：`sudo apt install fonts-wqy-microhei`
- macOS：通常已内置，确保 `chinese_font=True`

或设置 `chinese_font=False` 仅使用英文标签。

### 问题：LLM 返回 "no code"

**原因**：查询描述过于模糊，模型无法理解。

**解决**：重写查询，提供更具体的描述和数据。

### 问题：代码执行超时

**原因**：生成的代码可能有死循环，或图表太复杂。

**解决**：

1. 增加 `timeout` 参数：`llmPIC(..., timeout=60)`
2. 拆分复杂图表为多个简单图表
3. 检查是否传入了极端大数据（考虑先采样）

### 问题：自动修复没有触发

**检查**：

- `max_fix_attempts > 0`（默认 2）
- 失败类型是代码执行错误（不是安全违规或超时）
- 查看日志确认 auto-fix 是否被调用

### 问题：SVG/PDF 保存后无法打开

**原因**：SVG 输出是 UTF-8 编码的 XML 文本，PDF 是二进制。确保用正确的程序打开。

**解决**：

- 用浏览器或矢量图形软件打开 SVG
- 用 PDF 阅读器打开 PDF
- 使用 `base64_svg()` 嵌入 HTML 预览

### 问题：导入错误 `ModuleNotFoundError: No module named 'llmpic'`

**解决**：

```bash
pip install -e .         # 开发模式安装
# 或
pip install llmpic       # 正式安装
```

### 问题：异步调用报错 `RuntimeError: no running event loop`

**原因**：在非异步环境中直接 `await`。

**解决**：使用 `asyncio.run()` 包装：

```python
async def main():
    lp = AsyncllmPIC(...)
    await lp.plot("test").save("test.png")

asyncio.run(main())
```

---

← [返回首页](./README_CN.md)
