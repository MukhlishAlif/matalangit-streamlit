import os
import sqlite3
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from sshtunnel import SSHTunnelForwarder

# =====================================
# PATH DATABASE
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "outlet.db")

print("DATABASE:", DB_PATH)

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# BARU BOLEH PAKAI CURSOR
cursor.execute("PRAGMA database_list")
print(cursor.fetchall())

# =====================================
# POSTGRE
# =====================================
import pandas as pd

url = "https://api.matalangit.cloud/bio/fetch-derfrtgty"

df = pd.read_json(url)

print(df.head())
# =====================================
# TABEL USER
# =====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT UNIQUE,
    password TEXT,
    role TEXT,
    atasan TEXT,
    status TEXT DEFAULT 'AKTIF',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# =====================================
# TABEL OUTLET
# =====================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS outlet (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_outlet TEXT,
    id_outlet TEXT,
    msisdn TEXT,
    input_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# =====================================
# USER
# =====================================

def login(user, password):

    cursor.execute("""
        SELECT *
        FROM users
        WHERE user = ?
        AND password = ?
        AND status = 'AKTIF'
    """, (user, password))

    return cursor.fetchone()


def tambah_user(user, password, role, atasan):

    cursor.execute("""
        INSERT INTO users
        (user,password,role,atasan)
        VALUES(?,?,?,?)
    """, (
        user,
        password,
        role,
        atasan
    ))

    conn.commit()


def tampil_user():

    cursor.execute("""
        SELECT
            user,
            role,
            atasan
        FROM users
        ORDER BY user
    """)

    return cursor.fetchall()

def tampil_user_master():

    cursor.execute("""
        SELECT
            id,
            user,
            password,
            role,
            atasan,
            status,
            created_at
        FROM users
        ORDER BY role, user
    """)

    return cursor.fetchall()

# =====================================
# UPDATE USER
# =====================================

def update_user(
        old_user,
        new_user,
        password,
        role,
        atasan
):

    cursor.execute("""
        UPDATE users
        SET
            user=?,
            password=?,
            role=?,
            atasan=?
        WHERE user=?
    """, (
        new_user,
        password,
        role,
        atasan,
        old_user
    ))

    conn.commit()

    return cursor.rowcount > 0
# =====================================
# HAPUS USER
# =====================================

def hapus_user(user):

    cursor.execute("""
        DELETE FROM users
        WHERE user=?
    """, (user,))

    conn.commit()



# =====================================
# OUTLET
# =====================================

def simpan_data(
    nama_outlet,
    id_outlet,
    msisdn,
    input_by
):

    waktu = datetime.now(
        ZoneInfo("Asia/Jakarta")
    ).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO outlet
        (
            nama_outlet,
            id_outlet,
            msisdn,
            input_by,
            created_at
        )
        VALUES(?,?,?,?,?)
    """, (
        nama_outlet,
        id_outlet,
        msisdn,
        input_by,
        waktu
    ))

    conn.commit()


def tampil_data():

    cursor.execute("""
        SELECT
            id,
            nama_outlet,
            id_outlet,
            msisdn,
            input_by,
            created_at
        FROM outlet
        ORDER BY created_at DESC
    """)

    return cursor.fetchall()


def hapus_data(id_data):

    cursor.execute(
        """
        DELETE FROM outlet
        WHERE id = ?
        """,
        (id_data,)
    )

    conn.commit()

    return cursor.rowcount
# =====================================
# DASHBOARD
# =====================================

def total_outlet():

    cursor.execute("""
        SELECT COUNT(DISTINCT id_outlet)
        FROM outlet
    """)

    return cursor.fetchone()[0]


def total_msisdn():

    cursor.execute("""
        SELECT COUNT(*)
        FROM outlet
    """)

    return cursor.fetchone()[0]


def total_cse():

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role IN ('CSE','RSE')
    """)

    return cursor.fetchone()[0]


def total_bsm():

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE role='BSM'
    """)

    return cursor.fetchone()[0]

def last_input(limit=10):

    cursor.execute("""
        SELECT
            nama_outlet,
            id_outlet,
            msisdn,
            input_by,
            created_at
        FROM outlet
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))

    return cursor.fetchall()
# =====================================
# HIRARKI USER
# =====================================

def bawahan(atasan):

    cursor.execute("""
        SELECT user
        FROM users
        WHERE atasan=?
    """, (atasan,))

    return [x["user"] for x in cursor.fetchall()]


def get_downline(user):
    """
    Mengambil seluruh bawahan secara recursive
    """

    hasil = []

    def cari(atasan):

        cursor.execute("""
            SELECT user
            FROM users
            WHERE atasan=?
        """, (atasan,))

        rows = cursor.fetchall()

        for row in rows:

            nama = row["user"]

            if nama not in hasil:

                hasil.append(nama)

                cari(nama)

    cari(user)

    return hasil


# =====================================
# HELPER USER
# =====================================

def get_user_role(role):

    cursor.execute("""
        SELECT user
        FROM users
        WHERE role=?
        ORDER BY user
    """, (role,))

    return [x["user"] for x in cursor.fetchall()]


def get_role(user):

    cursor.execute("""
        SELECT role
        FROM users
        WHERE user=?
    """, (user,))

    row = cursor.fetchone()

    if row:
        return row["role"]

    return ""


def get_atasan(user):

    cursor.execute("""
        SELECT atasan
        FROM users
        WHERE user=?
    """, (user,))

    row = cursor.fetchone()

    if row:
        return row["atasan"]

    return ""


# =====================================
# FILTER DATA OUTLET
# =====================================

def data_by_user(user):

    cursor.execute("""
        SELECT
            id,
            nama_outlet,
            id_outlet,
            msisdn,
            input_by,
            created_at
        FROM outlet
        WHERE input_by=?
        ORDER BY created_at DESC
    """, (user,))

    return cursor.fetchall()


def data_by_users(user_list):

    if not user_list:
        return []

    placeholder = ",".join(["?"] * len(user_list))

    cursor.execute(f"""
        SELECT
            id,
            nama_outlet,
            id_outlet,
            msisdn,
            input_by,
            created_at
        FROM outlet
        WHERE input_by IN ({placeholder})
        ORDER BY created_at DESC
    """, user_list)

    return cursor.fetchall()

# =====================================
# MASTER USER
# =====================================

def bawahan(atasan):

    cursor.execute("""
        SELECT user
        FROM users
        WHERE atasan=?
    """, (atasan,))

    return [x["user"] for x in cursor.fetchall()]
    
cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
""")

for row in cursor.fetchall():
    print(row["name"])

# =====================================
# VALIDASI
# =====================================


def cek_msisdn(msisdn):

    cursor.execute("""
        SELECT
            input_by,
            created_at
        FROM outlet
        WHERE msisdn=?
        LIMIT 1
    """, (msisdn,))

    return cursor.fetchone()
    
# ==========================================
# AMBIL SEMUA BAWAHAN (RECURSIVE)
# ==========================================

def get_downline(user):

    hasil = []

    def cari(atasan):

        cursor.execute("""
            SELECT user
            FROM users
            WHERE atasan=?
        """, (atasan,))

        rows = cursor.fetchall()

        for row in rows:

            nama = row["user"]

            if nama not in hasil:
                hasil.append(nama)
                cari(nama)

    cari(user)

    return hasil