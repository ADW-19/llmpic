# API 参考 — llmpic

> 所有类、方法、参数的完整说明。

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

---



## llmPIC（同步 SDK）

主入口类，所有同步图表生成由此开始。

### 构造函数

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

| 参数                  | 类型      | 默认值         | 说明                                             |
| --------------------- | --------- | -------------- | ------------------------------------------------ |
| `api_key`           | `str`   | 必填           | OpenAI 兼容 API 密钥                             |
| `base_url`          | `str`   | 必填           | API 地址，如 `https://api.openai.com/v1`       |
| `model`             | `str`   | `"gpt-4o"`   | 代码生成使用的模型                               |
| `safety_model`      | `str`   | `None`       | 安全审查使用的模型（默认与 model 相同）          |
| `safety_level`      | `str`   | `"fast"`     | 安全级别：`"fast"` 仅正则，`"full"` 正则+LLM |
| `chinese_font`      | `bool`  | `True`       | 是否启用中日韩字体支持                           |
| `timeout`           | `int`   | `30`         | 代码执行超时（秒）                               |
| `dpi`               | `int`   | `150`        | 默认输出 DPI                                     |
| `output_dir`        | `str`   | `"~/llmpic_charts"` | 默认输出目录（用户主目录下，支持相对/绝对路径） |
| `temperature`       | `float` | `0.3`        | LLM 生成温度（0-2）                              |
| `max_tokens`        | `int`   | `2048`       | LLM 最大输出 tokens                              |
| `structured_output` | `bool`  | `True`       | 是否使用 JSON 结构化输出                         |
| `max_retries`       | `int`   | `3`          | LLM 调用失败最大重试次数（指数退避：1s, 2s, 4s） |
| `max_fix_attempts`  | `int`   | `2`          | 代码执行失败自动修复次数                         |

### 图表类型方法

所有方法返回 `PlotBuilder` 对象，可链式调用 `.data()` `.style()` `.format()` `.render()` `.save()`。

| 方法                 | 返回类型        | 说明         |
| -------------------- | --------------- | ------------ |
| `.plot(query)`     | `PlotBuilder` | 折线图       |
| `.scatter(query)`  | `PlotBuilder` | 散点图       |
| `.bar(query)`      | `PlotBuilder` | 柱状图       |
| `.pie(query)`      | `PlotBuilder` | 饼图         |
| `.hist(query)`     | `PlotBuilder` | 直方图       |
| `.heatmap(query)`  | `PlotBuilder` | 热力图       |
| `.boxplot(query)`  | `PlotBuilder` | 箱线图       |
| `.area(query)`     | `PlotBuilder` | 面积图       |
| `.radar(query)`    | `PlotBuilder` | 雷达图       |
| `.subplots(query)` | `PlotBuilder` | 子图仪表盘   |
| `.custom(query)`   | `PlotBuilder` | 智能推荐类型 |

参数 `query: str` — 自然语言图表描述，支持中、日、韩、英文。

---


## AsyncllmPIC（异步 SDK）

异步版本，参数与 `llmPIC` 完全一致。额外提供批量并发生成。

### 构造函数

参数与 `llmPIC` 完全相同。

### 图表类型方法

与 `llmPIC` 相同的 11 种方法，返回 `AsyncPlotBuilder`。

### async batch()

```python
async def batch(
    requests: List[Tuple[str, str]]
) -> List[ChartResult]
```

并发生成多张图表。

| 参数         | 类型                      | 说明                                   |
| ------------ | ------------------------- | -------------------------------------- |
| `requests` | `List[Tuple[str, str]]` | `[(图表类型, 查询描述), ...]` 的列表 |

图表类型可选值：`"line"` `"scatter"` `"bar"` `"pie"` `"hist"` `"heatmap"` `"boxplot"` `"area"` `"radar"` `"subplots"` `"custom"`

返回值：与 `requests` 顺序一一对应的 `ChartResult` 列表。

```python
results = await lp.batch([
    ("plot", "CPU趋势"),
    ("bar", "销售额"),
    ("scatter", "相关性"),
])
```

---


## PlotBuilder（同步构建器）

流式构建器，所有方法支持链式调用。**惰性执行**：仅在调用 `.render()` / `.save()` 或访问 `.image_bytes` / `.code` 时才触发生成。

### 方法

#### .data(data)

附加数据。

| 参数     | 类型                                                        | 说明                                  |
| -------- | ----------------------------------------------------------- | ------------------------------------- |
| `data` | `DataFrame` / `ndarray` / `dict` / `list` / `str` | 图表数据，未调用则让 LLM 生成演示数据 |

#### .style(style_spec)

设置视觉样式。

| 参数           | 类型                      | 说明     |
| -------------- | ------------------------- | -------- |
| `style_spec` | `dict` 或 `str`(JSON) | 样式配置 |

**支持的样式键：**

| 键                 | 类型           | 默认值      | 说明                                                                    |
| ------------------ | -------------- | ----------- | ----------------------------------------------------------------------- |
| `figsize`        | `[int, int]` | `[10, 6]` | 图表尺寸（英寸）                                                        |
| `dpi`            | `int`        | `150`     | 输出分辨率                                                              |
| `color_scheme`   | `str`        | `"blues"` | 配色方案：`blues` `warm` `cool` `pastel` `dark` `grayscale` |
| `title_fontsize` | `int`        | `14`      | 标题字号                                                                |
| `label_fontsize` | `int`        | `12`      | 坐标轴标签字号                                                          |
| `tick_fontsize`  | `int`        | `10`      | 刻度字号                                                                |
| `grid`           | `bool`       | `True`    | 是否显示网格                                                            |
| `grid_alpha`     | `float`      | `0.3`     | 网格透明度                                                              |
| `tight_layout`   | `bool`       | `True`    | 是否紧凑布局                                                            |
| `facecolor`      | `str`        | `"white"` | 图表背景色                                                              |

#### .format(fmt)

设置输出格式。

| 参数    | 类型    | 默认值    | 说明                               |
| ------- | ------- | --------- | ---------------------------------- |
| `fmt` | `str` | `"png"` | `"png"` `"svg"` `"pdf"` 之一 |

#### .render()

触发图表生成，返回 `ChartResult`。

#### .save(path=None)

触发生成并保存到文件。格式由扩展名决定，路径可选（默认 `~/llmpic_charts/`）。

#### .image_bytes（属性）

触发图表生成，返回 PNG 字节。

#### .code（属性）

触发图表生成，返回生成的 matplotlib 代码。

---


## AsyncPlotBuilder（异步构建器）

异步版本的流式构建器，使用方式与 `PlotBuilder` 相同，但关键方法需 `await`。

| 方法                  | 异步         | 说明         |
| --------------------- | ------------ | ------------ |
| `.data(data)`       | 否           | 附加数据     |
| `.style(spec)`      | 否           | 设置样式     |
| `.format(fmt)`      | 否           | 设置输出格式 |
| `await .render()`   | **是** | 触发生成     |
| `await .save(path=None)` | **是** | 生成并保存，路径可选 |

---


## ChartResult（结果对象）

封装图表生成结果。

### 属性

| 属性              | 类型                | 说明                                     |
| ----------------- | ------------------- | ---------------------------------------- |
| `success`       | `bool`            | 是否成功                                 |
| `image_bytes`   | `bytes`           | 主格式字节（默认 PNG）                   |
| `error_message` | `str` 或 `None` | 错误信息                                 |
| `code`          | `str` 或 `None` | 生成的 matplotlib 代码                   |
| `token_usage`   | `dict`            | Token 用量 `{"input": N, "output": M}` |
| `size_kb`       | `float`           | 图片大小 (KB)                            |
| `svg_bytes`     | `bytes`           | SVG 字节（懒加载，首次访问时重新渲染）   |
| `pdf_bytes`     | `bytes`           | PDF 字节（懒加载）                       |
| `svg`           | `str`             | SVG 文本字符串                           |

### 方法

#### .save(path=None)

保存图表到文件。格式由扩展名自动决定，路径可选。

```python
result.save()                    # → ~/llmpic_charts/chart_20250101_120000.png
result.save("chart.png")        # PNG
result.save("chart.svg")        # SVG
result.save("chart.pdf")        # PDF
result.save("/abs/path/ch.png") # 绝对路径
```

#### .show()

在 Jupyter Notebook / IPython 中内联显示图表（无需额外操作）。

```python
result.show()  # cell 下方直接出图
```

#### .base64()

返回 PNG 的 base64 data URI：`data:image/png;base64,...`

#### .base64_svg()

返回 SVG 的 base64 data URI：`data:image/svg+xml;base64,...`

#### .edit(edit_query)

用自然语言修改图表，返回新的 `ChartResult`。

| 参数           | 类型    | 说明                                      |
| -------------- | ------- | ----------------------------------------- |
| `edit_query` | `str` | 修改描述，如 `"改成红色柱子，标题加粗"` |

```python
v1 = lp.plot("月度销售额").render()
v2 = v1.edit("改成柱状图，颜色换成红色")
v2.save("v2.png")
```

---


## SandboxExecutor（沙箱执行器）

在受限环境中执行 matplotlib 代码，返回图像字节。

### 构造函数

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

| 参数       | 类型     | 默认值    | 说明                                    |
| ---------- | -------- | --------- | --------------------------------------- |
| `code`   | `str`  | 必填      | matplotlib Python 代码                  |
| `style`  | `dict` | `{}`    | 样式字典                                |
| `format` | `str`  | `"png"` | 输出格式：`"png"` `"svg"` `"pdf"` |

沙箱执行机制：

- 禁止 `plt.show()` / `plt.savefig()` / `plt.close()` — 被拦截为无操作
- 禁止文件 I/O、系统命令、网络请求、动态执行
- 线程池执行 + 超时熔断
- 全局执行锁防止 matplotlib 状态竞争

---


## CodeSafetyChecker（安全检查器）

双重安全检查：正则模式匹配 + 可选 LLM 语义审查。

### 构造函数

```python
CodeSafetyChecker(
    client: OpenAI,
    model: str,
    level: str = "fast",
)
```

| 参数       | 类型       | 默认值     | 说明                                   |
| ---------- | ---------- | ---------- | -------------------------------------- |
| `client` | `OpenAI` | 必填       | OpenAI 客户端                          |
| `model`  | `str`    | 必填       | 审查模型                               |
| `level`  | `str`    | `"fast"` | `"fast"` 仅正则，`"full"` 正则+LLM |

### check()

```python
def check(
    code: str,
    llm_review: bool = None,
) -> tuple  # (is_safe: bool, reason: str)
```

### regex_check()

```python
def regex_check(code: str) -> list  # 违规标签列表
```

32 条预编译正则规则覆盖：系统命令、文件操作、动态执行、网络访问、危险模块、反射逃逸。

---


## 配置常量

### 配色方案

| 名称          | 颜色                                                        |
| ------------- | ----------------------------------------------------------- |
| `blues`     | `#3498DB` `#5DADE2` `#87CEEB` `#2980B9` `#AED6F1` |
| `warm`      | `#E74C3C` `#F39C12` `#E67E22` `#F1C40F` `#D35400` |
| `cool`      | `#1ABC9C` `#3498DB` `#9B59B6` `#2ECC71` `#16A085` |
| `pastel`    | `#FADBD8` `#D5F5E3` `#D6EAF8` `#F9E79F` `#E8DAEF` |
| `dark`      | `#2C3E50` `#34495E` `#7F8C8D` `#95A5A6` `#BDC3C7` |
| `grayscale` | `#333333` `#666666` `#999999` `#BBBBBB` `#DDDDDD` |

### 默认样式

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

← [返回首页](./README_CN.md)

```
