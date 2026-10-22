"""Run the csv-to-json profile-maintenance command."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from toolbox import main
raise SystemExit(main(["csv-to-json", *sys.argv[1:]]))
