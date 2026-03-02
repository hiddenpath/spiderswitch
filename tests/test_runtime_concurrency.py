# Tests for runtime concurrency behavior
"""
测试运行时并发切换行为，验证切换互斥语义。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import pytest

from spiderswitch.runtime.base import ModelCapabilities, ModelInfo
from spiderswitch.runtime.python_runtime import PythonRuntime


@dataclass
class _DummyClient:
    """Minimal async-close client for runtime switch tests."""

    async def close(self) -> None:
        return None


@pytest.mark.asyncio
async def test_switch_model_is_serialized_under_concurrency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Concurrent switch requests should execute client creation serially."""
    runtime = PythonRuntime()
    runtime._is_initialized = True  # noqa: SLF001
    runtime._available_models = {  # noqa: SLF001
        "openai/gpt-4o": ModelInfo(
            id="openai/gpt-4o",
            provider="openai",
            capabilities=ModelCapabilities(streaming=True, tools=True),
        )
    }

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    active = 0
    max_active = 0
    state_lock = asyncio.Lock()

    async def fake_create(*_: object, **__: object) -> _DummyClient:
        nonlocal active, max_active
        async with state_lock:
            active += 1
            max_active = max(max_active, active)
        await asyncio.sleep(0.01)
        async with state_lock:
            active -= 1
        return _DummyClient()

    monkeypatch.setattr(
        "spiderswitch.runtime.python_runtime.AiClient.create",
        fake_create,
    )

    await asyncio.gather(
        runtime.switch_model("openai/gpt-4o"),
        runtime.switch_model("openai/gpt-4o"),
        runtime.switch_model("openai/gpt-4o"),
    )

    assert max_active == 1
