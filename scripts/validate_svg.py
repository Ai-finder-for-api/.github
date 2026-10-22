"""Parse bundled SVG files using Python's standard library."""
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    files = list((ROOT / "assets").rglob("*.svg"))
    errors = []
    for path in files:
        try:
            ET.parse(path)
            print("OK", path.relative_to(ROOT))
        except ET.ParseError as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Validated {len(files)} SVG file(s).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
