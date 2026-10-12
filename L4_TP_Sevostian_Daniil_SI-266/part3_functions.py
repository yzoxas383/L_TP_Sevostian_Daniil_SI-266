# Laborator: funcții, metode și importuri pe web
# Student: Sevostian Daniil
# Grupa: SI-266

import time
import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde
_last_request = None


def pause_between_requests() -> None:
    """Pune o pauză de o secundă între cererile consecutive."""
    global _last_request
    if _last_request is not None:
        time.sleep(1)
    _last_request = time.perf_counter()


# Exercițiul 21
def fetch(url: str) -> requests.Response:
    """Returnează răspunsul GET pentru URL-ul primit."""
    pause_between_requests()
    return requests.get(url, timeout=TIMEOUT)

try:
    response = fetch(BASE_URL)
    print("Ex. 21. Cod de stare:", response.status_code)
except requests.RequestException as error:
    print("Ex. 21. Cererea nu a reușit:", error)

# fetch() primește adresa ca parametru și returnează întregul răspuns.
# Din obiectul returnat putem citi status_code, text și headers.


# Exercițiul 22
def get_status(url: str) -> int:
    """Returnează numai codul de stare HTTP al paginii."""
    return fetch(url).status_code

for path in ["/", "/robots.txt", "/sitemap.xml"]:
    try:
        print("Ex. 22.", path, get_status(BASE_URL + path))
    except requests.RequestException as error:
        print("Ex. 22.", path, error)

# get_status() returnează un int, spre deosebire de fetch().
# Funcția pause_between_requests() aplică time.sleep(1) între apeluri.


# Exercițiul 23
def fetch(url: str, timeout: float = 10) -> requests.Response:
    """Returnează răspunsul GET, cu un timeout configurabil."""
    pause_between_requests()
    return requests.get(url, timeout=timeout)

for timeout in [TIMEOUT, 3]:
    try:
        response = fetch(BASE_URL) if timeout == TIMEOUT else fetch(BASE_URL, timeout=3)
        print("Ex. 23. Timeout:", timeout, "| Status:", response.status_code)
    except requests.RequestException as error:
        print("Ex. 23. Cererea nu a reușit:", error)

# Noua definiție înlocuiește funcția fetch() din exercițiul 21.
# Fără argumentul timeout se folosesc 10 secunde; timeout=3 schimbă valoarea.


# Exercițiul 24
def get_title(html: str) -> str:
    """Extrage titlul HTML; returnează un șir gol dacă tag-urile lipsesc."""
    start = html.lower().find("<title>")
    if start == -1:
        return ""
    start += len("<title>")
    end = html.lower().find("</title>", start)
    return html[start:end].strip() if end != -1 else ""

try:
    html = fetch(BASE_URL).text
    print("Ex. 24. Titlu:", get_title(html))
except requests.RequestException as error:
    print("Ex. 24. Cererea nu a reușit:", error)

# .find() găsește tag-urile, slicing extrage titlul, iar .strip() îl curăță.
# Funcția primește HTML deja descărcat și nu efectuează cereri de rețea.


# Exercițiul 25
def show_title_help() -> None:
    """Afișează documentația funcției get_title()."""
    help(get_title)

show_title_help()
# Docstring-ul este textul dintre triple ghilimele de la începutul funcției.
# help(get_title) afișează semnătura și explicația scrisă în docstring.


# Exercițiul 26
def demonstrate_type_hints() -> None:
    """Arată că adnotările nu verifică automat tipurile la rulare."""
    try:
        print(get_status(123))
    except requests.RequestException as error:
        print("Ex. 26. Eroare pentru get_status(123):", type(error).__name__)

demonstrate_type_hints()
# Adnotările str și int documentează tipurile și ajută editorul.
# Python permite apelul get_status(123); requests respinge URL-ul fără schemă.
# Eroarea vine din biblioteca requests, nu din verificarea adnotărilor.


# Exercițiul 27
def page_exists(url: str) -> bool:
    """Returnează True pentru un răspuns reușit și False la orice eroare de cerere."""
    try:
        return fetch(url).ok
    except requests.RequestException:
        return False

print("Ex. 27. Pagina principală:", page_exists(BASE_URL))
print("Ex. 27. Domeniu invalid:", page_exists("https://this-domain-does-not-exist.invalid"))
# try / except împiedică oprirea programului la o eroare de conexiune.
# .ok verifică succesul HTTP, dar un site poate răspunde 200 și pentru o cale absentă.


# Exercițiul 28
def check_paths(base: str, paths: list) -> dict:
    """Returnează {cale: cod HTTP}; None înseamnă că cererea a eșuat."""
    results = {}
    for path in paths:
        try:
            results[path] = get_status(base.rstrip("/") + "/" + path.lstrip("/"))
        except requests.RequestException as error:
            print("Nu pot verifica", path, error)
            results[path] = None
    return results

print("Ex. 28.", check_paths(BASE_URL, ["/", "/robots.txt", "/sitemap.xml"]))
# Dicționarul asociază fiecare cale cu răspunsul serverului.
# Pauzele se aplică în fetch(), inclusiv pentru cererile din buclă.


# Exercițiul 29
def get_header(url: str, name: str, default: str = "lipsește") -> str:
    """Returnează valoarea antetului sau valoarea implicită dacă lipsește."""
    return fetch(url).headers.get(name, default)

try:
    print("Ex. 29. Server:", get_header(BASE_URL, name="Server"))
except requests.RequestException as error:
    print("Ex. 29. Cererea nu a reușit:", error)
# name="Server" este un argument cu nume, deci sensul său este vizibil în apel.
# .get() evită KeyError atunci când antetul nu există.


# Exercițiul 30
def security_headers(url: str) -> dict:
    """Returnează prezența celor cinci antete de securitate."""
    names = ["Strict-Transport-Security", "Content-Security-Policy",
             "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy"]
    response = fetch(url)
    response.raise_for_status()
    return {name: name in response.headers for name in names}

try:
    print("Ex. 30.", security_headers(BASE_URL))
except requests.RequestException as error:
    print("Ex. 30. Cererea nu a reușit:", error)
# Operatorul in verifică dacă fiecare nume se află în antetele răspunsului.
# Verificăm doar prezența antetelor, nu corectitudinea configurației lor.


# Exercițiul 31
def score_headers(results: dict) -> str:
    """Returnează scorul antetelor prezente în forma număr/total."""
    return f"{sum(results.values())}/{len(results)}"

try:
    print("Ex. 31. Scor:", score_headers(security_headers(BASE_URL)))
except requests.RequestException as error:
    print("Ex. 31. Cererea nu a reușit:", error)
# True este numărat ca 1, iar False ca 0 de către sum().
# Rezultatul security_headers() devine argument pentru score_headers().


# Exercițiul 32
def fetch_robots(base: str):
    """Returnează textul robots.txt sau None dacă nu este disponibil."""
    try:
        response = fetch(base.rstrip("/") + "/robots.txt")
        if not response.ok or "<html" in response.text.lower():
            return None
        return response.text
    except requests.RequestException:
        return None


def disallowed_paths(robots_text) -> list:
    """Extrage valorile Disallow ne-goale, inclusiv când textul este None."""
    paths = []
    for line in (robots_text or "").splitlines():
        name, separator, value = line.split("#", 1)[0].partition(":")
        if separator and name.strip().lower() == "disallow" and value.strip():
            paths.append(value.strip())
    return paths

print("Ex. 32. Căi interzise:", disallowed_paths(fetch_robots(BASE_URL)))
print("Ex. 32. Pentru None:", disallowed_paths(None))
# Descărcarea și analiza sunt separate în două funcții.
# Disallow fără valoare nu interzice o cale, deci este ignorat.
# Nu accesăm căile găsite în robots.txt.


# Exercițiul 33
def response_times(*urls: str) -> dict:
    """Returnează timpul total al fiecărei cereri, fără pauza dintre cereri."""
    results = {}
    for url in urls:
        pause_between_requests()
        start = time.perf_counter()
        try:
            requests.get(url, timeout=TIMEOUT)
            results[url] = time.perf_counter() - start
        except requests.RequestException as error:
            print("Nu pot cronometra", url, error)
            results[url] = None
    return results

print("Ex. 33.", response_times(BASE_URL, BASE_URL + "/robots.txt"))
# *urls colectează oricâte argumente poziționale într-un tuplu.
# perf_counter() măsoară durata cererii; pauza este făcută înainte de cronometrare.


# Exercițiul 34
def log(message: str, **details) -> None:
    """Afișează mesajul și detaliile primite ca argumente cu nume."""
    values = [message] + [f"{key}={value}" for key, value in details.items()]
    print(" | ".join(values))

log("verificat", url=BASE_URL, status=200)
# **details colectează argumentele cu nume într-un dicționar.
# print() doar afișează o valoare; return o trimite înapoi apelantului.
# O valoare returnată poate fi salvată sau transmisă unei alte funcții.
