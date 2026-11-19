# DATA-DICTIONARY — xid-catalogue v1

One row per Xid code. Files: `xid-catalogue.csv`, `xid-catalogue.json` (identical content; the JSON adds a `metadata` object). Rows: 186. Columns: 35. Encoding UTF-8. Empty string means 'source gives nothing for this field'; classification fields never empty (they hold 'not documented', 'unused' or 'not applicable (unused)').

Source keys: S1 = docs catalogue Table 1; S1b = r555 archive page table; S2 = nverror.h; S3 = debug guidelines Table 1. Details in SOURCES.md.

| # | Column | Type | Definition | Source |
|---|---|---|---|---|
| 1 | `code` | integer | The Xid number as printed in kernel logs (NVRM: Xid ...). Primary key; unique per row. | S1/S1b/S2/S3 (the number itself) |
| 2 | `code_type` | string | Always XID in v1. SXID reserved for a later version (no SXID codes in the listed sources). | fixed |
| 3 | `name` | string | Preferred name: the first docs-catalogue mnemonic when the docs list the code, otherwise the header macro. | S1, else S2 |
| 4 | `name_docs` | string | Mnemonic(s) from docs catalogue Table 1 column 'Mnemonic'. Two mnemonics are joined with ' / ' (Xid 13). Empty if the docs do not list the code. | S1 |
| 5 | `name_header` | string | Macro name from nverror.h that has this code as value. Empty if the header has no macro for the code. | S2 |
| 6 | `header_aliases` | string | Other header macros defined as aliases of name_header (63 and 64 only). Semicolon separated. | S2 |
| 7 | `name_conflict` | string | Non-empty when docs mnemonic and header macro differ in more than spelling or a listed alias. Text: 'docs mnemonic and header macro differ'. | computed |
| 8 | `status` | enum | unused = docs description is 'Unused' and all four applies-to flags are NO, or header macro name says UNUSED, or code 108 (description and trigger text say Unused, flags say applicable; see notes); 'unused in catalogue; action in debug guidelines' = codes 61 and 123 (docs say unused, debug guidelines give a reset action); reserved = header macro name says RESERVED and the docs do not list the code; active = anything else documented; 'active (header only)' = active by header name, no further documentation. | computed from S1, S2 |
| 9 | `meaning` | string, <=25 words | Short factual summary in the cataloguer's words. For rows with explanatory text in the docs it summarises that text; for the rest it restates the short label ('Catalogue label: ...') or says that nothing is described. See SOURCES.md for the fields where this was hard to keep apart from the source wording. | S1, S1b, S2 (summarised) |
| 10 | `docs_description` | string | Docs Table 1 column 'Description': the source's short label, verbatim when it is at most 8 words. For codes 45, 54, 166, 171 and 172 the source label is longer and the field holds the cataloguer's own-words label instead (flagged in `notes`). Empty if not in docs. | S1 |
| 11 | `applies_a100` | YES/NO/not documented | Docs Table 1 'Applies to A100'. 'not documented' when the docs do not list the code. | S1 |
| 12 | `applies_h100` | YES/NO/not documented | Docs Table 1 'Applies to H100'. | S1 |
| 13 | `applies_b100` | YES/NO/not documented | Docs Table 1 'Applies to B100'. | S1 |
| 14 | `applies_gb200` | YES/NO/not documented | Docs Table 1 'Applies to GB200'. | S1 |
| 15 | `docs_immediate_bucket` | string | Docs Table 1 'Resolution Bucket (Immediate Action)', verbatim identifier (e.g. RESTART_APP, RESET_GPU, WORKFLOW_XID_48). Empty if blank or not in docs. Table 3 of the docs defines the identifiers. | S1 |
| 16 | `docs_investigatory_bucket` | string | Docs Table 1 'Resolution Bucket (Investigatory Action)', verbatim identifier. Empty if blank or not in docs. | S1 |
| 17 | `docs_xid154_linkage` | string | Docs Table 1 'Xid 154 linkage' (driver/CUDA version from which the code also triggers Xid 154), verbatim. Empty if blank. | S1 |
| 18 | `archive_failure_label` | string | Failure label from the r555 archive page failure-cause table. Several labels for one code are joined with ' | '. Codes taken from a range row carry the range row's label (Reserved). Verbatim when at most 8 words; own-words label for codes 45 and 54 (flagged in `notes`). | S1b |
| 19 | `archive_cause_flags` | string | Cause columns marked X in the archive table (HW Error, Driver Error, User App Error, System Memory Corruption, Bus Error, Thermal Issue, FB Corruption). One group per label, groups joined with ' | ', causes joined with ';', '-' for none. | S1b |
| 20 | `debug_guideline_action` | string, <=25 words | Cataloguer's summary of the action in debug-guidelines Table 1 (gpu-node-triage page). Empty if the code is not in that table. | S3 (summarised) |
| 21 | `rma_guidance_referenced` | yes/no | yes if the debug-guidelines row for the code points to the guide's RMA criteria. It is a pointer, not a recommendation to RMA. | S3 |
| 22 | `subsystem` | enum | Functional area. Values: memory/ECC, PCIe/bus, NVLink/C2C interconnect, engine/channel, media/accelerator engine, display, firmware/microcontroller, power/thermal, security, virtualization, driver/software, not documented. Rule in CLASSIFICATION.md. | computed |
| 23 | `subsystem_basis` | string | Which text decided subsystem: a docs/archive description phrase, a name token, or a docs trigger-text statement; or why the value is 'not documented'. | computed |
| 24 | `severity_derived` | enum | fatal, degraded, informational, varies by subcode, unused, not documented. The cataloguer's derivation from the documented recovery action, not a severity stated by NVIDIA and not a measure of intrinsic impact. Rule in CLASSIFICATION.md. | computed |
| 25 | `severity_basis` | string | Why severity_derived has its value (the documented action or text relied on). | computed |
| 26 | `recovery_action` | enum | none needed, restart application, restart VM, reset GPU, restart host (bare metal), drain-and-reset (defined, unused in v1), contact support, update firmware/software, check mechanical seating, conditional workflow, not applicable (unused), not documented. Rule in CLASSIFICATION.md. | computed from S1/S3 text |
| 27 | `recovery_basis` | string | Source of the recovery_action value (docs bucket, docs trigger text, or debug guidelines). | computed |
| 28 | `recovery_detail` | string, <=25 words | Cataloguer's note where the documented action has conditions or extra steps. Empty otherwise. | S1/S3 (summarised) |
| 29 | `in_docs_catalogue` | yes/no | Code is a row in docs Table 1. | S1 |
| 30 | `in_header` | yes/no | Code has a macro in nverror.h (code range block only). | S2 |
| 31 | `in_archive_listing` | yes/no | Code is covered by the r555 archive failure-cause table (single row or inside a range row). | S1b |
| 32 | `in_debug_guidelines` | yes/no | Code has a row in debug-guidelines Table 1. | S3 |
| 33 | `source_count` | integer 1-4 | Number of the four 'in_' flags that are yes. | computed |
| 34 | `source_pointers` | string | URL plus locator for each source that lists the code, joined with ' ; '. Header pointers are permalinks pinned to the commit in SOURCES.md, with line number. | S1-S3 |
| 35 | `notes` | string | Row-level flags: source inconsistencies noted during the build, and a flag where a label was paraphrased. Several flags are joined with '; '. Empty if none. | computed |
