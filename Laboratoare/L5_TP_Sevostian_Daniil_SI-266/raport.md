# Laboratorul 5 Informații invizibile forensics și steganografie

Student în anul I: Sevostian Daniil, grupa SI-266, UTM, FCIM, Securitate Informațională.

## Scopul lucrării

Am realizat un decoder pentru Base64, HEX și URL, o căutare a cheii XOR și o căutare de parole într-un dicționar. Am analizat semnăturile fișierelor, textul dintr-un binar, metadatele EXIF și GPS, o arhivă ascunsă și un mesaj ascuns în pixelii unei imagini.

**Starea probelor:** profesorul nu ne-a furnizat probele originale sau scriptul `probe/pregateste.py`. Am folosit fișiere proprii, generate prin `demo/pregateste_demo.py`, pentru a implementa și verifica exercițiile. Mesajele, cheia, parolele și coordonatele din acest raport aparțin acestor date demonstrative.

## Instrumente utilizate

Windows, Visual Studio Code, Python 3.12.14, Pillow 12.3.0, bibliotecile standard argparse, base64, hashlib, json, pathlib, re, urllib.parse, zipfile și unittest. Mediul `.venv` funcționează cu pachetele disponibile din instalarea Python locală. Comanda de instalare fără rețea a confirmat că Pillow este deja disponibilă. Pentru alt calculator, pașii de instalare sunt în README.md.

## Lucrarea A

### A1 Text și octeți

Cerință: Conversia textului în bytes, HEX și înapoi.

Implementare: Am folosit encode, hex și bytes.fromhex; primul octet este un număr.

Comandă:

```powershell
python arsenal/forensics/decode.py --mod a1
```

Rezultat real pe date demonstrative:

```text
Octeți: b'Salut' Primul octet: 83
HEX: 53616c7574 Refăcut: b'Salut'
```

Concluzie: Conversia păstrează textul Salut.

### A2 Recunoașterea codării

Cerință: Identificarea URL, HEX și Base64 în această ordine.

Implementare: ghici_strat verifică expresii regulate. HEX cere lungime pară. Forma unui șir nu garantează că acesta este într-adevăr codat.

Comandă:

```powershell
python -c "from arsenal.forensics.decode import ghici_strat; print(ghici_strat('%2Fetc')); print(ghici_strat('48656c6c6f'))"
```

Rezultat real pe date demonstrative:

```text
url
hex
```

Concluzie: URL are prioritate, apoi HEX, apoi Base64.

### A3 Decodarea

Cerință: Returnarea tipului și a rezultatului bytes.

Implementare: desfa folosește base64.b64decode cu validare, bytes.fromhex și unquote_to_bytes. Pentru URL păstrez octeții, inclusiv UTF-8.

Comandă:

```powershell
python -c "from arsenal.forensics.decode import desfa; print(desfa('U2FsdXQ=')); print(desfa('53616c7574')); print(desfa('Salut%20lume'))"
```

Rezultat real pe date demonstrative:

```text
('base64', b'Salut')
('hex', b'Salut')
('url', b'Salut lume')
```

Concluzie: Toate cele trei conversii dau rezultatul așteptat.

### A4 Straturi multiple

Cerință: Desfacerea succesivă, cu maximum opt încercări.

Implementare: Continui dacă rezultatul citibil poate fi încă decodat. La o codare invalidă păstrez ultimul rezultat. HEX și Base64 cu padding pot produce bytes binari, păstrați în fișă ca HEX. Pentru Base64 fără padding aplic o euristică de text citibil. Base64 fără marcaje poate fi ambiguu; recunoașterea este o euristică.

Comandă:

```powershell
python arsenal/forensics/decode.py demo/mesaj.txt --fisier
```

Rezultat real pe date demonstrative:

```text
Stratul 1: url -> 526b7842523374745a584e68616c396b5a573176626e4e30636d463061585a39
Stratul 2: hex -> RkxBR3ttZXNhal9kZW1vbnN0cmF0aXZ9
Stratul 3: base64 -> FLAG{mesaj_demonstrativ}
Rezultat: FLAG{mesaj_demonstrativ}
Format: utf-8
```

Concluzie: Mesajul demonstrativ a avut trei straturi: URL, HEX, Base64. Proba originală mesaj.txt lipsește.

### A5 XOR cu un octet

Cerință: Încercarea tuturor celor 256 de chei.

Implementare: Calculez bytes(c ^ cheie) și aleg textul cu cel mai bun scor după spații și litere frecvente. Cheia este probabilă; algoritmul nu garantează identificarea oricărui text.

Comandă:

```powershell
python arsenal/forensics/decode.py demo/xor.bin --mod xor --fisa demo/fisa_xor.json
```

Rezultat real pe date demonstrative:

```text
Cheie probabilă: 73
Mesaj probabil: Acesta este un mesaj demonstrativ pentru laborator.
Rezultatul este estimat după frecvența literelor.
```

Concluzie: Cheia găsită coincide cu cheia 73 folosită de generatorul demonstrativ.

### A6 Căutarea parolei după hash

Cerință: Recunoașterea MD5, SHA1 și SHA256 și verificarea dicționarului.

Implementare: Algoritmul este ales după lungime și forma HEX. Verific fiecare hash din fișier și fiecare parolă din dicționar; absența parolei este raportată.

Comandă:

```powershell
python arsenal/forensics/decode.py demo/hashuri.txt --fisier --mod hash --wordlist demo/wordlist.txt --fisa demo/fisa_hash.json
```

Rezultat real pe date demonstrative:

```text
md5 Parolă: student123
sha1 Parolă: student123
sha256 Parolă: student123
```

Concluzie: Parola demonstrativă student123 a fost găsită pentru toate cele trei hash-uri. Dicționarul profesorului lipsește.

### A7 CLI JSON și test

Cerință: Intrare ca șir sau fișier, fișă JSON și testul Salut.

Implementare: argparse selectează modul; `--fisier` citește bytes. Fișa reține stratul, rezultatul și formatul (`utf-8` sau `hex` pentru date binare). Datele binare nu sunt înlocuite cu caractere de substituție.

Comenzi:

```powershell
python arsenal/forensics/decode.py "U2FsdXQ=" --fisa demo/fisa_salut.json
Get-Content demo/fisa_salut.json
python -m unittest teste.test_decode -v
```

Output al decoderului:

```text
Stratul 1: base64 -> Salut
Rezultat: Salut
Format: utf-8
```

Conținutul fișei `demo/fisa_salut.json`:

```json
{
  "strat": "base64",
  "rezultat": "Salut",
  "format": "utf-8",
  "pasi": [
    {"strat": "base64", "rezultat": "Salut", "format": "utf-8"}
  ]
}
```

Fișa obligatorie `arsenal/forensics/fisa.json` este generată separat prin comanda din A4 pentru mesajul demonstrativ cu trei straturi. Output-urile actualizate și testele sunt în `rezultate/`.

## Lucrarea B

### B1 Magic bytes

Cerință: Identificarea PDF, PNG, JPEG și ZIP/DOCX.

Implementare: Citesc primii opt octeți în modul rb. ZIP și DOCX au aceeași familie de semnături.

Comandă:

```powershell
python forensics.py --probe demo
```

Rezultat real pe date demonstrative:

```text
B1: Tipurile reale
ascuns.png -> png
fisa_hash.json -> necunoscut: 7b0d0a2020227374
fisa_salut.json -> necunoscut: 7b0d0a2020227374
fisa_xor.json -> necunoscut: 7b0d0a2020227374
foto.jpg -> jpeg
hashuri.txt -> necunoscut: 6164366132383034
mesaj.txt -> necunoscut: 2533352533322533
pregateste_demo.py -> necunoscut: 2222224461746520
semnatura.pdf -> pdf
wordlist.txt -> necunoscut: 73616c75740d0a73
xor.bin -> necunoscut: 082a2c3a3d28692c
```

Concluzie: Semnăturile imaginilor, ale arhivei și ale mostrei PDF sunt identificate. semnatura.pdf este doar o mostră de antet, nu un PDF complet.

### B2 Strings

Cerință: Extragerea textului imprimabil din ascuns.png.

Implementare: Expresia regulată pe bytes [ -~]{4,} găsește secvențe ASCII de minimum patru caractere.

Comandă:

```powershell
python forensics.py --probe demo
```

Rezultat real pe date demonstrative:

```text
Șiruri din ascuns.png
IHDR
IDATx
IEND
qK]Ba
indiciu_demo.txtFLAG{arhiva_demonstrativa}
qK]Ba
indiciu_demo.txtPK
```

Concluzie: În imagine apar numele indiciu_demo.txt și mesajul din arhiva demonstrativă.

### B3 EXIF și GPS

Cerință: Citirea metadatelor și conversia coordonatelor.

Implementare: Folosesc getexif și blocul GPS; formula este grade + minute/60 + secunde/3600. S și W dau valori negative.

Comandă:

```powershell
python forensics.py --probe demo
```

Rezultat real pe date demonstrative:

```text
EXIF și GPS
ImageDescription = Imagine demonstrativa pentru laborator
Make = Demo
GPS = {'GPSLatitudeRef': 'N', 'GPSLatitude': '(47.0, 1.0, 30.0)', 'GPSLongitudeRef': 'E', 'GPSLongitude': '(28.0, 50.0, 15.0)'}
Latitudine = 47.025
Longitudine = 28.8375
```

Concluzie: Coordonatele demonstrative sunt 47.025 și 28.8375. Nu sunt coordonate extrase din proba profesorului.

### B4 File carving

Cerință: Separarea ZIP-ului lipit la imagine și citirea conținutului.

Implementare: Folosesc directorul central ZIP pentru a identifica începutul real, verific arhiva și CRC-urile în memorie, apoi salvez gasit.zip printr-un fișier temporar. O eroare nu șterge și nu suprascrie destinația existentă.

Comandă:

```powershell
python forensics.py --probe demo
```

Rezultat real pe date demonstrative:

```text
Arhiva ascunsă
Arhiva extrasă de la octetul 208
Fișier: indiciu_demo.txt
FLAG{arhiva_demonstrativa}
```

Concluzie: Arhiva demonstrativă conține indiciu_demo.txt cu FLAG{arhiva_demonstrativa}.

### B5 Ascunderea LSB

Cerință: Ascunderea FLAG{ascuns_in_pixeli} în RGB.

Implementare: Adaug octetul zero la final. Modific ultimul bit al fiecărui canal și verific capacitatea. Salvez PNG.

Comandă:

```powershell
python stego.py ascunde demo/foto.jpg
```

Rezultat real pe date demonstrative:

```text
Imagine salvată: stego.png
Verificare reușită: FLAG{ascuns_in_pixeli}
Laborator_5\stego.py:14: DeprecationWarning: Image.Image.getdata is deprecated and will be removed in Pillow 14 (2027-10-15). Use get_flattened_data instead.
  pixeli = list(img.getdata())
Laborator_5\stego.py:33: DeprecationWarning: Image.Image.getdata is deprecated and will be removed in Pillow 14 (2027-10-15). Use get_flattened_data instead.
  for pixel in img.getdata():
```

Concluzie: stego.png a fost creat pe fotografia demonstrativă. Fiecare canal se schimbă cu maximum o unitate.

### B6 Extragerea LSB

Cerință: Reconstruirea mesajului din biți.

Implementare: Citesc RGB în aceeași ordine, formez câte un octet din opt biți și mă opresc la octetul zero. Lipsa marcajului produce o eroare.

Comandă:

```powershell
python stego.py dezvaluie stego.png
```

Rezultat real pe date demonstrative:

```text
Mesaj extras: FLAG{ascuns_in_pixeli}
Laborator_5\stego.py:33: DeprecationWarning: Image.Image.getdata is deprecated and will be removed in Pillow 14 (2027-10-15). Use get_flattened_data instead.
  for pixel in img.getdata():
```

Concluzie: Mesajul extras coincide complet cu mesajul ascuns.

## Rezultatele obținute

Codul acoperă toate exercițiile A1-A7 și B1-B6. Am verificat automat decodările, ordinea recunoașterii, straturile multiple și limita buclei, XOR, toate cele trei hash-uri și parola absentă, semnăturile, strings, GPS și emisferele, ZIP, mesajele UTF-8, capacitatea imaginii și marcajul de final. Probele originale nu au fost furnizate de profesor; verificarea efectuată folosește date proprii. Challenge.bin este opțional și nu a fost disponibil.

Comandă: `python -m unittest discover -s teste -v`.

```text
Au fost generate datele demonstrative în demo/.
test_base64 (test_decode.TestDecode.test_base64) ... ok
test_citibil (test_decode.TestDecode.test_citibil) ... ok
test_hash (test_decode.TestDecode.test_hash) ... ok
test_hex_url (test_decode.TestDecode.test_hex_url) ... ok
test_intrare_ambigua (test_decode.TestDecode.test_intrare_ambigua) ... ok
test_recunoastere (test_decode.TestDecode.test_recunoastere) ... ok
test_straturi (test_decode.TestDecode.test_straturi) ... ok
test_xor (test_decode.TestDecode.test_xor) ... ok
test_lsb (test_forensics_stego.TestForensicsStego.test_lsb) ... Laborator_5\stego.py:14: DeprecationWarning: Image.Image.getdata is deprecated and will be removed in Pillow 14 (2027-10-15). Use get_flattened_data instead.
  pixeli = list(img.getdata())
Laborator_5\stego.py:33: DeprecationWarning: Image.Image.getdata is deprecated and will be removed in Pillow 14 (2027-10-15). Use get_flattened_data instead.
  for pixel in img.getdata():
Laborator_5\teste\test_forensics_stego.py:44: DeprecationWarning: Image.Image.getdata is deprecated and will be removed in Pillow 14 (2027-10-15). Use get_flattened_data instead.
  for p, q in zip(a.getdata(), b.getdata()):
ok
test_semnaturi_strings_zip_gps (test_forensics_stego.TestForensicsStego.test_semnaturi_strings_zip_gps) ... ok
test_bytes_si_codari_binare (test_regresii.TestRegresii.test_bytes_si_codari_binare) ... ok
test_cli_fisier_binar (test_regresii.TestRegresii.test_cli_fisier_binar) ... ok
test_hash_spatii_si_utf8 (test_regresii.TestRegresii.test_hash_spatii_si_utf8) ... ok
test_spatii_pastrate (test_regresii.TestRegresii.test_spatii_pastrate) ... ok
test_zip_crc_pastreaza_destinatia (test_regresii.TestRegresii.test_zip_crc_pastreaza_destinatia) ... ok
test_zip_eroare_pastreaza_destinatia (test_regresii.TestRegresii.test_zip_eroare_pastreaza_destinatia) ... ok
test_zip_nu_suprascrie_sursa (test_regresii.TestRegresii.test_zip_nu_suprascrie_sursa) ... ok
test_zip_semnatura_falsa (test_regresii.TestRegresii.test_zip_semnatura_falsa) ... ok

----------------------------------------------------------------------
Ran 18 tests in 0.541s

OK
```

Ieșirile complete ale comenzilor sunt salvate în rezultate/. Fișierele demonstrative sunt în demo/. Laboratoarele anterioare sunt păstrate în copia depozitului, iar .venv și cache-urile sunt ignorate de Git. Nu am executat git push și nu am trimis email.

## Concluzii

Am înțeles diferența dintre text și octeți și am verificat că un mesaj poate avea mai multe codări. XOR cu o cheie de un octet poate fi încercat în întregime, dar alegerea textului rămâne o estimare. Hash-urile se compară cu parole din dicționar. Semnătura reală a fișierului și metadatele pot arăta informații care nu apar la deschiderea normală. Pentru LSB, folosirea PNG și a octetului zero permite recuperarea exactă a mesajului.

## Corecții verificate

Au trecut 18 teste: cele 10 teste inițiale și 8 teste de regresie pentru bytes, codări binare, spații, dicționar UTF-8, antet ZIP fals, destinație păstrată la eroare sau CRC invalid și protejarea sursei. `rezultate/a7_salut.txt` și `demo/fisa_salut.json` documentează același mesaj Salut. Fișa de straturi și arhiva extrasă au fost regenerate din datele demonstrative incluse.
