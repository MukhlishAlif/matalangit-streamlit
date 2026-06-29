from io import BytesIO
import streamlit as st
import pandas as pd

from database import (
    tampil_data,
    tampil_user,
    hapus_data,
    get_downline
)

# ===========================
# HALAMAN DATA OUTLET
# ===========================

def show():

    st.title("📋 Data Outlet")

    # ===========================
    # LOAD DATA
    # ===========================

    data = tampil_data()

    if len(data) == 0:
        st.info("Belum ada data.")
        return

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

    users = tampil_user()

    users = pd.DataFrame(
        users,
        columns=[
            "USER",
            "ROLE",
            "ATASAN"
        ]
    )

    # ===========================
    # SESSION
    # ===========================

    role = st.session_state.outlet_role
    user = st.session_state.outlet_user

    # ===========================
    # FILTER USER
    # ===========================

    if role == "ADMIN":

        list_user = ["Semua"] + sorted(
            users["USER"].tolist()
        )

    else:

        list_user = ["Semua"] + sorted(
            [user] + get_downline(user)
        )

    # ===========================
    # FILTER AKSES
    # ===========================

    if role != "ADMIN":

        akses = get_downline(user)

        if user not in akses:
            akses.append(user)

        df = df[
            df["Input By"].isin(akses)
        ]

    # ===========================
    # FILTER
    # ===========================

    col1, col2 = st.columns(2)

    with col1:

        keyword = st.text_input(
            "🔍 Cari Outlet / ID Outlet / MSISDN / User"
        )

    with col2:

        pilih_user = st.selectbox(
            "👤 Input By",
            list_user
        )

    # ===========================
    # SEARCH
    # ===========================

    if keyword:

        keyword = keyword.lower()

        df = df[
            df.astype(str)
            .apply(
                lambda x:
                x.str.lower().str.contains(keyword)
            )
            .any(axis=1)
        ]

    # ===========================
    # FILTER USER
    # ===========================

    if pilih_user != "Semua":

        df = df[
            df["Input By"] == pilih_user
        ]

    # ===========================
    # FILTER TANGGAL
    # ===========================

    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"],
        errors="coerce"
    )

    tanggal = st.date_input(
        "📅 Filter Tanggal",
        value=None
    )

    if tanggal:

        df = df[
            df["Tanggal"].dt.date == tanggal
        ]

    st.divider()

    # ===========================
    # SUMMARY
    # ===========================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "🏪 Outlet",
            df["ID Outlet"].nunique()
        )

    with col2:

        st.metric(
            "📱 MSISDN",
            df["MSISDN"].nunique()
        )

    with col3:

        st.metric(
            "👤 User",
            df["Input By"].nunique()
        )

    st.divider()

    # ===========================
    # ROLE MAP
    # ===========================

    role_map = users.set_index(
        "USER"
    )["ROLE"].to_dict()

    df["ROLE"] = df["Input By"].map(
        role_map
    )

    # ===========================
    # SPLIT ROLE
    # ===========================

    role_data = {

        "CSE_RSE": df[
            df["ROLE"].isin(
                ["CSE", "RSE"]
            )
        ],

        "DSE": df[
            df["ROLE"] == "DSE"
        ],

        "FRONTLINER": df[
            df["ROLE"] == "FRONTLINER"
        ],

        "PROMOTOR": df[
            df["ROLE"] == "PROMOTOR"
        ]

    }

    # ===========================
    # LOOP TABEL
    # ===========================

    for nama_role, temp_df in role_data.items():

        st.subheader(
            f"📋 Data {nama_role}"
        )

        # ===========================
        # DOWNLOAD
        # ===========================

        buffer = BytesIO()

        with pd.ExcelWriter(
            buffer,
            engine="openpyxl"
        ) as writer:

            temp_df.drop(
                columns=["ID", "ROLE"],
                errors="ignore"
            ).to_excel(
                writer,
                index=False
            )

        st.download_button(

            f"📥 Download {nama_role}",

            buffer.getvalue(),

            file_name=f"{nama_role}.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key=f"download_{nama_role}"

        )

        st.divider()

        # ===========================
        # JIKA TIDAK ADA DATA
        # ===========================

        if temp_df.empty:

            st.info(
                "Tidak ada data."
            )

            st.divider()

            continue

        # ===========================
        # TABEL
        # ===========================

        tampil = temp_df.copy()

        id_map = tampil["ID"]

        tampil = tampil.drop(
            columns=["ID"]
        )

        tampil["Hapus"] = False

        edited = st.data_editor(

            tampil,

            use_container_width=True,

            hide_index=True,

            disabled=[

                "Nama Outlet",
                "ID Outlet",
                "MSISDN",
                "Input By",
                "Tanggal",
                "ROLE"

            ],

            column_config={

                "Hapus":
                st.column_config.CheckboxColumn(
                    "Hapus"
                )

            },

            key=f"editor_{nama_role}"

        )

        # ===========================
        # DELETE
        # ===========================

        if role == "ADMIN":

            hapus = edited[
                edited["Hapus"]
            ]

            if not hapus.empty:

                if st.button(

                    f"🗑️ Hapus {len(hapus)} Data {nama_role}",

                    type="primary",

                    key=f"hapus_{nama_role}"

                ):

                    for idx in hapus.index:

                        hapus_data(
                            id_map.iloc[idx]
                        )

                    st.success(
                        "Data berhasil dihapus."
                    )

                    st.rerun()

        st.divider()