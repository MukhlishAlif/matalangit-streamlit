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
from modules.performance import show as performance

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

st.markdown(
    """
    <link rel="stylesheet"
    href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" />
    """,
    unsafe_allow_html=True
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

    /* Setiap opsi menu jadi kartu kecil -- width DIPAKSA 100% supaya
       border kanan semua item SEJAJAR/rata, tidak mengikuti panjang
       teks masing-masing (mis. "Dashboard BSM" vs
       "Dashboard DSE Promotor"). */
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > label {
        background: #fff;
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 10px;
        padding: 8px 12px;
        margin-bottom: 2px;
        width: 100% !important;
        box-sizing: border-box;
        display: flex !important;
        align-items: center !important;
        transition: all 0.15s ease;
    }

    /* Parent radiogroup -- pastikan setiap <label> ikut lebar penuh
       kolom sidebar, bukan lebar konten teksnya sendiri. */
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] {
        width: 100% !important;
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
    /* Dipakai via st.sidebar.button  */
    /* (key diawali "navbtn_") supaya */
    /* TIDAK full-reload browser      */
    /* (aman dari kehilangan sesi)    */
    /* ============================= */

    [data-testid="stSidebar"] div[class*="st-key-navbtn_"] {
        margin-bottom: 4px;
    }

    /* Tinggi tombol nav DIKUNCI (min-height) supaya semua tombol
       dashboard punya ukuran kotak yang SAMA PERSIS, baik yang
       ada badge/centang di sampingnya maupun yang tidak (mis.
       Dashboard Frontliner yang sudah tanpa notif). */
    [data-testid="stSidebar"] div[class*="st-key-navbtn_"] button {
        background: #fff !important;
        color: #1F2937 !important;
        border: 1px solid rgba(0,0,0,0.06) !important;
        border-radius: 10px !important;
        padding: 9px 12px !important;
        min-height: 42px !important;
        font-weight: 500 !important;
        font-size: 14.5px !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        transform: none !important;
        display: flex !important;
    }

    /* Perkuat rata kiri sampai ke wrapper teks di dalam tombol,   */
    /* karena Streamlit kadang nge-center teks tombol lewat        */
    /* div/markdown-container internal, bukan cuma di elemen       */
    /* <button>-nya sendiri.                                       */
    [data-testid="stSidebar"] div[class*="st-key-navbtn_"] button > div,
    [data-testid="stSidebar"] div[class*="st-key-navbtn_"] button div[data-testid="stMarkdownContainer"] {
        justify-content: flex-start !important;
        text-align: left !important;
        width: 100% !important;
    }

    [data-testid="stSidebar"] div[class*="st-key-navbtn_"] button div[data-testid="stMarkdownContainer"] p {
        text-align: left !important;
        width: 100% !important;
        margin: 0 !important;
    }

    [data-testid="stSidebar"] div[class*="st-key-navbtn_"] button:hover {
        border-color: #D4537E !important;
        background: rgba(212,83,126,0.05) !important;
        transform: none !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] div[class*="st-key-navbtn_"] button p {
        color: #1F2937 !important;
        font-weight: 500 !important;
    }

    /* Item aktif (type="primary") */
    /* PENTING: border-width DISAMAKAN dengan tombol non-aktif (1px)
       supaya ukuran/tinggi kotak semua tombol dashboard SERAGAM.
       Bedanya cukup lewat warna border + background saja, bukan
       lewat ketebalan border. */
    [data-testid="stSidebar"] div[class*="st-key-navbtn_"] button[kind="primary"] {
        background: rgba(212,83,126,0.08) !important;
        border: 1px solid #D4537E !important;
    }

    [data-testid="stSidebar"] div[class*="st-key-navbtn_"] button[kind="primary"] p {
        color: #1F2937 !important;
        font-weight: 600 !important;
    }

    /* ============================= */
    /* BADGE NOTIF (kolom kecil di    */
    /* sebelah tombol nav)            */
    /*                                 */
    /* Selector di-prefix ganda       */
    /* [data-testid="stSidebar"] +    */
    /* .ml-badge/.ml-check supaya     */
    /* SPESIFISITAS-nya lebih tinggi  */
    /* daripada aturan global         */
    /* "[data-testid=stSidebar] span" */
    /* di atas, jadi warnanya tidak   */
    /* ketiban abu-abu.               */
    /* ============================= */

    /* Wrapper badge/centang: dibuat setinggi tombol nav (min-height
       sama dengan button di atas) dan di-flex-center supaya badge
       SEJAJAR/rata tengah vertikal dengan tombol dashboard-nya,
       bukan nempel di atas (margin-top manual). */
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .ml-badge-wrap{
        display:flex;
        align-items:center;
        justify-content:center;
        height:42px;
        width:100%;
        margin-top:-20px;
    }

    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .ml-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 26px;
        height: 26px;
        padding: 0 8px;
        border-radius: 999px;
        background: #FF3B30 !important;
        color: #fff !important;
        font-size: 12.5px;
        font-weight: 700;
        line-height: 1;
        box-shadow: 0 1px 3px rgba(0,0,0,0.25);
    }

    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .ml-check {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        border-radius: 999px;
        background: #25A244 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.25);
        position: relative;
    }

    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] .ml-check::after {
        content: "";
        position: absolute;
        width: 10px;
        height: 6px;
        border-left: 2px solid #fff;
        border-bottom: 2px solid #fff;
        transform: rotate(-45deg);
        top: 8px;
        left: 8px;
    }

    /* ============================= */
    /* POPUP SUMMARY BELUM SUBMIT     */
    /* ============================= */

    .ml-summary-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 14px;
        border-radius: 10px;
        background: #F9FAFB;
        border: 1px solid rgba(0,0,0,0.06);
        margin-bottom: 6px;
    }

    .ml-summary-label {
        font-weight: 600;
        color: #1F2937;
        font-size: 14.5px;
    }

    .ml-summary-value-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 26px;
        height: 26px;
        padding: 0 8px;
        border-radius: 999px;
        background: #FF3B30;
        color: #fff;
        font-size: 13px;
        font-weight: 700;
    }

    .ml-summary-value-check {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        border-radius: 999px;
        background: #25A244;
        position: relative;
    }

    .ml-summary-value-check::after {
        content: "";
        position: absolute;
        width: 10px;
        height: 6px;
        border-left: 2px solid #fff;
        border-bottom: 2px solid #fff;
        transform: rotate(-45deg);
        top: 8px;
        left: 8px;
    }

    /* Row "sudah semua submit" -> aksen hijau */
    .ml-summary-row-done {
        background: rgba(37,162,68,0.06) !important;
        border-color: rgba(37,162,68,0.25) !important;
    }

    /* ============================= */
    /* TOMBOL LONCENG NOTIF (buka    */
    /* ulang popup ringkasan)         */
    /* ============================= */

    div[class*="st-key-btn_bell_summary"] button {
        background: #FF3B30 !important;
        color: #fff !important;
        border: none !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        padding: 0 !important;
        font-size: 17px !important;
        box-shadow: 0 2px 8px rgba(255,59,48,0.4) !important;
        transform: none !important;
        animation: ml-bell-pulse 2s ease-in-out infinite;
    }

    div[class*="st-key-btn_bell_summary"] button:hover {
        background: #E5352B !important;
        transform: scale(1.05) !important;
        box-shadow: 0 3px 10px rgba(255,59,48,0.5) !important;
    }

    @keyframes ml-bell-pulse {
        0%, 100% {
            box-shadow: 0 0 0 0 rgba(255,59,48,0.5);
        }
        50% {
            box-shadow: 0 0 0 6px rgba(255,59,48,0);
        }
    }

    .ml-summary-label-done {
        color: #1D8A3A !important;
        font-weight: 600 !important;
    }

    /* Expander "belum submit" -> aksen merah di border/background.
       DI-SCOPE hanya di dalam dialog popup (stDialog), supaya
       TIDAK ikut mengubah tampilan st.expander di halaman/dashboard
       lain yang tidak berhubungan dengan popup ini. */
    div[data-testid="stDialog"] div[data-testid="stExpander"],
    div[data-testid="stExpander"].ml-expander-belum {
        border: 1px solid rgba(255,59,48,0.25) !important;
        background: rgba(255,59,48,0.04) !important;
        border-radius: 10px !important;
        margin-bottom: 6px !important;
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

        .ml-summary-label {
            font-size: 13px;
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
#
# CATATAN: "Dashboard Frontliner" SENGAJA TIDAK dimasukkan ke
# ROLE_MAP. Sesuai permintaan, menu ini tidak butuh notif
# badge/centang sama sekali -> status belum-submit-nya diabaikan.
# =====================================

ROLE_MAP = {
    "Dashboard DSE": "DSE",
    "Dashboard DSE Promotor": "PROMOTOR",
    "Dashboard GSE": "GSE",
    "Dashboard RGE": "RGE",
    "Dashboard GEMPI": "GEMINI",
    "Dashboard Promotor": "NP",
    "Dashboard CSE/RSE": ["CSE", "RSE"],
    "Dashboard BSM": "BSM",
}


# =====================================
# MAPPING UNTUK POPUP SUMMARY
# =====================================
#
# role login -> { label yang ditampilkan di popup : role/list-role
# target di tabel user }. Hanya role HOS, BSM, CSE, RSE yang punya
# popup summary (role submitter murni seperti DSE/FRONTLINER/dst
# tidak punya bawahan sehingga tidak perlu popup).
#
# Catatan: popup ringkasan ini TIDAK diubah -> "Frontliner" masih
# tetap tampil di sana kalau permintaannya cuma untuk badge di
# sidebar nav. Kalau mau Frontliner juga diabaikan di popup ini,
# tinggal hapus baris "Frontliner" di tiap dict di bawah.
# =====================================

POPUP_SUMMARY_MAP = {
    "HOS": {
        "BSM": "BSM",
        "DSE": "DSE",
        "DSE Promotor": "PROMOTOR",
        "Promotor": "NP",
        "GSE": "GSE",
        "RGE": "RGE",
        "GEMPI": "GEMINI",
        "CSE/RSE": ["CSE", "RSE"],
    },
    "BSM": {
        "DSE": "DSE",
        "DSE Promotor": "PROMOTOR",
        "Promotor": "NP",
        "GSE": "GSE",
        "RGE": "RGE",
        "GEMPI": "GEMINI",
        "CSE/RSE": ["CSE", "RSE"],
    },
    "CSE": {
        "DSE": "DSE",
        "DSE Promotor": "PROMOTOR",
        "GSE": "GSE",
    },
    "RSE": {
        "DSE": "DSE",
        "DSE Promotor": "PROMOTOR",
        "GSE": "GSE",
    },
}


@st.cache_data(ttl=60)
def _get_submission_status_today():
    """
    Ambil df_user (semua user, kolom di-uppercase) dan set username
    yang sudah submit MSISDN HARI INI. Di-cache 60 detik supaya
    sidebar/popup tidak nge-hit DB/API berkali-kali tiap render.
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


def _get_user_list_belum_submit(target_roles, current_user):
    """
    Ambil daftar detail user (Username, Nama) yang BELUM submit
    hari ini, untuk role target_roles yang berada di downline
    current_user dan berstatus aktif. Dipakai untuk isi tabel
    detail di dalam expander popup.
    """

    if isinstance(target_roles, str):
        target_roles = [target_roles]

    df_user, sudah_submit = _get_submission_status_today()

    if df_user.empty:
        return pd.DataFrame(columns=["Username", "Nama"])

    downline = set(get_downline(current_user))

    target = df_user[

        (df_user["ROLE"].isin(target_roles))

        &

        (df_user["FLAG_ACTIVE"] == True)

        &

        (df_user["USER"].astype(str).str.strip().isin(downline))

    ].copy()

    target["USER"] = target["USER"].astype(str).str.strip()

    belum_df = target[~target["USER"].isin(sudah_submit)]

    # cari kolom nama secara otomatis (sesuaikan di sini kalau
    # nama kolom di database kamu berbeda)
    name_col = next(
        (c for c in ["REAL_NAME", "NAMA", "NAME", "NAMA_LENGKAP"] if c in belum_df.columns),
        None
    )

    if name_col:
        result = (
            belum_df[["USER", name_col]]
            .drop_duplicates()
            .sort_values("USER")
            .reset_index(drop=True)
            .rename(columns={"USER": "Username", name_col: "Nama"})
        )
    else:
        result = (
            belum_df[["USER"]]
            .drop_duplicates()
            .sort_values("USER")
            .reset_index(drop=True)
            .rename(columns={"USER": "Username"})
        )

    return result


def render_sidebar_nav(menu_items, current_user, default_item=None):
    """
    Render menu sidebar custom (bukan st.radio) supaya bisa nampilin
    badge merah (belum submit) / centang hijau (sudah lengkap) di
    tiap item, mirip notif WhatsApp.

    PENTING: navigasi memakai st.sidebar.button (bukan <a href>).
    <a href="?menu=..."> menyebabkan BROWSER RELOAD PENUH, yang
    memutus koneksi/sesi Streamlit sehingga user "ke-logout" saat
    pindah dashboard. st.button tetap dalam sesi Streamlit yang
    sama (rerun via WebSocket), jadi session_state login TIDAK
    pernah hilang.

    KHUSUS "Dashboard Frontliner": item ini SENGAJA dikecualikan
    dari perhitungan badge (lihat ROLE_MAP di atas, item ini tidak
    ada di sana) -> total selalu 0 -> kolom badge dibiarkan kosong,
    tapi tombolnya tetap dirender dengan ukuran/tinggi yang SAMA
    seperti tombol dashboard lain (dikunci lewat CSS min-height),
    supaya kotaknya tetap seragam meski tanpa badge di sampingnya.
    """

    default_item = default_item or menu_items[0]

    current_menu = st.session_state.get(
        "outlet_menu_selected", default_item
    )

    if current_menu not in menu_items:
        current_menu = default_item

    st.session_state["outlet_menu_selected"] = current_menu

    for item in menu_items:

        belum, total = 0, 0
        target_roles = ROLE_MAP.get(item)

        if target_roles:
            belum, total = hitung_belum_submit(
                target_roles, current_user
            )

        is_active = (item == current_menu)

        col_btn, col_badge = st.sidebar.columns(
            [5, 1], gap="small", vertical_alignment="center"
        )

        with col_btn:
            clicked = st.button(
                item,
                key=f"navbtn_{item}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            )

        with col_badge:
            if total > 0:
                if belum > 0:
                    st.markdown(
                        f'<div class="ml-badge-wrap"><div class="ml-badge">{belum}</div></div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div class="ml-badge-wrap"><div class="ml-check"></div></div>',
                        unsafe_allow_html=True
                    )

        if clicked and not is_active:
            st.session_state["outlet_menu_selected"] = item

            # sinkronkan URL biar bisa di-bookmark (opsional,
            # tidak memicu reload karena di-set lewat Python API,
            # bukan lewat <a href> / navigasi browser)
            try:
                st.query_params["menu"] = item
            except Exception:
                pass

            st.rerun()

    return st.session_state["outlet_menu_selected"]


# =====================================
# POPUP RINGKASAN "BELUM SUBMIT"
# =====================================
#
# Muncul SEKALI setiap sesi login (bukan setiap pindah menu/page),
# untuk role HOS / BSM / CSE / RSE. Ditandai lewat session_state
# per-username, jadi tidak akan trigger ulang saat rerun karena
# pindah dashboard, dan tidak menyentuh state login sama sekali
# (aman dari ke-logout).
# =====================================

# fallback kalau versi streamlit belum punya st.dialog (>=1.31)
_dialog_decorator = getattr(st, "dialog", None) or getattr(
    st, "experimental_dialog", None
)


def _popup_flag_key(user):
    return f"popup_summary_shown__{user}"


def _render_summary_rows(role, user):

    role_targets = POPUP_SUMMARY_MAP.get(role, {})

    if not role_targets:
        st.info("Tidak ada data ringkasan untuk role ini.")
        return

    any_row = False

    for label, target_roles in role_targets.items():

        belum, total = hitung_belum_submit(target_roles, user)

        if total == 0:
            continue

        any_row = True

        if belum > 0:

            # baris yang masih ada tunggakan -> merah, bisa diklik
            # untuk buka detail siapa aja yang belum submit
            with st.expander(
                f":red[**{label}**]  —  :red[**{belum}**] dari {total} belum submit"
            ):

                df_detail = _get_user_list_belum_submit(
                    target_roles, user
                )

                if df_detail.empty:
                    st.caption("Tidak ada detail user yang bisa ditampilkan.")
                else:
                    st.dataframe(
                        df_detail,
                        use_container_width=True,
                        hide_index=True
                    )

        else:

            # semua sudah submit -> hijau, row biasa (tidak ada
            # detail untuk dibuka)
            st.markdown(
                f'<div class="ml-summary-row ml-summary-row-done">'
                f'<span class="ml-summary-label ml-summary-label-done">{label}</span>'
                f'<span class="ml-summary-value-check"></span>'
                f'</div>',
                unsafe_allow_html=True
            )

    if not any_row:
        st.info("Belum ada bawahan aktif untuk role ini.")


if _dialog_decorator is not None:

    @_dialog_decorator("DAILY QUEST")
    def _show_submit_summary_popup(role, user):

        _render_summary_rows(role, user)


else:

    # fallback paling aman untuk versi streamlit lama (tanpa
    # st.dialog): tampilkan di atas halaman sebagai container biasa
    # (BUKAN st.expander, karena tiap baris "belum submit" di
    # _render_summary_rows sudah pakai st.expander sendiri --
    # Streamlit tidak mengizinkan expander bersarang/nested).
    def _show_submit_summary_popup(role, user):

        st.markdown("#### Tim Belum Submit")
        _render_summary_rows(role, user)
        st.divider()


# =====================================
# ROLE
# =====================================

role = st.session_state.outlet_role
user = st.session_state.outlet_user


# tampilkan popup ringkasan sekali saja per sesi login,
# hanya untuk role yang punya bawahan (HOS / BSM / CSE / RSE)
if role in POPUP_SUMMARY_MAP:

    flag_key = _popup_flag_key(user)

    force_popup = st.session_state.pop(
        "force_show_summary_popup", False
    )

    if force_popup or not st.session_state.get(flag_key, False):
        st.session_state[flag_key] = True
        _show_submit_summary_popup(role, user)

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
        "Dashboard Promotor",
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
        "Performance Team",
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

elif menu == "Performance Team":

    performance()