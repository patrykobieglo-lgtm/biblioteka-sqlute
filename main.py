import sqlite3

conn = sqlite3.connect("biblioteka.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS ksiazki (
    id INTEGER PRIMARY KEY,
    tytul TEXT NOT NULL,
    autor TEXT NOT NULL,
    rok_wydania INTEGER
)
""")

print("Tabela ksiazki jest gotowa.")


# ==================================
# ZADANIE 2 – DODAWANIE KSIĄŻEK
# ==================================

cursor.execute("DELETE FROM ksiazki")

ksiazki = [
    ("Lalka", "Bolesław Prus", 1890),
    ("Quo vadis", "Henryk Sienkiewicz", 1896),
    ("Ferdydurke", "Witold Gombrowicz", 1937),
    ("Solaris", "Stanisław Lem", 1961),
    ("Cyberiada", "Stanisław Lem", 1965)
]

cursor.executemany(
    "INSERT INTO ksiazki (tytul, autor, rok_wydania) VALUES (?, ?, ?)",
    ksiazki
)

cursor.execute("SELECT COUNT(*) FROM ksiazki")
liczba = cursor.fetchone()[0]

print("Dodano książek:", len(ksiazki))
print("Liczba książek w bazie:", liczba)


#zadanie 3

cursor.execute("""
    SELECT rok_wydania, tytul, autor
    FROM ksiazki
    ORDER BY rok_wydania DESC
""")

wyniki = cursor.fetchall()

for rok, tytul, autor in wyniki:
    print(f"{rok} | {tytul} | {autor}")

    #zadanie 4

autor = input("Podaj autora: ")

cursor.execute("""
    SELECT rok_wydania, tytul, autor
    FROM ksiazki
    WHERE autor = ?
    ORDER BY rok_wydania
""", (autor,))

wyniki = cursor.fetchall()

if wyniki:
    for rok, tytul, autor in wyniki:
        print(f"{rok} | {tytul} | {autor}")
else:
    print("Nie znaleziono książek tego autora.")


#zadanie 5

cursor.execute("SELECT id, tytul FROM ksiazki")
ksiazki = cursor.fetchall()

print("\nDostępne książki:")

for id, tytul in ksiazki:
    print(f"{id}: {tytul}")

# Zapytaj o ID
id_ksiazki = int(input("Podaj ID książki do usunięcia: "))

# Usuń książkę
cursor.execute(
    "DELETE FROM ksiazki WHERE id = ?",
    (id_ksiazki,)
)

# Sprawdź wynik
if cursor.rowcount > 0:
    conn.commit()
    print(f"Usunięto książkę o id {id_ksiazki}.")
else:
    print(f"Nie ma książki o id {id_ksiazki}.")

    #zadanie 6

def szukaj_tytulow(conn, fraza) -> list[str]:
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tytul
        FROM ksiazki
        WHERE tytul LIKE ?
        ORDER BY tytul
    """, (f"%{fraza}%",))

    wyniki = cursor.fetchall()

    return [wiersz[0] for wiersz in wyniki]


# Test
print("\nWyszukiwanie tytułów:")

print("is:", szukaj_tytulow(conn, "is"))
print("IS:", szukaj_tytulow(conn, "IS"))
print("xyz:", szukaj_tytulow(conn, "xyz"))

#zadanie 7

from datetime import date

# Ustawienie dostępu do kolumn po nazwach
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Pobranie aktualnego roku
aktualny_rok = date.today().year

# Jedno zapytanie SQL
cursor.execute("""
    SELECT
        tytul,
        rok_wydania AS rok,
        ? - rok_wydania AS lat_temu
    FROM ksiazki
    ORDER BY rok_wydania DESC
    LIMIT 3
""", (aktualny_rok,))

wyniki = cursor.fetchall()

for ksiazka in wyniki:
    print(
        f"{ksiazka['rok']} | "
        f"{ksiazka['tytul']} | "
        f"{ksiazka['lat_temu']} lat temu"
    )

#zadanie 8

def zmien_rok(conn, id_ksiazki, nowy_rok) -> bool:
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ksiazki
        SET rok_wydania = ?
        WHERE id = ?
    """, (nowy_rok, id_ksiazki))

    # Kolejność parametrów odpowiada kolejności znaków ?
    # Pierwszy ? to nowy rok, drugi ? to ID książki.

    if cursor.rowcount > 0:
        conn.commit()
        return True

    return False


# Test 1 – zmiana istniejącej książki
if zmien_rok(conn, 1, 1887):
    cursor.execute(
        "SELECT * FROM ksiazki WHERE id = ?",
        (1,)
    )

    ksiazka = cursor.fetchone()

    print("Zmieniono:", tuple(ksiazka))


# Test 2 – próba zmiany nieistniejącej książki
if not zmien_rok(conn, 42, 2000):
    print("Nie znaleziono książki o id 42.")

#zadanie 9

import csv

poprawne_ksiazki = []

with open("nowe_ksiazki.csv", "r", encoding="utf-8", newline="") as plik:
    czytnik = csv.DictReader(plik, delimiter=";")

    for wiersz in czytnik:
        try:
            rok = int(wiersz["rok_wydania"])

            poprawne_ksiazki.append((
                wiersz["tytul"],
                wiersz["autor"],
                rok
            ))

        except ValueError:
            print(
                f"Pominięto „{wiersz['tytul']}”: "
                f"niepoprawny rok „{wiersz['rok_wydania']}”"
            )

# Dodanie poprawnych książek jednym executemany()
cursor.executemany("""
    INSERT INTO ksiazki (tytul, autor, rok_wydania)
    VALUES (?, ?, ?)
""", poprawne_ksiazki)

conn.commit()

print(f"Zaimportowano książek: {len(poprawne_ksiazki)}")

conn.commit()
conn.close()

#zadanie 10

import sqlite3

# 1. Tworzymy bazę tylko w pamięci RAM
conn10 = sqlite3.connect(":memory:")
cursor10 = conn10.cursor()

# 2. Tworzymy tabelę katalog
cursor10.execute("""
CREATE TABLE katalog (
    tytul TEXT,
    ukryta INTEGER
)
""")

# 3. Dodajemy książki
ksiazki = [
    ("Lalka", 0),
    ("Quo vadis", 0),
    ("Solaris", 0),
    ("Rękopis – tylko dla redakcji", 1)
]

cursor10.executemany(
    "INSERT INTO katalog VALUES (?, ?)",
    ksiazki
)

conn10.commit()


# 4. Wersja podatna na SQL Injection
def szukaj_podatnie(fraza):
    zapytanie = f"""
    SELECT tytul FROM katalog
    WHERE ukryta = 0 AND tytul LIKE '%{fraza}%'
    """
    cursor10.execute(zapytanie)
    return cursor10.fetchall()


# 5. Wersja bezpieczna - parametr ?
def szukaj_bezpiecznie(fraza):
    cursor10.execute("""
        SELECT tytul FROM katalog
        WHERE ukryta = 0 AND tytul LIKE ?
    """, (f"%{fraza}%",))

    return cursor10.fetchall()


# 6. Test SQL Injection
fraza = "' OR 1=1 --"

print("Wersja podatna:")
print(szukaj_podatnie(fraza))

print("\nWersja bezpieczna:")
print(szukaj_bezpiecznie(fraza))

conn10.close()


#zadanie 11

import sqlite3

# Łączymy się z bazą biblioteki
conn11 = sqlite3.connect("biblioteka.db")
cursor11 = conn11.cursor()


# Funkcja dodająca paczkę książek
def dodaj_paczke(conn, ksiazki):
    with conn:
        conn.executemany("""
            INSERT INTO ksiazki (tytul, autor, rok_wydania)
            VALUES (?, ?, ?)
        """, ksiazki)


try:
    # Sprawdzamy liczbę książek przed operacją
    liczba_przed = cursor11.execute(
        "SELECT COUNT(*) FROM ksiazki"
    ).fetchone()[0]

    print(f"Książek przed: {liczba_przed}")

    # Pierwsza paczka - trzecia książka ma błędny tytuł
    paczka = [
        ("W pustyni i w puszczy", "Henryk Sienkiewicz", 1911),
        ("Pan Tadeusz", "Adam Mickiewicz", 1834),
        (None, "Jan Kochanowski", 1584)
    ]

    try:
        dodaj_paczke(conn11, paczka)

    except sqlite3.IntegrityError as blad:
        print(f"Błąd: {blad} - nie dodano żadnej książki")

    # Poprawiamy trzecią książkę
    paczka[2] = ("Treny", "Jan Kochanowski", 1584)

    # Ponawiamy dodawanie
    dodaj_paczke(conn11, paczka)

    print("Poprawiona paczka została dodana.")

    # Sprawdzamy liczbę książek po operacji
    liczba_po = cursor11.execute(
        "SELECT COUNT(*) FROM ksiazki"
    ).fetchone()[0]

    print(f"Książek po: {liczba_po}")
finally:
        conn11.close()
        print("Połączenie z bazą zostało zamknięte.")

#zadanie 12

import json

conn = sqlite3.connect("biblioteka.db")
                       
# Ustawiamy sposób odczytu rekordów
try:
    conn.row_factory = sqlite3.Row

        # Pobieramy książki posortowane po autorze i tytule
    cursor = conn.cursor()

    cursor.execute("""
                SELECT id, tytul, autor, rok_wydania
                FROM ksiazki
                ORDER BY autor, tytul
            """)

    wiersze = cursor.fetchall()

            # Zamieniamy rekordy SQLite.Row na słowniki
    ksiazki_json = [dict(wiersz) for wiersz in wiersze]

            # Zapisujemy do pliku JSON
    with open("biblioteka.json", "w", encoding="utf-8") as plik:
                json.dump(
                    ksiazki_json,
                    plik,
                    ensure_ascii=False,
                    indent=2
                )

    print(f"Zapisano {len(ksiazki_json)} książek do biblioteka.json")

            # Wczytujemy plik JSON
    with open("biblioteka.json", "r", encoding="utf-8") as plik:
                odczytane_ksiazki = json.load(plik)

    # Sprawdzamy liczbę rekordów w bazie
    cursor.execute("SELECT COUNT(*) FROM ksiazki")
    liczba_w_bazie = cursor.fetchone()[0]

            # Porównujemy wyniki
    print("Zgodność z bazą:", len(odczytane_ksiazki) == liczba_w_bazie)
finally:
    conn11.close()
    print("Połączenie z bazą zostało zamknięte.")

    #zadanie 13

    # zadanie 13
import sqlite3

# Otwieramy połączenie z bazą
conn = sqlite3.connect("biblioteka.db")
cursor = conn.cursor()

# Dozwolone kolumny sortowania
dozwolone_sortowanie = ["tytul", "autor", "rok_wydania"]

# Pobieramy wybór użytkownika
sortowanie = input(
    "Sortuj po (tytul/autor/rok_wydania): "
).strip()

# Sprawdzamy, czy kolumna jest dozwolona
if sortowanie not in dozwolone_sortowanie:
    print("Nieznana kolumna – sortuję po tytule.")
    sortowanie = "tytul"

# Pobieramy numer strony
strona = int(input("Strona: "))

# Liczba książek na stronie
limit = 2

# Obliczamy przesunięcie
offset = (strona - 1) * limit

# Pobieramy książki z bazy
cursor.execute(f"""
    SELECT rok_wydania, tytul
    FROM ksiazki
    ORDER BY {sortowanie}
    LIMIT ? OFFSET ?
""", (limit, offset))

ksiazki = cursor.fetchall()

# Wyświetlamy wyniki
if ksiazki:
    for rok, tytul in ksiazki:
        print(f"{rok} | {tytul}")
else:
    print("Ta strona jest pusta.")

# Zamykamy połączenie
conn.close()