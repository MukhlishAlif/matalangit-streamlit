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

PERSONNEL_ROLES = ["DSE", "CSE", "RSE", "RGE", "PROMOTOR", "GSE", "FRONTLINER", "GEMINI"]

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

        padding-top:20px;

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

        height:397px;

        background:linear-gradient(160deg,#A78BFA,#7C3AED);
        color:#FFFFFF;

        z-index:3;

    }

    .podium-card.place-2{

        order:1;

        height:355px;

        background:linear-gradient(160deg,#FF6B95,#EC1C4C);

        color:#FFFFFF;

    }

    .podium-card.place-3{

        order:3;

        height:320px;

        background:linear-gradient(160deg,#FFE066,#F5B400);

        color:#3A2A00;

    }

    .podium-card.place-4{

        order:4;

        height:275px;

        background:linear-gradient(160deg,#CBD5E1,#94A3B8);

        color:#1E293B;

    }

    .podium-crown{

        font-size:45px;

        margin-bottom:10px;

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

        margin:0 auto 6px auto;

    }

    .podium-name{

        font-weight:700;

        font-size:12.5px;

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

    .podium-stand{

        font-size:34px;

        font-weight:900;

        color:rgba(255,255,255,.25);

        line-height:1;

        margin-top:10px;

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
    # Catatan: khusus Quick Count, kita TIDAK peduli status biometrik.
    # Yang dihitung sebagai leaderboard Quick Count = jumlah baris submit.
    # Karena itu load_biometrik() & merge-nya SENGAJA tidak dilakukan di
    # sini lagi (sebelumnya di-load & di-merge padahal tidak pernah dipakai
    # -> kerja sia-sia yang bikin loading lebih berat).
    # ------------------------------------------------

    df = pd.DataFrame(

        outlet_rows,

        columns=[
            "ID",
            "Nama Outlet",
            "ID Outlet",
            "MSISDN",
            "Input By",
            "Tanggal"
        ]

    )

    df["MSISDN"] = df["MSISDN"].fillna("").astype(str).str.strip()

    df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors="coerce")

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

    # ------------------------------------------------
    # Cari MC/Branch/HOS sekali per USER UNIK, bukan per baris.
    # Banyak baris punya "Input By" yang sama (1 personel submit
    # berkali-kali), jadi susur-hierarki per baris itu kerja
    # berulang yang sia-sia dan bikin lemot kalau datanya besar.
    # ------------------------------------------------

    unique_users = df["Input By"].dropna().unique()

    mc_lookup = {u: (ancestor_by_role(u, {"CSE", "RSE"}) or "-") for u in unique_users}
    branch_lookup = {u: (ancestor_by_role(u, {"BSM"}) or "-") for u in unique_users}
    hos_lookup = {u: (ancestor_by_role(u, {"HOS"}) or "-") for u in unique_users}

    df["MC"] = df["Input By"].map(mc_lookup).fillna("-")
    df["Branch"] = df["Input By"].map(branch_lookup).fillna("-")
    df["HOS"] = df["Input By"].map(hos_lookup).fillna("-")

    df["Brand"] = df["Input By"].map(brand_map).fillna("")

    # hanya baris personil yang brand-nya terdeteksi
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
            <div class="kpi-icon" style="background:{color};">{icon}</div>
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

    f1, f2, f3, f4, f5 = st.columns([2, 1.2, 1.5, 1.5, 1])

    with f1:

        periode = st.date_input(
            "📅 Tanggal",
            value=date.today(),
            key="qc_periode"   # key unik, beda dari yang di dashboard.py biar gak bentrok kalau sepanel
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
            "⬇ Export",
            data=to_excel(df),
            file_name="leaderboard_quickcount.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

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
            "👥",
            "Team Total",
            fmt(total_team),
            "-",
            "#3B82F6"
        ),

        (
            "🔥",
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
            "📮",
            "Submit Total",
            fmt(submit_total),
            f"Avg {avg_total:.1f} Submit/Person",
            "#0F766E"
        ),

    ]
    kpi_cols = st.columns(5)

    for col, (icon, label, value, foot, color) in zip(kpi_cols, kpi_defs):

        with col:

            kpi_card(icon, label, value, foot, color)

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # PERSONNEL SUMMARY (Versi Rapi & Manteb)
    # ------------------------------------------------

    st.markdown("### 👥 Performance")

    role_icons = {

        "CSE": "👤",
        "DSE": "👤",
        "GSE": "👤",
        "RGE": "👤"

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
        "CSE/RSE": ["CSE", "RSE"],
        "DSE": ["DSE"],
        "GSE": ["GSE"],
        "RGE": ["RGE"]
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

            position:relative;
            border-radius:20px;
            padding:24px 20px 18px 20px;
            text-align:center;
            color:white;
            box-shadow:0 6px 18px rgba(0,0,0,.14);
            transition:all .2s ease;
            overflow:hidden;

        }

        .kpi-card:hover{

            transform:translateY(-3px);
            box-shadow:0 10px 24px rgba(0,0,0,.20);

        }

        .kpi-card::before{

            content:"";
            position:absolute;
            top:-30px;
            right:-30px;
            width:100px;
            height:100px;
            background:rgba(255,255,255,.08);
            border-radius:50%;

        }

        .kpi-icon-badge{

            width:40px;
            height:40px;
            border-radius:12px;
            background:rgba(255,255,255,.20);
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:18px;
            margin:0 auto 10px auto;
            backdrop-filter:blur(2px);

        }

        .kpi-role{

            font-size:14px;
            font-weight:700;
            letter-spacing:1.2px;
            text-transform:uppercase;
            opacity:.95;
            margin-bottom:14px;

        }

        .kpi-ring-wrap{

            display:flex;
            justify-content:center;
            margin-bottom:10px;
            position:relative;
            z-index:1;

        }

        .kpi-percent{

            font-size:19px;
            font-weight:800;
            fill:white;

        }

        .kpi-footer{

            display:flex;
            align-items:center;
            justify-content:center;
            gap:6px;
            background:rgba(255,255,255,.18);
            border-radius:999px;
            padding:6px 14px;
            font-size:12.5px;
            font-weight:600;
            margin-top:6px;

        }

        </style>
        """,

        unsafe_allow_html=True

    )

    cols = st.columns(4)

    for idx, row in summary_role.iterrows():

        theme = get_theme(
            row["Persentase"]
        )

        icon = role_icons.get(

            row["Role"],

            "👤"

        )

        pct = row["Persentase"]

        radius = 38

        circumference = 2 * 3.14159 * radius

        offset = circumference - (

            pct / 100 * circumference

        )

        ring_svg = f"""
<div class="kpi-ring-wrap">
    <svg width="94" height="94" viewBox="0 0 94 94">
        <circle
            cx="47"
            cy="47"
            r="{radius}"
            stroke="rgba(255,255,255,.25)"
            stroke-width="7"
            fill="none"
        />
        <circle
            cx="47"
            cy="47"
            r="{radius}"
            stroke="white"
            stroke-width="7"
            fill="none"
            stroke-dasharray="{circumference:.1f}"
            stroke-dashoffset="{offset:.1f}"
            stroke-linecap="round"
            transform="rotate(-90 47 47)"
        />
        <text
            x="47"
            y="53"
            text-anchor="middle"
            class="kpi-percent"
        >
            {pct:.0f}%
        </text>
    </svg>
</div>
"""

        with cols[idx]:

            st.markdown(

                f"""
<div class="kpi-card" style="background:{theme['grad']};">

<div class="kpi-icon-badge">

{icon}

</div>

<div class="kpi-role">

{row['Role']}

</div>

{ring_svg}

<div class="kpi-footer">

👤 {row['Input']} / {row['Total']} Personel

</div>

<div style="
    margin-top:10px;
    font-size:12px;
    font-weight:600;
    color:white;
    opacity:.95;
">
📮 {row['Submit']} Submit <br>
Avg Submit : <b>{row['Avg Submit']:.1f}</b> / Personel

</div>
</div>
                """,

                unsafe_allow_html=True

            )

    st.markdown("<br>", unsafe_allow_html=True)
    # ------------------------------------------------
    # ACHIEVEMENT HOS + TOP 3 BRANCH
    # (berbasis JUMLAH SUBMIT, bukan Biometrik)
    # ------------------------------------------------

    col_hos, col_top3 = st.columns([1.6, 1])

    with col_hos:

        with st.container(border=True):

            st.markdown(
                "<div class='mld-card-title'>🏅 Achievement HOS (by Avg Submit / Person)</div>",
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

                hos_df = dff[
                    dff["Input By"].isin(downline)
                ]

                if hos_df.empty:

                    continue

                total_submit = len(hos_df)

                total_person = hos_df["Input By"].nunique()

                avg_submit = (

                    total_submit / total_person

                ) if total_person > 0 else 0

                hos_scores.append(

                    (
                        hos_user,
                        real_name_map.get(
                            hos_user,
                            "-"
                        ),
                        total_submit,
                        avg_submit,
                        atasan_map.get(
                            hos_user,
                            "-"
                        )
                    )

                )
            # Ranking berdasarkan Average Submit / Person
            hos_scores = sorted(

                hos_scores,

                key=lambda x: x[3],   # avg_submit

                reverse=True

            )[:4]
            if hos_scores:

                medal_icon = {1: "🥇", 2: "🥈", 3: "🥉", 4: "🎖️"}
                crown = {1: "👑"}

                podium_cards = []

                for i, (

                    username,
                    real_name,
                    total_submit,
                    avg_submit,
                    atasan

                ) in enumerate(

                    hos_scores,

                    start=1

                ):

                    card_html = (

                        f'<div class="podium-card place-{i}">'

                        f'<div class="podium-crown">{crown.get(i, "")}</div>'

                        f'<div class="podium-medal">{medal_icon.get(i, i)}</div>'

                        f'<div class="podium-name">{username}</div>'

                        f'<div style="font-size:11px;opacity:.82;margin-top:-2px;margin-bottom:6px;">'
                        f'{real_name}'
                        f'</div>'

                        f'<div class="podium-val">{avg_submit:.1f}</div>'

                        f'<div class="podium-caption">Avg Submit / Person</div>'

                        f'<div class="podium-submit-pill">📮 {fmt(total_submit)} Submit</div>'

                        f'<div class="podium-stand">{i}</div>'

                        f'</div>'

                    )

                    podium_cards.append(card_html)

                podium_html = '<div class="podium-wrap">' + "".join(podium_cards) + "</div>"

                st.markdown(podium_html, unsafe_allow_html=True)

            else:

                st.info(

                    "Belum ada data HoS untuk periode/filter ini."

                )
    with col_top3:

        with st.container(border=True):

            st.markdown(
                "<div class='mld-card-title'>🏆 Top 3 Branch (by Avg Submit / Person)</div>",
                unsafe_allow_html=True
            )

            def rank_badge_class(r):

                if r == 1:

                    return "rank-1"

                elif r == 2:

                    return "rank-2"

                elif r == 3:

                    return "rank-3"

                return "rank-other"

            for b in ["IM3", "3ID"]:

                if selected_brand != "Semua Brand" and selected_brand != b:

                    continue

                st.markdown(
                    f"<div class='brand-pill' style='background:{BRAND_COLOR[b]};'>{b}</div>",
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

                for branch_name, branch_df in dff[dff["Brand"] == b].groupby("Branch"):

                    total_submit = len(branch_df)

                    total_person = branch_df["Input By"].nunique()

                    avg_submit = (

                        total_submit / total_person

                    ) if total_person > 0 else 0

                    bsm_name = bsm_name_map.get(

                        str(branch_name).strip().upper(),

                        "-"

                    )

                    branch_scores.append(

                        (

                            branch_name,

                            bsm_name,

                            total_submit,

                            avg_submit

                        )

                    )

                branch_scores = sorted(

                    branch_scores,

                    key=lambda x: x[3],

                    reverse=True

                )[:3]

                if not branch_scores:

                    st.caption("Belum ada data.")

                else:

                    for rank, (

                        branch_name,
                        bsm_name,
                        total_submit,
                        avg_submit

                    ) in enumerate(

                        branch_scores,

                        start=1

                    ):

                        badge_cls = rank_badge_class(rank)

                        medal = {

                            1: "🥇",
                            2: "🥈",
                            3: "🥉"

                        }.get(rank, str(rank))

                        st.markdown(

                            f"""
                            <div class="rank-row">

                            <div class="rank-badge {badge_cls}">
                                {medal}
                            </div>

                            <div class="rank-body">

                            <div
                                style="
                                display:flex;
                                align-items:center;
                                justify-content:space-between;
                                gap:12px;
                                "
                            >

                            <div
                                style="
                                flex:1;
                                min-width:0;
                                "
                            >

                            <div class="rank-branch-name">
                                {branch_name}
                            </div>

                            <div
                                style="
                                font-size:15px;
                                font-weight:700;
                                color:#6B7280;
                                margin-top:2px;
                                "
                            >
                                <b>{bsm_name}</b>
                            </div>

                            </div>

                            <div class="rank-submit-pill">
                                📮 {fmt(total_submit)} Submit
                            </div>

                            <div
                                style="
                                text-align:right;
                                min-width:60px;
                                "
                            >

                            <div class="rank-avg-val">
                                {avg_submit:.1f}
                            </div>

                            <div class="rank-avg-label">
                                 Avg/Person
                            </div>

                            </div>

                            </div>

                            </div>

                            </div>
                            """,

                            unsafe_allow_html=True

                        )

    # ------------------------------------------------
    # 5 LEADERBOARD: CSE/RSE, RGE, DSE, AE, GSE
    # (Total Submit, bukan Total Biometrik)
    # ------------------------------------------------

    # Map username -> nama asli (strip + upper biar aman dari mismatch)
    real_name_map = (
        df_user
        .drop_duplicates(subset="USER")
        .assign(USER=lambda x: x["USER"].astype(str).str.strip().str.upper())
        .set_index("USER")["REAL_NAME"]
        .to_dict()
    )

    lb_cols = st.columns(5)
    lb_defs = [
        ("CSE / RSE", PERSONNEL_GROUPS["CSE/RSE"]),
        ("DSE", PERSONNEL_GROUPS["DSE"]),
        ("PROMOTOR", PERSONNEL_GROUPS["PROMOTOR"]),
        ("RGE", PERSONNEL_GROUPS["RGE"]),
        ("GSE", PERSONNEL_GROUPS["GSE"]),
    ]
    for col, (title, roles) in zip(lb_cols, lb_defs):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"<div class='lb-title'>{title} <span class='muted-pill'>(Total Submit)</span></div>",
                    unsafe_allow_html=True,
                )
                grp = (
                    dff[dff["Role"].isin(roles)]
                    .groupby(["Input By", "Branch"])
                    .size()
                    .reset_index(name="Submit")
                    .sort_values("Submit", ascending=False)
                )

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
                bottom3 = grp.tail(3).sort_values("Submit")

                st.markdown(
                    "<div class='lb-sub'>Top 3</div>",
                    unsafe_allow_html=True,
                )
                if top3.empty:
                    st.caption("-")
                else:
                    for i, row in enumerate(top3.itertuples(), start=1):
                        lb_row(i, row._4, row.Branch, row.Submit)

                st.markdown(
                    "<div class='lb-sub' style='margin-top:8px;'>Bottom 3</div>",
                    unsafe_allow_html=True,
                )
                if bottom3.empty:
                    st.caption("-")
                else:
                    for i, row in enumerate(bottom3.itertuples(), start=1):
                        lb_row(i, row._4, row.Branch, row.Submit)
    st.markdown("<br>", unsafe_allow_html=True)
    # ------------------------------------------------
    # BRANCH PERFORMANCE TABLE
    # (metrik utama = jumlah submit MSISDN)
    # ------------------------------------------------

    with st.container(border=True):

        st.markdown("<div class='mld-card-title'>📋 Branch Performance</div>", unsafe_allow_html=True)

        t1, t2 = st.columns([1, 3])

        with t1:

            table_group = st.selectbox(
                "Personnel (tabel)",
                list(PERSONNEL_GROUPS.keys()),
                key="qc_table_personnel"
            )

        with t2:

            search = st.text_input("🔎 Search Branch / MC", key="qc_search")

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

                    if selected_group != "Semua Personnel":

                        mc_all = mc_all[
                            mc_all["Role"].isin(
                                PERSONNEL_GROUPS[selected_group]
                            )
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