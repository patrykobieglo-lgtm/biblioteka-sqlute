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