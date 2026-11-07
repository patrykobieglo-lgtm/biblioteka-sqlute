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

conn.commit()
conn.close()