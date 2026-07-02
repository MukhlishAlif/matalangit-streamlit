# ==========================================================
# IMPORT
# ==========================================================

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

# ==========================================================
# LOAD BIOMETRIK
# ==========================================================

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

# ==========================================================
# GRID TABLE
# ==========================================================

def show_grid(df):

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_default_column(

        resizable=True,
        sortable=True,
        filter=True

    )

    # ======================================================
    # PINNED BOTTOM TOTAL
    # ======================================================

    total_row = {}

    for col in df.columns:

        # ==================================================
        # NUMERIC
        # ==================================================

        if pd.api.types.is_numeric_dtype(df[col]):

            total_row[col] = int(
                df[col].sum()
            )

        # ==================================================
        # TEXT
        # ==================================================

        else:

            if col in [

                "HoS",
                "Branch",
                "BSM",
                "CSE/RSE"

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

    # ======================================================
    # AUTO HEIGHT
    # ======================================================

    row_count = len(df)

    table_height = min(

        80 + (row_count * 42),

        500

    )

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
# ==========================================================
# DASHBOARD
# ==========================================================

def show():

    st.title("📊 Dashboard CSE/RSE")

    # ======================================================
    # LOAD DATA
    # ======================================================

    data = tampil_data()

    users = tampil_user()

    # ======================================================
    # EMPTY
    # ======================================================

    if len(data) == 0:

        st.info(
            "Belum ada data."
        )

        return

    # ======================================================
    # DATAFRAME
    # ======================================================

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

    # ======================================================
    # BIOMETRIK
    # ======================================================

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
        .astype(int)

    )

    # ======================================================
    # USER DATAFRAME
    # ======================================================

    df_user = pd.DataFrame(

        users,

        columns=[

            "USER",
            "ROLE",
            "ATASAN"

        ]

    )

    # ======================================================
    # SESSION
    # ======================================================

    role = st.session_state.outlet_role

    user = st.session_state.outlet_user

    # ======================================================
    # FILTER TANGGAL
    # ======================================================

    df["Tanggal"] = pd.to_datetime(

        df["Tanggal"],

        errors="coerce"

    )

    tanggal = st.date_input(

        "📅 Filter Tanggal",

        value=None,

        key="dashboard_tanggal"

    )

    if tanggal:

        df = df[

            df["Tanggal"].dt.date
            == tanggal

        ]

    st.divider()

    # ======================================================
    # FILTER ROLE
    # ======================================================

    if role in [

        "CSE",
        "RSE",
        "DSE",
        "FRONTLINER",
        "PROMOTOR"

    ]:

        df = df[
            df["Input By"] == user
        ]

    elif role == "BSM":

        bawahan = df_user[

            df_user["ATASAN"] == user

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(bawahan)
        ]

    elif role == "HOS":

        daftar_bsm = df_user[

            df_user["ATASAN"] == user

        ]["USER"].tolist()

        bawahan = df_user[

            df_user["ATASAN"]
            .isin(daftar_bsm)

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(bawahan)
        ]

    # ======================================================
    # KPI KHUSUS INPUT CSE/RSE
    # ======================================================

    cse_user = df_user[

        df_user["ROLE"]
        .isin([
            "CSE",
            "RSE"
        ])

    ]["USER"].tolist()

    # ======================================================
    # DATA INPUT CSE/RSE
    # ======================================================

    df_cse = df[

        df["Input By"]
        .isin(cse_user)

    ]

    # ======================================================
    # KPI
    # ======================================================

    jumlah_user = (
        df_cse["Input By"]
        .nunique()
    )

    jumlah_outlet = (
        df_cse["ID Outlet"]
        .nunique()
    )

    jumlah_msisdn = len(
        df_cse
    )

    jumlah_biometrik = (
        df_cse["Biometrik"]
        .sum()
    )

    # ======================================================
    # KPI UI
    # ======================================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(

        "👤 CSE/RSE Aktif",

        jumlah_user

    )

    col2.metric(

        "🏪 Outlet",

        jumlah_outlet

    )

    col3.metric(

        "📱 MSISDN",

        jumlah_msisdn

    )

    col4.metric(

        "✅ Biometrik",

        jumlah_biometrik

    )

    st.divider()
    # ======================================================
    # CSE / RSE
    # ======================================================

    if role in [

        "CSE",
        "RSE",
        "DSE",
        "FRONTLINER",
        "PROMOTOR"

    ]:

        st.subheader(
            "📋 Detail Input"
        )

        detail_df = df[[

            "Nama Outlet",
            "ID Outlet",
            "MSISDN",
            "Biometrik",
            "Tanggal"

        ]]

        show_grid(detail_df)

    # ======================================================
    # BSM
    # ======================================================

    elif role == "BSM":

        st.subheader(
            "📋 Rekap CSE/RSE"
        )

        summary = (

            df

            .groupby("Input By")

            .agg(

                Outlet=(
                    "ID Outlet",
                    "nunique"
                ),

                MSISDN=(
                    "MSISDN",
                    "count"
                ),

                Biometrik=(
                    "Biometrik",
                    "sum"
                )

            )

            .reset_index()

            .rename(

                columns={
                    "Input By": "CSE/RSE"
                }

            )

            .sort_values(

                "MSISDN",

                ascending=False

            )

        )

        show_grid(summary)

    # ======================================================
    # HOS
    # ======================================================

    elif role == "HOS":

        # ==================================================
        # REKAP BSM
        # ==================================================

        st.subheader(
            "📋 Rekap BSM"
        )

        daftar = []

        daftar_bsm = df_user[

            df_user["ATASAN"] == user

        ]["USER"].tolist()

        for bsm in daftar_bsm:

            bawahan = df_user[

                (df_user["ATASAN"] == bsm)

                &

                (df_user["ROLE"].isin([

                    "CSE",
                    "RSE"

                ]))

            ]["USER"].tolist()

            temp = df[

                df["Input By"]
                .isin(bawahan)

            ]

            daftar.append({

                "BSM": bsm,

                "CSE/RSE":
                    temp["Input By"]
                    .nunique(),

                "CSE/RSE Aktif":
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
            daftar
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

        # ==================================================
        # REKAP CSE
        # ==================================================

        st.subheader(
            "📋 Rekap CSE/RSE"
        )

        rekap_cse = []

        for bsm in daftar_bsm:

            bawahan = df_user[

                df_user["ATASAN"] == bsm

            ]

            for _, row in bawahan.iterrows():

                user_cse = row["USER"]

                temp = df[

                    df["Input By"]
                    == user_cse

                ]

                rekap_cse.append({

                    "CSE/RSE":
                        user_cse,

                    "Branch":
                        bsm,

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

                    ["MSISDN"],

                    ascending=False

                )

            )

        show_grid(summary_cse)

    # ======================================================
    # ADMIN
    # ======================================================

    else:

        # ==================================================
        # REKAP HOS
        # ==================================================

        st.subheader(
            "📋 Rekap HoS"
        )

        rekap_hos = []

        hos_list = df_user[

            df_user["ROLE"] == "HOS"

        ]["USER"].tolist()

        for hos in hos_list:

            daftar_bsm = df_user[

                df_user["ATASAN"] == hos

            ]["USER"].tolist()

            daftar_cse = df_user[

                (df_user["ATASAN"]
                .isin(daftar_bsm))

                &

                (df_user["ROLE"].isin([

                    "CSE",
                    "RSE"

                ]))

            ]["USER"].tolist()

            temp = df[

                df["Input By"]
                .isin(daftar_cse)

            ]

            rekap_hos.append({

                "HoS": hos,

                "BSM":
                    len(daftar_bsm),

                "CSE/RSE":
                    len(daftar_cse),

                "CSE/RSE Aktif":
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

        # ==================================================
        # REKAP BRANCH
        # ==================================================

        st.subheader(
            "📋 Rekap Branch"
        )

        rekap = []

        bsm_list = df_user[

            df_user["ROLE"] == "BSM"

        ]["USER"].tolist()

        for bsm in bsm_list:

            bawahan = df_user[

                df_user["ATASAN"] == bsm

            ]["USER"].tolist()

            temp = df[

                df["Input By"]
                .isin(bawahan)

            ]

            rekap.append({

                "Branch": bsm,

                "CSE/RSE":
                     len(bawahan),

                "CSE/RSE Aktif":
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

        summary = pd.DataFrame(
            rekap
        )

        if not summary.empty:

            summary = (

                summary

                .sort_values(

                    "MSISDN",

                    ascending=False

                )

            )

        show_grid(summary)

        st.divider()

        # ==================================================
        # REKAP CSE
        # ==================================================

        st.subheader(
            "📋 Rekap CSE/RSE"
        )

        rekap_cse = []

        cse_list = df_user[

            df_user["ROLE"].isin([

                "CSE",
                "RSE"

            ])

        ]

        for _, row in cse_list.iterrows():

            user_cse = row["USER"]

            branch = row["ATASAN"]

            temp = df[

                df["Input By"]
                == user_cse

            ]

            # ==============================================
            # HANYA MASUKKAN YANG ADA INPUT
            # ==============================================

            if len(temp) > 0:

                rekap_cse.append({

                    "CSE/RSE":
                        user_cse,

                    "Branch":
                        branch,

                    # ======================================
                    # INPUT ACTIVE
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