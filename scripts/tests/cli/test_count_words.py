import subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "toolbox.py"
FIX = ROOT / "scripts" / "tests" / "fixtures"
class CliTest(unittest.TestCase):
    def test_command(self):
        args = ['FIXTURE:sample.txt']
        args = [str(FIX / a.split(":",1)[1]) if a.startswith("FIXTURE:") else a for a in args]
        result = subprocess.run([sys.executable, str(SCRIPT), "count-words", *args], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn('"words": 5', result.stdout)
if __name__ == "__main__": unittest.main()