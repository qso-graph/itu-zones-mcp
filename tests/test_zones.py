"""The IARU's 90 ITU zones, and answers to the questions the zones exist for."""

from __future__ import annotations

from itu_zones_mcp import reference

BLANK = {76, 77} | set(range(79, 90))


def test_all_90_zones_present_blank_ones_empty():
    recs = reference.lists()["itu_zones"].records
    assert [r["code"] for r in recs] == [str(z) for z in range(1, 91)]
    for r in recs:
        assert bool(r["covers"]) == (int(r["code"]) not in BLANK), r["code"]
    assert reference.lookup("90")[0]["covers"][0]["prefix"] == "JD1"


def test_w7_states_split_at_110w():
    hits = {h["code"]: h for h in reference.codes_for(291, "AZ")}
    assert set(hits) == {"6", "7"}
    assert hits["6"]["covers"][0]["boundary"] == "west of 110W"
    assert hits["7"]["covers"][0]["boundary"] == "east of 110W"


def test_edition_is_the_chapters_own_footer():
    assert reference.source()["edition"].startswith("2000-11")
