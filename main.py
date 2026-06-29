# =====================================
# IMPORT
# =====================================

import streamlit as st

from modules.input_outlet import show as input_outlet
from modules.data_outlet import show as data_outlet
from modules.dashboard_cse import show as dashboard_cse
from modules.dashboard_dse import show as dashboard_dse
from modules.dashboard_fl import show as dashboard_fl
from modules.dashboard_pm import show as dashboard_pm

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

    .hero-container {
        padding-top: 30px;
        padding-bottom: 20px;
        text-align: center;
    }

    .hero-title {
        font-size: 58px;
        font-weight: 800;
        margin-bottom: 10px;
        background: linear-gradient(
            90deg,
            #001F5B,
            #2563EB,
            #06B6D4
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 22px;
        color: #6B7280;
        margin-bottom: 30px;
        font-weight: 500;
    }

    .hero-card {

        background: linear-gradient(
            135deg,
            rgba(37,99,235,0.10),
            rgba(6,182,212,0.10)
        );

        border: 1px solid rgba(255,255,255,0.2);

        padding: 40px;

        border-radius: 28px;

        backdrop-filter: blur(12px);

        max-width: 1000px;

        margin: auto;

        box-shadow:
            0 10px 40px rgba(0,0,0,0.08);
    }

    .hero-logo {
        width: 520px;
        max-width: 90%;
        margin-bottom: 20px;
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
            width: 280px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)
# =====================================
# HERO LOGO
# =====================================

col1, col2, col3 = st.columns([1,2,1])

with col2:

    st.image(
        r"C:\Users\INSP-PRAYU\Monitoring\outlet\logo.png",
        use_container_width=True
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

if role in ["DSE", "FRONTLINER", "PROMOTOR"]:

    menu = st.sidebar.radio(
        "Menu",
        [
            "Input MSISDN",
            "Data Outlet"
        ],
        key="outlet_menu"
    )

elif role in ["CSE", "RSE"]:

    menu = st.sidebar.radio(
        "Menu",
        [
            "Dashboard DSE",
            "Dashboard Frontliner",
            "Dashboard Promotor",
            "Input MSISDN",
            "Data Outlet"
        ],
        key="outlet_menu"
    )

elif role == "BSM":

    menu = st.sidebar.radio(
        "Menu",
        [
            "Dashboard DSE",
            "Dashboard Frontliner",
            "Dashboard Promotor",
            "Dashboard CSE",
            "Data Outlet"
        ],
        key="outlet_menu"
    )

elif role == "HOS":

    menu = st.sidebar.radio(
        "Menu",
        [
            "Dashboard DSE",
            "Dashboard Frontliner",
            "Dashboard Promotor",
            "Dashboard CSE",
            "Data Outlet"
        ],
        key="outlet_menu"
    )

elif role == "ADMIN":

    menu = st.sidebar.radio(
        "Menu",
        [
            "Dashboard DSE",
            "Dashboard Frontliner",
            "Dashboard Promotor",
            "Dashboard CSE",
            "Data Outlet",
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

elif menu == "Dashboard Frontliner":

    dashboard_fl()

elif menu == "Dashboard Promotor":

    dashboard_pm()

elif menu == "Dashboard CSE":

    dashboard_cse()

elif menu == "Input MSISDN":

    input_outlet()

elif menu == "Data Outlet":

    data_outlet()

elif menu == "Master User":

    st.title("👥 Master User")
    st.info("Menu masih dalam proses migrasi.")