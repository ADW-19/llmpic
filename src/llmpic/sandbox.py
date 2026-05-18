"""Safe sandbox for executing matplotlib chart code."""

import os
import sys
import platform
import traceback
import logging
import concurrent.futures
import io
import threading

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import seaborn as sns
except ImportError:
    sns = None

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════
#  Module-level lock: serializes sandbox execution
# ══════════════════════════════════════════════
# Matplotlib patches Figure.__init__ / Figure.savefig globally,
# so concurrent executions would race. This lock prevents that.

_execl_lock = threading.Lock()

# ══════════════════════════════════════════════
#  Module-level cache: font setup (run once)
# ══════════════════════════════════════════════

_font_lock = threading.Lock()
_font_configured = False
_font_name = "sans-serif"


def _ensure_font():
    """Configure matplotlib for Chinese/CJK font. Cross-platform. Cached — runs once."""
    global _font_configured, _font_name

    if _font_configured:
        return _font_name

    with _font_lock:
        if _font_configured:
            return _font_name

        system = platform.system()
        if system == 'Windows':
            candidates = ['Microsoft YaHei', 'SimHei', 'SimSun']
        elif system == 'Linux':
            candidates = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'Noto Sans CJK SC', 'Noto Sans SC']
        elif system == 'Darwin':
            candidates = ['PingFang SC', 'Heiti SC', 'STHeiti']
        else:
            candidates = []

        # Try each font
        for font in candidates:
            try:
                plt.rcParams['font.sans-serif'] = [font] + plt.rcParams.get('font.sans-serif', [])
                plt.rcParams['font.family'] = 'sans-serif'
                plt.rcParams['axes.unicode_minus'] = False
                _font_name = font
                _font_configured = True
                logger.debug("Font configured: %s", font)
                return _font_name
            except Exception:
                continue

        # Fallback: list all candidates
        plt.rcParams['font.sans-serif'] = candidates + plt.rcParams.get('font.sans-serif', [])
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.unicode_minus'] = False
        _font_name = 'sans-serif'
        _font_configured = True
        return _font_name


# ══════════════════════════════════════════════
#  Module-level: pre-built safe namespace template
# ══════════════════════════════════════════════

_SAFE_BUILTINS = {
    'True': True, 'False': False, 'None': None,
    'int': int, 'float': float, 'str': str, 'bool': bool,
    'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
    'frozenset': frozenset, 'bytes': bytes, 'bytearray': bytearray,
    'abs': abs, 'round': round, 'min': min, 'max': max, 'sum': sum,
    'len': len, 'range': range, 'enumerate': enumerate, 'zip': zip,
    'map': map, 'filter': filter, 'sorted': sorted, 'reversed': reversed,
    'isinstance': isinstance, 'issubclass': issubclass, 'type': type,
    'hasattr': hasattr, 'getattr': getattr,
    'print': print, 'repr': repr, 'format': format,
    'pow': pow, 'divmod': divmod, 'complex': complex,
    'slice': slice, 'property': property, 'staticmethod': staticmethod,
    'classmethod': classmethod, 'super': super, 'object': object,
    '__import__': __import__,
    'Exception': Exception, 'ValueError': ValueError, 'TypeError': TypeError,
    'KeyError': KeyError, 'IndexError': IndexError, 'RuntimeError': RuntimeError,
    'StopIteration': StopIteration, 'ZeroDivisionError': ZeroDivisionError,
}


def _build_namespace():
    """Build a clean execution namespace with safe builtins."""
    ns = {
        '__builtins__': _SAFE_BUILTINS,
        'mpl': matplotlib,
        'plt': _SafePlt(plt),
        'np': np,
        'Figure': Figure,
    }
    if pd is not None:
        ns['pd'] = pd
    if sns is not None:
        ns['sns'] = sns
    return ns


# ══════════════════════════════════════════════

class _SafePlt:
    """Proxy for matplotlib.pyplot that intercepts savefig/show/close."""

    def __init__(self, real_plt):
        self._real_plt = real_plt

    def savefig(self, *args, **kwargs):
        logger.debug("plt.savefig() intercepted — use .save() on the result instead")

    def show(self, *args, **kwargs):
        logger.debug("plt.show() intercepted — use .save() on the result instead")

    def close(self, *args, **kwargs):
        logger.debug("plt.close() intercepted")

    def __getattr__(self, name):
        return getattr(self._real_plt, name)


class SandboxExecutor:
    """Executes matplotlib code in a sandboxed environment and returns chart bytes.

    Optimizations:
      - Font setup cached at module level (runs once, not per-execute)
      - Safe namespace pre-allocated per execution
      - Thread-limited execution with timeout
    """

    def __init__(self, chinese_font: bool = True, timeout: int = 30,
                 dpi: int = 150, output_dir: str = "~/llmpic_charts"):
        self._use_font = chinese_font
        self._timeout = timeout
        self._dpi = dpi
        self._output_dir = output_dir

    def execute(self, code: str, style: dict = None, format: str = 'png') -> tuple:
        """Execute matplotlib code in sandbox.

        Args:
            code: Python matplotlib code to execute.
            style: Style dict (figsize, dpi, etc.).
            format: Output format — 'png', 'svg', or 'pdf'.

        Returns (image_bytes: bytes | None, error_message: str | None).
        """
        if style is None:
            style = {}

        os.makedirs(os.path.expanduser(self._output_dir), exist_ok=True)

        if self._use_font:
            _ensure_font()

        # Serialize to avoid Figure.__init__/savefig patch races
        with _execl_lock:
            try:
                return self._execute(code, style, format)
            except concurrent.futures.TimeoutError:
                return (None, f"Timeout ({self._timeout}s). Possible infinite loop or too many iterations. Use smaller data ranges or fewer loops.")
            except SyntaxError as e:
                return (None, f"SyntaxError: {e.msg} (line {e.lineno}, col {e.offset}). Fix the syntax on that line.")
            except NameError as e:
                return (None, f"NameError: {e}. Check that all variables are defined before use and column names match the data.")
            except ValueError as e:
                return (None, f"ValueError: {e}. Check array shapes, data types, and parameter values.")
            except TypeError as e:
                return (None, f"TypeError: {e}. Check argument types and function signatures.")
            except Exception as e:
                tb_lines = traceback.format_exc().strip().split('\n')
                # Keep last 6 lines of traceback (error + context, skip deep internals)
                tb_short = '\n'.join(tb_lines[-8:]) if len(tb_lines) > 8 else '\n'.join(tb_lines)
                return (None, f"{type(e).__name__}: {e}\n\n{tb_short}")

    def _execute(self, code: str, style: dict, format: str = 'png') -> tuple:
        """Core sandboxed execution in a thread-limited environment."""
        existing_fignums = set(plt.get_fignums())
        created_figures = []

        # Save originals
        _orig_fig_init = Figure.__init__
        _orig_fig_savefig = Figure.savefig

        # Track figure creation
        def _track_init(self, *args, **kwargs):
            _orig_fig_init(self, *args, **kwargs)
            created_figures.append(self)

        Figure.__init__ = _track_init
        Figure.savefig = lambda *a, **kw: None  # Block code from calling savefig

        namespace = _build_namespace()

        try:
            def _run():
                exec(code, namespace)

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_run)
                future.result(timeout=self._timeout)

            # Find the figure that was created
            fig = None
            for candidate in reversed(created_figures):
                if candidate.get_axes():
                    fig = candidate
                    break

            if fig is None:
                new_fignums = [n for n in plt.get_fignums() if n not in existing_fignums]
                if new_fignums:
                    fig = plt.figure(new_fignums[-1])
                elif plt.get_fignums():
                    fig = plt.figure(plt.get_fignums()[-1])
                else:
                    fig = plt.gcf()

            if not fig or not fig.get_axes():
                return (None,
                    "No chart content after execution. "
                    "Did the code call ax.plot/bar/scatter/... ?"
                )

            # Render using the ORIGINAL (unpatched) savefig
            buf = io.BytesIO()
            dpi = style.get('dpi', self._dpi)
            save_kw = dict(format=format, dpi=dpi,
                           bbox_inches='tight' if style.get('tight_layout', True) else None,
                           facecolor=style.get('facecolor', 'white'))
            if format == 'svg':
                save_kw.pop('dpi', None)  # SVG ignores dpi
            _orig_fig_savefig(fig, buf, **save_kw)
            buf.seek(0)
            image_bytes = buf.read()
            return (image_bytes, None)

        finally:
            Figure.savefig = _orig_fig_savefig
            Figure.__init__ = _orig_fig_init
            plt.close('all')
