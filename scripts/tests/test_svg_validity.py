"""Check bundled SVG files parse as XML."""
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
class SvgTests(unittest.TestCase):
    def test_svg_files_parse(self):
        files = list((ROOT / "assets").rglob("*.svg"))
        self.assertGreaterEqual(len(files), 2)
        for path in files:
            with self.subTest(path=str(path)): ET.parse(path)
if __name__ == "__main__": unittest.main()
