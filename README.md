<!-- mcp-name: io.github.qso-graph/itu-zones-mcp -->
# itu-zones-mcp

[![PyPI](https://img.shields.io/pypi/v/itu-zones-mcp?label=PyPI&color=blue)](https://pypi.org/project/itu-zones-mcp/)
[![MCP Registry](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fregistry.modelcontextprotocol.io%2Fv0%2Fservers%3Fsearch%3Dio.github.qso-graph%2Fitu-zones-mcp%26version%3Dlatest&query=%24.servers%5B0%5D.server.version&label=MCP%20Registry&color=blue)](https://registry.modelcontextprotocol.io/v0/servers?search=io.github.qso-graph/itu-zones-mcp&version=latest)

MCP server for **ITU zones** as the IARU publishes them for amateur use: the 90 zones of chapter 9.8, "Definition of ITU-Zones when used by radio amateurs", of the [IARU Region 1 HF Managers Handbook](https://www.iaru-r1.org/wp-content/uploads/2019/12/IARURegion1HFManagerHandbook8.2.1.pdf) (v8.2), used by the IARU HF Championship and ITU-zone awards. Each zone's prefixes are given in ADIF's own DXCC and subdivision codes, with the IARU's own wording where it splits an area by a line.

Part of the [qso-graph](https://qso-graph.io/) project. **No network, no authentication**: the owner's list ships with the package, and every answer names its source.

## Install

```bash
uvx itu-zones-mcp            # run it; nothing to install
```

## Tools

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `itu_zones_lookup` | One zone: every prefix, subdivision and boundary the IARU lists, with the citation | code |
| `itu_zones_codes_for` | Which zones cover an ADIF DXCC entity, or one of its subdivisions | dxcc, subdivision |
| `itu_zones_search` | Find zones by prefix or wording | text, limit |
| `itu_zones_valid_on` | Whether a zone was valid on a date (ITU zones have no validity window) | code, on_date |
| `itu_zones_source_info` | Owner, edition, terms and the shipped file's checksum | — |
| `get_version_info` | Service version + the owner's edition served (fleet identity attestation) | — |

## Quick Start

No credentials needed — just install and configure your MCP client.

### Configure your MCP client

itu-zones-mcp works with any MCP-compatible client. Add the server config and restart — tools appear automatically.

#### Claude Desktop

Add to `claude_desktop_config.json` (`~/Library/Application Support/Claude/` on macOS, `%APPDATA%\Claude\` on Windows):

```json
{
  "mcpServers": {
    "itu-zones": {
      "command": "uvx",
      "args": ["itu-zones-mcp"]
    }
  }
}
```

#### Claude Code

Add to `.claude/settings.json`:

```json
{
  "mcpServers": {
    "itu-zones": {
      "command": "uvx",
      "args": ["itu-zones-mcp"]
    }
  }
}
```

#### ChatGPT Desktop

```json
{
  "mcpServers": {
    "itu-zones": {
      "command": "uvx",
      "args": ["itu-zones-mcp"]
    }
  }
}
```

#### Cursor

Add to `.cursor/mcp.json` (project-level) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "itu-zones": {
      "command": "uvx",
      "args": ["itu-zones-mcp"]
    }
  }
}
```

#### VS Code / GitHub Copilot

Add to `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "itu-zones": {
      "command": "uvx",
      "args": ["itu-zones-mcp"]
    }
  }
}
```

#### Gemini CLI

Add to `~/.gemini/settings.json` (global) or `.gemini/settings.json` (project):

```json
{
  "mcpServers": {
    "itu-zones": {
      "command": "uvx",
      "args": ["itu-zones-mcp"]
    }
  }
}
```

### Ask questions

> "Which ITU zone is Arizona in?"

> "What does ITU zone 75 cover?"

> "Which ITU zones does Antarctica span?"

## MCP Inspector

```bash
itu-zones-mcp --transport streamable-http --port 8017
```

Then open the MCP Inspector at `http://localhost:8017`.

## Development

```bash
git clone https://github.com/qso-graph/itu-zones-mcp.git
cd itu-zones-mcp
uv sync --group dev
uv run pytest
```

`scripts/build.py` checks the owner's files against their checksums and regenerates `derived/` and `load.sql`, a PostgreSQL load for QSO Graph's reference data (load QG ADIF's `adif` schema first).

## License

itu-zones-mcp's own code is GPL-3.0-or-later. See [LICENSE](LICENSE) for details.

**The zone definitions are the IARU's, not ours.** The package ships the **IARU Region 1 HF Managers Handbook** v8.2 (<https://www.iaru-r1.org/wp-content/uploads/2019/12/IARURegion1HFManagerHandbook8.2.1.pdf>) unchanged, with its SHA-256, and answers from facts copied from chapter 9.8, each citing its page and zone. The chapter's own pages are dated November 2000. Under IARU Region 1 recommendation REC/99/LH/C4.2 (Lillehammer 1999) the zone border-lines for amateur use are kept in this handbook; the list was drafted by G3HTA from the ITU's CIRAF zones and approved by all three IARU regions. It is IARU Region 1's work; our licence doesn't cover it, and we claim no rights in it. The entity → zones file (`derived/`) is ours. How the chapter was read is recorded in [docs/TRANSCRIPTION.md](docs/TRANSCRIPTION.md). See [NOTICE](NOTICE).
