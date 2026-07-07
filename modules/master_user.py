# =====================================
# IMPORT
# =====================================

import streamlit as st
import pandas as pd
from database import tampil_user

from database import (
    tampil_user_master,
    tambah_user,
    update_user,
    hapus_user,
    get_user_role
)

# =====================================
# ROLE
# =====================================

ROLE_LIST = [
    "ADMIN",
    "HOS",
    "BSM",
    "CSE",
    "RSE",
    "DSE",
    "FRONTLINER",
    "AE",
    "GSE"
]


# =====================================
# ATASAN
# =====================================

def pilihan_atasan(role):

    if role == "ADMIN":
        return ["-"]

    if role == "HOS":
        return ["-"]

    if role == "BSM":
        return get_user_role("HOS")

    if role in ["CSE", "RSE"]:
        return get_user_role("BSM")

    if role in ["DSE", "FRONTLINER", "AE", "GSE"]:
        return get_user_role("CSE") + get_user_role("RSE")

    return ["-"]

# =====================================
# PAGE
# =====================================

def show():

    st.title("👥 Master User")

    if "notif" in st.session_state:

        st.success(
            st.session_state["notif"]
        )

        del st.session_state["notif"]


    rows = tampil_user_master()

    df = pd.DataFrame(
        [dict(row) for row in rows]
    )

    if rows:

        df = pd.DataFrame(
            [dict(row) for row in rows]
        )

    else:

        df = pd.DataFrame(
            columns=[
                "id",
                "user",
                "password",
                "role",
                "atasan",
                "status",
                "created_at"
            ]
        )

    tab1, tab2, tab3 = st.tabs([
        "Daftar User",
        "Tambah User",
        "Edit / Hapus"
    ])
    # =====================================
    # DAFTAR USER
    # =====================================

    with tab1:

        col1, col2 = st.columns([3, 1])

        with col1:

            keyword = st.text_input(

                "🔍 Cari Username / Role / Upline",

                key="search_user"

            )

        with col2:

            st.metric(

                "👥 Total User",

                len(df)

            )

        tampil_df = df.copy()

        if keyword:

            keyword = keyword.lower()

            tampil_df = tampil_df[

                tampil_df.astype(str)

                .apply(

                    lambda x:

                    x.str.lower().str.contains(keyword)

                )

                .any(axis=1)

            ]

        st.caption(

            f"Menampilkan {len(tampil_df)} dari {len(df)} user"

        )

        st.dataframe(

            tampil_df,

            use_container_width=True,

            hide_index=True

        )

    # =====================================
    # TAMBAH USER
    # =====================================

    with tab2:

        st.subheader("Tambah User")

        role_tambah = st.selectbox(
            "Role",
            ROLE_LIST,
            key="role_tambah"
        )

        pilihan = pilihan_atasan(role_tambah)

        user_tambah = st.text_input(
            "Username",
            key="user_tambah"
        )

        password_tambah = st.text_input(
            "Password",
            type="password",
            key="password_tambah"
        )

        atasan_tambah = st.selectbox(
            "Upline",
            pilihan,
            key="atasan_tambah"
        )

        if st.button(
            "Tambah User",
            use_container_width=True
        ):

            if user_tambah == "" or password_tambah == "":

                st.error(
                    "Username dan Password wajib diisi."
                )

            else:

                try:

                    tambah_user(
                        user_tambah,
                        password_tambah,
                        role_tambah,
                        atasan_tambah
                    )

                    st.session_state["notif"] = (
                        f"✅ User '{user_tambah}' berhasil ditambahkan."
                    )

                    st.rerun()
                except Exception as e:

                    st.error(str(e))
    # =====================================
    # EDIT / HAPUS
    # =====================================

    with tab3:

        st.subheader("Edit / Hapus User")

        if df.empty:

            st.info("Belum ada data user.")

        else:

            pilih_id = st.selectbox(
                "Pilih User",
                df["id"].tolist(),
                format_func=lambda x: df[df["id"] == x]["user"].values[0],
                key="pilih_user"
            )

            row = df[df["id"] == pilih_id].iloc[0]

            user_edit = st.text_input(
                "Username",
                value=row["user"]
            )

            password_edit = st.text_input(
                "Password",
                value=row["password"],
                type="password"
            )

            st.text_input(
                "Role",
                value=row["role"],
                disabled=True
            )

            st.text_input(
                "Upline",
                value=row["atasan"],
                disabled=True
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "💾 Update",
                    use_container_width=True
                ):

                    st.write("DEBUG ROW")
                    st.write(row.to_dict())

                    hasil = update_user(
                        row["user"],
                        user_edit,
                        password_edit,
                        row["role"],
                        row["atasan"]
                    )

                    if hasil:

                        st.session_state["notif"] = (
                            f"✏️ User '{user_edit}' berhasil diupdate."
                        )

                        st.cache_data.clear()

                        st.rerun()

                    else:

                        st.error(
                            "❌ Data tidak berhasil diupdate."
                        )
            with col2:

                if st.button(
                    "🗑 Hapus",
                    use_container_width=True,
                    type="primary"
                ):

                    hapus_user(
                        row["user"]
                    )

                    st.session_state["notif"] = (
                        f"🗑️ User '{row['user']}' berhasil dihapus."
                    )

                    st.rerun()