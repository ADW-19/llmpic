"""llmpic - LLM-powered chart generation SDK.

Usage (sync):
    from llmpic import llmPIC

    sdk = llmPIC(api_key="...", base_url="https://api.openai.com/v1")
    sdk.plot("CPU usage trend over 30 days").save("cpu.png")

    # Map charts (v0.2.3+)
    sdk.map("World population by country").save("world.png")

Usage (async):
    from llmpic import AsyncllmPIC

    sdk = AsyncllmPIC(api_key="...", base_url="https://api.openai.com/v1")
    await sdk.plot("CPU trend").save("cpu.png")

    # Batch concurrent generation
    results = await sdk.batch([
        ("plot", "CPU trend"),
        ("bar", "Sales by region"),
        ("map", "World cities population"),
    ])
"""

from .core import llmPIC, AsyncllmPIC, ChartResult, PlotBuilder, AsyncPlotBuilder

__version__ = "0.3.0"
__all__ = ["llmPIC", "AsyncllmPIC", "ChartResult", "PlotBuilder", "AsyncPlotBuilder"]
