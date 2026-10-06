"""The MCP tools, through FastMCP."""

from __future__ import annotations

import asyncio

from fastmcp import Client

from itu_zones_mcp import server

TOOLS = {"get_version_info", "itu_zones_source_info", "itu_zones_lookup", "itu_zones_search", "itu_zones_codes_for", "itu_zones_valid_on"}


def call(name: str, args: dict | None = None) -> dict:
    async def go():
        async with Client(server.mcp) as c:
            return (await c.call_tool(name, args or {})).data
    return asyncio.run(go())


def test_tool_list():
    async def go():
        async with Client(server.mcp) as c:
            return {t.name for t in await c.list_tools()}
    assert asyncio.run(go()) == TOOLS


def test_version_info():
    r = call("get_version_info")
    assert r["service_name"] == "itu-zones-mcp" and r["spec_version"]


def test_source_info_credits_the_owner():
    r = call("itu_zones_source_info")
    assert r["owner"] and r["url"].startswith("https://") and r["terms"]
    assert all(f["sha256"] for f in r["published_files"].values())


def test_every_answer_names_its_source():
    for name, args in (("itu_zones_lookup", {"code": "6"}), ("itu_zones_search", {"text": "Antarctica"}),
                       ("itu_zones_codes_for", {"dxcc": 291}), ("itu_zones_valid_on", {"code": "6", "on_date": "2026-10-06"})):
        r = call(name, args)
        assert "error" not in r, (name, r)
        assert r["source"]["owner"] and r["source"]["url"], name


def test_bad_input_is_an_error():
    assert "error" in call("itu_zones_lookup", {"code": "A B; DROP"})
    assert "error" in call("itu_zones_search", {"text": "x" * 101})
    assert "error" in call("itu_zones_codes_for", {"dxcc": 5000})
    assert "error" in call("itu_zones_codes_for", {"dxcc": 1, "subdivision": "TOOLONG"})
    assert "error" in call("itu_zones_valid_on", {"code": "6", "on_date": "06.10.2026"})


def test_unknown_code_is_not_found():
    assert call("itu_zones_lookup", {"code": "ZZZ999"})["found"] is False


def test_help_and_version_exit_without_serving(capsys, monkeypatch):
    monkeypatch.setattr("sys.argv", ["itu-zones-mcp", "--version"])
    server.main()
    assert "itu-zones-mcp" in capsys.readouterr().out
