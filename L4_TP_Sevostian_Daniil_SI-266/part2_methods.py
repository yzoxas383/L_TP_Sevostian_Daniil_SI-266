# Laborator: funcții, metode și importuri pe web
# Student: Sevostian Daniil
# Grupa: SI-266

import requests

BASE_URL = "https://cybercor.org"
ECHO_URL = "https://httpbin.org"
TIMEOUT = 10  # secunde

# Exercițiul 9

response = requests.get(BASE_URL, timeout=TIMEOUT)

print("Status code:", response.status_code)  # atribut
print("OK:", response.ok)                    # atribut
print("URL:", response.url)                  # atribut
print("Encoding:", response.encoding)        # atribut

# response reprezintă răspunsul primit de la server.
# status_code conține codul de stare HTTP al răspunsului.
# ok indică dacă cererea s-a încheiat cu succes.
# url conține adresa finală a paginii.
# encoding indică modul de codificare a textului răspunsului.
# Toate cele patru sunt atribute, deoarece sunt accesate fără paranteze.

# Exercițiul 10

response = requests.get(BASE_URL, timeout=TIMEOUT)
response.raise_for_status()

print("Pagina principală a fost încărcată cu succes.")

try:
    response_error = requests.get(
        BASE_URL + "/this-page-does-not-exist",
        timeout=TIMEOUT
    )

    print("Status pagina inexistentă:", response_error.status_code)
    response_error.raise_for_status()

except requests.HTTPError:
    print("Eroare: pagina solicitată nu a fost găsită.")

# raise_for_status() verifică dacă răspunsul conține o eroare HTTP.
# Pagina principală returnează codul 200, deci nu apare nicio eroare.
# În prezent, serverul cybercor.org returnează codul 200 chiar și pentru
# calea /this-page-does-not-exist, de aceea HTTPError nu este generată.
# Dacă serverul ar returna 404, excepția ar fi prinsă de blocul except.

# Exercițiul 11

response = requests.get(BASE_URL, timeout=TIMEOUT)

print("Antetele răspunsului:")

for nume, valoare in response.headers.items():
    print(f"{nume}: {valoare}")

# response.headers conține antetele HTTP primite de la server.
# Metoda .items() permite parcurgerea fiecărui antet sub forma
# unei perechi: nume și valoare.
# Bucla for afișează fiecare antet în forma "Nume: valoare".

# Exercițiul 12

print("Server:", response.headers.get("Server", "lipsește"))
print("Content-Type:", response.headers.get("Content-Type", "lipsește"))

print(
    "content-type cu litere mici:",
    response.headers.get("content-type", "lipsește")
)

# Metoda .get() caută valoarea unui antet după numele acestuia.
# Dacă antetul nu există, este returnată valoarea implicită "lipsește".
# În obiectul response.headers, numele antetelor nu sunt sensibile
# la litere mari sau mici.
# De aceea, "Content-Type" și "content-type" returnează aceeași valoare.

# Exercițiul 13

numar_cyber = response.text.lower().count("cyber")

print("Numărul de apariții ale cuvântului 'cyber':", numar_cyber)

# response.text conține codul HTML al paginii sub formă de șir de caractere.
# Metoda .lower() transformă toate literele din text în litere mici.
# Metoda .count("cyber") numără de câte ori apare cuvântul "cyber".
# Metodele pot fi înlănțuite deoarece .lower() returnează tot un șir de
# caractere, iar metoda .count() poate fi apelată pe acest șir.

# Exercițiul 14

html = response.text

start = html.find("<title>") + len("<title>")
end = html.find("</title>")

title = html[start:end].strip()

print("Titlul paginii:", title)

# response.text conține codul HTML al paginii.
# .find("<title>") găsește poziția unde începe tag-ul <title>.
# len("<title>") este adăugat pentru a începe extragerea după tag.
# .find("</title>") găsește poziția unde se termină titlul.
# Prin slicing [start:end] extragem textul dintre cele două tag-uri.
# .strip() elimină spațiile inutile de la începutul și sfârșitul titlului.

# Exercițiul 15

lines = response.text.splitlines()

longest_line = max(lines, key=len)

print("Numărul de linii HTML:", len(lines))
print("Lungimea celei mai lungi linii:", len(longest_line))

# .splitlines() împarte codul HTML în linii și returnează o listă.
# len(lines) arată numărul total de linii din pagina HTML.
# max(lines, key=len) găsește linia care are cea mai mare lungime.
# len(longest_line) afișează numărul de caractere din cea mai lungă linie.

# Exercițiul 16

if response.url.startswith("https://"):
    print("Conexiune securizată")
else:
    print("Conexiune nesecurizată")

# response.url conține adresa finală a paginii.
# Metoda .startswith("https://") verifică dacă URL-ul începe cu "https://".
# Dacă rezultatul este True, conexiunea folosește HTTPS și este afișat
# mesajul "Conexiune securizată".
# În caz contrar, este afișat mesajul "Conexiune nesecurizată".

# Exercițiul 17

response_redirect = requests.get(
    "http://cybercor.org",
    timeout=TIMEOUT
)

print("Redirecționări:")

for redirect in response_redirect.history:
    print("Cod de stare:", redirect.status_code, "| URL:", redirect.url)

print("URL final:", response_redirect.url)

# Cererea este trimisă inițial către versiunea HTTP a site-ului.
# response.history conține lista redirecționărilor efectuate până la
# ajungerea la pagina finală.
# Pentru fiecare redirecționare sunt afișate codul de stare și URL-ul.
# response_redirect.url conține adresa finală după toate redirecționările.

# Exercițiul 18

response_head = requests.head(BASE_URL, timeout=TIMEOUT)
response_get = requests.get(BASE_URL, timeout=TIMEOUT)

print("Lungimea conținutului HEAD:", len(response_head.content))
print("Lungimea conținutului GET:", len(response_get.content))

# Cererea HEAD solicită doar informațiile și antetele răspunsului,
# fără a descărca corpul paginii.
# Din acest motiv, response_head.content este de obicei gol.
# Cererea GET descarcă atât antetele, cât și conținutul paginii.
# De aceea, lungimea conținutului GET este mai mare decât la HEAD.

# Exercițiul 19

if response.cookies:
    for cookie in response.cookies:
        print("Nume cookie:", cookie.name)
        print("Secure:", cookie.secure)
else:
    print("Niciun cookie setat")

# response.cookies conține cookie-urile primite de la server.
# Dacă există cookie-uri, bucla for le parcurge pe fiecare.
# Atributul .name conține numele cookie-ului.
# Atributul .secure indică dacă acel cookie este transmis doar prin HTTPS.
# Dacă serverul nu a setat niciun cookie, este afișat mesajul
# "Niciun cookie setat".

# Exercițiul 20

session = requests.Session()

session.headers.update({
    "User-Agent": "WebLab-Sevostian-Daniil"
})

response_session = session.get(
    ECHO_URL + "/headers",
    timeout=TIMEOUT
)

data = response_session.json()

print("Antetele primite de httpbin:")
print(data)

print("User-Agent trimis:", data["headers"]["User-Agent"])

# requests.Session() creează o sesiune care poate păstra aceleași
# setări pentru mai multe cereri.
# session.headers.update() adaugă un antet User-Agent personalizat.
# Cererea este trimisă către httpbin.org/headers, care returnează
# antetele primite de server.
# Metoda .json() transformă răspunsul JSON într-un dicționar Python.
# La final verificăm dacă User-Agent-ul personalizat a fost trimis corect.
# response.text este un atribut și conține direct textul răspunsului,
# de aceea este accesat fără paranteze.
# response.json() este o metodă care execută o acțiune și transformă
# răspunsul JSON într-un obiect Python, de aceea se apelează cu paranteze.