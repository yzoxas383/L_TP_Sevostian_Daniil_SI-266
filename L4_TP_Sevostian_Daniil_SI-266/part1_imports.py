# Laborator: funcții, metode și importuri pe web
# Student: Sevostian Daniil
# Grupa: SI-266

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 5 # secunde


#exercitiul 1

import requests

print("Versiunea requests:", requests.__version__)

import urllib.request
# requests este o bibliotecă externă și trebuie instalată cu pip install requests.
# urllib face parte din biblioteca standard Python și nu necesită instalare separată.

#exercitiul 2

response = requests.get(BASE_URL, timeout=TIMEOUT)
print("Cod de stare:", response.status_code)

from requests import get

response = get(BASE_URL, timeout=TIMEOUT)
print("Cod de stare (from requests import get):", response.status_code)

# requests.get este mai clar deoarece se vede modulul folosit.
# from requests import get este mai scurt, deoarece putem apela direct funcția get().

#exercitiul 3

import requests as rq

response = rq.get(BASE_URL, timeout=TIMEOUT)
print("Cod de stare cu alias rq:", response.status_code)

# Alias-ul face codul mai ușor de citit când numele este scurt și folosit des.
# Un alias poate face codul mai greu de citit dacă numele ales nu este clar.

#exercițiul 4

request = urllib.request.Request(
    BASE_URL,
    headers={"User-Agent": "Mozilla/5.0"}
)

response_urllib = urllib.request.urlopen(request, timeout=TIMEOUT)

print("Cod de stare urllib:", response_urllib.status)

body = response_urllib.read().decode("utf-8")
print("Primele 200 de caractere:")
print(body[:200])

# urllib.request.Request creează o cerere către site și adaugă un User-Agent.
# urlopen() trimite cererea și primește răspunsul de la server.
# .status afișează codul de stare HTTP.
# .read() citește conținutul paginii în bytes, iar .decode("utf-8") îl transformă în text.
# body[:200] afișează primele 200 de caractere din pagina HTML.

#exercitiul 5

print(dir(requests))

# dir(requests) afișează toate numele disponibile în modulul requests,
# cum ar fi funcții, clase și alte module.

# get - funcție, este folosită pentru a trimite cereri HTTP de tip GET.
# Session - clasă, este folosită pentru a crea și gestiona o sesiune HTTP.
# exceptions - modul, conține excepțiile și erorile folosite de requests.

#exercitiul 6

help(requests.get)

response = requests.get(BASE_URL, timeout=TIMEOUT)
print("Cod de stare cu timeout:", response.status_code)

# help(requests.get) afișează documentația funcției get().
# Parametrul timeout stabilește timpul maxim de așteptare pentru cerere.
# În acest caz, TIMEOUT = 10, deci cererea are un timeout de 10 secunde.

#exercitiul 7

import time 
start = time.perf_counter()

response = requests.get(BASE_URL, timeout=TIMEOUT)

end = time.perf_counter()

durata = end - start

print("Timp masurat cu perf_counter:", durata, "secunde")
print("Timp raportat de response.elapsed:", response.elapsed.total_seconds(), "secunde")

# time.perf_counter() măsoară timpul înainte și după efectuarea cererii.
# Diferența dintre end și start reprezintă timpul total al cererii.
# response.elapsed arată timpul măsurat de biblioteca requests pentru primirea răspunsului.
# Valorile pot fi apropiate, dar nu trebuie să fie exact egale.

#exercițiul 8

try:
    import bs4
    print("Modulul bs4 este instalat.")
except ImportError:
    print("Instalați modulul cu: pip install beautifulsoup4")

# Blocul try încearcă să importe modulul bs4.
# Dacă modulul nu este instalat, apare ImportError și se execută blocul except.
# Astfel, programul nu se oprește cu eroare și afișează comanda necesară pentru instalare.

# Modulul este un singur fișier Python care conține cod reutilizabil.
# Pachetul este o colecție de module Python organizate împreună.
# Biblioteca este o colecție mai mare de module și pachete folosite pentru anumite sarcini.