"""MCP server smoke tests (no live MCP client)."""

import importlib


def test_browser_mcp_imports():
    mod = importlib.import_module("browser_mcp")
    assert hasattr(mod, "mcp")
    assert hasattr(mod, "browser_start")
    assert hasattr(mod, "browser_close")
    assert hasattr(mod, "browser_navigate")
    assert hasattr(mod, "browser_get_state")
    assert hasattr(mod, "browser_click")
    assert hasattr(mod, "browser_type")
    assert hasattr(mod, "browser_scroll")
    assert hasattr(mod, "browser_execute_javascript")


def test_agent_mcp_imports():
    mod = importlib.import_module("browser_agent.mcp_server")
    assert hasattr(mod, "run_browser_task")


def test_agent_tools_count():
    from browser_agent.tools import get_browser_tools

    tools = get_browser_tools()
    assert len(tools) == 9
    names = {t.name for t in tools}
    assert "browser_get_state" in names
    assert "browser_close" in names
