# Laboratorul 5

Sevostian Daniil, SI-266. Codul, mesajele și raportul sunt în limba română.
Toate cele 13 exerciții sunt implementate și testate pe date demonstrative proprii.
**Profesorul nu a furnizat probele originale sau generatorul. Folosim date proprii din demo/.** Nu prezentați
rezultatele din demo/ drept rezultate ale probelor profesorului.

## Rulare în Windows PowerShell

```powershell
cd D:\laboratoare\TP_Sevostian_Daniil_SI-266\Laborator_5
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
..\.venv\Scripts\python.exe demo/pregateste_demo.py
..\.venv\Scripts\python.exe arsenal/forensics/decode.py --mod a1
..\.venv\Scripts\python.exe arsenal/forensics/decode.py demo/mesaj.txt --fisier
..\.venv\Scripts\python.exe arsenal/forensics/decode.py demo/xor.bin --mod xor --fisa demo/fisa_xor.json
..\.venv\Scripts\python.exe arsenal/forensics/decode.py demo/hashuri.txt --fisier --mod hash --wordlist demo/wordlist.txt --fisa demo/fisa_hash.json
..\.venv\Scripts\python.exe forensics.py --probe demo
..\.venv\Scripts\python.exe stego.py ascunde demo/foto.jpg
..\.venv\Scripts\python.exe stego.py dezvaluie stego.png
..\.venv\Scripts\python.exe -m unittest discover -s teste -v
```

Mediul existent folosește Python 3.12.14 cu Pillow 12.3.0 disponibile local.
La mutarea pe alt calculator, creați un mediu nou cu Python 3.12 instalat:

```powershell
cd D:\laboratoare\TP_Sevostian_Daniil_SI-266
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r Laborator_5/requirements.txt
```

## După primirea fișierelor originale

Copiați scriptul profesorului în probe/pregateste.py și dicționarul în probe/wordlist.txt.
Din Laborator_5 rulați comenzile de mai jos și actualizați raportul cu ieșirile reale:

```powershell
..\.venv\Scripts\python.exe probe/pregateste.py
..\.venv\Scripts\python.exe arsenal/forensics/decode.py probe/mesaj.txt --fisier
..\.venv\Scripts\python.exe arsenal/forensics/decode.py probe/xor.bin --mod xor --fisa probe/fisa_xor.json
..\.venv\Scripts\python.exe arsenal/forensics/decode.py probe/hashuri.txt --fisier --mod hash --wordlist probe/wordlist.txt --fisa probe/fisa_hash.json
..\.venv\Scripts\python.exe forensics.py
..\.venv\Scripts\python.exe stego.py ascunde probe/foto.jpg
..\.venv\Scripts\python.exe stego.py dezvaluie stego.png
```

## Predarea prin Git

Depozitul copiat păstrează origin și istoria Git. Laboratoarele 1-4 nu au fost modificate.
În sursa locală, fișierele laboratorului 4 erau deja neînregistrate în Git; în copie au rămas la fel.
Nu a fost creat un commit și nu a fost executat push.
După verificarea probelor originale și a raportului:

```powershell
cd D:\laboratoare\TP_Sevostian_Daniil_SI-266
git status --short
git add -- .gitignore Laborator_5
git diff --cached --stat
git commit -m "Lab 5: decoder universal + forensics si stego"
# Numai după confirmarea proprietarului:
git push origin main
git rev-parse --short HEAD
```

Fișa cere și anunțarea profesorului prin email după push, cu linkul depozitului
și codul commitului. Emailul nu a fost trimis. Verificați separat accesul profesorului
la depozitul privat. Structura completă a laboratorului este în STRUCTURA.txt.

## Corecții și verificări suplimentare

`--fisier` citește octeți. Fișa indică `format: utf-8` pentru text și `format: hex` pentru date binare; rezultatul HEX se reface cu `bytes.fromhex`. Spațiile din text sunt păstrate. Pentru un dicționar UTF-8, folosiți `--wordlist-encoding utf-8`; implicit rămâne Latin-1 conform exemplului din fișa de laborator.

Carving identifică antetele din directorul central al ZIP-ului, verifică CRC înainte de scriere și păstrează destinația la eroare. Sursa și destinația identice sunt respinse. Testele de regresie sunt în `teste/test_regresii.py`.

Dacă probele originale lipsesc, `forensics.py` folosește implicit `demo/`, iar decoderul selectează dicționarul demonstrativ disponibil. `--probe` și `--wordlist` permit alegerea explicită.
