"""Agent unit tests (no live LLM)."""

import pytest

from browser_agent.agent import _provider_key_configured, run_task


def test_provider_key_openai_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert _provider_key_configured("openai/gpt-4o") is False


def test_provider_key_openai_present(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    assert _provider_key_configured("openai/gpt-4o") is True


def test_provider_key_ollama_always_ok():
    assert _provider_key_configured("ollama/llama3") is True


@pytest.mark.asyncio
async def test_run_task_no_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result = await run_task("go to example.com", model="openai/gpt-4o")
    assert result["success"] is False
    assert result["code"] == "LLM_ERROR"
