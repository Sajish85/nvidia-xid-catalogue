"""Step 5: generate QA.md, SOURCES.md, DATA-DICTIONARY.md, CLASSIFICATION.md from data. Run from project root.
The article is hand-edited and is not written by this script."""
import json, collections, csv
import sys; sys.path.insert(0,"scripts"); import build
SEVC=build.SEV_COL; PARA=build.LABEL_REWRITE
R=json.load(open("xid-catalogue.json"))["records"]; Q=json.load(open("qa-results.json"))
N=len(R); C=Q["counts"]; SHA="e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9"
cnt=lambda k:collections.Counter(r[k] for r in R)
sev,rec,sub,sta=cnt(SEVC),cnt("recovery_action"),cnt("subsystem"),cnt("status")
docs_only=Q["docs_only"]; hdr_only=Q["header_only"]; d_not_a=Q["docs_not_archive"]
def rng(l):
    out=[];s=p=None
    for x in l:
        if s is None: s=p=x
        elif x==p+1: p=x
        else: out.append((s,p)); s=p=x
    if s is not None: out.append((s,p))
    return ", ".join(str(a) if a==b else f"{a}-{b}" for a,b in out)
fmt=lambda d:"\n".join(f"| {k} | {v} |" for k,v in d.most_common())
retr="2026-11-18"; retr_t=Q["refetch_utc"]
spot=Q["spot_log"]
# ------------------------------------------------------------------ QA.md
qa=f"""# QA — xid-catalogue v1 (built {retr})

## Summary
- Rows: **{N}** in CSV, **{len(R)}** in JSON; CSV == JSON content check: **{Q['csv_json_equal']}**. Codes 1-{max(r['code'] for r in R)}, no duplicates (duplicate count {Q['dupe_codes']}).
- SXID rows: **0** (no SXID codes appear in the three listed sources; SXID is out of scope for this release).
- Spot-check: **{Q['spot_total']}** codes re-verified against a fresh live fetch, **{Q['spot_fail']}** failures.
- Rows with an empty classification cell: **{len(Q['empty_class_cells'])}**. Rows with no source pointer: **{len(Q['no_pointer'])}**. `meaning` fields over 25 words: **{len(Q['meaning_over_25_words'])}**.

## 1. Counts per source (codes, not rows of source tables)
| Source | Codes found | Notes |
|---|---|---|
| S1 docs catalogue, Table 1 (analyzing-xid-catalog.html, Ampere and newer) | {C['docs']} | Codes 1-172, all type XID; HTML table and downloadable Xid-Catalog.xlsx agree on the code set ({Q['xlsx_xid_rows']} XID rows in the xlsx, code sets equal: {Q['xlsx_codes_equal_html']}) |
| S1b docs archive page (r555, older GPUs) failure-cause table | {C['archive']} | Codes 1-143. Includes 13 codes taken from two range rows ("126-136", "138-139", both labelled Reserved) |
| S2 header nverror.h (commit {SHA[:12]}) | {C['header']} | {Q['hdr_excluded'] and 'Excluded from count: '+', '.join(e[1] for e in Q['hdr_excluded'])}. Two alias macros (INFOROM_DRAM_RETIREMENT_EVENT/FAILURE) map to codes 63/64 and are stored in `header_aliases`, not as extra rows |
| S3 debug guidelines, gpu-node-triage.html Table 1 | {C['debug']} | Codes {rng(sorted(c for c in [r['code'] for r in R if r['in_debug_guidelines']=='yes']))}. Other debug pages (overview, initial-incident-report, best-practices) hold no code tables |
| **Union (dataset rows)** | **{Q['union']}** | |

## 2. Overlap and dedup
- One row per integer code. Primary key is the code number; sources are joined on it.
- Codes in both docs catalogue and header: {Q['both_docs_header']}.
- Source-count distribution (how many of the four sources list a code): {', '.join(f'{k} source(s): {v} codes' for k,v in sorted(Q['source_count_dist'].items()))}.
- Header alias macros: {', '.join(f'{a} = {b[0][1]} (line {b[0][0]})' for a,b in Q['hdr_alias'].items())}.
- Header lines excluded as non-codes: {'; '.join(f'line {e[0]} {e[1]} ({e[3]})' for e in Q['hdr_excluded'])}.
- Name conflicts between docs mnemonic and header macro for the same code ({len(Q['name_conflicts'])}): {'; '.join(f'{c}: {d} vs {h}' for c,d,h in Q['name_conflicts'])}. Both names are kept (`name_docs`, `name_header`); `name` uses the docs mnemonic when present.
- Docs-catalogue Xid 13 lists two mnemonics (GR_EXCEPTION / GR_ERROR_SW_NOTIFY); both are kept in `name_docs`, joined with " / ". The xlsx and the HTML table give the same two mnemonics for code 13 (xlsx mnemonic mismatches after whitespace normalisation: {len(Q['xlsx_mnemonic_mismatch'])}); xlsx immediate-action bucket mismatches: {len(Q['xlsx_imm_bucket_mismatch'])}.

## 3. Codes present in one source but not another
**In header, not in docs catalogue ({len(hdr_only)}):** {rng(hdr_only)}. The docs catalogue stops at code 172; header runs to 186.
**In docs catalogue, not in header ({len(docs_only)}):** {rng(docs_only)}.
**In docs catalogue, not in the r555 archive listing ({len(d_not_a)}):** {rng(d_not_a)}.
**In archive listing, not in docs catalogue:** {len(Q['archive_not_docs'])} codes.
**In debug guidelines, not in docs catalogue:** {len(Q['debug_not_docs'])} codes.
**Docs says Unused, archive gives a failure label ({len(Q['docs_unused_but_archive_has_label'])} codes):** {rng(Q['docs_unused_but_archive_has_label'])}. The sources do not say why they differ (the archive page is the r555 document for older GPUs); both labels are kept.
**Docs description and archive label worded differently ({len(Q['docs_desc_vs_archive_differ'])} codes):** {rng(Q['docs_desc_vs_archive_differ'])} (for example archive "Reserved" or "Unused" against a docs engine label for 39-41 and 126-135, or reworded labels such as 94 "Contained ECC error" against "Contained memory error"). Not resolved; both kept.
**Debug guidelines give an action for codes the docs catalogue marks Unused:** 61, 123. They carry the status "unused in catalogue; action in debug guidelines" and a note.
**Docs description and trigger text say Unused but the product flags say applicable:** 108. Coded unused, with a note stating the conflict. Code 14 has the same flag pattern but real trigger text, so it stays active.
**Row-level notes ({len(Q['notes_rows'])}):** {'; '.join(f'{c}: {n}' for c,n in Q['notes_rows'])}.

## 4. Classification distributions
**status**

| value | rows |
|---|---|
{fmt(sta)}

**subsystem**

| value | rows |
|---|---|
{fmt(sub)}

**{SEVC}**

| value | rows |
|---|---|
{fmt(sev)}

**recovery_action**

| value | rows |
|---|---|
{fmt(rec)}

## 5. Spot-check log ({Q['spot_total']} codes)
Method: all four source pages were fetched again on {retr_t} (UTC) into `qa-live/`. Each of the four fresh files was byte-identical to the file used for extraction (identical flags: docs {Q['identical_to_raw_docs']}, archive {Q['identical_to_raw_arch']}, header {Q['identical_to_raw_hdr']}, debug {Q['identical_to_raw_dbg']}). Codes were then re-read from the fresh files with a second, independent parser (regular expressions on the raw HTML or header text; the extraction used an HTML table parser) and compared with the dataset row: mnemonic, description, applies-to flags, immediate and investigatory bucket, header name and line, archive label, debug row presence. Sample = 15 hand-picked codes (important or unusual) + 10 drawn with seed 20261118. A same-day re-fetch cannot detect later page changes; it checks extraction and transcription.

| Code | Result | What was compared |
|---|---|---|
""" + "\n".join(f"| {c} | {'PASS' if ok else 'FAIL'} | {t} |" for c,ok,t in spot) + f"""

Paraphrased labels: for codes {', '.join(map(str,sorted(PARA)))} the dataset label is deliberately not the source label (source label over {build.LABEL_MAX_WORDS} words); the spot-check confirms the source label is long and the dataset holds the own-words label. Longest source label kept verbatim: {Q['label_words_max']} words.

Manual read (by eye, from `qa-live/`, on the first build, before the later revisions to labels, meanings, subsystem values and status values): codes 123, 152, 163, 186 were also read directly in the live header and docs table text and compared with the dataset row (name, applies-to flags, buckets, status, classification); no differences.

## 6. Acceptance-bar checks
| Check | Result |
|---|---|
| CSV rows == JSON rows | {Q['csv_rows']} == {Q['json_rows']} |
| Row count stated in paper.md | {N} (number tokens checked by scripts/check_article.py paper.md) |
| Longest source label kept verbatim | {Q['label_words_max']} words (limit {build.LABEL_MAX_WORDS}) |
| Every row has a source pointer | {len(Q['no_pointer'])} rows without |
| Empty classification cells | {len(Q['empty_class_cells'])} |
| `meaning` >25 words | {len(Q['meaning_over_25_words'])} |
| `debug_guideline_action` >25 words | {len(Q['debug_summary_over_25_words'])} |
| `recovery_detail` >25 words | {len(Q['recov_detail_over_25_words'])} |

## 7. Known QA limits
- The classification rules are applied by script; the rule outputs were reviewed by reading the full 186-row table, but no second reviewer has checked the rule design.
- Spot-check compares the dataset to the sources, not the classification to ground truth: no ground truth exists beyond the sources.
- The meaning field for rows with no explanatory text is a restated label, not an independent description.
"""
open("QA.md","w").write(qa)

# ------------------------------------------------------------------ shared facts
cols=list(R[0].keys()); NC=len(cols)
def ex(field,val,n=6): return ", ".join(str(r["code"]) for r in R if r[field]==val)[:200] if sum(1 for r in R if r[field]==val)<=n else ", ".join(str(r["code"]) for r in [x for x in R if x[field]==val][:n])+", ..."
meaning_codes=sorted(build.MEANING)
# ------------------------------------------------------------------ DATA-DICTIONARY.md
D={
"code":("integer","The Xid number as printed in kernel logs (NVRM: Xid ...). Primary key; unique per row.","S1/S1b/S2/S3 (the number itself)"),
"code_type":("string","Always XID in v1. SXID reserved for a later version (no SXID codes in the listed sources).","fixed"),
"name":("string","Preferred name: the first docs-catalogue mnemonic when the docs list the code, otherwise the header macro.","S1, else S2"),
"name_docs":("string","Mnemonic(s) from docs catalogue Table 1 column 'Mnemonic'. Two mnemonics are joined with ' / ' (Xid 13). Empty if the docs do not list the code.","S1"),
"name_header":("string","Macro name from nverror.h that has this code as value. Empty if the header has no macro for the code.","S2"),
"header_aliases":("string","Other header macros defined as aliases of name_header (63 and 64 only). Semicolon separated.","S2"),
"name_conflict":("string","Non-empty when docs mnemonic and header macro differ in more than spelling or a listed alias. Text: 'docs mnemonic and header macro differ'.","computed"),
"status":("enum","unused = docs description is 'Unused' and all four applies-to flags are NO, or header macro name says UNUSED, or code 108 (description and trigger text say Unused, flags say applicable; see notes); 'unused in catalogue; action in debug guidelines' = codes 61 and 123 (docs say unused, debug guidelines give a reset action); reserved = header macro name says RESERVED and the docs do not list the code; active = anything else documented; 'active (header only)' = active by header name, no further documentation.","computed from S1, S2"),
"meaning":("string, <=25 words","Short factual summary in the cataloguer's words. For rows with explanatory text in the docs it summarises that text; for the rest it restates the short label ('Catalogue label: ...') or says that nothing is described. See SOURCES.md for the fields where this was hard to keep apart from the source wording.","S1, S1b, S2 (summarised)"),
"docs_description":("string","Docs Table 1 column 'Description': the source's short label, verbatim when it is at most 8 words. For codes 45, 54, 166, 171 and 172 the source label is longer and the field holds the cataloguer's own-words label instead (flagged in `notes`). Empty if not in docs.","S1"),
"applies_a100":("YES/NO/not documented","Docs Table 1 'Applies to A100'. 'not documented' when the docs do not list the code.","S1"),
"applies_h100":("YES/NO/not documented","Docs Table 1 'Applies to H100'.","S1"),
"applies_b100":("YES/NO/not documented","Docs Table 1 'Applies to B100'.","S1"),
"applies_gb200":("YES/NO/not documented","Docs Table 1 'Applies to GB200'.","S1"),
"docs_immediate_bucket":("string","Docs Table 1 'Resolution Bucket (Immediate Action)', verbatim identifier (e.g. RESTART_APP, RESET_GPU, WORKFLOW_XID_48). Empty if blank or not in docs. Table 3 of the docs defines the identifiers.","S1"),
"docs_investigatory_bucket":("string","Docs Table 1 'Resolution Bucket (Investigatory Action)', verbatim identifier. Empty if blank or not in docs.","S1"),
"docs_xid154_linkage":("string","Docs Table 1 'Xid 154 linkage' (driver/CUDA version from which the code also triggers Xid 154), verbatim. Empty if blank.","S1"),
"archive_failure_label":("string","Failure label from the r555 archive page failure-cause table. Several labels for one code are joined with ' | '. Codes taken from a range row carry the range row's label (Reserved). Verbatim when at most 8 words; own-words label for codes 45 and 54 (flagged in `notes`).","S1b"),
"archive_cause_flags":("string","Cause columns marked X in the archive table (HW Error, Driver Error, User App Error, System Memory Corruption, Bus Error, Thermal Issue, FB Corruption). One group per label, groups joined with ' | ', causes joined with ';', '-' for none.","S1b"),
"debug_guideline_action":("string, <=25 words","Cataloguer's summary of the action in debug-guidelines Table 1 (gpu-node-triage page). Empty if the code is not in that table.","S3 (summarised)"),
"rma_guidance_referenced":("yes/no","yes if the debug-guidelines row for the code points to the guide's RMA criteria. It is a pointer, not a recommendation to RMA.","S3"),
"subsystem":("enum","Functional area. Values: memory/ECC, PCIe/bus, NVLink/C2C interconnect, engine/channel, media/accelerator engine, display, firmware/microcontroller, power/thermal, security, virtualization, driver/software, not documented. Rule in CLASSIFICATION.md.","computed"),
"subsystem_basis":("string","Which text decided subsystem: a docs/archive description phrase, a name token, or a docs trigger-text statement; or why the value is 'not documented'.","computed"),
"severity_derived":("enum","fatal, degraded, informational, varies by subcode, unused, not documented. The cataloguer's derivation from the documented recovery action, not a severity stated by NVIDIA and not a measure of intrinsic impact. Rule in CLASSIFICATION.md.","computed"),
"severity_basis":("string","Why severity_derived has its value (the documented action or text relied on).","computed"),
"recovery_action":("enum","none needed, restart application, restart VM, reset GPU, restart host (bare metal), drain-and-reset (defined, unused in v1), contact support, update firmware/software, check mechanical seating, conditional workflow, not applicable (unused), not documented. Rule in CLASSIFICATION.md.","computed from S1/S3 text"),
"recovery_basis":("string","Source of the recovery_action value (docs bucket, docs trigger text, or debug guidelines).","computed"),
"recovery_detail":("string, <=25 words","Cataloguer's note where the documented action has conditions or extra steps. Empty otherwise.","S1/S3 (summarised)"),
"in_docs_catalogue":("yes/no","Code is a row in docs Table 1.","S1"),
"in_header":("yes/no","Code has a macro in nverror.h (code range block only).","S2"),
"in_archive_listing":("yes/no","Code is covered by the r555 archive failure-cause table (single row or inside a range row).","S1b"),
"in_debug_guidelines":("yes/no","Code has a row in debug-guidelines Table 1.","S3"),
"source_count":("integer 1-4","Number of the four 'in_' flags that are yes.","computed"),
"source_pointers":("string","URL plus locator for each source that lists the code, joined with ' ; '. Header pointers are permalinks pinned to the commit in SOURCES.md, with line number.","S1-S3"),
"notes":("string","Row-level flags: source inconsistencies noted during the build, and a flag where a label was paraphrased. Several flags are joined with '; '. Empty if none.","computed"),
}
assert list(D)==cols, (set(cols)^set(D))
dd="# DATA-DICTIONARY — xid-catalogue v1\n\nOne row per Xid code. Files: `xid-catalogue.csv`, `xid-catalogue.json` (identical content; the JSON adds a `metadata` object). "+f"Rows: {N}. Columns: {NC}. Encoding UTF-8. Empty string means 'source gives nothing for this field'; classification fields never empty (they hold 'not documented', 'unused' or 'not applicable (unused)').\n\nSource keys: S1 = docs catalogue Table 1; S1b = r555 archive page table; S2 = nverror.h; S3 = debug guidelines Table 1. Details in SOURCES.md.\n\n| # | Column | Type | Definition | Source |\n|---|---|---|---|---|\n"+"\n".join(f"| {i+1} | `{k}` | {t} | {d} | {s} |" for i,(k,(t,d,s)) in enumerate(D.items()))
open("DATA-DICTIONARY.md","w").write(dd+"\n")
# ------------------------------------------------------------------ CLASSIFICATION.md
import re as _re
_as=[r for r in R if r["subsystem"]!="not documented"]
ev_name=sum(1 for r in _as if r["subsystem_basis"].startswith("name"))
ev_desc=len(_as)-ev_name
ev_media=sum(1 for r in _as if _re.search(r"name token '(NVDEC|NVENC|NVJPG|OFA)'",r["subsystem_basis"]))
ev_hdr=sum(1 for r in _as if r["in_docs_catalogue"]=="no")
cls=f"""# CLASSIFICATION — scheme and decision rules

Principle: a value is assigned only when a source supports it. Otherwise the value is `not documented`. The three fields are separate; each has a `*_basis` or `recovery_basis` column so a reader can see why.

```mermaid
flowchart TD
  S1[docs Table 1: bucket, description, applies-to] --> REC[recovery_action]
  S1T[docs trigger text] --> REC
  S3[debug guidelines Table 1] --> REC
  REC --> SEV[severity_derived]
  S1 --> UN{{status = unused?}}
  UN -->|yes| SEVU[severity_derived = unused, recovery = not applicable]
  UN -->|no| REC
  S1 --> SUBD[subsystem: description phrase]
  S1B[archive label] --> SUBD
  S2[header macro name] --> SUBN[subsystem: name token]
  SUBD -->|no match| SUBN
  SUBN -->|no match| NDS[subsystem = not documented]
```
Walkthrough: documentation text (docs bucket, trigger text, debug guidelines) decides `recovery_action`. `severity_derived` is then derived from that action. Unused codes short-circuit to `unused`. `subsystem` is decided separately from description phrases first, then name tokens. No connection in this diagram is inferred; all follow `scripts/build.py`.

## 1. status
- `unused`: docs description is "Unused" and all four applies-to flags are NO; or the header macro name contains UNUSED; or (code 108) the description and trigger text say Unused although the flags say applicable, recorded in `notes`.
- `unused in catalogue; action in debug guidelines`: codes 61 and 123. The docs catalogue lists them as unused, the debug guidelines give a reset action. Their severity and recovery values come from the debug guidelines.
- `reserved`: header macro name contains RESERVED and the docs do not list the code.
- `active`: documented and not unused. `active (header only)`: header name only, nothing documented.
- Counts: {', '.join(f'{k} {v}' for k,v in sta.most_common())}.

## 2. recovery_action (documented action)
Order of evidence: (1) explicit statements in docs trigger text or Table 3 workflows where they override the bucket (codes 45, 48, 74, 154, 163-165, 168, 144-150); (2) docs immediate-action bucket mapped by the table below; (3) debug-guidelines action when the docs have no usable bucket (codes 61, 123 only); otherwise `not documented`.

| docs bucket | recovery_action |
|---|---|
| IGNORE | none needed |
| RESTART_APP | restart application |
| RESTART_VM | restart VM |
| RESET_GPU | reset GPU |
| RESTART_BM | restart host (bare metal) |
| CONTACT_SUPPORT | contact support (for unused codes: not applicable (unused), since it is the default) |
| UPDATE_SWFW | update firmware/software |
| CHECK_MECHANICALS | check mechanical seating |
| WORKFLOW_*, XID_154, CHECK_UVM | conditional workflow |
| blank | not documented |

Recovery values considered but not used in v1: `RMA` and `driver restart`. No source gives either as the action for a single code. The debug guidelines point to RMA criteria for codes {', '.join(map(str,Q['rma_flag_codes']))}; that is recorded in `rma_guidance_referenced`, not as the action. `drain-and-reset` appears in the docs only as a branch inside the Xid 48 workflow and in debug-guideline text for 48, 63, 95; it is kept in `recovery_detail`/`debug_guideline_action`, not as a primary value, because the primary action differs by branch. Examples: Xid 8 -> restart application (bucket RESTART_APP); Xid 46 -> reset GPU (RESET_GPU); Xid 79 -> restart host (RESTART_BM); Xid 48 -> reset GPU (trigger text: reset or reboot needed), with the Table 3 branches in `recovery_detail`.
Counts: {', '.join(f'{k} {v}' for k,v in rec.most_common())}.

## 3. severity_derived
Derived from the documented recovery action. It reflects what the documentation requires to recover, not how bad the fault is physically. It is not NVIDIA's severity: NVIDIA states a severity only per subcode for codes 144-150 (docs Table 2, column "Severity"), and that column is not in v1. The column name carries `_derived` so the value is not read as vendor-stated.
- `fatal`: action is reset GPU, restart host, or drain-and-reset (the GPU or node cannot continue without it). Example: Xid 95.
- `degraded`: action is restart application or restart VM (the docs state the GPU itself needs no reset: Table 3 text for RESTART_APP and RESTART_VM). Example: Xid 94.
- `informational`: action is none needed (bucket IGNORE, Table 3 text "No Action required"), or the docs say the code only reports another Xid (Xid 154, Xid 45). Example: Xid 121.
- `varies by subcode`: codes 144-150; docs Table 2 gives severity per decoded subcode (link fatal, GPU fatal, non-fatal) and no single value fits. Subcode severities are not in v1.
- `unused`: status is unused (docs say unused / header name says unused or reserved).
- `not documented`: no documented action maps to the three levels (contact support, update firmware, check seating, unresolved conditional workflows, blank bucket). Example: Xid 142 (bucket CONTACT_SUPPORT), Xid 167 (name contains FATAL but no source gives behaviour).
Counts: {', '.join(f'{k} {v}' for k,v in sev.most_common())}.

Known weakness: docs mark some codes IGNORE that a reader may regard as serious (for example 44, graphics-engine fault during context switch). The dataset follows the documentation and says so in `severity_basis`.

## 4. subsystem
Rule order: (a) explicit override from docs trigger text (codes 119, 120, 159; code 183 by name token with a stated link to 119/120); (b) phrase in docs description or archive label, e.g. "micro-controller", "ECC", "memory error", "Power", "CC", "Display", "Video processor", "semaphore"; (c) token in the macro/mnemonic, e.g. FIFO, GR_, CE<n>, NVDEC, NVLINK, C2C, PCIE, PSHC, GSP; (d) otherwise `not documented`.
Tokens the sources do not explain (for example LTC, RIST, SPARING, COHERENCY, FECS, CHI, SEC2, ALI, DLA in name alone) are not decoded; the row stays `not documented` unless a description phrase decides it. The same holds for names that state no subsystem or an ambiguous one: channel retirement (160, 161), resource retirement (156, 157), bank remapping (177), telemetry driver report (87), recovery action changed (154).
How name tokens are supported. FIFO, GR, PBDMA, CE, VP, PMU, NVLINK, C2C, PCIE and GSP are tied to a subsystem by a label or text in the sources for at least one code of the family (for example CE0-CE2 are labelled "Copy Engine Exception"; GR codes are labelled "Graphics Engine"; PMU_BREAKPOINT is labelled as a micro-controller breakpoint). NVDEC, NVENC, NVJPG and OFA are not expanded anywhere in the sources reviewed; the header groups them as indexed engine families, and their assignment to media/accelerator engine rests on NVIDIA's public engine names, not on a statement in the sources. Rows decided by a name token say so in `subsystem_basis`; a user who wants description-only evidence can filter on that column. Examples: Xid 48 -> memory/ECC (description "Double Bit ECC Error"); Xid 79 -> PCIe/bus (name token FALLEN_OFF_THE_BUS); Xid 60 -> media/accelerator engine (description "Video processor exception", although the name says SEC2); Xid 186 -> not documented.
Grouping choices are the cataloguer's: INFOROM codes are grouped with firmware/microcontroller; copy engines (CE<n>) and the FIFO/GR/PBDMA family are grouped as engine/channel; NVDEC/NVENC/NVJPG/OFA/DLA are grouped as media/accelerator engine; C2C is grouped with NVLink.
Counts: {', '.join(f'{k} {v}' for k,v in sub.most_common())}.
Evidence behind the {N-sub['not documented']} assigned values: description phrase or docs trigger text {ev_desc}; name token {ev_name} (of which NVDEC/NVENC/NVJPG/OFA {ev_media}). Header-only codes with a subsystem from the name token: {ev_hdr} of {len(hdr_only)}.
"""
open("CLASSIFICATION.md","w").write(cls)
# ------------------------------------------------------------------ SOURCES.md
src=f"""# SOURCES — xid-catalogue v1

Retrieval date: {retr} (first fetch 2026-11-18T22:21:32Z; verification re-fetches 2026-11-18T22:31:10Z and {retr_t} UTC, each byte-identical to the first fetch). All fetches returned HTTP 200 and were saved unmodified under `raw/`.

```mermaid
flowchart LR
  D1[docs catalogue page + xlsx] --> X1[extraction/docs-catalog-*.csv]
  D2[docs archive page r555] --> X2[extraction/archive-*.csv]
  H[nverror.h at pinned commit] --> X3[extraction/header-defines.csv]
  G[debug guidelines pages] --> X4[extraction/debug-*.csv]
  X1 & X2 & X3 & X4 --> B[scripts/build.py] --> OUT[xid-catalogue.csv / .json]
  OUT --> QA[scripts/qa.py: fresh re-fetch + independent parse]
```

| Key | Source | URL | What was taken |
|---|---|---|---|
| S1 | NVIDIA XID Errors, "Analyzing Xid Errors with the Xid Catalog" (page shows "Last updated on Nov 11, 2026") | https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html (anchor #id1 = Table 1) | Table 1: code, mnemonic, description, applies-to A100/H100/B100/GB200, immediate and investigatory bucket, Xid 154 linkage; trigger-condition text (summarised only). Tables 2-4 (Xid 144-150 decode, resolution buckets, customer user guide) read for the rules; Table 3 bucket meanings used in CLASSIFICATION.md. Same data downloaded as https://docs.nvidia.com/deploy/xid-errors/_downloads/4586dadb59119a55d1e93a181caa4272/Xid-Catalog.xlsx and used as a cross-check only |
| S1 root | https://docs.nvidia.com/deploy/xid-errors/index.html and sub-pages introduction.html, working-with-xid-errors.html, Notices.html | | index, working-with-xid-errors and Notices read for context and terms; introduction.html read for its SXid statement (SXids are documented in the Fabric Manager User Guide; the page notes that SXid messages apply only to Hopper and earlier generation GPUs). No code rows on these pages. |
| S1b | NVIDIA XID Errors r555 archive page (older GPUs) | https://docs.nvidia.com/deploy/xid-errors/archive/index.html (section #xid-error-listing) | Failure-cause table: failure label per Xid and the seven cause columns. Section 1.2 states SXids are documented in the Fabric Manager User Guide. |
| S2 | nverror.h, open-gpu-kernel-modules | https://github.com/NVIDIA/open-gpu-kernel-modules/blob/main/src/common/sdk/nvidia/inc/nverror.h ; pinned to commit {SHA} (committer date 2026-11-05T00:16:53Z, commit message "620.70.06", read from the GitHub commits API). Raw file at that commit is byte-identical to the file fetched from main. | Macro name and value for each code, with line number (#L<n> permalinks in `source_pointers`). |
| S3 | NVIDIA GPU Debug Guidelines | https://docs.nvidia.com/deploy/gpu-debug-guidelines/index.html ; code table at .../gpu-node-triage.html (Table 1 "Common XID Messages and Recommended Steps"); overview, initial-incident-report, best-practices fetched and scanned for Xid/SXID/RMA mentions and tables (no code tables found); Notices read | Per-code action for 14 codes (summarised). Mentions of RMA criteria and SXIDs noted. |

## Licence and terms notes
- **NVIDIA documentation (S1, S1b, S3).** Pages show "Copyright © 2013-2026, NVIDIA Corporation & affiliates. All rights reserved." The Notices page (read on both doc sets) says reproduction of information in the document is permissible only if approved in advance by NVIDIA in writing, reproduced without alteration, and with all associated conditions, limitations and notices; it also says no licence is granted under NVIDIA copyright. **This is a rights risk for a public release of docs-derived content.** The dataset limits itself to factual fields (numbers, identifiers, short labels, applicability flags) and own-words summaries. No permission has been sought or given, and the dataset is not endorsed by NVIDIA. The release states this in its rights note (README.md and the paper).
- **Header (S2).** The file begins with a permission notice in MIT form (read in the file); the repository's COPYING states that, except where noted, individual files are licensed MIT (first lines read, commit {SHA[:12]}). The notice requires the copyright and permission text to be kept with copies or substantial portions; the dataset copies only names and numbers, and should still cite the file and carry the notice in its README.
- **Do not deposit** `raw/`, `extraction/` or `qa-live/`: they hold unmodified NVIDIA pages and files.

## Fields that carry source wording (current state)
- `docs_description`, `archive_failure_label`: the source's short label, verbatim, when it is at most {build.LABEL_MAX_WORDS} words (longest kept: {Q['label_words_max']} words). Source labels longer than that are not copied: codes {', '.join(map(str,sorted(PARA)))} hold an own-words label, set in `scripts/build.py` (`LABEL_REWRITE`) and flagged in `notes`.
- `name_docs`, `name_header`, `docs_immediate_bucket`, `docs_investigatory_bucket`, `docs_xid154_linkage`, applies-to flags: identifiers and short strings as given. A few investigatory values are short phrases (for example "N/A Informational only regarding another Xid").
- `meaning`: for the {sum(1 for r in R if r['meaning'].startswith('Catalogue label:'))} rows without explanatory text it restates the short label ("Catalogue label: ..."). For codes {', '.join(map(str,meaning_codes))} it is an own-words summary of a narrow factual statement.
- `debug_guideline_action` and `recovery_detail`: own-words summaries of procedural text.
- Trigger-condition text, Table 3 workflow text and Table 4 text are not copied into any field.
- The dataset still reproduces, as facts, most cells of docs Table 1 for 172 codes (mnemonic, flags, buckets, linkage, short label). Whether that needs NVIDIA's approval under the Notices wording is not settled here; the release carries a rights note (README.md).
"""
open("SOURCES.md","w").write(src)
