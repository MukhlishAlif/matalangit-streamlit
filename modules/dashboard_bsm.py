# ==========================================================
# IMPORT
# ==========================================================

import streamlit as st
import pandas as pd
import base64

from st_aggrid import (
    AgGrid,
    GridOptionsBuilder,
    GridUpdateMode
)

from io import BytesIO

from database import (
    tampil_data_by_date,
    get_latest_data_date,
    tampil_user
)


# ==========================================================
# BASE64 IMAGE HELPER (untuk logo header)
# ==========================================================

def get_base64_image(path):

    try:

        with open(path, "rb") as f:

            return base64.b64encode(f.read()).decode()

    except Exception:

        return ""


# ==========================================================
# GRID TABLE
# ==========================================================

def show_grid(
    df,
    selectable=False,
    key=None,
    col_align=None      # <-- BARU: dict {"Nama Kolom": "left" / "center" / "right"}
):

    if df.empty:

        st.info("Tidak ada data.")
        return None

    if col_align is None:

        col_align = {}

    st.markdown(
        """
        <style>

        .ag-theme-balham .ag-pinned-bottom {

            font-weight:700 !important;
            min-height:42px !important;
            line-height:42px !important;

        }

        /* HEADER CENTER */
        .header-center .ag-header-cell-label {

            justify-content: center !important;

        }

        </style>
        """,
        unsafe_allow_html=True
    )

    gb = GridOptionsBuilder.from_dataframe(df)

    # =========================
    # HELPER: MAP ALIGNMENT -> FLEX JUSTIFY
    # =========================

    def get_justify(align_value):

        mapping = {

            "left": "flex-start",
            "center": "center",
            "right": "flex-end"

        }

        return mapping.get(align_value, "center")

    # =========================
    # DEFAULT COLUMN
    # =========================

    gb.configure_default_column(

        resizable=True,
        sortable=True,
        filter=False,
        suppressMenu=True,
        floatingFilter=False,

        flex=1,
        minWidth=180,

        cellStyle={
            "textAlign": "center",
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center"
        }

    )

    # =========================
    # FIRST COLUMN
    # =========================

    first_col = df.columns[0]

    first_col_align = col_align.get(first_col, "left")

    gb.configure_column(

        first_col,
        pinned="left",

        flex=2,
        minWidth=270,

        cellStyle={
            "textAlign": first_col_align,
            "display": "flex",
            "justifyContent": get_justify(first_col_align),
            "alignItems": "center",
            "paddingLeft": "12px" if first_col_align == "left" else "0px"
        },

        filter=False,
        suppressMenu=True,
        floatingFilter=False

    )

    # =========================
    # OVERRIDE ALIGNMENT KOLOM LAIN SESUAI col_align
    # =========================

    for field, align_value in col_align.items():

        if field == first_col:

            continue

        padding_style = {}

        if align_value == "left":

            padding_style = {"paddingLeft": "12px"}

        elif align_value == "right":

            padding_style = {"paddingRight": "12px"}

        gb.configure_column(

            field,

            cellStyle={
                "textAlign": align_value,
                "display": "flex",
                "justifyContent": get_justify(align_value),
                "alignItems": "center",
                **padding_style
            }

        )

    if selectable:

        gb.configure_selection(

            selection_mode="single",
            use_checkbox=False

        )

    # =========================
    # GRID OPTIONS
    # =========================

    gb.configure_grid_options(

        headerHeight=45,
        rowHeight=42,
        domLayout="normal"

    )

    # =====================================================
    # TOTAL ROW
    # =====================================================

    total_row = {}

    for col in df.columns:

        if pd.api.types.is_numeric_dtype(df[col]):

            total_row[col] = int(
                df[col].sum()
            )

        else:

            if col in [

                "HOS",
                "BSM",
                "Branch",
                "CSE/RSE",
                "AE",
                "Atasan",
                "Nama"

            ]:

                total_row[col] = (
                    df[col].nunique()
                )

            else:

                total_row[col] = ""

    # =====================================================
    # BUILD GRID
    # =====================================================

    grid_options = gb.build()

    # =====================================================
    # HILANGKAN CORONG
    # =====================================================

    for col in grid_options["columnDefs"]:

        col["filter"] = False
        col["floatingFilter"] = False
        col["suppressMenu"] = True

    # =====================================================
    # PINNED BOTTOM
    # =====================================================

    grid_options["pinnedBottomRowData"] = [
        total_row
    ]

    header_height = 45
    row_height = 42
    footer_height = 45

    table_height = min(

        header_height
        + (len(df) * row_height)
        + footer_height
        + 10,

        560

    )

    grid_response = AgGrid(

        df,

        key=key,

        gridOptions=grid_options,

        fit_columns_on_grid_load=False,

        update_mode=GridUpdateMode.SELECTION_CHANGED,

        height=table_height,

        theme="balham",

        allow_unsafe_jscode=True,

        custom_css={

            ".ag-root-wrapper": {

                "border": "1px solid #f0dce2",
                "border-radius": "14px"

            },

            # =========================================
            # HEADER DEFAULT CENTER
            # =========================================

            ".ag-header": {

                "background": "linear-gradient(120deg, #FCEFE1 0%, #FBE3E0 60%, #F8DDE6 100%)"

            },

            ".ag-header-cell-label": {

                "justify-content": "center",
                "font-weight": "700",
                "color": "#7A2C46"

            },

            # =========================================
            # HEADER FIRST COLUMN LEFT
            # =========================================

            ".ag-pinned-left-header .ag-header-cell-label": {

                "justify-content": "flex-start !important",
                "padding-left": "12px"

            },

            ".ag-row": {

                "font-size": "14px"

            },

            ".ag-row-hover": {

                "background-color": "#FFF5F7 !important"

            },

            ".ag-pinned-bottom": {

                "background-color": "#FDF1F5",
                "font-weight": "700",
                "border-top": "2px solid #D4537E",
                "min-height": "42px"

            }

        }

    )

    return grid_response


# ==========================================================
# SAFE SELECT
# ==========================================================

def get_selected_value(
    grid,
    column_name
):

    if not grid:
        return None

    selected = grid.get(
        "selected_rows"
    )

    if selected is None:
        return None

    if isinstance(
        selected,
        pd.DataFrame
    ):

        if not selected.empty:

            return selected.iloc[0][column_name]

    elif isinstance(
        selected,
        list
    ):

        if len(selected) > 0:

            return selected[0][column_name]

    return None


# ==========================================================
# EXPORT EXCEL
# ==========================================================

def to_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(

        output,
        engine="openpyxl"

    ) as writer:

        df.to_excel(

            writer,

            index=False,

            sheet_name="Dashboard"

        )

    return output.getvalue()


# ==========================================================
# KPI CARD
# ==========================================================

def kpi_card(icon, label, value, color):

    st.markdown(

        f"""
        <div class="bsm-kpi-card" style="border-top:4px solid {color};">
            <div class="bsm-kpi-icon">
                <span class="material-symbols-outlined">{icon}</span>
            </div>
            <div class="bsm-kpi-value">{value}</div>
            <div class="bsm-kpi-label">{label}</div>
        </div>
        """,

        unsafe_allow_html=True

    )


# ==========================================================
# SECTION TITLE
# ==========================================================

def section_title(text, icon=None):

    icon_html = (

        f'<span class="material-symbols-outlined" style="vertical-align:-6px;margin-right:6px;">{icon}</span>'

        if icon else ""

    )

    st.markdown(

        f"<div class='bsm-card-title'>{icon_html}{text}</div>",

        unsafe_allow_html=True

    )

# ==========================================================
# DASHBOARD
# ==========================================================

def show():
    st.markdown(
        """
        <link rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" />
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # LOAD USER LEBIH AWAL
    # =====================================================

    users = tampil_user()

    df_user = pd.DataFrame(

        [dict(row) for row in users]

    )

    df_user.columns = (
        df_user.columns.str.upper()
    )

    # =====================================================
    # FLAG_ACTIVE: True = Aktif (tampil di rekap & KPI),
    # False = Non Aktif (HANYA dihitung di KPI Vacant)
    #
    # Fallback ke True kalau kolom belum tersedia dari
    # tampil_user() (mis. database.py belum ter-update /
    # cache lama), supaya dashboard tidak crash.
    # =====================================================

    df_user["FLAG_ACTIVE"] = (
        df_user["STATUS"]
        .astype(str)
        .str.strip()
        .str.upper()
        == "AKTIF"
    )

    active_users_set = set(

        df_user[
            df_user["FLAG_ACTIVE"] == True
        ]["USER"]
        .astype(str)
        .str.strip()

    )

    # ======================================================
    # USER -> REAL NAME
    # ======================================================

    real_name_map = (
        df_user
        .drop_duplicates(subset="USER")
        .assign(
            USER=lambda x: x["USER"]
            .astype(str)
            .str.strip()
            .str.upper()
        )
        .set_index("USER")["REAL_NAME"]
        .to_dict()
    )

    def get_real_name(username):

        key = str(username).strip().upper()

        nama = real_name_map.get(key)

        nama_str = str(nama).strip().upper()

        if (
            pd.isna(nama)
            or nama_str in ["", "VACANT", "NAN", "NONE"]
        ):

            return nama

        return nama

    # =====================================================
    # USER BRAND
    # =====================================================

    df_user["BRAND"] = ""

    df_user.loc[

        df_user["ATASAN"]
        .astype(str)
        .str.lower()
        .str.contains("_im3", na=False),

        "BRAND"

    ] = "IM3"

    df_user.loc[

        df_user["ATASAN"]
        .astype(str)
        .str.lower()
        .str.contains("_3id", na=False),

        "BRAND"

    ] = "3ID"

    # =====================================================
    # SESSION
    # =====================================================

    role = st.session_state.outlet_role
    user = st.session_state.outlet_user

    display_name = real_name_map.get(
        str(user).strip().upper(),
        user
    )

    initials = "".join(
        [w[0].upper() for w in str(display_name).split()[:2]]
    ) or "-"

    # =====================================================
    # HEADER (gaya sama seperti Promotor)
    # =====================================================

    logo_b64 = get_base64_image("icon.png")

    st.markdown(

        f"""
        <style>
        .bsm-header {{
            border-radius: 16px;
            overflow: hidden;
            background: linear-gradient(120deg, #F5B400 0%, #F0997B 35%, #D4537E 70%, #993556 100%);
            padding: 1.5rem 1.75rem;
            margin-bottom: 1.5rem;
            position: relative;
        }}
        .bsm-header-inner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
            position: relative;
        }}
        .bsm-title-row {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .bsm-logo-img {{
            width: 60px;
            height: 60px;
            object-fit: contain;
            filter: drop-shadow(0 1px 2px rgba(0,0,0,0.15));
        }}
        .bsm-title-row span.bsm-title-text {{
            font-size: 26px;
            font-weight: 600;
            color: #fff;
        }}
        .bsm-sub {{
            font-size: 14px;
            color: rgba(255,255,255,0.88);
            margin-top: 4px;
        }}
        .bsm-user-card {{
            background: rgba(255,255,255,0.16);
            border-radius: 12px;
            padding: 10px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .bsm-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 14px;
            color: #993556;
            flex-shrink: 0;
        }}
        .bsm-user-name {{
            font-weight: 600;
            font-size: 15px;
            color: #fff;
        }}
        .bsm-role-pill {{
            background: rgba(255,255,255,0.25);
            color: #fff;
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 10px;
            margin-top: 2px;
            display: inline-block;
        }}

        /* ============ KPI CARD ============ */
        .bsm-kpi-card {{
            background: #fff;
            border-radius: 14px;
            padding: 16px 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(153, 53, 86, 0.08);
            border: 1px solid #f3e3e8;
        }}
        .bsm-kpi-icon {{
            font-size: 22px;
            margin-bottom: 4px;
        }}
        .bsm-kpi-value {{
            font-size: 22px;
            font-weight: 700;
            color: #3d2230;
        }}
        .bsm-kpi-label {{
            font-size: 12px;
            color: #9a7a86;
            margin-top: 2px;
        }}

        /* ============ SECTION / CARD TITLE ============ */
        .bsm-card-title {{
            font-size: 20px;
            font-weight: 700;
            color: #993556;
            margin-bottom: 10px;
        }}
        </style>

        <div class="bsm-header">
            <div class="bsm-header-inner">
                <div>
                    <div class="bsm-title-row">
                        <img src="data:image/png;base64,{logo_b64}" class="bsm-logo-img" />
                        <span class="bsm-title-text">Dashboard BSM</span>
                    </div>
                </div>
            </div>
        </div>
        """,

        unsafe_allow_html=True

    )

    # =====================================================
    # TENTUKAN TANGGAL & BRAND DULU, SEBELUM LOAD DATA
    # =====================================================

    latest_date = get_latest_data_date()

    with st.container(border=True):

        col_tgl, col_brand = st.columns(2)

        with col_tgl:

            tanggal = st.date_input(

                ":material/calendar_month: Filter Tanggal",

                value=(

                    latest_date,

                    latest_date

                ),

                key="pm_tanggal"

            )

        with col_brand:

            brand = st.selectbox(

                ":material/sim_card: Filter Brand",

                options=[

                    "Semua",
                    "IM3",
                    "3ID"

                ],

                index=0

            )

    if isinstance(tanggal, tuple):

        if len(tanggal) == 2:

            start_date, end_date = tanggal

        elif len(tanggal) == 1:

            start_date = end_date = tanggal[0]

        else:

            start_date = end_date = latest_date

    else:

        start_date = end_date = tanggal

    # =====================================================
    # LOAD DATA SESUAI RENTANG TANGGAL
    # =====================================================

    data = tampil_data_by_date(

        start_date,

        end_date

    )

    if len(data) == 0:

        st.info(

            "Belum ada data."

        )

        return

    # ======================================================
    # DATAFRAME
    # ======================================================

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

    # =====================================================
    # BIOMETRIK
    # =====================================================

    df["Biometrik"] = (

        df["flag_bio"]
        .fillna(False)
        .astype(bool)

    )

    # ======================================================
    # FILTER
    # ======================================================

    df["Tanggal"] = pd.to_datetime(

        df["Tanggal"],

        errors="coerce"

    ).dt.date

    st.divider()

    # ======================================================
    # FILTER ROLE
    # ======================================================

    if role == "BSM":

        df = df[
            df["Input By"] == user
        ]

    elif role == "HOS":

        bawahan = df_user[

            (df_user["ATASAN"] == user)
            &
            (df_user["ROLE"] == "BSM")
            &
            (df_user["FLAG_ACTIVE"] == True)

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(bawahan)
        ]

    # role == "ADMIN" -> tidak difilter, lihat semua

    # ======================================================
    # FILTER: HANYA SUBMISSION DARI USER AKTIF.
    # User non-aktif tidak boleh muncul/dihitung di manapun
    # (dashboard maupun rekap) -- cukup dihitung di Vacant.
    # Jaring pengaman tambahan, meniru pola di Leaderboard,
    # supaya konsisten walau ada penambahan role/cabang baru
    # di FILTER ROLE di atas yang lupa memfilter FLAG_ACTIVE.
    # ======================================================

    df = df[
        df["Input By"]
        .astype(str)
        .str.strip()
        .isin(active_users_set)
    ]

    # ======================================================
    # BRAND MAP
    # ======================================================

    brand_map = df_user.set_index(
        "USER"
    )["BRAND"].to_dict()

    df["BRAND"] = df["Input By"].map(
        brand_map
    )

    # ======================================================
    # FILTER BRAND
    # ======================================================

    if brand != "Semua":

        df = df[
            df["BRAND"] == brand
        ]

    # =====================================================
    # DATA KHUSUS INPUT BSM
    # =====================================================

    daftar_bsm_role = df_user[

        (df_user["ROLE"] == "BSM")

        &

        (df_user["FLAG_ACTIVE"] == True)

    ]["USER"].tolist()

    df_bsm = df[

        df["Input By"].isin(
            daftar_bsm_role
        )

    ]

    # =====================================================
    # KPI ROLE AWARE
    # =====================================================

    if role == "BSM":

        total_user = 1

        user_aktif = (

            1

            if len(df_bsm) > 0

            else 0

        )

        daftar_user = [user]

    elif role == "HOS":

        daftar_user = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "BSM")

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]["USER"].tolist()

        total_user = len(
            daftar_user
        )

        total_user = len(
            daftar_user
        )

        user_aktif = df_bsm[

            df_bsm["Input By"].isin(
                daftar_user
            )

        ]["Input By"].nunique()

    else:

        daftar_user = daftar_bsm_role

        total_user = len(
            daftar_user
        )

        user_aktif = df_bsm[

            df_bsm["Input By"].isin(
                daftar_user
            )

        ]["Input By"].nunique()


    # =====================================================
    # JUMLAH VACANT = BSM/HOS dalam scope yang STATUS-nya
    # Non Aktif (FLAG_ACTIVE == False)
    #
    # daftar_user di atas HANYA berisi user AKTIF (sudah
    # difilter FLAG_ACTIVE == True), jadi scope penuh untuk
    # hitung vacant harus diambil ulang TANPA filter aktif.
    # =====================================================

    if role == "BSM":

        daftar_user_all = [user]

    elif role == "HOS":

        daftar_user_all = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "BSM")

        ]["USER"].tolist()

    else:

        daftar_user_all = df_user[

            df_user["ROLE"] == "BSM"

        ]["USER"].tolist()

    jumlah_vacant = (

        len(daftar_user_all)
        -
        len(daftar_user)

    )

    # =====================================================
    # KPI TOTAL
    # =====================================================

    total_outlet = df_bsm["ID Outlet"].nunique()

    total_msisdn = len(df_bsm)

    total_bio = df_bsm["Biometrik"].sum()

    persen_user_aktif = round(

        (
            user_aktif / total_user
        ) * 100,

        2

    ) if total_user > 0 else 0

    persen_bio = round(

        (
            total_bio / total_msisdn
        ) * 100,

        2

    ) if total_msisdn > 0 else 0

    # =====================================================
    # UI KPI (card berwarna, bukan st.metric polos)
    # =====================================================

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        kpi_card("groups", "BSM", total_user, "#F5B400")

    with col2:

        kpi_card("person_off", "Vacant", jumlah_vacant, "#E8A33D")

    with col3:

        kpi_card("bolt", "BSM Aktif", user_aktif, "#F0997B")

    with col4:

        kpi_card("trending_up", "% BSM Aktif", f"{persen_user_aktif}%", "#D4537E")

    with col5:

        kpi_card("smartphone", "MSISDN", total_msisdn, "#993556")

    st.divider()

    # =====================================================
    # HIERARCHY SESSION
    # =====================================================

    if "selected_hos_bsm" not in st.session_state:

        st.session_state.selected_hos_bsm = None

    # ======================================================
    # BSM (LEAF - INPUT SENDIRI)
    # ======================================================

    if role == "BSM":

        section_title("Detail Input", icon="list_alt")

        detail_df = df[[

            "Nama Outlet",
            "ID Outlet",
            "MSISDN",
            "Biometrik",
            "Tanggal"

        ]]

        with st.container(border=True):

            st.download_button(

                label=":material/download: Download Detail Input",

                data=to_excel(detail_df),

                file_name="detail_input.xlsx",

                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

                key="download_detail_bsm"

            )

            show_grid(detail_df)

    # ======================================================
    # HOS (REKAP BSM DI BAWAHNYA)
    # ======================================================

    elif role == "HOS":

        header_col, reset_col = st.columns([5, 1])

        with header_col:

            section_title("Rekap BSM", icon="list_alt")

        with reset_col:

            if st.button(

                "Reset",
                icon=":material/refresh:",

                use_container_width=True,

                key="reset_hos_bsm"

            ):

                st.rerun()

        rekap_bsm = []

        daftar_bsm = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "BSM")

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]

        for _, row in daftar_bsm.iterrows():

            nama_bsm = row["USER"]


            temp = df[

                df["Input By"] == nama_bsm

            ]

            total_msisdn = len(temp)

            total_bio = temp["Biometrik"].sum()

            persen_bio = round(

                (
                    total_bio / total_msisdn
                ) * 100,

                2

            ) if total_msisdn > 0 else 0

            rekap_bsm.append({

                "BSM":
                    nama_bsm,

                "Nama":
                    get_real_name(nama_bsm),

                "Status":

                    "Aktif"

                    if total_msisdn > 0

                    else

                    "Belum Input",

                "MSISDN":
                    total_msisdn,

                "Biometrik":
                    total_bio,

                "% Biometrik":
                    f"{persen_bio}%"

            })

        summary_bsm = pd.DataFrame(
            rekap_bsm
        )

        if brand != "Semua":

            summary_bsm = summary_bsm[

                summary_bsm["BSM"]
                .astype(str)
                .str.contains(
                    brand,
                    case=False,
                    na=False
                )

            ]

        if not summary_bsm.empty:

            summary_bsm = (

                summary_bsm

                .sort_values(

                    "MSISDN",

                    ascending=False

                )

            )

        with st.container(border=True):

            st.download_button(

                label=":material/download: Download Rekap BSM",

                data=to_excel(summary_bsm),

                file_name="rekap_bsm.xlsx",

                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

                key="download_hos_bsm"

            )

            show_grid(

                summary_bsm,

                selectable=False,

                key="bsm_hos",
                col_align={
                    "Nama": "left"
                }

            )

    # ======================================================
    # ADMIN (REKAP HOS -> DRILL REKAP BSM)
    # ======================================================

    else:

        # ==================================================
        # REKAP HOS
        # ==================================================

        header_col, reset_col = st.columns([5, 1])

        with header_col:

            section_title("Rekap HOS", icon="list_alt")

        with reset_col:

            if st.button(

                "Reset",
                icon=":material/refresh:",
                use_container_width=True,

                key="reset_admin_bsm"

            ):

                st.session_state.selected_hos_bsm = None
                st.rerun()

        rekap_hos = []

        hos_list = df_user[

            (df_user["ROLE"] == "HOS")

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]

        for _, row in hos_list.iterrows():

            nama_hos = row["USER"]

            daftar_bsm = df_user[

                (df_user["ATASAN"] == nama_hos)

                &

                (df_user["ROLE"] == "BSM")

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]["USER"].tolist()

            total_bsm = len(daftar_bsm)

            # =========================================
            # PENTING: "temp" harus dihitung dari data
            # submission SEMUA BSM di bawah HOS ini
            # (sebelumnya variabel "temp" tidak pernah
            # didefinisikan di sini -> NameError / bug).
            # =========================================

            temp = df[

                df["Input By"].isin(
                    daftar_bsm
                )

            ]

            total_aktif = temp["Input By"].nunique()

            total_msisdn = len(temp)

            total_bio = temp["Biometrik"].sum()

            persen_aktif = round(

                (
                    total_aktif / total_bsm
                ) * 100,

                2

            ) if total_bsm > 0 else 0

            persen_bio = round(

                (
                    total_bio / total_msisdn
                ) * 100,

                2

            ) if total_msisdn > 0 else 0

            rekap_hos.append({

                "HOS":
                    nama_hos,

                "Nama":
                    get_real_name(nama_hos),

                "BSM":
                    total_bsm,

                "BSM Aktif":
                    total_aktif,

                "% User Aktif":
                    f"{persen_aktif}%",

                "MSISDN":
                    total_msisdn,

                "Biometrik":
                    total_bio,

                "% Biometrik":
                    f"{persen_bio}%"

            })

        summary_hos = pd.DataFrame(
            rekap_hos
        )

        if brand != "Semua":

            summary_hos = summary_hos[

                summary_hos["HOS"]
                .astype(str)
                .str.contains(
                    brand,
                    case=False,
                    na=False
                )

            ]

        if not summary_hos.empty:

            summary_hos = (

                summary_hos

                .sort_values(

                    "MSISDN",

                    ascending=False

                )

            )

        with st.container(border=True):

            st.download_button(

                label=":material/download: Download Rekap HOS",

                data=to_excel(summary_hos),

                file_name="rekap_hos.xlsx",

                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

                key="download_admin_hos_bsm"

            )

            hos_grid = show_grid(

                summary_hos,

                selectable=True,

                key="hos_admin_bsm",
                col_align={
                    "Nama": "left"
                }

            )

        selected_hos = get_selected_value(
            hos_grid,
            "HOS"
        )

        if selected_hos:

            if st.session_state.selected_hos_bsm != selected_hos:

                st.session_state.selected_hos_bsm = selected_hos

                st.rerun()

        st.divider()

        # ==================================================
        # REKAP BSM
        # ==================================================

        section_title("Rekap BSM", icon="list_alt")

        rekap_bsm = []

        bsm_list = df_user[

            (df_user["ROLE"] == "BSM")

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]

        for _, row in bsm_list.iterrows():

            if st.session_state.selected_hos_bsm:

                if row["ATASAN"] != st.session_state.selected_hos_bsm:
                    continue

            nama_bsm = row["USER"]

            temp = df[

                df["Input By"]
                == nama_bsm

            ]

            total_msisdn = len(temp)

            total_bio = temp["Biometrik"].sum()

            persen_bio = round(

                (
                    total_bio / total_msisdn
                ) * 100,

                2

            ) if total_msisdn > 0 else 0

            status_user = (

                "Aktif"

                if total_msisdn > 0

                else

                "Belum Input"

            )

            rekap_bsm.append({

                "BSM":
                    nama_bsm,

                "Nama":
                    get_real_name(nama_bsm),

                "Status":
                    status_user,

                "MSISDN":
                    total_msisdn,

                "Biometrik":
                    total_bio,

                "% Biometrik":
                    f"{persen_bio}%"

            })

        summary_bsm = pd.DataFrame(
            rekap_bsm
        )

        if brand != "Semua":

            summary_bsm = summary_bsm[

                summary_bsm["BSM"]
                .astype(str)
                .str.contains(
                    brand,
                    case=False,
                    na=False
                )

            ]

        if not summary_bsm.empty:

            summary_bsm = (

                summary_bsm

                .sort_values(

                    "MSISDN",

                    ascending=False

                )

            )

        with st.container(border=True):

            st.download_button(

                label=":material/download: Download Rekap BSM",

                data=to_excel(summary_bsm),

                file_name="rekap_bsm.xlsx",

                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

                key="download_admin_bsm_detail"

            )

            show_grid(

                summary_bsm,

                selectable=False,

                key="bsm_admin",
                col_align={
                    "Nama": "left"
                }

            )