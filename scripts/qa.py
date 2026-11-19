"""Step 4: QA. Fresh live re-fetch + independent re-parse for spot checks; cross-source counts. Run from project root."""
import csv, json, re, random, subprocess, zipfile, html, collections, sys, os, datetime
sys.path.insert(0,"scripts")
import build   # for LABEL_REWRITE (labels deliberately paraphrased) and SEV_COL
PARA=build.LABEL_REWRITE
R=json.load(open("xid-catalogue.json"))["records"]; by={r["code"]:r for r in R}
out={}
# --- live re-fetch into qa-live/ (separate from raw/) ---
URLS={"docs":"https://docs.nvidia.com/deploy/xid-errors/analyzing-xid-catalog.html",
 "arch":"https://docs.nvidia.com/deploy/xid-errors/archive/index.html",
 "hdr":"https://raw.githubusercontent.com/NVIDIA/open-gpu-kernel-modules/main/src/common/sdk/nvidia/inc/nverror.h",
 "dbg":"https://docs.nvidia.com/deploy/gpu-debug-guidelines/gpu-node-triage.html"}
stamp=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"); out["refetch_utc"]=stamp
for k,u in URLS.items():
    p=f"qa-live/{k}.txt"
    code=subprocess.run(["curl","-sL","-m","90","-w","%{http_code}","-o",p,u],capture_output=True,text=True).stdout
    out[f"http_{k}"]=code
    out[f"identical_to_raw_{k}"]= subprocess.run(["cmp","-s",p,{"docs":"raw/docs/analyzing-xid-catalog.html","arch":"raw/archive/index.html","hdr":"raw/header/nverror.h","dbg":"raw/debug/gpu-node-triage.html"}[k]]).returncode==0
live={k:open(f"qa-live/{k}.txt",encoding="utf-8").read() for k in URLS}
def tx(s): return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",s))).strip()
# independent parsers (regex based, different from HTMLParser extraction)
def live_docs(c):
    m=re.search(r'<tr class="row-\w+"><th class="stub"><p>XID</p></th>\s*<td><p>%d</p></td>(.*?)</tr>'%c,live["docs"],re.S)
    if not m: return None
    cells=[tx(x) for x in re.findall(r"<td>(.*?)</td>",m.group(1),re.S)]
    return cells  # mnemonic, desc, A100,H100,B100,GB200, imm, inv, x154, trig
def live_hdr(c):
    for i,l in enumerate(live["hdr"].splitlines(),1):
        m=re.match(r"#define\s+(\w+)\s+\(%d\)\s*$"%c,l)
        if m and not m.group(1).startswith("ROBUST_CHANNEL_LAST") : return i,m.group(1)
def live_arch_label(c):
    t=live["arch"]; i=t.find("<tbody>",t.find("Failure"))
    for m in re.finditer(r"<tr[^>]*>(.*?)</tr>",t,re.S):
        cells=[tx(x) for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>",m.group(1),re.S)]
        if cells and cells[0]==str(c): return cells[1]
def live_dbg(c):
    for m in re.finditer(r"<tr[^>]*>(.*?)</tr>",live["dbg"],re.S):
        cells=[tx(x) for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>",m.group(1),re.S)]
        if cells and cells[0]==str(c): return cells[1]
random.seed(20261118)
must=[13,31,45,48,63,74,79,94,95,154,162,173,186,152,123]   # important/unusual codes
pool=[c for c in by if c not in must]
sample=sorted(must+random.sample(pool,10))
log=[]; fails=0
for c in sample:
    r=by[c]; res=[]; ok=True
    if r["in_docs_catalogue"]=="yes":
        d=live_docs(c)
        if d is None: ok=False; res.append("docs row NOT FOUND live")
        else:
            m=[x.strip() for x in re.split(r"\s*/\s*",d[0])]
            c1= r["name_docs"].replace(" / "," / ") and all(x in r["name_docs"] for x in m)
            para_d= c in PARA and "docs_description" in PARA[c][1]
            c2= (r["docs_description"]==PARA[c][0] and len(d[1].split())>build.LABEL_MAX_WORDS) if para_d else d[1]==r["docs_description"]; c3=[d[2],d[3],d[4],d[5]]==[r["applies_a100"],r["applies_h100"],r["applies_b100"],r["applies_gb200"]]
            c4= d[6]==r["docs_immediate_bucket"] and d[7]==r["docs_investigatory_bucket"].replace("\n"," ")
            ok&=c1 and c2 and c3 and c4; res.append(f"docs: mnemonic {'ok' if c1 else 'DIFF'}, description {('paraphrased on purpose, source label %d words'%len(d[1].split()) if para_d else 'ok') if c2 else 'DIFF'}, applies {'ok' if c3 else 'DIFF'}, buckets {'ok' if c4 else 'DIFF('+d[6]+'|'+d[7]+')'}")
    if r["in_header"]=="yes":
        h=live_hdr(c)
        okh= h and h[1]==r["name_header"] and r["source_pointers"].count(f"#L{h[0]}")==1
        ok&=bool(okh); res.append(f"header: line {h[0] if h else None} {h[1] if h else None} {'ok' if okh else 'DIFF'}")
    if r["in_archive_listing"]=="yes":
        a=live_arch_label(c)
        if a is None and r["archive_failure_label"]=="Reserved": res.append("archive: in a range row (not independently matched by single-code regex)"); 
        else:
            para_a= c in PARA and "archive_failure_label" in PARA[c][1]
            oka=a is not None and ((r["archive_failure_label"]==PARA[c][0] and len(a.split())>build.LABEL_MAX_WORDS) if para_a else a in r["archive_failure_label"]); ok&=oka; res.append(f"archive label {('paraphrased on purpose' if para_a else 'ok') if oka else 'DIFF ('+str(a)+')'}")
    if r["in_debug_guidelines"]=="yes":
        g=live_dbg(c); okg=g is not None; ok&=okg; res.append(f"debug row {'found' if okg else 'MISSING'}: {g}")
    fails+= (not ok); log.append((c,ok,"; ".join(res)))
out["spot_total"]=len(sample); out["spot_fail"]=fails; out["spot_log"]=log
# --- xlsx cross-check of docs catalogue ---
z=zipfile.ZipFile("raw/docs/Xid-Catalog.xlsx")
ss=[tx(re.sub(r"<rPh.*?</rPh>","",x)) for x in re.findall(r"<si>(.*?)</si>",z.read("xl/sharedStrings.xml").decode(),re.S)]
sh=z.read("xl/worksheets/sheet1.xml").decode(); xl={}
for row in re.finditer(r"<row [^>]*>(.*?)</row>",sh,re.S):
    cells={}
    for c in re.finditer(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(.*?)</c>)',row.group(1),re.S):
        v=re.search(r"<v>(.*?)</v>",c.group(3) or "")
        if v: cells[c.group(1)]=ss[int(v.group(1))] if 't="s"' in c.group(2) else v.group(1)
    if cells.get("A")=="XID" and str(cells.get("B","")).replace(".0","").isdigit(): xl[int(float(cells["B"]))]=cells
out["xlsx_xid_rows"]=len(xl)
out["xlsx_codes_equal_html"]= set(xl)==set(c for c,r in by.items() if r["in_docs_catalogue"]=="yes")
out["xlsx_mnemonic_mismatch"]=[c for c in xl if re.sub(r"\s+","",xl[c].get("C",""))!=re.sub(r"\s+","",by[c]["name_docs"].replace(" / ","/"))]
out["xlsx_imm_bucket_mismatch"]=[c for c in xl if re.sub(r"\s+"," ",xl[c].get("I","")).strip()!=by[c]["docs_immediate_bucket"]]
# --- cross source ---
S={k:{c for c,r in by.items() if r[f]=="yes"} for k,f in dict(docs="in_docs_catalogue",header="in_header",archive="in_archive_listing",debug="in_debug_guidelines").items()}
out["counts"]={k:len(v) for k,v in S.items()}; out["union"]=len(R)
out["header_only"]=sorted(S["header"]-S["docs"]); out["docs_only"]=sorted(S["docs"]-S["header"])
out["archive_not_docs"]=sorted(S["archive"]-S["docs"]); out["docs_not_archive"]=sorted(S["docs"]-S["archive"])
out["debug_not_docs"]=sorted(S["debug"]-S["docs"])
out["both_docs_header"]=len(S["docs"]&S["header"])
out["name_conflicts"]=[(c,by[c]["name_docs"].split(" / ")[0],by[c]["name_header"]) for c in sorted(by) if by[c]["name_conflict"]]
out["source_count_dist"]=dict(collections.Counter(r["source_count"] for r in R))
out["status"]=dict(collections.Counter(r["status"] for r in R))
for k in ("subsystem",build.SEV_COL,"recovery_action"): out[k]=dict(collections.Counter(r[k] for r in R).most_common())
# --- acceptance checks ---
csvrows=list(csv.DictReader(open("xid-catalogue.csv",encoding="utf-8")))
out["csv_rows"]=len(csvrows); out["json_rows"]=len(R)
out["csv_json_equal"]=all(all(str(r[k])==x[k] for k in x) for r,x in zip(R,csvrows))
out["empty_class_cells"]=[(r["code"],k) for r in R for k in("subsystem",build.SEV_COL,"recovery_action") if not str(r[k]).strip()]
out["no_pointer"]=[r["code"] for r in R if not r["source_pointers"]]
out["meaning_over_25_words"]=[(r["code"],len(r["meaning"].split())) for r in R if len(r["meaning"].split())>25]
out["debug_summary_over_25_words"]=[(r["code"],len(r["debug_guideline_action"].split())) for r in R if len(r["debug_guideline_action"].split())>25]
out["recov_detail_over_25_words"]=[(r["code"],len(r["recovery_detail"].split())) for r in R if len(r["recovery_detail"].split())>25]
out["docs_unused_but_archive_has_label"]=[r["code"] for r in R if r["docs_description"]=="Unused" and r["archive_failure_label"] and not set(x.strip() for x in r["archive_failure_label"].split("|"))<= {"Unused","Reserved"}]
out["docs_desc_vs_archive_differ"]=[r["code"] for r in R if r["docs_description"] not in("","Unused") and r["archive_failure_label"] and r["docs_description"].split("\n")[0] not in r["archive_failure_label"]]
out["label_words_max"]=max([len(x.split()) for r in R for x in [r["docs_description"]]+r["archive_failure_label"].split(" | ") if r["code"] not in PARA]+[0])
out["paraphrased_labels"]=sorted(PARA)
out["notes_rows"]=[(r["code"],r["notes"]) for r in R if r["notes"]]
out["rma_flag_codes"]=[r["code"] for r in R if r["rma_guidance_referenced"]=="yes"]
out["dupe_codes"]=len(R)-len({r["code"] for r in R})
aux=json.load(open("extraction/build-aux.json")); out["hdr_excluded"]=aux["hdr_excluded"]; out["hdr_alias"]=aux["hdr_alias"]
json.dump(out,open("qa-results.json","w"),indent=1,default=list)
print(json.dumps({k:v for k,v in out.items() if k not in("spot_log",)},default=list)[:6000])
