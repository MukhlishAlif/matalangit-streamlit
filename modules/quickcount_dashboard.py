# ==========================================================
# IMPORT
# ==========================================================

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date, timedelta

from database import (
    tampil_data_by_date,
    load_user_hierarchy
)

# ==========================================================
# CONSTANTS
# ==========================================================

PERSONNEL_ROLES = ["BSM","DSE", "CSE", "RSE", "RGE", "PROMOTOR", "GSE", "FRONTLINER", "GEMINI","NP"]

TARGET_PER_DAY = 5

BRAND_COLOR = {
    "IM3": "#F59E0B",
    "3ID": "#EC1C4C"
}

PERSONNEL_GROUPS = {
    "CSE/RSE": ["CSE", "RSE"],
    "RGE": ["RGE"],
    "DSE": ["DSE"],
    "PROMOTOR": ["PROMOTOR"],
    "GSE": ["GSE"],
    "NP": ["NP"],
    "BSM": ["BSM"],
    "FRONTLINER": ["FRONLINER"],
    "GEMINI": ["GEMINI"],
}

# ==========================================================
# CSS
# ==========================================================

def inject_css():

    st.markdown("""
    <style>

    .stApp{
        background:#F5F7FB;
    }

    #MainMenu{visibility:hidden;}
    footer{visibility:hidden;}


    .mld-title{
        font-size:26px;
        font-weight:800;
        color:#1F2937;
        margin-bottom:0px;
    }

    .mld-sub{
        color:#6B7280;
        font-size:14px;
        margin-bottom:6px;
    }

    /* KPI CARD */

    .kpi-box{
        background:white;
        border-radius:16px;
        padding:16px 18px;
        box-shadow:0px 3px 12px rgba(0,0,0,.06);
    }

    .kpi-icon{
        width:42px;
        height:42px;
        border-radius:12px;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:20px;
        color:white;
        margin-bottom:8px;
    }

    .kpi-label{
        color:#6B7280;
        font-size:11px;
        font-weight:700;
        text-transform:uppercase;
        letter-spacing:.4px;
    }

    .kpi-value{
        font-size:26px;
        font-weight:800;
        color:#111827;
        margin-top:2px;
    }

    .kpi-foot{
        color:#9CA3AF;
        font-size:11px;
        margin-top:4px;
    }

    .mld-card-title{
        font-weight:800;
        font-size:14px;
        color:#374151;
        margin-bottom:12px;
    }


    /* ===== HOS ACHIEVEMENT - PODIUM ===== */

    .hos-panel{

        height:620px;
        display:flex;
        align-items:flex-end;

    }

    .podium-wrap{

        width:100%;

        display:flex;
        align-items:flex-end;
        justify-content:center;

        gap:15px;

        padding-top:15px;

    }

    .podium-card{

        flex:1;
        max-width:140px;

        border-radius:16px 16px 6px 6px;

        text-align:center;
        color:white;

        box-shadow:0 6px 16px rgba(0,0,0,.14);

        padding:14px 8px 12px 8px;

        position:relative;
        overflow:hidden;

        transition:all .2s ease;

        display:flex;
        flex-direction:column;
        justify-content:flex-end;

        align-self:flex-end;

    }

    .podium-card:hover{

        transform:translateY(-4px);

    }

    .podium-card::before{

        content:"";

        position:absolute;

        top:-24px;
        right:-24px;

        width:80px;
        height:80px;

        background:rgba(255,255,255,.10);

        border-radius:50%;

    }

    /* ===== Rank ===== */

    .podium-card.place-1{

        order:2;

        height:335px;

        background:linear-gradient(160deg,#A78BFA,#7C3AED);
        color:#FFFFFF;

        z-index:3;

    }

    .podium-card.place-2{

        order:1;

        height:300px;

        background:linear-gradient(160deg,#FF6B95,#EC1C4C);

        color:#FFFFFF;

    }

    .podium-card.place-3{

        order:3;

        height:270px;

        background:linear-gradient(160deg,#FFE066,#F5B400);

        color:#3A2A00;

    }

    .podium-card.place-4{

        order:4;

        height:235px;

        background:linear-gradient(160deg,#CBD5E1,#94A3B8);

        color:#1E293B;

    }

    .podium-crown{

        font-size:45px;

        margin-bottom:30px;

    }

    .podium-medal{

        display:inline-flex;

        align-items:center;
        justify-content:center;

        width:30px;
        height:30px;

        border-radius:50%;

        background:rgba(255,255,255,.35);

        font-weight:1000;

        font-size:20px;

        margin:0 auto 17px auto;

    }

    .podium-name{

        font-weight:700;

        font-size:13.5px;

        white-space:nowrap;

        overflow:hidden;

        text-overflow:ellipsis;

    }

    .podium-val{

        font-size:24px;

        font-weight:800;

        margin-top:6px;

    }

    .podium-caption{

        font-size:9.5px;

        opacity:.85;

        margin-top:2px;

    }

    .podium-submit-pill{

        display:inline-block;

        margin-top:8px;

        padding:3px 10px;

        border-radius:999px;

        background:rgba(255,255,255,.25);

        font-size:10.5px;

        font-weight:700;

    }

    /* ===== RANKING ROW v2 ===== */

    .rank-row{

        display:flex;
        align-items:center;

        gap:8px;

        padding:7px 4px;

        border-bottom:1px solid #F3F4F6;

    }

    .rank-row:last-child{

        border-bottom:none;

    }

    .rank-badge{

        flex-shrink:0;

        width:26px;
        height:26px;

        border-radius:50%;

        display:flex;
        align-items:center;
        justify-content:center;

        font-weight:800;
        font-size:12px;

        color:white;

    }

    .rank-body{

        flex:1;

        min-width:0;

    }

    .rank-name-row{

        display:flex;

        justify-content:space-between;

        align-items:center;

        gap:4px;

    }

    .rank-branch-name{

        font-weight:800;

        font-size:13px;

        color:#111827;

        white-space:nowrap;

        overflow:hidden;

        text-overflow:ellipsis;

    }

    .rank-avg-val{

        font-weight:800;

        font-size:15px;

        line-height:1;

        color:#111827;

    }

    .rank-avg-label{

        font-size:8px;

        margin-top:1px;

        color:#9CA3AF;

        font-weight:700;

        text-transform:uppercase;

        text-align:right;

        line-height:1;

    }

    .rank-meta-row{

        display:flex;

        justify-content:space-between;

        align-items:center;

        margin-top:3px;

        gap:6px;

    }

    .rank-submit-pill{

        font-size:10px;

        font-weight:700;

        color:#6B7280;

        background:#F3F4F6;

        padding:1px 7px;

        border-radius:999px;

        white-space:nowrap;

    }

    .rank-bar-track{

        flex:1;

        height:4px;

        background:#EEF1F6;

        border-radius:999px;

        overflow:hidden;

    }

    .rank-bar-fill{

        height:100%;

        border-radius:999px;

    }


    /* LEADERBOARD */

    .lb-title{
        font-weight:800;
        font-size:13px;
        color:#374151;
        margin-bottom:8px;
    }

    .lb-sub{
        font-size:10px;
        font-weight:700;
        color:#9CA3AF;
        text-transform:uppercase;
        margin-bottom:6px;
    }

    .lb-row{
        display:flex;
        justify-content:space-between;
        align-items:center;
        padding:5px 0px;
        border-bottom:1px solid #F5F5F5;
    }

    .lb-left{
        display:flex;
        align-items:center;
        gap:6px;
    }

    .lb-num{
        font-weight:800;
        font-size:11px;
        color:#9CA3AF;
        width:14px;
    }

    .lb-name{
        font-size:12px;
        font-weight:700;
        color:#111827;
    }

    .lb-branch{
        font-size:10px;
        color:#9CA3AF;
    }

    .lb-val{
        font-size:12px;
        font-weight:800;
        color:#374151;
    }

    /* ACHIEVEMENT BADGE */

    .badge-green{
        background:#DCFCE7;
        color:#15803D;
        font-weight:700;
        font-size:12px;
        padding:3px 8px;
        border-radius:6px;
    }

    .badge-amber{
        background:#FEF3C7;
        color:#B45309;
        font-weight:700;
        font-size:12px;
        padding:3px 8px;
        border-radius:6px;
    }

    .badge-red{
        background:#FEE2E2;
        color:#B91C1C;
        font-weight:700;
        font-size:12px;
        padding:3px 8px;
        border-radius:6px;
    }

    .muted-pill{
        color:#9CA3AF;
        font-size:12px;
    }

    /* jadikan container(border=True) bawaan streamlit terlihat seperti card */

    div[data-testid="stVerticalBlockBorderWrapper"]{
        border-radius:16px !important;
        box-shadow:0px 3px 12px rgba(0,0,0,.06);
    }

    section[data-testid="stSidebar"]{
        background:#FFFFFF;
    }
    /* ===== BRANCH PERFORMANCE - VISUAL BARU ===== */

    .branch-card-header{
        display:flex;
        justify-content:space-between;
        align-items:center;
        flex-wrap:wrap;
        gap:14px;
        padding:16px 18px;
        border-radius:14px;
        background:linear-gradient(135deg, rgba(37,99,235,.07), rgba(6,182,212,.07));
        border:1px solid rgba(37,99,235,.12);
        margin-bottom:16px;
    }

    .branch-card-name{
        font-weight:800;
        font-size:16px;
        color:#111827;
    }

    .branch-card-sub{
        font-size:12px;
        color:#6B7280;
        margin-top:2px;
    }

    .branch-stat-row{
        display:flex;
        gap:10px;
        flex-wrap:wrap;
    }

    .branch-stat-chip{
        background:white;
        border-radius:12px;
        padding:8px 16px;
        text-align:center;
        box-shadow:0 2px 8px rgba(0,0,0,.06);
        min-width:78px;
    }

    .branch-stat-val{
        font-size:16px;
        font-weight:800;
        color:#111827;
    }

    .branch-stat-label{
        font-size:9.5px;
        color:#9CA3AF;
        text-transform:uppercase;
        font-weight:700;
        letter-spacing:.3px;
        margin-top:1px;
    }

    .progress-wrap{
        margin:6px 0 18px 0;
    }

    .progress-label{
        display:flex;
        justify-content:space-between;
        font-size:11px;
        font-weight:700;
        color:#6B7280;
        margin-bottom:5px;
    }

    .progress-track{
        width:100%;
        height:9px;
        background:#EEF1F6;
        border-radius:999px;
        overflow:hidden;
    }

    .progress-fill{
        height:100%;
        border-radius:999px;
        transition:width .3s ease;
    }

    .mc-table{
        width:100%;
        border-collapse:separate;
        border-spacing:0;
        font-size:12.5px;
    }

    .mc-table th{
        text-align:left;
        color:#9CA3AF;
        font-size:10px;
        text-transform:uppercase;
        letter-spacing:.3px;
        font-weight:800;
        padding:9px 10px;
        border-bottom:2px solid #F1F5F9;
        background:#FAFBFF;
    }

    .mc-table td{
        padding:10px 10px;
        border-bottom:1px solid #F5F5F7;
        color:#374151;
    }

    .mc-table tr:hover td{
        background:#F8FAFF;
    }

    .mc-name-cell{
        font-weight:700;
        color:#111827;
    }

    .delta-up{
        color:#15803D;
        font-weight:800;
        background:#DCFCE7;
        padding:2px 8px;
        border-radius:999px;
        font-size:11.5px;
    }

    .delta-down{
        color:#B91C1C;
        font-weight:800;
        background:#FEE2E2;
        padding:2px 8px;
        border-radius:999px;
        font-size:11.5px;
    }

    .delta-flat{
        color:#6B7280;
        font-weight:700;
        background:#F3F4F6;
        padding:2px 8px;
        border-radius:999px;
        font-size:11.5px;
    }

    .delta-new{
        color:#1D4ED8;
        font-weight:800;
        background:#DBEAFE;
        padding:2px 8px;
        border-radius:999px;
        font-size:11.5px;
    }

    .mini-badge{
        font-weight:700;
        font-size:11px;
        padding:2px 9px;
        border-radius:999px;
    }

    .mat-icon{
        font-variation-settings:'FILL' 1;
        vertical-align:middle;
        line-height:1;
    }

    </style>
    """, unsafe_allow_html=True)


# ==========================================================
# DATA LOADING & HIERARCHY
# ==========================================================

@st.cache_data(ttl=120)
def load_all_data(start_date, end_date):
    buffer_start = start_date - timedelta(days=3)

    outlet_rows = tampil_data_by_date(buffer_start, end_date)

    (
        df_user,
        role_map,
        atasan_map,
        brand_map,
        children_map
    ) = load_user_hierarchy()

    # ------------------------------------------------
    # OUTLET
    # ------------------------------------------------
    # Catatan: khusus Quick Count, "Biometrik" di sini dipakai untuk
    # info tambahan saja -- metrik utama Quick Count tetap JUMLAH BARIS
    # SUBMIT (bukan biometrik). Kolom Biometrik diambil LANGSUNG dari
    # flag_bio yang dikirim API per baris outlet (lewat SELECT di
    # tampil_data_by_date), tidak perlu load_biometrik()/merge manual lagi.
    # ------------------------------------------------

    df = pd.DataFrame(

        outlet_rows,

        columns=[
            "ID",
            "Nama Outlet",
            "ID Outlet",
            "MSISDN",
            "Input By",
            "Tanggal",
            "Biometrik",
            "ga_dt"
        ]

    )

    df["MSISDN"] = df["MSISDN"].fillna("").astype(str).str.strip()

    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")

    df["Biometrik"] = df["Biometrik"].fillna(0).astype(int)

    # ------------------------------------------------
    # BUANG BARIS DI LUAR RENTANG TANGGAL SEDINI MUNGKIN,
    # sebelum susur hierarki (baris yang tersisa jadi lebih sedikit
    # kalau histori data-nya besar).
    # ------------------------------------------------

    df = df[
        (df["Tanggal"].dt.date >= buffer_start)
        &
        (df["Tanggal"].dt.date <= end_date)
    ].copy()

    def ancestor_by_role(start_user, target_roles, max_depth=15):

        current = start_user
        depth = 0

        while current and depth < max_depth:

            if role_map.get(current, "") in target_roles:

                return current

            current = atasan_map.get(current, "")

            depth += 1

        return None

    df["Role"] = df["Input By"].map(role_map).fillna("")

    unique_users = df["Input By"].dropna().unique()

    mc_lookup = {u: (ancestor_by_role(u, {"CSE", "RSE"}) or "-") for u in unique_users}
    branch_lookup = {u: (ancestor_by_role(u, {"BSM"}) or "-") for u in unique_users}
    hos_lookup = {u: (ancestor_by_role(u, {"HOS"}) or "-") for u in unique_users}

    df["MC"] = df["Input By"].map(mc_lookup).fillna("-")
    df["Branch"] = df["Input By"].map(branch_lookup).fillna("-")
    df["HOS"] = df["Input By"].map(hos_lookup).fillna("-")

    df["Brand"] = df["Input By"].map(brand_map).fillna("")

    df = df[df["Role"].isin(PERSONNEL_ROLES)]
    df = df[df["Brand"] != ""]

    return df, df_user, role_map, atasan_map, brand_map, children_map


def get_descendants(root, children_map, max_depth=20):

    hasil = []
    queue = [root]
    depth = 0

    while queue and depth < max_depth:

        nxt = []

        for node in queue:

            for child in children_map.get(node, []):

                if child not in hasil:

                    hasil.append(child)
                    nxt.append(child)

        queue = nxt
        depth += 1

    return hasil


def ancestor_lookup(u, target_roles, role_map, atasan_map, max_depth=15):

    current = u
    depth = 0

    while current and depth < max_depth:

        if role_map.get(current, "") in target_roles:

            return current

        current = atasan_map.get(current, "")

        depth += 1

    return "-"


# ==========================================================
# HELPER FORMAT
# ==========================================================

def fmt(n):

    try:

        return f"{int(n):,}".replace(",", ".")

    except Exception:

        return str(n)

def mat_icon(name, size=16, color=None, valign=-3):
    """Render ikon Material Symbols sebagai pengganti emoji."""

    style = f"font-size:{size}px;vertical-align:{valign}px;"

    if color:
        style += f"color:{color};"

    return f'<span class="material-symbols-outlined mat-icon" style="{style}">{name}</span>'


def achievement_badge(pct):

    if pct >= 100:

        cls = "badge-green"
        arrow = "▲"

    elif pct >= 90:

        cls = "badge-amber"
        arrow = "▲"

    else:

        cls = "badge-red"
        arrow = "▼"

    return f'<span class="{cls}">{arrow} {pct:.0f}%</span>'


def to_excel(data):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        data.to_excel(writer, index=False)

    return output.getvalue()


def kpi_card(icon, label, value, foot, color):

    st.markdown(
        f"""
        <div class="kpi-box">
            <div class="kpi-icon" style="background:{color};">
                <span class="material-symbols-outlined">{icon}</span>
            </div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def lb_row(rank, name, branch, value):

    st.markdown(
        f"""
        <div class="lb-row">
            <div class="lb-left">
                <span class="lb-num">{rank}</span>
                <div>
                    <div class="lb-name">{name}</div>
                    <div class="lb-branch">{branch}</div>
                </div>
            </div>
            <div class="lb-val">{fmt(value)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# MAIN
# ==========================================================
import base64

@st.cache_data
def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

im3_icon = get_base64_image("im3.png")
tid_icon = get_base64_image("3id.png")

def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def show():

    st.markdown(
        """
        <link rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" />
        """,
        unsafe_allow_html=True
    )
    
    inject_css()

    # ------------------------------------------------
    # Hierarki user (df_user, role_map, dst) TIDAK tergantung
    # tanggal filter, jadi diambil duluan di sini (cache ttl=300)
    # supaya bisa dipakai untuk header & dropdown HoS sebelum
    # tahu tanggal apa yang dipilih user.
    # ------------------------------------------------
    (
        df_user,
        role_map,
        atasan_map,
        brand_map,
        children_map
    ) = load_user_hierarchy()

    # ------------------------------------------------
    # HEADER
    # ------------------------------------------------
    current_user = st.session_state.get("outlet_user", "-")
    current_role = role_map.get(current_user, "-")

    real_name_map = (
        df_user
        .drop_duplicates(subset="USER")
        .assign(USER=lambda x: x["USER"].astype(str).str.strip().str.upper())
        .set_index("USER")["REAL_NAME"]
        .to_dict()
    )
    display_name = real_name_map.get(
        str(current_user).strip().upper(),
        current_user
    )

    initials = "".join(
        [w[0].upper() for w in str(display_name).split()[:2]]
    ) or "-"

    # Load logo jadi base64
    logo_b64 = get_base64_image("icon.png")  # sesuaikan path kalau perlu, mis. "assets/icon.png"

    st.markdown(
        f"""
        <style>
        .mld-header {{
            border-radius: 16px;
            overflow: hidden;
            background: linear-gradient(120deg, #F5B400 0%, #F0997B 35%, #D4537E 70%, #993556 100%);
            padding: 1.5rem 1.75rem;
            margin-bottom: 1.5rem;
            position: relative;
        }}
        .mld-header-inner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
            position: relative;
        }}
        .mld-title-row {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .mld-logo-img {{
            width: 70px;
            height: 70px;
            object-fit: contain;
            filter: drop-shadow(0 1px 2px rgba(0,0,0,0.15));
        }}
        .mld-title-row span.mld-title-text {{
            font-size: 28px;
            font-weight: 600;
            color: #fff;
        }}
        .mld-sub {{
            font-size: 14px;
            color: rgba(255,255,255,0.88);
            margin-top: 4px;
        }}
        .mld-pill {{
            background: rgba(255,255,255,0.18);
            color: #fff;
            font-size: 12px;
            padding: 4px 12px;
            border-radius: 20px;
            display: inline-block;
        }}
        .mld-pill-row {{
            display: flex;
            gap: 8px;
            margin-top: 12px;
        }}
        .mld-user-card {{
            background: rgba(255,255,255,0.16);
            border-radius: 12px;
            padding: 12px 18px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .mld-avatar {{
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 15px;
            color: #993556;
            flex-shrink: 0;
        }}
        .mld-user-name {{
            font-weight: 600;
            font-size: 15px;
            color: #fff;
        }}
        .mld-role-pill {{
            background: rgba(255,255,255,0.25);
            color: #fff;
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 10px;
            margin-top: 2px;
            display: inline-block;
        }}
        </style>

        <div class="mld-header">
            <div class="mld-header-inner">
                <div>
                    <div class="mld-title-row">
                        <img src="data:image/jpg;base64,{logo_b64}" class="mld-logo-img" />
                        <span class="mld-title-text">Leaderboard Quick Count</span>
                    </div>
                    <div class="mld-sub">
                        Leaderboard berdasarkan jumlah submit MSISDN
                    </div>
                </div>
            </div>
        </div>

        <script>
        function mldTick() {{
            var d = new Date();
            var h = String(d.getHours()).padStart(2, '0');
            var m = String(d.getMinutes()).padStart(2, '0');
            var s = String(d.getSeconds()).padStart(2, '0');
            var el = document.getElementById('mld-clock');
            if (el) {{ el.textContent = h + ':' + m + ':' + s + ' WIB'; }}
        }}
        mldTick();
        setInterval(mldTick, 1000);
        </script>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------
    # FILTER BAR
    # ------------------------------------------------

    f1, f2, f3, f4, f5, f6 = st.columns([2, 1.2, 1.5, 1.5, 1, 1])

    with f1:

        periode = st.date_input(

            ":material/calendar_month: Filter Tanggal",

            value=(date.today(), date.today()),   # <-- tuple = aktifkan mode rentang, default cuma hari ini

            key="mld_periode"

        )

        if isinstance(periode, tuple):
            if len(periode) == 2:
                start_date, end_date = periode
            else:
                start_date = end_date = periode[0]
        else:
            start_date = end_date = periode

    # ==========================================
    # LOAD DATA OUTLET SESUAI TANGGAL YANG DIPILIH.
    # df_user/role_map/atasan_map/brand_map/children_map SUDAH
    # diambil di atas (tidak tergantung tanggal), jadi di sini
    # cukup ambil df-nya saja -- tidak menimpa variabel di atas.
    # ==========================================

    df, _, _, _, _, _ = load_all_data(start_date, end_date)

    with f2:

        selected_brand = st.selectbox(
            "Brand",
            ["Semua Brand", "IM3", "3ID"],
            key="qc_brand"
        )

    with f3:

        hos_list = sorted(
            df_user[df_user["ROLE"] == "HOS"]["USER"].dropna().unique().tolist()
        )

        selected_hos = st.selectbox(
            "HoS Area",
            ["Semua HoS"] + hos_list,
            key="qc_hos"
        )

    with f4:

        selected_group = st.selectbox(
            "Personnel",
            ["Semua Personnel"] + list(PERSONNEL_GROUPS.keys()),
            key="qc_personnel"
        )

    with f5:

        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        st.download_button(
            ":material/download: Export",
            data=to_excel(df),
            file_name="leaderboard_quickcount.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with f6:

        st.markdown("<div style='height:23px'></div>", unsafe_allow_html=True)

        if st.button("Refresh", use_container_width=True, key="mld_refresh"):

            # Bersihkan cache load_all_data supaya data ke-load ulang
            # dari database, bukan dari cache lama.
            st.cache_data.clear()

            st.rerun()

    # ------------------------------------------------
    # APPLY FILTER
    # ------------------------------------------------

    dff = df.copy()

    # ==========================================
    # PASTIKAN KOLOM TANGGAL BERTIPE DATETIME
    # ==========================================

    dff["Tanggal"] = pd.to_datetime(
        dff["Tanggal"]
    )

    # ==========================================
    # FILTER PERIODE
    # ==========================================

    if isinstance(periode, tuple):

        if len(periode) == 2:

            start_date, end_date = periode

        else:

            start_date = end_date = periode[0]

    else:

        start_date = end_date = periode

    dff = dff[

        (dff["Tanggal"].dt.date >= start_date)

        &

        (dff["Tanggal"].dt.date <= end_date)

    ]

    # ==========================================
    # FILTER BRAND
    # ==========================================

    if selected_brand != "Semua Brand":

        dff = dff[

            dff["Brand"] == selected_brand

        ]

    # ==========================================
    # FILTER HOS
    # ==========================================

    if selected_hos != "Semua HoS":

        dff = dff[

            dff["HOS"] == selected_hos

        ]

    # ==========================================
    # FILTER PERSONNEL
    # ==========================================

    if selected_group != "Semua Personnel":

        dff = dff[

            dff["Role"].isin(

                PERSONNEL_GROUPS[
                    selected_group
                ]

            )

        ]

    st.divider()

    # =====================================================
    # PERSONNEL
    # =====================================================

    all_personnel = df_user[
        df_user["ROLE"].isin(PERSONNEL_ROLES)
    ]

    active_personnel = df_user[
        (df_user["ROLE"].isin(PERSONNEL_ROLES))
        &
        (df_user["STATUS"].astype(str).str.upper() == "AKTIF")
    ]

    if selected_brand != "Semua Brand":

        all_personnel = all_personnel[
            all_personnel["BRAND"] == selected_brand
        ]

        active_personnel = active_personnel[
            active_personnel["BRAND"] == selected_brand
        ]

    if selected_group != "Semua Personnel":

        all_personnel = all_personnel[
            all_personnel["ROLE"].isin(PERSONNEL_GROUPS[selected_group])
        ]

        active_personnel = active_personnel[
            active_personnel["ROLE"].isin(PERSONNEL_GROUPS[selected_group])
        ]

    # ==========================================
    # Hanya personel aktif yang submit pada periode terpilih
    # ==========================================

    submitted_users = (
        dff["Input By"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    active_personnel = active_personnel[
        active_personnel["USER"]
        .astype(str)
        .str.strip()
        .isin(submitted_users)
    ]

    total_team = all_personnel["USER"].nunique()
    active_team = active_personnel["USER"].nunique()

# ==========================================
    # METRIK UTAMA QUICK COUNT = JUMLAH SUBMIT
    # ==========================================

    submit_im3 = len(dff[dff["Brand"] == "IM3"])
    submit_3id = len(dff[dff["Brand"] == "3ID"])
    submit_total = len(dff)

    # ==========================================
    # TOTAL VACANT (REAL_NAME KOSONG/NULL/NONE/-)
    # ==========================================

    total_vacant = all_personnel[
        (all_personnel["REAL_NAME"].isna()) |
        (all_personnel["REAL_NAME"].astype(str).str.strip() == "") |
        (all_personnel["REAL_NAME"].astype(str).str.upper() == "VACANT") |
        (all_personnel["REAL_NAME"].astype(str).str.upper() == "NONE") |
        (all_personnel["REAL_NAME"].astype(str).str.strip() == "-")
    ]["USER"].nunique()

    # ==========================================
    # TEAM PER BRAND
    # ==========================================

    team_im3 = all_personnel[
        all_personnel["BRAND"] == "IM3"
    ]["USER"].nunique()

    team_3id = all_personnel[
        all_personnel["BRAND"] == "3ID"
    ]["USER"].nunique()

    # ==========================================
    # AVG SUBMIT / PERSONEL
    # ==========================================

    avg_im3 = (
        submit_im3 / team_im3
        if team_im3 else 0
    )

    avg_3id = (
        submit_3id / team_3id
        if team_3id else 0
    )

    avg_total = (
        submit_total / total_team
        if total_team else 0
    )

    kpi_defs = [

        (
            "group",
            "Team Total",
            fmt(total_team),
            "-",
            "#3B82F6"
        ),

        (
            "person_off",
            "Vacant",
            fmt(total_vacant),
            "-",
            "#EF4444"
        ),

        (
            "bolt",
            "Team Aktif",
            fmt(active_team),
            "-",
            "#10B981"
        ),

        (
            f'<img src="data:image/png;base64,{im3_icon}" style="width:35px;height:35px;object-fit:contain;vertical-align:-4px;" />',
            "Submit IM3",
            fmt(submit_im3),
            f"Avg {avg_im3:.1f} Submit/Person",
            "#F59E0B"
        ),

        (
            f'<img src="data:image/png;base64,{tid_icon}" style="width:28px;height:28px;object-fit:contain;vertical-align:-4px;" />',
            "Submit 3ID",
            fmt(submit_3id),
            f"Avg {avg_3id:.1f} Submit/Person",
            "#EC1C4C"
        ),

        (
            "lock",
            "Submit Total",
            fmt(submit_total),
            f"Avg {avg_total:.1f} Submit/Person",
            "#0F766E"
        ),

    ]

    kpi_cols = st.columns(6)

    for col, (icon, label, value, foot, color) in zip(kpi_cols, kpi_defs):

        with col:

            kpi_card(icon, label, value, foot, color)

    st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------------
    # PERSONNEL SUMMARY - SUBMIT (Versi Rapi & Manteb)
    # ------------------------------------------------

    st.markdown(
        '<h3><span class="material-symbols-outlined" style="vertical-align:-6px;">group</span> Performance</h3>',
        unsafe_allow_html=True
    )

    role_icons = {
        "BSM": mat_icon("person", size=13, valign=-2),
        "RGE": mat_icon("person", size=13, valign=-2),
        "CSE": mat_icon("person", size=13, valign=-2),
        "DSE": mat_icon("person", size=13, valign=-2)

    }

    def get_theme(percent):

        if percent >= 80:

            return {

                "grad": "linear-gradient(160deg, #34d399 0%, #059669 100%)"

            }

        elif percent >= 50:

            return {

                "grad": "linear-gradient(160deg, #fbbf24 0%, #d97706 100%)"

            }

        else:

            return {

                "grad": "linear-gradient(160deg, #f87171 0%, #dc2626 100%)"

            }

    role_groups = {
        "BSM": ["BSM"],
        "CSE/RSE": ["CSE", "RSE"],
        "RGE": ["RGE"],
        "DSE": ["DSE"],
        "DSE PROMOTOR": ["PROMOTOR"],
        "Promotor": ["NP"],
        "GSE": ["GSE"],
        "GEMPI": ["GEMINI"],
    }

    role_summary = []

    for group_label, roles in role_groups.items():

        # Total personel aktif
        total_role = df_user[

            (df_user["ROLE"].isin(roles))
            &
            (df_user["STATUS"].astype(str).str.upper() == "AKTIF")
            &
            (
                (selected_brand == "Semua Brand")
                |
                (df_user["BRAND"] == selected_brand)
            )

        ]["USER"].nunique()

        role_data = dff[

            dff["Role"].isin(roles)

        ]

        # Personel yang submit
        input_role = role_data["Input By"].nunique()

        # Total submit
        submit_role = len(role_data)

        # Persentase personel yang submit
        percent = (

            input_role / total_role * 100

        ) if total_role > 0 else 0

        # Average submit per personel yang submit
        avg_submit = (

            submit_role / input_role

        ) if input_role > 0 else 0

        role_summary.append({

            "Role": group_label,

            "Total": total_role,

            "Input": input_role,

            "Submit": submit_role,

            "Avg Submit": avg_submit,

            "Persentase": percent

        })

    summary_role = pd.DataFrame(
        role_summary
    )

    st.markdown(

        """
        <style>

        .kpi-card{

            background:var(--accent-grad, #d1d5db);
            border-radius:16px;
            padding:16px 14px;
            text-align:center;
            box-shadow:0 4px 14px rgba(0,0,0,.12);
            transition:all .18s ease;
            margin-bottom:22px;

        }

        .kpi-card:hover{

            box-shadow:0 8px 20px rgba(0,0,0,.18);
            transform:translateY(-2px);

        }

        .kpi-icon-badge{

            width:28px;
            height:28px;
            border-radius:9px;
            background:rgba(255,255,255,.22);
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:13px;
            color:white;
            margin:0 auto 8px auto;

        }

        .kpi-role{

            font-size:15px;
            font-weight:700;
            letter-spacing:.8px;
            text-transform:uppercase;
            color:#ffffff;
            margin-bottom:10px;

        }

        .kpi-ring-wrap{

            display:flex;
            justify-content:center;
            margin-bottom:8px;

        }

        .kpi-percent{

            font-size:14px;
            font-weight:800;
            fill:#ffffff;

        }

        .kpi-footer{

            font-size:14px;
            font-weight:600;
            color:rgba(255,255,255,.92);
            margin-bottom:2px;

        }

        .kpi-avg{

            font-size:12px;
            font-weight:500;
            color:rgba(255,255,255,.72);

        }

        </style>
        """,

        unsafe_allow_html=True

    )

    # Layout 4 kolom per baris (otomatis lanjut ke baris berikutnya)
    CARDS_PER_ROW = 4

    for row_start in range(0, len(summary_role), CARDS_PER_ROW):

        chunk = summary_role.iloc[
            row_start:row_start + CARDS_PER_ROW
        ]

        cols = st.columns(CARDS_PER_ROW)

        for col_idx, (_, row) in enumerate(chunk.iterrows()):

            theme = get_theme(
                row["Persentase"]
            )

            icon = role_icons.get(

                row["Role"],

                mat_icon("person", size=13, valign=-2)

            )

            pct = row["Persentase"]

            radius = 30

            circumference = 2 * 3.14159 * radius

            offset = circumference - (

                pct / 100 * circumference

            )

            # PENTING: string dibangun satu baris (tanpa newline/indentasi),
            # kalau tidak Streamlit akan menganggapnya sebagai code block Markdown.
            ring_svg = (
                '<div class="kpi-ring-wrap">'
                '<svg width="76" height="76" viewBox="0 0 76 76">'
                f'<circle cx="38" cy="38" r="{radius}" stroke="rgba(255,255,255,.28)" stroke-width="6" fill="none" />'
                f'<circle cx="38" cy="38" r="{radius}" stroke="#ffffff" stroke-width="6" fill="none" '
                f'stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{offset:.1f}" stroke-linecap="round" '
                f'transform="rotate(-90 38 38)" />'
                f'<text x="38" y="43" text-anchor="middle" class="kpi-percent">{pct:.0f}%</text>'
                '</svg>'
                '</div>'
            )

            card_html = (
                f'<div class="kpi-card" style="--accent-grad:{theme["grad"]};">'
                f'<div class="kpi-icon-badge">{icon}</div>'
                f'<div class="kpi-role">{row["Role"]}</div>'
                f'{ring_svg}'
                f'<div class="kpi-footer">{row["Input"]} / {row["Total"]} personel</div>'
                f'<div class="kpi-avg">{row["Submit"]} submit &middot; avg {row["Avg Submit"]:.1f}</div>'
                '</div>'
            )

            with cols[col_idx]:

                st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    # ------------------------------------------------
    # Helper kompak: 1 baris ranking branch (avg + total submit),
    # ukurannya disamakan dengan card leaderboard (lb-row).
    # ------------------------------------------------

    def lb_branch_row(rank_label, branch_name, bsm_name, avg_val, total_val):

        st.markdown(
            f"""
            <div class="lb-row">
                <div class="lb-left">
                    <span class="lb-num">{rank_label}</span>
                    <div>
                        <div class="lb-name">{branch_name}</div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div class="lb-val">{avg_val:.1f}</div>
                    <div style="font-size:12px;color:#9CA3AF;">{mat_icon("send", size=12, valign=-4)} {fmt(total_val)} · Avg/Person</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ------------------------------------------------
    # Helper: render 1 card branch (Top3 + Bottom3) untuk 1 brand.
    # Logic IM3 & 3ID identik, jadi cukup ditulis sekali.
    # ------------------------------------------------

    def render_brand_branch_card(brand, brand_label):

        st.markdown(
            f"<div class='mld-card-title'>{mat_icon('emoji_events', size=16, color='#F59E0B', valign=-3)} {brand_label} Branch (by Avg Submit / Person)</div>",
            unsafe_allow_html=True
        )

        bsm_name_map = (
            df_user[
                df_user["ROLE"].astype(str).str.upper() == "BSM"
            ]
            .drop_duplicates(subset="USER")
            .assign(
                USER=lambda x: x["USER"].astype(str).str.strip().str.upper()
            )
            .set_index("USER")["REAL_NAME"]
            .to_dict()
        )

        branch_scores = []

        for branch_name, branch_df in dff[dff["Brand"] == brand].groupby("Branch"):

            total_submit = len(branch_df)

            total_person = branch_df["Input By"].nunique()

            avg_submit = (total_submit / total_person) if total_person > 0 else 0

            bsm_name = bsm_name_map.get(str(branch_name).strip().upper(), "-")

            branch_scores.append((branch_name, bsm_name, total_submit, avg_submit))

        top3 = sorted(branch_scores, key=lambda x: x[3], reverse=True)[:3]
        bottom3 = sorted(branch_scores, key=lambda x: x[3])[:3][::-1]

        medals = {
            1: mat_icon("military_tech", size=16, color="#FFD700"),
            2: mat_icon("military_tech", size=16, color="#C0C0C0"),
            3: mat_icon("military_tech", size=16, color="#CD7F32"),
        }

        st.markdown("<div class='lb-sub'>Top 3</div>", unsafe_allow_html=True)

        if not top3:
            st.caption("Belum ada data.")
        else:
            for i, (branch_name, bsm_name, total_submit, avg_submit) in enumerate(top3, start=1):
                lb_branch_row(medals.get(i, str(i)), branch_name, bsm_name, avg_submit, total_submit)

        st.markdown("<div class='lb-sub' style='margin-top:8px;'>Bottom 3</div>", unsafe_allow_html=True)

        if not bottom3:
            st.caption("Belum ada data.")
        else:
            for i, (branch_name, bsm_name, total_submit, avg_submit) in enumerate(bottom3, start=0):
                lb_branch_row(mat_icon("trending_down", size=16, color="#EF4444"), branch_name, bsm_name, avg_submit, total_submit)

 # ------------------------------------------------
    # ACHIEVEMENT HOS + IM3 + 3ID BRANCH
    # (berbasis JUMLAH SUBMIT, bukan Biometrik)
    # ------------------------------------------------

    col_hos, col_im3, col_3id = st.columns([1.6, 0.8, 0.8])

    with col_hos:

        with st.container(border=True):

            st.markdown(
                f"<div class='mld-card-title'>{mat_icon('military_tech', size=18, color='#FFD700', valign=-4)} Achievement HOS (by Avg Submit / Person)</div>",
                unsafe_allow_html=True
            )

            real_name_map = (
                df_user
                .drop_duplicates(subset="USER")
                .set_index("USER")["REAL_NAME"]
                .to_dict()
            )

            hos_scores = []

            for hos_user in hos_list:

                downline = get_descendants(hos_user, children_map)

                hos_df = dff[dff["Input By"].isin(downline)]

                if hos_df.empty:
                    continue

                total_submit = len(hos_df)
                total_person = hos_df["Input By"].nunique()
                avg_submit = (total_submit / total_person) if total_person > 0 else 0

                hos_scores.append((
                    hos_user,
                    real_name_map.get(hos_user, "-"),
                    total_submit,
                    avg_submit,
                    atasan_map.get(hos_user, "-")
                ))

            hos_scores = sorted(hos_scores, key=lambda x: x[3], reverse=True)[:4]

            if hos_scores:

                medal_icon = {
                    1: mat_icon("military_tech", size=20, color="#FFD700", valign=-4),
                    2: mat_icon("military_tech", size=20, color="#C0C0C0", valign=-4),
                    3: mat_icon("military_tech", size=20, color="#CD7F32", valign=-4),
                    4: mat_icon("workspace_premium", size=20, color="#94A3B8", valign=-4),
                }
                crown = {1: mat_icon("workspace_premium", size=45, color="#FFD700", valign=-8)}

                podium_cards = []

                for i, (username, real_name, total_submit, avg_submit, atasan) in enumerate(hos_scores, start=1):

                    card_html = (
                        f'<div class="podium-card place-{i}">'
                        f'<div class="podium-crown">{crown.get(i, "")}</div>'
                        f'<div class="podium-medal">{medal_icon.get(i, i)}</div>'
                        f'<div class="podium-name">{username}</div>'
                        f'<div style="font-size:10px;opacity:.82;margin-top:-2px;margin-bottom:6px;">{real_name}</div>'
                        f'<div class="podium-val">{avg_submit:.1f}</div>'
                        f'<div class="podium-caption">Avg Submit / Person</div>'
                        f'<div class="podium-submit-pill">{mat_icon("check_circle", size=12, valign=-2)}  {fmt(total_submit)} Submit</div>'
                        f'</div>'
                    )

                    podium_cards.append(card_html)

                st.markdown(
                    '<div class="podium-wrap">' + "".join(podium_cards) + "</div>",
                    unsafe_allow_html=True
                )

            else:

                st.info("Belum ada data HoS untuk periode/filter ini.")

    with col_im3:

        with st.container(border=True):

            render_brand_branch_card("IM3", "IM3")

    with col_3id:

        with st.container(border=True):

            render_brand_branch_card("3ID", "3ID")

# ------------------------------------------------
    # 6 LEADERBOARD: BSM, CSE/RSE, DSE, RGE, PROMOTOR, NP
    # (Total Submit, bukan Total Biometrik)
    # ------------------------------------------------

    st.markdown(

        """
        <style>

        .lb-card-wrap{

            position:relative;
            overflow:hidden;
            width:100%;
            box-sizing:border-box;

        }

        .lb-card-title{

            font-size:14px;
            font-weight:800;
            color:#111827;
            padding:12px 14px 10px 14px;
            box-sizing:border-box;

        }

        .lb-card-title .lb-total-tag{

            font-size:10.5px;
            font-weight:600;
            color:#9ca3af;
            margin-left:4px;

        }

        .lb-split{

            display:grid;
            grid-template-columns:1fr 1fr;
            width:100%;
            box-sizing:border-box;
            overflow:hidden;

        }

        .lb-side{

            padding:0 0 10px 0;
            min-width:0;
            box-sizing:border-box;

        }

        .lb-side.top{

            border-right:1px solid #eef0f3;
            padding-right:2px;

        }

        .lb-side.bottom{

            padding-left:2px;

        }

        .lb-side-header{

            display:flex;
            align-items:center;
            gap:6px;
            font-size:10.5px;
            font-weight:800;
            letter-spacing:.5px;
            text-transform:uppercase;
            padding:6px 12px;
            margin:0 10px 6px 10px;
            border-radius:8px;

        }

        .lb-side-header.top{

            color:#059669;
            background:rgba(5,150,105,.10);

        }

        .lb-side-header.bottom{

            color:#dc2626;
            background:rgba(220,38,38,.10);

        }

        .lb-item{

            display:flex;
            align-items:center;
            gap:14px;
            padding:9px 12px;

        }

        .lb-item:nth-child(even){

            background:#fafafa;

        }

        .lb-rank{

            flex:0 0 20px;
            height:20px;
            border-radius:50%;
            background:#eef0f3;
            color:#9ca3af;
            font-size:11px;
            display:flex;
            align-items:center;
            justify-content:center;

        }

        .lb-rank .material-symbols-outlined{

            font-size:12px !important;

        }

        .lb-side.top .lb-item:nth-child(1) .lb-rank{

            background:#059669;
            color:#ffffff;

        }

        .lb-side.top .lb-item:nth-child(2) .lb-rank,
        .lb-side.top .lb-item:nth-child(3) .lb-rank{

            background:rgba(5,150,105,.12);
            color:#059669;

        }

        .lb-side.bottom .lb-item:nth-child(1) .lb-rank{

            background:#dc2626;
            color:#ffffff;

        }

        .lb-side.bottom .lb-item:nth-child(2) .lb-rank,
        .lb-side.bottom .lb-item:nth-child(3) .lb-rank{

            background:rgba(220,38,38,.12);
            color:#dc2626;

        }

        .lb-name-block{

            flex:1 1 auto;
            min-width:0;

        }

        .lb-name{

            font-size:11.5px;
            font-weight:600;
            color:#111827;
            line-height:1.3;
            margin-bottom:2px;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis;

        }

        .lb-branch{

            font-size:10px;
            color:#9ca3af;
            line-height:1.2;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis;

        }

        .lb-value{

            flex:0 0 auto;
            font-size:12.5px;
            font-weight:800;
            color:#111827;
            padding-left:4px;

        }

        .lb-empty{

            padding:4px 12px 8px 12px;
            font-size:11px;
            color:#c1c5cc;

        }

        </style>
        """,

        unsafe_allow_html=True

    )

    # Map username -> nama asli (strip + upper biar aman dari mismatch)
    real_name_map = (
        df_user
        .drop_duplicates(subset="USER")
        .assign(USER=lambda x: x["USER"].astype(str).str.strip().str.upper())
        .set_index("USER")["REAL_NAME"]
        .to_dict()
    )

    lb_defs = [
        ("BSM", PERSONNEL_GROUPS["BSM"]),
        ("CSE / RSE", PERSONNEL_GROUPS["CSE/RSE"]),
        ("DSE", PERSONNEL_GROUPS["DSE"]),
        ("RGE", PERSONNEL_GROUPS["RGE"]),
        ("DSE PROMOTOR", PERSONNEL_GROUPS["PROMOTOR"]),
        ("Promotor", PERSONNEL_GROUPS["NP"]),
    ]

    # Layout 3 kolom per baris:
    # Baris 1 -> BSM | CSE/RSE | DSE
    # Baris 2 -> RGE | PROMOTOR | NP
    LB_PER_ROW = 3

    for row_start in range(0, len(lb_defs), LB_PER_ROW):

        chunk_defs = lb_defs[row_start:row_start + LB_PER_ROW]

        lb_cols = st.columns(LB_PER_ROW)

        for col, (title, roles) in zip(lb_cols, chunk_defs):
            with col:
                with st.container(border=True):

                    # ==========================================
                    # BASE: SEMUA USER DENGAN ROLE INI
                    # (bukan cuma yang ada di dff)
                    # ==========================================

                    base_users = df_user[
                        df_user["ROLE"].isin(roles)
                    ][["USER", "BRANCH"]].drop_duplicates(subset="USER").rename(
                        columns={"USER": "Input By", "BRANCH": "Branch"}
                    )

                    # Kalau brand/branch difilter di halaman ini, terapkan juga ke base_users
                    if selected_brand != "Semua Brand":
                        base_users = df_user[
                            (df_user["ROLE"].isin(roles))
                            & (df_user["BRAND"] == selected_brand)
                        ][["USER", "BRANCH"]].drop_duplicates(subset="USER").rename(
                            columns={"USER": "Input By", "BRANCH": "Branch"}
                        )

                    # ==========================================
                    # SUBMIT COUNT DARI dff (bisa kosong utk user tertentu)
                    # ==========================================

                    submit_count = (
                        dff[dff["Role"].isin(roles)]
                        .groupby("Input By")
                        .size()
                        .reset_index(name="Submit")
                    )

                    # ==========================================
                    # LEFT JOIN: semua user tetap muncul, yang gak submit -> 0
                    # ==========================================

                    grp = base_users.merge(
                        submit_count,
                        on="Input By",
                        how="left"
                    )

                    grp["Submit"] = grp["Submit"].fillna(0).astype(int)

                    grp = grp.sort_values("Submit", ascending=False)

                    # Tambahkan kolom Real Name (fallback ke username kalau kosong/tidak ada)

                    real_name_raw = (
                        grp["Input By"]
                        .astype(str)
                        .str.strip()
                        .str.upper()
                        .map(real_name_map)
                    )

                    real_name_str = (
                        real_name_raw
                        .astype(str)
                        .str.strip()
                        .str.upper()
                    )

                    is_invalid = (
                        real_name_raw.isna()
                        | real_name_str.isin(["", "VACANT", "NAN", "NONE", "NAT"])
                    )

                    grp["Real Name"] = real_name_raw.where(
                        ~is_invalid,
                        grp["Input By"]
                    )

                    top3 = grp.head(3)
                    bottom3 = (
                        grp
                        .nsmallest(3, "Submit")
                        .sort_values("Submit", ascending=False)
                    )

                    def build_lb_items(df_rank, side_icon):

                        # PENTING: setiap baris dibangun tanpa newline/indentasi
                        # supaya Streamlit tidak menganggapnya sebagai code block Markdown.
                        if df_rank.empty:
                            return '<div class="lb-empty">-</div>'

                        rank_icon = mat_icon(side_icon, size=12, valign=-2)

                        rows_html = ""

                        for i, r in enumerate(df_rank.itertuples(), start=0):

                            name = getattr(r, "_4")
                            branch = r.Branch
                            value = r.Submit

                            rows_html += (
                                '<div class="lb-item">'
                                f'<div class="lb-rank">{rank_icon}</div>'
                                '<div class="lb-name-block">'
                                f'<div class="lb-name">{name}</div>'
                                f'<div class="lb-branch">{branch}</div>'
                                '</div>'
                                f'<div class="lb-value">{value}</div>'
                                '</div>'
                            )

                        return rows_html

                    card_html = (
                        '<div class="lb-card-wrap">'
                        f'<div class="lb-card-title">{title} '
                        f'<span class="lb-total-tag">(Total Submit)</span></div>'
                        '<div class="lb-split">'
                        '<div class="lb-side top">'
                        '<div class="lb-side-header top">Top 3</div>'
                        f'{build_lb_items(top3, "military_tech")}'
                        '</div>'
                        '<div class="lb-side bottom">'
                        '<div class="lb-side-header bottom">Bottom 3</div>'
                        f'{build_lb_items(bottom3, "trending_down")}'
                        '</div>'
                        '</div>'
                        '</div>'
                    )

                    st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
# ------------------------------------------------
    # BRANCH PERFORMANCE TABLE
    # (metrik utama = jumlah submit MSISDN)
    # ------------------------------------------------
    """
    with st.container(border=True):

        st.markdown(
            f"<div class='mld-card-title'>{mat_icon('assignment', size=18, valign=-4)} Branch Performance</div>",
            unsafe_allow_html=True
        )

        t1, t2 = st.columns([1, 3])

        with t1:

            table_group = st.selectbox(
                "Personnel (tabel)",
                list(PERSONNEL_GROUPS.keys()),
                key="qc_table_personnel"
            )

        with t2:

            st.markdown(
                f"<div style='font-size:13px;margin-bottom:2px;'>{mat_icon('search', size=14, valign=-2)} Search Branch / MC</div>",
                unsafe_allow_html=True
            )
            search = st.text_input(
                "Search Branch / MC",
                key="qc_search",
                label_visibility="collapsed"
            )

        roles_for_table = PERSONNEL_GROUPS[table_group]

        table_df = dff[
            dff["Role"].isin(roles_for_table)
        ].copy()

        # User yang submit pada periode terpilih
        submitted_users = (
            table_df["Input By"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )

        roster = df_user[

            (df_user["ROLE"].isin(roles_for_table))
            &
            (
                (selected_brand == "Semua Brand")
                |
                (df_user["BRAND"] == selected_brand)
            )

        ].copy()

        # Hanya personel yang submit pada periode terpilih
        roster = roster[

            roster["USER"]
            .astype(str)
            .str.strip()
            .isin(submitted_users)

        ]

        roster["Branch"] = roster["USER"].apply(

            lambda u: ancestor_lookup(
                u,
                {"BSM"},
                role_map,
                atasan_map
            )

        )

        roster["MC"] = roster["USER"].apply(

            lambda u: ancestor_lookup(
                u,
                {"CSE", "RSE"},
                role_map,
                atasan_map
            )

        )

        branch_list = sorted(

            table_df["Branch"]
            .dropna()
            .unique()

        )

        if search:

            branch_list = [

                b for b in branch_list

                if search.lower() in b.lower()

            ]

        if not branch_list:

            st.info("Tidak ada data Branch untuk filter ini.")

        for branch_name in branch_list:

            branch_roster = roster[roster["Branch"] == branch_name]
            branch_data = table_df[table_df["Branch"] == branch_name]

            n_personnel = branch_roster["USER"].nunique()
            n_active = branch_data["Input By"].nunique()
            n_submit = len(branch_data)

            avg_per_person = (

                n_submit / n_personnel

                if n_personnel

                else 0

            )
            with st.expander(
                f"**{branch_name}**  ·  {n_personnel} personnel  ·  "
                f"{fmt(n_submit)} submit  ",
                expanded=False
            ):

                b1, b2, b3, b4 = st.columns(4)

                b1.metric("# Personnel", n_personnel)

                b2.metric("Active", n_active)

                b3.metric("Submit", fmt(n_submit))

                b4.metric(
                    "Avg/Person",
                    f"{avg_per_person:.1f}"
                )

                mc_list = sorted(

                    branch_data["MC"]
                    .dropna()
                    .unique()

                )

                mc_list = [m for m in mc_list if m and m != "-"]

                rows = []

                for mc_name in mc_list:

                    mc_roster = branch_roster[
                        branch_roster["MC"] == mc_name
                    ]

                    mc_data = branch_data[
                        branch_data["MC"] == mc_name
                    ]

                    mc_personnel = mc_roster["USER"].nunique()

                    mc_active = mc_data["Input By"].nunique()

                    mc_submit = len(mc_data)

                    mc_avg = (

                        mc_submit / mc_personnel

                        if mc_personnel

                        else 0

                    )

                    # ======================================
                    # DATA FULL (TIDAK TERFILTER PERIODE)
                    # ======================================

                    mc_all = df[

                        (df["MC"] == mc_name)

                        &

                        (
                            (selected_brand == "Semua Brand")
                            |
                            (df["Brand"] == selected_brand)
                        )

                    ].copy()

                    if selected_hos != "Semua HoS":

                        mc_all = mc_all[
                            mc_all["HOS"] == selected_hos
                        ]

                    # gunakan role filter yang SAMA dengan tabel ini
                    # (roles_for_table = PERSONNEL_GROUPS[table_group])
                    # bukan filter personnel global (selected_group),
                    # supaya D-1/D-2/D-3 konsisten dengan kolom Submit di baris ini
                    mc_all = mc_all[
                        mc_all["Role"].isin(roles_for_table)
                    ]

                    mc_all["Tanggal"] = pd.to_datetime(
                        mc_all["Tanggal"]
                    )

                    # ======================================
                    # D-1 / D-2 / D-3
                    # berdasarkan tanggal akhir filter
                    # ======================================

                    d1_date = end_date - timedelta(days=1)
                    d2_date = end_date - timedelta(days=2)
                    d3_date = end_date - timedelta(days=3)

                    d1 = len(
                        mc_all[
                            mc_all["Tanggal"].dt.date == d1_date
                        ]
                    )

                    d2 = len(
                        mc_all[
                            mc_all["Tanggal"].dt.date == d2_date
                        ]
                    )

                    d3 = len(
                        mc_all[
                            mc_all["Tanggal"].dt.date == d3_date
                        ]
                    )

                    rows.append({

                        "MC": mc_name,
                        "# Personnel": mc_personnel,
                        "Active": mc_active,
                        "Submit": mc_submit,
                        "Avg/Person": round(
                            mc_avg,
                            1
                        ),

                        f"D-1 ({d1_date.strftime('%d/%m')})": d1,
                        f"D-2 ({d2_date.strftime('%d/%m')})": d2,
                        f"D-3 ({d3_date.strftime('%d/%m')})": d3

                    })

                if rows:

                    st.dataframe(

                        pd.DataFrame(rows),

                        use_container_width=True,

                        hide_index=True

                    )

                else:

                    st.caption("Belum ada Micro Cluster / data untuk branch ini.")
    """

    DATE_COL = "Tanggal"

    dff[DATE_COL] = pd.to_datetime(dff[DATE_COL], errors="coerce").dt.date
# ------------------------------------------------
# SECTION 1: TEAM PERFORMANCE
# (3 TAB: HOS, BSM, CSE/RSE)
# ------------------------------------------------
    with st.container(border=True):

        title_col, filter_brand_col, filter_personnel_col = st.columns([2.5, 1, 1.5])

        with title_col:
            st.markdown(
                f"<div class='mld-card-title'>{mat_icon('table_chart', size=18, valign=-4)} Team Performance</div>",
                unsafe_allow_html=True
            )

        with filter_brand_col:
            brand_options = ["Semua Brand", "IM3", "3ID"]
            selected_brand_filter = st.selectbox(
                "Brand",
                brand_options,
                key="team_brand_filter",
                label_visibility="collapsed"
            )

        with filter_personnel_col:
            personnel_options = ["Semua Personnel"] + list(PERSONNEL_GROUPS.keys())
            selected_personnel_filter = st.selectbox(
                "Personnel",
                personnel_options,
                key="team_personnel_filter",
                label_visibility="collapsed"
            )

        st.markdown(
            """
            <style>

                .mld-stat-chip {
                    border-radius: 12px;
                    padding: 12px 14px;
                    height: 100%;
                    border: 1px solid #E2E8F0;
                    background: #F8FAFC;
                }

                .mld-stat-chip .mld-stat-label {
                    font-size: 11px;
                    font-weight: 600;
                    letter-spacing: .3px;
                    text-transform: uppercase;
                    margin-bottom: 4px;
                    color: #64748B;
                }

                .mld-stat-chip .mld-stat-value {
                    font-size: 20px;
                    font-weight: 700;
                    color: #0F172A;
                }

                /* -- Slate (default/Jumlah) -- */
                .mld-stat-chip.mld-stat-slate {
                    background: #F8FAFC;
                    border: 1px solid #E2E8F0;
                }
                .mld-stat-chip.mld-stat-slate .mld-stat-label { color: #64748B; }
                .mld-stat-chip.mld-stat-slate .mld-stat-value { color: #0F172A; }

                /* -- Blue (MSISDN) -- */
                .mld-stat-chip.mld-stat-blue {
                    background: #EFF6FF;
                    border: 1px solid #BFDBFE;
                }
                .mld-stat-chip.mld-stat-blue .mld-stat-label { color: #1D4ED8; }
                .mld-stat-chip.mld-stat-blue .mld-stat-value { color: #1D4ED8; }

                /* -- Purple -- */
                .mld-stat-chip.mld-stat-purple {
                    background: #F5F3FF;
                    border: 1px solid #DDD6FE;
                }
                .mld-stat-chip.mld-stat-purple .mld-stat-label { color: #6D28D9; }
                .mld-stat-chip.mld-stat-purple .mld-stat-value { color: #6D28D9; }

                /* -- Green (KPI utama / rata-rata) -- */
                .mld-stat-chip.mld-stat-green {
                    background: #ECFDF5;
                    border: 1px solid #A7F3D0;
                }
                .mld-stat-chip.mld-stat-green .mld-stat-label { color: #047857; }
                .mld-stat-chip.mld-stat-green .mld-stat-value { color: #047857; }

                /* -- Amber (warning / belum capai target) -- */
                .mld-stat-chip.mld-stat-amber {
                    background: #FFFBEB;
                    border: 1px solid #FDE68A;
                }
                .mld-stat-chip.mld-stat-amber .mld-stat-label { color: #B45309; }
                .mld-stat-chip.mld-stat-amber .mld-stat-value { color: #B45309; }

                /* -- Red (danger) -- */
                .mld-stat-chip.mld-stat-danger {
                    background: #FEF2F2;
                    border: 1px solid #FECACA;
                }
                .mld-stat-chip.mld-stat-danger .mld-stat-label { color: #B91C1C; }
                .mld-stat-chip.mld-stat-danger .mld-stat-value { color: #DC2626; }

                /* -- Orange (Jumlah) -- */
                .mld-stat-chip.mld-stat-orange {
                    background: #FFF7ED;
                    border: 1px solid #FED7AA;
                }
                .mld-stat-chip.mld-stat-orange .mld-stat-label { color: #C2410C; }
                .mld-stat-chip.mld-stat-orange .mld-stat-value { color: #C2410C; }

                button[data-baseweb="tab"] {
                    border-radius: 10px 10px 0 0 !important;
                    font-weight: 600 !important;
                }

            </style>
            """,
            unsafe_allow_html=True
        )

     # ==========================================
    # HITUNG TANGGAL D-1, D-2, D-3 DARI end_date PERIODE
    # ==========================================

    if isinstance(periode, tuple):
        if len(periode) == 2:
            _start_date_tmp, _end_date_tmp = periode
        elif len(periode) == 1:
            _start_date_tmp = _end_date_tmp = periode[0]
        else:
            _start_date_tmp = _end_date_tmp = date.today()
    else:
        _start_date_tmp = _end_date_tmp = periode

    d1_date = _end_date_tmp - timedelta(days=1)
    d2_date = _end_date_tmp - timedelta(days=2)
    d3_date = _end_date_tmp - timedelta(days=3)

    d1_label = f"D-1 ({d1_date.strftime('%d/%m')})"
    d2_label = f"D-2 ({d2_date.strftime('%d/%m')})"
    d3_label = f"D-3 ({d3_date.strftime('%d/%m')})"

    # ==========================================
    # FUNGSI HELPER (khusus Team Performance)
    # (SEMUA BERBASIS SUBMIT, BUKAN BIOMETRIK)
    # ==========================================

    def get_msisdn_avg_team(user_list):

        user_data = dff[
            dff["Input By"].isin(user_list)
        ]

        if selected_brand_filter != "Semua Brand":
            user_data = user_data[
                user_data["Brand"] == selected_brand_filter
            ]

        if selected_personnel_filter != "Semua Personnel":
            user_data = user_data[
                user_data["Role"].isin(
                    PERSONNEL_GROUPS[
                        selected_personnel_filter
                    ]
                )
            ]

        total_msisdn = len(user_data)

        # pembagi = jumlah orang (dari user_list) yang BENAR-BENAR submit
        total_person_submit = user_data["Input By"].nunique()

        avg_per_person = (
            (total_msisdn / total_person_submit)
            if total_person_submit > 0
            else 0
        )

        return total_msisdn, total_person_submit, avg_per_person

    def get_submit_by_date_team(user_list, target_date):
        user_data = df[
            df["Input By"].isin(user_list)
        ].copy()

        if selected_brand_filter != "Semua Brand":
            user_data = user_data[
                user_data["Brand"] == selected_brand_filter
            ]

        if selected_personnel_filter != "Semua Personnel":
            user_data = user_data[
                user_data["Role"].isin(
                    PERSONNEL_GROUPS[selected_personnel_filter]
                )
            ]

        # samakan tipe: strip jam, sisakan tanggal murni, baru dibandingkan
        tanggal_only = pd.to_datetime(user_data["Tanggal"]).dt.date

        return len(
            user_data[
                tanggal_only == target_date
            ]
        )

    def stat_chip(label, value, color="slate"):
        """color: slate, blue, purple, green, amber, orange, danger"""

        css_class = f"mld-stat-chip mld-stat-{color}"

        st.markdown(
            f"""
            <div class="{css_class}">
                <div class="mld-stat-label">{label}</div>
                <div class="mld-stat-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    def build_rekap_rows(
        role_filter,
        id_col_name,
        include_role_col=False,
        leaf=False
    ):

        rows = []

        role_list = (
            role_filter
            if isinstance(role_filter, list)
            else [role_filter]
        )

        all_users = df_user[
            df_user["ROLE"].isin(role_list)
        ]["USER"].unique().tolist()

        if selected_brand_filter != "Semua Brand":

            all_users = df_user[
                (df_user["ROLE"].isin(role_list))
                &
                (
                    df_user["BRAND"]
                    == selected_brand_filter
                )
            ]["USER"].unique().tolist()

        for u in all_users:

            u_info = df_user[
                df_user["USER"] == u
            ].iloc[0]

            u_name = u_info["REAL_NAME"]
            u_role = u_info["ROLE"]

            downline = [u] + (
                []
                if leaf
                else get_descendants(
                    u,
                    children_map
                )
            )

            u_msisdn, u_person_submit, u_avg = (
                get_msisdn_avg_team(
                    downline
                )
            )

            d1_submit = get_submit_by_date_team(
                downline,
                d1_date
            )

            d2_submit = get_submit_by_date_team(
                downline,
                d2_date
            )

            d3_submit = get_submit_by_date_team(
                downline,
                d3_date
            )

            row = {
                id_col_name: u,
                "Nama": u_name,
                "MSISDN": u_msisdn,
                "Avg MSISDN/Person": round(u_avg, 1),
                d1_label: d1_submit,
                d2_label: d2_submit,
                d3_label: d3_submit,
            }

            if include_role_col:
                row["Role"] = u_role

            rows.append(row)

        return rows

    def render_rekap_table(
        rows,
        id_col,
        target_threshold=None
    ):

        if not rows:
            st.info("Tidak ada data.")
            return

        dfr = pd.DataFrame(rows)

        total_msisdn = int(
            dfr["MSISDN"].sum()
        )

        avg_msisdn_person = (
            round(
                dfr["Avg MSISDN/Person"].mean(),
                1
            )
            if len(dfr) > 0
            else 0
        )

        n_chip = (
            4
            if target_threshold is not None
            else 3
        )

        chip_cols = st.columns(n_chip)

        with chip_cols[0]:
            stat_chip("Jumlah", len(dfr), color="orange")

        with chip_cols[1]:
            stat_chip(
                "MSISDN",
                f"{total_msisdn:,}",
                color="blue"
            )

        with chip_cols[2]:
            stat_chip(
                "Avg MSISDN/Person%",
                f"{avg_msisdn_person}",
                color="green"
            )

        if target_threshold is not None:

            below_target = int(
                (
                    dfr["MSISDN"]
                    < target_threshold
                ).sum()
            )

            with chip_cols[3]:
                stat_chip(
                    f"Belum Capai Target (<{target_threshold} MSISDN)",
                    below_target,
                    color="amber" if below_target > 0 else "slate"
                )

        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )

        dfr = dfr.sort_values(
            "Avg MSISDN/Person",
            ascending=False
        )

        column_config = {
            id_col: st.column_config.TextColumn(width=130),
            "Nama": st.column_config.TextColumn(width=190),
            "MSISDN": st.column_config.NumberColumn(format="%d", width=100),
            "Avg MSISDN/Person": st.column_config.NumberColumn(format="%.1f", width=140),
            d3_label: st.column_config.NumberColumn(format="%d", width=100),
            d2_label: st.column_config.NumberColumn(format="%d", width=100),
            d1_label: st.column_config.NumberColumn(format="%d", width=100),
        }

        if "Role" in dfr.columns:
            column_config["Role"] = st.column_config.TextColumn(width=80)

        if target_threshold is not None:

            def highlight_below_target(row):
                if row["MSISDN"] < target_threshold:
                    return ['background-color: #FEE2E2; color: #991B1B;'] * len(row)
                return [''] * len(row)

            styled = dfr.style.apply(highlight_below_target, axis=1)

            st.dataframe(
                styled,
                use_container_width=True,
                hide_index=True,
                column_config=column_config
            )

        else:
            st.dataframe(
                dfr,
                use_container_width=True,
                hide_index=True,
                column_config=column_config
            )

    tab_hos, tab_bsm, tab_cse = st.tabs([
        ":material/apartment: HOS",
        ":material/supervisor_account: BSM",
        ":material/group: CSE/RSE"
    ])

    with tab_hos:
        rows_hos = build_rekap_rows("HOS", "HOS")
        render_rekap_table(rows_hos, "HOS", target_threshold=None)

    with tab_bsm:
        rows_bsm = build_rekap_rows("BSM", "BSM")
        render_rekap_table(rows_bsm, "BSM", target_threshold=None)

    with tab_cse:
        rows_cse = build_rekap_rows(["CSE", "RSE"], "CSE/RSE", include_role_col=False)
        render_rekap_table(rows_cse, "CSE/RSE", target_threshold=None)

    st.divider()

# ------------------------------------------------
# SECTION 2: INDIVIDUAL PERFORMANCE
# (6 TAB: BSM, CSE/RSE, DSE, RGE, PROMOTOR, NP)
# Kolom MSISDN/Avg Submit/Day tetap dari INPUT BY DIA SENDIRI.
# Kolom D-1/D-2/D-3 = submission TURUNAN (dia + descendants) pada tanggal itu.
# ------------------------------------------------

    TARGET_AVG_PER_DAY_MIN = 5

    df_user["ROLE"] = df_user["ROLE"].astype(str).str.strip().str.upper()
    df_user["USER"] = df_user["USER"].astype(str).str.strip()
    df_user["ATASAN"] = df_user["ATASAN"].astype(str).str.strip()

    if isinstance(periode, tuple):
        if len(periode) == 2:
            start_date, end_date = periode
        elif len(periode) == 1:
            start_date = end_date = periode[0]
        else:
            start_date = end_date = date.today()
    else:
        start_date = end_date = periode

    n_days = max((end_date - start_date).days + 1, 1)

    # tanggal D-1/D-2/D-3 mengikuti end_date (sama seperti Section 1)
    d1_date = end_date - timedelta(days=1)
    d2_date = end_date - timedelta(days=2)
    d3_date = end_date - timedelta(days=3)

    d1_label = f"D-1 ({d1_date.strftime('%d/%m')})"
    d2_label = f"D-2 ({d2_date.strftime('%d/%m')})"
    d3_label = f"D-3 ({d3_date.strftime('%d/%m')})"

    atasan_map = (
        df_user
        .drop_duplicates(subset="USER")
        .set_index("USER")["ATASAN"]
        .to_dict()
    )

    def get_ancestors(user):
        ancestors = []
        current = atasan_map.get(user)
        seen = set()
        while current and current not in seen and current != "NAN":
            ancestors.append(current)
            seen.add(current)
            current = atasan_map.get(current)
        return ancestors

    def matches_hierarchy_filter(u, selected_hos, selected_bsm, selected_cse):
        ancestors = get_ancestors(u)

        if selected_hos != "Semua HOS":
            if not (u == selected_hos or selected_hos in ancestors):
                return False

        if selected_bsm != "Semua BSM":
            if not (u == selected_bsm or selected_bsm in ancestors):
                return False

        if selected_cse != "Semua CSE/RSE":
            if not (u == selected_cse or selected_cse in ancestors):
                return False

        return True

    with st.container(border=True):

        st.markdown(
            f"<div class='mld-card-title'>{mat_icon('flag', size=18, valign=-4)} Individual Performance</div>",
            unsafe_allow_html=True
        )

        f_brand, f_hos, f_bsm, f_cse = st.columns(4)

        with f_brand:
            brand_options = ["Semua Brand", "IM3", "3ID"]
            selected_brand_filter = st.selectbox(
                ":material/sim_card: Filter Brand",
                brand_options,
                key="ip_filter_brand"
            )

        hos_candidates = df_user[df_user["ROLE"] == "HOS"]
        if selected_brand_filter != "Semua Brand":
            hos_candidates = hos_candidates[
                hos_candidates["BRAND"] == selected_brand_filter
            ]

        hos_options = ["Semua HOS"] + sorted(
            hos_candidates["USER"].unique().tolist()
        )

        with f_hos:
            selected_hos = st.selectbox(
                ":material/apartment: Filter HOS",
                hos_options,
                key="ip_filter_hos"
            )

        bsm_candidates = df_user[df_user["ROLE"] == "BSM"]

        if selected_brand_filter != "Semua Brand":
            bsm_candidates = bsm_candidates[
                bsm_candidates["BRAND"] == selected_brand_filter
            ]

        if selected_hos != "Semua HOS":
            bsm_candidates = bsm_candidates[
                bsm_candidates["ATASAN"] == selected_hos
            ]

        bsm_options = ["Semua BSM"] + sorted(
            bsm_candidates["USER"].unique().tolist()
        )

        with f_bsm:
            selected_bsm = st.selectbox(
                ":material/supervisor_account: Filter BSM",
                bsm_options,
                key="ip_filter_bsm"
            )

        cse_candidates = df_user[
            df_user["ROLE"].isin(["CSE", "RSE"])
        ]

        if selected_brand_filter != "Semua Brand":
            cse_candidates = cse_candidates[
                cse_candidates["BRAND"] == selected_brand_filter
            ]

        if selected_bsm != "Semua BSM":
            cse_candidates = cse_candidates[
                cse_candidates["ATASAN"] == selected_bsm
            ]

        elif selected_hos != "Semua HOS":

            bsm_under_hos = df_user[
                (df_user["ROLE"] == "BSM")
                & (df_user["ATASAN"] == selected_hos)
            ]["USER"].tolist()

            cse_candidates = cse_candidates[
                cse_candidates["ATASAN"].isin(bsm_under_hos)
            ]

        cse_options = ["Semua CSE/RSE"] + sorted(
            cse_candidates["USER"].unique().tolist()
        )

        with f_cse:
            selected_cse = st.selectbox(
                ":material/group: Filter CSE/RSE",
                cse_options,
                key="ip_filter_cse"
            )

        st.caption(
            f"Berdasarkan input by masing-masing user • periode {n_days} hari • "
            f"target minimal {TARGET_AVG_PER_DAY_MIN} submit/hari • "
        )

    def get_msisdn_bio_individual(user_list):
        user_data = dff[dff["Input By"].isin(user_list)]
        total_msisdn = len(user_data)
        total_bio = len(user_data[user_data["Biometrik"] == True])
        persen_bio = (total_bio / total_msisdn * 100) if total_msisdn > 0 else 0
        return total_msisdn, total_bio, persen_bio

    def get_msisdn_by_date_team(user_list, target_date):
        """Jumlah MSISDN submission pada 1 tanggal, untuk list user (dia + turunannya)."""
        user_data = df[
            df["Input By"].isin(user_list)
        ].copy()

        tanggal_only = pd.to_datetime(
            user_data[DATE_COL]
        ).dt.date

        user_data = user_data[
            tanggal_only == target_date
        ]

        if selected_brand_filter != "Semua Brand":
            user_data = user_data[
                user_data["Brand"] == selected_brand_filter
            ]

        return len(user_data)

    def build_target_rows(
        role_filter,
        id_col_name,
        n_days,
        include_role_col=False,
        include_upline_col=True
    ):
        rows = []

        role_list = role_filter if isinstance(role_filter, list) else [role_filter]

        all_users = df_user[
            df_user["ROLE"].isin(role_list)
        ]["USER"].unique().tolist()

        if selected_brand_filter != "Semua Brand":
            all_users = df_user[
                (df_user["ROLE"].isin(role_list))
                & (df_user["BRAND"] == selected_brand_filter)
            ]["USER"].unique().tolist()

        all_users = [
            u for u in all_users
            if matches_hierarchy_filter(u, selected_hos, selected_bsm, selected_cse)
        ]

        for u in all_users:

            u_info = df_user[df_user["USER"] == u].iloc[0]
            u_name = u_info["REAL_NAME"]
            u_role = u_info["ROLE"]

            u_msisdn, u_bio, _ = get_msisdn_bio_individual([u])

            avg_per_day = round(
                u_msisdn / n_days if n_days > 0 else 0,
                2
            )

            # D-1/D-2/D-3 = submission user itu SENDIRI (sama seperti kolom MSISDN),
            # cuma bedanya di tanggal
            d1_msisdn = get_msisdn_by_date_team([u], d1_date)
            d2_msisdn = get_msisdn_by_date_team([u], d2_date)
            d3_msisdn = get_msisdn_by_date_team([u], d3_date)

            row = {
                id_col_name: u,
                "Nama": u_name,
            }

            if include_upline_col:

                # ==========================================
                # UPLINE = username atasan langsung user ini
                # ==========================================

                upline_username = atasan_map.get(u, "-")

                if not upline_username or str(upline_username).strip().upper() in ["", "NAN", "NONE", "-"]:
                    upline_display = "-"
                else:
                    upline_display = upline_username

                row["Upline"] = upline_display

            row.update({
                "MSISDN": u_msisdn,
                "Avg Submit/Day": avg_per_day,
                d1_label: d1_msisdn,
                d2_label: d2_msisdn,
                d3_label: d3_msisdn,
            })

            if include_role_col:
                row["Role"] = u_role

            rows.append(row)

        return rows

    def render_target_table(rows, id_col, target_threshold):
        if not rows:
            st.info("Tidak ada data.")
            return

        dfr = pd.DataFrame(rows)

        total_msisdn = int(dfr["MSISDN"].sum())
        below_target = int((dfr["Avg Submit/Day"] < target_threshold).sum())

        chip_cols = st.columns(4)

        with chip_cols[0]:
            stat_chip("Jumlah", len(dfr), color="orange")
        with chip_cols[1]:
            stat_chip("MSISDN", f"{total_msisdn:,}", color="blue")
        with chip_cols[2]:
            stat_chip(
                "Rata-rata Submit/Hari",
                f"{round(dfr['Avg Submit/Day'].mean(), 2)}",
                color="green"
            )
        with chip_cols[3]:
            stat_chip(
                f"Belum Achiev (<{target_threshold}/hari)",
                below_target,
                color="amber" if below_target > 0 else "slate"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        dfr = dfr.sort_values("Avg Submit/Day", ascending=False)

        column_config = {
            id_col: st.column_config.TextColumn(width=130),
            "Nama": st.column_config.TextColumn(width=190),
            "MSISDN": st.column_config.NumberColumn(format="%d", width=100),
            "Avg Submit/Day": st.column_config.NumberColumn(format="%.2f", width=130),
            d3_label: st.column_config.NumberColumn(format="%d", width=100),
            d2_label: st.column_config.NumberColumn(format="%d", width=100),
            d1_label: st.column_config.NumberColumn(format="%d", width=100),
        }

        if "Upline" in dfr.columns:
            column_config["Upline"] = st.column_config.TextColumn(width=170)

        if "Role" in dfr.columns:
            column_config["Role"] = st.column_config.TextColumn(width=80)

        def highlight_below_target(row):
            if row["Avg Submit/Day"] < target_threshold:
                return ['background-color: #FEE2E2; color: #991B1B;'] * len(row)
            return [''] * len(row)

        styled = dfr.style.apply(highlight_below_target, axis=1)

        st.dataframe(
            styled,
            use_container_width=True,
            hide_index=True,
            column_config=column_config
        )

    (
        tab_bsm2,
        tab_cse2,
        tab_dse2,
        tab_rge2,
        tab_promotor2,
        tab_np2,
        tab_gse2,
        tab_gemini2
    ) = st.tabs([
        ":material/supervisor_account: BSM",
        ":material/group: CSE/RSE",
        ":material/person: DSE",
        ":material/badge: RGE",
        ":material/campaign: DSE Promotor",
        ":material/store: Promotor",
        ":material/store: GSE",
        ":material/star: GEMPI"
    ])

    with tab_bsm2:
        rows_bsm2 = build_target_rows(
            "BSM", "BSM", n_days,
            include_upline_col=False
        )
        render_target_table(rows_bsm2, "BSM", TARGET_AVG_PER_DAY_MIN)

    with tab_cse2:
        rows_cse2 = build_target_rows(
            ["CSE", "RSE"],
            "CSE/RSE",
            n_days,
            include_role_col=True,
            include_upline_col=False
        )
        render_target_table(rows_cse2, "CSE/RSE", TARGET_AVG_PER_DAY_MIN)

    with tab_dse2:
        rows_dse2 = build_target_rows("DSE", "DSE", n_days)
        render_target_table(rows_dse2, "DSE", TARGET_AVG_PER_DAY_MIN)

    with tab_rge2:
        rows_rge2 = build_target_rows("RGE", "RGE", n_days)
        render_target_table(rows_rge2, "RGE", TARGET_AVG_PER_DAY_MIN)

    with tab_promotor2:
        rows_promotor2 = build_target_rows("PROMOTOR", "DSE Promotor", n_days)
        render_target_table(rows_promotor2, "DSE Promotor", TARGET_AVG_PER_DAY_MIN)

    with tab_np2:
        rows_np2 = build_target_rows("NP", "Promotor", n_days)
        render_target_table(rows_np2, "Promotor", TARGET_AVG_PER_DAY_MIN)

    with tab_gse2:
        rows_gse2 = build_target_rows("GSE", "GSE", n_days)
        render_target_table(rows_gse2, "GSE", TARGET_AVG_PER_DAY_MIN)

    with tab_gemini2:
        rows_gemini2 = build_target_rows("GEMINI", "GEMPI", n_days)
        render_target_table(rows_gemini2, "GEMPI", TARGET_AVG_PER_DAY_MIN)

    st.divider()