"""Pre-release: our facts are still in the IARU's chapter 9.8 (run with --live; CI runs it on the
release PR).

Not a byte comparison: every prefix and boundary wording in our facts must still be in the
chapter's text. Whitespace is ignored (the PDF's text layer spaces superscripts, e.g. "50 E").
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

import pytest
from pypdf import PdfReader

from itu_zones_mcp import reference

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import fetch_published  # noqa: E402

DOC = "IARURegion1HFManagerHandbook8.2.1.pdf"
logging.getLogger("pypdf").setLevel(logging.ERROR)  # font-encoding notices, not about the text


def squash(text: str) -> str:
    return re.sub(r"\s+", "", text)


def chapter_text() -> str:
    path = fetch_published.fetch(DOC, reference.source()["published"][DOC])
    with path.open("rb") as fh:
        pages = [p.extract_text() or "" for p in PdfReader(fh).pages]
    chapter = [t for t in pages if "Chapter 9.8" in t]
    assert len(chapter) >= 4, "chapter 9.8 not found where expected"
    return squash(" ".join(chapter))


@pytest.mark.live
def test_every_fact_is_still_in_the_chapter():
    text = chapter_text()
    missing = []
    for r in reference.lists()["itu_zones"].records:
        for c in r["covers"]:
            for value in (c["prefix"], c["boundary"]):
                if value and squash(value) not in text:
                    missing.append((r["code"], value))
    assert not missing, missing[:20]
