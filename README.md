# NVIDIA Xid error code catalogue

A table of 186 NVIDIA GPU Xid error codes (numbered 1 to 186), one row per code, joined from four public NVIDIA sources: the Xid catalogue page and spreadsheet for Ampere and newer GPUs, the archived Xid page for older GPUs (r555), the header `nverror.h` (open GPU kernel modules, commit e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9) and the GPU debug guidelines "GPU Node Triage" page. Sources were retrieved on 2026-11-18. Each row has the names the sources use, applicability flags and resolution buckets, a short own-words summary, three classification fields (subsystem, derived severity, recovery action) with a stated basis for each value, and pointers to the source locations. Where the sources give no support, a field holds "not documented". SXID (NVSwitch) codes are not included.

## Files

| File | Content |
|---|---|
| `xid-catalogue.csv` | The dataset, 186 rows, 35 columns |
| `xid-catalogue.json` | Same content as the CSV, plus a metadata object |
| `DATA-DICTIONARY.md` | Column definitions |
| `SOURCES.md` | Source list, retrieval details, rights observations |
| `CLASSIFICATION.md` | Rules behind the status, recovery action, severity and subsystem fields |
| `QA.md` | Counts, cross-source checks, spot-check log |
| `paper.md` | Data article describing the dataset |
| `scripts/` | Build, QA and documentation scripts (`extract_raw.py`, `build.py`, `qa.py`, `docs_gen.py`, `check_article.py`) |
| `LICENSE` | CC BY 4.0 full text |

The scripts read the unmodified source pages, which are not redistributed here. Fetch them from the URLs in `SOURCES.md` to rebuild.

## How the classification was derived

Recovery action comes from the documentation's immediate-action bucket, overridden by explicit documentation text for named codes. Derived severity follows from the recovery action and is the cataloguer's reading, not a severity stated by NVIDIA. Subsystem comes from phrases in the documentation, then from tokens in the code name, and stays "not documented" where the sources do not support a value. `CLASSIFICATION.md` gives the rules and the counts.

## Rights note

Code numbers, names, applicability flags and bucket identifiers are reproduced as facts from the cited sources; the header nverror.h is distributed by NVIDIA under an MIT-style permission notice, which accompanies the dataset. Descriptive text in the dataset is the author's own wording, apart from short labels of at most 8 words that serve as the sources' names for a condition. The NVIDIA documentation pages are copyright NVIDIA Corporation and state that reproduction requires NVIDIA's prior written approval; no such approval has been sought or given, and the dataset is not endorsed by NVIDIA.

## Notice for nverror.h

The names of the 143 code macros in `xid-catalogue.csv` and `xid-catalogue.json` come from `nverror.h`, which carries this notice:

```
Copyright (c) 1993-2026, NVIDIA CORPORATION. All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
```

## Licence

The dataset is released under the Creative Commons Attribution 4.0 International licence (CC BY 4.0); see `LICENSE`. This applies to the cataloguer's own contribution. It does not change the terms of the NVIDIA material described in the rights note and the notice above.

## Author

Sajish Krishnan, Independent researcher

## Citation

Krishnan, S. (2026). NVIDIA Xid error code catalogue (v1) [Data set]. DOI: [DOI to be assigned on deposit]
