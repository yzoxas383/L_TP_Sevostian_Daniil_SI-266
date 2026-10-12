# Laborator: funcții, metode și importuri pe web
# Student: Sevostian Daniil
# Grupa: SI-266

import hashlib
import json
import re
import socket
import ssl
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde
OUTPUT_DIR = Path(__file__).resolve().parent
SECURITY_HEADERS = (
    "Strict-Transport-Security", "Content-Security-Policy",
    "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy",
)

# Exercițiul 47
DEFAULT_HEADERS = {"User-Agent": "WebLab-Sevostian-Daniil"}
# Constanta păstrează antetele folosite de funcția fetch().
# Regulile laboratorului permit antete personalizate doar către httpbin.org.

_last_request = None


def pause_between_requests() -> None:
    """Așteaptă o secundă între cererile consecutive ale acestui modul."""
    global _last_request
    if _last_request is not None:
        time.sleep(1)
    _last_request = time.perf_counter()


# Exercițiul 44
def fetch(url: str, timeout: float = TIMEOUT) -> requests.Response:
    """Descarcă un URL prin GET, cu timeout și pauză între cereri."""
    pause_between_requests()
    headers = DEFAULT_HEADERS if urlparse(str(url)).hostname == "httpbin.org" else None
    return requests.get(url, timeout=timeout, headers=headers)


def get_status(url: str) -> int:
    """Returnează codul de stare HTTP al adresei primite."""
    return fetch(url).status_code


def get_title(html: str) -> str:
    """Extrage și curăță titlul HTML; returnează un șir gol dacă lipsește."""
    start = html.lower().find("<title>")
    if start == -1:
        return ""
    start += len("<title>")
    end = html.lower().find("</title>", start)
    if end == -1:
        return ""
    return html[start:end].strip()


def security_headers(url: str) -> dict:
    """Verifică prezența celor cinci antete de securitate cerute."""
    response = fetch(url)
    response.raise_for_status()
    return {name: name in response.headers for name in SECURITY_HEADERS}

# Funcțiile sunt definite în modul și pot fi importate din alte fișiere.
# Importarea modulului nu execută automat demonstrațiile din laborator.


def score_headers(results: dict) -> str:
    """Returnează numărul antetelor prezente față de numărul verificat."""
    return f"{sum(results.values())}/{len(results)}"


def check_paths(base: str, paths: list) -> dict:
    """Returnează codul HTTP pentru fiecare cale; None indică eroare de rețea."""
    results = {}
    for path in paths:
        try:
            results[path] = get_status(urljoin(base, path))
        except requests.RequestException as error:
            print(f"Nu pot verifica {path}: {error}")
            results[path] = None
    return results


def fetch_robots(base: str):
    """Returnează robots.txt sau None dacă lipsește ori nu poate fi citit."""
    try:
        response = fetch(urljoin(base, "/robots.txt"))
        if not response.ok or "<html" in response.text.lower():
            return None
        return response.text
    except requests.RequestException:
        return None


def disallowed_paths(robots_text) -> list:
    """Extrage toate valorile ne-goale Disallow, ignorând comentariile."""
    paths = []
    for line in (robots_text or "").splitlines():
        line = line.split("#", 1)[0].strip()
        name, separator, value = line.partition(":")
        if separator and name.strip().lower() == "disallow" and value.strip():
            paths.append(value.strip())
    return paths


def extract_links(html: str) -> list:
    """Returnează legăturile href între ghilimele duble, fără duplicate."""
    return list(dict.fromkeys(re.findall(r'href="([^"]+)"', html)))


def split_links(links: list, domain: str) -> tuple:
    """Separă URL-urile HTTP/HTTPS interne de cele externe, fără a le accesa."""
    base = domain if "://" in domain else "https://" + domain
    target = urlparse(base).netloc.lower()
    internal, external = [], []
    for link in links:
        absolute = urljoin(base, link)
        parsed = urlparse(absolute)
        if parsed.scheme not in ("http", "https"):
            continue  # mailto:, tel: și javascript: nu sunt pagini web.
        destination = internal if parsed.netloc.lower() == target else external
        if absolute not in destination:
            destination.append(absolute)
    return internal, external


def page_fingerprint(url: str) -> str:
    """Returnează amprenta SHA-256 a octeților paginii."""
    response = fetch(url)
    response.raise_for_status()
    return hashlib.sha256(response.content).hexdigest()


def resolve(hostname: str) -> str:
    """Returnează adresa IPv4 obținută prin DNS pentru domeniu."""
    return socket.gethostbyname(hostname)


def cert_days_left(hostname: str) -> int:
    """Citește certificatul TLS validat și calculează zilele până la expirare."""
    pause_between_requests()
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as secure_sock:
            certificate = secure_sock.getpeercert()
    expiration = datetime.fromtimestamp(
        ssl.cert_time_to_seconds(certificate["notAfter"]), timezone.utc
    )
    return (expiration - datetime.now(timezone.utc)).days


# Exercițiul 50
def site_report(url: str) -> dict:
    """Colectează, afișează și salvează raportul site-ului în report.json."""
    report = {"requested_url": url, "checked_at": datetime.now().astimezone().isoformat(),
              "errors": {}}
    response = None
    try:
        response = fetch(url)
        report.update(status_code=response.status_code, final_url=response.url,
                      title=get_title(response.text))
        if not response.ok:
            report["errors"]["page"] = f"HTTP {response.status_code}"
    except requests.RequestException as error:
        report.update(status_code=None, final_url=None, title=None)
        report["errors"]["page"] = str(error)

    hostname = urlparse(url).hostname
    try:
        report["ip_address"] = resolve(hostname)
    except OSError as error:
        report["ip_address"] = None
        report["errors"]["dns"] = str(error)

    http_url = urlunparse(urlparse(url)._replace(scheme="http"))
    try:
        redirected = fetch(http_url)
        report["redirects"] = [
            {"status": item.status_code, "url": item.url,
             "location": item.headers.get("Location")}
            for item in redirected.history
        ]
        report["redirect_final_url"] = redirected.url
        report["redirect_final_status"] = redirected.status_code
    except requests.RequestException as error:
        report["redirects"] = []
        report["redirect_final_url"] = None
        report["redirect_final_status"] = None
        report["errors"]["redirects"] = str(error)

    try:
        report["security_headers"] = security_headers(url)
        report["security_score"] = score_headers(report["security_headers"])
    except requests.RequestException as error:
        report["security_headers"] = None
        report["security_score"] = None
        report["errors"]["security"] = str(error)

    try:
        report["certificate_days_left"] = cert_days_left(hostname)
    except (OSError, ValueError, KeyError) as error:
        report["certificate_days_left"] = None
        report["errors"]["certificate"] = str(error)

    if response is not None and response.ok:
        internal, external = split_links(extract_links(response.text), response.url)
        report["internal_links"] = len(internal)
        report["external_links"] = len(external)
    else:
        report["internal_links"] = report["external_links"] = None
    robots_text = fetch_robots(url)
    report["disallowed_paths"] = disallowed_paths(robots_text)
    report["robots_available"] = robots_text is not None

    print(f"=== Raport site: {url} ===")
    print("Cod de stare:", report["status_code"])
    print("URL final:", report["final_url"])
    print("Titlu:", report["title"])
    print("Adresă IP:", report["ip_address"])
    print("Redirecționări:", report["redirects"])
    print("URL final de la HTTP:", report["redirect_final_url"])
    print("Cod final de la HTTP:", report["redirect_final_status"])
    print("Scor securitate:", report["security_score"])
    print("Certificat:", report["certificate_days_left"], "zile rămase")
    print("Legături:", report["internal_links"], "interne,",
          report["external_links"], "externe")
    print("Căi interzise:", report["disallowed_paths"])
    for component, error in report["errors"].items():
        print(f"Nu s-a putut verifica {component}: {error}")
    with (OUTPUT_DIR / "report.json").open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
    print("Salvat în report.json")
    return report

# site_report() refolosește funcțiile pentru descărcare, titlu, DNS,
# redirecționări, antete, certificat, legături și robots.txt.
# Erorile reale sunt salvate separat; o valoare necunoscută devine null în JSON.
# Legăturile și căile Disallow sunt analizate, fără a fi accesate.


# Exercițiul 46
if __name__ == "__main__":
    try:
        print("Autotest:", get_status("https://cybercor.org"))
    except requests.RequestException as error:
        print("Autotest: cererea nu a reușit:", error)

# La rularea python webtools.py, __name__ are valoarea "__main__".
# La import webtools, __name__ este "webtools", deci autotestul nu rulează.
