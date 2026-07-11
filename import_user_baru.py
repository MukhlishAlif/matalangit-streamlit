import os
import sqlite3
import pandas as pd

print("DATABASE :", os.path.abspath("outlet.db"))

# =====================================
# KONEKSI DATABASE
# =====================================

conn = sqlite3.connect("outlet.db")
cursor = conn.cursor()

# =====================================
# CEK STRUKTUR USER
# =====================================

cursor.execute("PRAGMA table_info(users)")
existing = {row[1].lower() for row in cursor.fetchall()}

print("Kolom sebelum update:")
print(existing)

# =====================================
# TAMBAH KOLOM BARU
# =====================================

new_columns = {
    "brand": "TEXT",
    "region": "TEXT",
    "area": "TEXT",
    "branch": "TEXT",
    "micro_cluster": "TEXT",
    "real_name": "TEXT"
}

for col, tipe in new_columns.items():

    if col not in existing:

        print(f"Menambah kolom : {col}")

        cursor.execute(
            f'ALTER TABLE users ADD COLUMN "{col}" {tipe}'
        )

conn.commit()

# =====================================
# CEK LAGI
# =====================================

cursor.execute("PRAGMA table_info(users)")
existing = [row[1] for row in cursor.fetchall()]

print("\nKolom sesudah update:")
for c in existing:
    print("-", c)

# =====================================
# IMPORT EXCEL
# =====================================

df = pd.read_excel("userbaru.xlsx")
df.columns = df.columns.str.strip().str.upper()

inserted = 0
updated = 0

for _, row in df.iterrows():

    data = {
        "user": str(row.get("USER", "")).strip(),
        "password": str(row.get("PASSWORD", "")).strip(),
        "role": str(row.get("ROLE", "")).strip(),
        "atasan": str(row.get("ATASAN", "")).strip(),
        "brand": str(row.get("BRAND", "")).strip(),
        "region": str(row.get("REGION", "")).strip(),
        "area": str(row.get("AREA", "")).strip(),
        "branch": str(row.get("BRANCH", "")).strip(),
        "micro_cluster": str(row.get("MICRO CLUSTER", "")).strip(),
        "real_name": str(row.get("REAL NAME", "")).strip()
    }

    cursor.execute(
        "SELECT id FROM users WHERE user=?",
        (data["user"],)
    )

    if cursor.fetchone() is None:

        cursor.execute(
            """
            INSERT INTO users(
                user,password,role,atasan,
                brand,region,area,branch,
                micro_cluster,real_name
            )
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                data["user"],
                data["password"],
                data["role"],
                data["atasan"],
                data["brand"],
                data["region"],
                data["area"],
                data["branch"],
                data["micro_cluster"],
                data["real_name"]
            )
        )

        inserted += 1

    else:

        cursor.execute(
            """
            UPDATE users
            SET
                password=?,
                role=?,
                atasan=?,
                brand=?,
                region=?,
                area=?,
                branch=?,
                micro_cluster=?,
                real_name=?
            WHERE user=?
            """,
            (
                data["password"],
                data["role"],
                data["atasan"],
                data["brand"],
                data["region"],
                data["area"],
                data["branch"],
                data["micro_cluster"],
                data["real_name"],
                data["user"]
            )
        )

        updated += 1

conn.commit()
conn.close()

print("\n========================")
print("Import selesai")
print("User Baru   :", inserted)
print("User Update :", updated)
print("========================")