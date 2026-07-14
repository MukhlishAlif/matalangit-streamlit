import os
import sqlite3
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

# =====================================
# PATH DATABASE
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "outlet.db")

print("DATABASE:", DB_PATH)

# =====================================
# API CLIENT (generik)
# =====================================

API_BASE_URL = "https://api.matalangit.cloud"

ENDPOINTS = {
    "login": "/auth/login",
    "logout": "/auth/logout",
    "outlet": "/sales-tap/legacy-report",
    "users": "/admin/users/legacy-report",
}


class ApiError(Exception):
    """Dilempar kalau request ke API gagal (status bukan 2xx, atau connect error)."""
    def __init__(self, status, message, data=None):
        self.status = status
        self.message = message
        self.data = data
        super().__init__(message)


def api_fetch(endpoint, method="GET", payload=None, token=None, timeout=30):
    """
    Client generik untuk semua panggilan ke API_BASE_URL.
    Lihat penjelasan lengkap di versi sebelumnya -- tidak berubah.
    """

    auth_token = token or st.session_state.get("outlet_token")

    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    url = f"{API_BASE_URL}{endpoint}"

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=payload if payload is not None else None,
            timeout=timeout,
        )
    except requests.RequestException as e:
        raise ApiError(status=0, message=f"Gagal connect ke API: {e}")

    try:
        data = response.json()
    except ValueError:
        data = response.text

    if not response.ok:
        message = "API request failed"
        if isinstance(data, dict) and data.get("message"):
            message = data["message"]
        raise ApiError(response.status_code, message, data)

    return data


# =====================================
# DATABASE CONNECTION (SQLite, dipakai fungsi TULIS: tambah/update/hapus)
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
# BIOMETRIK (API, sudah ada sebelumnya)
# =====================================

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
# MASTER MSISDN (API, sudah ada sebelumnya)
# =====================================

@st.cache_data(ttl=300)
def load_master_msisdn():

    url = "https://api.matalangit.cloud/bio/fetch-derfrtgty2"

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    df = pd.json_normalize(
        data["data"]
    )

    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
    )

    df["MSISDN"] = (
        df["MSISDN"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return set(
        df["MSISDN"]
    )


# =====================================================================================
# RAW FETCH DARI API (dipakai semua fungsi baca outlet/users di bawah)
# =====================================================================================
#
# ASUMSI bentuk response (BELUM DIKONFIRMASI dari server -- kalau field
# aslinya beda nama, tinggal sesuaikan .get("nama_field_asli") di bagian
# _fetch_outlet_raw() / _fetch_users_raw() di bawah, tidak perlu ubah
# fungsi lain):
#
#   GET /sales-tap/legacy-report -> { "data": [ {id, nama_outlet, id_outlet,
#       msisdn, input_by, created_at}, ... ] }
#
#   GET /admin/users/legacy-report -> { "data": [ {id, user, password, role,
#       atasan, status, created_at, brand, region, area, branch,
#       micro_cluster, real_name}, ... ] }
# =====================================================================================

@st.cache_data(ttl=120)
def _fetch_outlet_raw():
    try:
        result = api_fetch(ENDPOINTS["outlet"], method="POST")
    except ApiError as e:
        print("[OUTLET] gagal ambil dari API:", e.status, e.message)
        return []

    rows = result.get("data", []) if isinstance(result, dict) else (result or [])
    return rows


@st.cache_data(ttl=300)
def _fetch_users_raw():
    try:
        result = api_fetch(ENDPOINTS["users"], method="POST")
    except ApiError as e:
        print("[USERS] gagal ambil dari API:", e.status, e.message)
        return []

    rows = result.get("data", []) if isinstance(result, dict) else (result or [])
    return rows

def _normalize_flag_bio(value):
    """
    API bisa mengirim flag_bio dalam berbagai bentuk (bool, int, string
    "true"/"false"/"1"/"0"). Normalisasi jadi 0/1 supaya konsisten
    disimpan di SQLite dan gampang dipakai sebagai angka di pandas.
    """

    if value is None:
        return 0

    if isinstance(value, bool):
        return int(value)

    if isinstance(value, (int, float)):
        return int(bool(value))

    text = str(value).strip().lower()

    return 1 if text in ("1", "true", "ya", "yes") else 0

def _outlet_row_tuple(r):
    """Ubah 1 dict outlet dari API jadi tuple urutan tetap
    (id, nama_outlet, id_outlet, msisdn, input_by, created_at, flag_bio, ga_dt),
    supaya kompatibel dengan kode lain yang mengakses berdasarkan posisi
    (mis. pd.DataFrame(rows, columns=[...]))."""
    return (
        r.get("id"),
        r.get("nama_outlet"),
        r.get("id_outlet"),
        r.get("msisdn"),
        r.get("input_by"),
        r.get("created_at"),
        _normalize_flag_bio(r.get("flag_bio")),
        r.get("ga_dt"),
    )

def _user_row_dict(r):

    role_raw = r.get("role") or ""         # <-- tambahkan baris ini

    return {
        "id": r.get("id"),
        "user": r.get("user") or r.get("username"),
        "role": role_raw.upper(),
        "atasan": r.get("atasan"),
        "status": r.get("status") or "AKTIF",
        "created_at": r.get("created_at"),
        "brand": r.get("brand"),
        "region": r.get("region"),
        "area": r.get("area"),
        "branch": r.get("branch"),
        "micro_cluster": r.get("micro_cluster"),
        "real_name": r.get("real_name") or r.get("full_name"),
    }


# =====================================
# USER HIERARCHY (API)
# =====================================

@st.cache_data(ttl=300)
def load_user_hierarchy():

    raw_rows = _fetch_users_raw()

    records = [_user_row_dict(r) for r in raw_rows]

    default_cols = [
        "id", "user", "role", "atasan", "status", "created_at",
        "brand", "region", "area", "branch", "micro_cluster", "real_name"
    ]

    df = pd.DataFrame(records, columns=default_cols)   # <-- kolom dipaksa ada meski data kosong

    df.columns = df.columns.str.upper()

    for col in ["ATASAN", "ROLE", "STATUS"]:
        if col not in df.columns:
            df[col] = ""

    df["ATASAN"] = df["ATASAN"].fillna("")
    df["ROLE"] = df["ROLE"].fillna("")
    df["STATUS"] = df["STATUS"].fillna("AKTIF")

    # ===========================
    # BRAND
    # ===========================

    df["BRAND"] = ""

    df.loc[
        df["ATASAN"].astype(str).str.lower().str.contains("_im3", na=False),
        "BRAND"
    ] = "IM3"

    df.loc[
        df["ATASAN"].astype(str).str.lower().str.contains("_3id", na=False),
        "BRAND"
    ] = "3ID"

    # ===========================
    # MAP
    # ===========================

    role_map = df.set_index("USER")["ROLE"].to_dict()

    atasan_map = df.set_index("USER")["ATASAN"].to_dict()

    brand_map = df.set_index("USER")["BRAND"].to_dict()

    # ===========================
    # CHILDREN
    # ===========================

    children_map = {}

    for user, atasan in atasan_map.items():

        if atasan:

            children_map.setdefault(

                atasan,

                []

            ).append(user)

    return (

        df,
        role_map,
        atasan_map,
        brand_map,
        children_map

    )


# =====================================
# TABEL USER & OUTLET (SQLite -- tetap ada, dipakai fungsi TULIS di bawah)
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    brand TEXT,
    region TEXT,
    area TEXT,
    branch TEXT,
    micro_cluster TEXT,
    real_name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS outlet (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_outlet TEXT,
    id_outlet TEXT,
    msisdn TEXT,
    input_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    flag_bio INTEGER DEFAULT 0,
    ga_dt TEXT
)
""")

cursor.execute("PRAGMA table_info(outlet)")
existing_cols = [row[1] for row in cursor.fetchall()]

if "flag_bio" not in existing_cols:
    cursor.execute("ALTER TABLE outlet ADD COLUMN flag_bio INTEGER DEFAULT 0")

if "ga_dt" not in existing_cols:
    cursor.execute("ALTER TABLE outlet ADD COLUMN ga_dt TEXT")

cursor.execute("CREATE INDEX IF NOT EXISTS idx_outlet_created_at ON outlet(created_at)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_outlet_msisdn ON outlet(msisdn)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_outlet_input_by ON outlet(input_by)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_atasan ON users(atasan)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")

conn.commit()
conn.close()


# =====================================
# LOGIN (API)
# =====================================

def login(username, password):
    """
    POST https://api.matalangit.cloud/auth/login   { username, password }
    (tidak berubah dari versi sebelumnya)
    """

    try:
        result = api_fetch(
            ENDPOINTS["login"],
            method="POST",
            payload={"username": username, "password": password},
        )
    except ApiError as e:
        print("[LOGIN] gagal:", e.status, e.message)
        return None

    if not result.get("success"):
        print("[LOGIN] gagal:", result.get("message", "unknown error"))
        return None

    data = result.get("data") or {}
    token = data.get("token") or result.get("token")

    if not token:
        print("[LOGIN] WARNING: token tidak ditemukan di response")
        return None

    role_raw = data.get("role") or ""

    hasil = {
        "token": token,
        "id": data.get("id"),
        "user": data.get("username"),
        "real_name": data.get("full_name"),
        "role": role_raw.upper(),
        "atasan": data.get("atasan", ""),
        "brand": data.get("brand", ""),
        "region": data.get("region", ""),
        "area": data.get("area", ""),
        "branch": data.get("branch", ""),
        "micro_cluster": data.get("micro_cluster", ""),
        "status": data.get("status", "AKTIF"),
    }

    return hasil


def logout():
    try:
        api_fetch(ENDPOINTS["logout"], method="POST")
    except ApiError as e:
        print("[LOGOUT] gagal panggil API (diabaikan):", e.status, e.message)


# =====================================
# USER -- BACA (API)
# =====================================

def tampil_user():
    """Dulu: SELECT user, role, atasan, real_name FROM users.
    Sekarang: dari API, dikembalikan sebagai list of dict supaya
    kompatibel dengan pola `dict(row)` yang dipakai di semua
    dashboard (dashboard_cse.py, dashboard_bsm.py, main_dashboard.py, dst)."""

    raw_rows = _fetch_users_raw()

    return [
        {
            "user": d["user"],
            "role": d["role"],
            "atasan": d["atasan"],
            "real_name": d["real_name"],
        }
        for d in (_user_row_dict(r) for r in raw_rows)
    ]


def tampil_user_master():
    """Dulu: SELECT semua kolom users ORDER BY role, user.
    Sekarang: dari API, dikembalikan sebagai list of dict."""

    raw_rows = _fetch_users_raw()

    data = [_user_row_dict(r) for r in raw_rows]

    data.sort(key=lambda d: (str(d["role"] or ""), str(d["user"] or "")))

    return data


# =====================================
# USER -- TULIS (tetap SQLite, MENUNGGU konfirmasi endpoint create/update/delete)
# =====================================

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
# OUTLET -- TULIS (tetap SQLite, MENUNGGU konfirmasi endpoint create/update/delete)
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
# OUTLET -- SYNC KE SQLITE LOKAL (mirror dari API)
# =====================================

def sync_outlet_to_sqlite():

    raw_rows = _fetch_outlet_raw()

    if not raw_rows:
        return

    rows = [_outlet_row_tuple(r) for r in raw_rows]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO outlet (id, nama_outlet, id_outlet, msisdn, input_by, created_at, flag_bio, ga_dt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            nama_outlet = excluded.nama_outlet,
            id_outlet   = excluded.id_outlet,
            msisdn      = excluded.msisdn,
            input_by    = excluded.input_by,
            created_at  = excluded.created_at,
            flag_bio    = excluded.flag_bio,
            ga_dt       = excluded.ga_dt
    """, rows)

    conn.commit()
    conn.close()

# =====================================
# TANGGAL TERBARU YANG ADA DATANYA
# =====================================

def get_latest_data_date():
    """
    Tanggal terbaru yang ada baris datanya di outlet (setelah sync
    dari API). Dipakai sebagai default kalau user belum pilih tanggal
    di date_input (value=None) -- supaya yang tampil otomatis data
    hari terakhir yang ada submit-nya, bukan kosong/error.
    """

    sync_outlet_to_sqlite()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(created_at) FROM outlet")
    row = cursor.fetchone()

    conn.close()

    max_created = row[0] if row else None

    if not max_created:
        return date.today()

    # created_at formatnya "YYYY-MM-DD HH:MM:SS", ambil bagian tanggalnya saja
    return datetime.strptime(max_created[:10], "%Y-%m-%d").date()
# =====================================
# OUTLET -- BACA SEMUA DATA (API, via mirror SQLite)
# =====================================

def tampil_data():

    sync_outlet_to_sqlite()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nama_outlet, id_outlet, msisdn, input_by, created_at, flag_bio, ga_dt
        FROM outlet
        ORDER BY created_at DESC
    """)

    rows = [tuple(r) for r in cursor.fetchall()]
    conn.close()

    return rows


def tampil_data_by_date(start_date, end_date):

    sync_outlet_to_sqlite()

    start_str = f"{start_date.isoformat()} 00:00:00"
    end_str = f"{end_date.isoformat()} 23:59:59"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nama_outlet, id_outlet, msisdn, input_by, created_at, flag_bio, ga_dt
        FROM outlet
        WHERE created_at >= ? AND created_at <= ?
        ORDER BY created_at DESC
    """, (start_str, end_str))

    rows = [tuple(r) for r in cursor.fetchall()]
    conn.close()

    return rows

def last_input(limit=10):
    return tampil_data()[:limit]


def data_by_user(user):
    return [row for row in tampil_data() if row[4] == user]


def data_by_users(user_list):
    if not user_list:
        return []
    user_set = set(user_list)
    return [row for row in tampil_data() if row[4] in user_set]


def cek_msisdn(msisdn):
    for row in tampil_data():
        if row[3] == msisdn:
            # (input_by, created_at) -- sama seperti bentuk hasil SQLite lama
            return {"input_by": row[4], "created_at": row[5]}
    return None


# =====================================
# DASHBOARD (API, dihitung di Python)
# =====================================

def total_outlet():
    rows = tampil_data()
    return len({row[2] for row in rows if row[2]})  # id_outlet unik


def total_msisdn():
    return len(tampil_data())


def total_cse():
    raw_rows = _fetch_users_raw()
    return sum(1 for r in raw_rows if r.get("role") in ("CSE", "RSE"))


def total_bsm():
    raw_rows = _fetch_users_raw()
    return sum(1 for r in raw_rows if r.get("role") == "BSM")


# =====================================
# HIRARKI USER (API, dihitung di Python)
# =====================================

def bawahan(atasan):
    raw_rows = _fetch_users_raw()
    return [
        (r.get("user") or r.get("username"))
        for r in raw_rows
        if r.get("atasan") == atasan
    ]


def get_downline(user):
    raw_rows = _fetch_users_raw()

    atasan_children = {}
    for r in raw_rows:
        nama = r.get("user") or r.get("username")
        atasan_children.setdefault(r.get("atasan"), []).append(nama)

    hasil = []

    def cari(atasan):
        for nama in atasan_children.get(atasan, []):
            if nama not in hasil:
                hasil.append(nama)
                cari(nama)

    cari(user)
    return hasil


# =====================================
# HELPER USER (API)
# =====================================

def get_user_role(role):
    raw_rows = _fetch_users_raw()
    hasil = [
        (r.get("user") or r.get("username"))
        for r in raw_rows
        if r.get("role") == role
    ]
    return sorted(hasil)


def get_role(user):
    raw_rows = _fetch_users_raw()
    for r in raw_rows:
        if (r.get("user") or r.get("username")) == user:
            return r.get("role") or ""
    return ""


def get_atasan(user):
    raw_rows = _fetch_users_raw()
    for r in raw_rows:
        if (r.get("user") or r.get("username")) == user:
            return r.get("atasan") or ""
    return ""