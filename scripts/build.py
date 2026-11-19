"""Step 3: build catalogue from extraction/ files. Run: python3 -I scripts/build.py (from project root)."""
import csv, json, re, collections, os
X="extraction/"
SHA="e6a2e01579fbbd1ca2ed43fef2ee2589e9bd8bd9"
U_DOCS="https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html"
U_ARCH="https://docs.nvidia.com/deploy/xid-errors/archive/index.html"
U_HDR=f"https://github.com/NVIDIA/open-gpu-kernel-modules/blob/{SHA}/src/common/sdk/nvidia/inc/nverror.h"
U_DBG="https://docs.nvidia.com/deploy/gpu-debug-guidelines/gpu-node-triage.html"
ND="not documented"

def rd(p): return list(csv.reader(open(X+p,encoding="utf-8")))
def flat(s): return re.sub(r"\s+"," ",s).strip()

# ---------- load sources ----------
docs={}
for r in rd("docs-catalog-id1.csv")[1:]:
    docs[int(r[2])]=dict(row=int(r[0]),type=r[1],mnem=[m.strip() for m in flat(r[3]).split("/") if m.strip()],desc=flat(r[4]),
        applies=r[5:9],imm=flat(r[9]),inv=flat(r[10]),x154=flat(r[11]),trig=flat(r[12]))
# header: only the contiguous XID block before ROBUST_CHANNEL_LAST_ERROR
hdr={}; hdr_alias=collections.defaultdict(list); hdr_excluded=[]
for r in rd("header-defines.csv")[1:]:
    line,mac,val,alias=int(r[0]),r[1],r[2],r[3]
    if mac=="ROBUST_CHANNEL_LAST_ERROR": hdr_excluded.append((line,mac,val,"range sentinel (= last code), not a code")); continue
    if mac.startswith("ROBUST_CHANNEL_ERROR_RECOVERY_LEVEL_"): hdr_excluded.append((line,mac,val,"recovery-level constant, not an Xid")); continue
    if alias:
        hdr_alias[alias].append((line,mac)); continue
    hdr[int(val)]=dict(line=line,macro=mac)
# archive table (rows: [n, xid, failure, 7 flags] or continuation [n, failure, 7 flags])
arch={}; arch_range=set(); cause_cols=rd("archive-t5.csv")[1][1:]
cur=None
for r in rd("archive-t5.csv")[2:]:
    n=int(r[0]); x=r[1].strip()
    if x.isdigit() or re.match(r"\d+-\s*\d+$",x):
        codes=[int(x)] if x.isdigit() else list(range(*(lambda a:(a[0],a[1]+1))(list(map(int,re.findall(r"\d+",x))))))
        cur=[]
        for c in codes:
            arch[c]=dict(rows=[n],fail=[r[2].strip()],flags=[[cause_cols[i] for i in range(7) if r[3+i].strip()=="X"]],rng=(not x.isdigit()))
            cur.append(c)
    else:  # continuation row for previous Xid(s): failure in r[1], flags in r[2:9]
        for c in cur:
            arch[c]["rows"].append(n); arch[c]["fail"].append(r[1].strip()); arch[c]["flags"].append([cause_cols[i] for i in range(7) if r[2+i].strip()=="X"])
dbg={}
for r in rd("debug-gpu-node-triage-t1.csv")[1:]:
    if r[1].strip().isdigit(): dbg.setdefault(int(r[1]),[]).append(dict(row=int(r[0]),desc=flat(r[2]),action=flat(r[3])))

# ---------- curated text (own words) ----------
DBG_SUMMARY={ # own-words summary of the debug-guidelines action, per code
13:"Check for hardware faults with DCGM and field diagnostics, else debug the application or report an issue.",
31:"Contact the hardware vendor for diagnostics.",
45:"No action; informative only, shows channels hit by another failure. Can appear alone on A100 after an unexpected Fabric Manager shutdown.",
48:"If followed by Xid 63/64, drain the node and reset the GPU. Otherwise run field diagnostics. RMA guidance referenced for excessive errors.",
61:"File a GPU issue report, then reset the GPU that logged the Xid.",
62:"File a GPU issue report, then reset the GPU that logged the Xid.",
63:"With Xid 48: drain and reset. Without it: single-bit origin, keep running until a convenient reboot. A100 row-remap variant also described. RMA guidance referenced.",
64:"Reset the GPU promptly because recording failed; if errors continue, drain and triage. Node reboot for A100 row remapping. RMA guidance referenced.",
74:"Decode the first hex dword bit by bit and follow the per-bit steps given in the guide.",
79:"Drain the node and report a GPU issue.",
92:"Run field diagnostics to collect data. RMA guidance referenced for excessive errors.",
94:"Restart the affected application; other work can continue until the GPU is reset or rebooted for row remapping. RMA guidance referenced.",
95:"With MIG: drain other instances and reset the GPU. Without MIG: reboot the node. RMA guidance referenced.",
123:"File a GPU issue report, then reset the GPU that logged the Xid.",
}
DBG_RMA={48,63,64,92,94,95}
MEANING={ # own-words meaning (<=25 words) for codes whose catalogue entry carries explanatory text
13:"General application fault on the graphics engine, usually an out-of-bounds access or illegal instruction; rarely hardware or driver.",
14:"Test error deliberately injected from user space rather than raised by a real fault.",
31:"MMU page fault, typically an illegal address access by the application; can also come from driver or hardware.",
32:"Fault from the DMA controller on the driver-to-GPU PCIe path, mostly PCIe signal quality rather than application behaviour.",
43:"Software fault in a user application forced it to stop; the GPU itself remains healthy and the driver is rarely at fault.",
54:"Reports that the auxiliary power cable to the GPU board is missing or unplugged; the catalogue adds no further description.",
45:"Driver tore down a running GPU application after it aborted (for example Ctrl-C, GPU reset, SIGKILL) or after another error.",
48:"GPU found an uncorrectable (double-bit) ECC error; clearing it takes resetting the GPU or rebooting the node.",
63:"ECC-related event reporting row-remapper activity (newer GPUs) or dynamic page retirement activity (older GPUs).",
64:"ECC-related failure reporting row-remapper or page-retirement activity could not be recorded.",
74:"NVLink connection to another GPU or NVSwitch has a problem, in the link or the remote device. Reset or reboot clears it.",
79:"Driver could not reach the GPU over PCI Express; often a PCIe link failure, sometimes failing GPU hardware or driver issues.",
93:"Driver could not update the InfoROM because the configured wear limit was exceeded; usually the intended wear-protection feature.",
94:"Memory error contained to one application on a containment-capable GPU; that application must restart, others are unaffected.",
95:"Memory error that spread beyond one application on a containment-capable GPU; reset the GPU before restarting applications.",
110:"Security fault, expected only with hardware failure; recovery is to undo recent hardware changes and cold reset.",
119:"Fault in code on the GPU's GSP core, or a missed reply to a GSP request; a reset or power cycle may be needed.",
120:"Fault in code on the GPU's GSP core, or a missed reply to a GSP request; a reset or power cycle may be needed.",
121:"Corrected errors seen on the C2C link to a Grace CPU; operation is unaffected. A GPU reset at a convenient time retrains the link.",
137:"Fault raised by the remote memory-management unit, such as a disallowed peer-to-peer access across NVLink; usually an application bug.",
140:"Uncorrectable GPU memory errors that blocked the driver from marking pages for offlining or row remapping.",
154:"Companion message stating which recovery step the accompanying Xids need: nothing, P2P drain, drain plus reset, GPU reset, or node reboot.",
155:"Raised when a link is taken down deliberately, for instance on entering the sleep state.",
157:"Resources for repair are exhausted, so no repair was made; work can continue, though the Xid may come back.",
159:"Reported on C2C-linked GPUs; catalogue gives no further detail.",
163:"Power-smoothing circuit has disengaged; a GPU reset is not needed. Thermal events or a timeout can be the cause.",
164:"Power-smoothing circuit is close to end of life and will shortly be switched off; plan for GPU replacement if the feature matters.",
165:"Power-smoothing circuit has reached end of life; the driver switches the feature off and power swings follow.",
166:"Confidential-computing mode only: protected traffic showed up before the link had been set up for encryption.",
168:"Faults detected in the write-protected memory region; expected only when ECC is turned off.",
170:"Confidential-computing mode only: an interrupt was seen.",
171:"Extra detail alongside Xid 48 that tells DRAM and SRAM faults apart.",
172:"Extra detail alongside Xid 48 that tells DRAM and SRAM faults apart.",
}
# Revision 1 (licence): source labels of 9+ words are not copied. The output holds this own-words label instead;
# classification rules still read the source label from extraction/. code -> (own-words label, fields replaced)
LABEL_REWRITE={
45:("Cleanup after an earlier error, typically a double-bit error with several CUDA applications running",("docs_description","archive_failure_label")),
54:("GPU board has no auxiliary power connection",("docs_description","archive_failure_label")),
166:("Confidential-computing traffic arrived before the link was set up for encryption",("docs_description",)),
171:("Companion to Xid 48 with fault detail separating DRAM from SRAM",("docs_description",)),
172:("Companion to Xid 48 with fault detail separating DRAM from SRAM",("docs_description",)),
}
LABEL_MAX_WORDS=8   # longest source label kept verbatim
# Revision 1 (severity ruling): the column is named severity_derived because the value is the cataloguer's derivation,
# not a vendor-stated severity. To revert the name, set SEV_COL="severity".
SEV_COL="severity_derived"
# recovery/severity overrides from explicit documentation text: code -> (recovery, severity, basis)
OVR={
48:("reset GPU","fatal","docs trigger text: GPU reset or node reboot needed to clear; Table 3 workflow WORKFLOW_XID_48"),
74:("reset GPU","fatal","docs trigger text: GPU reset or node reboot needed to clear"),
45:("conditional workflow","informational","docs Table 3 WORKFLOW_XID_45 (solo: restart FM, else ignore); debug guidelines: informative only"),
154:("conditional workflow","informational","docs investigatory bucket: informational only regarding another Xid"),
61:("reset GPU","fatal","debug guidelines Table 1 (docs catalogue lists code as unused)"),
123:("reset GPU","fatal","debug guidelines Table 1 (docs catalogue lists code as unused)"),
163:("conditional workflow","not documented","docs trigger text: no reset required; resolve thermal events, or reload driver/reset if timeout"),
164:("conditional workflow","not documented","docs trigger text: monitor power swings; GPU replacement expected if feature needed"),
165:("conditional workflow","not documented","docs trigger text: replace GPUs if power swings unacceptable"),
168:("conditional workflow","not documented","docs trigger text: enable ECC or retry boot with shifted WPR"),
}
for c in range(144,151): OVR[c]=("conditional workflow","varies by subcode","docs Table 2 'Severity' column, per decoded subcode")
# Revision 2: recovery_basis cites the source of the recovery action, not the severity column
REC_BASIS_OVR={c:"docs immediate-action bucket WORKFLOW_NVLINK5_ERR; Table 3 workflow of that name" for c in range(144,151)}
# Revision 2 status rulings
STATUS_DBG="unused in catalogue; action in debug guidelines"   # 61, 123
STATUS_OVR={108:("unused","docs catalogue description and trigger text both say Unused; only the product flags say applicable")}
RECOV_DETAIL={ # own-words detail, optional
48:"Table 3: solo -> reset GPU; with Xid 63/64 -> drain and reset. SRAM faults: check threshold flag, run field diagnostics, RMA flow if exceeded.",
94:"Restart the affected application; resetting the GPU when convenient is also recommended.",
95:"GPU reset required before applications restart.",
74:"If repeated after reset/reboot, contact hardware vendor.",
79:"Debug guidelines add: drain the node and report a GPU issue.",
110:"Revert recent hardware changes, cold reset; if that fails contact hardware vendor.",
119:"Reset or power cycle if persistent; follow debug guidelines if it recurs after power cycle.",
120:"Reset or power cycle if persistent; follow debug guidelines if it recurs after power cycle.",
140:"Reset GPU; if it persists contact hardware vendor.",
121:"Optional GPU reset at a service window to retrain the link.",
93:"Clear the InfoROM erase limit with the vendor flashing tool; report to NVIDIA if that does not help.",
}
BUCKET={"IGNORE":"none needed","RESTART_APP":"restart application","RESTART_VM":"restart VM","RESET_GPU":"reset GPU",
 "RESTART_BM":"restart host (bare metal)","CONTACT_SUPPORT":"contact support","UPDATE_SWFW":"update firmware/software",
 "CHECK_MECHANICALS":"check mechanical seating","XID_154":"conditional workflow","CHECK_UVM":"conditional workflow"}
def bucket_to_action(b):
    if not b: return ND
    if b.startswith("WORKFLOW_"): return "conditional workflow"
    return BUCKET.get(b,ND)
SEV_FROM_ACTION={"reset GPU":"fatal","restart host (bare metal)":"fatal","drain-and-reset":"fatal",
 "restart application":"degraded","restart VM":"degraded","none needed":"informational"}

# ---------- subsystem rules ----------
# 1) description rules: applied to docs description + archive labels (text actually printed by NVIDIA). 2) name-token rules.
DESC_RULES=[
 (r"micro-controller|firmware","firmware/microcontroller"),
 (r"ECC|memory error|memory remapping|video memory","memory/ECC"),
 (r"[Pp]ower","power/thermal"),
 (r"\bCC\b|confidential","security"),
 (r"^Display|Display Engine|Display (Bundle|Pipeline|Core|Window|Cursor)|Display Pixel Pipeline|DP Link","display"),
 (r"[Vv]ideo processor|Mpeg|Motion Estimation","media/accelerator engine"),
 (r"semaphore","engine/channel"),
 (r"Illegal access by driver|SMBPBI","driver/software"),
]
NAME_RULES=[
 (r"CHANNEL_RETIREMENT|FIFO|(^|_)GR_|PBDMA|(^|_)CE\d+|CTXSW|RESETCHANNEL|PREEMPTIVE","engine/channel"),
 (r"ECC|SBE|DBE|DRAM|SRAM|FB_MEMORY|BANK_REMAPPING|MEMORY_SUBSYSTEM|REDUCED_GPU_MEMORY|CONTAINED_ERROR","memory/ECC"),
 (r"PCIE|FALLEN_OFF_THE_BUS|BUS_MASTER","PCIe/bus"),
 (r"NVLINK|C2C|ALI_TRAINING","NVLink/C2C interconnect"),
 (r"PSHC|ISINK|PWR|TEMP|THERMAL","power/thermal"),
 (r"^VGPU","virtualization"),
 (r"KEY_ROTATION|SEC_FAULT","security"),
 (r"INFOROM|PMU","firmware/microcontroller"),
 (r"NVDEC|NVENC|NVJPG|OFA|_VP_|VP2|MPEG|_ME_|MSVLD|MSPDEC|MSPPP|VIC_|BSP|DLA","media/accelerator engine"),
 (r"DISP|VBLANK|SCANLINE|VGA","display"),
 (r"FAKE_ERROR|TELEMETRY|RECOVERY_ACTION_CHANGED|SMBPBI","driver/software"),
]
SUB_OVR={
 119:("firmware/microcontroller","docs trigger text: error in code running on the GSP core"),
 120:("firmware/microcontroller","docs trigger text: error in code running on the GSP core"),
 183:("firmware/microcontroller","name token GSP (docs trigger text for 119/120 describes GSP as an on-GPU core)"),
 159:("NVLink/C2C interconnect","docs trigger text: seen on C2C link-connected GPUs"),
 156:(ND,"name 'resource retirement' is not decoded by the sources"),157:(ND,"name 'resource retirement' is not decoded by the sources"),
 # Revision 1 downgrades: name tokens that no source decodes, or that name no subsystem
 160:(ND,"name 'channel retirement' is not decoded by the sources (kind of channel not stated)"),
 161:(ND,"name 'channel retirement' is not decoded by the sources (kind of channel not stated)"),
 177:(ND,"name 'bank remapping' is not decoded by the sources (header name only)"),
 136:(ND,"name token ALI is not decoded by the sources; the label does not say which link"),
 138:(ND,"name token DLA is not decoded by the sources"),152:(ND,"name token DLA is not decoded by the sources"),153:(ND,"name token DLA is not decoded by the sources"),
 87:(ND,"name 'telemetry driver report' names no subsystem; code unused"),
 154:(ND,"companion message about other Xids; the name gives no subsystem"),
 45:("engine/channel","name ROBUST_CHANNEL_PREEMPTIVE_REMOVAL; debug guidelines Table 1 describes it as marking channels hit by another failure"),
}
def pname(c):
    d=docs.get(c)
    if d and d["mnem"]: return d["mnem"][0]
    return hdr[c]["macro"]
def norm(s): return re.sub(r"[^A-Z0-9]","",s.upper())

rows=[]
codes=sorted(set(docs)|set(hdr)|set(arch)|set(dbg))
for c in codes:
    d=docs.get(c); h=hdr.get(c); a=arch.get(c); g=dbg.get(c)
    name_docs=" / ".join(d["mnem"]) if d else ""
    name_hdr=h["macro"] if h else ""
    aliases="; ".join(m for _,m in hdr_alias.get(name_hdr,[]))
    primary=pname(c)
    name_conflict=""
    if d and h and norm(h["macro"]) not in [norm(m) for m in d["mnem"]] and not any(norm(m)==norm(x) for m in d["mnem"] for _,x in hdr_alias.get(h["macro"],[])):
        name_conflict="docs mnemonic and header macro differ"
    # status
    notes=[]
    if d:
        all_no=all(x=="NO" for x in d["applies"])
        if d["desc"]=="Unused" and all_no: status="unused"
        else:
            status="active"
            if d["desc"]=="Unused": notes.append("docs description says Unused but Applies-to columns say YES")
            if all_no: notes.append("no listed product (A100/H100/B100/GB200) marked YES, but description is not Unused")
    else:
        status="unused" if re.search(r"UNUSED",name_hdr) else ("reserved" if re.search(r"RESERVED",name_hdr) else "active")
        if status=="active": status="active (header only)"
    if c in STATUS_OVR:
        status=STATUS_OVR[c][0]
        notes=[n for n in notes if not n.startswith("docs description says Unused but")]
        notes.append("source conflict: docs description and trigger text say Unused, but all four applies-to flags are YES; coded unused (2 of 3 source fields say unused)")
    if c in (61,123) and g:
        status=STATUS_DBG
        notes.append("docs catalogue lists code as unused; debug guidelines give a reset action")
    # recovery
    imm=d["imm"] if d else ""
    rec_docs=bucket_to_action(imm) if d else ND
    basis_rec="docs immediate-action bucket "+imm if d and imm else ("none in sources" )
    rec=rec_docs
    if status=="unused" and c not in OVR: rec="not applicable (unused)"; basis_rec="code marked unused in docs catalogue (bucket %s is the default)"%imm if d else "header name marks code unused"
    if c in STATUS_OVR: basis_rec="code marked unused (docs description and trigger text say Unused); docs bucket %s not used, see notes"%imm
    sev=None; sev_basis=""
    if c in OVR: rec,sev,sev_basis=OVR[c]; basis_rec=REC_BASIS_OVR.get(c,sev_basis)
    if sev is None:
        if status=="unused": sev,sev_basis="unused","docs catalogue marks code unused" if d else "header macro name marks code unused"
        elif rec in SEV_FROM_ACTION: sev=SEV_FROM_ACTION[rec]; sev_basis="derived from documented recovery action: "+rec
        else: sev=ND; sev_basis="no documented behaviour maps to fatal/degraded/informational"
    if status=="reserved": sev,sev_basis="unused","header macro name marks code reserved"; rec="not applicable (unused)"; basis_rec="header macro name marks code reserved"
    # subsystem
    text=" ".join([d["desc"] if d else ""]+(a["fail"] if a else []))
    if c in SUB_OVR: sub,sub_basis=SUB_OVR[c]
    else:
        sub=ND; sub_basis="no decodable subsystem token in name or description"
        for pat,sname in DESC_RULES:
            if re.search(pat,text): sub=sname; sub_basis="description text '%s'"%re.search(pat,text).group(0); break
        else:
            for pat,sname in NAME_RULES:
                if re.search(pat,primary) or (h and re.search(pat,h["macro"])): sub=sname; sub_basis="name token '%s'"%(re.search(pat,primary) or re.search(pat,h["macro"])).group(0).strip("_"); break
    # meaning
    if c in MEANING: meaning=MEANING[c]
    elif d and d["desc"]!="Unused": meaning="Catalogue label: "+d["desc"].replace("(newer drivers)","").strip()+"; no further description."
    elif d: meaning="Listed as unused in the docs catalogue; no active condition described."
    elif a and any(f!="Unused" and f!="Reserved" for f in a["fail"]): meaning="Older-GPU listing label: "+"; ".join(a["fail"])+"; header gives name only."
    else: meaning="Header gives the macro name only; no description in the sources."
    # labels: copy short source labels; replace long ones with the own-words label
    out_desc=d["desc"] if d else ""; out_arch=" | ".join(a["fail"]) if a else ""
    if c in LABEL_REWRITE:
        own,fields=LABEL_REWRITE[c]
        if "docs_description" in fields: n_src=len(out_desc.split()); out_desc=own
        if "archive_failure_label" in fields: out_arch=own
        notes.append("%s paraphrased by the cataloguer (source label is %d words); see source pointer for the original"%(" and ".join(fields),n_src))
    assert all(len(x.split())<=LABEL_MAX_WORDS for x in ([d["desc"]] if d and c not in LABEL_REWRITE else [])), c
    assert all(len(x.split())<=LABEL_MAX_WORDS for x in (a["fail"] if a and not (c in LABEL_REWRITE and "archive_failure_label" in LABEL_REWRITE[c][1]) else [])), c
    # source pointers
    src=[]
    if d: src.append(f"{U_DOCS}#id1 (Table 1, row Code={c})")
    if h: src.append(f"{U_HDR}#L{h['line']}")
    if a: src.append(f"{U_ARCH}#xid-error-listing (r555 table, Xid {c})")
    if g: src.append(f"{U_DBG} (Table 1, Xid {c})")
    row=dict(
      code=c,code_type="XID",name=primary,
      name_docs=name_docs,name_header=name_hdr,header_aliases=aliases,name_conflict=name_conflict,
      status=status,meaning=meaning,
      docs_description=out_desc,
      applies_a100=(d["applies"][0] if d else ND),applies_h100=(d["applies"][1] if d else ND),
      applies_b100=(d["applies"][2] if d else ND),applies_gb200=(d["applies"][3] if d else ND),
      docs_immediate_bucket=imm,docs_investigatory_bucket=(d["inv"] if d else ""),docs_xid154_linkage=(d["x154"] if d else ""),
      archive_failure_label=out_arch,
      archive_cause_flags=(" | ".join(";".join(f) if f else "-" for f in a["flags"]) if a else ""),
      debug_guideline_action=(DBG_SUMMARY[c] if g else ""),rma_guidance_referenced=("yes" if c in DBG_RMA else "no"),
      subsystem=sub,subsystem_basis=sub_basis,
      **{SEV_COL:sev},severity_basis=sev_basis,
      recovery_action=rec,recovery_basis=basis_rec,recovery_detail=RECOV_DETAIL.get(c,""),
      in_docs_catalogue="yes" if d else "no",in_header="yes" if h else "no",
      in_archive_listing="yes" if a else "no",in_debug_guidelines="yes" if g else "no",
      source_count=sum(bool(x) for x in (d,h,a,g)),
      source_pointers=" ; ".join(src),notes="; ".join(notes))
    rows.append(row)
if __name__=="__main__":
    cols=list(rows[0].keys())
    with open("xid-catalogue.csv","w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols,lineterminator="\n"); w.writeheader(); w.writerows(rows)
    json.dump(dict(metadata=dict(title="NVIDIA XID error code catalogue",version="v1",built="2026-11-18",row_count=len(rows),
        header_commit=SHA,columns=cols),records=rows),open("xid-catalogue.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
    json.dump(dict(hdr_excluded=hdr_excluded,hdr_alias={k:v for k,v in hdr_alias.items()}),open("extraction/build-aux.json","w"),indent=1)
    print(len(rows),"rows"); 
    for k in("status",SEV_COL,"recovery_action","subsystem"): print(k,collections.Counter(r[k] for r in rows).most_common())
