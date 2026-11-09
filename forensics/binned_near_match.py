import json
import re
import math
from pathlib import Path
from collections import Counter, defaultdict

DATA = Path("Data/redacted.jsonl")
OUT = Path("/Users/id19/scratchpad/binned_near_match_candidates.jsonl")
REPORT = Path("/Users/id19/scratchpad/binned_near_match_report.md")
MARKERS = set()

def textual_signature(text):
    t = text.strip()
    if not t or len(t) < 4:
        return None
    # stabilize obvious placeholder numeric counters
    norm = re.sub(r"\[[^\]]*\]", "PH", t.lower())
    norm = re.sub(r"(?<!\d)\d{3,}(?!\d)", "#", norm)
    key = (len(norm) // 10) * 10, frozenset(re.findall(r"zz[A-Za-z0-9_]{4,}", t))
    return key

def lev(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    if abs(len(a)-len(b)) > 4:
        return 9999
    prev = list(range(len(b)+1))
    for i,ch in enumerate(a,1):
        cur=[i]
        for j,k in enumerate(b,1):
            cost=0 if ch==k else 1
            cur.append(min(prev[j]+1, cur[j-1]+1, prev[j-1]+cost))
        prev=cur
    return prev[-1]

def main():
    rows=[]
    with DATA.open() as f:
        for line in f:
            if not line.strip():
                continue
            r=json.loads(line)
            r["_sig"]=textual_signature(r.get("text",""))
            if r["_sig"] is None:
                continue
            rows.append(r)
    buckets=defaultdict(list)
    for r in rows:
        buckets[r["_sig"]].append(r)
    max_bucket_pairs = 250
    total_candidates=0
    candidate_out=open(OUT,'w',encoding='utf-8')
    families=Counter()
    for sig, members in buckets.items():
        families[len(members)] += 1
        if len(members) > 35:
            continue
        # candidate pair cap on each family-bucket
        pairs=0
        for i in range(len(members)):
            a=members[i]["text"] if "text" in members[i] else ""
            for j in range(i+1,len(members)):
                b=members[j]["text"]
                d=lev(a,b)
                if d <= max(1, len(a)//50):
                    total_candidates+=1
                    payload={"a":members[i]["id"],"b":members[j]["id"],"distance":d,"length_bucket":sig[0],"family_id":sorted(sig[1]),"exact":a==b}
                    candidate_out.write(json.dumps(payload,ensure_ascii=False)+"\n")
                pairs+=1
                if pairs > max_bucket_pairs:
                    break
    candidate_out.close()
    report=f"""# Binned near-match candidates

Rows considered: {len(rows)}
Max bucket size allowed: 35
Candidate pairs emitted: {total_candidates}
Families bucket sizes: {families.most_common(10)}
Output: {OUT}
"""
    REPORT.write_text(report,encoding='utf-8')
    print("rows",len(rows),"candidates",total_candidates,"output",OUT)
    print("bucket sizes top",families.most_common(5))

if __name__=="__main__":
    main()
