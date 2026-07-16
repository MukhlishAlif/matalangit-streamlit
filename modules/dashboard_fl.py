# =========================================================
# dashboard_frontliner.py
# DASHBOARD FRONTLINER
# HOS -> BSM -> CSE/RSE -> FRONTLINER
# =========================================================

import streamlit as st
import pandas as pd
from io import BytesIO
import base64

from st_aggrid import (
    AgGrid,
    GridOptionsBuilder,
    GridUpdateMode
)

from database import (
    tampil_data_by_date,
    get_latest_data_date,
    tampil_user
)

# =========================================================
# HELPER TAMPILAN (disamakan dengan dashboard_dse.py)
# =========================================================

def get_base64_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

def kpi_card(icon, label, value, color):

    st.markdown(

        f"""
        <div class="dse-kpi-card" style="border-top:4px solid {color};">
            <div class="dse-kpi-icon">
                <span class="material-symbols-outlined">{icon}</span>
            </div>
            <div class="dse-kpi-value">{value}</div>
            <div class="dse-kpi-label">{label}</div>
        </div>
        """,

        unsafe_allow_html=True

    )

def section_title(text, icon=None):

    icon_html = (

        f'<span class="material-symbols-outlined" style="vertical-align:-6px;margin-right:6px;">{icon}</span>'

        if icon else ""

    )

    st.markdown(

        f"<div class='dse-card-title'>{icon_html}{text}</div>",

        unsafe_allow_html=True

    )

# =========================================================
# GET SELECTED VALUE
# =========================================================

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

# =========================================================
# GRID TABLE
# =========================================================

def show_grid(
    df,
    selectable=False,
    key=None,
    total_outlet=None,
    col_align=None
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

            font-weight: 700 !important;
            min-height: 42px !important;
            line-height: 42px !important;

        }

        </style>
        """,
        unsafe_allow_html=True
    )

    gb = GridOptionsBuilder.from_dataframe(df)

    # =====================================================
    # DEFAULT COLUMN
    # =====================================================

    gb.configure_default_column(

        resizable=False,
        sortable=True,
        filter=False,
        suppressMenu=True,
        floatingFilter=False

    )

    # =====================================================
    # SELECTABLE
    # =====================================================

    if selectable:

        gb.configure_selection(

            selection_mode="single",
            use_checkbox=False

        )

    # =====================================================
    # GRID OPTIONS
    # =====================================================

    gb.configure_grid_options(

        headerHeight=45,
        rowHeight=42,
        domLayout="normal",

        suppressMovableColumns=True

    )
    # =====================================================
    # TOTAL ROW
    # =====================================================

    total_row = {}

    for col in df.columns:

        if pd.api.types.is_numeric_dtype(df[col]):

            # =============================================
            # KHUSUS OUTLET
            # =============================================

            if col == "Outlet":

                total_row[col] = (

                    total_outlet
                    if total_outlet is not None
                    else 0

                )

            else:

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
                "Atasan"

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
    # HELPER: MAP ALIGNMENT -> FLEX JUSTIFY
    # =====================================================

    def get_justify(align_value):

        mapping = {

            "left": "flex-start",
            "center": "center",
            "right": "flex-end"

        }

        return mapping.get(align_value, "center")

    def get_text_align(align_value):

        return align_value if align_value in ["left", "center", "right"] else "center"

    # =====================================================
    # FIX COLUMN WIDTH BERDASARKAN ISI + ALIGNMENT
    # =====================================================

    first_col = df.columns[0]

    for col in grid_options["columnDefs"]:

        field = col["field"]

        max_len = max(

            len(str(field)),
            df[field].astype(str).str.len().max()

        )

        width = min(

            max(
                max_len * 10 + 30,
                120
            ),

            450

        )

        col["width"] = int(width)
        col["minWidth"] = int(width)
        col["maxWidth"] = int(width)

        # =================================================
        # TENTUKAN ALIGNMENT KOLOM INI
        # =================================================

        if field in col_align:

            align_value = col_align[field]

        elif field == first_col:

            align_value = "left"

        else:

            align_value = "center"

        justify_value = get_justify(align_value)
        text_align_value = get_text_align(align_value)

        padding_style = {}

        if align_value == "left":

            padding_style = {"paddingLeft": "12px"}

        elif align_value == "right":

            padding_style = {"paddingRight": "12px"}

        if field == first_col:

            col["width"] = 260
            col["minWidth"] = 260
            col["maxWidth"] = 260

            # Freeze kolom pertama
            col["pinned"] = "left"
            col["lockPinned"] = True
            col["lockPosition"] = True
            col["suppressMovable"] = True

            col["cellStyle"] = {

                "textAlign": text_align_value,
                "display": "flex",
                "justifyContent": justify_value,
                "alignItems": "center",
                "fontWeight": "600",
                **padding_style

            }

        else:

            col["cellStyle"] = {

                "textAlign": text_align_value,
                "display": "flex",
                "justifyContent": justify_value,
                "alignItems": "center",
                **padding_style

            }

    # =====================================================
    # HILANGKAN CORONG SEMUA KOLOM
    # =====================================================

    for col in grid_options["columnDefs"]:

        col["filter"] = False
        col["floatingFilter"] = False
        col["suppressMenu"] = True

    # =====================================================
    # FOOTER
    # =====================================================

    grid_options["pinnedBottomRowData"] = [
        total_row
    ]

    # =====================================================
    # HEIGHT
    # =====================================================

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

    # ======================================================
    # GRID
    # ======================================================

    grid_response = AgGrid(

        df,

        key=key,

        gridOptions=grid_options,

        fit_columns_on_grid_load=False,

        height=table_height,

        theme="balham",

        update_mode=GridUpdateMode.SELECTION_CHANGED,

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
# =========================================================
# DASHBOARD
# =========================================================

def show():

    st.markdown(
        """
        <link rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" />
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # LOAD DATA AWAL (JANGAN DIUBAH) — dipakai untuk header
    # dan sebagai nilai default filter tanggal
    # =====================================================

    latest_date = get_latest_data_date()

    data = tampil_data_by_date(latest_date, latest_date)
    users = tampil_user()

    if len(data) == 0:

        st.info(

            "Belum ada data."

        )

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

    # =====================================================
    # USER DF
    # =====================================================

    df_user = pd.DataFrame(

        users,

        columns=[

            "user",
            "role",
            "atasan",
            "real_name"

        ]

    )

    df_user.columns = (
        df_user.columns.str.upper()
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

        if (
            pd.isna(nama)
            or str(nama).strip() == ""
            or str(nama).strip().lower() == "vacant"
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

    # =====================================================
    # ⭐ HEADER (tampil paling atas, sebelum filter)
    # =====================================================

    logo_b64 = get_base64_image("icon.png")

    display_name = real_name_map.get(
        str(user).strip().upper(),
        user
    )

    initials = "".join(
        [w[0].upper() for w in str(display_name).split()[:2]]
    ) or "-"

    st.markdown(
        f"""
        <style>
        .dse-header {{
            border-radius: 16px;
            overflow: hidden;
            background: linear-gradient(120deg, #F5B400 0%, #F0997B 35%, #D4537E 70%, #993556 100%);
            padding: 1.5rem 1.75rem;
            margin-bottom: 1.5rem;
        }}
        .dse-header-inner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
        }}
        .dse-title-row {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .dse-logo-img {{
            width: 60px;
            height: 60px;
            object-fit: contain;
            filter: drop-shadow(0 1px 2px rgba(0,0,0,0.15));
        }}
        .dse-title-row span.dse-title-text {{
            font-size: 26px;
            font-weight: 600;
            color: #fff;
        }}
        .dse-user-card {{
            background: rgba(255,255,255,0.16);
            border-radius: 12px;
            padding: 10px 16px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .dse-avatar {{
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
        }}
        .dse-user-name {{
            font-weight: 600;
            font-size: 15px;
            color: #fff;
        }}
        .dse-role-pill {{
            background: rgba(255,255,255,0.25);
            color: #fff;
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 10px;
            margin-top: 2px;
            display: inline-block;
        }}
        .dse-kpi-card {{
            background: #fff;
            border-radius: 14px;
            padding: 16px 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(153, 53, 86, 0.08);
            border: 1px solid #f3e3e8;
        }}
        .dse-kpi-icon {{
            font-size: 22px;
            margin-bottom: 4px;
        }}
        .dse-kpi-value {{
            font-size: 22px;
            font-weight: 700;
            color: #3d2230;
        }}
        .dse-kpi-label {{
            font-size: 12px;
            color: #9a7a86;
            margin-top: 2px;
        }}
        .dse-card-title {{
            font-size: 20px;
            font-weight: 700;
            color: #993556;
            margin-bottom: 10px;
        }}
        </style>

        <div class="dse-header">
            <div class="dse-header-inner">
                <div>
                    <div class="dse-title-row">
                        <img src="data:image/png;base64,{logo_b64}" class="dse-logo-img" />
                        <span class="dse-title-text">Dashboard Frontliner</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # FILTER (tampil setelah header)
    # =====================================================

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

        if isinstance(tanggal, tuple):

            if len(tanggal) == 2:

                start_date, end_date = tanggal

            elif len(tanggal) == 1:

                start_date = end_date = tanggal[0]

            else:

                start_date = end_date = latest_date

        else:

            start_date = end_date = tanggal

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

    # =====================================================
    # RELOAD DATA SESUAI RENTANG TANGGAL HASIL FILTER
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

    df["Biometrik"] = (

        df["flag_bio"]
        .fillna(False)
        .astype(bool)

    )

    # =====================================================
    # FILTER ROLE
    # =====================================================

    if role == "FRONTLINER":

        df = df[
            df["Input By"] == user
        ]

    elif role in [

        "CSE",
        "RSE"

    ]:

        daftar_fl = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "FRONTLINER")

        ]["USER"].tolist()

        df = df[
            df["Input By"]
            .isin(daftar_fl)
        ]

    elif role == "BSM":

        daftar_cse = df_user[
            df_user["ATASAN"] == user
        ]["USER"].tolist()

        daftar_fl = df_user[

            (df_user["ATASAN"]
            .isin(daftar_cse))

            &

            (df_user["ROLE"] == "FRONTLINER")

        ]["USER"].tolist()

        df = df[
            df["Input By"]
            .isin(daftar_fl)
        ]

    elif role == "HOS":

        daftar_bsm = df_user[
            df_user["ATASAN"] == user
        ]["USER"].tolist()

        daftar_cse = df_user[
            df_user["ATASAN"]
            .isin(daftar_bsm)
        ]["USER"].tolist()

        daftar_fl = df_user[

            (df_user["ATASAN"]
            .isin(daftar_cse))

            &

            (df_user["ROLE"] == "FRONTLINER")

        ]["USER"].tolist()

        df = df[
            df["Input By"]
            .isin(daftar_fl)
        ]

    # =====================================================
    # BRAND MAP
    # =====================================================

    brand_map = (
         df_user
         .drop_duplicates(subset="USER")
         .set_index("USER")["BRAND"]
         .to_dict()
    )

    df["BRAND"] = df["Input By"].map(
        brand_map
    )

    # =====================================================
    # FILTER BRAND
    # =====================================================

    if brand != "Semua":

        df = df[

            df["BRAND"] == brand

        ]

        # =========================
    # JUMLAH VACANT
    # =========================

    user_master = (
        df_user[
            df_user["ROLE"] == "FRONTLINER"
        ]
        .drop_duplicates(subset="USER")
    )

    real_name_clean = (
        user_master["REAL_NAME"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    vacant_labels = [
        "",
        "nan",
        "none",
        "null",
        "vacant",
        "-"
    ]

    jumlah_vacant = (
        real_name_clean.isin(vacant_labels)
        .sum()
    )


    # =====================================================
    # KPI
    # =====================================================

    fl_all = df_user[
        df_user["ROLE"] == "FRONTLINER"
    ]["USER"].tolist()

    df_fl = df[
        df["Input By"].isin(fl_all)
    ]

    fl_aktif = df_fl["Input By"].nunique()
    jumlah_outlet = df_fl["ID Outlet"].nunique()
    jumlah_msisdn = len(df_fl)
    jumlah_biometrik = (df_fl["Biometrik"] == True).sum()

    total_fl = len(fl_all)

    # =========================
    # PERSENTASE
    # =========================

    persen_fl_aktif = (
        round((fl_aktif / total_fl) * 100, 2)
        if total_fl > 0 else 0
    )

    persen_biometrik = (
        round((jumlah_biometrik / jumlah_msisdn) * 100, 2)
        if jumlah_msisdn > 0 else 0
    )

    # =========================
    # KPI UI (disamakan dengan dashboard_dse.py)
    # =========================

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        kpi_card("store", "Outlet", jumlah_outlet, "#F5B400")

    with col2:
        kpi_card("groups", "Frontliner", total_fl, "#F0997B")

    with col3:
        kpi_card("person_off", "Vacant", jumlah_vacant, "#E8A33D")

    with col4:
        kpi_card("bolt", "FL Aktif", fl_aktif, "#D4537E")

    with col5:
        kpi_card("trending_up", "% FL Aktif", f"{persen_fl_aktif}%", "#993556")

    with col6:
        kpi_card("smartphone", "MSISDN", jumlah_msisdn, "#7A2C46")

    st.divider()

    # =====================================================
    # HIERARCHY FILTER
    # =====================================================

    selected_hos = None
    selected_bsm = None
    selected_cse = None

    # =====================================================
    # HIERARCHY FILTER
    # =====================================================

    if "selected_hos_fl" not in st.session_state:
        st.session_state.selected_hos_fl = None

    if "selected_bsm_fl" not in st.session_state:
        st.session_state.selected_bsm_fl = None

    if "selected_cse_fl" not in st.session_state:
        st.session_state.selected_cse_fl = None

    # =====================================================
    # HEADER + RESET
    # =====================================================

    header_col, reset_col = st.columns([5, 1])

    with header_col:

        if role == "ADMIN":

            section_title("Rekap HOS", icon="list_alt")

        elif role == "HOS":

            section_title("Rekap BSM", icon="list_alt")

        elif role == "BSM":

            section_title("Rekap CSE/RSE", icon="list_alt")

        else:

            section_title("Rekap Frontliner", icon="list_alt")

    with reset_col:

        if st.button(
            "Reset",
            icon=":material/refresh:",
            use_container_width=True,
            key="reset_fl"
        ):

            st.session_state.selected_hos_fl = None
            st.session_state.selected_bsm_fl = None
            st.session_state.selected_cse_fl = None

            st.rerun()

    # =====================================================
    # REKAP HOS
    # =====================================================

    if role == "ADMIN":

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
                (df_user["ATASAN"].isin(daftar_bsm))
                &
                (df_user["ROLE"].isin([
                    "CSE",
                    "RSE"
                ]))
            ]["USER"].tolist()

            daftar_fl = df_user[
                (df_user["ATASAN"].isin(daftar_cse))
                &
                (df_user["ROLE"] == "FRONTLINER")
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_fl)
            ]

            total_fl = len(daftar_fl)

            fl_aktif = temp["Input By"].nunique()

            total_msisdn = len(temp)

            total_bio = temp["Biometrik"].sum()

            persen_active = round(
                (fl_aktif / total_fl) * 100,
                2
            ) if total_fl > 0 else 0

            persen_bio = round(
                (total_bio / total_msisdn) * 100,
                2
            ) if total_msisdn > 0 else 0

            rekap_hos.append({

                "HOS":
                    nama_hos,

                "Nama":
                    get_real_name(nama_hos), 


                "Frontliner":
                    total_fl,

                "Frontliner Aktif":
                    fl_aktif,

                "% Frontliner Aktif":
                    f"{persen_active}%",

                "Outlet":
                    temp["ID Outlet"].nunique(),

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

        # =====================================================
        # FILTER BRAND
        # =====================================================

        if brand != "Semua":
            summary_hos = summary_hos[
                summary_hos["HOS"]
                .astype(str)
                .str.contains(brand, case=False, na=False)
            ]

        with st.container(border=True):                    # ← BARU, level 8

            buffer = BytesIO()                              # ← level 12 (masuk 1 tab ke dalam container)
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                summary_hos.to_excel(writer, index=False)

            st.download_button(                             # ← level 12
                label=":material/download: Download HOS",
                data=buffer.getvalue(),
                file_name="rekap_hos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_hos"
            )

            hos_grid = show_grid(                           # ← level 12
                summary_hos,
                selectable=True,
                key=f"hos_{tanggal}_{role}_{user}",
                col_align={"Nama": "left"},
                total_outlet=(
                    df["ID Outlet"].dropna().astype(str).str.strip().nunique()
                )
            )

        selected_hos = get_selected_value(hos_grid, "HOS")   # ← BALIK ke level 8 (di luar container)

        if selected_hos:                                    # ← level 8
            st.session_state.selected_hos_fl = selected_hos
            st.session_state.selected_bsm_fl = None
            st.session_state.selected_cse_fl = None

        st.divider()                                        # ← level 8

    # =====================================================
    # REKAP BSM
    # =====================================================

    if role in ["HOS", "ADMIN"]:

        if role == "ADMIN":

            section_title("Rekap BSM", icon="list_alt")

        rekap_bsm = []

        if role == "HOS":

            bsm_list = df_user[

                (df_user["ROLE"] == "BSM")

                &

                (df_user["ATASAN"] == user)

            ]

        else:

            bsm_list = df_user[
                df_user["ROLE"] == "BSM"
            ]

        for _, row in bsm_list.iterrows():

            if st.session_state.selected_hos_fl:

                if row["ATASAN"] != st.session_state.selected_hos_fl:

                    continue

            nama_bsm = row["USER"]

            daftar_cse = df_user[

                (df_user["ATASAN"] == nama_bsm)

                &

                (df_user["ROLE"].isin([
                    "CSE",
                    "RSE"
                ]))

            ]["USER"].tolist()

            daftar_fl = df_user[

                (df_user["ATASAN"].isin(
                    daftar_cse
                ))

                &

                (df_user["ROLE"] == "FRONTLINER")

            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(
                    daftar_fl
                )
            ]

            total_fl = len(
                daftar_fl
            )

            fl_aktif = temp[
                "Input By"
            ].nunique()

            total_msisdn = len(temp)

            total_bio = temp[
                "Biometrik"
            ].sum()

            persen_active = round(
                (
                    fl_aktif / total_fl
                ) * 100,
                2
            ) if total_fl > 0 else 0

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

                "Frontliner":
                    total_fl,

                "Frontliner Aktif":
                    fl_aktif,

                "% Frontliner Aktif":
                    f"{persen_active}%",

                "Outlet":
                    temp["ID Outlet"].nunique(),

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

        with st.container(border=True):

            buffer = BytesIO()

            with pd.ExcelWriter(
                buffer,
                engine="openpyxl"
            ) as writer:

                summary_bsm.to_excel(
                    writer,
                    index=False
                )

            st.download_button(

                label=":material/download: Download BSM",

                data=buffer.getvalue(),

                file_name="rekap_bsm.xlsx",

                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

                key="download_bsm"

            )

            bsm_grid = show_grid(

                summary_bsm,

                selectable=True,

                key=f"bsm_{tanggal}_{role}_{user}",
                col_align={
                    "Nama": "left"
                },

                total_outlet=(

                    df["ID Outlet"]

                    .dropna()

                    .astype(str)

                    .str.strip()

                    .nunique()

                )

            )

        selected_bsm = get_selected_value(
            bsm_grid,
            "BSM"
        )

        if selected_bsm:

            st.session_state.selected_bsm_fl = (
                selected_bsm
            )

            st.session_state.selected_cse_fl = None

        st.divider()

    # =====================================================
    # REKAP CSE/RSE
    # =====================================================

    if role in ["BSM", "HOS", "ADMIN"]:

        if role in ["ADMIN", "HOS"]:

            section_title("Rekap CSE/RSE", icon="list_alt")

        rekap_cse = []

        if role == "BSM":

            cse_list = df_user[

                (df_user["ROLE"].isin([
                    "CSE",
                    "RSE"
                ]))

                &

                (df_user["ATASAN"] == user)

            ]

        elif role == "HOS":

            daftar_bsm = df_user[

                (df_user["ATASAN"] == user)

                &

                (df_user["ROLE"] == "BSM")

            ]["USER"].tolist()

            cse_list = df_user[

                (df_user["ROLE"].isin([
                    "CSE",
                    "RSE"
                ]))

                &

                (df_user["ATASAN"].isin(
                    daftar_bsm
                ))

            ]

        else:

            cse_list = df_user[
                df_user["ROLE"].isin([
                    "CSE",
                    "RSE"
                ])
            ]

        for _, row in cse_list.iterrows():

            if role in ["ADMIN", "HOS"]:

                if st.session_state.selected_bsm_fl:

                    if row["ATASAN"] != st.session_state.selected_bsm_fl:
                        continue

            nama_cse = row["USER"]

            daftar_fl = df_user[

                (df_user["ATASAN"] == nama_cse)

                &

                (df_user["ROLE"] == "FRONTLINER")

            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(
                    daftar_fl
                )
            ]

            total_fl = len(daftar_fl)

            fl_aktif = temp[
                "Input By"
            ].nunique()

            total_msisdn = len(temp)

            total_bio = temp[
                "Biometrik"
            ].sum()

            persen_active = round(

                (
                    fl_aktif / total_fl
                ) * 100,

                2

            ) if total_fl > 0 else 0

            persen_bio = round(

                (
                    total_bio / total_msisdn
                ) * 100,

                2

            ) if total_msisdn > 0 else 0

            rekap_cse.append({

                "CSE/RSE":
                    nama_cse,

                "Nama":
                    get_real_name(nama_cse), 

                "Frontliner":
                    total_fl,

                "Frontliner Aktif":
                    fl_aktif,

                "% Frontliner Aktif":
                    f"{persen_active}%",

                "Outlet":
                    temp["ID Outlet"]
                    .nunique(),

                "MSISDN":
                    total_msisdn,

                "Biometrik":
                    total_bio,

                "% Biometrik":
                    f"{persen_bio}%"

            })

        summary_cse = pd.DataFrame(
            rekap_cse
        )

        if brand != "Semua":

            summary_cse = summary_cse[

                summary_cse["CSE/RSE"]
                .astype(str)
                .str.contains(
                    brand,
                    case=False,
                    na=False
                )

            ]

        with st.container(border=True):

            buffer = BytesIO()

            with pd.ExcelWriter(
                buffer,
                engine="openpyxl"
            ) as writer:

                summary_cse.to_excel(
                    writer,
                    index=False
                )

            st.download_button(

                label=":material/download: Download CSE/RSE",

                data=buffer.getvalue(),

                file_name="rekap_cse.xlsx",

                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

                key="download_cse"

            )

            cse_grid = show_grid(

                summary_cse,

                selectable=True,

                key=f"cse_{tanggal}_{role}_{user}",
                col_align={
                    "Nama": "left"
                },

                total_outlet=(

                    df["ID Outlet"]

                    .dropna()

                    .astype(str)

                    .str.strip()

                    .nunique()

                )

            )

        selected_cse = get_selected_value(
            cse_grid,
            "CSE/RSE"
        )

        if selected_cse:

            st.session_state.selected_cse_fl = (
                selected_cse
            )

        st.divider()

    # =====================================================
    # REKAP FRONTLINER
    # =====================================================
    if role not in ["CSE", "RSE"]:
       section_title("Rekap Frontliner", icon="list_alt")

    rekap_fl = []

    fl_user = df_user[
        df_user["ROLE"] == "FRONTLINER"
    ]

    for _, row in fl_user.iterrows():

        # =============================================
        # FILTER HIERARKI
        # =============================================

        if role in ["CSE", "RSE"]:

            if row["ATASAN"] != user:
                continue

        elif role == "BSM":

            daftar_cse = df_user[

                (df_user["ATASAN"] == user)

                &

                (df_user["ROLE"].isin([
                    "CSE",
                    "RSE"
                ]))

            ]["USER"].tolist()

            if row["ATASAN"] not in daftar_cse:
                continue

        elif role == "HOS":

            daftar_bsm = df_user[

                (df_user["ATASAN"] == user)

                &

                (df_user["ROLE"] == "BSM")

            ]["USER"].tolist()

            daftar_cse = df_user[

                (df_user["ATASAN"].isin(
                    daftar_bsm
                ))

                &

                (df_user["ROLE"].isin([
                    "CSE",
                    "RSE"
                ]))

            ]["USER"].tolist()

            if row["ATASAN"] not in daftar_cse:
                continue

            if st.session_state.selected_cse_fl:

                if row["ATASAN"] != st.session_state.selected_cse_fl:
                    continue

        elif role == "ADMIN":

            if st.session_state.selected_cse_fl:

                if row["ATASAN"] != st.session_state.selected_cse_fl:
                    continue

            elif st.session_state.selected_bsm_fl:

                daftar_cse = df_user[

                    (df_user["ATASAN"] == st.session_state.selected_bsm_fl)

                    &

                    (df_user["ROLE"].isin([
                        "CSE",
                        "RSE"
                    ]))

                ]["USER"].tolist()

                if row["ATASAN"] not in daftar_cse:
                    continue

            elif st.session_state.selected_hos_fl:

                daftar_bsm = df_user[
                    df_user["ATASAN"]
                    == st.session_state.selected_hos_fl
                ]["USER"].tolist()

                daftar_cse = df_user[

                    (df_user["ATASAN"].isin(
                        daftar_bsm
                    ))

                    &

                    (df_user["ROLE"].isin([
                        "CSE",
                        "RSE"
                    ]))

                ]["USER"].tolist()

                if row["ATASAN"] not in daftar_cse:
                    continue

        nama_fl = row["USER"]

        temp = df[
            df["Input By"] == nama_fl
        ]

        total_msisdn = len(temp)

        total_bio = temp[
            "Biometrik"
        ].sum()

        persen_bio = round(

            (
                total_bio / total_msisdn
            ) * 100,

            2

        ) if total_msisdn > 0 else 0

        rekap_fl.append({

            "Frontliner":
                nama_fl,

            "Nama":
                get_real_name(nama_fl), 


            "Upline":
                row["ATASAN"],

            "Status":

                "Aktif"

                if total_msisdn > 0

                else

                "Belum Input",

            "Outlet":
                temp["ID Outlet"]
                .nunique(),

            "MSISDN":
                total_msisdn,

            "Biometrik":
                total_bio,

            "% Biometrik":
                f"{persen_bio}%"

        })

    summary_fl = pd.DataFrame(
        rekap_fl
    )

    if brand != "Semua":

        summary_fl = summary_fl[

            summary_fl["Upline"]
            .astype(str)
            .str.contains(
                brand,
                case=False,
                na=False
            )

        ]

    with st.container(border=True):

        buffer = BytesIO()

        with pd.ExcelWriter(
            buffer,
            engine="openpyxl"
        ) as writer:

            summary_fl.to_excel(
                writer,
                index=False
            )

        st.download_button(

            label=":material/download: Download Frontliner",

            data=buffer.getvalue(),

            file_name="rekap_frontliner.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key="download_frontliner"

        )

        show_grid(

            summary_fl,

            selectable=False,

            key="frontliner",
            col_align={
                "Nama": "left"
            },

            total_outlet=(

                df["ID Outlet"]

                .dropna()

                .astype(str)

                .str.strip()

                .nunique()

            )

        )