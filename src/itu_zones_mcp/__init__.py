"""ITU zones as the IARU publishes them for amateur use, in ADIF's DXCC and subdivision codes."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from typing import Final

try:
    _pkg_version = version("itu-zones-mcp")
except PackageNotFoundError:  # local dev / editable installs without dist metadata
    _pkg_version = "0.0.0-dev"

__version__: Final[str] = _pkg_version

# The owner's edition this package serves (data/SOURCE.json). Reported by get_version_info.
__spec_version__: Final[str] = "iaru-r1-hfmh-8.2-ch9.8-2000-11"
