# =========================================================
# dashboard_frontliner.py
# DASHBOARD FRONTLINER
# HOS -> BSM -> CSE/RSE -> FRONTLINER
# =========================================================

import streamlit as st
import pandas as pd

from st_aggrid import (
    AgGrid,
    GridOptionsBuilder
)

from database import (
    tampil_data,
    tampil_user
)

# =========================================================
# LOAD BIOMETRIK
# =========================================================

@st.cache_data
def load_biometrik():

    biometrik = pd.read_csv(

        "ga_biometrics_cj.csv",

        dtype=str,

        low_memory=False

    )

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

    return set(
        biometrik["msisdn"]
    )

# =========================================================
# GRID TABLE
# =========================================================

def show_grid(df):

    if df.empty:

        st.info("Tidak ada data.")
        return

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(

        resizable=True,

        sortable=True,

        filter=True

    )

    # =====================================================
    # TOTAL ROW
    # =====================================================

    total_row = {}

    for col in df.columns:

        # =================================================
        # NUMERIC
        # =================================================

        if pd.api.types.is_numeric_dtype(df[col]):

            total_row[col] = int(
                df[col].sum()
            )

        # =================================================
        # TEXT
        # =================================================

        else:

            if col in [

                "HOS",
                "BSM",
                "Branch",
                "CSE/RSE",
                "Frontliner"

            ]:

                total_row[col] = (
                    df[col].nunique()
                )

            else:

                total_row[col] = ""

    grid_options = gb.build()

    grid_options["pinnedBottomRowData"] = [
        total_row
    ]

    # =====================================================
    # HEIGHT
    # =====================================================

    row_count = len(df)

    table_height = min(

        80 + (row_count * 42),

        500

    )

    # =====================================================
    # GRID
    # =====================================================

    AgGrid(

        df,

        gridOptions=grid_options,

        fit_columns_on_grid_load=True,

        height=table_height,

        theme="balham",

        allow_unsafe_jscode=True,

        custom_css={

            ".ag-root-wrapper": {

                "border": "1px solid #e5e7eb",

                "border-radius": "14px",

                "overflow": "hidden"

            },

            ".ag-header": {

                "background-color": "#f8fafc",

                "font-weight": "700"

            },

            ".ag-row": {

                "font-size": "14px"

            },

            ".ag-pinned-bottom": {

                "background-color": "#eef2ff",

                "font-weight": "700",

                "border-top": "2px solid #6366f1"

            }

        }

    )

# =========================================================
# DASHBOARD
# =========================================================

def show():

    st.title("📊 Dashboard Frontliner")

    # =====================================================
    # LOAD DATA
    # =====================================================

    data = tampil_data()

    users = tampil_user()

    if len(data) == 0:

        st.info(
            "Belum ada data."
        )

        return

    # =====================================================
    # DATAFRAME
    # =====================================================

    df = pd.DataFrame(

        data,

        columns=[

            "ID",
            "Nama Outlet",
            "ID Outlet",
            "MSISDN",
            "Input By",
            "Tanggal"

        ]

    )

    # =====================================================
    # BIOMETRIK
    # =====================================================

    biometrik_set = load_biometrik()

    df["MSISDN"] = (

        df["MSISDN"]

        .fillna("")
        .astype(str)
        .str.strip()

    )

    df["Biometrik"] = (

        df["MSISDN"]
        .isin(biometrik_set)

    )

    # =====================================================
    # USER DF
    # =====================================================

    df_user = pd.DataFrame(

        users,

        columns=[

            "USER",
            "ROLE",
            "ATASAN"

        ]

    )

    # =====================================================
    # SESSION
    # =====================================================

    role = st.session_state.outlet_role

    user = st.session_state.outlet_user

    # =====================================================
    # FILTER TANGGAL
    # =====================================================

    df["Tanggal"] = pd.to_datetime(

        df["Tanggal"],

        errors="coerce"

    )

    tanggal = st.date_input(

        "📅 Filter Tanggal",

        value=None,

        key="fl_tanggal"

    )

    if tanggal:

        df = df[

            df["Tanggal"].dt.date == tanggal

        ]

    st.divider()

    # =====================================================
    # FILTER ROLE
    # =====================================================

    if role == "FRONTLINER":

        df = df[
            df["Input By"] == user
        ]

    elif role in [

        "CSE",
        "RSE"

    ]:

        daftar_fl = df_user[

            (df_user["ATASAN"] == user)
            &
            (df_user["ROLE"] == "FRONTLINER")

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(
                daftar_fl
            )
        ]

    elif role == "BSM":

        daftar_cse = df_user[

            df_user["ATASAN"] == user

        ]["USER"].tolist()

        daftar_fl = df_user[

            (df_user["ATASAN"]
            .isin(daftar_cse))
            &
            (df_user["ROLE"] == "FRONTLINER")

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(
                daftar_fl
            )
        ]

    elif role == "HOS":

        daftar_bsm = df_user[

            df_user["ATASAN"] == user

        ]["USER"].tolist()

        daftar_cse = df_user[

            df_user["ATASAN"]
            .isin(daftar_bsm)

        ]["USER"].tolist()

        daftar_fl = df_user[

            (df_user["ATASAN"]
            .isin(daftar_cse))
            &
            (df_user["ROLE"] == "FRONTLINER")

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(
                daftar_fl
            )
        ]

    # =====================================================
    # KPI FRONTLINER
    # FOKUS INPUT FRONTLINER
    # =====================================================

    daftar_fl_all = df_user[

        df_user["ROLE"] == "FRONTLINER"

    ]["USER"].tolist()

    df_fl = df[

        df["Input By"]
        .isin(daftar_fl_all)

    ]

    fl_aktif = (

        df_fl["Input By"]
        .nunique()

    )

    jumlah_outlet = (

        df_fl["ID Outlet"]
        .nunique()

    )

    jumlah_msisdn = len(
        df_fl
    )

    jumlah_biometrik = (

        df_fl["Biometrik"]
        .sum()

    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(

        "👤 Frontliner Aktif",

        fl_aktif

    )

    col2.metric(

        "🏪 Outlet Input Frontliner",

        jumlah_outlet

    )

    col3.metric(

        "📱 MSISDN Input Frontliner",

        jumlah_msisdn

    )

    col4.metric(

        "✅ Biometrik Input Frontliner",

        jumlah_biometrik

    )

    st.divider()

    # =====================================================
    # REKAP HOS
    # =====================================================

    if role == "ADMIN":

        st.subheader("📋 Rekap HOS")

        rekap_hos = []

        hos_list = df_user[
            df_user["ROLE"] == "HOS"
        ]

        for _, row in hos_list.iterrows():

            nama_hos = row["USER"]

            daftar_bsm = df_user[
                df_user["ATASAN"] == nama_hos
            ]["USER"].tolist()

            daftar_cse = df_user[
                df_user["ATASAN"]
                .isin(daftar_bsm)
            ]["USER"].tolist()

            daftar_fl = df_user[

                (df_user["ATASAN"]
                .isin(daftar_cse))
                &
                (df_user["ROLE"] == "FRONTLINER")

            ]["USER"].tolist()

            temp = df[
                df["Input By"]
                .isin(daftar_fl)
            ]

            rekap_hos.append({

                "HOS":
                    nama_hos,

                "BSM":
                    len(daftar_bsm),

                "CSE/RSE":
                    len(daftar_cse),

                # ======================================
                # TOTAL FRONTLINER
                # ======================================

                "Frontliner":
                    len(daftar_fl),

                # ======================================
                # FRONTLINER AKTIF
                # ======================================

                "Frontliner Aktif":
                    temp["Input By"]
                    .nunique(),

                # ======================================
                # KPI HARUS INPUT FRONTLINER
                # ======================================

                "Outlet":
                    temp["ID Outlet"]
                    .nunique(),

                "MSISDN":
                    len(temp),

                "Biometrik":
                    temp["Biometrik"]
                    .sum()

            })

        summary_hos = pd.DataFrame(
            rekap_hos
        )

        if not summary_hos.empty:

            summary_hos = (

                summary_hos

                .sort_values(

                    "MSISDN",

                    ascending=False

                )

            )

        show_grid(summary_hos)

        st.divider()

    # =====================================================
    # REKAP BSM
    # =====================================================

    if role in [

        "HOS",
        "ADMIN"

    ]:

        st.subheader("📋 Rekap BSM")

        rekap_bsm = []

        bsm_list = df_user[
            df_user["ROLE"] == "BSM"
        ]

        for _, row in bsm_list.iterrows():

            nama_bsm = row["USER"]

            daftar_cse = df_user[
                df_user["ATASAN"] == nama_bsm
            ]["USER"].tolist()

            daftar_fl = df_user[

                (df_user["ATASAN"]
                .isin(daftar_cse))
                &
                (df_user["ROLE"] == "FRONTLINER")

            ]["USER"].tolist()

            temp = df[
                df["Input By"]
                .isin(daftar_fl)
            ]

            rekap_bsm.append({

                "BSM":
                    nama_bsm,

                "CSE/RSE":
                    len(daftar_cse),

                # ======================================
                # TOTAL FRONTLINER
                # ======================================

                "Frontliner":
                    len(daftar_fl),

                # ======================================
                # FRONTLINER AKTIF
                # ======================================

                "Frontliner Aktif":
                    temp["Input By"]
                    .nunique(),

                "Outlet":
                    temp["ID Outlet"]
                    .nunique(),

                "MSISDN":
                    len(temp),

                "Biometrik":
                    temp["Biometrik"]
                    .sum()

            })

        summary_bsm = pd.DataFrame(
            rekap_bsm
        )

        if not summary_bsm.empty:

            summary_bsm = (

                summary_bsm

                .sort_values(

                    "MSISDN",

                    ascending=False

                )

            )

        show_grid(summary_bsm)

        st.divider()

    # =====================================================
    # REKAP CSE/RSE
    # =====================================================

    if role in [

        "BSM",
        "HOS",
        "ADMIN"

    ]:

        st.subheader("📋 Rekap CSE/RSE")

        rekap_cse = []

        cse_list = df_user[
            df_user["ROLE"]
            .isin([
                "CSE",
                "RSE"
            ])
        ]

        for _, row in cse_list.iterrows():

            nama_cse = row["USER"]

            daftar_fl = df_user[

                (df_user["ATASAN"] == nama_cse)
                &
                (df_user["ROLE"] == "FRONTLINER")

            ]["USER"].tolist()

            temp = df[
                df["Input By"]
                .isin(daftar_fl)
            ]

            if len(temp) > 0:

                rekap_cse.append({

                    "CSE/RSE":
                        nama_cse,

                    "Branch":
                        row["ATASAN"],

                    # ==============================
                    # TOTAL FRONTLINER
                    # ==============================

                    "Frontliner":
                        len(daftar_fl),

                    # ==============================
                    # FRONTLINER AKTIF
                    # ==============================

                    "Frontliner Aktif":
                        temp["Input By"]
                        .nunique(),

                    "Outlet":
                        temp["ID Outlet"]
                        .nunique(),

                    "MSISDN":
                        len(temp),

                    "Biometrik":
                        temp["Biometrik"]
                        .sum()

                })

        summary_cse = pd.DataFrame(
            rekap_cse
        )

        if not summary_cse.empty:

            summary_cse = (

                summary_cse

                .sort_values(

                    "MSISDN",

                    ascending=False

                )

            )

        show_grid(summary_cse)

        st.divider()

    # =====================================================
    # REKAP FRONTLINER
    # =====================================================

    st.subheader("📋 Rekap Frontliner")

    rekap_fl = []

    fl_user = df_user[
        df_user["ROLE"] == "FRONTLINER"
    ]

    for _, row in fl_user.iterrows():

        nama_fl = row["USER"]

        temp = df[
            df["Input By"] == nama_fl
        ]

        if len(temp) > 0:

            rekap_fl.append({

                "Frontliner":
                    nama_fl,

                "Atasan":
                    row["ATASAN"],

                "Outlet":
                    temp["ID Outlet"]
                    .nunique(),

                "MSISDN":
                    len(temp),

                "Biometrik":
                    temp["Biometrik"]
                    .sum()

            })

    summary_fl = pd.DataFrame(
        rekap_fl
    )

    if not summary_fl.empty:

        summary_fl = (

            summary_fl

            .sort_values(

                "MSISDN",

                ascending=False

            )

        )

    show_grid(summary_fl)

    st.divider()

