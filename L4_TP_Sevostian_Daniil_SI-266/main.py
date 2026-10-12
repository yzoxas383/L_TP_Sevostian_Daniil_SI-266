# Laborator: funcții, metode și importuri pe web
# Student: Sevostian Daniil
# Grupa: SI-266

import argparse
import csv
from datetime import datetime
from pathlib import Path

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

# Exercițiul 44
import webtools


def demonstrate_module(url: str) -> None:
    """Apelează funcțiile din modul folosind numele webtools."""
    print("Ex. 44. Titlu:", webtools.get_title(webtools.fetch(url).text))

# import webtools permite apeluri în forma webtools.nume_funcție().
# Funcția este apelată din main() cu URL-ul primit din linia de comandă.


# Exercițiul 45
from webtools import get_title, security_headers


def demonstrate_named_imports(url: str) -> None:
    """Apelează direct funcțiile importate din webtools."""
    print("Ex. 45. Titlu:", get_title(webtools.fetch(url).text))
    print("Ex. 45. Antete:", security_headers(url))

# from webtools import ... permite apelarea fără prefixul webtools.
# Dacă definim după import o funcție proprie get_title, ea înlocuiește numele importat.
# Dacă importul vine după definiția proprie, numele importat o înlocuiește pe aceasta.
# webtools.get_title rămâne accesibil prin numele modulului în ambele cazuri.


# Exercițiul 46
# Blocul de autotest se află la finalul webtools.py.
# python webtools.py îl execută deoarece __name__ este "__main__".
# python main.py importă modulul cu __name__ == "webtools" și nu execută autotestul.


# Exercițiul 47
from webtools import DEFAULT_HEADERS


def show_default_headers() -> None:
    """Afișează constanta importată și verifică antetul pe httpbin."""
    print("Ex. 47. DEFAULT_HEADERS:", DEFAULT_HEADERS)
    response = webtools.fetch(ECHO_URL + "/headers")
    response.raise_for_status()
    actual = response.json()["headers"].get("User-Agent")
    print("User-Agent primit de httpbin:", actual)
    print("Antet confirmat:", actual == DEFAULT_HEADERS["User-Agent"])

# Constanta este definită o singură dată în webtools și reutilizată la import.
# fetch() trimite acest User-Agent către httpbin, conform regulilor laboratorului.


# Exercițiul 48
def parse_arguments():
    """Citește URL-ul primit din linia de comandă."""
    parser = argparse.ArgumentParser(description="Raport despre un site web")
    parser.add_argument("url", nargs="?", default=BASE_URL,
                        help="URL-ul site-ului (implicit: https://cybercor.org)")
    arguments = parser.parse_args()
    parsed = webtools.urlparse(arguments.url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        parser.error("Folosiți un URL complet, cu http:// sau https://.")
    return arguments

# argparse citește argumentul URL, iar main() îl transmite funcțiilor.
# Exemplu: python main.py https://cybercor.org
# Dacă argumentul lipsește, este folosit BASE_URL.


# Exercițiul 49
def save_csv_report(url: str) -> dict:
    """Verifică cele trei căi și salvează coloanele path, status, checked_at."""
    results = webtools.check_paths(url, ["/", "/robots.txt", "/sitemap.xml"])
    checked_at = datetime.now().isoformat()
    output = Path(__file__).resolve().parent / "report.csv"
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["path", "status", "checked_at"])
        writer.writeheader()
        for path, status in results.items():
            writer.writerow({"path": path, "status": status, "checked_at": checked_at})
    print("Ex. 49. Salvat în report.csv:", results)
    return results

# DictWriter scrie câte un rând pentru fiecare cale verificată.
# newline="" evită liniile goale suplimentare în CSV pe Windows.
# datetime.now().isoformat() scrie data și ora în format ISO.


# Exercițiul 50
def main() -> None:
    """Rulează demonstrațiile din partea 5 și generează rapoartele site-ului."""
    arguments = parse_arguments()
    for exercise in [demonstrate_module, demonstrate_named_imports]:
        try:
            exercise(arguments.url)
        except requests.RequestException as error:
            print("Cererea nu a reușit:", error)
    try:
        show_default_headers()
    except (requests.RequestException, ValueError, KeyError) as error:
        print("Nu pot confirma antetul pe httpbin:", error)
    save_csv_report(arguments.url)
    webtools.site_report(arguments.url)

# site_report() se află în webtools.py și refolosește funcțiile laboratorului.
# La rularea programului sunt create report.csv și report.json în web_lab.


if __name__ == "__main__":
    main()
