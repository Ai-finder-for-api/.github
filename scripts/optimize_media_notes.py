"""Report media files larger than 5 MiB; does not modify any files."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
WARN_BYTES = 5 * 1024 * 1024

def main() -> int:
    total = 0
    large = []
    for path in (ROOT / "assets").rglob("*"):
        if path.is_file():
            size = path.stat().st_size
            total += size
            if size > WARN_BYTES:
                large.append((size, path.relative_to(ROOT)))
    print(f"Total assets: {total / 1024 / 1024:.2f} MiB")
    for size, path in sorted(large, reverse=True):
        print(f"WARNING {size / 1024 / 1024:.2f} MiB  {path}")
    if not large:
        print("No assets above 5 MiB.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
