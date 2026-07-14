from io import BytesIO
import streamlit as st
import pandas as pd

from database import (
    tampil_data_by_date,
    tampil_data,
    tampil_user,
    get_latest_data_date,
    hapus_data,
    get_downline
)

# ===========================
# LOAD BIOMETRIK
# ===========================

import requests
import pandas as pd
import streamlit as st


@st.cache_data
def load_biometrik():

    # ===========================
    # URL JSON
    # ===========================

    url = "https://api.matalangit.cloud/bio/fetch-derfrtgty"

    # ===========================
    # REQUEST
    # ===========================

    response = requests.get(url)

    data = response.json()

    # ===========================
    # DATAFRAME
    # ===========================

    biometrik = pd.json_normalize(data["data"])

    # ===========================
    # CLEAN COLUMN
    # ===========================

    biometrik.columns = (
        biometrik.columns
        .str.strip()
        .str.lower()
    )

    # ===========================
    # CLEAN MSISDN
    # ===========================

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

        dayfirst=True,

        errors="coerce"

    )

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
    # TENTUKAN TANGGAL DULU, SEBELUM LOAD DATA
    # ===========================

    col_tgl1, col_tgl2 = st.columns([4, 1])

    with col_tgl1:

        tanggal = st.date_input(
            "📅 Filter Tanggal",
            value=None,
            key="msisdn_tanggal"
        )

    with col_tgl2:

        st.markdown("<br>", unsafe_allow_html=True)

        semua_tanggal = st.toggle(
            "Semua",
            value=True,           # <-- default ON, karena ini master data
            key="msisdn_semua_tanggal"
        )

    # ===========================
    # LOAD DATA
    # ===========================
    # Default: SEMUA tanggal (ini halaman master MSISDN untuk
    # kelola/hapus data, jadi wajar defaultnya lihat semua histori).
    # Kalau user matikan toggle "Semua" dan pilih tanggal tertentu,
    # baru difilter ke tanggal itu saja.
    # ===========================

    if semua_tanggal or tanggal is None:

        data = tampil_data()

    else:

        data = tampil_data_by_date(tanggal, tanggal)

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
            "Tanggal",
            "flag_bio"
        ]
    )


    df["Biometrik H-1"] = (

        df["flag_bio"]

        .fillna(False)
        .astype(bool)

        .map(

            {

                True: "Valid",

                False: "Unvalid"

            }

        )

    )


    users = tampil_user()

    users = pd.DataFrame(
        users,
        columns=[
            "user",
            "role",
            "atasan",
            "real_name"
        ]
    )

    users.columns = (
        users.columns.str.upper()
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
    # SUMMARY KPI (ROLE AWARE)
    # ===========================

    total_data = len(df)

    total_outlet = df["ID Outlet"].nunique()
    total_msisdn = df["MSISDN"].nunique()

    # ===========================
    # USER AKTIF (ROLE AWARE)
    # ===========================

    if role == "ADMIN":

        # =======================
        # TOTAL USER
        # =======================

        total_cse = len(

            users[

                users["ROLE"].isin([

                    "BSM", 
                    "CSE",
                    "RSE"

                ])

            ]

        )

        total_dse = len(

            users[

                users["ROLE"].isin([

                    "DSE",
                    "PROMOTOR",
                    "GSE",
                    "RGE",
                    "FRONTLINER",
                    "GEMINI"

                ])

            ]

        )

        total_user_all = (

            total_cse

            +

            total_dse

        )

        # =======================
        # USER AKTIF
        # =======================

        aktif_cse = df[

            df["Input By"].isin(

                users[

                    users["ROLE"].isin([

                        "BSM",
                        "CSE",
                        "RSE"

                    ])

                ]["USER"].tolist()

            )

        ]["Input By"].nunique()

        aktif_dse = df[

            df["Input By"].isin(

                users[

                    users["ROLE"].isin([

                        "DSE",
                        "PROMOTOR",
                        "GSE",
                        "RGE",
                        "FRONTLINER",
                        "GEMINI"

                    ])

                ]["USER"].tolist()

            )

        ]["Input By"].nunique()

        total_user = (

            aktif_cse

            +

            aktif_dse

        )

    elif role == "HOS":

        # =======================
        # GET BSM
        # =======================

        daftar_bsm = users[

            (users["ATASAN"] == user)

            &

            (users["ROLE"] == "BSM")

        ]["USER"].tolist()

        # =======================
        # GET CSE/RSE
        # =======================

        daftar_cse = users[

            (users["ATASAN"].isin(
                daftar_bsm
            ))

            &

            (users["ROLE"].isin([

                "CSE",
                "RSE"

            ]))

        ]["USER"].tolist()

        # =======================
        # GET DSE/PM/FL
        # =======================

        daftar_dse = users[

            (users["ATASAN"].isin(
                daftar_cse
            ))

            &

            (users["ROLE"].isin([

                "DSE",
                "PROMOTOR",
                "GSE",
                "RGE",
                "FRONTLINER",
                "GEMINI"

            ]))

        ]["USER"].tolist()

        total_user_all = (

            len(daftar_cse)

            +

            len(daftar_dse)

        )

        aktif_cse = df[

            df["Input By"].isin(
                daftar_cse
            )

        ]["Input By"].nunique()

        aktif_dse = df[

            df["Input By"].isin(
                daftar_dse
            )

        ]["Input By"].nunique()

        total_user = (

            aktif_cse

            +

            aktif_dse

        )

    elif role == "BSM":

        # =======================
        # GET CSE/RSE
        # =======================

        daftar_cse = users[

            (users["ATASAN"] == user)

            &

            (users["ROLE"].isin([

                "BSM",
                "CSE",
                "RSE"

            ]))

        ]["USER"].tolist()

        # =======================
        # GET DSE/PM/FL
        # =======================

        daftar_dse = users[

            (users["ATASAN"].isin(
                daftar_cse
            ))

            &

            (users["ROLE"].isin([

                "DSE",
                "PROMOTOR",
                "GSE",
                "RGE",
                "FRONTLINER",
                "GEMINI"

            ]))

        ]["USER"].tolist()

        total_user_all = (

            len(daftar_cse)

            +

            len(daftar_dse)

        )

        aktif_cse = df[

            df["Input By"].isin(
                daftar_cse
            )

        ]["Input By"].nunique()

        aktif_dse = df[

            df["Input By"].isin(
                daftar_dse
            )

        ]["Input By"].nunique()

        total_user = (

            aktif_cse

            +

            aktif_dse

        )

    elif role in [

        "CSE",
        "RSE"

    ]:

        # =======================
        # GET DSE/PM/FL
        # =======================

        daftar_dse = users[

            (users["ATASAN"] == user)

            &

            (users["ROLE"].isin([

                "DSE",
                "PROMOTOR",
                "GSE",
                "RGE",
                "FRONTLINER",
                "GEMINI"

            ]))

        ]["USER"].tolist()

        total_user_all = (

            1

            +

            len(daftar_dse)

        )

        # =======================
        # CSE ITU SENDIRI AKTIF
        # =======================

        aktif_cse = 1 if len(df) > 0 else 0

        aktif_dse = df[

            df["Input By"].isin(
                daftar_dse
            )

        ]["Input By"].nunique()

        total_user = (

            aktif_cse

            +

            aktif_dse

        )

    else:

        total_user_all = 1
        total_user = 1 if len(df) > 0 else 0

    # ===========================
    # KPI LAIN
    # ===========================

    total_data = len(df)

    total_outlet = df["ID Outlet"].nunique()

    total_msisdn = df["MSISDN"].nunique()

    total_biometrik = (

        df["Biometrik H-1"] == "Valid"

    ).sum()

    # ===========================
    # PERSENTASE
    # ===========================

    persen_user_aktif = round(

        (
            total_user / total_user_all
        ) * 100,

        2

    ) if total_user_all > 0 else 0

    persen_biometrik = round(

        (
            total_biometrik / total_data
        ) * 100,

        2

    ) if total_data > 0 else 0

    st.divider()

    # ===========================
    # ROLE MAP
    # ===========================

    role_map = (
        users
        .drop_duplicates(subset="USER")
        .set_index("USER")["ROLE"]
        .to_dict()
    )

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

        "BSM": df[
            df["ROLE"] == "BSM"
        ],

        "DSE": df[
            df["ROLE"] == "DSE"
        ],

        "FRONTLINER": df[
            df["ROLE"] == "FRONTLINER"
        ],

        "PROMOTOR": df[
            df["ROLE"] == "PROMOTOR"
        ],

        "GSE": df[
            df["ROLE"] == "GSE"
        ],

        "GEMINI": df[
            df["ROLE"] == "GEMINI"
        ],

        "RGE": df[
            df["ROLE"] == "RGE"
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

        tampil["Hapus"] = False

        edited = st.data_editor(
            tampil,
            use_container_width=True,
            hide_index=True,
            disabled=[
                "ID",
                "Nama Outlet",
                "ID Outlet",
                "MSISDN",
                "Input By",
                "Tanggal",
                "ROLE",
                "Biometrik H-1"
            ],
            column_config={

                "ID": st.column_config.NumberColumn(
                    "ID",
                    width="small"
                ),

                "Hapus": st.column_config.CheckboxColumn(
                    "Hapus"
                )

            },
            column_order=[
                "Hapus",
                "Nama Outlet",
                "ID Outlet",
                "MSISDN",
                "Input By",
                "Tanggal",
                "Tanggal Biometrik",
                "Biometrik H-1",
                "ROLE",
                "ID"
            ],
            key=f"editor_{nama_role}"
        )
        st.divider()
        # ===========================
        # DELETE
        # ===========================

        hapus = edited[
            edited["Hapus"]
        ]

        if not hapus.empty:

            st.warning(
                f"⚠️ {len(hapus)} data dipilih untuk dihapus."
            )

            if st.button(
                "🗑️ HAPUS DATA",
                type="primary",
                key=f"hapus_btn_{nama_role}"
            ):

                deleted = 0
                gagal = 0

                progress = st.progress(0)

                for i, id_data in enumerate(hapus["ID"]):

                    try:

                        hasil = hapus_data(
                            int(id_data)
                        )

                        if hasil > 0:

                            deleted += 1

                        else:

                            gagal += 1

                    except Exception as e:

                        gagal += 1

                        st.error(
                            f"ID {id_data} gagal dihapus: {e}"
                        )

                    progress.progress(
                        (i + 1) / len(hapus)
                    )

                progress.empty()

                if deleted > 0:

                    st.success(
                        f"✅ Berhasil menghapus {deleted} data."
                    )

                    st.toast(
                        f"🗑️ {deleted} data berhasil dihapus!"
                    )

                    st.cache_data.clear()

                    st.rerun()

                if gagal > 0:

                    st.error(
                        f"❌ {gagal} data gagal dihapus."
                    )