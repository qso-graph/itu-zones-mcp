"""Conformance with the Model Context Protocol, revision 2026-07-28.

We documented how to *publish* an MCP server in detail and never wrote down what makes
one *valid*, which is how missing ``isError`` and missing annotations reached every
server in the fleet.

This is cq-zones-mcp's sibling and the shape of the work is the same, so the premises
are asserted here rather than assumed from the family resemblance:

* **All six tools share one annotation block.** Honest here — every one answers from the
  ITU-zone data bundled in the wheel, nothing opens a socket, nothing writes. But one
  shared block is also exactly what a careless copy produces, so
  ``TestOneBlockIsCorrectHere`` tests the claim underneath the hints rather than the
  hints alone.

* **The registered names are prefixed and the issue's are not.** Issue #16 lists
  ``codes_for``, ``lookup``, ``search``, ``source_info``, ``valid_on`` — the *function*
  names. A client sees ``itu_zones_codes_for`` and so on, because the decorators pass
  ``name=f"{P}_..."``. The module attribute keeps the function name, which is a trap
  worth pinning: probing ``server.itu_zones_lookup`` raises ``AttributeError``.

* **The IARU credit is gone from failures and that cost nothing.** ``_err`` returned
  ``{"error": msg, "source": _credit()}``. Every successful answer builds its own
  ``source`` — checked before the change — so attribution still rides on every piece of
  data returned, including a "not found" answer.

The owner here is the IARU, from the ITU's CIRAF zones, and the document is a **PDF**
referenced by URL and SHA-256 rather than shipped. Checked 2026-10-21: the published
file still hashes ``8d64ab9b…``, matching ``SOURCE.json`` — unlike cq-zones-mcp, whose
page had drifted and blocked its release.

Test IDs: IT-C01 onward.
"""

from __future__ import annotations

import asyncio

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from itu_zones_mcp import server

ANNOTATION_HINTS = ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")

TOOLS = {
    "get_version_info", "itu_zones_source_info", "itu_zones_lookup", "itu_zones_search",
    "itu_zones_codes_for", "itu_zones_valid_on",
}


def _tools() -> dict[str, object]:
    return {t.name: t for t in asyncio.run(server.mcp.list_tools())}


def _wire(tool: object) -> dict[str, object]:
    annotations = getattr(tool, "annotations", None)
    assert annotations is not None, "tool declares no annotations"
    return annotations.model_dump(by_alias=True, exclude_none=True)


def call(name: str, args: dict | None = None):
    async def go():
        async with Client(server.mcp) as c:
            return (await c.call_tool(name, args or {})).data
    return asyncio.run(go())


def fails(name: str, args: dict | None = None) -> str:
    with pytest.raises(ToolError) as caught:
        call(name, args)
    return str(caught.value)


class TestToolAnnotations:
    def test_every_tool_declares_all_four_hints(self) -> None:
        """IT-C01: the defaults are pessimistic, so silence is the wrong answer."""
        for name, tool in _tools().items():
            wire = _wire(tool)
            for hint in ANNOTATION_HINTS:
                assert hint in wire, f"{name} omits {hint}; got {sorted(wire)}"

    def test_all_six_are_read_only_closed_world_and_idempotent(self) -> None:
        """IT-C02: one answer for all six, because one reason covers all six."""
        for name, tool in _tools().items():
            wire = _wire(tool)
            assert wire["readOnlyHint"] is True, name
            assert wire["destructiveHint"] is False, name
            assert wire["idempotentHint"] is True, name
            assert wire["openWorldHint"] is False, name


class TestOneBlockIsCorrectHere:
    """Sharing one block is only honest while the premise holds, so assert the premise."""

    def test_no_module_in_the_package_opens_a_socket(self) -> None:
        """IT-C10: `openWorldHint: false` on all six depends on this.

        The IARU handbook is referenced by URL and SHA-256 in SOURCE.json, not fetched
        at runtime — the facts taken from it ship as data. If anything here started
        fetching, every one of these hints would become a lie at once.
        """
        import pathlib

        src = pathlib.Path(server.__file__).parent
        offenders = [
            f"{py.name}:{i}: {line.strip()}"
            for py in src.rglob("*.py")
            for i, line in enumerate(py.read_text().splitlines(), 1)
            if any(t in line for t in ("urlopen", "http.client", "socket.",
                                       "requests.", "httpx."))
        ]
        assert not offenders, (
            "something here reaches the network, so openWorldHint: false is wrong:\n"
            + "\n".join(offenders)
        )

    def test_nothing_in_the_package_writes(self) -> None:
        """IT-C11: `readOnlyHint: true` on all six depends on this."""
        import pathlib

        src = pathlib.Path(server.__file__).parent
        offenders = [
            f"{py.name}:{i}: {line.strip()}"
            for py in src.rglob("*.py")
            for i, line in enumerate(py.read_text().splitlines(), 1)
            if any(t in line for t in ("write_text(", ".write(", "mkdir("))
        ]
        assert not offenders, (
            "something here writes, so readOnlyHint: true is wrong:\n"
            + "\n".join(offenders)
        )

    def test_the_data_ships_in_the_wheel(self) -> None:
        """IT-C12: why the answers are stable, not merely side-effect free."""
        from itu_zones_mcp import reference

        assert reference.DATA.joinpath("SOURCE.json").is_file()


class TestBadInputIsFlagged:
    def test_every_validation_path_raises(self) -> None:
        """IT-C20: all six `_err` call sites, not a sample of them."""
        for name, args in (
            ("itu_zones_lookup", {"code": "A B; DROP"}),
            ("itu_zones_search", {"text": "x" * 101}),
            ("itu_zones_codes_for", {"dxcc": 5000}),
            ("itu_zones_codes_for", {"dxcc": 1, "subdivision": "TOOLONG"}),
            ("itu_zones_valid_on", {"code": "A B; DROP", "on_date": "2026-10-06"}),
            ("itu_zones_valid_on", {"code": "6", "on_date": "06.10.2026"}),
        ):
            fails(name, args)

    def test_the_message_says_what_was_wrong(self) -> None:
        """IT-C21: a flagged error the caller cannot act on is only half the fix."""
        assert "1 to 100" in fails("itu_zones_search", {"text": "x" * 101})
        assert "YYYY-MM-DD" in fails(
            "itu_zones_valid_on", {"code": "6", "on_date": "06.10.2026"})

    def test_no_error_payload_remains_in_the_source(self) -> None:
        """IT-C22: the conversion is complete, not partial.

        Reads the *parse tree* and looks for a dict literal with an ``"error"`` key,
        because the two text-based forms of this check both fail in their own way and
        both were tried here first:

        * a raw-line search matches ``_err``'s own docstring, which *quotes* the old
          ``{"error": msg, ...}`` shape to explain why it is gone — a text search cannot
          tell a sentence about a thing from the thing;
        * stripping comments **and string literals** with ``tokenize`` fixes that by
          deleting the payload key as well, since the key is itself a string literal.
          The check then cannot fail at all. It passed a planted
          ``return {"error": "left behind"}`` in the falsification run, which is how
          this was caught — cq-zones-mcp shipped that version and is being corrected.

        The limit of the tree form: a key assembled at runtime (``{"erro" + "r": ...}``)
        is not a constant and is not seen. Nobody writes that by accident; it is what
        the IT-C20 falsification used deliberately, to break ``_err`` without also
        tripping this check.
        """
        import ast
        import pathlib

        src = pathlib.Path(server.__file__).parent
        offenders = [
            f"{py.name}:{node.lineno}"
            for py in src.rglob("*.py")
            for node in ast.walk(ast.parse(py.read_text()))
            if isinstance(node, ast.Dict)
            and any(isinstance(k, ast.Constant) and k.value == "error" for k in node.keys)
        ]
        assert not offenders, f"error payloads remain at: {offenders}"


class TestAttributionSurvives:
    """The IARU credit was in the error payload; dropping it must not lose it."""

    def test_every_data_answer_carries_the_credit(self) -> None:
        """IT-C30: checked per tool, not assumed from one."""
        for name, args in (
            ("itu_zones_lookup", {"code": "6"}),
            ("itu_zones_search", {"text": "eu"}),
            ("itu_zones_codes_for", {"dxcc": 291}),
            ("itu_zones_valid_on", {"code": "6", "on_date": "2026-10-06"}),
        ):
            answer = call(name, args)
            assert "source" in answer, f"{name} returns data with no attribution"
            assert answer["source"].get("owner"), f"{name} credit has no owner"

    def test_an_unknown_code_still_carries_the_credit(self) -> None:
        """IT-C31: "not found" is an answer, so it is attributed too."""
        answer = call("itu_zones_lookup", {"code": "ZZZ999"})
        assert answer["found"] is False
        assert answer["source"].get("owner")


class TestAnEmptyAnswerIsNotAnError:
    def test_unknown_code_is_a_successful_call(self) -> None:
        """IT-C40: the distinction the specification draws."""
        answer = call("itu_zones_lookup", {"code": "ZZZ999"})
        assert isinstance(answer, dict)
        assert answer["found"] is False


class TestVersionInfoShape:
    def test_it_matches_the_shape_the_fleet_returns(self) -> None:
        """IT-C50: the convention that drifted because nobody asserted it."""
        info = call("get_version_info")
        assert info["service_name"] == "itu-zones-mcp"
        assert info["service_version"]
        assert info["spec_version"]


class TestRegistration:
    def test_the_names_a_client_sees_are_prefixed(self) -> None:
        """IT-C60: issue #16 lists the function names, not these."""
        assert set(_tools()) == TOOLS

    def test_the_module_attribute_is_not_the_registered_name(self) -> None:
        """IT-C61: the trap that follows from prefixing, pinned.

        The decorator registers `itu_zones_lookup` while the module attribute stays
        `lookup`. Probing `server.itu_zones_lookup` raises AttributeError — which it
        did to me, verifying the published wheel of the sibling repo. A caller uses the
        registered name; only test code reaches for the attribute.
        """
        assert not hasattr(server, "itu_zones_lookup")
        assert hasattr(server, "lookup")
