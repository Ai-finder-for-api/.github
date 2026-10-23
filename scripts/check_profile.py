"""Check that the personal profile README and its referenced core assets exist."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / ".github" / "profile" / "README.md"

def main() -> int:
    errors = []
    if not README.is_file():
        print("Missing required file: profile/README.md")
        return 1

    readme = README.read_text(encoding="utf-8")
    for placeholder in ("YOUR_USERNAME", "REPLACE_ME"):
        if placeholder in readme:
            errors.append(f"Unexpected placeholder in README: {placeholder}")

    # Validate only the personal profile's actual local image references.
    for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", readme):
        target = target.strip().split()[0].strip("<>")
        if target.startswith(("https://", "http://", "data:", "#")):
            continue
        target = target.split("#", 1)[0]
        if target and not (README.parent / target).resolve().is_file():
            errors.append(f"Missing README image: {target}")

    if errors:
        print("\n".join(errors))
        return 1
    print("Personal profile checks passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
