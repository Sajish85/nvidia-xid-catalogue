"""Every number token in the article must appear in the dataset/QA/SOURCES/CLASSIFICATION files. Run from project root."""
import re,json,sys
art=open(sys.argv[1] if len(sys.argv)>1 else "paper.md").read()
corpus=" ".join(open(f).read() for f in ["QA.md","SOURCES.md","CLASSIFICATION.md","DATA-DICTIONARY.md","xid-catalogue.csv"])
tokens=set(re.findall(r"(?<![\w.])\d+(?:[.,]\d+)*(?![\w])",corpus))
R=json.load(open("xid-catalogue.json"))["records"]
nums=re.findall(r"(?<![\w.#])\d+(?![\w])",re.sub(r"[a-f0-9]{12}","",art))
bad=sorted({n for n in nums if n not in tokens},key=int)
print("numbers in draft:",len(nums),"| not traceable:",bad)
n=len(R)
print("row count claims:",[int(m) for m in re.findall(r"\b(\d+) (?:rows|codes)",art) if int(m)==n][:3],"dataset rows",n)
