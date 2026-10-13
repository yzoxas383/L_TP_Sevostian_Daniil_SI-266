import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from arsenal.forensics.decode import desfa, straturi, sparge_hash
from forensics import extrage_zip

ROOT = Path(__file__).resolve().parents[1]

class TestRegresii(unittest.TestCase):
    def test_spatii_pastrate(self):
        self.assertEqual(desfa(' Salut%20lume ')[1], b' Salut lume ')
        self.assertEqual(straturi(' Salut%20lume ')[0], b' Salut lume ')
        self.assertEqual(straturi(b' text simplu \r\n')[0], b' text simplu \r\n')

    def test_bytes_si_codari_binare(self):
        for intrare in (b'\x00\xff', '00ff', 'AP8='):
            self.assertEqual(straturi(intrare)[0], b'\x00\xff')
        self.assertEqual(straturi('AA==')[0], b'\x00')
        self.assertEqual(straturi('U2FsdXQ=\r\n')[0], b'Salut')

    def test_cli_fisier_binar(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "teste") as d:
            sursa = Path(d)/'input.bin'; fisa = Path(d)/'fisa.json'
            sursa.write_bytes(b'\x00\xff')
            p = subprocess.run([sys.executable, str(ROOT/'arsenal/forensics/decode.py'),
                str(sursa), '--fisier', '--fisa', str(fisa)], capture_output=True, timeout=10)
            self.assertEqual(p.returncode, 0, p.stderr)
            rezultat = json.loads(fisa.read_text(encoding='utf-8'))
            self.assertEqual(rezultat['format'], 'hex')
            self.assertEqual(bytes.fromhex(rezultat['rezultat']), sursa.read_bytes())

    def test_hash_spatii_si_utf8(self):
        self.assertEqual(sparge_hash(hashlib.md5(b' pass ').hexdigest(), [' pass \n']), ('md5', ' pass '))
        with tempfile.TemporaryDirectory(dir=ROOT / "teste") as d:
            dic = Path(d)/'wordlist.txt'; fisa = Path(d)/'fisa.json'
            dic.write_text('țară\n', encoding='utf-8')
            tinta = hashlib.md5('țară'.encode()).hexdigest()
            p = subprocess.run([sys.executable, str(ROOT/'arsenal/forensics/decode.py'), tinta,
                '--mod', 'hash', '--wordlist', str(dic), '--wordlist-encoding', 'utf-8',
                '--fisa', str(fisa)], capture_output=True, timeout=10)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(fisa.read_text(encoding='utf-8'))['rezultat'][0]['parola'], 'țară')

    @staticmethod
    def arhiva():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as z:
            z.writestr('clue.txt', b'demo')
        return buffer.getvalue()

    def test_zip_semnatura_falsa(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "teste") as d:
            sursa = Path(d)/'ascuns.bin'; iesire = Path(d)/'gasit.zip'
            prefix = b'IMAGEPK\x03\x04FALSE HEADER filler'
            sursa.write_bytes(prefix + self.arhiva())
            pozitie, continut = extrage_zip(sursa, iesire)
            self.assertEqual(pozitie, len(prefix))
            self.assertEqual(continut, {'clue.txt': b'demo'})
            self.assertEqual(iesire.read_bytes(), sursa.read_bytes()[pozitie:])

    def test_zip_eroare_pastreaza_destinatia(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "teste") as d:
            sursa = Path(d)/'input.bin'; iesire = Path(d)/'existing.zip'
            for date in (b'no ZIP', b'PK\x03\x04false header'):
                sursa.write_bytes(date); iesire.write_bytes(b'KEEP')
                with self.assertRaises(ValueError):
                    extrage_zip(sursa, iesire)
                self.assertEqual(iesire.read_bytes(), b'KEEP')
            self.assertEqual(sorted(p.name for p in Path(d).iterdir()), ['existing.zip', 'input.bin'])

    def test_zip_crc_pastreaza_destinatia(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "teste") as d:
            sursa = Path(d)/'bad.zip'; iesire = Path(d)/'existing.zip'
            date = bytearray(self.arhiva()); date[date.find(b'demo')] ^= 1
            sursa.write_bytes(date); iesire.write_bytes(b'KEEP')
            with self.assertRaises(ValueError):
                extrage_zip(sursa, iesire)
            self.assertEqual(iesire.read_bytes(), b'KEEP')

    def test_zip_nu_suprascrie_sursa(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "teste") as d:
            sursa = Path(d)/'input.zip'; date = self.arhiva(); sursa.write_bytes(date)
            with self.assertRaises(ValueError):
                extrage_zip(sursa, sursa)
            self.assertEqual(sursa.read_bytes(), date)

if __name__ == '__main__':
    unittest.main()

