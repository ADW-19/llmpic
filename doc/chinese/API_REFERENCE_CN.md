# API 参考 — llmpic

> 所有类、方法、参数、返回类型的完整参考。

---

## 目录

- [llmPIC（同步 SDK）](#llmpic同步-sdk)
- [AsyncllmPIC（异步 SDK）](#asyncllmpic异步-sdk)
- [PlotBuilder（同步构建器）](#plotbuilder同步构建器)
- [AsyncPlotBuilder（异步构建器）](#asyncplotbuilder异步构建器)
- [ChartResult（结果对象）](#chartresult结果对象)
- [SandboxExecutor（沙箱执行器）](#sandboxexecutor沙箱执行器)
- [CodeSafetyChecker（安全检查器）](#codesafetychecker安全检查器)
- [配置常量](#配置常量)
- [常用模式](#常用模式)

---

## llmPIC（同步 SDK）

`llmPIC` 是同步图表生成的主入口类。它管理 LLM 客户端、安全审查器和沙箱执行器。

### 构造函数

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

| 参数 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `api_key` | `str` | **必填** | OpenAI 兼容 API 密钥。本地端点可用 `"ollama"` 或 `"not-needed"`。 |
| `base_url` | `str` | **必填** | API 端点地址。需包含路径前缀（如 `.../v1`）。 |
| `model` | `str` | `"gpt-4o"` | 代码生成使用的模型名称。建议使用支持 JSON 结构化输出的模型。 |
| `safety_model` | `str \| None` | `None` | LLM 安全审查使用的模型。`None` 时默认与 `model` 相同。仅在 `safety_level="full"` 时生效。 |
| `safety_level` | `str` | `"fast"` | `"fast"` — 仅正则（~0ms）。`"full"` — 正则 + LLM 语义审查（额外 ~1-2s）。 |
| `chinese_font` | `bool` | `True` | 自动检测并配置中日韩字体。纯英文图表可设为 `False`（启动略快）。 |
| `timeout` | `int` | `30` | 代码执行超时（秒）。复杂仪表盘可能需要 60+。 |
| `dpi` | `int` | `150` | 默认输出分辨率。单张图可通过 `.style({"dpi": ...})` 覆盖。 |
| `output_dir` | `str` | `"~/llmpic_charts"` | 默认保存目录（`save()` 无参数时使用）。支持 `~`（主目录）、相对路径和绝对路径。 |
| `temperature` | `float` | `0.3` | LLM 采样温度（0–2）。越低越确定，越高越多样。 |
| `max_tokens` | `int` | `2048` | 最大输出 token 数。复杂仪表盘可增大至 4096。 |
| `structured_output` | `bool` | `True` | 使用 JSON 结构化输出模式以稳定提取代码。不支持 JSON mode 的模型请设为 `False`。 |
| `max_retries` | `int` | `3` | LLM 调用失败重试次数，指数退避：1s → 2s → 4s。包括瞬时 API 错误和无解析响应。 |
| `max_fix_attempts` | `int` | `2` | 代码执行失败自动修复轮数。每次修复将错误+代码发回 LLM 修正。设为 `0` 关闭自动修复。 |

### 图表类型方法

所有图表方法返回 `PlotBuilder` 对象，支持链式调用。在 `.render()` / `.save()` 或访问 `.image_bytes` / `.code` 之前不会执行任何操作。

```python
plot(query: str)      -> PlotBuilder   # 折线图
scatter(query: str)   -> PlotBuilder   # 散点图
bar(query: str)       -> PlotBuilder   # 柱状图（纵向或横向）
pie(query: str)       -> PlotBuilder   # 饼图（或环形图）
hist(query: str)      -> PlotBuilder   # 直方图
heatmap(query: str)   -> PlotBuilder   # 热力图
boxplot(query: str)   -> PlotBuilder   # 箱线图
area(query: str)      -> PlotBuilder   # 面积图
radar(query: str)     -> PlotBuilder   # 雷达图 / 蜘蛛图
subplots(query: str)  -> PlotBuilder   # 多图仪表盘
custom(query: str)    -> PlotBuilder   # 智能推荐最佳图表类型
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `query` | `str` | 自然语言图表描述。支持中文、英文、日文、韩文。 |

**示例：**

```python
lp = llmPIC(api_key="sk-...", base_url="https://api.deepseek.com/v1")

# 每种方法均返回 PlotBuilder —— 此时尚未执行任何操作
builder = lp.plot("月度销售趋势")       # PlotBuilder
builder = lp.bar("各地区营收对比")      # PlotBuilder
builder = lp.custom("自动判断最佳类型")  # PlotBuilder

# 触发生成
result = builder.render()
```

### 内部方法（不属于公开 API）

| 方法 | 签名 | 用途 |
|------|------|------|
| `_generate_code` | `(user_prompt: str, system_prompt: str = None) -> Tuple[Optional[str], dict]` | 调用 LLM，失败重试，返回 `(code, token_usage)` |
| `_fix_code` | `(code: str, error: str, query: str) -> Tuple[Optional[str], dict]` | 请求 LLM 修复执行失败的代码 |

---

## AsyncllmPIC（异步 SDK）

`llmPIC` 的异步版本。构造函数和图表方法完全一致，额外提供 `batch()` 并发生成方法。

### 构造函数

参数与 `llmPIC` 完全相同。内部使用 `AsyncOpenAI` 客户端。

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

### 图表类型方法

与 `llmPIC` 完全相同的 11 种方法，每种返回 `AsyncPlotBuilder`。关键方法需要 `await`。

```python
lp = AsyncllmPIC(api_key="sk-...", base_url="...")

builder = lp.plot("CPU使用趋势")   # AsyncPlotBuilder —— 此时尚未执行
result = await builder.render()      # ← 触发生成
```

### async batch()

```python
async def batch(
    self,
    requests: List[Tuple[str, str]]
) -> List[ChartResult]
```

使用 `asyncio.gather` 并发生成多张图表。总耗时 ≈ 最慢的那张图表。

| 参数 | 类型 | 说明 |
|------|------|------|
| `requests` | `List[Tuple[str, str]]` | `(图表类型, 查询描述)` 的列表 |

**图表类型可选值：**
`"line"` `"scatter"` `"bar"` `"pie"` `"hist"` `"heatmap"` `"boxplot"` `"area"` `"radar"` `"subplots"` `"custom"`

**返回值：** `List[ChartResult]`，与输入请求顺序一一对应。

**示例：**

```python
async def main():
    lp = AsyncllmPIC(api_key="sk-...", base_url="https://api.deepseek.com/v1")

    results = await lp.batch([
        ("plot", "过去12个月销售趋势"),
        ("bar", "各部门营收对比"),
        ("scatter", "用户行为相关性分析"),
    ])

    for i, r in enumerate(results):
        if r.success:
            r.save(f"batch_{i}.png")

asyncio.run(main())
```

**注意：** `batch()` 使用默认样式，不支持为每张图绑定不同数据。如需为每张图自定义数据/样式/格式，请直接用 `asyncio.gather()` 配合 Builder 模式（详见使用指南）。

---

## PlotBuilder（同步构建器）

所有 `llmPIC` 图表方法返回的流式构建器。**惰性执行** — 在调用 `.render()` / `.save()` 或访问 `.image_bytes` / `.code` 之前，不会触发 LLM 调用、安全审查或沙箱执行。

### 构造函数（不直接调用）

```python
# 由 llmPIC 的图表方法创建：
builder = lp.plot("描述需求")   # 返回 PlotBuilder
```

### .data(data) → PlotBuilder

绑定图表数据。未调用时，LLM 使用 numpy 自动生成合理的演示数据。

```python
def data(self, data) -> PlotBuilder
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `data` | `pandas.DataFrame` \| `pandas.Series` \| `numpy.ndarray` \| `dict` \| `list` \| `tuple` \| `str` | 图表数据。会被序列化后传给 LLM 作为上下文（不会将原始数据全部发送）。 |

**数据序列化行为：**

| 输入类型 | LLM 收到的信息 |
|---------|-------------|
| `DataFrame` | 形状、列名、数据类型、前5行样本、统计摘要（>5行时） |
| `Series` | 名称、数据类型、前10个值 |
| `ndarray` (1维) | 形状、数据类型、前10个元素 |
| `ndarray` (多维) | 形状、数据类型、前5行 |
| `dict` | 键列表 + 值（每个值截断至150字符） |
| `list` / `tuple` | 长度 + 前15个元素 |
| `str` | 原始文本，截断至2000字符 |

### .style(style_spec) → PlotBuilder

设置视觉样式。在 `DEFAULT_STYLE`（见配置常量）基础上合并。

```python
def style(self, style_spec: dict | str) -> PlotBuilder
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `style_spec` | `dict` 或 `str`(JSON) | 样式配置字典或 JSON 字符串 |

**支持的样式键：**

| 键 | 类型 | 默认值 | 说明 |
|---|------|-------|------|
| `figsize` | `[int, int]` | `[10, 6]` | 图表尺寸（英寸）：`[宽, 高]` |
| `dpi` | `int` | `150` | 输出分辨率（每英寸点数） |
| `color_scheme` | `str` | `"blues"` | 配色方案：`"blues"`, `"warm"`, `"cool"`, `"pastel"`, `"dark"`, `"grayscale"` |
| `title_fontsize` | `int` | `14` | 标题字号（磅） |
| `label_fontsize` | `int` | `12` | 坐标轴标签字号（磅） |
| `tick_fontsize` | `int` | `10` | 刻度标签字号（磅） |
| `grid` | `bool` | `True` | 是否显示背景网格 |
| `grid_alpha` | `float` | `0.3` | 网格线透明度（0=不可见, 1=完全不透明） |
| `tight_layout` | `bool` | `True` | 渲染时使用 `bbox_inches='tight'` |
| `facecolor` | `str` | `"white"` | 图表背景色（任意 CSS 颜色名或十六进制值） |

### .format(fmt) → PlotBuilder

设置渲染输出格式。

```python
def format(self, fmt: str) -> PlotBuilder
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `fmt` | `str` | `"png"`, `"svg"`, 或 `"pdf"`。无效值会引发 `ValueError`。 |

### .render() → ChartResult

触发图表生成。此时执行整个管线：
1. 构建用户提示词 → 调用 LLM（含重试）
2. 安全审查（正则 + 可选 LLM）
3. 沙箱执行（含失败自动修复）

```python
def render(self) -> ChartResult
```

多次调用 `.render()` 会返回缓存结果，不会重新执行管线。要强制重新生成，先调用 `.data()` / `.style()` / `.format()`（它们会清除缓存）。

### .save(path: str = None) → str

便捷方法：先调用 `.render()`，再调用结果的 `.save()`。

```python
def save(self, path: str = None) -> str
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `path` | `str` 或 `None` | 文件路径。格式根据扩展名自动检测（.png/.svg/.pdf）。`None` 时保存至 `output_dir/chart_{timestamp}.png`。 |

**返回值：** 文件保存的绝对路径。

### .image_bytes（属性）→ bytes

触发图表生成，返回主格式的图像字节。

```python
@property
def image_bytes(self) -> bytes
```

### .code（属性）→ str

触发图表生成，返回 LLM 生成的 matplotlib 代码。

```python
@property
def code(self) -> str
```

---

## AsyncPlotBuilder（异步构建器）

`PlotBuilder` 的异步版本。API 相同，但 `render()` 和 `save()` 是异步协程。

| 方法 | 是否需要 `await` | 签名 |
|------|-----------------|------|
| `.data(data)` | 否 | `(data) -> AsyncPlotBuilder` |
| `.style(spec)` | 否 | `(style_spec: dict \| str) -> AsyncPlotBuilder` |
| `.format(fmt)` | 否 | `(fmt: str) -> AsyncPlotBuilder` |
| `await .render()` | **是** | `async () -> ChartResult` |
| `await .save(path=None)` | **是** | `async (path: str = None) -> str` |

**示例：**

```python
async def main():
    lp = AsyncllmPIC(...)
    result = await lp.plot("CPU趋势").data(df).style({"color_scheme":"warm"}).render()
    result.show()

asyncio.run(main())
```

---

## ChartResult（结果对象）

封装一次图表生成的完整结果。由 `PlotBuilder.render()` 和 `AsyncPlotBuilder.render()` 返回。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `success` | `bool` | 图表生成是否成功 |
| `image_bytes` | `bytes \| None` | 主格式图像字节（默认 PNG）。失败时为 `None`。 |
| `error_message` | `str \| None` | 错误描述。成功时为 `None`。 |
| `code` | `str \| None` | 生成的 matplotlib Python 代码。失败时为 `None`。 |
| `token_usage` | `dict` | Token 用量：`{"input": N, "output": M}`。失败时为空字典。 |
| `size_kb` | `float` | 图片大小（KB）。无图像时为 `0.0`。 |
| `svg_bytes` | `bytes` | SVG 格式字节。懒加载 — 首次访问时根据存储的代码重新渲染，之后缓存。 |
| `pdf_bytes` | `bytes` | PDF 格式字节。懒加载 — 首次访问时根据存储的代码重新渲染，之后缓存。 |
| `svg` | `str` | SVG 的 UTF-8 字符串。委托给 `svg_bytes.decode('utf-8')`。 |

**关于懒加载格式属性的说明：** `svg_bytes` 和 `pdf_bytes` 通过以不同格式重新执行存储的 matplotlib 代码来工作。这意味着：
- 即使原始渲染是 PNG，也可以获取 SVG/PDF
- 需要 `ChartResult` 由 SDK 实例创建（需要 `_sdk` 引用）
- 首次访问后缓存 — 后续访问即时返回

### 方法

#### .save(path: str = None) → str

保存图表到文件。格式根据扩展名自动检测。

```python
def save(self, path: str = None) -> str
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `path` | `str \| None` | 输出文件路径。`None` 时保存至 `~/llmpic_charts/chart_{YYYYMMDD_HHMMSS}.png`。 |

| 扩展名 | 格式 | 工作原理 |
|--------|------|---------|
| `.png` | PNG | 直接使用 `image_bytes` |
| `.svg` | SVG | 使用 `svg_bytes`（懒加载重新渲染） |
| `.pdf` | PDF | 使用 `pdf_bytes`（懒加载重新渲染） |

**返回值：** 文件保存的绝对路径。

**异常：** `success` 为 `False` 时引发 `RuntimeError`。

```python
result.save()                        # → ~/llmpic_charts/chart_20250101_120000.png
result.save("chart.png")             # PNG
result.save("chart.svg")             # SVG（若原始为PNG则懒加载重新渲染）
result.save("chart.pdf")             # PDF（若原始为PNG则懒加载重新渲染）
result.save("/abs/path/chart.png")   # 绝对路径
```

#### .show()

在 Jupyter Notebook 或 IPython 中内联显示图表。

```python
def show(self) -> None
```

- 在 Jupyter/IPython 中：在 cell 下方直接渲染图表
- 在普通 Python 中：记录一条警告（不会报错）
- 支持 PNG、SVG、PDF 格式
- `success` 为 `False` 时引发 `RuntimeError`

```python
result = lp.plot("CPU使用趋势").render()
result.show()  # 在 Jupyter cell 下方直接出图
```

#### .base64() → str

返回 PNG 的 base64 数据 URI。

```python
def base64(self) -> str
```

返回：`"data:image/png;base64,{base64编码的字节}"`

用于 HTML、Markdown 或 API 嵌入：
```html
<img src="{result.base64()}" />
```

#### .base64_svg() → str

返回 SVG 的 base64 数据 URI。

```python
def base64_svg(self) -> str
```

返回：`"data:image/svg+xml;base64,{base64编码的字节}"`

#### .edit(edit_query: str) → ChartResult

用自然语言修改图表。返回**新的** `ChartResult` —— 原始对象不受影响。

```python
def edit(self, edit_query: str) -> ChartResult
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `edit_query` | `str` | 自然语言修改描述。例如：`"改成红色柱子"`、`"换成折线图，加网格"`、`"标题字号加大到18，用暖色系"` |

**返回值：** 包含修改后图表的**新** `ChartResult`。

**执行管线：** 发送当前代码 + 修改描述 → LLM 返回修改后代码 → 安全审查 → 沙箱执行 → 新 ChartResult。

**必要条件：**
- `ChartResult` 的 `success` 必须为 `True`
- `ChartResult` 必须由 SDK 实例创建（内部持有 `_sdk` 引用）

**示例：**

```python
v1 = lp.plot("月度销售: 1月=100").render()

# edit() 不改变 v1
v2 = v1.edit("改成柱状图，红色")
v3 = v2.edit("标题改为'Q1报告'，添加网格线")
v4 = v3.edit("标题字号加大到18")

v4.save("final.png")

# v1, v2, v3 仍然可用，方便随时回溯
v1.save("v1_original.png")
```

#### .__repr__() → str

```python
def __repr__(self) -> str
```

返回：
- 成功时：`"ChartResult(ok, {size_kb:.1f}KB, {format})"`
- 失败时：`"ChartResult(fail, {error_message!r})"`

---

## SandboxExecutor（沙箱执行器）

在受限沙箱环境中执行 matplotlib 代码。由 `llmPIC` 内部使用 — 大多数用户无需直接与此类交互。

### 构造函数

```python
SandboxExecutor(
    chinese_font: bool = True,
    timeout: int = 30,
    dpi: int = 150,
    output_dir: str = "~/llmpic_charts",
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `chinese_font` | `bool` | `True` | 构造时启用 CJK 字体自动检测 |
| `timeout` | `int` | `30` | 代码执行超时（秒） |
| `dpi` | `int` | `150` | 默认渲染 DPI |
| `output_dir` | `str` | `"~/llmpic_charts"` | 输出目录（不存在则自动创建） |

### execute()

```python
def execute(
    self,
    code: str,
    style: dict = None,
    format: str = 'png',
) -> Tuple[bytes | None, str | None]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `code` | `str` | **必填** | 要执行的 matplotlib Python 代码 |
| `style` | `dict` | `{}` | 样式字典（figsize, dpi, facecolor, tight_layout） |
| `format` | `str` | `"png"` | 输出格式：`"png"`, `"svg"`, 或 `"pdf"` |

**返回值：** `(image_bytes, error_message)` 元组。两者恰好有一个为 `None`。

### 沙箱保障

沙箱提供以下保障：

1. **受限命名空间** — 仅包含安全内置函数 + `mpl`(matplotlib)、`plt`(代理)、`np`(numpy)、`pd`(pandas，若可用)、`sns`(seaborn，若可用)、`Figure`
2. **plt 拦截** — `plt.show()`、`plt.savefig()`、`plt.close()` 均为空操作
3. **Figure.savefig 拦截** — 代码无法直接写入文件；沙箱统一接管渲染
4. **Figure.__init__ 追踪** — 沙箱检测代码创建的图形对象
5. **超时熔断** — 代码在 `ThreadPoolExecutor` 中执行，可配置超时
6. **全局互斥锁** — 模块级 `threading.Lock` 防止并发生成时的 matplotlib 状态冲突
7. **字体缓存** — CJK 字体检测仅在模块级运行一次，之后缓存

### 内部架构（供理解，非使用接口）

```
execute()
  │
  ├─ _ensure_font()           ← 模块级缓存
  │
  ├─ _execl_lock（互斥锁）    ← 防止 matplotlib 竞争
  │
  └─ _execute()               ← ThreadPoolExecutor + 超时
       │
       ├─ 猴子补丁 Figure.__init__ / Figure.savefig
       ├─ 构建安全命名空间
       ├─ exec(code, namespace)         ← 线程池中执行
       ├─ 检测创建的图形对象
       ├─ 通过原始 Figure.savefig 渲染
       └─ 恢复 Figure 猴子补丁
```

---

## CodeSafetyChecker（安全检查器）

双重代码安全验证。由 `llmPIC` 内部使用 — 大多数用户无需直接与此类交互。

### 构造函数

```python
CodeSafetyChecker(
    client: OpenAI,
    model: str,
    level: str = "fast",
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `client` | `OpenAI` | **必填** | OpenAI 客户端实例（`full` 模式下用于 LLM 审查） |
| `model` | `str` | **必填** | LLM 安全审查使用的模型名称 |
| `level` | `str` | `"fast"` | `"fast"` — 仅正则。`"full"` — 正则 + LLM 语义审查。 |

### check()

```python
def check(
    self,
    code: str,
    llm_review: bool = None,
) -> Tuple[bool, str]
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| `code` | `str` | **必填** | 要检查的 Python 代码 |
| `llm_review` | `bool \| None` | `None` | 覆盖安全级别：`True`=LLM审查，`False`=仅正则，`None`=使用实例默认值 |

**返回值：** `(is_safe: bool, reason: str)`
- `(True, "")` — 代码通过所有检查
- `(False, "Forbidden operations:\n  - os.system()\n  - ...")` — 发现正则违规
- `(False, "LLM review: 代码尝试访问文件系统")` — LLM 审查标记代码有问题

### regex_check()

```python
def regex_check(self, code: str) -> List[str]
```

**返回值：** 违规标签列表（空列表 = 安全）。

32 条预编译规则覆盖：

| 类别 | 违规标签 |
|------|---------|
| 系统命令 | `os.system()`, `os.popen()`, `os.exec*()`, `os.spawn*()`, `subprocess` |
| 文件操作 | `os.remove()`, `os.unlink()`, `os.rmdir()`, `os.rename()`, `os.mkdir/makedirs()`, `os.chmod()`, `os.environ`, `open()` |
| 动态执行 | `exec()`, `eval()`, `compile()`, `__import__()` |
| 网络访问 | `socket`, `urllib`, `requests`, `httpx`, `curl` |
| 进程退出 | `sys.exit()` |
| 危险模块 | `shutil`, `ctypes`, `pickle` |
| 反射逃逸 | `setattr()`, `delattr()`, `__subclasses__`, `__bases__`, `__mro__` |

### llm_review()

```python
def llm_review(self, code: str) -> Tuple[bool, str]
```

将代码（去除注释后）发送给 LLM 进行语义安全审查。使用 `temperature=0` 和 JSON 结构化输出。

**返回值：** `(is_safe: bool, reason: str)`

### _strip_comments()（静态方法）

```python
@staticmethod
def _strip_comments(code: str) -> str
```

使用 `tokenize` 模块去除 Python 注释，保留字符串字面量。在 LLM 审查前使用，防止通过注释进行 prompt 注入。

---

## 配置常量

可通过 `llmpic.templates` 导入：

```python
from llmpic.templates import DEFAULT_STYLE, COLOR_SCHEMES, LANGUAGE_HINTS
```

### DEFAULT_STYLE（默认样式）

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

所有键可通过 `.style()` 覆盖。未指定的键使用以上默认值。

### COLOR_SCHEMES（配色方案）

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

每种方案含 5 种颜色。LLM 用这些颜色作为图表元素的调色板。

### LANGUAGE_HINTS（语言提示）

```python
LANGUAGE_HINTS = {
    'en': 'Use English for all labels and titles.',
    'zh': 'Use Simplified Chinese (简体中文) for all labels and titles.',
    'ja': 'Use Japanese (日本語) for all labels and titles.',
    'ko': 'Use Korean (한국어) for all labels and titles.',
}
```

语言由 `detect_language()` 从查询文本中自动检测。

### detect_language()（语言检测函数）

```python
from llmpic.templates import detect_language

def detect_language(text: str) -> str
```

返回以下之一：`'zh'`, `'ja'`, `'ko'`, `'en'`。

检测逻辑：
- **`'zh'`**：CJK 统一表意文字（U+4E00–U+9FFF）或扩展 A 区（U+3400–U+4DBF）
- **`'ja'`**：日文假名（U+3040–U+30FF）或片假名扩展（U+31F0–U+31FF）
- **`'ko'`**：韩文谚文音节（U+AC00–U+D7AF）
- **`'en'`**：默认（未检测到 CJK 字符）

---

## 常用模式

### 模式一：快速一行

```python
llmPIC(api_key="...", base_url="...").plot("销售趋势").save("chart.png")
```

### 模式二：标准工作流

```python
lp = llmPIC(api_key="...", base_url="...")

result = (lp.plot("销售趋势")
           .data(df)
           .style({"color_scheme": "warm", "dpi": 200})
           .render())

if result.success:
    result.save("chart.png")
    print(f"成功: {result.size_kb:.1f}KB")
else:
    print(f"失败: {result.error_message}")
```

### 模式三：一次调用导出三格式

```python
result = lp.bar("各地区营收").data(df).render()

result.save("chart.png")   # PNG
result.save("chart.svg")   # SVG（懒加载重新渲染）
result.save("chart.pdf")   # PDF（懒加载重新渲染）
```

### 模式四：查看代码并迭代编辑

```python
result = lp.plot("月度销售").render()
print(result.code)          # 查看 LLM 生成的代码
print(result.token_usage)   # 查看 Token 用量

# 逐步优化
result = result.edit("改成柱状图")
result = result.edit("柱子颜色改为红色，标题改为'Q1营收'")
result.save("final.png")
```

### 模式五：错误分类处理

```python
result = lp.plot("复杂图表").data(df).render()

if not result.success:
    if "Safety rejected" in (result.error_message or ""):
        print("LLM生成了不安全代码 —— 尝试重新措辞")
    elif "timed out" in (result.error_message or ""):
        print("图表太复杂 —— 增加超时时间或简化需求")
    elif "no code" in (result.error_message or ""):
        print("LLM未能理解需求 —— 描述更具体或提供数据")
    else:
        print(f"未知错误: {result.error_message}")
```

### 模式六：Jupyter 工作流

```python
# Cell 1: 初始化
from llmpic import llmPIC
lp = llmPIC(api_key="...", base_url="...")

# Cell 2: 快速探索
lp.plot("销售额分布").data(df).render().show()

# Cell 3: 精细调整
result = lp.plot("销售额分布").data(df).render()
result = result.edit("叠加KDE密度曲线，使用暗色主题")
result.show()

# Cell 4: 导出最终版
result.save("final_distribution.png")
```

### 模式七：异步批量 + 日志

```python
import asyncio, logging
from llmpic import AsyncllmPIC

logging.basicConfig(level=logging.INFO)

async def main():
    lp = AsyncllmPIC(api_key="...", base_url="...")
    results = await lp.batch(requests)

    for i, r in enumerate(results):
        status = "成功" if r.success else "失败"
        print(f"[{i}] {status}: {r}")
        if r.success:
            r.save(f"out_{i}.png")

asyncio.run(main())
```

---

← [返回首页](../README_CN.md)
