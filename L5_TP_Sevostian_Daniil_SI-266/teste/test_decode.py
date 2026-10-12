import base64
import hashlib
import unittest
from arsenal.forensics.decode import desfa, ghici_strat, straturi, citibil, sparge_xor, sparge_hash

def test_base64():
    strat, b = desfa("U2FsdXQ=")
    assert strat == "base64"
    assert b == b"Salut"

class TestDecode(unittest.TestCase):
    def test_base64(self):
        test_base64()

    def test_recunoastere(self):
        self.assertEqual(ghici_strat("%2Fetc"), "url")
        self.assertEqual(ghici_strat("48656c6c6f"), "hex")
        self.assertEqual(ghici_strat("Salut!"), "necunoscut")

    def test_hex_url(self):
        self.assertEqual(desfa("53616c7574"), ("hex", b"Salut"))
        self.assertEqual(desfa("Salut%20lume"), ("url", b"Salut lume"))
        self.assertEqual(desfa("%C8%99"), ("url", "ș".encode()))

    def test_straturi(self):
        s = base64.b64encode(b"53616c7574").decode()
        b, pasi = straturi(s)
        self.assertEqual(b, b"Salut")
        self.assertEqual(len(pasi), 2)
        self.assertEqual(len(straturi(s, 1)[1]), 1)

    def test_intrare_ambigua(self):
        self.assertEqual(straturi("Salut")[0], b"Salut")
        self.assertEqual(straturi("test")[0], b"test")
        self.assertEqual(straturi("")[0], b"")
        with self.assertRaises(ValueError):
            desfa("A")

    def test_citibil(self):
        self.assertTrue(citibil(b"Salut"))
        self.assertFalse(citibil(b"\x00"))

    def test_xor(self):
        clar = b"Acesta este un mesaj demonstrativ pentru laborator."
        cheie, b = sparge_xor(bytes(c ^ 73 for c in clar))
        self.assertEqual((cheie, b), (73, clar))
        with self.assertRaises(ValueError):
            sparge_xor(b"")

    def test_hash(self):
        for algoritm in ("md5", "sha1", "sha256"):
            tinta = hashlib.new(algoritm, b"student123").hexdigest()
            self.assertEqual(sparge_hash(tinta, ["salut", "student123"]), (algoritm, "student123"))
            self.assertEqual(sparge_hash(tinta, ["salut"]), (algoritm, None))
        with self.assertRaises(ValueError):
            sparge_hash("xyz", [])

if __name__ == "__main__":
    unittest.main()

