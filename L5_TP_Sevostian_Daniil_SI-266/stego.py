"""Ascunderea și citirea mesajului prin biții LSB: B5-B6."""
import argparse
from PIL import Image

def ascunde(sursa, destinatie, mesaj):
    if "\0" in mesaj:
        raise ValueError("Mesajul nu poate conține octetul zero.")
    date = mesaj.encode("utf-8") + b"\0"
    biti = "".join(f"{c:08b}" for c in date)
    with Image.open(sursa) as original:
        img = original.convert("RGB")
    if len(biti) > img.width * img.height * 3:
        raise ValueError("Imaginea este prea mică pentru mesaj.")
    pixeli = list(img.getdata())
    noi = []
    i = 0
    for pixel in pixeli:
        canale = list(pixel)
        for j in range(3):
            if i < len(biti):
                canale[j] = (canale[j] & ~1) | int(biti[i])
                i += 1
        noi.append(tuple(canale))
    img.putdata(noi)
    img.save(destinatie, format="PNG")

def dezvaluie(cale):
    with Image.open(cale) as original:
        img = original.convert("RGB")
    date = bytearray()
    valoare = 0
    numar = 0
    for pixel in img.getdata():
        for canal in pixel:
            valoare = (valoare << 1) | (canal & 1)
            numar += 1
            if numar == 8:
                if valoare == 0:
                    return date.decode("utf-8")
                date.append(valoare)
                valoare = 0
                numar = 0
    raise ValueError("Nu a fost găsit marcajul de sfârșit.")

def main():
    p = argparse.ArgumentParser(description="Steganografie LSB")
    p.add_argument("actiune", choices=["ascunde", "dezvaluie"])
    p.add_argument("imagine")
    p.add_argument("--iesire", default="stego.png")
    p.add_argument("--mesaj", default="FLAG{ascuns_in_pixeli}")
    a = p.parse_args()
    try:
        if a.actiune == "ascunde":
            ascunde(a.imagine, a.iesire, a.mesaj)
            rezultat = dezvaluie(a.iesire)
            if rezultat != a.mesaj:
                raise ValueError("Mesajul extras nu coincide.")
            print("Imagine salvată:", a.iesire)
            print("Verificare reușită:", rezultat)
        else:
            print("Mesaj extras:", dezvaluie(a.imagine))
    except (OSError, ValueError) as e:
        p.exit(1, f"Eroare: {e}\n")

if __name__ == "__main__":
    main()
