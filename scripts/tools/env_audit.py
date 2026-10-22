"""Run the env-audit profile-maintenance command."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from toolbox import main
raise SystemExit(main(["env-audit", *sys.argv[1:]]))
