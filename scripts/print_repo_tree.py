"""Print a compact repository tree, skipping common generated folders."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".venv", "venv", "__pycache__", "node_modules"}

def walk(path: Path, prefix: str = "") -> None:
    children = sorted((p for p in path.iterdir() if p.name not in SKIP),
                      key=lambda p: (p.is_file(), p.name.lower()))
    for index, child in enumerate(children):
        last = index == len(children) - 1
        print(prefix + ("└── " if last else "├── ") + child.name)
        if child.is_dir():
            walk(child, prefix + ("    " if last else "│   "))

if __name__ == "__main__":
    print(ROOT.name + "/")
    walk(ROOT)
