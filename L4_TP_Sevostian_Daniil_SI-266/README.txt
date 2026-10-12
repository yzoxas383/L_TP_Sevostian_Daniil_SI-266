Laborator L4 — Sevostian Daniil, SI-266

Deschideți directorul web_lab în Visual Studio Code.
În terminal, cu Python 3.9 sau mai nou:
  python -m pip install -r requirements.txt
  python part3_functions.py
  python part4_modules.py
  python webtools.py
  python main.py https://cybercor.org
  python bonus_functions.py

Părțile 1 și 2 sunt fișierele originale ale studentului.
Partea 5 este implementată în webtools.py și main.py, conform cerințelor.
Fiecare exercițiu nou are explicații în comentarii, în limba română.
Partea 4 conține soluțiile; webtools.py păstrează variantele reutilizabile.
headers.json, report.csv și report.json se salvează lângă programe.

Nu se accesează automat legăturile descoperite sau căile Disallow.
Toate cererile noi folosesc timeout și pauze de o secundă.
Erorile de rețea sunt afișate; valorile necunoscute în raport sunt null.
Un status 200 pentru robots.txt poate fi o pagină HTML de rezervă.
În acest caz, fișierul robots.txt este considerat indisponibil.

Arhiva de predare: L4_TP_Sevostian_Daniil_SI-266.zip
Subiectul emailului: L4_TP_Sevostian_Daniil_SI-266
