"""Small standard-library CLI helpers for profile and media maintenance."""
from __future__ import annotations
import argparse, csv, difflib, hashlib, json, os, re, sys
from datetime import datetime, timezone
from pathlib import Path

def read_text(p): return Path(p).read_text(encoding="utf-8", errors="replace")
def slugify(s): return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")
def word_count(s): return {"words":len(re.findall(r"\b[\w'-]+\b",s)), "characters":len(s), "lines":len(s.splitlines())}
def safe_name(s): return re.sub(r"[^A-Za-z0-9._-]+", "-", s).strip(".-") or "untitled"
def json_load(p): return json.loads(read_text(p))
def tree(path):
    base=Path(path); rows=[]
    for p in sorted(base.rglob("*")):
        if any(x in {".git","node_modules",".venv","venv","__pycache__"} for x in p.parts): continue
        rows.append(("DIR " if p.is_dir() else "FILE ") + str(p))
    return "\n".join(rows)
def media_manifest(path):
    exts={".png",".jpg",".jpeg",".webp",".gif",".mp4",".webm",".svg",".mp3",".wav",".ogg"}
    return [{"path":str(p),"bytes":p.stat().st_size,"extension":p.suffix.lower()} for p in sorted(Path(path).rglob("*")) if p.is_file() and p.suffix.lower() in exts]
def duplicate_files(path):
    groups={}
    for p in Path(path).rglob("*"):
        if p.is_file() and not any(x in {".git","node_modules",".venv","venv","__pycache__"} for x in p.parts):
            try: digest=hashlib.sha256(p.read_bytes()).hexdigest()
            except OSError: continue
            groups.setdefault(digest,[]).append(str(p))
    return [v for v in groups.values() if len(v)>1]
def find_large(path, limit):
    return [{"path":str(p),"bytes":p.stat().st_size} for p in Path(path).rglob("*") if p.is_file() and p.stat().st_size >= limit and not any(x in {".git","node_modules",".venv","venv"} for x in p.parts)]
def scan_secrets(path):
    patterns=[("private-key",re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),("token-like",re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,})\b"))]
    hits=[]
    for p in Path(path).rglob("*"):
        if not p.is_file() or any(x in {".git","node_modules",".venv","venv","__pycache__"} for x in p.parts): continue
        try: lines=read_text(p).splitlines()
        except OSError: continue
        for n,line in enumerate(lines,1):
            for label,pat in patterns:
                if pat.search(line): hits.append({"path":str(p),"line":n,"kind":label})
    return hits
def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__); sub=ap.add_subparsers(dest="cmd",required=True)
    def arg(cmd): return sub.add_parser(cmd)
    q=arg("slugify"); q.add_argument("text")
    q=arg("safe-filename"); q.add_argument("text")
    for cmd in ("count-words","text-stats","file-hash","json-format","json-sort","json-minify","json-to-csv","csv-to-json","json-diff","markdown-toc","markdown-headings","markdown-links","line-count","trailing-whitespace","normalize-newlines","log-summary"): q=arg(cmd); q.add_argument("file"); q.add_argument("other",nargs="?")
    for cmd in ("duplicates","large-files","empty-dirs","repo-tree","media-manifest","sizes-csv","env-audit","secret-scan"): q=arg(cmd); q.add_argument("path",nargs="?",default="."); q.add_argument("--limit",type=int,default=1000000)
    q=arg("duration"); q.add_argument("seconds",type=float)
    q=arg("timestamp"); q.add_argument("value",nargs="?",default="")
    q=arg("color-rgb"); q.add_argument("hex")
    q=arg("color-contrast"); q.add_argument("foreground"); q.add_argument("background")
    q=arg("required-json-keys"); q.add_argument("file"); q.add_argument("keys",nargs="+")
    a=ap.parse_args(argv); c=a.cmd
    if c=="slugify": out=slugify(a.text)
    elif c=="safe-filename": out=safe_name(a.text)
    elif c in {"count-words","text-stats"}: out=json.dumps(word_count(read_text(a.file)),indent=2)
    elif c=="file-hash": out=hashlib.sha256(Path(a.file).read_bytes()).hexdigest()
    elif c in {"json-format","json-sort","json-minify","json-to-csv"}:
        d=json_load(a.file)
        if c=="json-format": out=json.dumps(d,indent=2,ensure_ascii=False)
        elif c=="json-sort": out=json.dumps(d,indent=2,sort_keys=True,ensure_ascii=False)
        elif c=="json-minify": out=json.dumps(d,separators=(",",":"),ensure_ascii=False)
        else:
            rows=d if isinstance(d,list) else [d]
            if not rows or not isinstance(rows[0],dict): raise ValueError("JSON must contain an object or list of objects")
            import io; b=io.StringIO(); w=csv.DictWriter(b,fieldnames=list(dict.fromkeys(k for row in rows for k in row))); w.writeheader(); w.writerows(rows); out=b.getvalue()
    elif c=="csv-to-json":
        with open(a.file,newline="",encoding="utf-8-sig") as f: out=json.dumps(list(csv.DictReader(f)),indent=2,ensure_ascii=False)
    elif c=="json-diff":
        if not a.other: raise ValueError("Provide a second JSON file")
        out="\n".join(difflib.unified_diff(json.dumps(json_load(a.file),indent=2,sort_keys=True).splitlines(),json.dumps(json_load(a.other),indent=2,sort_keys=True).splitlines(),fromfile=a.file,tofile=a.other,lineterm=""))
    elif c=="duplicates": out=json.dumps(duplicate_files(a.path),indent=2)
    elif c=="large-files": out=json.dumps(find_large(a.path,a.limit),indent=2)
    elif c=="empty-dirs": out=json.dumps([str(p) for p in Path(a.path).rglob("*") if p.is_dir() and not any(p.iterdir())],indent=2)
    elif c=="repo-tree": out=tree(a.path)
    elif c=="media-manifest": out=json.dumps(media_manifest(a.path),indent=2)
    elif c=="sizes-csv": out="path,bytes\n"+"\n".join(f"{json.dumps(str(p))},{p.stat().st_size}" for p in Path(a.path).rglob("*") if p.is_file())
    elif c=="env-audit": out=json.dumps(sorted(k for k in os.environ if any(x in k.lower() for x in ("token","key","secret","password","auth"))),indent=2)
    elif c=="secret-scan":
        hits=scan_secrets(a.path); out=json.dumps(hits,indent=2)
        if hits: print(out); return 1
    elif c=="markdown-toc": out="\n".join("- ["+m.group(2).strip()+"](#"+slugify(m.group(2).strip())+")" for m in re.finditer(r"^(#{1,6})\s+(.+)$",read_text(a.file),re.M))
    elif c=="markdown-headings": out=json.dumps([{"level":len(m.group(1)),"text":m.group(2).strip()} for m in re.finditer(r"^(#{1,6})\s+(.+)$",read_text(a.file),re.M)],indent=2)
    elif c=="markdown-links": out=json.dumps(re.findall(r"\[[^\]]*\]\(([^)]+)\)",read_text(a.file)),indent=2)
    elif c=="line-count": out=str(len(read_text(a.file).splitlines()))
    elif c=="trailing-whitespace":
        hits=[i for i,l in enumerate(read_text(a.file).splitlines(),1) if l.rstrip(" \t")!=l]; out=json.dumps(hits,indent=2)
        if hits: print(out); return 1
    elif c=="normalize-newlines": out=read_text(a.file).replace("\r\n","\n").replace("\r","\n")
    elif c=="log-summary":
        lines=read_text(a.file).splitlines(); out=json.dumps({"lines":len(lines),"errors":sum("error" in x.lower() for x in lines),"warnings":sum("warn" in x.lower() for x in lines)},indent=2)
    elif c=="timestamp":
        dt=datetime.now(timezone.utc) if not a.value else datetime.fromisoformat(a.value.replace("Z","+00:00")); out=dt.astimezone(timezone.utc).isoformat()
    elif c=="duration":
        n=max(0,int(a.seconds)); out=f"{n//86400}d {(n%86400)//3600}h {(n%3600)//60}m {n%60}s"
    elif c=="color-rgb":
        h=a.hex.lstrip("#")
        if len(h)==3: h="".join(ch*2 for ch in h)
        if not re.fullmatch(r"[0-9a-fA-F]{6}",h): raise ValueError("Use #RGB or #RRGGBB")
        out=json.dumps({"r":int(h[0:2],16),"g":int(h[2:4],16),"b":int(h[4:6],16)},indent=2)
    elif c=="color-contrast":
        def lum(h):
            h=h.lstrip("#"); vals=[int(h[i:i+2],16)/255 for i in (0,2,4)]; vals=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in vals]; return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]
        x,y=sorted([lum(a.foreground),lum(a.background)],reverse=True); ratio=(x+.05)/(y+.05); out=json.dumps({"ratio":round(ratio,2),"wcag_aa_normal":ratio>=4.5,"wcag_aa_large":ratio>=3},indent=2)
    elif c=="required-json-keys":
        d=json_load(a.file); missing=[k for k in a.keys if k not in d]; out=json.dumps({"valid":not missing,"missing":missing},indent=2)
        if missing: print(out); return 1
    else: raise ValueError("Unknown command")
    print(out); return 0
if __name__=="__main__":
    try: raise SystemExit(main())
    except (OSError,ValueError,json.JSONDecodeError) as exc: print("error: "+str(exc),file=sys.stderr); raise SystemExit(2)
