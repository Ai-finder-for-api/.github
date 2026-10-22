import subprocess, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "toolbox.py"
FIX = ROOT / "scripts" / "tests" / "fixtures"
class CliTest(unittest.TestCase):
    def test_command(self):
        args = ['Quantum Suite / Core']
        args = [str(FIX / a.split(":",1)[1]) if a.startswith("FIXTURE:") else a for a in args]
        result = subprocess.run([sys.executable, str(SCRIPT), "slugify", *args], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn('quantum-suite-core', result.stdout)
if __name__ == "__main__": unittest.main()