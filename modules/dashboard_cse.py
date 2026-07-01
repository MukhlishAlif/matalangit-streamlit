import streamlit as st
import pandas as pd

from database import tampil_data, tampil_user

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

    biometrik.columns = biometrik.columns.str.strip().str.lower()

    biometrik["msisdn"] = (
        biometrik["msisdn"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return set(biometrik["msisdn"])

def hapus_data(id_data):

    cursor.execute("""
        DELETE FROM outlet
        WHERE id=?
    """, (id_data,))

    conn.commit()

def show():

    st.title("📊 Dashboard ")

    # ===========================
    # LOAD DATA
    # ===========================

    data = tampil_data()
    users = tampil_user()

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
    # CEK BIOMETRIK
    # ===========================

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
        key="cse_tanggal"
    )

    if tanggal:

        df = df[
            df["Tanggal"].dt.date == tanggal
        ]

    st.divider()

    # ===========================
    # FILTER ROLE
    # ===========================

    if role in ["CSE", "RSE", "DSE", "FRONTLINER", "PROMOTOR"]:

        df = df[df["Input By"] == user]

    elif role == "BSM":

        bawahan = df_user[
            df_user["ATASAN"] == user
        ]["USER"].tolist()

        df = df[df["Input By"].isin(bawahan)]

    elif role == "HOS":

        daftar_bsm = df_user[
            df_user["ATASAN"] == user
        ]["USER"].tolist()

        bawahan = df_user[
            df_user["ATASAN"].isin(daftar_bsm)
        ]["USER"].tolist()

        df = df[df["Input By"].isin(bawahan)]

    # ADMIN melihat semua data

    # ===========================
    # SUMMARY
    # ===========================

    if role == "HOS":

        jumlah_bsm = len(
            df_user[
                df_user["ATASAN"] == user
            ]
        )

        jumlah_cse = df["Input By"].nunique()

        col1, col2, col3 = st.columns(3)

        
        col1.metric("👤 CSE/RSE Aktif", jumlah_cse)
        col2.metric("🏪 Outlet", df["ID Outlet"].nunique())
        col3.metric("📱 MSISDN", len(df))

    else:

        jumlah_user = df["Input By"].nunique()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "👤 CSE/RSE Aktif",
            jumlah_user
        )

        col2.metric(
            "🏪 Outlet",
            df["ID Outlet"].nunique()
        )

        col3.metric(
            "📱 MSISDN",
            len(df)
        )

    st.divider()

    # ===========================
    # REKAP
    # ===========================

    if role in ["CSE", "RSE", "DSE", "FRONTLINER", "PROMOTOR"]:

        st.info("Dashboard hanya menampilkan ringkasan untuk CSE/RSE.")

    elif role == "BSM":

        summary = (
            df.groupby("Input By")
            .agg(
                Outlet=("ID Outlet", "nunique"),
                MSISDN=("MSISDN", "count"),
                Biometrik=("Biometrik", "sum")
            )
            .reset_index()
            .sort_values(
                "MSISDN",
                ascending=False
            )
        )
        st.subheader("📋 Rekap CSE/RSE")

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True
        )

    elif role == "HOS":

        daftar = []

        daftar_bsm = df_user[
            df_user["ATASAN"] == user
        ]["USER"].tolist()

        for bsm in daftar_bsm:

            bawahan = df_user[
                df_user["ATASAN"] == bsm
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(bawahan)
            ]

            daftar.append({

                "BSM": bsm,

                "CSE/RSE Aktif":
                    temp["Input By"].nunique(),

                "Outlet":
                    temp["ID Outlet"].nunique(),

                "MSISDN":
                    len(temp),

                "Biometrik H-1":
                    temp["Biometrik"].sum()

            })

        st.subheader("📋 Rekap BSM")

        summary_bsm = pd.DataFrame(daftar)

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

        st.subheader("📋 Rekap CSE/RSE")

        rekap_cse = []

        for bsm in daftar_bsm:

            bawahan = df_user[
                df_user["ATASAN"] == bsm
            ]

            for _, row in bawahan.iterrows():

                user_cse = row["USER"]

                temp = df[
                    df["Input By"] == user_cse
                ]

                rekap_cse.append({

                    "CSE/RSE": user_cse,

                    "Branch": bsm,

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
                ["MSISDN", "Outlet"],
                ascending=False
            )

        st.dataframe(
            summary_cse,
            use_container_width=True,
            hide_index=True
        )

    else:

        
        # ===========================
        # REKAP HOS
        # ===========================

        st.subheader("📋 Rekap HoS")

        rekap_hos = []

        hos_list = df_user[
            df_user["ROLE"] == "HOS"
        ]["USER"].tolist()

        for hos in hos_list:

            # Semua BSM milik HoS
            daftar_bsm = df_user[
                df_user["ATASAN"] == hos
            ]["USER"].tolist()

            # Semua CSE/RSE milik HoS
            daftar_cse = df_user[
                df_user["ATASAN"].isin(daftar_bsm)
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_cse)
            ]

            rekap_hos.append({

                "HoS": hos,

                "BSM":
                    len(daftar_bsm),

                "CSE/RSE":
                    len(daftar_cse),

                "CSE/RSE Aktif":
                    temp["Input By"].nunique(),

                "Outlet":
                    temp["ID Outlet"].nunique(),

                "MSISDN":
                    len(temp),

                "Biometrik H-1":
                    temp["Biometrik"].sum()

            })
        summary_hos = pd.DataFrame(rekap_hos)

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
                
        
        st.subheader("📋 Rekap Branch")

        rekap = []

        # Semua BSM
        bsm_list = df_user[
            df_user["ROLE"] == "BSM"
        ]["USER"].tolist()

        for bsm in bsm_list:

            # Semua bawahan BSM
            bawahan = df_user[
                df_user["ATASAN"] == bsm
            ]["USER"].tolist()

            # Data input bawahan
            temp = df[
                df["Input By"].isin(bawahan)
            ]

            rekap.append({

                "Branch": bsm,

                "CSE/RSE":
                    len(bawahan),

                "CSE/RSE Aktif":
                    temp["Input By"].nunique(),

                "Outlet":
                    temp["ID Outlet"].nunique(),

                "MSISDN":
                    len(temp),

                "Biometrik H-1":
                    temp["Biometrik"].sum()

            })
        summary = pd.DataFrame(rekap)

        if not summary.empty:
            summary = summary.sort_values(
                "MSISDN",
                ascending=False
            )

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # ===========================
        # REKAP CSE/RSE
        # ===========================

        st.subheader("📋 Rekap CSE/RSE")

        rekap_cse = []

        # Semua CSE dan RSE
        cse_list = df_user[
            df_user["ROLE"].isin(["CSE", "RSE"])
        ]

        for _, row in cse_list.iterrows():

            user_cse = row["USER"]
            branch = row["ATASAN"]

            temp = df[
                df["Input By"] == user_cse
            ]

            rekap_cse.append({

                "CSE/RSE": user_cse,

                "Branch": branch,

                "Outlet":
                    temp["ID Outlet"].nunique(),

                "MSISDN":
                    len(temp),

                "Biometrik H-1":
                    temp["Biometrik"].sum()

            })
        summary_cse = pd.DataFrame(rekap_cse)

        summary_cse = summary_cse.sort_values(
            ["MSISDN", "Outlet"],
            ascending=False
        )

        st.dataframe(
            summary_cse,
            use_container_width=True,
            hide_index=True
        )
