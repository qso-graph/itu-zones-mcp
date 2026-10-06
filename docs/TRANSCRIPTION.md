# Transcribing the IARU's ITU-zone definitions

`src/itu_zones_mcp/data/facts/itu_zones.json` holds the facts of chapter 9.8, "Definition of ITU-Zones
when used by radio amateurs", of the **IARU Region 1 HF Managers Handbook** v8.2
(<https://www.iaru-r1.org/wp-content/uploads/2019/12/IARURegion1HFManagerHandbook8.2.1.pdf>). The
handbook is shipped unchanged in `data/published/`. The chapter is a table of zones and prefixes in
prose, so its facts were copied in by hand once and reviewed against renders of the PDF pages (9.8-1 to
9.8-4, PDF pages 95–98). This file records how it was read.

**90 zones, 458 covers.** Zones 76, 77 and 79–89 have no entry in this edition (name null, no covers).

## Edition

The chapter's own page footers read **"HF Managers Handbook V8.2 … November 2000"**. "January 2009"
appears only in the footer of the page before (9.7-4, "V8.1 January 2009"), so this package gives the
chapter's edition as **2000-11**, as printed in the v8.2 handbook (2016).

## How a zone's entry becomes covers

- One cover per prefix or area, in the chapter's order. `prefix` as printed, `dxcc` and `pas` ADIF's
  codes, `boundary` the chapter's own wording for a partial area.
- `pas` is set only for the US states the chapter names ("W7 (ID, NV, OR, WA)" is four covers). VE, VK
  and UA prefixes have `pas` null: the chapter names no province or oblast.
- A boundary printed at the end of a list applies to every item of it ("W7 (AZ, MT, UT, west of
  110W)").
- A parenthesis that names a whole entity gets its dxcc and no boundary ("HK0 (San Andres)"); one that
  also carries a limit keeps the limit as boundary ("R1F (FJL south of 80N)" → 61, "south of 80N").
- Antarctica: prefix null (the chapter gives none), dxcc 13.

## Judgement calls

1. **Zone 2:** "(south of 80N and west of 110W)" is printed after VY1 only, but applies to VE6, VE7, VE8
   and VY1 (VE8 is also in zones 3, 4, 9 and 75).
2. **Zone 9:** "(south of 80N and east of 70W but excluding Baffin Island)", printed after VE8, applies
   to VE1, VE2 and VE8.
3. **Zone 47, "1J":** not a prefix. Read as TJ (Cameroon, 406), which is otherwise absent; ARRL and
   cty.dat both put Cameroon in zone 47. The prefix is kept as "1J".
4. **Zone 11, "FJ/FS":** one cover, 213 (Saint Martin), the entity of that era.
5. **Entities ADIF lists as deleted**, used because the chapter means them: "PJ (Netherlands Antilles)"
   85, "PJ (Sint Maarten)" 255, "R1M (MV Island)" 151, "KH5 (Kingman Reef)" 134, "ST0" 244.
6. **KH5 (Palmyra but not Jarvis) / KH5 (Jarvis)** and **T32 (Northern Line Islands only) / T32
   (Central & Southern Line Islands)** are boundaries within one entity (197, 48): the chapter splits
   each across two zones.
7. **Zone 78, "CE0 (Sala y Gomez)":** not an entity; dxcc 47 (Easter I.) with boundary "Sala y Gomez".
8. **UA9 in zone 20 and zone 30** cover parts of both European (54) and Asiatic (15) Russia, so their
   dxcc is null. Zone 19's UA9 west of 50E is 54. Otherwise UA1/3/4/6 → 54, UA2 → 126, UA0, UA9/0, UA8T
   and UA8V → 15.
9. **YU** → 296; **IG9** and **IH9** → 248 (Italy), two covers.

## Slips in the chapter, kept as published

Zone 7 "Wà" (W0); Zone 26 "Uaà" (UA0); Zone 21 "betwwen"; Zone 23 "60and"; Zone 8 "W5 (AR LA, MS" and
"90W) ,"; Zone 11 "VP2 (Br. Virgin Is.) VP2" and "YV0,ZF"; Zone 12 "PY (west of 60W) PZ"; Zone 30 "EZ
(Turkmenistan, UA4" and the spellings "Kyrgyztan", "Tajikstan"; Zone 31 "Kyrgyzstaneast"; Zone 74
"South Pole))" (the stray ")" is left out of the boundary); "Trinidade", "Andemans", "North Cook" /
"North Cooks". Superscript E (50E, 90E, 130E, 40E) is written as a plain E; the decimal comma in
"16,5S" is kept.

Gaps in the chapter: overlapping CP boundaries (zones 12, 13, 14); JT, 7O, ST and ST0 in two zones with
no boundary; G (England), GW (Wales), DC and Fiji proper (3D2, 176) absent; entities created later
absent.

## Cross-checks (the chapter wins)

Tested in `tests/test_crosscheck.py`; a new disagreement fails the tests.

- **ADIF 3.1.7's subdivision zones:** ADIF gives Minnesota (MN) 07,08; the chapter lists MN in zone 7
  only. ADIF gives DC zone 08; the chapter doesn't list DC.
- **ARRL's DXCC list** gives fewer zones than the chapter for Guatemala (12 vs 11), Bolivia, Easter I.,
  Franz Josef Land, Svalbard, Micronesia, the Cooks, Italy and Yemen.
- **AD1C's cty.dat:** Cocos I. (TI9) 11 against the chapter's 12 (ARRL agrees with the chapter); a single
  default zone per entity otherwise.
