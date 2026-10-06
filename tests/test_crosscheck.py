"""Cross-checks: ADIF's own ITU-zone column, AD1C's country file, and (live) ARRL's DXCC list.

They are checks, never the source (planning/QSO-GRAPH-REFERENCE-DATA.md): when one of them
disagrees with The IARU's chapter, The IARU's chapter wins. Every disagreement known today is listed below with the
reason it stands; a new one fails, so a change on either side is seen and reported, never silently
picked. docs/TRANSCRIPTION.md explains each.
"""

from __future__ import annotations

import json
import re
import urllib.request
from functools import cache
from importlib.resources import files
from pathlib import Path

import pytest

from itu_zones_mcp import reference

HERE = Path(__file__).parent
COLUMN = "ITU Zone"   # ADIF 3.1.7 Primary_Administrative_Subdivision column
CTY_FIELD = 2   # cty.dat entity line: name, CQ, ITU, ...
CTY_OVERRIDE = re.compile(r"\[(\d+)\]")


def facts():
    return reference.lists()["itu_zones"].records


@cache
def zones_by_entity() -> dict[int, set[int]]:
    out: dict[int, set[int]] = {}
    for r in facts():
        for c in r["covers"]:
            if c["dxcc"] is not None:
                out.setdefault(c["dxcc"], set()).add(int(r["code"]))
    return out


def adif_disagreements() -> dict[str, tuple[list[int], list[int]]]:
    """Subdivisions the owner names explicitly whose zones ADIF lists differently."""
    ours: dict[tuple[str, int], set[int]] = {}
    for r in facts():
        for c in r["covers"]:
            if c["pas"]:
                ours.setdefault((c["pas"], c["dxcc"]), set()).add(int(r["code"]))
    spec = files("adif_mcp").joinpath("resources", "spec", "317")
    pas = json.loads(spec.joinpath("enumerations_primary_administrative_subdivision.json").read_text(encoding="utf-8"))
    out = {}
    for r in pas["Adif"]["Enumerations"]["Primary_Administrative_Subdivision"]["Records"].values():
        key = (r["Code"], int(r["DXCC Entity Code"]))
        if r.get("Deleted") == "true" or not r.get(COLUMN) or key not in ours:
            continue
        adif = {int(z) for z in re.split(r"[,/]", r[COLUMN])}
        if adif != ours[key]:
            out[f"{key[0]}.{key[1]}"] = (sorted(adif), sorted(ours[key]))
    return out


def cty_disagreements() -> dict[str, tuple[int, list[int]]]:
    """Covers whose prefix AD1C's cty.dat puts in a zone the owner doesn't give that entity."""
    prefixes: dict[str, int] = {}
    entity_zone = None
    for line in (HERE / "crosscheck" / "cty.dat").read_text(encoding="latin-1").splitlines():
        if line and not line[0].isspace():
            entity_zone = int(line.split(":")[CTY_FIELD].strip())
            continue
        for item in line.replace(";", ",").split(","):
            item = item.strip()
            if not item or item.startswith("="):
                continue
            m = CTY_OVERRIDE.search(item)
            prefixes[re.match(r"[A-Z0-9/]+", item).group()] = int(m.group(1)) if m else entity_zone
    # Only prefixes the owner uses for one entity: a shared prefix (FO, VK9, 3Y ...) names
    # different islands in different zones, and AD1C's entry for it can't tell them apart.
    owners: dict[str, set[int]] = {}
    for r in facts():
        for c in r["covers"]:
            m = re.match(r"[A-Z0-9]+", c["prefix"] or "")
            if m and c["dxcc"] is not None:
                owners.setdefault(m.group(), set()).add(c["dxcc"])
    out = {}
    for r in facts():
        for c in r["covers"]:
            m = re.match(r"[A-Z0-9]+", c["prefix"] or "")
            if not m or c["dxcc"] is None or m.group() not in prefixes or len(owners[m.group()]) > 1:
                continue
            z = prefixes[m.group()]
            if z not in zones_by_entity()[c["dxcc"]]:
                out[f"{m.group()}.{c['dxcc']}"] = (z, sorted(zones_by_entity()[c["dxcc"]]))
    return out


# Known today; each explained in docs/TRANSCRIPTION.md. The IARU's chapter wins.
KNOWN_ADIF = {
    # MN: ADIF gives 07/08; the chapter lists Minnesota in zone 7 only.
    "MN.291": ([7, 8], [7]),
}
KNOWN_CTY = {
    # TI9 Cocos I.: AD1C gives 11; the chapter (and ARRL) give 12.
    "TI9.37": (11, [12]),
    # Asiatic Russia: AD1C carries one default zone per prefix; the chapter splits UA0, UA8T and
    # "Uaà" (its typo for UA0) by lines of latitude and longitude.
    "UA0.15": (30, [21, 22, 23, 24, 25, 26, 31, 32, 33, 34, 35, 75]),
    "U.15": (29, [21, 22, 23, 24, 25, 26, 31, 32, 33, 34, 35, 75]),
    "UA8T.15": (30, [21, 22, 23, 24, 25, 26, 31, 32, 33, 34, 35, 75]),
}


def test_adif_subdivision_zones():
    assert adif_disagreements() == KNOWN_ADIF


def test_ad1c_country_file():
    assert cty_disagreements() == KNOWN_CTY


@pytest.mark.live
def test_arrl_dxcc_list():
    """ARRL's current DXCC list gives each entity's zones; every zone it gives should be one the
    owner gives that entity. Fetched live (ARRL's file is not shipped)."""
    url = "https://www.arrl.org/files/file/DXCC/2020%20Current_Deleted.txt"
    with urllib.request.urlopen(url, timeout=30) as resp:  # https, ARRL
        text = resp.read().decode("latin-1")
    row = re.compile(r"^\s+\S+\s+.+?\s{2,}(AF|AN|AS|EU|NA|OC|SA)[, A-Z]*\s+(\S+)\s+(\S+)\s+(\d{3})\s*$")
    out = {}
    for line in text.split("DELETED ENTITIES")[0].splitlines():
        m = row.match(line)
        if not m:
            continue
        field = m.group(2)
        if not re.fullmatch(r"\d\d(?:[-,]\d\d)*", field):
            continue  # lettered notes ((A)-(I)) aren't in the text file
        zs: set[int] = set()
        for part in field.split(","):
            a, _, b = part.partition("-")
            zs |= set(range(int(a), int(b or a) + 1))
        code = int(m.group(4))
        if code in zones_by_entity() and not zs <= zones_by_entity()[code]:
            out[code] = sorted(zs - zones_by_entity()[code])
    assert out == KNOWN_ARRL


KNOWN_ARRL: dict = {
    # Guatemala: ARRL gives ITU zone 12; the chapter lists TG in zone 11.
    76: [12],
}
