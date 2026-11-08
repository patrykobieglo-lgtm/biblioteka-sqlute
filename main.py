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

conn.commit()
conn.close()