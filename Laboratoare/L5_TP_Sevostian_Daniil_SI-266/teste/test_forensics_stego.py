import tempfile
import unittest
import zipfile
from pathlib import Path
from PIL import Image
from forensics import tip_real, strings, grade, metadate, extrage_zip
from stego import ascunde, dezvaluie
from demo.pregateste_demo import main as pregateste_demo

class TestForensicsStego(unittest.TestCase):
    def test_semnaturi_strings_zip_gps(self):
        pregateste_demo()
        self.assertEqual(tip_real("demo/foto.jpg"), "jpeg")
        self.assertEqual(tip_real("demo/ascuns.png"), "png")
        self.assertEqual(tip_real("demo/semnatura.pdf"), "pdf")
        self.assertIn("indiciu_demo.txt", " ".join(strings("demo/ascuns.png")))
        date = metadate("demo/foto.jpg")
        self.assertAlmostEqual(date["Latitudine"], 47.025)
        self.assertAlmostEqual(date["Longitudine"], 28.8375)
        self.assertEqual(grade((10, 30, 0), "S"), -10.5)
        self.assertEqual(grade((10, 30, 0), "W"), -10.5)
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as d:
            cale = Path(d) / "gasit.zip"
            pozitie, continut = extrage_zip("demo/ascuns.png", cale)
            self.assertGreater(pozitie, 0)
            self.assertEqual(tip_real(cale), "zip/docx")
            self.assertEqual(continut["indiciu_demo.txt"], b"FLAG{arhiva_demonstrativa}\n")
            self.assertTrue(zipfile.is_zipfile(cale))
            sursa = Path(d) / "simplu.png"
            Image.new("RGB", (20, 20)).save(sursa)
            with self.assertRaises(ValueError):
                extrage_zip(sursa, Path(d) / "lipsa.zip")
            self.assertNotIn("Latitudine", metadate(sursa))

    def test_lsb(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as d:
            sursa = Path(d) / "sursa.png"
            iesire = Path(d) / "stego.png"
            Image.new("RGB", (20, 20), (90, 140, 190)).save(sursa)
            for mesaj in ("FLAG{ascuns_in_pixeli}", "Salut, țară!", ""):
                ascunde(sursa, iesire, mesaj)
                self.assertEqual(dezvaluie(iesire), mesaj)
                with Image.open(sursa) as a, Image.open(iesire) as b:
                    for p, q in zip(a.getdata(), b.getdata()):
                        self.assertTrue(all(abs(x-y) <= 1 for x, y in zip(p, q)))
            with self.assertRaises(ValueError):
                ascunde(sursa, iesire, "A" * 200)
            with self.assertRaises(ValueError):
                ascunde(sursa, iesire, "a\0b")
            Image.new("RGB", (4, 4), (1, 1, 1)).save(sursa)
            with self.assertRaises(ValueError):
                dezvaluie(sursa)

if __name__ == "__main__":
    unittest.main()

