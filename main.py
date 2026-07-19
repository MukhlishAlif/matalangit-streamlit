# =====================================
# IMPORT
# =====================================

import streamlit as st
import pandas as pd
import urllib.parse
from datetime import date

from modules.data_outlet import show as data_outlet
from modules.dashboard_cse import show as dashboard_cse
from modules.dashboard_dse import show as dashboard_dse
from modules.dashboard_fl import show as dashboard_fl
from modules.dashboard_ae import show as dashboard_ae
from modules.dashboard_rge import show as dashboard_rge
from modules.dashboard_pm import show as dashboard_pm
from modules.dashboard_gse import show as dashboard_gse
from modules.main_dashboard import show as main_dashboard
from modules.quickcount_dashboard import show as quickcount_dashboard
from modules.dashboard_bsm import show as dashboard_bsm
from modules.dashboard_np import show as dashboard_np

from auth import login_page, sidebar

from database import (
    tampil_user,
    tampil_data_by_date,
    get_downline
)


# =====================================
# CONFIG
# =====================================

st.set_page_config(
    page_title="MataLangit",
    page_icon="icon.png",
    layout="wide"
)

# =====================================
# CUSTOM CSS
# =====================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 0rem;
    }

    /* ============================= */
    /* HERO / LOGIN PAGE             */
    /* ============================= */

    .hero-container {
        padding-top: 40px;
        padding-bottom: 20px;
        text-align: center;
        position: relative;
    }

    .hero-title {
        font-size: 58px;
        font-weight: 800;
        margin-bottom: 10px;
        background: linear-gradient(
            90deg,
            #F5B400,
            #D4537E,
            #993556
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        font-size: 20px;
        color: #6B7280;
        margin-bottom: 30px;
        font-weight: 500;
    }

    .hero-card {

        background: linear-gradient(
            135deg,
            rgba(245,180,0,0.08),
            rgba(212,83,126,0.08)
        );

        border: 1px solid rgba(245,180,0,0.25);

        padding: 45px;

        border-radius: 28px;

        backdrop-filter: blur(12px);

        max-width: 480px;

        margin: auto;

        box-shadow:
            0 10px 40px rgba(153,53,86,0.12);
    }

    .hero-logo {
        width: 260px;
        max-width: 90%;
        margin-bottom: 20px;
        filter: drop-shadow(0 4px 12px rgba(153,53,86,0.15));
    }

    .hero-card input[type="text"],
    .hero-card input[type="password"] {
        border-radius: 12px !important;
        border: 1.5px solid rgba(212,83,126,0.25) !important;
        padding: 10px 14px !important;
        font-size: 15px !important;
        transition: border-color 0.2s ease;
    }

    .hero-card input[type="text"]:focus,
    .hero-card input[type="password"]:focus {
        border-color: #D4537E !important;
        box-shadow: 0 0 0 3px rgba(212,83,126,0.12) !important;
    }

    /* ============================= */
    /* SIDEBAR                       */
    /* ============================= */

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFF8ED 0%, #FFFFFF 40%);
        border-right: 1px solid rgba(212,83,126,0.12);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    /* FIX: paksa semua teks sidebar jadi gelap & kebaca */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #1F2937 !important;
    }

    /* Judul menu radio */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 4px;
    }

    /* Setiap opsi menu jadi kartu kecil */
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > label {
        background: #fff;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 10px;
        padding: 8px 12px;
        margin-bottom: 2px;
        transition: all 0.15s ease;
    }

    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > label:hover {
        border-color: #D4537E;
        background: rgba(212,83,126,0.05);
    }

    /* Divider tipis */
    [data-testid="stSidebar"] hr {
        border-color: rgba(212,83,126,0.15);
        margin: 1rem 0;
    }

    /* ============================= */
    /* BUTTON (login & logout & lainnya) */
    /* ============================= */

    .stButton > button {
        background: linear-gradient(90deg, #F5B400, #D4537E) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        box-shadow: 0 4px 14px rgba(212,83,126,0.3);
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(212,83,126,0.4);
    }

    .stButton > button p {
        color: #fff !important;
    }

    /* ============================= */
    /* SIDEBAR NAV DENGAN BADGE       */
    /* (HOS / BSM / CSE-RSE)          */
    /* ============================= */

    .ml-nav {
        display: flex;
        flex-direction: column;
        gap: 4px;
        margin-bottom: 0.5rem;
    }

    .ml-nav-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        background: #fff;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 10px;
        padding: 9px 12px;
        text-decoration: none !important;
        color: #1F2937 !important;
        font-size: 14.5px;
        font-weight: 500;
        transition: all 0.15s ease;
    }

    .ml-nav-item:hover {
        border-color: #D4537E;
        background: rgba(212,83,126,0.05);
    }

    .ml-nav-item.active {
        background: linear-gradient(90deg, #F5B400, #D4537E);
        border-color: transparent;
        color: #fff !important;
        font-weight: 600;
        box-shadow: 0 4px 14px rgba(212,83,126,0.25);
    }

    .ml-nav-label {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* Badge merah bulat (mirip notif WhatsApp) */
    .ml-badge {
        flex-shrink: 0;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 20px;
        height: 20px;
        padding: 0 6px;
        border-radius: 999px;
        background: #FF3B30;
        color: #fff !important;
        font-size: 11.5px;
        font-weight: 700;
        line-height: 1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.25);
    }

    /* Badge hijau centang (semua sudah submit) */
    .ml-check {
        flex-shrink: 0;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        border-radius: 999px;
        background: #25A244;
        box-shadow: 0 1px 3px rgba(0,0,0,0.25);
        position: relative;
    }

    .ml-check::after {
        content: "";
        position: absolute;
        width: 9px;
        height: 5px;
        border-left: 2px solid #fff;
        border-bottom: 2px solid #fff;
        transform: rotate(-45deg);
        top: 6px;
        left: 5px;
    }

    @media (max-width: 768px) {

        .hero-title {
            font-size: 36px;
        }

        .hero-subtitle {
            font-size: 16px;
        }

        .hero-card {
            padding: 25px;
            border-radius: 20px;
        }

        .hero-logo {
            width: 200px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =====================================
# LOGIN
# =====================================

login_page()

# =====================================
# SIDEBAR
# =====================================

sidebar()

# =====================================
# ROLE MAPPING UNTUK BADGE NOTIF
# =====================================
#
# Setiap nama menu di sidebar dipetakan ke ROLE user (di tabel
# user) yang jadi "target submit" untuk menu tersebut. Dipakai
# HANYA untuk role HOS, BSM, CSE/RSE (bukan ADMIN/HOR / role
# submitter lainnya).
# =====================================

ROLE_MAP = {
    "Dashboard DSE": "DSE",
    "Dashboard Frontliner": "FRONTLINER",
    "Dashboard DSE Promotor": "PROMOTOR",
    "Dashboard GSE": "GSE",
    "Dashboard RGE": "RGE",
    "Dashboard GEMPI": "GEMINI",
    "Dashboard Promotor": "NP",
    "Dashboard CSE/RSE": ["CSE", "RSE"],
    "Dashboard BSM": "BSM",
}


@st.cache_data(ttl=60)
def _get_submission_status_today():
    """
    Ambil df_user (semua user, kolom di-uppercase) dan set username
    yang sudah submit MSISDN HARI INI. Di-cache 60 detik supaya
    sidebar tidak nge-hit DB/API berkali-kali tiap render.
    """

    users = tampil_user()
    df_user = pd.DataFrame(users)

    if not df_user.empty:
        df_user.columns = df_user.columns.str.upper()
        df_user["FLAG_ACTIVE"] = (
            df_user["FLAG_ACTIVE"].fillna(True).astype(bool)
        )

    hari_ini = date.today()
    data = tampil_data_by_date(hari_ini, hari_ini)

    df = pd.DataFrame(
        data,
        columns=[
            "ID", "Nama Outlet", "ID Outlet", "MSISDN",
            "Input By", "Tanggal", "flag_bio", "ga_dt"
        ]
    )

    sudah_submit = (
        set(df["Input By"].astype(str).str.strip())
        if not df.empty else set()
    )

    return df_user, sudah_submit


def hitung_belum_submit(target_roles, current_user):
    """
    Hitung (jumlah_belum_submit, total_aktif) untuk semua user
    ber-ROLE target_roles yang berada di downline current_user
    dan berstatus aktif (FLAG_ACTIVE == True).
    """

    if isinstance(target_roles, str):
        target_roles = [target_roles]

    df_user, sudah_submit = _get_submission_status_today()

    if df_user.empty:
        return 0, 0

    downline = set(get_downline(current_user))

    target = df_user[

        (df_user["ROLE"].isin(target_roles))

        &

        (df_user["FLAG_ACTIVE"] == True)

        &

        (df_user["USER"].astype(str).str.strip().isin(downline))

    ]

    total = target["USER"].nunique()

    if total == 0:
        return 0, 0

    target_users = set(
        target["USER"].astype(str).str.strip()
    )

    belum = len(target_users - sudah_submit)

    return belum, total


def render_sidebar_nav(menu_items, current_user, default_item=None):
    """
    Render menu sidebar custom (bukan st.radio) supaya bisa nampilin
    badge bulat merah (belum submit) / centang hijau (sudah lengkap)
    di sisi kanan tiap item, mirip notif WhatsApp.

    Navigasi memakai query param ?menu=... (klik = <a href>), karena
    st.radio tidak bisa merender HTML/badge di dalam optionnya.
    """

    default_item = default_item or menu_items[0]

    query_menu = st.query_params.get("menu")

    if query_menu in menu_items:
        current_menu = query_menu
    else:
        current_menu = st.session_state.get(
            "outlet_menu_selected", default_item
        )

    if current_menu not in menu_items:
        current_menu = default_item

    st.session_state["outlet_menu_selected"] = current_menu

    html = '<div class="ml-nav">'

    for item in menu_items:

        badge_html = ""
        target_roles = ROLE_MAP.get(item)

        if target_roles:

            belum, total = hitung_belum_submit(
                target_roles, current_user
            )

            if total > 0:

                if belum > 0:
                    badge_html = f'<span class="ml-badge">{belum}</span>'
                else:
                    badge_html = '<span class="ml-check"></span>'

        active_class = " active" if item == current_menu else ""
        encoded = urllib.parse.quote(item)

        html += (
            f'<a class="ml-nav-item{active_class}" '
            f'href="?menu={encoded}" target="_self">'
            f'<span class="ml-nav-label">{item}</span>'
            f'{badge_html}'
            f'</a>'
        )

    html += '</div>'

    st.sidebar.markdown(html, unsafe_allow_html=True)

    return current_menu


# =====================================
# ROLE
# =====================================

role = st.session_state.outlet_role
user = st.session_state.outlet_user

# =====================================
# MENU
# =====================================

if role in ["DSE", "FRONTLINER", "PROMOTOR", "GSE", "GEMINI", "RGE", "NP"]:

    menu = st.sidebar.radio(
        "Menu",
        [
            "Data MSISDN"
        ],
        key="outlet_menu"
    )

elif role in ["CSE","RSE"]:

    menu_items = [
        "Leaderboard Biometrik",
        "Leaderboard Quick Count",
        "Dashboard DSE",
        "Dashboard Frontliner",
        "Dashboard DSE Promotor",
        "Dashboard GSE",
        "Data MSISDN"
    ]

    menu = render_sidebar_nav(menu_items, user)

elif role == "BSM":

    menu_items = [
        "Leaderboard Biometrik",
        "Leaderboard Quick Count",
        "Dashboard DSE",
        "Dashboard Frontliner",
        "Dashboard DSE Promotor",
        "Dashboard Promotor",
        "Dashboard GSE",
        "Dashboard RGE",
        "Dashboard GEMPI",
        "Dashboard CSE/RSE",
        "Data MSISDN"
    ]

    menu = render_sidebar_nav(menu_items, user)

elif role == "HOS":

    menu_items = [
        "Leaderboard Biometrik",
        "Leaderboard Quick Count",
        "Dashboard BSM",
        "Dashboard DSE",
        "Dashboard Frontliner",
        "Dashboard DSE Promotor",
        "Dashboard Promotor",
        "Dashboard GSE",
        "Dashboard RGE",
        "Dashboard GEMPI",
        "Dashboard CSE/RSE",
        "Data MSISDN"
    ]

    menu = render_sidebar_nav(menu_items, user)

elif role in ["ADMIN", "HOR"]:

    menu = st.sidebar.radio(
        "Menu",
        [
            "Leaderboard Biometrik",
            "Leaderboard Quick Count",
            "Dashboard BSM",
            "Dashboard DSE",
            "Dashboard Frontliner",
            "Dashboard DSE Promotor",
            "Dashboard Promotor",
            "Dashboard GSE",
            "Dashboard RGE",
            "Dashboard GEMPI",
            "Dashboard CSE/RSE",
            "Data MSISDN"
        ],
        key="outlet_menu"
    )

else:

    st.error(f"Role tidak dikenali: {role}")
    st.stop()

# =====================================
# ROUTING
# =====================================

if menu == "Dashboard DSE":

    dashboard_dse()

elif menu == "Leaderboard Biometrik":

    main_dashboard()

elif menu == "Dashboard BSM":

    dashboard_bsm()

elif menu == "Leaderboard Quick Count":

    quickcount_dashboard()

elif menu == "Dashboard Frontliner":

    dashboard_fl()

elif menu == "Dashboard DSE Promotor":

    dashboard_ae()

elif menu == "Dashboard GSE":

    dashboard_gse() 

elif menu == "Dashboard CSE/RSE":

    dashboard_cse()

elif menu == "Dashboard GEMPI":

    dashboard_pm()

elif menu == "Dashboard RGE":

    dashboard_rge()

elif menu == "Dashboard Promotor":

    dashboard_np()

elif menu == "Data MSISDN":

    data_outlet()