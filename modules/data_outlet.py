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

# ==========================================================
# CSS
# ==========================================================

def _inject_css():

    st.markdown(
        """
        <style>

        .rekap-row{
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:10px;
            background:white;
            border-radius:12px;
            padding:10px 14px;
            box-shadow:0px 2px 8px rgba(0,0,0,.05);
            margin-bottom:8px;
        }

        .rekap-left{
            display:flex;
            align-items:center;
            gap:10px;
            min-width:0;
        }

        .rekap-icon{
            flex-shrink:0;
            width:32px;
            height:32px;
            border-radius:9px;
            display:flex;
            align-items:center;
            justify-content:center;
            background:#F1F5F9;
            color:#334155;
        }

        .rekap-name{
            font-weight:700;
            font-size:14px;
            color:#111827;
            white-space:nowrap;
            overflow:hidden;
            text-overflow:ellipsis;
        }

        .rekap-stats{
            flex-shrink:0;
            display:flex;
            gap:16px;
        }

        .rekap-stat{
            text-align:center;
        }

        .rekap-stat-val{
            font-size:14px;
            font-weight:800;
            color:#111827;
            line-height:1.1;
        }

        .rekap-stat-label{
            font-size:9px;
            color:#9CA3AF;
            font-weight:700;
            text-transform:uppercase;
        }

        .mat-icon{
            font-variation-settings:'FILL' 1;
            vertical-align:middle;
            line-height:1;
        }

        </style>
        <link rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" />
        """,
        unsafe_allow_html=True
    )


def _mat_icon(name, size=16, color=None, valign=-3):

    style = f"font-size:{size}px;vertical-align:{valign}px;"

    if color:
        style += f"color:{color};"

    return f'<span class="material-symbols-outlined mat-icon" style="{style}">{name}</span>'


def _render_rekap(df, title, icon, nama_role):
    """
    Rekap ringkas 1 baris per role: icon + nama di kiri, jumlah
    Data / Valid / Unvalid di kanan. Detail (termasuk hapus data)
    ada di dalam expander.
    """

    n_data = len(df)
    n_valid = int((df["Biometrik H-1"] == "Valid").sum()) if not df.empty else 0
    n_unvalid = n_data - n_valid

    row_html = (
        '<div class="rekap-row">'
        '<div class="rekap-left">'
        f'<div class="rekap-icon">{_mat_icon(icon, size=16)}</div>'
        f'<div class="rekap-name">{title}</div>'
        '</div>'
        '<div class="rekap-stats">'
        f'<div class="rekap-stat"><div class="rekap-stat-val">{n_data}</div><div class="rekap-stat-label">Data</div></div>'
        f'<div class="rekap-stat"><div class="rekap-stat-val">{n_valid}</div><div class="rekap-stat-label">Valid</div></div>'
        f'<div class="rekap-stat"><div class="rekap-stat-val">{n_unvalid}</div><div class="rekap-stat-label">Unvalid</div></div>'
        '</div>'
        '</div>'
    )

    st.markdown(row_html, unsafe_allow_html=True)

    with st.expander(f"Lihat detail {title}"):

        # ===========================
        # DOWNLOAD
        # ===========================

        buffer = BytesIO()

        with pd.ExcelWriter(
            buffer,
            engine="openpyxl"
        ) as writer:

            df.drop(
                columns=["ID", "ROLE"],
                errors="ignore"
            ).to_excel(
                writer,
                index=False
            )

        st.download_button(

            f"Download {title}",

            buffer.getvalue(),

            file_name=f"{nama_role}.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key=f"download_{nama_role}"

        )

        if df.empty:

            st.info("Tidak ada data.")

            return

        # ===========================
        # TABEL
        # ===========================

        tampil = df.copy()

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
                "Upline",
                "Tanggal",
                "Tanggal Biometrik",
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
                "Upline",
                "Tanggal",
                "Tanggal Biometrik",
                "Biometrik H-1",
                "ROLE",
                "ID"
            ],
            key=f"editor_{nama_role}"
        )
        # ===========================
        # DELETE
        # ===========================

        hapus = edited[
            edited["Hapus"]
        ]

        if not hapus.empty:

            st.warning(
                f"{len(hapus)} data dipilih untuk dihapus."
            )

            if st.button(
                "Hapus Data",
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
                        f"Berhasil menghapus {deleted} data."
                    )

                    st.toast(
                        f"{deleted} data berhasil dihapus."
                    )

                    st.cache_data.clear()

                    st.rerun()

                if gagal > 0:

                    st.error(
                        f"{gagal} data gagal dihapus."
                    )


# ===========================
# HALAMAN DATA OUTLET
# ===========================

def show():

    _inject_css()

    st.title("Data MSISDN")

    if st.session_state.get("outlet_sync_error"):
        st.warning(st.session_state["outlet_sync_error"])

    # ===========================
    # FILTER TANGGAL
    # ===========================

    tanggal = st.date_input(

        "Filter Tanggal",

        value=(),

        key="msisdn_tanggal"

    )

    # ===========================
    # LOAD DATA
    # ===========================

    if isinstance(tanggal, tuple):

        if len(tanggal) == 0:

            data = tampil_data()

        elif len(tanggal) == 1:

            data = tampil_data_by_date(

                tanggal[0],

                tanggal[0]

            )

        else:

            data = tampil_data_by_date(

                tanggal[0],

                tanggal[1]

            )

    else:

        data = tampil_data_by_date(

            tanggal,

            tanggal

        )

    if len(data) == 0:

        st.info(

            "Belum ada data."

        )

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
            "flag_bio",
            "ga_dt"
        ]
    )

    # ===========================
    # TANGGAL INPUT -- buang jam/menit/detik, tanggal saja
    # ===========================

    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"],
        errors="coerce"
    ).dt.date

    df["Biometrik H-1"] = (
        df["flag_bio"]
        .fillna(False)
        .astype(bool)
        .map({True: "Valid", False: "Unvalid"})
    )

    # ===========================
    # TANGGAL BIOMETRIK -- buang jam/menit/detik, tanggal saja
    # ===========================

    df["Tanggal Biometrik"] = pd.to_datetime(
        df["ga_dt"],
        dayfirst=True,
        errors="coerce"
    ).dt.date

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
    # FILTER USER (untuk dropdown)
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
    # FILTER (SEARCH + INPUT BY)
    # ===========================

    col1, col2 = st.columns(2)

    with col1:

        keyword = st.text_input(
            "Cari Outlet / ID Outlet / MSISDN / User"
        )

    with col2:

        pilih_user = st.selectbox(
            "Input By",
            list_user
        )

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

    if pilih_user != "Semua":

        df = df[
            df["Input By"] == pilih_user
        ]

    st.divider()

    # ===========================
    # ROLE MAP
    # ===========================

    role_map = (
        users
        .drop_duplicates(subset="USER")
        .assign(
            USER=lambda x: x["USER"].astype(str).str.strip().str.upper()
        )
        .set_index("USER")["ROLE"]
        .to_dict()
    )

    df["ROLE"] = (
        df["Input By"]
        .astype(str)
        .str.strip()
        .str.upper()
        .map(role_map)
        .fillna("")
    )

    # ===========================
    # UPLINE MAP
    # ===========================

    atasan_map = (
        users
        .drop_duplicates(subset="USER")
        .assign(
            USER=lambda x: x["USER"].astype(str).str.strip().str.upper()
        )
        .set_index("USER")["ATASAN"]
        .to_dict()
    )

    df["Upline"] = (
        df["Input By"]
        .astype(str)
        .str.strip()
        .str.upper()
        .map(atasan_map)
        .fillna("")
    )

    df["ROLE"] = (
        df["Input By"]
        .astype(str)
        .str.strip()
        .str.upper()
        .map(role_map)
        .fillna("")
    )

    # ===========================
    # REKAP PER ROLE (9 ROLE)
    # ===========================

    REKAP_DEFS = [
        ("Rekap CSE/RSE",      ["CSE", "RSE"],  "groups"),
        ("Rekap BSM",          ["BSM"],         "supervisor_account"),
        ("Rekap DSE",          ["DSE"],         "badge"),
        ("Rekap DSE Promotor", ["PROMOTOR"],    "campaign"),
        ("Rekap Promotor",     ["NP"],          "sell"),
        ("Rekap GEMPI",        ["GEMINI"],      "star"),
        ("Rekap GSE",          ["GSE"],         "store"),
        ("Rekap RGE",          ["RGE"],         "military_tech"),
        ("Rekap Frontliner",   ["FRONTLINER"],  "storefront"),
    ]

    for title, roles, icon in REKAP_DEFS:

        nama_role = "_".join(roles)

        df_role = df[df["ROLE"].isin(roles)].copy()

        _render_rekap(df_role, title, icon, nama_role)