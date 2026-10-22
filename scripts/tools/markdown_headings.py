"""Run the markdown-headings profile-maintenance command."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from toolbox import main
raise SystemExit(main(["markdown-headings", *sys.argv[1:]]))
