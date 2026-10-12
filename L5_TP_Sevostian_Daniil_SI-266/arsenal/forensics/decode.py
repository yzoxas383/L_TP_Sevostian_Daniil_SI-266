"""Decoder pentru exercițiile A1-A7."""
import argparse
import base64
import binascii
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote_to_bytes

RADACINA = Path(__file__).resolve().parents[2]

def ghici_strat(s):
    if re.search(r"%[0-9a-fA-F]{2}", s):
        return "url"
    if s and len(s) % 2 == 0 and re.fullmatch(r"[0-9a-fA-F]+", s):
        return "hex"
    if s and re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", s):
        return "base64"
    return "necunoscut"

def desfa(s):
    strat = ghici_strat(s)
    if strat == "url":
        return strat, unquote_to_bytes(s)
    if strat == "hex":
        return strat, bytes.fromhex(s)
    if strat == "base64":
        return strat, base64.b64decode(s, validate=True)
    return strat, s.encode("utf-8")

def citibil(b):
    return all(32 <= c < 127 for c in b)

def reprezentare(date):
    """Păstrează exact octeții; datele binare sunt reprezentate în HEX."""
    try:
        text = date.decode("utf-8")
        if all(c.isprintable() or c in "\r\n\t" for c in text):
            return {"rezultat": text, "format": "utf-8"}
    except UnicodeDecodeError:
        pass
    return {"rezultat": date.hex(), "format": "hex"}


def straturi(s, limita=8):
    rezultat = s.encode("utf-8") if isinstance(s, str) else bytes(s)
    pasi = []
    for _ in range(limita):
        try:
            text = rezultat.decode("utf-8")
        except UnicodeDecodeError:
            break
        # Un fișier cu o codare poate avea un separator de linie la final.
        # Spațiile din mesaj și textul necodat rămân intacte.
        candidat = text.rstrip("\r\n")
        strat = ghici_strat(candidat)
        if strat == "necunoscut":
            break
        try:
            _, date = desfa(candidat)
        except (ValueError, binascii.Error):
            break
        # Un cuvânt obișnuit poate avea alfabetul Base64. Fără padding,
        # acceptăm automat numai o decodare care produce text citibil.
        if strat == "base64" and "=" not in candidat:
            if reprezentare(date)["format"] != "utf-8":
                break
        if date == rezultat:
            break
        pasi.append({"strat": strat, **reprezentare(date)})
        rezultat = date
    return rezultat, pasi


def scor_text(b):
    scor = 0
    frecvente = "etaoinrsulcdmp"
    for c in b.lower():
        if c == 32:
            scor += 5
        elif chr(c) in frecvente:
            scor += 3
        elif 97 <= c <= 122:
            scor += 1
        elif c in b".,!?{}_-0123456789":
            scor += 0
        elif c in (9, 10, 13):
            scor += 0
        elif 32 <= c < 127:
            scor -= 2
        else:
            scor -= 15
    return scor

def sparge_xor(date):
    if not date:
        raise ValueError("Fișierul XOR este gol.")
    variante = []
    for cheie in range(256):
        clar = bytes(c ^ cheie for c in date)
        variante.append((scor_text(clar), cheie, clar))
    variante.sort(reverse=True)
    _, cheie, clar = variante[0]
    return cheie, clar

def sparge_hash(tinta, cuvinte):
    algoritmi = {32: "md5", 40: "sha1", 64: "sha256"}
    algoritm = algoritmi.get(len(tinta))
    if algoritm is None or not re.fullmatch(r"[0-9a-fA-F]+", tinta):
        raise ValueError("Hash nerecunoscut.")
    for cuvant in cuvinte:
        parola = cuvant.rstrip("\r\n")
        calculat = hashlib.new(algoritm, parola.encode("utf-8")).hexdigest()
        if calculat == tinta.lower():
            return algoritm, parola
    return algoritm, None

def main():
    p = argparse.ArgumentParser(description="Decoder universal pentru laborator")
    p.add_argument("intrare", nargs="?", help="Șir sau cale către fișier")
    p.add_argument("--fisier", action="store_true", help="Citește intrarea din fișier")
    p.add_argument("--mod", choices=["straturi", "xor", "hash", "a1"], default="straturi")
    p.add_argument("--wordlist", default="probe/wordlist.txt" if Path("probe/wordlist.txt").is_file() else "demo/wordlist.txt")
    p.add_argument("--wordlist-encoding", default="latin1", help="Codarea dicționarului, de exemplu utf-8")
    p.add_argument("--fisa", default=str(RADACINA / "arsenal/forensics/fisa.json"))
    a = p.parse_args()
    try:
        if a.mod == "a1":
            b = "Salut".encode()
            print("Octeți:", b, "Primul octet:", b[0])
            print("HEX:", b.hex(), "Refăcut:", bytes.fromhex(b.hex()))
            return
        if a.intrare is None:
            p.error("Lipsește intrarea.")
        if a.mod == "xor":
            cheie, b = sparge_xor(Path(a.intrare).read_bytes())
            print("Cheie probabilă:", cheie)
            print("Mesaj probabil:", b.decode("utf-8", errors="replace"))
            print("Rezultatul este estimat după frecvența literelor.")
            fisa = {"strat": "xor", "cheie": cheie, "rezultat": b.decode("utf-8", errors="replace")}
        elif a.mod == "hash":
            tinte = Path(a.intrare).read_text(encoding="ascii").splitlines() if a.fisier else [a.intrare]
            cuvinte = Path(a.wordlist).read_text(encoding=a.wordlist_encoding).splitlines()
            rezultate = []
            for tinta in tinte:
                if not tinta.strip():
                    continue
                algoritm, parola = sparge_hash(tinta.strip(), cuvinte)
                print(algoritm, "Parolă:", parola if parola is not None else "Nu există în dicționar")
                rezultate.append({"hash": tinta, "algoritm": algoritm, "parola": parola})
            fisa = {"strat": "hash", "rezultat": rezultate}
        else:
            s = Path(a.intrare).read_bytes() if a.fisier else a.intrare
            b, pasi = straturi(s)
            for nr, pas in enumerate(pasi, 1):
                print(f"Stratul {nr}: {pas['strat']} -> {pas['rezultat']}")
            valoare = reprezentare(b)
            print("Rezultat:", valoare["rezultat"])
            print("Format:", valoare["format"])
            fisa = {"strat": pasi[0]["strat"] if pasi else "necunoscut", **valoare, "pasi": pasi}
        Path(a.fisa).write_text(json.dumps(fisa, ensure_ascii=False, indent=2), encoding="utf-8")
    except (OSError, ValueError, LookupError) as e:
        p.exit(1, f"Eroare: {e}\n")

if __name__ == "__main__":
    main()
