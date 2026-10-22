"""Run the markdown-toc profile-maintenance command."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from toolbox import main
raise SystemExit(main(["markdown-toc", *sys.argv[1:]]))
