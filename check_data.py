import sqlite3

conn = sqlite3.connect("resume_data.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM user_data")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
