import os

print("DATABASE:", os.path.abspath("outlet.db"))
import pandas as pd
import sqlite3

# Koneksi database
conn = sqlite3.connect("outlet.db")
cursor = conn.cursor()

# Baca Excel
df = pd.read_excel("userpm.xlsx")

# Samakan nama kolom
df.columns = df.columns.str.strip().str.upper()

inserted = 0
updated = 0

# Import user
for _, row in df.iterrows():

    user = str(row["USER"]).strip()
    password = str(row["PASSWORD"]).strip()
    role = str(row["ROLE"]).strip()

    atasan = ""
    if "ATASAN" in df.columns:
        atasan = str(row["ATASAN"]).strip()

    cursor.execute(
        "SELECT id FROM users WHERE user=?",
        (user,)
    )

    cek = cursor.fetchone()

    if cek is None:

        # User baru
        cursor.execute(
            """
            INSERT INTO users
            (user,password,role,atasan)
            VALUES(?,?,?,?)
            """,
            (
                user,
                password,
                role,
                atasan
            )
        )
        inserted += 1

    else:

        # Update data user lama
        cursor.execute(
            """
            UPDATE users
            SET
                password=?,
                role=?,
                atasan=?
            WHERE user=?
            """,
            (
                password,
                role,
                atasan,
                user
            )
        )
        updated += 1

conn.commit()
conn.close()

print(f"""
==========================
Import selesai

User Baru : {inserted}
User Update : {updated}
==========================
""")
