"""Check required profile files and obvious placeholders."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["README.md", "docs/INTERACTIVE_STATS.md", "docs/MEDIA_GUIDE.md",
            "assets/banners/profile-banner.svg", "assets/images/README_FOOTER.svg"]

def main() -> int:
    errors = [f"Missing required file: {name}" for name in REQUIRED if not (ROOT / name).is_file()]
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for placeholder in ("YOUR_USERNAME", "REPLACE_ME"):
        if placeholder in readme:
            errors.append(f"Unexpected placeholder in README: {placeholder}")
    if errors:
        print("\n".join(errors))
        return 1
    print("Profile structure checks passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
