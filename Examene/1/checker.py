import requests

SITES = [
    # Pagini obișnuite (Părțile 2, 3 și 4)
    "https://example.com",
    "https://httpbin.org/html",
    "https://httpbin.org/json",
    "https://httpbin.org/status/200",
    "https://httpbin.org/redirect/1",
    "https://httpbin.org/delay/2",
    # Pagini care eșuează
    "https://httpbin.org/status/404",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
    "http://this-site-does-not-exist.invalid",
    # Anteturi de securitate (Partea 5)
    "https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff",
    "https://httpbin.org/response-headers?x-frame-options=DENY",
    # Răspunde aleatoriu cu 200 sau 500 (Partea 6)
    "https://httpbin.org/status/200,500",
]

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
]


def build_url(host, path):
    """Returnează o adresă completă, de exemplu https://example.com/login."""
    if not path.startswith("/"):
        path = "/" + path
    return "https://" + host + path


def is_https(url):
    """Returnează True dacă adresa începe cu https://, altfel False."""
    return url.startswith("https://")


def show_response(url):
    """Trimite un GET la url și afișează statusul și Content-Type."""
    try:
        r = requests.get(url, timeout=5)
        print("Status:", r.status_code)
        print ("Content-type:",
               r.headers.get("Content-Type", "unknown") )
    except requests.RequestException as e:
        print("Eroare:", e)


def check_site(url):
    """Returnează un dicționar cu: status, content_type, length, server."""
    try:
        r = requests.get(url, timeout=5)
        rezultat = {
            "status": r.status_code,
            "content_type": r.headers.get("Content-Type", "unknown"),
            "length": len(r.content),
            "server": r.headers.get("Server", "unknown"),
        }
        return rezultat

    except requests.RequestException as e:
        return {
            "status": None,
            "error": str(e)
        }


def scan_sites():
    """Verifică toate site-urile din SITES, afișează-le pe cele care merg și un rezumat."""
    rezultate = []

    for url in SITES:
        rezultat = check_site(url)
        rezultat["url"] = url
        rezultate.append(rezultat)
    reusite = []

    for rezultat in rezultate:
        if rezultat.get("status") == 200:
            reusite.append(rezultat)
    reusite.sort(key=lambda x: x["length"], reverse=True)
    for rezultat in reusite:
        print(rezultat["url"], "->", rezultat["status"], ",", rezultat["length"], "octeti")
    print("Reusite:", len(reusite), "| Esuate", len(rezultate) - len(reusite))
              

def check_headers(url):
    """Returnează un dicționar cu: present, missing, score."""
    try:
        r = requests.get(url, timeout=5)

        present = []
        missing = []

        for header in SECURITY_HEADERS:
            if header in r.headers:
                present.append(header)
            else:
                missing.append(header)

        score = int(len(present) / len(SECURITY_HEADERS) * 100)

        return {
            "present": present,
            "missing": missing,
            "score": score
        }

    except requests.RequestException as e:
        return {
            "status": None,
            "error": str(e)
        }


def retry_check(url, attempts=3):
    """Încearcă de cel mult `attempts` ori; returnează un dicționar cu: status, attempts."""
    status = None
    error = None

    for i in range(attempts):
        try:
            r = requests.get(url, timeout=5)
            status = r.status_code
            error = None

            if status < 500:
                return {
                    "status": status,
                    "attempts": i + 1
                }

        except requests.RequestException as e:
            error = str(e)

    rezultat = {
        "status": status,
        "attempts": attempts
    }

    if error is not None:
        rezultat["error"] = error

    return rezultat
