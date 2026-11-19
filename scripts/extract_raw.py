"""Step 1: raw extraction per source, no cleaning. Run: python3 -I scripts/extract_raw.py"""
import re, json, csv, html, sys
from html.parser import HTMLParser
R="raw/"; O="extraction/"
import os; os.makedirs(O,exist_ok=True)

class T(HTMLParser):
    def __init__(s): super().__init__(); s.tables=[]; s.cur=None; s.row=None; s.cell=None; s.cap=None; s.incap=False
    def handle_starttag(s,t,a):
        if t=="table": s.cur={"id":dict(a).get("id"),"caption":"","rows":[]}
        elif t=="caption": s.incap=True
        elif t=="tr" and s.cur is not None: s.row=[]
        elif t in("td","th") and s.row is not None: s.cell=[]
        elif t=="br" and s.cell is not None: s.cell.append("\n")
    def handle_endtag(s,t):
        if t=="table": s.tables.append(s.cur); s.cur=None
        elif t=="caption": s.incap=False
        elif t=="tr" and s.row is not None: s.cur["rows"].append(s.row); s.row=None
        elif t in("td","th") and s.cell is not None: s.row.append("".join(s.cell).strip()); s.cell=None
        elif t=="p" and s.cell is not None: s.cell.append("\n")
    def handle_data(s,d):
        if s.incap and s.cur is not None: s.cur["caption"]+=d
        elif s.cell is not None: s.cell.append(d)

def tables(p):
    h=T(); h.feed(open(p,encoding="utf-8").read()); return h.tables

# Source 1: docs catalogue (current) tables
for t in tables(R+"docs/analyzing-xid-catalog.html"):
    n=t["id"]
    with open(f"{O}docs-catalog-{n}.csv","w",newline="") as f:
        w=csv.writer(f); 
        for i,r in enumerate(t["rows"]): w.writerow([i+1]+[re.sub(r"[ \t]*\n[ \t\n]*","\n",c) for c in r])
    print("docs",n,t["caption"].strip()[:40],len(t["rows"]),"rows")
# Archive page tables
for t in tables(R+"archive/index.html"):
    n=t["id"] or "t%d"%len(os.listdir(O))
    with open(f"{O}archive-{n}.csv","w",newline="") as f:
        w=csv.writer(f)
        for i,r in enumerate(t["rows"]): w.writerow([i+1]+[re.sub(r"\s+"," ",c) for c in r])
    print("archive",n,len(t["rows"]),"rows")
# Source 2: header, every #define with its line number
rows=[]
for i,l in enumerate(open(R+"header/nverror.h"),1):
    m=re.match(r"#define\s+(\w+)\s+\((\d+)\)\s*$",l)
    a=re.match(r"#define\s+(\w+)\s+([A-Z_0-9]+)\s*$",l)
    if m: rows.append([i,m.group(1),m.group(2),""])
    elif a: rows.append([i,a.group(1),"",a.group(2)])
with open(O+"header-defines.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["line","macro","value","alias_of"]); w.writerows(rows)
print("header defines",len(rows))

# Source 3: debug guidelines tables (every page)
for p in ["overview","initial-incident-report","gpu-node-triage","best-practices"]:
    for k,t in enumerate(tables(R+f"debug/{p}.html")):
        fn=f"{O}debug-{p}-t{k+1}.csv"
        with open(fn,"w",newline="") as f:
            w=csv.writer(f)
            for i,r in enumerate(t["rows"]): w.writerow([i+1]+[re.sub(r"[ \t]*\n[ \t\n]*","\n",c) for c in r])
        print("debug",p,k+1,t["caption"].strip()[:50].replace("\n"," "),len(t["rows"]),"rows")
