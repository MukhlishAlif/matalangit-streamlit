# =========================================================
# dashboard_dse.py
# DASHBOARD HIERARCHY DSE
# HOS -> BSM -> CSE/RSE -> DSE
# =========================================================

import streamlit as st
import pandas as pd

from database import (
    tampil_data,
    tampil_user
)

@st.cache_data
def load_biometrik():

    biometrik = pd.read_csv(
        "ga_biometrics_cj.csv",
        dtype=str,
        low_memory=False
    )

    biometrik.columns = biometrik.columns.str.strip().str.lower()

    biometrik["msisdn"] = (
        biometrik["msisdn"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return set(
        biometrik["msisdn"]
    )

def show():

    st.title("📊 Dashboard DSE")

    # =====================================================
    # LOAD DATA
    # =====================================================

    data = tampil_data()
    users = tampil_user()

    if len(data) == 0:
        st.info("Belum ada data.")
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
    # CEK BIOMETRIK
    # =====================================================

    biometrik_set = load_biometrik()

    df["MSISDN"] = (
        df["MSISDN"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["Biometrik"] = df["MSISDN"].isin(
        biometrik_set
    )
    df_user = pd.DataFrame(
        users,
        columns=[
            "USER",
            "ROLE",
            "ATASAN"
        ]
    )

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
        key="dse_tanggal"
    )

    if tanggal:

        df = df[
            df["Tanggal"].dt.date == tanggal
        ]

    st.divider()

    # =====================================================
    # FILTER ROLE
    # =====================================================

    # -------------------------
    # DSE / FRONTLINER
    # -------------------------

    if role in ["DSE", "PROMOTOR", "FRONTLINER"]:

        df = df[
            df["Input By"] == user
        ]

    # -------------------------
    # CSE / RSE
    # -------------------------

    elif role in ["CSE", "RSE"]:

        daftar_dse = df_user[
            df_user["ATASAN"] == user
        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(daftar_dse)
        ]

    # -------------------------
    # BSM
    # -------------------------

    elif role == "BSM":

        daftar_cse = df_user[
            df_user["ATASAN"] == user
        ]["USER"].tolist()

        daftar_dse = df_user[
            df_user["ATASAN"].isin(daftar_cse)
        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(daftar_dse)
        ]

    # -------------------------
    # HOS
    # -------------------------

    elif role == "HOS":

        daftar_bsm = df_user[
            df_user["ATASAN"] == user
        ]["USER"].tolist()

        daftar_cse = df_user[
            df_user["ATASAN"].isin(daftar_bsm)
        ]["USER"].tolist()

        daftar_dse = df_user[
            df_user["ATASAN"].isin(daftar_cse)
        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(daftar_dse)
        ]

    # ADMIN melihat semua

    # =====================================================
    # SUMMARY
    # =====================================================

    # semua user role DSE
    dse_user = df_user[
        df_user["ROLE"].isin(
            [
                "DSE"
            ]
        )
    ]

    # total DSE
    total_dse = len(dse_user)

    col1, col2, col3 = st.columns(3)

    # =====================================================
    # DSE AKTIF
    # =====================================================

    daftar_dse = df_user[
        df_user["ROLE"] == "DSE"
    ]["USER"].tolist()

    dse_aktif = df[
        df["Input By"].isin(daftar_dse)
    ]["Input By"].nunique()

    col1.metric(
        "👤 DSE Aktif",
        dse_aktif
    )
    col2.metric(
        "🏪 Outlet",
        df["ID Outlet"].nunique()
    )

    col3.metric(
        "📱 MSISDN",
        df["MSISDN"].nunique()
    )

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

            # Semua BSM milik HOS
            daftar_bsm = df_user[
                df_user["ATASAN"] == nama_hos
            ]["USER"].tolist()

            # Semua CSE milik BSM
            daftar_cse = df_user[
                df_user["ATASAN"].isin(daftar_bsm)
            ]["USER"].tolist()

            # Semua DSE milik CSE
            daftar_dse = df_user[
                df_user["ATASAN"].isin(daftar_cse)
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_dse)
            ]

            rekap_hos.append({

                "HOS": nama_hos,

                "BSM":
                    len(daftar_bsm),

                "CSE/RSE":
                    len(daftar_cse),

                "DSE Aktif":
                    temp["Input By"].nunique(),

                "Outlet":
                    temp["ID Outlet"].nunique(),

                "MSISDN":
                    len(temp),

                "Biometrik H-1":
                    temp["Biometrik"].sum()

            })

        summary_hos = pd.DataFrame(rekap_hos)

        if not summary_hos.empty:

            summary_hos = summary_hos.sort_values(
                "MSISDN",
                ascending=False
            )

        st.dataframe(
            summary_hos,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

    # =====================================================
    # REKAP BSM
    # =====================================================

    if role in ["HOS", "ADMIN"]:

        st.subheader("📋 Rekap BSM")

        rekap_bsm = []

        bsm_list = df_user[
            df_user["ROLE"] == "BSM"
        ]

        for _, row in bsm_list.iterrows():

            nama_bsm = row["USER"]

            # Semua CSE milik BSM
            daftar_cse = df_user[
                df_user["ATASAN"] == nama_bsm
            ]["USER"].tolist()

            # Semua DSE milik CSE
            daftar_dse = df_user[
                df_user["ATASAN"].isin(daftar_cse)
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_dse)
            ]

            if role != "ADMIN":

                if len(temp) == 0:
                    continue

            rekap_bsm.append({

                "BSM": nama_bsm,

                "CSE/RSE":
                    len(daftar_cse),

                "DSE Aktif":
                    temp["Input By"].nunique(),

                "Outlet":
                    temp["ID Outlet"].nunique(),

                "MSISDN":
                    len(temp),

                "Biometrik H-1":
                    temp["Biometrik"].sum()

            })

        summary_bsm = pd.DataFrame(rekap_bsm)

        if not summary_bsm.empty:

            summary_bsm = summary_bsm.sort_values(
                "MSISDN",
                ascending=False
            )

        st.dataframe(
            summary_bsm,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

    # =====================================================
    # REKAP CSE / RSE
    # =====================================================

    if role in ["BSM", "HOS", "ADMIN"]:

        st.subheader("📋 Rekap CSE/RSE")

        rekap_cse = []

        cse_list = df_user[
            df_user["ROLE"].isin(
                ["CSE", "RSE"]
            )
        ]

        for _, row in cse_list.iterrows():

            nama_cse = row["USER"]

            # Semua DSE milik CSE
            daftar_dse = df_user[
                df_user["ATASAN"] == nama_cse
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_dse)
            ]

            if role != "ADMIN":

                if len(temp) == 0:
                    continue

            rekap_cse.append({

                "CSE/RSE": nama_cse,

                "Branch": row["ATASAN"],

                "DSE Aktif":
                    temp["Input By"].nunique(),

                "Outlet":
                    temp["ID Outlet"].nunique(),

                "MSISDN":
                    len(temp),

                "Biometrik H-1":
                    temp["Biometrik"].sum()

            })

        summary_cse = pd.DataFrame(rekap_cse)

        if not summary_cse.empty:

            summary_cse = summary_cse.sort_values(
                "MSISDN",
                ascending=False
            )

        st.dataframe(
            summary_cse,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

    # =====================================================
    # REKAP DSE
    # =====================================================

    st.subheader("📋 Rekap DSE")

    rekap_dse = []

    dse_user = df_user[
        df_user["ROLE"].isin(
            [
                "DSE"
            ]
        )
    ]

    for _, row in dse_user.iterrows():

        nama_dse = row["USER"]

        temp = df[
            df["Input By"] == nama_dse
        ]

        if role != "ADMIN":

            if nama_dse not in df["Input By"].unique():
                continue

        rekap_dse.append({

            "DSE": nama_dse,

            "Atasan": row["ATASAN"],

            "Outlet":
                temp["ID Outlet"].nunique(),

            "MSISDN":
                len(temp),

            "Biometrik H-1":
                temp["Biometrik"].sum()

        })

    summary_dse = pd.DataFrame(rekap_dse)

    if not summary_dse.empty:

        summary_dse = summary_dse.sort_values(
            "MSISDN",
            ascending=False
        )

    st.dataframe(
        summary_dse,
        use_container_width=True,
        hide_index=True
    )