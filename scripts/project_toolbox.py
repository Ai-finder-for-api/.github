from __future__ import annotations
import argparse, hashlib, json, os, re, sys
from collections import Counter
from pathlib import Path

SKIP={'.git','.venv','venv','node_modules','__pycache__','.pytest_cache','.mypy_cache','dist','build'}
TEXT={'.py','.js','.mjs','.ts','.tsx','.jsx','.json','.toml','.yaml','.yml','.md','.txt','.html','.css','.xml','.svg','.ini','.cfg','.ps1','.bat','.sh'}

def walk(root: Path):
    for p in root.rglob('*'):
        if any(part in SKIP for part in p.parts): continue
        if p.is_file(): yield p

def inventory(root: Path):
    files=list(walk(root)); sizes=[p.stat().st_size for p in files]
    ext=Counter(p.suffix.lower() or '[no extension]' for p in files)
    print(f'Root: {root.resolve()}\nFiles: {len(files)}\nBytes: {sum(sizes):,}\nLargest:')
    for p in sorted(files,key=lambda x:x.stat().st_size,reverse=True)[:15]: print(f'  {p.stat().st_size:>10,}  {p.relative_to(root)}')
    print('Extensions:')
    for e,n in ext.most_common(): print(f'  {e:<16} {n:>5}')

def duplicates(root: Path):
    seen={}; groups=[]
    for p in walk(root):
        try:
            if p.stat().st_size==0: continue
            h=hashlib.sha256()
            with p.open('rb') as f:
                for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
            key=(p.stat().st_size,h.hexdigest())
            if key in seen: groups.append((seen[key],p))
            else: seen[key]=p
        except OSError as e: print(f'WARN {p}: {e}',file=sys.stderr)
    if not groups: print('No byte-identical duplicate files found.'); return
    for a,b in groups: print(f'DUPLICATE\n  {a}\n  {b}')
    print(f'\nDuplicate pairs: {len(groups)}')

def validate_json(root: Path):
    bad=0; count=0
    for p in walk(root):
        if p.suffix.lower()!='.json': continue
        count+=1
        try: json.loads(p.read_text(encoding='utf-8-sig'))
        except (OSError,UnicodeError,json.JSONDecodeError) as e: bad+=1; print(f'INVALID {p.relative_to(root)}: {e}')
    print(f'Checked {count} JSON file(s); invalid: {bad}.'); return int(bad>0)

def text_report(root: Path):
    rows=[]
    for p in walk(root):
        if p.suffix.lower() not in TEXT: continue
        try: s=p.read_text(encoding='utf-8-sig')
        except (OSError,UnicodeError): continue
        rows.append((len(s),len(s.split()),len(s.splitlines()),p))
    print(f'Text files: {len(rows)} | characters: {sum(x[0] for x in rows):,} | words: {sum(x[1] for x in rows):,} | lines: {sum(x[2] for x in rows):,}')
    for chars,words,lines,p in sorted(rows,reverse=True)[:20]: print(f'{chars:>9,} chars {words:>8,} words {lines:>7,} lines  {p.relative_to(root)}')

def tree(root: Path, max_depth: int):
    root=root.resolve(); print(root.name+'/')
    def visit(folder, prefix, depth):
        if depth>=max_depth: return
        try: children=sorted((x for x in folder.iterdir() if x.name not in SKIP),key=lambda x:(x.is_file(),x.name.casefold()))
        except OSError as e: print(prefix+f'! {e}'); return
        for i,x in enumerate(children):
            last=i==len(children)-1; print(prefix+('└── ' if last else '├── ')+x.name+('/' if x.is_dir() else ''))
            if x.is_dir(): visit(x,prefix+('    ' if last else '│   '),depth+1)
    visit(root,'',0)

def large(root: Path, limit: int):
    found=sorted(((p.stat().st_size,p) for p in walk(root) if p.stat().st_size>=limit),reverse=True)
    if not found: print(f'No files at or above {limit:,} bytes.'); return
    for size,p in found: print(f'{size:>12,} bytes  {p.relative_to(root)}')
    print(f'{len(found)} file(s), {sum(x[0] for x in found):,} bytes total.')

def markdown_audit(root: Path):
    count=missing=0; pattern=re.compile(r'!?\[[^\]]*\]\(([^)]+)\)')
    for p in walk(root):
        if p.suffix.lower() not in {'.md','.mdx'}: continue
        try: body=p.read_text(encoding='utf-8-sig')
        except (OSError,UnicodeError) as e: print(f'WARN {p}: {e}'); continue
        for raw in pattern.findall(body):
            target=raw.split('#',1)[0].split('?',1)[0].strip('<>')
            if not target or re.match(r'^(https?:|mailto:|#|data:)',target,re.I): continue
            count+=1; candidate=(p.parent/target).resolve()
            if not candidate.exists(): missing+=1; print(f'MISSING {p.relative_to(root)} -> {target}')
    print(f'Checked {count} local Markdown link(s); missing: {missing}.'); return int(missing>0)

def secret_scan(root: Path):
    # Heuristic only: this never prints the matched secret, only its file and line.
    patterns=[('private-key header',re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
      ('token-like assignment',re.compile(r'(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret)\b\s*[:=]\s*[\"\'][^\"\']{12,}[\"\']')),
      ('GitHub token',re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{20,}\b')),
      ('AWS access key',re.compile(r'\bAKIA[0-9A-Z]{16}\b'))]
    hits=0
    for p in walk(root):
        if p.suffix.lower() not in TEXT: continue
        try: lines=p.read_text(encoding='utf-8-sig').splitlines()
        except (OSError,UnicodeError): continue
        for no,line in enumerate(lines,1):
            for label,rx in patterns:
                if rx.search(line): print(f'REVIEW {p.relative_to(root)}:{no} [{label}]'); hits+=1
    print(f'Potential matches: {hits}. Heuristic scan; review findings manually and never treat a clean result as proof.'); return int(hits>0)

def main():
    ap=argparse.ArgumentParser(description='Practical local project inspection tools; read-only unless an output path is explicitly supplied.')
    ap.add_argument('command',choices=['inventory','duplicates','json','text','tree','large','markdown','secrets'])
    ap.add_argument('path',nargs='?',default='.',help='Folder to inspect (default: current directory)')
    ap.add_argument('--depth',type=int,default=3,help='Maximum folder depth for tree (default: 3)')
    ap.add_argument('--min-bytes',type=int,default=5*1024*1024,help='Minimum size for large-file report (default: 5 MiB)')
    a=ap.parse_args(); root=Path(a.path).expanduser()
    if not root.exists() or not root.is_dir(): ap.error(f'not a directory: {root}')
    if a.command=='inventory': inventory(root)
    elif a.command=='duplicates': duplicates(root)
    elif a.command=='json': return validate_json(root)
    elif a.command=='text': text_report(root)
    elif a.command=='tree': tree(root,max(0,a.depth))
    elif a.command=='large': large(root,max(0,a.min_bytes))
    elif a.command=='markdown': return markdown_audit(root)
    elif a.command=='secrets': return secret_scan(root)
    return 0
if __name__=='__main__': raise SystemExit(main())
