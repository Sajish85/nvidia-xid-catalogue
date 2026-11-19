# QA — xid-catalogue v1 (built 2026-11-18)

## Summary
- Rows: **186** in CSV, **186** in JSON; CSV == JSON content check: **True**. Codes 1-186, no duplicates (duplicate count 0).
- SXID rows: **0** (no SXID codes appear in the three listed sources; SXID is out of scope for this release).
- Spot-check: **25** codes re-verified against a fresh live fetch, **0** failures.
- Rows with an empty classification cell: **0**. Rows with no source pointer: **0**. `meaning` fields over 25 words: **0**.

## 1. Counts per source (codes, not rows of source tables)
| Source | Codes found | Notes |
|---|---|---|
| S1 docs catalogue, Table 1 (analyzing-xid-catalog.html, Ampere and newer) | 172 | Codes 1-172, all type XID; HTML table and downloadable Xid-Catalog.xlsx agree on the code set (172 XID rows in the xlsx, code sets equal: True) |
| S1b docs archive page (r555, older GPUs) failure-cause table | 143 | Codes 1-143. Includes 13 codes taken from two range rows ("126-136", "138-139", both labelled Reserved) |
| S2 header nverror.h (commit e6a2e01579fb) | 143 | Excluded from count: ROBUST_CHANNEL_LAST_ERROR, ROBUST_CHANNEL_ERROR_RECOVERY_LEVEL_INFO, ROBUST_CHANNEL_ERROR_RECOVERY_LEVEL_NON_FATAL, ROBUST_CHANNEL_ERROR_RECOVERY_LEVEL_FATAL. Two alias macros (INFOROM_DRAM_RETIREMENT_EVENT/FAILURE) map to codes 63/64 and are stored in `header_aliases`, not as extra rows |
| S3 debug guidelines, gpu-node-triage.html Table 1 | 14 | Codes 13, 31, 45, 48, 61-64, 74, 79, 92, 94-95, 123. Other debug pages (overview, initial-incident-report, best-practices) hold no code tables |
| **Union (dataset rows)** | **186** | |

## 2. Overlap and dedup
- One row per integer code. Primary key is the code number; sources are joined on it.
- Codes in both docs catalogue and header: 129.
- Source-count distribution (how many of the four sources list a code): 1 source(s): 14 codes, 2 source(s): 72 codes, 3 source(s): 86 codes, 4 source(s): 14 codes.
- Header alias macros: INFOROM_PAGE_RETIREMENT_EVENT = INFOROM_DRAM_RETIREMENT_EVENT (line 70), INFOROM_PAGE_RETIREMENT_FAILURE = INFOROM_DRAM_RETIREMENT_FAILURE (line 72).
- Header lines excluded as non-codes: line 183 ROBUST_CHANNEL_LAST_ERROR (range sentinel (= last code), not a code); line 308 ROBUST_CHANNEL_ERROR_RECOVERY_LEVEL_INFO (recovery-level constant, not an Xid); line 309 ROBUST_CHANNEL_ERROR_RECOVERY_LEVEL_NON_FATAL (recovery-level constant, not an Xid); line 310 ROBUST_CHANNEL_ERROR_RECOVERY_LEVEL_FATAL (recovery-level constant, not an Xid).
- Name conflicts between docs mnemonic and header macro for the same code (10): 23: ROBUST_CHANNEL_RC_LOGGING_ENABLED vs ROBUST_CHANNEL_UNUSED_ERROR_23; 30: ROBUST_CHANNEL_BAD_ADDR_ACCESS vs ROBUST_CHANNEL_UNUSED_ERROR_30; 152: ROBUST_CHANNEL_DLA_SMMU_ERROR vs RESERVED7_ERROR; 153: ROBUST_CHANNEL_DLA_TIMEOUT vs RESERVED8_ERROR; 162: PSHC_REENGAGED vs ISINK_REENGAGED; 163: PSHC_DISENGAGED vs ISINK_DISENGAGED; 164: PSHC_LOW_LIFETIME vs ISINK_LOW_LIFETIME; 165: PSHC_ZERO_LIFETIME vs ISINK_ZERO_LIFETIME; 166: NVLINK_SECURE_CRYPTO_ERR vs NVLINK_SECURE_NVLE_ERROR; 170: NVLINK_SECURE_OTHER vs NVLINK_SECURE_ERROR. Both names are kept (`name_docs`, `name_header`); `name` uses the docs mnemonic when present.
- Docs-catalogue Xid 13 lists two mnemonics (GR_EXCEPTION / GR_ERROR_SW_NOTIFY); both are kept in `name_docs`, joined with " / ". The xlsx and the HTML table give the same two mnemonics for code 13 (xlsx mnemonic mismatches after whitespace normalisation: 0); xlsx immediate-action bucket mismatches: 0.

## 3. Codes present in one source but not another
**In header, not in docs catalogue (14):** 173-186. The docs catalogue stops at code 172; header runs to 186.
**In docs catalogue, not in header (43):** 1-12, 15, 17-18, 24-26, 37-38, 46, 49-57, 66-67, 106-107, 109, 111-118.
**In docs catalogue, not in the r555 archive listing (29):** 144-172.
**In archive listing, not in docs catalogue:** 0 codes.
**In debug guidelines, not in docs catalogue:** 0 codes.
**Docs says Unused, archive gives a failure label (46 codes):** 1-4, 6-7, 9, 12, 16, 18-22, 24, 26-30, 33-36, 42, 47, 56-59, 61, 65, 73, 81, 111-118, 122-125. The sources do not say why they differ (the archive page is the r555 document for older GPUs); both labels are kept.
**Docs description and archive label worded differently (25 codes):** 39-41, 63-64, 94-95, 121, 126-137, 139-143 (for example archive "Reserved" or "Unused" against a docs engine label for 39-41 and 126-135, or reworded labels such as 94 "Contained ECC error" against "Contained memory error"). Not resolved; both kept.
**Debug guidelines give an action for codes the docs catalogue marks Unused:** 61, 123. They carry the status "unused in catalogue; action in debug guidelines" and a note.
**Docs description and trigger text say Unused but the product flags say applicable:** 108. Coded unused, with a note stating the conflict. Code 14 has the same flag pattern but real trigger text, so it stays active.
**Row-level notes (11):** 14: docs description says Unused but Applies-to columns say YES; 45: docs_description and archive_failure_label paraphrased by the cataloguer (source label is 20 words); see source pointer for the original; 54: docs_description and archive_failure_label paraphrased by the cataloguer (source label is 9 words); see source pointer for the original; 61: docs catalogue lists code as unused; debug guidelines give a reset action; 108: source conflict: docs description and trigger text say Unused, but all four applies-to flags are YES; coded unused (2 of 3 source fields say unused); 123: docs catalogue lists code as unused; debug guidelines give a reset action; 152: no listed product (A100/H100/B100/GB200) marked YES, but description is not Unused; 153: no listed product (A100/H100/B100/GB200) marked YES, but description is not Unused; 166: docs_description paraphrased by the cataloguer (source label is 12 words); see source pointer for the original; 171: docs_description paraphrased by the cataloguer (source label is 14 words); see source pointer for the original; 172: docs_description paraphrased by the cataloguer (source label is 14 words); see source pointer for the original.

## 4. Classification distributions
**status**

| value | rows |
|---|---|
| active | 110 |
| unused | 61 |
| active (header only) | 12 |
| unused in catalogue; action in debug guidelines | 2 |
| reserved | 1 |

**subsystem**

| value | rows |
|---|---|
| engine/channel | 45 |
| media/accelerator engine | 33 |
| not documented | 29 |
| firmware/microcontroller | 15 |
| NVLink/C2C interconnect | 15 |
| display | 13 |
| memory/ECC | 13 |
| power/thermal | 8 |
| driver/software | 5 |
| PCIe/bus | 5 |
| security | 4 |
| virtualization | 1 |

**severity_derived**

| value | rows |
|---|---|
| unused | 62 |
| degraded | 49 |
| not documented | 27 |
| informational | 22 |
| fatal | 19 |
| varies by subcode | 7 |

**recovery_action**

| value | rows |
|---|---|
| not applicable (unused) | 62 |
| restart application | 48 |
| none needed | 20 |
| not documented | 19 |
| reset GPU | 18 |
| conditional workflow | 14 |
| check mechanical seating | 1 |
| update firmware/software | 1 |
| restart host (bare metal) | 1 |
| contact support | 1 |
| restart VM | 1 |

## 5. Spot-check log (25 codes)
Method: all four source pages were fetched again on 2026-11-19T06:29:52Z (UTC) into `qa-live/`. Each of the four fresh files was byte-identical to the file used for extraction (identical flags: docs True, archive True, header True, debug True). Codes were then re-read from the fresh files with a second, independent parser (regular expressions on the raw HTML or header text; the extraction used an HTML table parser) and compared with the dataset row: mnemonic, description, applies-to flags, immediate and investigatory bucket, header name and line, archive label, debug row presence. Sample = 15 hand-picked codes (important or unusual) + 10 drawn with seed 20261118. A same-day re-fetch cannot detect later page changes; it checks extraction and transcription.

| Code | Result | What was compared |
|---|---|---|
| 5 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; archive label ok |
| 12 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; archive label ok |
| 13 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 37 ROBUST_CHANNEL_GR_EXCEPTION ok; archive label ok; debug row found: Graphics Engine Exception |
| 21 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 42 ROBUST_CHANNEL_ME_ERROR_SW_METHOD ok; archive label ok |
| 31 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 49 ROBUST_CHANNEL_FIFO_ERROR_MMU_ERR_FLT ok; archive label ok; debug row found: Suspected Hardware Problems |
| 45 | PASS | docs: mnemonic ok, description paraphrased on purpose, source label 20 words, applies ok, buckets ok; header: line 61 ROBUST_CHANNEL_PREEMPTIVE_REMOVAL ok; archive label paraphrased on purpose; debug row found: Robust Channel Preemptive Removal |
| 48 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 63 ROBUST_CHANNEL_GPU_ECC_DBE ok; archive label ok; debug row found: Double Bit ECC Error |
| 57 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; archive label ok |
| 62 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 68 PMU_HALT_ERROR ok; archive label ok; debug row found: PMU Halt Error |
| 63 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 69 INFOROM_PAGE_RETIREMENT_EVENT ok; archive label ok; debug row found: Legacy GPU: ECC page retirement recording event |
| 74 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 80 NVLINK_ERROR ok; archive label ok; debug row found: NVLink Error |
| 79 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 85 ROBUST_CHANNEL_GPU_HAS_FALLEN_OFF_THE_BUS ok; archive label ok; debug row found: GPU has fallen off the bus |
| 88 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 94 ROBUST_CHANNEL_NVDEC3_ERROR ok; archive label ok |
| 94 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 100 ROBUST_CHANNEL_CONTAINED_ERROR ok; archive label ok; debug row found: Contained ECC error occurred (A100 only) |
| 95 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 101 ROBUST_CHANNEL_UNCONTAINED_ERROR ok; archive label ok; debug row found: Uncontained ECC error occurred (A100 only) |
| 97 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 103 ROBUST_CHANNEL_NVDEC6_ERROR ok; archive label ok |
| 107 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; archive label ok |
| 123 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 118 SPI_PMU_RPC_WRITE_FAIL ok; archive label ok; debug row found: SPI PMU RPC write fail |
| 137 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 132 NVLINK_PRIV_ERR ok; archive label ok |
| 152 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 147 RESERVED7_ERROR ok |
| 154 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 149 GPU_RECOVERY_ACTION_CHANGED ok |
| 162 | PASS | docs: mnemonic ok, description ok, applies ok, buckets ok; header: line 157 ISINK_REENGAGED ok |
| 173 | PASS | header: line 168 C2C_FATAL_LINK_FAILURE ok |
| 182 | PASS | header: line 177 PCIE_RESET_FAILURE ok |
| 186 | PASS | header: line 181 COHERENCY_ERROR ok |

Paraphrased labels: for codes 45, 54, 166, 171, 172 the dataset label is deliberately not the source label (source label over 8 words); the spot-check confirms the source label is long and the dataset holds the own-words label. Longest source label kept verbatim: 8 words.

Manual read (by eye, from `qa-live/`, on the first build, before the later revisions to labels, meanings, subsystem values and status values): codes 123, 152, 163, 186 were also read directly in the live header and docs table text and compared with the dataset row (name, applies-to flags, buckets, status, classification); no differences.

## 6. Acceptance-bar checks
| Check | Result |
|---|---|
| CSV rows == JSON rows | 186 == 186 |
| Row count stated in paper.md | 186 (number tokens checked by scripts/check_article.py paper.md) |
| Longest source label kept verbatim | 8 words (limit 8) |
| Every row has a source pointer | 0 rows without |
| Empty classification cells | 0 |
| `meaning` >25 words | 0 |
| `debug_guideline_action` >25 words | 0 |
| `recovery_detail` >25 words | 0 |

## 7. Known QA limits
- The classification rules are applied by script; the rule outputs were reviewed by reading the full 186-row table, but no second reviewer has checked the rule design.
- Spot-check compares the dataset to the sources, not the classification to ground truth: no ground truth exists beyond the sources.
- The meaning field for rows with no explanatory text is a restated label, not an independent description.
