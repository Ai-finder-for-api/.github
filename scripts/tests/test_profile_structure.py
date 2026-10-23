"""Minimal standard-library tests for essential profile files."""
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
class ProfileStructureTests(unittest.TestCase):
    def test_readme_exists(self): self.assertTrue((ROOT / ".github" / "profile" / "README.md").is_file())
    def test_banner_exists(self):
        path = ROOT / "assets/banners/profile-banner.svg"
        self.assertTrue(path.is_file())
        self.assertIn("<svg", path.read_text(encoding="utf-8"))
if __name__ == "__main__": unittest.main()

