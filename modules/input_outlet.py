# =====================
# LOAD BIOMETRIK
# =====================

import requests
import pandas as pd
import streamlit as st

from database import ( simpan_data, cek_msisdn )

@st.cache_data
def load_biometrik():

    # =====================
    # API URL
    # =====================

    url = "https://api.matalangit.cloud/bio/fetch-derfrtgty"

    # =====================
    # REQUEST
    # =====================

    response = requests.get(url)

    data = response.json()

    # =====================
    # DATAFRAME
    # =====================

    biometrik = pd.json_normalize(
        data["data"]
    )

    # =====================
    # CLEAN COLUMN
    # =====================

    biometrik.columns = (

        biometrik.columns

        .str.strip()

        .str.lower()

    )

    # =====================
    # CLEAN MSISDN
    # =====================

    biometrik["msisdn"] = (

        biometrik["msisdn"]

        .fillna("")

        .astype(str)

        .str.strip()

    )

    # =====================
    # FORMAT TANGGAL
    # =====================

    biometrik["ga_dt"] = pd.to_datetime(

        biometrik["ga_dt"],

        dayfirst=True,

        errors="coerce"

    )

    return biometrik


# =====================
# HALAMAN INPUT
# =====================

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

    # =====================
    # FORM
    # =====================

    st.title("Input Outlet")

    # =====================
    # ROLE
    # =====================

    role = st.session_state.outlet_role

    # =====================
    # KHUSUS AE & GSE
    # =====================

    if role in ["AE", "GSE"]:

        nama_outlet = "-"
        id_outlet = "-"

    else:

        nama_outlet = st.text_input(
            "Nama Outlet *"
        )

        id_outlet = st.text_input(
            "ID Outlet *"
        )

    st.divider()

    st.subheader("📱 MSISDN")

    col1, col2 = st.columns(2)

    # =====================
    # TAMBAH
    # =====================

    with col1:

        if st.button("➕ Tambah MSISDN", use_container_width=True):

            if st.session_state.jumlah_msisdn < 10:
                st.session_state.jumlah_msisdn += 1
                st.rerun()

    # =====================
    # KURANGI
    # =====================

    with col2:

        if st.button("➖ Kurangi MSISDN", use_container_width=True):

            if st.session_state.jumlah_msisdn > 1:
                st.session_state.jumlah_msisdn -= 1
                st.rerun()

    # =====================
    # INPUT MSISDN
    # =====================

    msisdn_list = []

    for i in range(st.session_state.jumlah_msisdn):

        nomor = st.text_input(
            f"MSISDN {i+1}",
            key=f"msisdn_{i}",
            placeholder="628xxxxxxxxxx"
        ).strip()
        msisdn_list.append(nomor)
 


    st.divider()

    # =====================
    # SIMPAN
    # =====================

    if st.button("💾 Simpan", use_container_width=True):

        # =====================
        # VALIDASI OUTLET
        # =====================

        if role not in ["AE", "GSE"]:

            if nama_outlet == "":
                st.error("Nama Outlet wajib diisi.")
                st.stop()

            if id_outlet == "":
                st.error("ID Outlet wajib diisi.")
                st.stop()

        # =====================
        # FILTER NOMOR ISI
        # =====================

        nomor_isi = [

            str(x).strip()

            for x in msisdn_list

            if str(x).strip() != ""

        ]

        if len(nomor_isi) == 0:
            st.error("Minimal isi 1 MSISDN.")
            st.stop()

        # =====================
        # DUPLIKAT FORM
        # =====================

        if len(nomor_isi) != len(set(nomor_isi)):
            st.error("Ada MSISDN yang sama pada form.")
            st.stop()

        # =====================
        # VALIDASI FORMAT
        # =====================

        for nomor in nomor_isi:

            if not nomor.isdigit():
                st.error(f"{nomor} hanya boleh angka.")
                st.stop()

            if not nomor.startswith("62"):
                st.error(f"{nomor} harus diawali 62.")
                st.stop()

        # =====================
        # CEK DB + GA BIOMETRIK (FINAL LOGIC)
        # =====================

        sudah_input_db = []
        valid_input = []

        for nomor in nomor_isi:

            # 1. CEK DATABASE
            cek = cek_msisdn(nomor)

            if cek:

                sudah_input_db.append({
                    "msisdn": nomor,
                    "input_by": cek["input_by"],
                    "created_at": cek["created_at"]
                })
                continue
            # 3. AMAN
            valid_input.append(nomor)

        # =====================
        # OUTPUT DB DUPLICATE
        # =====================

        if sudah_input_db:

            for item in sudah_input_db:

                st.error(
                    f"""
MSISDN **{item['msisdn']}**

Sudah pernah diinput.

Input By : **{item['input_by']}**
Tanggal : **{item['created_at']}**
"""
                )

            st.stop()

        # =====================
        # STOP JIKA TIDAK ADA YANG VALID
        # =====================

        if len(valid_input) == 0:
            st.error("Tidak ada MSISDN yang bisa disimpan.")
            st.stop()

        # =====================
        # SIMPAN DATABASE
        # =====================

        for nomor in valid_input:

            simpan_data(
                nama_outlet,
                id_outlet,
                nomor,
                st.session_state.outlet_user
            )

        st.success(f"Berhasil menyimpan {len(valid_input)} MSISDN.")

        # =====================
        # RESET FORM
        # =====================

        st.session_state.jumlah_msisdn = 1

        for i in range(10):
            key = f"msisdn_{i}"
            if key in st.session_state:
                del st.session_state[key]
