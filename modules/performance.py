# ==========================================================
# IMPORT
# ==========================================================

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import date, timedelta

from database import (
    tampil_data_by_date,
    load_user_hierarchy,
    load_leave_map,
    get_leave_flag_range
)

# ==========================================================
# CONSTANTS
# ==========================================================

PERSONNEL_ROLES = ["BSM","DSE", "CSE", "RSE", "RGE", "PROMOTOR", "GSE", "GEMINI","NP"]

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

    .kpi-value-sub{
        font-size:12px;
        font-weight:700;
        color:#059669;
        background:#DCFCE7;
        padding:2px 8px;
        border-radius:999px;
        margin-left:6px;
        vertical-align:middle;
    }

    .mld-card-title{
        font-weight:800;
        font-size:14px;
        color:#374151;
        margin-bottom:12px;
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

def get_active_descendants(root, children_map, active_users_set, max_depth=20):
    downline = get_descendants(root, children_map, max_depth=max_depth)
    return [u for u in downline if u in active_users_set]


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


LEAVE_CATEGORY_LABEL = {
    "sick": "Sakit",
    "leave": "Izin",
}


def categorize_leave_type(leave_type):
    key = str(leave_type or "").strip().lower()
    return LEAVE_CATEGORY_LABEL.get(key, "Lainnya")


def get_leave_breakdown(leave_map, user_list, filter_start, filter_end):
    counts = {}

    for u in user_list:

        key = str(u).strip().upper()
        entries = leave_map.get(key, [])

        matched = next(
            (
                e for e in entries
                if e["start"] <= filter_end and e["end"] >= filter_start
            ),
            None
        )

        if matched:
            cat = categorize_leave_type(matched["leave_type"])
            counts[cat] = counts.get(cat, 0) + 1

    return counts


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
    # Hierarki user (tidak tergantung tanggal filter)
    # ------------------------------------------------
    (
        df_user,
        role_map,
        atasan_map,
        brand_map,
        children_map
    ) = load_user_hierarchy()

    active_users_set = set(
        df_user[df_user["FLAG_ACTIVE"] == True]["USER"]
        .astype(str)
        .str.strip()
    )

    leave_map = load_leave_map()

    # ------------------------------------------------
    # USER YANG LOGIN = HOS PEMILIK HALAMAN INI.
    # Seluruh halaman di-scope HANYA ke HoS ini + bawahan-
    # bawahannya (downline). Tidak ada lagi filter/pemilihan
    # HoS lain -- halaman ini memang khusus 1 HoS.
    # ------------------------------------------------

    current_user = str(st.session_state.get("outlet_user", "-")).strip()
    current_role = role_map.get(current_user, "-")

    hos_root = current_user

    # Downline AKTIF (dipakai untuk semua perhitungan performance)
    hos_downline_active = get_active_descendants(hos_root, children_map, active_users_set)

    # Downline SEMUA (termasuk non-aktif, dipakai untuk hitung Vacant)
    hos_downline_all = get_descendants(hos_root, children_map)

    # ==========================================
    # BRAND DIKUNCI KE BRAND HOS INI SENDIRI.
    # HoS IM3 tidak boleh melihat/memilih data 3ID, dan
    # sebaliknya -- brand-nya TIDAK bisa dipilih bebas.
    # ==========================================

    hos_brand = brand_map.get(hos_root, "")

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

    # Load logo jadi base64
    logo_b64 = get_base64_image("icon.png")

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
        </style>

        <div class="mld-header">
            <div class="mld-header-inner">
                <div>
                    <div class="mld-title-row">
                        <img src="data:image/jpg;base64,{logo_b64}" class="mld-logo-img" />
                        <span class="mld-title-text">Performance Team</span>
                    </div>
                    <div class="mld-sub">
                        Performance Team {display_name} ({hos_root}) berdasarkan jumlah submit MSISDN
                    </div>
                    <div class="mld-pill" style="margin-top:10px;">HoS Area : {display_name}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------
    # FILTER BAR (tanpa filter HoS -- sudah fix ke HoS login)
    # ------------------------------------------------

    f1, f2, f3, f4, f5 = st.columns([2, 1.2, 1.5, 1, 1])

    with f1:

        periode = st.date_input(

            ":material/calendar_month: Filter Tanggal",

            value=(date.today(), date.today()),

            key="mld_periode"

        )

        if isinstance(periode, tuple):
            if len(periode) == 2:
                start_date, end_date = periode
            else:
                start_date = end_date = periode[0]
        else:
            start_date = end_date = periode

    df, _, _, _, _, _ = load_all_data(start_date, end_date)

    with f2:

        if hos_brand in ("IM3", "3ID"):

            selected_brand = hos_brand

            st.markdown(
                f"<div style='padding-top:6px;'><span class='mld-pill' "
                f"style='background:rgba(0,0,0,.06);color:#374151;'>"
                f"Brand: {hos_brand}</span></div>",
                unsafe_allow_html=True
            )

        else:

            selected_brand = st.selectbox(
                "Brand",
                ["Semua Brand", "IM3", "3ID"],
                key="qc_brand"
            )

    with f3:

        selected_group = st.selectbox(
            "Personnel",
            ["Semua Personnel"] + list(PERSONNEL_GROUPS.keys()),
            key="qc_personnel"
        )

    with f4:

        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        st.download_button(
            ":material/download: Export",
            data=to_excel(df[df["Input By"].isin(hos_downline_active)]),
            file_name="performance_team_hos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with f5:

        st.markdown("<div style='height:23px'></div>", unsafe_allow_html=True)

        if st.button("Refresh", use_container_width=True, key="mld_refresh"):

            st.cache_data.clear()

            st.rerun()

    # ------------------------------------------------
    # APPLY FILTER
    # ------------------------------------------------

    dff = df.copy()

    dff["Tanggal"] = pd.to_datetime(
        dff["Tanggal"]
    )

    if isinstance(periode, tuple):

        if len(periode) == 2:

            start_date, end_date = periode

        else:

            start_date = end_date = periode[0]

    else:

        start_date = end_date = periode

    n_days = max((end_date - start_date).days + 1, 1)

    dff = dff[

        (dff["Tanggal"].dt.date >= start_date)

        &

        (dff["Tanggal"].dt.date <= end_date)

    ]

    if selected_brand != "Semua Brand":

        dff = dff[

            dff["Brand"] == selected_brand

        ]

    # ==========================================
    # SCOPE KE HOS INI SAJA -- hanya submission dari
    # bawahan (downline) HoS yang sedang login.
    # ==========================================

    dff = dff[
        dff["Input By"]
        .astype(str)
        .str.strip()
        .isin(hos_downline_active)
    ]

    if selected_group != "Semua Personnel":

        dff = dff[

            dff["Role"].isin(

                PERSONNEL_GROUPS[
                    selected_group
                ]

            )

        ]

    # (dff sudah di-scope ke user aktif lewat hos_downline_active)

    st.divider()

    # =====================================================
    # PERSONNEL (SCOPE KE DOWNLINE HOS INI)
    # =====================================================

    all_personnel_raw = df_user[
        (df_user["ROLE"].isin(PERSONNEL_ROLES))
        &
        (df_user["USER"].astype(str).str.strip().isin(hos_downline_all))
    ]

    if selected_brand != "Semua Brand":
        all_personnel_raw = all_personnel_raw[
            all_personnel_raw["BRAND"] == selected_brand
        ]

    if selected_group != "Semua Personnel":
        all_personnel_raw = all_personnel_raw[
            all_personnel_raw["ROLE"].isin(PERSONNEL_GROUPS[selected_group])
        ]

    all_personnel = all_personnel_raw[
        all_personnel_raw["FLAG_ACTIVE"] == True
    ]

    active_personnel = all_personnel[
        all_personnel["STATUS"].astype(str).str.upper() == "AKTIF"
    ]

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
    # METRIK UTAMA = JUMLAH SUBMIT
    # ==========================================

    submit_im3 = len(dff[dff["Brand"] == "IM3"])
    submit_3id = len(dff[dff["Brand"] == "3ID"])
    submit_total = len(dff)

    bio_im3 = int(dff.loc[dff["Brand"] == "IM3", "Biometrik"].sum())
    bio_3id = int(dff.loc[dff["Brand"] == "3ID", "Biometrik"].sum())
    bio_total = int(dff["Biometrik"].sum())

    bio_pct_im3 = (bio_im3 / submit_im3 * 100) if submit_im3 else 0
    bio_pct_3id = (bio_3id / submit_3id * 100) if submit_3id else 0
    bio_pct_total = (bio_total / submit_total * 100) if submit_total else 0

    total_vacant = all_personnel_raw[
        all_personnel_raw["FLAG_ACTIVE"] == False
    ]["USER"].nunique()

    # ==========================================
    # TOTAL IZIN = Izin + Sakit (approved, overlap filter tanggal)
    # ==========================================

    leave_counts_total = get_leave_breakdown(
        leave_map,
        all_personnel["USER"].astype(str).str.strip().unique().tolist(),
        start_date,
        end_date
    )

    total_izin = (
        leave_counts_total.get("Izin", 0)
        + leave_counts_total.get("Sakit", 0)
    )

    team_im3 = all_personnel[
        all_personnel["BRAND"] == "IM3"
    ]["USER"].nunique()

    team_3id = all_personnel[
        all_personnel["BRAND"] == "3ID"
    ]["USER"].nunique()

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

    ]

    # Card Submit IM3 HANYA muncul kalau HoS ini bukan khusus 3ID
    if hos_brand != "3ID":
        kpi_defs.append((
            f'<img src="data:image/png;base64,{im3_icon}" style="width:35px;height:35px;object-fit:contain;vertical-align:-4px;" />',
            "Submit IM3",
            f'{fmt(submit_im3)} <span class="kpi-value-sub">{bio_pct_im3:.0f}% Bio</span>',
            f"Avg {avg_im3:.1f} Submit/Person",
            "#F59E0B"
        ))

    # Card Submit 3ID HANYA muncul kalau HoS ini bukan khusus IM3
    if hos_brand != "IM3":
        kpi_defs.append((
            f'<img src="data:image/png;base64,{tid_icon}" style="width:28px;height:28px;object-fit:contain;vertical-align:-4px;" />',
            "Submit 3ID",
            f'{fmt(submit_3id)} <span class="kpi-value-sub">{bio_pct_3id:.0f}% Bio</span>',
            f"Avg {avg_3id:.1f} Submit/Person",
            "#EC1C4C"
        ))

    kpi_defs.append((
        "lock",
        "Submit Total",
        f'{fmt(submit_total)} <span class="kpi-value-sub">{bio_pct_total:.0f}% Bio</span>',
        f"Avg {avg_total:.1f} Submit/Person",
        "#0F766E"
    ))

    kpi_cols = st.columns(len(kpi_defs))

    for col, (icon, label, value, foot, color) in zip(kpi_cols, kpi_defs):

        with col:

            kpi_card(icon, label, value, foot, color)

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # PERSONNEL SUMMARY - SUBMIT (scope downline HoS ini)
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

        role_filter_base = (
            (df_user["ROLE"].isin(roles))
            & (df_user["FLAG_ACTIVE"] == True)
            & (df_user["STATUS"].astype(str).str.upper() == "AKTIF")
            & (df_user["USER"].astype(str).str.strip().isin(hos_downline_all))
            & (
                (selected_brand == "Semua Brand")
                | (df_user["BRAND"] == selected_brand)
            )
        )

        role_users = df_user[role_filter_base]["USER"].unique().tolist()
        total_role = len(role_users)

        role_data = dff[

            dff["Role"].isin(roles)

        ]

        input_role = role_data["Input By"].nunique()

        submit_role = len(role_data)

        bio_role = int(role_data["Biometrik"].sum())

        percent = (

            input_role / total_role * 100

        ) if total_role > 0 else 0

        avg_submit = (

            submit_role / input_role

        ) if input_role > 0 else 0

        bio_pct_role = (

            bio_role / submit_role * 100

        ) if submit_role > 0 else 0

        leave_counts = get_leave_breakdown(
            leave_map, role_users, start_date, end_date
        )

        jumlah_cuti = leave_counts.get("Izin", 0)
        jumlah_sakit = leave_counts.get("Sakit", 0)
        jumlah_izin = jumlah_cuti + jumlah_sakit

        pct_cuti = (jumlah_cuti / total_role * 100) if total_role > 0 else 0
        pct_sakit = (jumlah_sakit / total_role * 100) if total_role > 0 else 0

        role_summary.append({

            "Role": group_label,

            "Total": total_role,

            "Input": input_role,

            "Submit": submit_role,

            "Avg Submit": avg_submit,

            "Bio Pct": bio_pct_role,

            "Persentase": percent,

            "PersentaseCuti": pct_cuti,
            "PersentaseSakit": pct_sakit,
            "JumlahIzin": jumlah_izin,

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

    CARDS_PER_ROW = 4

    for row_start in range(0, len(summary_role), CARDS_PER_ROW):

        chunk = summary_role.iloc[
            row_start:row_start + CARDS_PER_ROW
        ]

        cols = st.columns(CARDS_PER_ROW)

        for col_idx, (_, row) in enumerate(chunk.iterrows()):

            theme = get_theme(row["Persentase"])
            icon = role_icons.get(row["Role"], mat_icon("person", size=13, valign=-2))

            pct_submit = row["Persentase"]
            pct_cuti = row["PersentaseCuti"]
            pct_sakit = row["PersentaseSakit"]

            radius = 30
            circumference = 2 * 3.14159 * radius

            def _ring_segment(offset_pct, length_pct, color):
                length = (length_pct / 100) * circumference
                gap = circumference - length
                dashoffset = -(offset_pct / 100) * circumference
                return (
                    f'<circle cx="38" cy="38" r="{radius}" stroke="{color}" stroke-width="6" fill="none" '
                    f'stroke-dasharray="{length:.2f} {gap:.2f}" stroke-dashoffset="{dashoffset:.2f}" '
                    f'stroke-linecap="butt" transform="rotate(-90 38 38)" />'
                )

            segments_html = ""
            cum = 0.0

            if pct_submit > 0:
                segments_html += _ring_segment(cum, pct_submit, "#ffffff")
                cum += pct_submit

            if pct_cuti > 0:
                segments_html += _ring_segment(cum, pct_cuti, "#60A5FA")
                cum += pct_cuti

            if pct_sakit > 0:
                segments_html += _ring_segment(cum, pct_sakit, "#FBBF24")
                cum += pct_sakit

            ring_svg = (
                '<div class="kpi-ring-wrap">'
                '<svg width="76" height="76" viewBox="0 0 76 76">'
                f'<circle cx="38" cy="38" r="{radius}" stroke="rgba(255,255,255,.28)" stroke-width="6" fill="none" />'
                f'{segments_html}'
                f'<text x="38" y="43" text-anchor="middle" class="kpi-percent">{pct_submit:.0f}%</text>'
                '</svg>'
                '</div>'
            )

            legend_parts = [f'{pct_submit:.0f}% Submit &middot; Bio {row["Bio Pct"]:.0f}%']

            if pct_cuti > 0:
                legend_parts.append(f'{pct_cuti:.0f}% Izin')

            if pct_sakit > 0:
                legend_parts.append(f'{pct_sakit:.0f}% Sakit')

            legend_html = ' &middot; '.join(legend_parts)

            jumlah_izin = row.get("JumlahIzin", 0)
            izin_suffix = f" - {jumlah_izin} izin" if jumlah_izin > 0 else ""

            card_html = (
                f'<div class="kpi-card" style="--accent-grad:{theme["grad"]};">'
                f'<div class="kpi-icon-badge">{icon}</div>'
                f'<div class="kpi-role">{row["Role"]}</div>'
                f'{ring_svg}'
                f'<div class="kpi-footer">{row["Input"]} / {row["Total"]} personel{izin_suffix}</div>'
                f'<div class="kpi-avg">{legend_html}</div>'
                '</div>'
            )

            with cols[col_idx]:

                st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ------------------------------------------------
    # Helper kompak: 1 baris ranking branch (avg + total submit)
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
    # Helper: render Top3 & Bottom3 BRANCH (BSM) SAMPINGAN
    # dalam 1 card. Satu HoS cuma pegang 1 brand (IM3 saja
    # atau 3ID saja) jadi tidak perlu split IM3/3ID lagi --
    # brand-nya ditentukan otomatis dari data downline (dff).
    # ------------------------------------------------

    def render_branch_top_bottom():

        brand_counts = dff["Brand"].value_counts()
        hos_brand_label = brand_counts.idxmax() if not brand_counts.empty else "-"

        st.markdown(
            f"<div class='mld-card-title'>{mat_icon('emoji_events', size=16, color='#F59E0B', valign=-3)} "
            f"Branch (BSM) Performance "
            f"<span style='font-weight:600;font-size:11px;color:#9CA3AF;'>· {hos_brand_label} · by Avg Submit/Person</span></div>",
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

        for branch_name, branch_df in dff.groupby("Branch"):

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

        col_top, col_bottom = st.columns(2)

        with col_top:

            st.markdown("<div class='lb-sub' style='color:#059669;'>Top 3</div>", unsafe_allow_html=True)

            if not top3:
                st.caption("Belum ada data.")
            else:
                for i, (branch_name, bsm_name, total_submit, avg_submit) in enumerate(top3, start=1):
                    lb_branch_row(medals.get(i, str(i)), branch_name, bsm_name, avg_submit, total_submit)

        with col_bottom:

            st.markdown("<div class='lb-sub' style='color:#dc2626;'>Bottom 3</div>", unsafe_allow_html=True)

            if not bottom3:
                st.caption("Belum ada data.")
            else:
                for i, (branch_name, bsm_name, total_submit, avg_submit) in enumerate(bottom3, start=0):
                    lb_branch_row(mat_icon("trending_down", size=16, color="#EF4444"), branch_name, bsm_name, avg_submit, total_submit)

    # ------------------------------------------------
    # RINGKASAN PERFORMANCE HOS INI (achievement vs target
    # + top 5 personel terbaik) + BRANCH (BSM) TOP/BOTTOM
    # ------------------------------------------------

    col_summary, col_branch = st.columns([1.5, 1.3])

    with col_summary:

        with st.container(border=True):

            st.markdown(
                f"<div class='mld-card-title'>{mat_icon('insights', size=18, color='#7C3AED', valign=-4)} Ringkasan Performance {display_name}</div>",
                unsafe_allow_html=True
            )

            n_branch = dff["Branch"].nunique()

            # ==========================================
            # TARGET PER USER BEDA-BEDA:
            # NP / PROMOTOR = 10 submit/hari, role lain = 5 submit/hari.
            # Dihitung dari SEMUA personel aktif di bawah HoS ini
            # (bukan cuma yang submit), lalu dijumlah -> target team.
            # ==========================================

            def target_per_user(role):
                return 10 if role in ("NP", "PROMOTOR") else TARGET_PER_DAY

            all_personnel_roles = all_personnel[["USER", "ROLE"]].drop_duplicates(subset="USER").copy()
            all_personnel_roles["Target"] = all_personnel_roles["ROLE"].apply(target_per_user) * n_days

            target_submit = int(all_personnel_roles["Target"].sum())
            achievement_pct = (submit_total / target_submit * 100) if target_submit else 0

            bar_color = (
                "#059669" if achievement_pct >= 100
                else "#D97706" if achievement_pct >= 70
                else "#DC2626"
            )

            st.markdown(
                f"""
                <div class="branch-card-header">
                    <div>
                        <div class="branch-card-name">{display_name}</div>
                        <div class="branch-card-sub">{hos_root} · {n_branch} Branch</div>
                    </div>
                    <div class="branch-stat-row">
                        <div class="branch-stat-chip">
                            <div class="branch-stat-val">{fmt(active_team)}</div>
                            <div class="branch-stat-label">Personel Aktif</div>
                        </div>
                        <div class="branch-stat-chip">
                            <div class="branch-stat-val">{avg_total:.1f}</div>
                            <div class="branch-stat-label">Avg / Person</div>
                        </div>
                        <div class="branch-stat-chip">
                            <div class="branch-stat-val">{achievement_badge(achievement_pct)}</div>
                            <div class="branch-stat-label">Achievement</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"""
                <div class="progress-wrap">
                    <div class="progress-label">
                        <span>Submit Semua team vs Target ({fmt(target_submit)})</span>
                        <span>{fmt(submit_total)} / {fmt(target_submit)}</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill" style="width:{min(achievement_pct, 100):.0f}%;background:{bar_color};"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


    with col_branch:

        with st.container(border=True):

            render_branch_top_bottom()

    # ------------------------------------------------
    # 6 LEADERBOARD: BSM, CSE/RSE, DSE, RGE, PROMOTOR, NP
    # (SCOPE ke downline HoS ini saja)
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

    lb_defs = [
        ("BSM", PERSONNEL_GROUPS["BSM"]),
        ("CSE / RSE", PERSONNEL_GROUPS["CSE/RSE"]),
        ("DSE", PERSONNEL_GROUPS["DSE"]),
        ("RGE", PERSONNEL_GROUPS["RGE"]),
        ("DSE PROMOTOR", PERSONNEL_GROUPS["PROMOTOR"]),
        ("Promotor", PERSONNEL_GROUPS["NP"]),
    ]

    LB_PER_ROW = 3

    for row_start in range(0, len(lb_defs), LB_PER_ROW):

        chunk_defs = lb_defs[row_start:row_start + LB_PER_ROW]

        lb_cols = st.columns(LB_PER_ROW)

        for col, (title, roles) in zip(lb_cols, chunk_defs):
            with col:
                with st.container(border=True):

                    # ==========================================
                    # BASE: SEMUA USER ROLE INI, DI BAWAH HOS INI
                    # ==========================================

                    base_users = df_user[
                        (df_user["ROLE"].isin(roles))
                        & (df_user["FLAG_ACTIVE"] == True)
                        & (df_user["USER"].astype(str).str.strip().isin(hos_downline_active))
                    ][["USER", "BRANCH"]].drop_duplicates(subset="USER").rename(
                        columns={"USER": "Input By", "BRANCH": "Branch"}
                    )

                    if selected_brand != "Semua Brand":
                        base_users = base_users[
                            base_users["Input By"].map(brand_map) == selected_brand
                        ]

                    submit_count = (
                        dff[dff["Role"].isin(roles)]
                        .groupby("Input By")
                        .size()
                        .reset_index(name="Submit")
                    )

                    grp = base_users.merge(
                        submit_count,
                        on="Input By",
                        how="left"
                    )

                    grp["Submit"] = grp["Submit"].fillna(0).astype(int)

                    grp = grp.sort_values("Submit", ascending=False)

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

    DATE_COL = "Tanggal"

    dff[DATE_COL] = pd.to_datetime(dff[DATE_COL], errors="coerce").dt.date

    # ------------------------------------------------
    # SECTION 1: TEAM PERFORMANCE
    # (2 TAB: BSM, CSE/RSE -- tab HOS dihapus karena
    # halaman ini sudah pasti scope 1 HoS)
    # ------------------------------------------------
   
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

                .mld-stat-chip.mld-stat-slate {
                    background: #F8FAFC;
                    border: 1px solid #E2E8F0;
                }
                .mld-stat-chip.mld-stat-slate .mld-stat-label { color: #64748B; }
                .mld-stat-chip.mld-stat-slate .mld-stat-value { color: #0F172A; }

                .mld-stat-chip.mld-stat-blue {
                    background: #EFF6FF;
                    border: 1px solid #BFDBFE;
                }
                .mld-stat-chip.mld-stat-blue .mld-stat-label { color: #1D4ED8; }
                .mld-stat-chip.mld-stat-blue .mld-stat-value { color: #1D4ED8; }

                .mld-stat-chip.mld-stat-purple {
                    background: #F5F3FF;
                    border: 1px solid #DDD6FE;
                }
                .mld-stat-chip.mld-stat-purple .mld-stat-label { color: #6D28D9; }
                .mld-stat-chip.mld-stat-purple .mld-stat-value { color: #6D28D9; }

                .mld-stat-chip.mld-stat-green {
                    background: #ECFDF5;
                    border: 1px solid #A7F3D0;
                }
                .mld-stat-chip.mld-stat-green .mld-stat-label { color: #047857; }
                .mld-stat-chip.mld-stat-green .mld-stat-value { color: #047857; }

                .mld-stat-chip.mld-stat-amber {
                    background: #FFFBEB;
                    border: 1px solid #FDE68A;
                }
                .mld-stat-chip.mld-stat-amber .mld-stat-label { color: #B45309; }
                .mld-stat-chip.mld-stat-amber .mld-stat-value { color: #B45309; }

                .mld-stat-chip.mld-stat-danger {
                    background: #FEF2F2;
                    border: 1px solid #FECACA;
                }
                .mld-stat-chip.mld-stat-danger .mld-stat-label { color: #B91C1C; }
                .mld-stat-chip.mld-stat-danger .mld-stat-value { color: #DC2626; }

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

    def stat_chip(label, value, color="slate"):

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
            (df_user["ROLE"].isin(role_list))
            & (df_user["FLAG_ACTIVE"] == True)
            & (df_user["USER"].astype(str).str.strip().isin(hos_downline_active))
        ]["USER"].unique().tolist()

        if selected_brand_filter != "Semua Brand":

            all_users = df_user[
                (df_user["ROLE"].isin(role_list))
                & (df_user["FLAG_ACTIVE"] == True)
                & (df_user["USER"].astype(str).str.strip().isin(hos_downline_active))
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
                else get_active_descendants(
                    u,
                    children_map,
                    active_users_set
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



    # ------------------------------------------------
    # SECTION 2: INDIVIDUAL PERFORMANCE
    # (8 TAB, SCOPE ke downline HoS ini saja.
    # Filter HOS dihapus karena sudah pasti HoS ini.)
    # ------------------------------------------------

    TARGET_AVG_PER_DAY_MIN = 5
    TARGET_AVG_PER_DAY_MIN_NP = 10

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

    def matches_hierarchy_filter(u, selected_bsm, selected_cse):
        ancestors = get_ancestors(u)

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

        f_brand, f_bsm, f_cse = st.columns(3)

        with f_brand:
            brand_options = ["Semua Brand", "IM3", "3ID"]
            selected_brand_filter = st.selectbox(
                ":material/sim_card: Filter Brand",
                brand_options,
                key="ip_filter_brand"
            )

        bsm_candidates = df_user[
            (df_user["ROLE"] == "BSM")
            & (df_user["FLAG_ACTIVE"] == True)
            & (df_user["USER"].isin(hos_downline_active))
        ]

        if selected_brand_filter != "Semua Brand":
            bsm_candidates = bsm_candidates[
                bsm_candidates["BRAND"] == selected_brand_filter
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
            (df_user["ROLE"].isin(["CSE", "RSE"]))
            & (df_user["FLAG_ACTIVE"] == True)
            & (df_user["USER"].isin(hos_downline_active))
        ]

        if selected_brand_filter != "Semua Brand":
            cse_candidates = cse_candidates[
                cse_candidates["BRAND"] == selected_brand_filter
            ]

        if selected_bsm != "Semua BSM":
            cse_candidates = cse_candidates[
                cse_candidates["ATASAN"] == selected_bsm
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
        include_upline_col=True,
        show_leave_flag=True
    ):
        rows = []

        role_list = role_filter if isinstance(role_filter, list) else [role_filter]

        all_users = df_user[
            (df_user["ROLE"].isin(role_list))
            & (df_user["FLAG_ACTIVE"] == True)
            & (df_user["USER"].isin(hos_downline_active))
        ]["USER"].unique().tolist()

        if selected_brand_filter != "Semua Brand":
            all_users = df_user[
                (df_user["ROLE"].isin(role_list))
                & (df_user["FLAG_ACTIVE"] == True)
                & (df_user["USER"].isin(hos_downline_active))
                & (df_user["BRAND"] == selected_brand_filter)
            ]["USER"].unique().tolist()

        all_users = [
            u for u in all_users
            if matches_hierarchy_filter(u, selected_bsm, selected_cse)
        ]

        for u in all_users:

            u_info = df_user[df_user["USER"] == u].iloc[0]
            u_name = u_info["REAL_NAME"]
            u_role = u_info["ROLE"]

            u_msisdn, u_bio, u_persen_bio = get_msisdn_bio_individual([u])

            avg_per_day = round(
                u_msisdn / n_days if n_days > 0 else 0,
                2
            )

            d1_msisdn = get_msisdn_by_date_team([u], d1_date)
            d2_msisdn = get_msisdn_by_date_team([u], d2_date)
            d3_msisdn = get_msisdn_by_date_team([u], d3_date)

            row = {
                id_col_name: u,
                "Nama": u_name,
            }

            if include_upline_col:

                upline_username = atasan_map.get(u, "-")

                if not upline_username or str(upline_username).strip().upper() in ["", "NAN", "NONE", "-"]:
                    upline_display = "-"
                else:
                    upline_display = upline_username

                row["Upline"] = upline_display

            row.update({
                "MSISDN": u_msisdn,
                "Avg Submit/Day": avg_per_day,
                "Biometrik": u_bio,
                "% Biometrik": round(u_persen_bio, 1),
                d1_label: d1_msisdn,
                d2_label: d2_msisdn,
                d3_label: d3_msisdn,
            })

            if show_leave_flag:
                row["Flag Izin"] = get_leave_flag_range(leave_map, u, start_date, end_date)

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
        total_bio = int(dfr["Biometrik"].sum())
        avg_bio_pct = round(dfr["% Biometrik"].mean(), 1) if len(dfr) > 0 else 0

        has_leave_flag = "Flag Izin" in dfr.columns

        if has_leave_flag:
            on_leave_mask = dfr["Flag Izin"].astype(str).str.strip().ne("")
            jumlah_cuti_izin = int(on_leave_mask.sum())
        else:
            on_leave_mask = pd.Series(False, index=dfr.index)
            jumlah_cuti_izin = 0

        below_target = int(
            (
                (dfr["Avg Submit/Day"] < target_threshold)
                & (~on_leave_mask)
            ).sum()
        )

        n_chip = 7 if has_leave_flag else 6

        chip_cols = st.columns(n_chip)

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
        with chip_cols[4]:
            stat_chip("Total Biometrik", f"{total_bio:,}", color="purple")
        with chip_cols[5]:
            stat_chip("Rata-rata % Biometrik", f"{avg_bio_pct:.1f}%", color="danger")

        if has_leave_flag:
            with chip_cols[6]:
                stat_chip(
                    "Cuti/Izin",
                    jumlah_cuti_izin,
                    color="purple" if jumlah_cuti_izin > 0 else "slate"
                )

        st.markdown("<br>", unsafe_allow_html=True)

        dfr = dfr.sort_values("Avg Submit/Day", ascending=False)

        column_config = {
            id_col: st.column_config.TextColumn(width=130),
            "Nama": st.column_config.TextColumn(width=190),
            "MSISDN": st.column_config.NumberColumn(format="%d", width=100),
            "Avg Submit/Day": st.column_config.NumberColumn(format="%.2f", width=130),
            "Biometrik": st.column_config.NumberColumn(format="%d", width=100),
            "% Biometrik": st.column_config.NumberColumn(format="%.1f%%", width=110),
            d3_label: st.column_config.NumberColumn(format="%d", width=100),
            d2_label: st.column_config.NumberColumn(format="%d", width=100),
            d1_label: st.column_config.NumberColumn(format="%d", width=100),
        }

        if "Flag Izin" in dfr.columns:
            column_config["Flag Izin"] = st.column_config.TextColumn(width=220)

        if "Upline" in dfr.columns:
            column_config["Upline"] = st.column_config.TextColumn(width=170)

        if "Role" in dfr.columns:
            column_config["Role"] = st.column_config.TextColumn(width=80)

        def highlight_below_target(row):
            on_leave = str(row.get("Flag Izin", "")).strip() != ""
            if on_leave:
                return [''] * len(row)
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
            include_upline_col=False,
            show_leave_flag=False
        )
        render_target_table(rows_bsm2, "BSM", TARGET_AVG_PER_DAY_MIN)

    with tab_cse2:
        rows_cse2 = build_target_rows(
            ["CSE", "RSE"],
            "CSE/RSE",
            n_days,
            include_role_col=False,
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
        render_target_table(rows_np2, "Promotor", TARGET_AVG_PER_DAY_MIN_NP)

    with tab_gse2:
        rows_gse2 = build_target_rows("GSE", "GSE", n_days)
        render_target_table(rows_gse2, "GSE", TARGET_AVG_PER_DAY_MIN)

    with tab_gemini2:
        rows_gemini2 = build_target_rows("GEMINI", "GEMPI", n_days)
        render_target_table(rows_gemini2, "GEMPI", TARGET_AVG_PER_DAY_MIN)

    st.divider()