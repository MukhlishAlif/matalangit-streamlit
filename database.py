import os
import sqlite3
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo

# =====================================
# PATH DATABASE
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "outlet.db")

print("DATABASE:", DB_PATH)

# =====================================
# DATABASE CONNECTION
# =====================================

def get_connection():

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
        timeout=30
    )

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    return conn

# =====================================
# POSTGRE
# =====================================
import requests
import pandas as pd
import streamlit as st


@st.cache_data(ttl=300)
def load_biometrik():

    url = "https://api.matalangit.cloud/bio/fetch-derfrtgty"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    biometrik = pd.json_normalize(data["data"])

    biometrik.columns = (
        biometrik.columns
        .str.strip()
        .str.lower()
    )

    biometrik["msisdn"] = (
        biometrik["msisdn"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    biometrik["tanggal_biometrik"] = pd.to_datetime(
        biometrik["ga_dt"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

    return biometrik[
        ["msisdn", "tanggal_biometrik"]
    ].drop_duplicates()

# =====================================
# TABEL USER
# =====================================

conn = get_connection()
cursor = conn.cursor()

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
conn.close()

# =====================================
# USER
# =====================================

def login(

    user,
    password

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT *

        FROM users

        WHERE user = ?

        AND password = ?

        AND status='AKTIF'

    """, (

        user,

        password

    ))

    hasil = cursor.fetchone()

    conn.close()

    return hasil


def tambah_user(

    user,
    password,
    role,
    atasan

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO users(

            user,
            password,
            role,
            atasan

        )

        VALUES(

            ?,?,?,?

        )

    """, (

        user,

        password,

        role,

        atasan

    ))

    conn.commit()

    conn.close()


def tampil_user():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            user,

            role,

            atasan

        FROM users

        ORDER BY user

    """)

    data = cursor.fetchall()

    conn.close()

    return data

def tampil_user_master():

    conn = get_connection()

    cursor = conn.cursor()

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

    data = cursor.fetchall()

    conn.close()

    return data



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

    conn = get_connection()

    cursor = conn.cursor()

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

    berhasil = cursor.rowcount > 0

    conn.close()

    return berhasil

# =====================================
# HAPUS USER
# =====================================

def hapus_user(

    user

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        DELETE

        FROM users

        WHERE user=?

    """, (

        user,

    ))

    conn.commit()

    conn.close()


# =====================================
# OUTLET
# =====================================

def simpan_data(

    nama_outlet,
    id_outlet,
    msisdn,
    input_by

):

    conn = get_connection()

    cursor = conn.cursor()

    waktu = datetime.now(

        ZoneInfo("Asia/Jakarta")

    ).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""

        INSERT INTO outlet (

            nama_outlet,
            id_outlet,
            msisdn,
            input_by,
            created_at

        )

        VALUES (

            ?, ?, ?, ?, ?

        )

    """, (

        nama_outlet,
        id_outlet,
        msisdn,
        input_by,
        waktu

    ))

    conn.commit()

    conn.close()


def tampil_data():

    conn = get_connection()

    cursor = conn.cursor()

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

    data = cursor.fetchall()

    conn.close()

    return data


def hapus_data(

    id_data

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        DELETE

        FROM outlet

        WHERE id = ?

    """, (

        id_data,

    ))

    conn.commit()

    hasil = cursor.rowcount

    conn.close()

    return hasil
# =====================================
# DASHBOARD
# =====================================

def total_outlet():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            COUNT(DISTINCT id_outlet)

        FROM outlet

    """)

    hasil = cursor.fetchone()[0]

    conn.close()

    return hasil


def total_msisdn():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            COUNT(*)

        FROM outlet

    """)

    hasil = cursor.fetchone()[0]

    conn.close()

    return hasil


def total_cse():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            COUNT(*)

        FROM users

        WHERE role IN (

            'CSE',
            'RSE'

        )

    """)

    hasil = cursor.fetchone()[0]

    conn.close()

    return hasil


def total_bsm():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            COUNT(*)

        FROM users

        WHERE role='BSM'

    """)

    hasil = cursor.fetchone()[0]

    conn.close()

    return hasil


def last_input(

    limit=10

):

    conn = get_connection()

    cursor = conn.cursor()

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

    """, (

        limit,

    ))

    data = cursor.fetchall()

    conn.close()

    return data
# =====================================
# HIRARKI USER
# =====================================

def bawahan(

    atasan

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            user

        FROM users

        WHERE atasan=?

    """, (

        atasan,

    ))

    hasil = [

        x["user"]

        for x in cursor.fetchall()

    ]

    conn.close()

    return hasil


def get_downline(

    user

):

    hasil = []

    conn = get_connection()

    cursor = conn.cursor()

    def cari(

        atasan

    ):

        cursor.execute("""

            SELECT

                user

            FROM users

            WHERE atasan=?

        """, (

            atasan,

        ))

        rows = cursor.fetchall()

        for row in rows:

            nama = row["user"]

            if nama not in hasil:

                hasil.append(

                    nama

                )

                cari(

                    nama

                )

    cari(

        user

    )

    conn.close()

    return hasil


# =====================================
# HELPER USER
# =====================================

def get_user_role(

    role

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            user

        FROM users

        WHERE role=?

        ORDER BY user

    """, (

        role,

    ))

    hasil = [

        x["user"]

        for x in cursor.fetchall()

    ]

    conn.close()

    return hasil


def get_role(

    user

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            role

        FROM users

        WHERE user=?

    """, (

        user,

    ))

    row = cursor.fetchone()

    conn.close()

    if row:

        return row["role"]

    return ""


def get_atasan(

    user

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            atasan

        FROM users

        WHERE user=?

    """, (

        user,

    ))

    row = cursor.fetchone()

    conn.close()

    if row:

        return row["atasan"]

    return ""


# =====================================
# FILTER DATA OUTLET
# =====================================

def data_by_user(

    user

):

    conn = get_connection()

    cursor = conn.cursor()

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

    """, (

        user,

    ))

    data = cursor.fetchall()

    conn.close()

    return data


def data_by_users(

    user_list

):

    if not user_list:

        return []

    conn = get_connection()

    cursor = conn.cursor()

    placeholder = ",".join(

        ["?"] * len(user_list)

    )

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

    data = cursor.fetchall()

    conn.close()

    return data


# =====================================
# VALIDASI
# =====================================

def cek_msisdn(

    msisdn

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            input_by,
            created_at

        FROM outlet

        WHERE msisdn=?

        LIMIT 1

    """, (

        msisdn,

    ))

    hasil = cursor.fetchone()

    conn.close()

    return hasil    
