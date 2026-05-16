"""Code safety checker — compiled regex + optional LLM semantic review."""

import io
import json
import tokenize
import logging

from openai import OpenAI

from .templates import SAFETY_REVIEW_PROMPT, COMPILED_FORBIDDEN

logger = logging.getLogger(__name__)


class CodeSafetyChecker:
    """Checks code safety via compiled regex patterns and optional LLM review.

    Two modes:
      - "fast": regex only, no extra API call (~0ms overhead)
      - "full": regex + LLM semantic review (~1-2s extra, safer)

    Benchmarks: fast mode cuts total latency ~50% vs full mode.
    """

    def __init__(self, client: OpenAI, model: str, level: str = "fast"):
        self._client = client
        self._model = model
        self._level = level

    # ── Public API ──

    def check(self, code: str, llm_review: bool = None) -> tuple:
        """Full safety check. Returns (is_safe: bool, reason: str).

        Args:
            code: The matplotlib Python code to check.
            llm_review: Override safety level. True=LLM review, False=regex only,
                        None=use instance default.
        """
        do_llm = llm_review if llm_review is not None else (self._level == "full")

        violations = self.regex_check(code)
        if violations:
            return (False, "Forbidden operations:\n" + "\n".join(f"  - {v}" for v in violations))

        if do_llm:
            return self.llm_review(code)

        return (True, "")

    def regex_check(self, code: str) -> list:
        """Run compiled regex safety check. Returns list of violation labels (empty = safe)."""
        violations = []
        for pattern, label in COMPILED_FORBIDDEN:
            if pattern.search(code):
                violations.append(label)
        return violations

    def llm_review(self, code: str) -> tuple:
        """LLM semantic safety review with JSON structured output.
        Returns (is_safe: bool, reason: str).
        """
        clean_code = self._strip_comments(code)
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SAFETY_REVIEW_PROMPT},
                    {"role": "user", "content": clean_code},
                ],
                max_tokens=80,
                temperature=0,
                response_format={"type": "json_object"},
            )
            result = response.choices[0].message.content.strip()
            data = json.loads(result)
            is_safe = data.get("safe", False)
            reason = data.get("reason", "") if not is_safe else ""
            return (is_safe, reason)

        except json.JSONDecodeError:
            logger.warning("LLM safety review returned non-JSON: '%s'", result[:100] if 'result' in dir() else '')
            return (False, "Safety review response unparseable")
        except Exception as e:
            logger.error("LLM safety review error: %s", e)
            return (False, f"Safety review error: {e}")

    # ── Helpers ──

    @staticmethod
    def _strip_comments(code: str) -> str:
        """Remove Python comments, preserving strings."""
        try:
            result = []
            tokens = tokenize.generate_tokens(io.StringIO(code).readline)
            for tok_type, tok_string, _, _, _ in tokens:
                if tok_type == tokenize.COMMENT:
                    continue
                result.append((tok_type, tok_string))
            return tokenize.untokenize(result)
        except tokenize.TokenizeError:
            return code
