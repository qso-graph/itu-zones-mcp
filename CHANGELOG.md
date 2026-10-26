# Changelog

All notable changes to `itu-zones-mcp` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] — 2026-10-26

### Changed

- `--transport streamable-http` now says where it bound, and the help text says
  it too. It binds `127.0.0.1`, and FastMCP takes no host option, so it was
  never reachable from another machine or from outside a container — and nothing
  said so. The bind address is unchanged: loopback-only is deliberate for a
  server that holds credentials and has no authentication of its own.

## [0.2.1] — 2026-10-26

- A release should appear on the Releases page
- Move every Node 20 action to its first Node 24 major
- The locked-dependency audit blocked every release
- Four upgrades arrived as 57 pull requests
- Nothing was auditing the lockfile
- Close every open security advisory in the lockfile
- A release is a workflow, not a merge

## [0.2.0] — 2026-10-22

**Upgrading:** a tool that rejects your input now returns `isError: true` instead of a successful
result whose payload carried an `error` key. Anything reading `result["error"]` should read the
error flag instead. The IARU credit is no longer attached to a rejection — it is still on every
answer that carries data, including a "not found", which is where attribution belongs.

### MCP specification 2026-07-28 (#16)

- **Tool errors are flagged `isError`.** `_err` built `{"error": msg, "source": _credit()}` and six
  call sites returned it, so on the wire a refusal arrived as a *successful* result and a client
  could not tell "the tool answered" from "the tool rejected your input". It now raises `ToolError`,
  typed `NoReturn` so the checker understands control flow ends there and the six call sites drop
  their `return`. The specification says of `CallToolResult.isError` that otherwise "the LLM would
  not be able to see that an error occurred and self-correct".
  The issue reports "2 occurrences"; measured, it is one payload construction reached from six call
  sites, which is the same defect counted differently.
- **All six tools declare the four annotation hints.** Omitting them advertises a tool as
  `destructiveHint: true`, `idempotentHint: false`, `openWorldHint: true` — so a client is entitled
  to put a human in the loop before it reads a zone number out of a table.
- **One shared annotation block, and the premise is asserted rather than assumed.** Every tool here
  answers from the ITU-zone data carried in the wheel, so the four hints and the *reason* for them
  are the same for all six. That is also exactly what a careless copy produces, so
  `TestOneBlockIsCorrectHere` tests the claim underneath the hints: no module in the package opens a
  socket, nothing writes, and the data ships in the wheel. Worth doing rather than inheriting from
  the sibling repo — `ionis-mcp` needed three blocks and `n1mm-mcp` two.
- `idempotentHint: true` here is stronger than elsewhere in the fleet. A server reading a live
  service is idempotent only in the sense the specification means — the tool changes nothing — while
  its answers still move. Here the data is carried, so the same call returns the same answer until
  the package is upgraded.
- **The IARU credit survives.** `_err` carried `source: _credit()`; the raised error does not. That
  cost nothing, and it was checked before the change rather than after: every successful answer
  builds its own `source`, a "not found" included. `TestAttributionSurvives` holds both.
- **`tests/test_mcp_conformance.py`** (IT-C01 onward, 14 tests) and `test_bad_input_is_an_error`
  renamed to `test_bad_input_is_a_flagged_error`, which now asserts the flag rather than the word.
- Every new check was falsified — broken on purpose, watched fail, restored — and **one failed to
  fail.** IT-C22, which says no `{"error": ...}` payload remains in `src/`, read the source with
  comments *and string literals* stripped by `tokenize`; that stops it matching `_err`'s own
  docstring, which quotes the old shape, but a dict key is itself a string literal, so the strip
  deleted the thing the check looks for. It passed a planted `return {"error": "left behind"}`. It
  reads the parse tree now and cannot be fooled by prose or blinded by the fix for it.
  `cq-zones-mcp` shipped the `tokenize` version in 0.2.0 and is corrected in its own PR; those two
  were the only repos in the fleet using that form, checked rather than assumed.
- **The registered names are prefixed and the issue's are not.** It lists `codes_for`, `lookup`,
  `search`, `source_info`, `valid_on`; a client sees `itu_zones_codes_for` and so on.
  `TestRegistration` pins the set a client actually sees, and pins the trap that follows — the
  module attribute keeps the function name, so `server.itu_zones_lookup` raises `AttributeError`.
- **Nothing moved on the wire but the annotations.** Every tool's name, description, `inputSchema`
  and `outputSchema` was dumped through a real `fastmcp.Client` before and after: six tools, six
  `annotations: null` → the block, and not one other byte different.

### Lint (#15, qso-graph-devel#70)

- **`E501` is adopted.** It reported **37 lines** and not one was a defect — which is the finding,
  not an argument against enforcing it. The rules that do find defects (`F`, `I`, mypy strict) went
  in first, which is why this waited.
- **The deferral note's prediction was wrong, and this repo is where it can be tested.** The note in
  this `pyproject.toml` said some lines "will not be reflowed at all", because they name ADIF's
  field `Primary_Administrative_Subdivision` exactly and the owner of a list is its authority.
  Measured: **four** lines name it, and all four reflow with the field name whole — bind the
  subscript chain to a name first and
  `subdivisions = pas["Adif"]["Enumerations"]["Primary_Administrative_Subdivision"]` is 83
  characters. **Zero exemptions were needed**; there is no `# noqa: E501` in the repo. The same
  prediction was tested on `cq-zones-mcp` and failed there too, so the exemption clause has now
  been checked in both repos it was written about.
- **Four tool descriptions change on the wire, in whitespace only.** `source_info`, `lookup`,
  `codes_for` and `valid_on` had summary lines over 95 columns, and FastMCP publishes the docstring
  as the description — so reflowing one reaches a client. Checked rather than assumed: with
  whitespace normalised all four are identical, **no words changed**, and every `inputSchema`,
  `outputSchema` and annotation block is byte-identical. Said here because the rest of this is
  formatting and a reader is entitled to assume formatting changes nothing — in `netlogger-mcp` it
  did not, where a reflowed `Args:` line changed two parameter descriptions.
- The server's `instructions` string came out **byte-identical**: it is a run of adjacent literals,
  so splitting it at word boundaries changes the source and not the value.
- Falsified: a long line planted in `src/` and another in `tests/`, both caught; `pytest -q --live`
  still 43 passed afterwards.

### Not applicable here

- **No `certifi` work and no issue for it** (qso-graph-devel#73). Nothing in the package makes an
  outbound call of any kind — the IARU handbook is referenced by URL and SHA-256 and the facts taken
  from it ship as data. Verified, and IT-C10 keeps it that way.
- **Provenance checked, unprompted.** `published/` still hashes
  `8d64ab9bcfa6211392ebe299efd8a750d3f3ee889e63090b60ccee16a61ee33e`, matching `SOURCE.json`.
  Checked because `cq-zones-mcp`'s release was blocked by exactly this: CQ's page had changed under
  a recorded hash. The IARU's has not.

## [0.1.2] — 2026-10-11

- **ruff and mypy run in CI** (qso-graph-devel#66), as a job the `ci-all-green` gate requires.
  Settings follow `adif-mcp`, the reference for every qso-graph Python repo.
- **Fixed: a dataclass field named `list` made every annotation after it wrong.** `OwnerList.list`
  shadowed the builtin inside the class body, so `records: list[dict[str, Any]]` resolved to that
  field subscripted rather than to the builtin — as did `by_code`. Nothing broke at run time,
  because `from __future__ import annotations` means the strings are never evaluated, but anything
  that resolves them saw the wrong type. The field is `list_name` now, which is what `search()`
  already called the same thing; the `"list"` key in tool output is unchanged, being the published
  field name. Found by mypy, which is the argument for having it.
- `source()` no longer returns `Any` from a function promising a dict, and `mcp.run` is given the
  literal fastmcp asks for rather than a `str` that happens to hold the right word.
- `E501` is deferred rather than adopted (qso-graph-devel#70): the lines it reports here are not
  defects, and some are long because they name a publisher's field exactly.
- **`fastmcp` is bounded: `>=4.0,<5`** (qso-graph-devel#60). It was `>=3.0` with no upper bound, and
  these servers are run with `uvx`, which resolves fresh — so a `fastmcp` 5.0 would have reached
  every user automatically, before anything here had been run against it. The floor rises to 4.0
  because that is what is actually tested: every lock in the fleet held a 4.x, and nothing in CI
  has ever exercised 3.x. A claim of 3.x support that no test backs is not support.
- `fastmcp` is locked at 4.1.0, the current release, so CI runs against what a new install gets.
- **The published contact is `maintainers@qso-graph.io`** (qso-graph-devel#69). The `authors` field
  carried a personal address, and that field is what PyPI shows on the package page. Everything in
  qso-graph is open source and open to contribution, so the contact is the project's.

## [0.1.1] — 2026-10-07

- CI: the owner's document is fetched and checked only on the release PR (develop → main), and the check is that our facts are still in it (each zone's name, prefixes and boundary wording). A changed SHA-256 is now a warning, not a failure: websites change menus and markup without changing the list.
- `load.sql` says in the database that the owner is the authority for this list: where ADIF's tables also carry a value for it, this schema is the answer (qso-graph-devel#56).

## [0.1.0] — 2026-10-06

- First release: the IARU's ITU-zone definitions, as published and credited, with the shared QG Reference tools
  (`source_info`, `lookup`, `search`, `codes_for`, `valid_on`) and `get_version_info`.
