"""Date demonstrative proprii, nu probe originale ale profesorului."""
import base64
import hashlib
import io
import zipfile
from pathlib import Path
from urllib.parse import quote
from PIL import Image
from PIL.TiffImagePlugin import IFDRational

def main():
    folder = Path(__file__).resolve().parent
    mesaj = "FLAG{mesaj_demonstrativ}"
    strat = base64.b64encode(mesaj.encode()).decode().encode().hex()
    strat = quote(strat, safe="")
    # Cifrele HEX nu sunt escapate de quote, deci adăugăm explicit un strat URL.
    strat = "".join(f"%{ord(c):02X}" for c in strat)
    (folder / "mesaj.txt").write_text(strat, encoding="utf-8")
    clar = b"Acesta este un mesaj demonstrativ pentru laborator."
    (folder / "xor.bin").write_bytes(bytes(c ^ 73 for c in clar))
    parola = "student123"
    hashuri = [hashlib.new(a, parola.encode()).hexdigest() for a in ("md5", "sha1", "sha256")]
    (folder / "hashuri.txt").write_text("\n".join(hashuri), encoding="ascii")
    (folder / "wordlist.txt").write_text("salut\nstudent123\nlaborator\n", encoding="latin1")
    img = Image.new("RGB", (80, 80), (90, 140, 190))
    exif = Image.Exif()
    exif[270] = "Imagine demonstrativa pentru laborator"
    exif[271] = "Demo"
    exif[34853] = {1: "N", 2: (IFDRational(47), IFDRational(1), IFDRational(30)),
                   3: "E", 4: (IFDRational(28), IFDRational(50), IFDRational(15))}
    img.save(folder / "foto.jpg", exif=exif)
    img.save(folder / "ascuns.png")
    arhiva = io.BytesIO()
    with zipfile.ZipFile(arhiva, "w", compression=zipfile.ZIP_STORED) as z:
        z.writestr("indiciu_demo.txt", "FLAG{arhiva_demonstrativa}\n")
    with (folder / "ascuns.png").open("ab") as f:
        f.write(arhiva.getvalue())
    (folder / "semnatura.pdf").write_bytes(b"%PDF-1.4\nDemonstratie de semnatura, nu document PDF complet.\n")
    print("Au fost generate datele demonstrative în demo/.")

if __name__ == "__main__":
    main()
