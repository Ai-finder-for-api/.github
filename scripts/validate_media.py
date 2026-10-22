"""Validate local Markdown image references without network requests."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
def main() -> int:
    missing, scanned = [], 0
    for md in ROOT.rglob("*.md"):
        if any(part in {".git", "node_modules", ".venv", "venv"} for part in md.parts):
            continue
        try: text = md.read_text(encoding="utf-8")
        except UnicodeDecodeError: continue
        for target in IMAGE.findall(text):
            target = target.strip().split()[0].strip("<>")
            if target.startswith(("https://", "http://", "data:")) or target.startswith("#"): continue
            target = target.split("#", 1)[0]
            if not target: continue
            scanned += 1
            if not (md.parent / target).resolve().exists(): missing.append(f"{md.relative_to(ROOT)} -> {target}")
    print(f"Checked {scanned} local image reference(s).")
    if missing:
        print("Missing references:\n" + "\n".join("  - " + item for item in missing)); return 1
    print("All local Markdown image references exist."); return 0
if __name__ == "__main__": raise SystemExit(main())
