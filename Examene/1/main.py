from checker import build_url, is_https

print("Partea 1. build_url:")
build_url("example.com", "login")
print("Partea 1. build_url:")
build_url("example.com", "/login")

print("Partea 1. is_https:",
      is_https("https://example.com"))
print("Partea 1. is_https:",
      is_https("http://example.com"))

from  checker import show_response

print("\n Partea 2: Trimiterea unei cereri")
print("Test 1:")
show_response("https://example.com")

print("Test 2:")
show_response("https://httbin.org/status/404")

from checker import check_site, SITES
print("\n Partea 3: Verificarea site-urilor")

for url in SITES:
    print("\nSite:", url)
    print("Rezultat:", check_site(url))

from checker import scan_sites

print("\nPartea 4: Verificarea mai multor site-uri")
scan_sites()

from checker import check_headers

print("\nPartea 5: Audit de securitate")

print("Test 1:")
print(check_headers(SITES[10]))

print("Test 2:")
print(check_headers(SITES[11]))

print("Test 3:")
print(check_headers(SITES[9]))

from checker import retry_check

print("\nPartea 6: Incercari repetate")

print("Test 1 - Status 200:")
print(retry_check(SITES[3]))

print("Test 2 - Status 404:")
print(retry_check(SITES[6]))

print("Test 3 - Status 500:")
print(retry_check(SITES[7]))

print("Test 4 - Site inaccesibil:")
print(retry_check(SITES[9]))