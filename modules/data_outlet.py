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
# LOAD BIOMETRIK
# ===========================

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

    # ===========================
    # TANGGAL BIOMETRIK
    # ===========================

    biometrik["tanggal_biometrik"] = pd.to_datetime(

        biometrik["ga_dt"],

        errors="coerce"

    ).dt.date

    return biometrik[

        [

            "msisdn",
            "tanggal_biometrik"

        ]

    ].drop_duplicates()

# ===========================
# HALAMAN DATA OUTLET
# ===========================

def show():

    st.title("📋 Data MSISDN")

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

    # ===========================
    # CEK BIOMETRIK H-1
    # ===========================

    biometrik = load_biometrik()

    df["MSISDN"] = (

        df["MSISDN"]

        .fillna("")
        .astype(str)
        .str.strip()

    )

    df["Tanggal"] = pd.to_datetime(

        df["Tanggal"],

        errors="coerce"

    ).dt.date

    df = df.merge(

        biometrik,

        left_on="MSISDN",

        right_on="msisdn",

        how="left"

    )

    df.drop(

        columns=[

            "msisdn"

        ],

        inplace=True

    )

    df.rename(

        columns={

            "tanggal_biometrik":

            "Tanggal Biometrik"

        },

        inplace=True

    )

    df["Biometrik H-1"] = (

        df["Tanggal"]

        ==

        df["Tanggal Biometrik"]

    ).map(

        {

            True: "Valid",

            False: "Unvalid"

        }

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

    col_tgl1, col_tgl2 = st.columns(

        [4, 1]

    )

    with col_tgl1:

        tanggal = st.date_input(

            "📅 Filter Tanggal",

            value=None

        )

    with col_tgl2:

        st.markdown(

            "<br>",

            unsafe_allow_html=True

        )

        semua_tanggal = st.toggle(

            "Semua",

            value=True

        )

    if not semua_tanggal and tanggal:

        df = df[

            df["Tanggal"].dt.date == tanggal

        ]
    # ===========================
    # SUMMARY KPI (DSE STYLE - 6 COL)
    # ===========================

    total_data = len(df)

    total_outlet = df["ID Outlet"].nunique()
    total_msisdn = df["MSISDN"].nunique()
    total_user = df["Input By"].nunique()

    total_biometrik = (df["Biometrik H-1"] == "YES").sum()

    total_user_all = users["USER"].nunique()

    persen_user_aktif = (
        round((total_user / total_user_all) * 100, 2)
        if total_user_all > 0 else 0
    )

    persen_biometrik = (
        round((total_biometrik / total_data) * 100, 2)
        if total_data > 0 else 0
    )

    avg_msisdn_per_user = (
        round(total_msisdn / total_user, 2)
        if total_user > 0 else 0
    )

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(
            "🏪 Outlet",
            total_outlet
        )

    with col2:
        st.metric(
            "📱 MSISDN",
            total_msisdn
        )

    with col3:
        st.metric(
            "👤 User Aktif",
            total_user
        )

    with col4:
        st.metric(
            "📊 % User Aktif",
            f"{persen_user_aktif}%"
        )

    with col5:
        st.metric(
            "✅ Biometrik",
            total_biometrik
        )

    with col6:
        st.metric(
            "📈 % Biometrik",
            f"{persen_biometrik}%"
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
                "ROLE", 
                "Biometrik H-1"

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