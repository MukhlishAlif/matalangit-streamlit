import streamlit as st
import pandas as pd

from datetime import datetime

from database import (
    simpan_data,
    cek_msisdn
)

# =====================
# LOAD BIOMETRIK
# =====================

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


def show():

    # =====================
    # SESSION
    # =====================

    if "jumlah_msisdn" not in st.session_state:

        st.session_state.jumlah_msisdn = 1

    # =====================
    # LOAD BIOMETRIK
    # =====================

    biometrik = load_biometrik()

    tanggal_hari_ini = datetime.now().date()

    # =====================
    # FORM
    # =====================

    st.title("📝 Input Outlet")

    nama_outlet = st.text_input(
        "Nama Outlet *"
    )

    id_outlet = st.text_input(
        "ID Outlet *"
    )

    st.divider()

    st.subheader("📱 MSISDN")

    col1, col2 = st.columns(2)

    with col1:

        if st.button(

            "➕ Tambah MSISDN",

            use_container_width=True

        ):

            if st.session_state.jumlah_msisdn < 10:

                st.session_state.jumlah_msisdn += 1

                st.rerun()

    with col2:

        if st.button(

            "➖ Kurangi MSISDN",

            use_container_width=True

        ):

            if st.session_state.jumlah_msisdn > 1:

                st.session_state.jumlah_msisdn -= 1

                st.rerun()

    msisdn_list = []

    for i in range(

        st.session_state.jumlah_msisdn

    ):

        nomor = st.text_input(

            f"MSISDN {i+1}",

            key=f"msisdn_{i}",

            placeholder="628xxxxxxxxxx"

        ).strip()

        # =====================
        # CEK BIOMETRIK REALTIME
        # =====================

        if nomor != "":

            cek_bio = biometrik[

                (biometrik["msisdn"] == nomor)

                &

                (
                    biometrik["tanggal_biometrik"]

                    ==

                    tanggal_hari_ini
                )

            ]

            if not cek_bio.empty:

                st.success(
                    f"{nomor} VALID BIOMETRIK"
                )

            else:

                st.error(
                    f"{nomor} TIDAK VALID BIOMETRIK"
                )

        msisdn_list.append(
            nomor
        )

    st.divider()

    # =====================
    # SIMPAN
    # =====================

    if st.button(

        "💾 Simpan",

        use_container_width=True

    ):

        if nama_outlet == "":

            st.error(
                "Nama Outlet wajib diisi."
            )

            st.stop()

        if id_outlet == "":

            st.error(
                "ID Outlet wajib diisi."
            )

            st.stop()

        nomor_isi = [

            x for x in msisdn_list

            if x != ""

        ]

        if len(nomor_isi) == 0:

            st.error(
                "Minimal isi 1 MSISDN."
            )

            st.stop()

        # =====================
        # CEK DUPLIKAT FORM
        # =====================

        if len(nomor_isi) != len(set(nomor_isi)):

            st.error(
                "Ada MSISDN yang sama pada form."
            )

            st.stop()

        # =====================
        # VALIDASI FORMAT
        # =====================

        for nomor in nomor_isi:

            if not nomor.isdigit():

                st.error(
                    f"{nomor} hanya boleh angka."
                )

                st.stop()

            if not nomor.startswith("62"):

                st.error(
                    f"{nomor} harus diawali 62."
                )

                st.stop()

        # =====================
        # VALIDASI BIOMETRIK
        # =====================

        for nomor in nomor_isi:

            cek_bio = biometrik[

                (biometrik["msisdn"] == nomor)

                &

                (
                    biometrik["tanggal_biometrik"]

                    ==

                    tanggal_hari_ini
                )

            ]

            if cek_bio.empty:

                st.error(
                    f"""
MSISDN **{nomor}** gagal diinput.

Nomor belum biometrik hari ini.
"""
                )

                st.stop()

        # =====================
        # CEK DATABASE
        # =====================

        for nomor in nomor_isi:

            cek = cek_msisdn(nomor)

            if cek:

                st.error(
                    f"""
MSISDN **{nomor}**

Sudah pernah diinput.

Input By : **{cek['input_by']}**

Tanggal : **{cek['created_at']}**
"""
                )

                st.stop()

        # =====================
        # SIMPAN DATABASE
        # =====================

        for nomor in nomor_isi:

            simpan_data(

                nama_outlet,
                id_outlet,
                nomor,
                st.session_state.outlet_user

            )

        st.success(
            f"Berhasil menyimpan {len(nomor_isi)} MSISDN."
        )

        st.balloons()

        # =====================
        # RESET FORM
        # =====================

        st.session_state.jumlah_msisdn = 1

        for i in range(10):

            key = f"msisdn_{i}"

            if key in st.session_state:

                del st.session_state[key]

        st.rerun()