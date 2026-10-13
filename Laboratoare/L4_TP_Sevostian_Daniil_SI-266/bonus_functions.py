# Laborator: funcții, metode și importuri pe web
# Student: Sevostian Daniil
# Grupa: SI-266

import requests
import webtools

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


# Exercițiul bonus
def get_title(html: str) -> str:
    """Extrage titlul paginii folosind BeautifulSoup."""
    if BeautifulSoup is None:
        raise ImportError("Instalați modulul cu: pip install beautifulsoup4")
    title = BeautifulSoup(html, "html.parser").find("title")
    return title.get_text(strip=True) if title else ""


def extract_links(html: str) -> list:
    """Extrage legăturile href fără duplicate folosind BeautifulSoup."""
    if BeautifulSoup is None:
        raise ImportError("Instalați modulul cu: pip install beautifulsoup4")
    soup = BeautifulSoup(html, "html.parser")
    return list(dict.fromkeys(tag["href"] for tag in soup.find_all(href=True)))


def main() -> None:
    """Compară variantele simple cu BeautifulSoup pe HTML cunoscut și pe site."""
    if BeautifulSoup is None:
        print("Instalați modulul cu: pip install beautifulsoup4")
        return
    sample = "<TITLE class='name'> Exemplu &amp; test </TITLE><a href='/about'>Link</a>"
    print("Titlu cu find():", webtools.get_title(sample))
    print("Titlu cu BeautifulSoup:", get_title(sample))
    print("Legături cu regex:", webtools.extract_links(sample))
    print("Legături cu BeautifulSoup:", extract_links(sample))
    try:
        html = webtools.fetch(BASE_URL).text
        print("Titlul real:", get_title(html))
        print("Legăturile reale:", extract_links(html))
    except requests.RequestException as error:
        print("Cererea nu a reușit:", error)

# BeautifulSoup gestionează atributele, ghilimelele simple și entitățile HTML.
# Varianta cu find() presupune un tag <title> simplu; regex-ul caută doar ghilimele duble.
# Parserul reduce verificările manuale și este mai sigur pentru HTML variat.


if __name__ == "__main__":
    main()
