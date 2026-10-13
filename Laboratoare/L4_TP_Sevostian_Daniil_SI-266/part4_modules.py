# Laborator: funcții, metode și importuri pe web
# Student: Sevostian Daniil
# Grupa: SI-266

import json
import hashlib
import re
import socket
import ssl
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import requests
from webtools import fetch, pause_between_requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde


# Exercițiul 35
def show_url_parts() -> None:
    """Afișează componentele unui URL, fără a trimite o cerere."""
    parsed = urlparse("https://cybercor.org/path?x=1#top")
    print("Scheme:", parsed.scheme)
    print("Netloc:", parsed.netloc)
    print("Path:", parsed.path)
    print("Query:", parsed.query)
    print("Fragment:", parsed.fragment)

# urlparse() descompune adresa în componente accesibile ca atribute.
# query conține x=1, iar fragment conține top, fără semnele ? și #.


# Exercițiul 36
def build_urls() -> list:
    """Transformă cele trei legături relative în URL-uri complete."""
    return [urljoin(BASE_URL, link) for link in ["/about", "contact.html", "../index.html"]]

# urljoin() combină baza și legătura relativă, inclusiv segmentele ../.
# Construim adresele cerute fără să accesăm aceste pagini.


# Exercițiul 37
def extract_links(html: str) -> list:
    """Extrage valorile href fără duplicate, păstrând ordinea lor."""
    return list(dict.fromkeys(re.findall(r'href="([^"]+)"', html)))

# re.findall(r'href="([^"]+)"', html) extrage valorile href.
# dict.fromkeys() elimină duplicatele și păstrează ordinea lor.


# Exercițiul 38
def split_links(links: list, domain: str) -> tuple:
    """Separă legăturile web de pe același domeniu de cele externe."""
    base = domain if "://" in domain else "https://" + domain
    internal, external = [], []
    for link in links:
        absolute = urljoin(base, link)
        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https"):
            continue
        destination = internal if parsed.netloc.lower() == urlparse(base).netloc.lower() else external
        if absolute not in destination:
            destination.append(absolute)
    return internal, external

# urljoin() transformă fiecare legătură într-un URL absolut.
# urlparse().netloc permite compararea domeniilor; nu accesăm legăturile.
# Schemele mailto:, tel: și javascript: nu sunt numărate ca pagini web.


# Exercițiul 39
class ImageFinder(HTMLParser):
    """Parser HTML care colectează sursele imaginilor în ordinea paginii."""

    def __init__(self):
        """Inițializează parserul și lista imaginilor găsite."""
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        """Adaugă atributul src al unui tag img dacă valoarea există."""
        if tag == "img":
            src = dict(attrs).get("src")
            if src:
                self.images.append(src)


def test_image_finder() -> None:
    """Verifică parserul pe HTML cu un rezultat cunoscut înainte de site-ul real."""
    test_html = """
    <html><body>
      <img src="/logo.png" alt="Logo">
      <IMG SRC="poza.jpg">
      <img alt="imagine fără src">
      <img src="https://cdn.example.com/banner.webp" />
      <a href="/despre">Aceasta nu este o imagine</a>
    </body></html>
    """
    finder = ImageFinder()
    finder.feed(test_html)
    print(finder.images)
    assert finder.images == [
        "/logo.png", "poza.jpg", "https://cdn.example.com/banner.webp"
    ], "Parserul nu a găsit exact imaginile așteptate"
    print("Testul a trecut!")


def find_page_images(html: str) -> list:
    """Parsează pagina reală și compară numărul surselor cu numărul tag-urilor img."""
    finder = ImageFinder()
    finder.feed(html)
    print(len(finder.images), "imagini găsite")
    for src in finder.images:
        print(src)
    print("Număr de apariții <img:", html.lower().count("<img"))
    print("Verificare manuală: deschideți cybercor.org și apăsați Ctrl+U.")
    return finder.images

# HTMLParser apelează automat handle_starttag() când feed() întâlnește un tag.
# Parserul normalizează tag-urile și numele atributelor scrise cu majuscule.
# O listă goală poate fi corectă dacă imaginile sunt afișate prin CSS sau SVG.
# Numărul tag-urilor poate fi mai mare dacă unele imagini nu au src.


# Exercițiul 40
def page_fingerprint(url: str) -> str:
    """Returnează amprenta SHA-256 a conținutului paginii."""
    response = fetch(url)
    response.raise_for_status()
    return hashlib.sha256(response.content).hexdigest()


def compare_fingerprints() -> None:
    """Descarcă pagina de două ori și compară amprentele SHA-256."""
    first = page_fingerprint(BASE_URL)
    second = page_fingerprint(BASE_URL)
    print("Prima amprentă:", first)
    print("A doua amprentă:", second)
    print("Amprente identice:", first == second)

# page_fingerprint() folosește hashlib.sha256(response.content).
# Amprentele diferă dacă se modifică oricare octet, inclusiv conținutul dinamic.
# fetch() pune o pauză între cele două cereri.


# Exercițiul 41
def save_headers() -> dict:
    """Salvează antetele în headers.json, apoi le citește înapoi."""
    from pathlib import Path
    response = fetch(BASE_URL)
    response.raise_for_status()
    output = Path(__file__).resolve().parent / "headers.json"
    with output.open("w", encoding="utf-8") as file:
        json.dump(dict(response.headers), file, indent=2, ensure_ascii=False)
    with output.open(encoding="utf-8") as file:
        headers = json.load(file)
    print("Content-Type:", requests.structures.CaseInsensitiveDict(headers).get(
        "Content-Type", "lipsește"))
    return headers

# json.dump() scrie dicționarul în fișier, iar json.load() îl reconstruiește.
# Fișierul este salvat lângă program, indiferent de directorul terminalului.
# În JSON cheile sunt obișnuite; CaseInsensitiveDict permite căutarea antetelor.


# Exercițiul 42
def resolve(hostname: str) -> str:
    """Returnează adresa IPv4 a domeniului prin DNS."""
    return socket.gethostbyname(hostname)


def show_ip() -> None:
    """Afișează adresa IPv4 a domeniului cybercor.org."""
    print("Adresă IP:", resolve("cybercor.org"))

# resolve() folosește socket.gethostbyname(hostname).
# Adresa IP este obținută prin DNS și poate fi diferită în timp.


# Exercițiul 43
def cert_days_left(hostname: str) -> int:
    """Returnează zilele până la expirarea certificatului TLS validat."""
    pause_between_requests()
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
            certificate = secure_sock.getpeercert()
    expiration = datetime.fromtimestamp(
        ssl.cert_time_to_seconds(certificate["notAfter"]), timezone.utc
    )
    return (expiration - datetime.now(timezone.utc)).days


def show_certificate() -> None:
    """Afișează numărul zilelor rămase până la expirarea certificatului TLS."""
    print("Certificat:", cert_days_left("cybercor.org"), "zile rămase")

# cert_days_left() folosește ssl.create_default_context() și conexiunea la 443.
# wrap_socket() validează certificatul pentru server_hostname.
# getpeercert()["notAfter"] este convertit cu ssl.cert_time_to_seconds().
# Diferența se calculează față de momentul curent în UTC, cu timeout de 10 secunde.


def run_exercises() -> None:
    """Rulează exercițiile 35–43 și afișează erorile fără opriri neașteptate."""
    print("Ex. 35")
    show_url_parts()
    print("Ex. 36:", build_urls())
    print("Ex. 39. Test local")
    test_image_finder()
    try:
        response = fetch(BASE_URL)
        response.raise_for_status()
        links = extract_links(response.text)
        print("Ex. 37. Legături:", links)
        internal, external = split_links(links, BASE_URL)
        print("Ex. 38. Interne:", internal)
        print("Ex. 38. Externe:", external)
        print("Ex. 39. Pagina reală")
        find_page_images(response.text)
    except requests.RequestException as error:
        print("Ex. 37–39. Cererea nu a reușit:", error)
    for number, exercise in [(40, compare_fingerprints), (41, save_headers),
                             (42, show_ip), (43, show_certificate)]:
        print(f"Ex. {number}")
        try:
            exercise()
        except (requests.RequestException, OSError, ValueError, KeyError) as error:
            print("Nu s-a putut efectua verificarea:", error)


if __name__ == "__main__":
    run_exercises()
