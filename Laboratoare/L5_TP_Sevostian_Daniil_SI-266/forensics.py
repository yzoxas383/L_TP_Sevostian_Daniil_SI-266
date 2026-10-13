"""Semnături, text, EXIF/GPS și extragerea unui ZIP: B1-B4."""
import argparse
import io
import os
import tempfile
import re
import zipfile
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def tip_real(cale):
    with open(cale, "rb") as f:
        cap = f.read(8)
    for semnatura, tip in [(b"%PDF", "pdf"), (b"\x89PNG\r\n\x1a\n", "png"), (b"\xff\xd8", "jpeg"), (b"PK\x03\x04", "zip/docx")]:
        if cap.startswith(semnatura):
            return tip
    return "necunoscut: " + cap.hex()

def strings(cale):
    return [s.decode("ascii") for s in re.findall(rb"[ -~]{4,}", Path(cale).read_bytes())]

def grade(valori, emisfera):
    rezultat = float(valori[0]) + float(valori[1]) / 60 + float(valori[2]) / 3600
    if emisfera in ("S", "W", b"S", b"W"):
        rezultat = -rezultat
    return rezultat

def metadate(cale):
    with Image.open(cale) as img:
        exif = img.getexif()
        date = {TAGS.get(k, str(k)): str(v) for k, v in exif.items() if k != 34853}
        gps = exif.get_ifd(34853) if 34853 in exif else {}
    date["GPS"] = {GPSTAGS.get(k, str(k)): str(v) for k, v in gps.items()}
    if all(k in gps for k in (1, 2, 3, 4)):
        date["Latitudine"] = grade(gps[2], gps[1])
        date["Longitudine"] = grade(gps[4], gps[3])
    return date

def extrage_zip(cale, destinatie):
    sursa = Path(cale)
    iesire = Path(destinatie)
    if sursa.resolve() == iesire.resolve() or (
        iesire.exists() and os.path.samefile(sursa, iesire)
    ):
        raise ValueError("Sursa și destinația trebuie să fie diferite.")
    date = sursa.read_bytes()
    try:
        # Directorul central indică antetele reale. O semnătură falsă din
        # imagine nu stabilește începutul arhivei.
        with zipfile.ZipFile(io.BytesIO(date)) as z:
            elemente = z.infolist()
            if not elemente:
                raise ValueError("Arhiva ZIP nu conține fișiere.")
            pozitie = min(i.header_offset for i in elemente)
        if pozitie < 0 or date[pozitie:pozitie + 4] != b"PK\x03\x04":
            raise ValueError("Antet ZIP invalid.")
        arhiva = date[pozitie:]
        with zipfile.ZipFile(io.BytesIO(arhiva)) as z:
            if min(i.header_offset for i in z.infolist()) != 0:
                raise ValueError("Început ZIP invalid.")
            defect = z.testzip()
            if defect:
                raise ValueError("Fișier ZIP deteriorat: " + defect)
            continut = {i.filename: z.read(i) for i in z.infolist() if not i.is_dir()}
    except zipfile.BadZipFile as e:
        raise ValueError("Nu s-a găsit o arhivă ZIP validă.") from e
    # Scriem doar după validare. La eșec, fișierul existent rămâne intact.
    temporar = None
    try:
        with tempfile.NamedTemporaryFile(dir=iesire.parent, delete=False) as f:
            temporar = Path(f.name)
            f.write(arhiva)
        os.replace(temporar, iesire)
    finally:
        if temporar is not None:
            temporar.unlink(missing_ok=True)
    return pozitie, continut


def main():
    p = argparse.ArgumentParser(description="Analiza fișierelor B1-B4")
    p.add_argument("--probe", default="probe" if Path("probe/foto.jpg").is_file() else "demo")
    p.add_argument("--zip", default="gasit.zip")
    a = p.parse_args()
    folder = Path(a.probe)
    try:
        print("B1: Tipurile reale")
        for cale in sorted(folder.iterdir()):
            if cale.is_file():
                print(cale.name, "->", tip_real(cale))
        print("B2: Șiruri din ascuns.png")
        for s in strings(folder / "ascuns.png"):
            print(s)
        print("B3: EXIF și GPS")
        date = metadate(folder / "foto.jpg")
        for k, v in date.items():
            print(k, "=", v)
        if "Latitudine" not in date:
            print("Coordonatele GPS lipsesc.")
        print("B4: Arhiva ascunsă")
        pozitie, continut = extrage_zip(folder / "ascuns.png", a.zip)
        print("Arhiva extrasă de la octetul", pozitie)
        for nume, date in continut.items():
            print("Fișier:", nume)
            print(date.decode("utf-8", errors="replace"))
    except (OSError, ValueError, zipfile.BadZipFile) as e:
        p.exit(1, f"Eroare: {e}\n")

if __name__ == "__main__":
    main()
