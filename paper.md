# Data article (Data in Brief style)

**Title.** A source-linked catalogue of NVIDIA GPU Xid error codes with documented-action classification

**Author.** Sajish Krishnan. Affiliation: Independent researcher. ORCID: https://orcid.org/0009-0009-7561-9290

**Abstract.** NVIDIA drivers report GPU faults to the system log as numbered Xid events. The numbers and their meanings are published in several places that differ in coverage and, for 10 codes, in naming. This dataset joins four NVIDIA-published sources into one table with one row per Xid code: 186 codes, numbered 1 to 186. Each row carries the names used by the sources, the product-applicability flags and resolution buckets from the documentation catalogue, a short own-words summary, three classification fields (subsystem, derived severity, documented recovery action) with the stated basis for each value, and pointers to the source locations. Where the sources give no support, the field holds "not documented". The files are a CSV and a JSON file with identical content, a data dictionary, a source list, a classification guide and a QA report. The release does not include SXID (NVSwitch) codes, which none of the four sources lists.

**Keywords.** NVIDIA; GPU; Xid; error codes; data centre operations; fault classification

## Specifications table
| Item | Value |
|---|---|
| Subject | Computer science; hardware reliability |
| Specific subject area | NVIDIA GPU driver error (Xid) codes |
| Type of data | Table (CSV, JSON); text documentation |
| How the data were acquired | Retrieval of public NVIDIA web pages and one public source header on 2026-11-18; extraction by script; classification by stated rules |
| Data format | Curated; 186 rows, 35 columns |
| Data source | docs.nvidia.com (Xid Errors, GPU Debug Guidelines); github.com/NVIDIA/open-gpu-kernel-modules, file nverror.h, commit e6a2e01579fb |
| Data accessibility | Repository: Zenodo. DOI: 10.5281/zenodo.24362095 |

## Value of the Data
- The catalogue gives one machine-readable row for each of 186 Xid codes, joined across four sources, with a pointer back to each source location. Log parsers and alert rules can use it as a lookup table.
- It records where the sources differ. Of the 129 codes present in both the documentation catalogue and the header, 10 have different names. 46 codes whose description in the current catalogue is "Unused" carry a failure label in the archived page for older GPUs.
- Classification values come with a basis column, so a user can see which documented statement or name token produced a value and can replace the rule with their own.
- 14 codes (173 to 186) exist only in the header. The dataset lists them by name. None has a documented recovery action; 6 carry a subsystem read from a literal token in the name (C2C, PCIE, MEMORY_SUBSYSTEM, GSP) and 2 are named unused or reserved.

## Data Description
The dataset has 186 rows (one per Xid code) and 35 columns (see DATA-DICTIONARY). Every row has `code_type` XID; no SXID rows are included. Table 1 gives the number of codes per source. Table 2 gives the distribution of the classification values.

**Table 1. Coverage by source.**

| Source | Codes |
|---|---|
| Documentation catalogue, current (Ampere and newer GPUs) | 172 |
| Archive page for older GPUs (r555), failure-cause table | 143 |
| Header nverror.h | 143 |
| Debug-guidelines table of common messages | 14 |
| Union (rows in dataset) | 186 |
| In documentation catalogue and header | 129 |
| In header only | 14 |
| In documentation catalogue only (not in header) | 43 |

**Table 2. Classification values (rows).**

| Field | Values |
|---|---|
| status | active 110, unused 61, active (header only) 12, unused in catalogue; action in debug guidelines 2, reserved 1 |
| severity_derived | unused 62, degraded 49, not documented 27, informational 22, fatal 19, varies by subcode 7 |
| recovery_action | not applicable (unused) 62, restart application 48, none needed 20, not documented 19, reset GPU 18, conditional workflow 14, check mechanical seating 1, update firmware/software 1, restart host (bare metal) 1, contact support 1, restart VM 1 |
| subsystem | engine/channel 45, media/accelerator engine 33, not documented 29, firmware/microcontroller 15, NVLink/C2C interconnect 15, display 13, memory/ECC 13, power/thermal 8, driver/software 5, PCIe/bus 5, security 4, virtualization 1 |

The `severity_derived` field is our derivation, not a severity stated by NVIDIA. It follows the documented recovery action: actions that require a GPU reset or host restart are coded fatal, application or VM restarts degraded, and "no action" informational. NVIDIA states a severity only per decoded subcode for codes 144 to 150; those seven codes are coded "varies by subcode" and the subcode table is not part of this release. The `meaning` field is a summary of at most 25 words. Text of the documentation is not reproduced. Source labels of up to 8 words and identifiers are kept as given; five longer labels (codes 45, 54, 166, 171, 172) are replaced by own-words labels and flagged in `notes`.

## Experimental Design, Materials and Methods
**Sources.** Four public NVIDIA sources were retrieved on 2026-11-18: (1) the current Xid catalogue page and its spreadsheet download, whose page footer showed "Last updated on Nov 11, 2026"; (2) the archived Xid Errors page for release r555, which covers older GPUs; (3) the file nverror.h from the open GPU kernel modules repository, pinned to commit e6a2e01579fb; (4) the GPU Debug Guidelines page "GPU Node Triage". The unmodified files were kept.

**Extraction.** Tables were parsed from the HTML into one raw file per table before any cleaning. For the header, every `#define` was listed with its line number; entries whose value is a code were kept (143 codes, numbered 13 to 186), and 4 further lines (a range sentinel and three recovery-level constants) were excluded as not being codes. Two alias macros were attached to codes 63 and 64. Range rows in the archive table (126 to 136 and 138 to 139) were expanded to single codes. The spreadsheet and the HTML table contain the same 172 codes with the same mnemonics, descriptions, applicability flags and buckets.

**Joining.** Rows were joined on the integer code. The documentation mnemonic is used as the primary name when present; the header macro is kept separately. No row was merged away: there are no duplicate codes.

**Classification.** Rules are given in CLASSIFICATION.md. Recovery action comes from the immediate-action bucket of the documentation catalogue. For 15 codes the value or its severity reading was set from other documentation text or tables: the recovery action itself differs from the bucket mapping for 6 of them (48, 74, 163, 164, 165, 168), and only the derived severity is affected for the other 9 (45, 144 to 150, 154). For two codes (61 and 123) that the catalogue lists as unused, the action comes from the debug-guidelines table, and the status field records this as "unused in catalogue; action in debug guidelines". Code 108 has the description and trigger text "Unused" but applicability flags of YES; it is coded unused and a note states the conflict. Derived severity follows from the recovery action. Subsystem comes first from phrases in the documentation description, archive label or trigger text (54 rows), then from tokens in the code name (103 rows). Tokens that the sources do not explain were left undecoded. For 20 of the name-token rows (NVDEC, NVENC, NVJPG and OFA engines) the sources reviewed do not expand the token, and the assignment rests on NVIDIA's public engine names. Fields without support hold "not documented".

**Quality checks.** Row counts agree between CSV and JSON (186 each). Every row has at least one source pointer. 25 codes were re-read from freshly retrieved copies of the sources with a second, independent parser. All matched; for the one sampled code with a paraphrased label (45) the check confirmed the paraphrase flag instead of the label text. The full documentation table (172 codes, nine columns) was also compared cell by cell with the spreadsheet download, with no differences other than the five paraphrased labels. The re-checks used byte-identical re-fetches of the same pages and the same author, not a second reviewer.

## Limitations
- SXID (NVSwitch) codes are not included: none of the four sources lists them. The documentation refers to the Fabric Manager User Guide for SXIDs and states that they apply only to Hopper and earlier generation GPUs. That guide was not used.
- 14 codes have no documentation beyond the header macro name. 61 codes have status unused (60 from the catalogue, 1 from the header name), and 2 more have the status "unused in catalogue; action in debug guidelines". 29 rows have no documented subsystem. 27 rows have no derived severity, in addition to the 62 coded unused.
- Derived severity is our reading of the documented action. It is not a measured or vendor-stated severity, and some codes with the action "none needed" may still matter operationally. Subcode-level severity for codes 144 to 150 is not included.
- 103 subsystem values rest on a token in the code name, not on a description. The basis column marks each of them.
- Codes 61 and 123 are listed as unused in the current catalogue, while the debug guidelines give a reset action for them. They carry the distinct status "unused in catalogue; action in debug guidelines", and their derived severity (fatal) and recovery action (reset GPU) come from the debug guidelines, so filtering on status does not drop them silently. Code 108 is described as "Unused" in the catalogue description and trigger text but flagged as applicable to all four products; two of the three source fields say unused, so it is coded unused and the conflict is stated in `notes`. The sources themselves remain in disagreement for these three codes.
- The 46 codes that are "Unused" in the current catalogue and labelled in the archive page may reflect product generation (the archive page covers older GPUs), not a conflict. The sources do not say.
- The sources are snapshots of 2026-11-18; NVIDIA updates them, and the numbering, names and buckets can change. The applicability flags cover four products (A100, H100, B100, GB200).
- The catalogue was not checked against real logs or hardware.

## Comparison with existing material
The documentation catalogue for Ampere and newer GPUs is published as an HTML table and as a downloadable spreadsheet; it lists codes 1 to 172 with mnemonic, description, applicability to four products and two resolution buckets. The archived page for r555 lists codes 1 to 143 with a failure label and seven cause columns. The debug-guidelines page gives actions for 14 codes. The header lists 143 code macros, from 13 to 186, as names without descriptions. The spreadsheet is already machine-readable; this dataset does not claim a new format. It adds a single row per code across all four sources, including the 14 codes that only the header has, classification fields with a stated basis for every value, a record of source differences, pointers with header line numbers and a pinned commit, and a versioned archive deposit with a DOI. It does not add information that the sources lack.

## Rights and permissions
Code numbers, names, applicability flags and bucket identifiers are reproduced as facts from the cited sources; the header nverror.h is distributed by NVIDIA under an MIT-style permission notice, which accompanies the dataset. Descriptive text in the dataset is the author's own wording, apart from short labels of at most 8 words that serve as the sources' names for a condition. The NVIDIA documentation pages are copyright NVIDIA Corporation and state that reproduction requires NVIDIA's prior written approval; no such approval has been sought or given, and the dataset is not endorsed by NVIDIA.

## Declaration of competing interests
The author declares no known competing financial interests or personal relationships that could have appeared to influence the work reported in this article.

## Data availability
The dataset is deposited in Zenodo. DOI: 10.5281/zenodo.24362095.

## CRediT
Sajish Krishnan: conceptualisation, data curation, methodology, writing.
