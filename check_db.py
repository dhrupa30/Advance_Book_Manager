import sqlite3

# 👇 Change the path if your DB file has a different name or location
conn = sqlite3.connect("databases/app.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables in DB:", cursor.fetchall())

conn.close()
