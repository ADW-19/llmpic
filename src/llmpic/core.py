"""Core module — llmPIC (sync), AsyncllmPIC (async), PlotBuilder, ChartResult."""

import json
import re
import time
import logging
import asyncio
import pathlib
from typing import Optional, Union, List, Tuple

import numpy as np
from openai import OpenAI, AsyncOpenAI

from .safety import CodeSafetyChecker
from .sandbox import SandboxExecutor
from .templates import (
    DEFAULT_STYLE, DEFAULT_MAP_STYLE, COLOR_SCHEMES, CHART_TYPE_PROMPTS,
    SYSTEM_PROMPT, FIX_PROMPT, EDIT_PROMPT,
    detect_language, LANGUAGE_HINTS,
)

try:
    import pandas as pd
except ImportError:
    pd = None

logger = logging.getLogger(__name__)

FIX_SYSTEM = "Fix this matplotlib code. Error given. Output JSON: {\"code\":\"<corrected>\"}. JSON only."
EDIT_SYSTEM = "Modify this matplotlib chart code per the edit request. Output JSON: {\"code\":\"<modified>\"}. JSON only."


# ═══════════════════════════════════════════════════════════════
#  ChartResult (shared)
# ═══════════════════════════════════════════════════════════════

class ChartResult:
    """Result of a chart generation. Supports PNG/SVG/PDF, base64, and iterative edit."""

    def __init__(self, success: bool, image_bytes: bytes = None,
                 error_message: str = None, code: str = None,
                 token_usage: dict = None,
                 _sdk=None, _chart_type: str = None, _query: str = None,
                 _data=None, _style: dict = None, _format: str = 'png'):
        self.success = success
        self.image_bytes = image_bytes          # primary format (defaults to png bytes)
        self.error_message = error_message
        self.code = code
        self.token_usage = token_usage or {}
        # Private: context for re-rendering (SVG/PDF/edit)
        self._sdk = _sdk
        self._chart_type = _chart_type
        self._query = _query
        self._data = _data
        self._style = _style or dict(DEFAULT_STYLE)
        self._format = _format
        # Lazy caches
        self._svg_bytes = None
        self._pdf_bytes = None

    # ── Save ──

    def save(self, path: str = None) -> str:
        """Save chart to file. Format auto-detected from extension.

        If path is not specified, saves to ~/llmpic_charts/chart_{timestamp}.png

        Examples:
            result.save()                          # → ~/llmpic_charts/chart_20250101_120000.png
            result.save("chart.svg")               # → SVG
            result.save("/abs/path/chart.pdf")     # → PDF
        """
        if not self.success:
            raise RuntimeError(f"Chart generation failed: {self.error_message}")

        if path is None:
            stamp = time.strftime("%Y%m%d_%H%M%S")
            path = str(pathlib.Path.home() / "llmpic_charts" / f"chart_{stamp}.png")

        p = pathlib.Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        ext = p.suffix.lower()
        fmt = {'png': 'png', '.png': 'png', '.svg': 'svg', '.pdf': 'pdf'}.get(ext, 'png')

        data = self.svg_bytes if fmt == 'svg' else (self.pdf_bytes if fmt == 'pdf' else self.image_bytes)
        with open(path, 'wb') as f:
            f.write(data)
        return path

    # ── Jupyter / IPython inline display ──

    def show(self):
        """Display chart inline in Jupyter Notebook or IPython."""
        if not self.success:
            raise RuntimeError(f"Chart generation failed: {self.error_message}")
        try:
            from IPython.display import display, Image as IPImage, SVG as IPSVG
        except ImportError:
            logger.warning("IPython not available; show() only works in Jupyter/IPython")
            return

        ext = ('.' + self._format) if not self._format.startswith('.') else self._format
        if ext in ('.svg',):
            display(IPSVG(self.svg))
        elif ext in ('.pdf',):
            display(IPImage(self.image_bytes, embed=True))
        else:
            display(IPImage(self.image_bytes, embed=True))

    # ── Format properties (lazy re-render) ──

    @property
    def svg_bytes(self) -> bytes:
        if self._format == 'svg' and self.image_bytes:
            return self.image_bytes
        if self._svg_bytes is None:
            self._svg_bytes = self._render_format('svg')
        return self._svg_bytes

    @property
    def pdf_bytes(self) -> bytes:
        if self._format == 'pdf' and self.image_bytes:
            return self.image_bytes
        if self._pdf_bytes is None:
            self._pdf_bytes = self._render_format('pdf')
        return self._pdf_bytes

    @property
    def svg(self) -> str:
        return self.svg_bytes.decode('utf-8')

    def _render_format(self, fmt: str) -> bytes:
        """Lazy re-render in a different format using stored code + style."""
        if not self.success or not self._sdk or not self.code:
            raise RuntimeError("Cannot re-render: no code context available")
        # _sdk may be a SandboxExecutor (tests) or an llmPIC/AsyncllmPIC
        sandbox = self._sdk._sandbox if hasattr(self._sdk, '_sandbox') else self._sdk
        img, err = sandbox.execute(self.code, self._style, format=fmt)
        if err:
            raise RuntimeError(f"Re-render failed ({fmt}): {err}")
        return img

    # ── Edit ──

    def edit(self, edit_query: str) -> 'ChartResult':
        """Modify this chart with natural language. Returns a new ChartResult."""
        if not self.success or not self._sdk or not self.code:
            raise RuntimeError("Cannot edit: no code context available")

        prompt = EDIT_PROMPT.format(edit=edit_query, code=self.code)
        code, tokens = self._sdk._generate_code(prompt, system_prompt=EDIT_SYSTEM)
        if not code:
            return ChartResult(False, error_message="Edit: LLM returned no code", token_usage=tokens)

        is_safe, reason = self._sdk._safety.check(code,
            llm_review=(self._sdk._safety_level == "full"))
        if not is_safe:
            return ChartResult(False, error_message=f"Edit safety rejected: {reason}", code=code, token_usage=tokens)

        img, err = self._sdk._sandbox.execute(code, self._style, format=self._format)
        if err:
            return ChartResult(False, error_message=f"Edit execution: {err}", code=code, token_usage=tokens)

        return ChartResult(True, image_bytes=img, code=code, token_usage=tokens,
                           _sdk=self._sdk, _chart_type=self._chart_type,
                           _query=f"{self._query} (edited: {edit_query})",
                           _data=self._data, _style=self._style, _format=self._format)

    # ── base64 ──

    def base64(self) -> str:
        import base64
        if not self.success:
            raise RuntimeError(f"Chart generation failed: {self.error_message}")
        data = base64.b64encode(self.image_bytes).decode()
        return f"data:image/png;base64,{data}"

    def base64_svg(self) -> str:
        import base64
        data = base64.b64encode(self.svg_bytes).decode()
        return f"data:image/svg+xml;base64,{data}"

    # ── Utils ──

    @property
    def size_kb(self) -> float:
        if self.image_bytes:
            return len(self.image_bytes) / 1024
        return 0.0

    def __repr__(self):
        if self.success:
            return f"ChartResult(ok, {self.size_kb:.1f}KB, {self._format})"
        return f"ChartResult(fail, {self.error_message!r})"


# ═══════════════════════════════════════════════════════════════
#  Shared helpers (module-level, stateless)
# ═══════════════════════════════════════════════════════════════

def _serialize_data(data) -> str:
    if data is None:
        return "No data. Generate realistic demo data with numpy (np.linspace, np.random, etc)."

    if pd is not None and isinstance(data, pd.DataFrame):
        parts = [
            f"DataFrame: {data.shape[0]}r x {data.shape[1]}c",
            f"Columns: {list(data.columns)}",
            f"Types: {dict(zip(data.columns, data.dtypes.astype(str)))}",
        ]
        if len(data) > 0:
            n_sample = min(5, len(data))
            parts.append(f"First {n_sample} rows:\n{data.head(n_sample).to_string()}")
            if len(data) > n_sample:
                parts.append(f"Stats:\n{data.describe().to_string()}")
        return "\n".join(parts)

    if pd is not None and isinstance(data, pd.Series):
        return f"Series '{data.name}': {data.dtype}\n{data.head(10).to_string()}"

    if isinstance(data, np.ndarray):
        if data.ndim == 1:
            return f"NumPy 1d: shape={data.shape}, dtype={data.dtype}\n{data[:10]}"
        else:
            return f"NumPy {data.ndim}d: shape={data.shape}, dtype={data.dtype}\n{data[:5]}"

    if isinstance(data, dict):
        lines = [f"Dict ({len(data)} keys): {list(data.keys())}"]
        for k, v in data.items():
            v_str = str(v)
            if len(v_str) > 150:
                v_str = v_str[:150] + "..."
            lines.append(f"  {k}: {v_str}")
        return "\n".join(lines)

    if isinstance(data, (list, tuple)):
        n = min(15, len(data))
        return f"List ({len(data)} items). First {n}: {data[:n]}"

    if isinstance(data, str):
        return data[:2000]

    return str(data)[:2000]


def _serialize_style(style: dict) -> str:
    parts = []
    if 'figsize' in style:
        w, h = style['figsize']
        parts.append(f"figsize=({w},{h})")
    if 'color_scheme' in style:
        scheme = style['color_scheme']
        colors = COLOR_SCHEMES.get(scheme, COLOR_SCHEMES['blues'])
        parts.append(f"colors={scheme} ({', '.join(colors[:5])})")
    if 'title_fontsize' in style:
        parts.append(f"title_fs={style['title_fontsize']}")
    if 'label_fontsize' in style:
        parts.append(f"label_fs={style['label_fontsize']}")
    if 'tick_fontsize' in style:
        parts.append(f"tick_fs={style['tick_fontsize']}")
    if 'grid' in style:
        parts.append(f"grid={'on' if style['grid'] else 'off'}"
                     f"{',alpha=' + str(style.get('grid_alpha', 0.3)) if style['grid'] else ''}")
    if 'facecolor' in style:
        parts.append(f"bg={style['facecolor']}")
    return "; ".join(parts) if parts else "default"


def _build_user_prompt(chart_type: str, query: str, data, style: dict) -> str:
    lang = detect_language(query or "")
    lang_hint = LANGUAGE_HINTS.get(lang, LANGUAGE_HINTS['en'])
    type_instruction = CHART_TYPE_PROMPTS.get(chart_type, CHART_TYPE_PROMPTS["custom"])
    return (
        f"Chart: {type_instruction}\n"
        f"Data: {_serialize_data(data)}\n"
        f"Style: {_serialize_style(style)}\n"
        f"Lang: {lang_hint}\n"
        f"Request: {query}"
    )


def _extract_code(content: str) -> Optional[str]:
    if not content:
        return None

    # 1. Try valid JSON
    try:
        data = json.loads(content)
        code = data.get("code", "").strip()
        if code:
            return code
    except (json.JSONDecodeError, TypeError):
        pass

    # 2. Try truncated JSON: {"code": "..."  without closing braces
    #    Use character-class alternation to properly skip JSON-escaped quotes (\").
    #    The old regex (.+?) would stop at the first " inside the code, truncating it.
    m = re.search(r'"code"\s*:\s*"((?:[^"\\]|\\.)*)(?:"|$)', content)
    if m:
        code = m.group(1)
        # Restore JSON-escaped sequences to their literal form
        code = (code.replace('\\"', '\x00')      # temp placeholder for escaped quotes
                    .replace('\\n', '\n')
                    .replace('\\t', '\t')
                    .replace('\\r', '\r')
                    .replace('\\\\', '\\')
                    .replace('\x00', '"'))
        if 'plt.' in code or 'ax.' in code:
            return code.strip()

    # 3. Try ```python ... ``` fence
    match = re.search(r'```(?:python)?\s*\n?(.*?)\n?```', content, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 4. Raw content if it looks like matplotlib code
    if 'plt.' in content or 'ax.' in content or 'fig,' in content:
        return content.strip()

    return None


# ═══════════════════════════════════════════════════════════════
#  PlotBuilder (sync)
# ═══════════════════════════════════════════════════════════════

class PlotBuilder:
    """Fluent (sync) builder. Lazy: nothing runs until render/save.

    Usage:
        sdk.plot("CPU trend").data(df).format('svg').save("cpu.svg")
    """

    def __init__(self, sdk: 'llmPIC', chart_type: str, query: str):
        self._sdk = sdk
        self._chart_type = chart_type
        self._query = query
        self._data = None
        self._style = dict(DEFAULT_STYLE)
        self._format = 'png'
        self._result = None

    def data(self, data) -> 'PlotBuilder':
        self._data = data
        self._result = None
        return self

    def style(self, style_spec) -> 'PlotBuilder':
        if isinstance(style_spec, str):
            style_spec = json.loads(style_spec)
        self._style = {**self._style, **style_spec}
        self._result = None
        return self

    def format(self, fmt: str) -> 'PlotBuilder':
        """Set output format: 'png', 'svg', or 'pdf'."""
        if fmt not in ('png', 'svg', 'pdf'):
            raise ValueError(f"Unsupported format '{fmt}'. Use 'png', 'svg', or 'pdf'.")
        self._format = fmt
        self._result = None
        return self

    def render(self) -> ChartResult:
        if self._result is not None:
            return self._result

        user_prompt = _build_user_prompt(
            self._chart_type, self._query, self._data, self._style)

        # 1. Generate code (with retry)
        code, tokens = self._sdk._generate_code(user_prompt)
        if not code:
            self._result = ChartResult(False, error_message="LLM returned no code. Try rephrasing.", token_usage=tokens)
            return self._result

        # 2. Safety check
        is_safe, reason = self._sdk._safety.check(code,
            llm_review=(self._sdk._safety_level == "full"))
        if not is_safe:
            self._result = ChartResult(False, error_message=f"Safety rejected: {reason}", code=code, token_usage=tokens)
            return self._result

        # 3. Execute in sandbox (with auto-fix on failure)
        image_bytes, error = self._sdk._sandbox.execute(code, self._style, format=self._format)
        fix_attempts = getattr(self._sdk, '_max_fix_attempts', 2)

        while error and fix_attempts > 0:
            logger.info("Auto-fix attempt %d: %s", fix_attempts, error[:100])
            fixed_code, fix_tokens = self._sdk._fix_code(code, error, self._query)
            if not fixed_code:
                break
            tokens['input'] += fix_tokens.get('input', 0)
            tokens['output'] += fix_tokens.get('output', 0)
            code = fixed_code

            is_safe, reason = self._sdk._safety.check(code,
                llm_review=(self._sdk._safety_level == "full"))
            if not is_safe:
                error = f"Fix safety rejected: {reason}"
                break

            image_bytes, error = self._sdk._sandbox.execute(code, self._style, format=self._format)
            fix_attempts -= 1

        if error:
            self._result = ChartResult(False, error_message=error, code=code, token_usage=tokens)
        else:
            self._result = ChartResult(True, image_bytes=image_bytes, code=code, token_usage=tokens,
                                       _sdk=self._sdk, _chart_type=self._chart_type,
                                       _query=self._query, _data=self._data,
                                       _style=self._style, _format=self._format)

        return self._result

    @property
    def image_bytes(self) -> bytes:
        return self.render().image_bytes

    @property
    def code(self) -> str:
        return self.render().code

    def save(self, path: str) -> str:
        return self.render().save(path)

    def __repr__(self):
        return f"PlotBuilder({self._chart_type}, {self._query!r})"


# ═══════════════════════════════════════════════════════════════
#  AsyncPlotBuilder
# ═══════════════════════════════════════════════════════════════

class AsyncPlotBuilder:
    """Fluent async builder. Lazy: nothing runs until await render/save."""

    def __init__(self, sdk: 'AsyncllmPIC', chart_type: str, query: str):
        self._sdk = sdk
        self._chart_type = chart_type
        self._query = query
        self._data = None
        self._style = dict(DEFAULT_STYLE)
        self._format = 'png'
        self._result = None

    def data(self, data) -> 'AsyncPlotBuilder':
        self._data = data
        self._result = None
        return self

    def style(self, style_spec) -> 'AsyncPlotBuilder':
        if isinstance(style_spec, str):
            style_spec = json.loads(style_spec)
        self._style = {**self._style, **style_spec}
        self._result = None
        return self

    def format(self, fmt: str) -> 'AsyncPlotBuilder':
        if fmt not in ('png', 'svg', 'pdf'):
            raise ValueError(f"Unsupported format '{fmt}'. Use 'png', 'svg', or 'pdf'.")
        self._format = fmt
        self._result = None
        return self

    async def render(self) -> ChartResult:
        if self._result is not None:
            return self._result

        user_prompt = _build_user_prompt(
            self._chart_type, self._query, self._data, self._style)

        # 1. Generate code (async, with retry)
        code, tokens = await self._sdk._generate_code(user_prompt)
        if not code:
            self._result = ChartResult(False, error_message="LLM returned no code.", token_usage=tokens)
            return self._result

        # 2. Safety check
        is_safe, reason = self._sdk._safety.check(code,
            llm_review=(self._sdk._safety_level == "full"))
        if not is_safe:
            self._result = ChartResult(False, error_message=f"Safety rejected: {reason}", code=code, token_usage=tokens)
            return self._result

        # 3. Execute + auto-fix
        loop = asyncio.get_running_loop()
        image_bytes, error = await loop.run_in_executor(
            None, self._sdk._sandbox.execute, code, self._style, self._format)
        fix_attempts = getattr(self._sdk, '_max_fix_attempts', 2)

        while error and fix_attempts > 0:
            logger.info("Async auto-fix attempt %d: %s", fix_attempts, error[:100])
            fixed_code, fix_tokens = await self._sdk._fix_code(code, error, self._query)
            if not fixed_code:
                break
            tokens['input'] += fix_tokens.get('input', 0)
            tokens['output'] += fix_tokens.get('output', 0)
            code = fixed_code

            is_safe, reason = self._sdk._safety.check(code,
                llm_review=(self._sdk._safety_level == "full"))
            if not is_safe:
                error = f"Fix safety rejected: {reason}"
                break

            image_bytes, error = await loop.run_in_executor(
                None, self._sdk._sandbox.execute, code, self._style, self._format)
            fix_attempts -= 1

        if error:
            self._result = ChartResult(False, error_message=error, code=code, token_usage=tokens)
        else:
            self._result = ChartResult(True, image_bytes=image_bytes, code=code, token_usage=tokens,
                                       _sdk=self._sdk, _chart_type=self._chart_type,
                                       _query=self._query, _data=self._data,
                                       _style=self._style, _format=self._format)

        return self._result

    async def save(self, path: str) -> str:
        result = await self.render()
        return result.save(path)

    async def base64(self) -> str:
        result = await self.render()
        return result.base64()

    @property
    async def image_bytes(self) -> bytes:
        r = await self.render()
        return r.image_bytes

    def __repr__(self):
        return f"AsyncPlotBuilder({self._chart_type}, {self._query!r})"


# ═══════════════════════════════════════════════════════════════
#  llmPIC (sync SDK)
# ═══════════════════════════════════════════════════════════════

class llmPIC:
    """LLM-powered chart generation SDK (sync).

    Usage:
        sdk = llmPIC(api_key="sk-...", base_url="https://api.openai.com/v1")
        sdk.plot("CPU trend").data(df).save("cpu.png")
        sdk.heatmap("correlation matrix").data(df).format('svg').save("heat.svg")

        # Edit an existing chart
        result = sdk.plot("sales trend").render()
        result.edit("make bars red, change title to Revenue").save("v2.png")

    Key params:
        safety_level: "fast" (regex only) or "full" (regex + LLM)
        max_retries: LLM retries on transient errors (default 3)
        max_fix_attempts: auto-fix on code execution errors (default 2)
    """

    def __init__(
        self,
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
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._structured_output = structured_output
        self._max_retries = max_retries
        self._max_fix_attempts = max_fix_attempts
        self._safety_level = safety_level

        self._client = OpenAI(api_key=api_key, base_url=base_url, max_retries=0)
        self._safety = CodeSafetyChecker(self._client, safety_model or model, level=safety_level)
        self._sandbox = SandboxExecutor(
            chinese_font=chinese_font, timeout=timeout, dpi=dpi, output_dir=output_dir)

    # ── Chart type entry points ──

    def plot(self, query: str) -> PlotBuilder:
        return PlotBuilder(self, "line", query)

    def scatter(self, query: str) -> PlotBuilder:
        return PlotBuilder(self, "scatter", query)

    def bar(self, query: str) -> PlotBuilder:
        return PlotBuilder(self, "bar", query)

    def pie(self, query: str) -> PlotBuilder:
        return PlotBuilder(self, "pie", query)

    def hist(self, query: str) -> PlotBuilder:
        return PlotBuilder(self, "hist", query)

    def heatmap(self, query: str) -> PlotBuilder:
        return PlotBuilder(self, "heatmap", query)

    def boxplot(self, query: str) -> PlotBuilder:
        return PlotBuilder(self, "boxplot", query)

    def area(self, query: str) -> PlotBuilder:
        return PlotBuilder(self, "area", query)

    def radar(self, query: str) -> PlotBuilder:
        return PlotBuilder(self, "radar", query)

    def subplots(self, query: str) -> PlotBuilder:
        return PlotBuilder(self, "subplots", query)

    def custom(self, query: str) -> PlotBuilder:
        return PlotBuilder(self, "custom", query)

    def map(self, query: str) -> PlotBuilder:
        """Generate a geographic map chart.

        Supports choropleth maps, scatter point maps, and world maps.
        Uses cartopy for projections if installed, falls back to pure matplotlib.

        Examples:
            sdk.map("World population by country").save("world.png")
            sdk.map("China major cities, red markers").save("china.png")
            sdk.map("Earthquake epicenters in Japan").data(df).save("japan.png")
        """
        builder = PlotBuilder(self, "map", query)
        builder._style = {**DEFAULT_STYLE, **DEFAULT_MAP_STYLE}
        return builder

    # ── Internal: LLM code generation ──

    def _generate_code(self, user_prompt: str, system_prompt: str = None) -> Tuple[Optional[str], dict]:
        """Call LLM to generate code. Retries on transient failures."""
        sp = system_prompt or SYSTEM_PROMPT
        last_error = None
        kwargs = dict(
            model=self.model,
            messages=[
                {"role": "system", "content": sp},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        if self._structured_output:
            kwargs["response_format"] = {"type": "json_object"}

        for attempt in range(self._max_retries):
            try:
                response = self._client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                tokens = {
                    "input": response.usage.prompt_tokens if response.usage else 0,
                    "output": response.usage.completion_tokens if response.usage else 0,
                }
                code = _extract_code(content)
                if code:
                    return (code, tokens)
                last_error = f"Unparseable response (attempt {attempt + 1})"
                logger.warning(last_error)
            except Exception as e:
                last_error = str(e)
                logger.warning("LLM error (attempt %d/%d): %s", attempt + 1, self._max_retries, e)

            if attempt < self._max_retries - 1:
                delay = 1.0 * (2 ** attempt)
                logger.debug("Retrying in %.1fs...", delay)
                time.sleep(delay)

        logger.error("All %d generation attempts failed: %s", self._max_retries, last_error)
        return (None, {})

    # ── Internal: auto-fix code ──

    def _fix_code(self, code: str, error: str, query: str) -> Tuple[Optional[str], dict]:
        """Ask LLM to fix code that failed execution. Returns (fixed_code, tokens)."""
        prompt = FIX_PROMPT.format(code=code, error=error[:1200])
        return self._generate_code(prompt, system_prompt=FIX_SYSTEM)


# ═══════════════════════════════════════════════════════════════
#  AsyncllmPIC (async SDK)
# ═══════════════════════════════════════════════════════════════

class AsyncllmPIC:
    """Async LLM-powered chart generation SDK.

    Usage:
        sdk = AsyncllmPIC(api_key="sk-...", base_url="https://api.openai.com/v1")
        await sdk.plot("CPU trend").save("cpu.png")

        # Batch concurrent
        results = await sdk.batch([
            ("plot", "CPU trend"),
            ("bar", "Sales by region"),
        ])
    """

    def __init__(
        self,
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
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._structured_output = structured_output
        self._max_retries = max_retries
        self._max_fix_attempts = max_fix_attempts
        self._safety_level = safety_level

        try:
            self._client = AsyncOpenAI(api_key=api_key, base_url=base_url, max_retries=0)
        except TypeError:
            self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._safety = CodeSafetyChecker(
            OpenAI(api_key=api_key, base_url=base_url, max_retries=0),
            safety_model or model, level=safety_level)
        self._sandbox = SandboxExecutor(
            chinese_font=chinese_font, timeout=timeout, dpi=dpi, output_dir=output_dir)

    # ── Chart type entry points ──

    def plot(self, query: str) -> AsyncPlotBuilder:
        return AsyncPlotBuilder(self, "line", query)

    def scatter(self, query: str) -> AsyncPlotBuilder:
        return AsyncPlotBuilder(self, "scatter", query)

    def bar(self, query: str) -> AsyncPlotBuilder:
        return AsyncPlotBuilder(self, "bar", query)

    def pie(self, query: str) -> AsyncPlotBuilder:
        return AsyncPlotBuilder(self, "pie", query)

    def hist(self, query: str) -> AsyncPlotBuilder:
        return AsyncPlotBuilder(self, "hist", query)

    def heatmap(self, query: str) -> AsyncPlotBuilder:
        return AsyncPlotBuilder(self, "heatmap", query)

    def boxplot(self, query: str) -> AsyncPlotBuilder:
        return AsyncPlotBuilder(self, "boxplot", query)

    def area(self, query: str) -> AsyncPlotBuilder:
        return AsyncPlotBuilder(self, "area", query)

    def radar(self, query: str) -> AsyncPlotBuilder:
        return AsyncPlotBuilder(self, "radar", query)

    def subplots(self, query: str) -> AsyncPlotBuilder:
        return AsyncPlotBuilder(self, "subplots", query)

    def custom(self, query: str) -> AsyncPlotBuilder:
        return AsyncPlotBuilder(self, "custom", query)

    def map(self, query: str) -> AsyncPlotBuilder:
        """Generate a geographic map chart (async).

        Supports choropleth maps, scatter point maps, and world maps.
        Uses cartopy for projections if installed, falls back to pure matplotlib.
        """
        builder = AsyncPlotBuilder(self, "map", query)
        builder._style = {**DEFAULT_STYLE, **DEFAULT_MAP_STYLE}
        return builder

    # ── Batch ──

    async def batch(self, requests: List[Tuple[str, str]]) -> List[ChartResult]:
        builders = []
        for ctype, query in requests:
            builders.append(AsyncPlotBuilder(self, ctype, query))
        return await asyncio.gather(*[b.render() for b in builders])

    # ── Internal: async LLM code generation ──

    async def _generate_code(self, user_prompt: str, system_prompt: str = None) -> Tuple[Optional[str], dict]:
        sp = system_prompt or SYSTEM_PROMPT
        last_error = None
        kwargs = dict(
            model=self.model,
            messages=[
                {"role": "system", "content": sp},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        if self._structured_output:
            kwargs["response_format"] = {"type": "json_object"}

        for attempt in range(self._max_retries):
            try:
                response = await self._client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content
                tokens = {
                    "input": response.usage.prompt_tokens if response.usage else 0,
                    "output": response.usage.completion_tokens if response.usage else 0,
                }
                code = _extract_code(content)
                if code:
                    return (code, tokens)
                last_error = f"Unparseable response (attempt {attempt + 1})"
                logger.warning(last_error)
            except Exception as e:
                last_error = str(e)
                logger.warning("LLM error (attempt %d/%d): %s", attempt + 1, self._max_retries, e)

            if attempt < self._max_retries - 1:
                delay = 1.0 * (2 ** attempt)
                await asyncio.sleep(delay)

        logger.error("All %d generation attempts failed: %s", self._max_retries, last_error)
        return (None, {})

    # ── Internal: async auto-fix ──

    async def _fix_code(self, code: str, error: str, query: str) -> Tuple[Optional[str], dict]:
        prompt = FIX_PROMPT.format(code=code, error=error[:1200])
        return await self._generate_code(prompt, system_prompt=FIX_SYSTEM)
