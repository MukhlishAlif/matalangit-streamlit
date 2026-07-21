import os
import sqlite3
import requests
from datetime import datetime, date
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
    "outlet": "/sales-tap/legacy-report-range",
    "users": "/admin/users/legacy-report",
    "fl": "/bio/fetch-all-fl",
    "bio": "/bio/fetch-all-bio",
    "leave" : "/leave/export" 
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
    Timeout default 30 detik.
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

# =====================================================================================
# RAW FETCH DARI API (dipakai semua fungsi baca outlet/users di bawah)
# =====================================================================================
#
# POST /sales-tap/legacy-report-range -> POST TANPA payload, filter tanggal
# dilakukan di SQLite (bukan dikirim ke API). Field diasumsikan:
#   { "data": [ {id, nama_outlet, id_outlet, msisdn, input_by,
#       created_at, flag_bio}, ... ] }
#
# POST /admin/users/legacy-report -> { "data": [ {id, user, password, role,
#       atasan, status, created_at, brand, region, area, branch,
#       micro_cluster, real_name}, ... ] }
# =====================================================================================

@st.cache_data(ttl=120)
def _fetch_outlet_raw():
    """POST tanpa payload. Kalau gagal, return [] (tidak melempar exception)."""
    try:
        result = api_fetch(ENDPOINTS["outlet"], method="POST")
    except ApiError as e:
        print("[OUTLET] gagal ambil dari API:", e.status, e.message)
        return []

    if isinstance(result, dict):
        rows = result.get("data", [])
    elif isinstance(result, list):
        rows = result
    else:
        rows = []

    print(f"[OUTLET] Total data API : {len(rows)}")

    if rows:
        print("[OUTLET] Sample Record :", rows[0])
        print("[OUTLET] Field :", list(rows[0].keys()))

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
    "true"/"false"/"1"/"0"). Normalisasi jadi 0/1.
    """

    if value is None:
        return 0

    if isinstance(value, bool):
        return int(value)

    if isinstance(value, (int, float)):
        return int(bool(value))

    text = str(value).strip().lower()

    return 1 if text in ("1", "true", "ya", "yes") else 0

def _normalize_join_date(value):
    """
    Ambil tanggal join dari field 'join_date' kalau API menyediakannya,
    kalau tidak fallback ke tanggal dari 'created_at' (dipotong jadi
    YYYY-MM-DD saja, tanpa jam).
    """

    if not value:
        return ""

    text = str(value).strip()

    if not text:
        return ""

    # kalau formatnya "2024-05-01 10:23:00" atau ada "T" (ISO),
    # ambil bagian tanggalnya saja
    return text[:10]


def _outlet_row_tuple(r, bio_map=None):
    """
    Ubah 1 dict outlet dari API jadi tuple urutan tetap:
    (id, nama_outlet, id_outlet, msisdn, input_by, created_at, flag_bio, ga_dt)

    flag_bio  -> diambil dari record outlet itu sendiri (/sales-tap/legacy-report-range)
    ga_dt     -> diambil dari /bio/fetch-all-bio (bio_map, keyed by msisdn)
    """

    bio_map = bio_map or {}

    msisdn = r.get("msisdn") or r.get("MSISDN") or ""

    bio = bio_map.get(msisdn, {})

    ga_dt = bio.get("ga_dt") or ""

    return (
        r.get("id"),
        r.get("nama_outlet"),
        r.get("id_outlet"),
        msisdn,
        r.get("input_by"),
        r.get("created_at"),
        _normalize_flag_bio(r.get("flag_bio")),   # <-- dari outlet
        ga_dt,                                     # <-- dari fetch-all-bio
    )


def _user_row_dict(r):

    role_raw = r.get("role") or ""
    status_raw = r.get("status")

    created_at = r.get("created_at")

    join_date_raw = r.get("join_date") or created_at

    return {
        "id": r.get("id"),
        "user": r.get("user") or r.get("username"),
        "role": role_raw.upper(),
        "atasan": r.get("atasan"),
        "status": status_raw,
        "created_at": created_at,
        "join_date": _normalize_join_date(join_date_raw),
        "brand": r.get("brand"),
        "region": r.get("region"),
        "area": r.get("area"),
        "branch": r.get("branch"),
        "micro_cluster": r.get("micro_cluster"),
        "real_name": r.get("real_name") or r.get("full_name"),
        "flag_active": str(status_raw).strip().upper() == "AKTIF",
    }

# =====================================================================================
# RAW FETCH: GA BIOMETRIK (ga_dt) & FL LIST
# =====================================================================================
#
# POST /bio/fetch-all-bio -> { "data": [ {msisdn, ga_dt}, ... ] }
#   -- HANYA dipakai untuk ambil ga_dt per outlet (join by msisdn).
#      flag_bio TIDAK diambil dari sini -- diambil langsung dari record outlet.
#
# POST /bio/fetch-all-fl -> { "data": [ {organization_id, fl_id, brand,
#       region_name, sub_area_name, branch, micro_cluster_name,
#       fl_target, ga_mtd}, ... ] }
# =====================================================================================

@st.cache_data(ttl=120)
def _fetch_bio_raw():
    """Kalau gagal, return [] -- ga_dt akan default kosong."""
    try:
        result = api_fetch(ENDPOINTS["bio"], method="POST")
    except ApiError as e:
        print("[BIO] gagal ambil dari API:", e.status, e.message)
        return []

    rows = result.get("data", []) if isinstance(result, dict) else (result or [])
    return rows


def _build_bio_map():
    """Map msisdn -> ga_dt dari /bio/fetch-all-bio. Hanya ga_dt yang dipakai
    dari endpoint ini; flag_bio diambil langsung dari record outlet."""
    raw_rows = _fetch_bio_raw()

    bio_map = {}
    for r in raw_rows:
        msisdn = r.get("msisdn") or r.get("MSISDN") or ""
        if not msisdn:
            continue

        ga_dt = (
            r.get("ga_dt")
            or r.get("ga_date")
            or r.get("tanggal_biometrik")
            or ""
        )

        bio_map[msisdn] = {"ga_dt": ga_dt}

    return bio_map


@st.cache_data(ttl=120)
def _fetch_fl_raw():
    try:
        result = api_fetch(ENDPOINTS["fl"], method="POST")
    except ApiError as e:
        print("[FL] gagal ambil dari API:", e.status, e.message)
        return []

    rows = result.get("data", []) if isinstance(result, dict) else (result or [])
    return rows


def _fl_row_dict(r):
    """
    Field PERSIS sesuai response /bio/fetch-all-fl:
    organization_id, fl_id, brand, region_name, sub_area_name, branch,
    micro_cluster_name, fl_target, ga_mtd.

    ga_mtd = biometrik akumulasi bulan berjalan, SUDAH dihitung di
    sisi API.
    """
    return {
        "organization_id": str(r.get("organization_id") or "").strip(),
        "fl_id": r.get("fl_id"),
        "brand": r.get("brand"),
        "region_name": r.get("region_name"),
        "sub_area_name": r.get("sub_area_name"),
        "branch": r.get("branch"),
        "micro_cluster_name": r.get("micro_cluster_name"),
        "fl_target": r.get("fl_target") or 10,
        "ga_mtd": r.get("ga_mtd"),
    }


# =====================================================================================
# GABUNGAN: FL + BIOMETRIK + ELIGIBLE
# =====================================================================================

def load_fl_summary(brand_filter=None):
    fl_rows = _fetch_fl_raw()

    df_fl = pd.DataFrame([_fl_row_dict(r) for r in fl_rows])

    if df_fl.empty:
        return pd.DataFrame()

    if brand_filter and brand_filter != "Semua":
        df_fl = df_fl[df_fl["brand"] == brand_filter]

    df_fl["fl_target"] = pd.to_numeric(
        df_fl["fl_target"], errors="coerce"
    ).fillna(10).astype(int)

    df_fl["Biometrik"] = pd.to_numeric(
        df_fl["ga_mtd"], errors="coerce"
    ).fillna(0).astype(int)

    df_fl["Eligible"] = df_fl["Biometrik"] >= df_fl["fl_target"]

    return df_fl

MONTH_ID = [
    "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]
 
 
@st.cache_data(ttl=120)
def _fetch_leave_raw():
    """POST tanpa payload. Kalau gagal, return [] (tidak melempar exception)."""
    try:
        result = api_fetch(ENDPOINTS["leave"], method="GET")
    except ApiError as e:
        print("[LEAVE] gagal ambil dari API:", e.status, e.message)
        return []
 
    rows = result.get("data", []) if isinstance(result, dict) else (result or [])
    return rows
 
 
def _leave_row_dict(r):
    return {
        "id": r.get("id"),
        "user_code": r.get("user_code"),
        "full_name": r.get("full_name"),
        "leave_type": r.get("leave_type"),
        "start_date": _normalize_join_date(r.get("start_date")),
        "end_date": _normalize_join_date(r.get("end_date")),
        "reason": r.get("reason"),
        "attachment_url": r.get("attachment_url"),
        "approval_status": str(r.get("approval_status") or "").strip().upper(),
        "approved_by": r.get("approved_by"),
        "rejection_reason": r.get("rejection_reason"),
        "created_at": r.get("created_at"),
        "updated_at": r.get("updated_at"),
    }
 
LEAVE_TYPE_ID = {
    "sick": "Sakit",
    "leave": "Izin",
}

def _format_leave_label(leave_type, start_date_str, end_date_str):
    try:
        d1 = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        d2 = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return leave_type or ""

    # normalisasi: hilangkan spasi & lowercase sebelum dicocokkan ke dict
    key = str(leave_type or "").strip().lower().replace(" ", "_")
    label_type = LEAVE_TYPE_ID.get(key, leave_type)

    if d1 == d2:
        tanggal = f"{d1.day} {MONTH_ID[d1.month]} {d1.year}"
    elif d1.month == d2.month and d1.year == d2.year:
        tanggal = f"{d1.day}-{d2.day} {MONTH_ID[d2.month]} {d2.year}"
    else:
        tanggal = (
            f"{d1.day} {MONTH_ID[d1.month]} {d1.year} - "
            f"{d2.day} {MONTH_ID[d2.month]} {d2.year}"
        )

    return f"{label_type} ({tanggal})"
 
 
def load_leave_map(only_approved=True):
    raw_rows = _fetch_leave_raw()
    records = [_leave_row_dict(r) for r in raw_rows]

    leave_map = {}
    for rec in records:
        if only_approved and rec["approval_status"] != "APPROVED":
            continue

        if not rec["user_code"] or not rec["start_date"] or not rec["end_date"]:
            continue

        try:
            d1 = datetime.strptime(rec["start_date"], "%Y-%m-%d").date()
            d2 = datetime.strptime(rec["end_date"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        label = _format_leave_label(rec["leave_type"], rec["start_date"], rec["end_date"])

        key = str(rec["user_code"]).strip().upper()   # <-- TAMBAHKAN INI

        leave_map.setdefault(key, []).append({
            "start": d1,
            "end": d2,
            "label": label,
            "leave_type": rec["leave_type"],
        })

    return leave_map


def get_leave_flag(leave_map, user_code, check_date):
    key = str(user_code).strip().upper()   # <-- TAMBAHKAN INI
    entries = leave_map.get(key, [])
    labels = [e["label"] for e in entries if e["start"] <= check_date <= e["end"]]
    return "; ".join(labels)


def get_leave_flag_range(leave_map, user_code, filter_start, filter_end):
    key = str(user_code).strip().upper()   # <-- TAMBAHKAN INI
    entries = leave_map.get(key, [])
    labels = [
        e["label"] for e in entries
        if e["start"] <= filter_end and e["end"] >= filter_start
    ]
    return "; ".join(labels)
 


def load_outlet_bio_summary(brand_filter=None):
    fl_rows = _fetch_fl_raw()

    df_fl = pd.DataFrame([_fl_row_dict(r) for r in fl_rows])

    if df_fl.empty:
        return pd.DataFrame()

    df_fl["fl_id"] = df_fl["fl_id"].astype(str)

    df_fl["Brand"] = df_fl["fl_id"].apply(
        lambda x: "IM3" if x.strip().upper().endswith("IM3")
        else ("3ID" if x.strip().upper().endswith("3ID") else "")
    )

    if brand_filter and brand_filter != "Semua":
        df_fl = df_fl[df_fl["Brand"] == brand_filter]

    df_fl["fl_target"] = pd.to_numeric(df_fl["fl_target"], errors="coerce").fillna(10).astype(int)
    df_fl["ga_mtd"] = pd.to_numeric(df_fl["ga_mtd"], errors="coerce").fillna(0).astype(int)

    df_fl = df_fl.rename(columns={"ga_mtd": "Biometrik"})

    df_fl["Eligible"] = df_fl["Biometrik"] >= df_fl["fl_target"]

    return df_fl




# =====================================
# USER HIERARCHY (API)
# =====================================

@st.cache_data(ttl=300)
def load_user_hierarchy():

    raw_rows = _fetch_users_raw()

    records = [_user_row_dict(r) for r in raw_rows]

    default_cols = [
        "id", "user", "role", "atasan", "status", "created_at", "join_date",
        "brand", "region", "area", "branch", "micro_cluster", "real_name",
        "flag_active"
    ]

    df = pd.DataFrame(records, columns=default_cols)

    df.columns = df.columns.str.upper()

    for col in ["ATASAN", "ROLE", "STATUS", "JOIN_DATE"]:
        if col not in df.columns:
            df[col] = ""

    df["ATASAN"] = df["ATASAN"].fillna("")
    df["ROLE"] = df["ROLE"].fillna("")
    df["STATUS"] = df["STATUS"].fillna("AKTIF")
    df["JOIN_DATE"] = df["JOIN_DATE"].fillna("")

    # ==========================================
    # FLAG_ACTIVE: true = aktif, false = non-aktif (dihitung Vacant,
    # tidak boleh muncul sebagai team/bawahan di manapun)
    # ==========================================

    if "FLAG_ACTIVE" not in df.columns:
        df["FLAG_ACTIVE"] = True

    df["FLAG_ACTIVE"] = df["FLAG_ACTIVE"].fillna(True).astype(bool)

    df["BRAND"] = ""

    df.loc[
        df["ATASAN"].astype(str).str.lower().str.contains("_im3", na=False),
        "BRAND"
    ] = "IM3"

    df.loc[
        df["ATASAN"].astype(str).str.lower().str.contains("_3id", na=False),
        "BRAND"
    ] = "3ID"

    # role_map/atasan_map/brand_map/children_map TETAP dibangun dari SEMUA user
    # (termasuk non-aktif) -- supaya rantai atasan (upline) & susur hirarki
    # tidak putus kalau kebetulan ada 1 orang di tengah rantai yang non-aktif.
    # Filter "non-aktif tidak boleh dihitung/ditampilkan" dilakukan di
    # pemanggil (dashboard), BUKAN di sini.

    role_map = df.set_index("USER")["ROLE"].to_dict()
    atasan_map = df.set_index("USER")["ATASAN"].to_dict()
    brand_map = df.set_index("USER")["BRAND"].to_dict()

    children_map = {}
    for user, atasan in atasan_map.items():
        if atasan:
            children_map.setdefault(atasan, []).append(user)

    return (df, role_map, atasan_map, brand_map, children_map)


# =====================================
# TABEL USER & OUTLET (SQLite -- dipakai fungsi TULIS di bawah)
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
    raw_rows = _fetch_users_raw()

    return [
        {
            "user": d["user"],
            "role": d["role"],
            "atasan": d["atasan"],
            "real_name": d["real_name"],
            "status": d["status"],
            "flag_active": d["flag_active"],
            "join_date": d["join_date"],
        }
        for d in (_user_row_dict(r) for r in raw_rows)
    ]


def tampil_user_master():
    raw_rows = _fetch_users_raw()

    data = [_user_row_dict(r) for r in raw_rows]

    data.sort(key=lambda d: (str(d["role"] or ""), str(d["user"] or "")))

    return data


# =====================================
# USER -- TULIS (tetap SQLite, MENUNGGU konfirmasi endpoint create/update/delete)
# =====================================

def tambah_user(user, password, role, atasan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users(user, password, role, atasan)
        VALUES(?,?,?,?)
    """, (user, password, role, atasan))
    conn.commit()
    conn.close()


def update_user(old_user, new_user, password, role, atasan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET user=?, password=?, role=?, atasan=?
        WHERE user=?
    """, (new_user, password, role, atasan, old_user))
    conn.commit()
    berhasil = cursor.rowcount > 0
    conn.close()
    return berhasil


def hapus_user(user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user=?", (user,))
    conn.commit()
    conn.close()


# =====================================
# OUTLET -- TULIS (tetap SQLite, MENUNGGU konfirmasi endpoint create/update/delete)
# =====================================

def simpan_data(nama_outlet, id_outlet, msisdn, input_by):
    conn = get_connection()
    cursor = conn.cursor()

    waktu = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO outlet (nama_outlet, id_outlet, msisdn, input_by, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (nama_outlet, id_outlet, msisdn, input_by, waktu))

    conn.commit()
    conn.close()


def hapus_data(id_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM outlet WHERE id = ?", (id_data,))
    conn.commit()
    hasil = cursor.rowcount
    conn.close()
    return hasil


# =====================================
# OUTLET -- SYNC KE SQLITE LOKAL (mirror dari API, UPDATE bukan replace)
# =====================================

def sync_outlet_to_sqlite():
    """
    Ambil semua data outlet (POST tanpa payload, tanpa filter tanggal di API).
    flag_bio diambil langsung dari record outlet; ga_dt digabung dari
    /bio/fetch-all-bio (join by msisdn). Lalu UPDATE ke SQLite (upsert per id)
    -- data lama TIDAK dihapus dulu.
    """

    raw_rows = _fetch_outlet_raw()

    if not raw_rows:
        st.session_state["outlet_sync_error"] = "Gagal ambil data terbaru dari server. Menampilkan data terakhir yang tersimpan."
        return

    st.session_state["outlet_sync_error"] = None

    bio_map = _build_bio_map()

    rows = [_outlet_row_tuple(r, bio_map) for r in raw_rows]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany(
        """
        INSERT INTO outlet (
            id, nama_outlet, id_outlet, msisdn, input_by,
            created_at, flag_bio, ga_dt
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            nama_outlet = excluded.nama_outlet,
            id_outlet   = excluded.id_outlet,
            msisdn      = excluded.msisdn,
            input_by    = excluded.input_by,
            created_at  = excluded.created_at,
            flag_bio    = excluded.flag_bio,
            ga_dt       = excluded.ga_dt
        """,
        rows
    )

    conn.commit()
    conn.close()


# =====================================
# TANGGAL TERBARU YANG ADA DATANYA
# =====================================

def get_latest_data_date():
    sync_outlet_to_sqlite()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(created_at) FROM outlet")
    row = cursor.fetchone()

    conn.close()

    max_created = row[0] if row else None

    if not max_created:
        return date.today()

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
    """
    Filter range tanggal dilakukan di SQLite (WHERE created_at BETWEEN ...),
    karena API sekarang dipanggil tanpa payload/tanpa filter tanggal.
    """

    sync_outlet_to_sqlite()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id, nama_outlet, id_outlet, msisdn, input_by,
            created_at, flag_bio, ga_dt
        FROM outlet
        WHERE created_at >= ? AND created_at <= ?
        ORDER BY created_at DESC
        """,
        (f"{start_date} 00:00:00", f"{end_date} 23:59:59")
    )

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
            return {"input_by": row[4], "created_at": row[5]}
    return None


# =====================================
# DASHBOARD (API, dihitung di Python)
# =====================================

def total_outlet():
    rows = tampil_data()
    return len({row[2] for row in rows if row[2]})


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


if __name__ == "__main__":
    rows = _fetch_outlet_raw()
    print()
    print("TOTAL :", len(rows))
    if rows:
        print(rows[0])