# =====================================
# IMPORT
# =====================================

import streamlit as st
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

from auth import login_page, sidebar



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
# ROLE
# =====================================

role = st.session_state.outlet_role

# =====================================
# MENU
# =====================================

if role in ["DSE", "FRONTLINER", "PROMOTOR", "GSE", "GEMINI", "RGE"]:

    menu = st.sidebar.radio(
        "Menu",
        [
            "Data MSISDN"
        ],
        key="outlet_menu"
    )

elif role in ["CSE", "RSE"]:

    menu = st.sidebar.radio(
        "Menu",
        [
            "Leaderboard Biometrik",
            "Leaderboard Quick Count",
            "Dashboard DSE",
            "Dashboard Frontliner",
            "Dashboard Promotor",
            "Dashboard GSE",
            "Data MSISDN"
        ],
        key="outlet_menu"
    )

elif role == "BSM":

    menu = st.sidebar.radio(
        "Menu",
        [
            "Leaderboard Biometrik",
            "Leaderboard Quick Count",
            "Dashboard DSE",
            "Dashboard Frontliner",
            "Dashboard Promotor",
            "Dashboard GSE",
            "Dashboard RGE",
            "Dashboard GEMPI",
            "Dashboard CSE/RSE",
            "Data MSISDN"
        ],
        key="outlet_menu"
    )

elif role == "HOS":

    menu = st.sidebar.radio(
        "Menu",
        [
            "Leaderboard Biometrik",
            "Leaderboard Quick Count",
            "Dashboard BSM",
            "Dashboard DSE",
            "Dashboard Frontliner",
            "Dashboard Promotor",
            "Dashboard GSE",
            "Dashboard RGE",
            "Dashboard GEMPI",
            "Dashboard CSE/RSE",
            "Data MSISDN"
        ],
        key="outlet_menu"
    )

elif role == "ADMIN":

    menu = st.sidebar.radio(
        "Menu",
        [
            "Leaderboard Biometrik",
            "Leaderboard Quick Count",
            "Dashboard BSM",
            "Dashboard DSE",
            "Dashboard Frontliner",
            "Dashboard Promotor",
            "Dashboard GSE",
            "Dashboard RGE",
            "Dashboard GEMPI",
            "Dashboard CSE/RSE",
            "Data MSISDN",
            "Master User"
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

elif menu == "Dashboard Promotor":

    dashboard_ae()

elif menu == "Dashboard GSE":

    dashboard_gse() 

elif menu == "Dashboard CSE/RSE":

    dashboard_cse()

elif menu == "Dashboard GEMPI":

    dashboard_pm()

elif menu == "Dashboard RGE":

    dashboard_rge()

elif menu == "Data MSISDN":

    data_outlet()