# =========================================================
# dashboard_frontliner.py
# DASHBOARD FRONTLINER
# HOS -> BSM -> CSE/RSE -> FRONTLINER
# =========================================================

import streamlit as st
import pandas as pd

from database import (
    tampil_data,
    tampil_user
)


def show():

    st.title("📊 Dashboard Frontliner")

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

    # -------------------------
    # FRONTLINER
    # -------------------------

    if role == "FRONTLINER":

        df = df[
            df["Input By"] == user
        ]

    # -------------------------
    # CSE / RSE
    # -------------------------

    elif role in ["CSE", "RSE"]:

        daftar_fl = df_user[
            (df_user["ATASAN"] == user)
            &
            (df_user["ROLE"] == "FRONTLINER")
        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(daftar_fl)
        ]

    # -------------------------
    # BSM
    # -------------------------

    elif role == "BSM":

        daftar_cse = df_user[
            df_user["ATASAN"] == user
        ]["USER"].tolist()

        daftar_fl = df_user[
            (df_user["ATASAN"].isin(daftar_cse))
            &
            (df_user["ROLE"] == "FRONTLINER")
        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(daftar_fl)
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

        daftar_fl = df_user[
            (df_user["ATASAN"].isin(daftar_cse))
            &
            (df_user["ROLE"] == "FRONTLINER")
        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(daftar_fl)
        ]

    # ADMIN melihat semua

    # =====================================================
    # SUMMARY
    # =====================================================

    daftar_fl = df_user[
        df_user["ROLE"] == "FRONTLINER"
    ]["USER"].tolist()

    fl_aktif = df[
        df["Input By"].isin(daftar_fl)
    ]["Input By"].nunique()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "👤 Frontliner Aktif",
        fl_aktif
    )

    col2.metric(
        "🏪 Outlet",
        df["ID Outlet"].nunique()
    )

    col3.metric(
        "📱 MSISDN",
        df["MSISDN"].nunique()
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
                df_user["ATASAN"].isin(daftar_bsm)
            ]["USER"].tolist()

            daftar_fl = df_user[
                (df_user["ATASAN"].isin(daftar_cse))
                &
                (df_user["ROLE"] == "FRONTLINER")
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_fl)
            ]

            rekap_hos.append({

                "HOS": nama_hos,

                "BSM":
                    len(daftar_bsm),

                "CSE/RSE":
                    len(daftar_cse),

                "Frontliner Aktif":
                    temp["Input By"].nunique(),

                "Outlet":
                    temp["ID Outlet"].nunique(),

                "MSISDN":
                    temp["MSISDN"].nunique()

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

            daftar_cse = df_user[
                df_user["ATASAN"] == nama_bsm
            ]["USER"].tolist()

            daftar_fl = df_user[
                (df_user["ATASAN"].isin(daftar_cse))
                &
                (df_user["ROLE"] == "FRONTLINER")
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_fl)
            ]

            rekap_bsm.append({

                "BSM": nama_bsm,

                "CSE/RSE":
                    len(daftar_cse),

                "Frontliner Aktif":
                    temp["Input By"].nunique(),

                "Outlet":
                    temp["ID Outlet"].nunique(),

                "MSISDN":
                    temp["MSISDN"].nunique()

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
    # REKAP CSE/RSE
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

            daftar_fl = df_user[
                (df_user["ATASAN"] == nama_cse)
                &
                (df_user["ROLE"] == "FRONTLINER")
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_fl)
            ]

            if role != "ADMIN":

                if len(temp) == 0:
                    continue

            rekap_cse.append({

                "CSE/RSE": nama_cse,

                "Branch": row["ATASAN"],

                "Frontliner Aktif":
                    temp["Input By"].nunique(),

                "Outlet":
                    temp["ID Outlet"].nunique(),

                "MSISDN":
                    temp["MSISDN"].nunique()

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

        if role != "ADMIN":

            if nama_fl not in df["Input By"].unique():
                continue

        rekap_fl.append({

            "Frontliner": nama_fl,

            "Atasan": row["ATASAN"],

            "Outlet":
                temp["ID Outlet"].nunique(),

            "MSISDN":
                temp["MSISDN"].nunique()

        })

    summary_fl = pd.DataFrame(rekap_fl)

    if not summary_fl.empty:

        summary_fl = summary_fl.sort_values(
            "MSISDN",
            ascending=False
        )

    st.dataframe(
        summary_fl,
        use_container_width=True,
        hide_index=True
    )

    st.divider()


