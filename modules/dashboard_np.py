
# =========================================================
# dashboard_promotor.py
# DASHBOARD PROMOTOR
# HOS -> BSM -> CSE/RSE -> PROMOTOR
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

        f"<div class='pm-card-title'>{icon_html}{text}</div>",

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
    selectable=True,
    key=None,
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
        minWidth=120,

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
                "NP",
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
# =========================================================
# TO EXCEL
# =========================================================

def to_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Sheet1"
        )

    return output.getvalue()

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

    logo_b64 = get_base64_image("icon.png")

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

        /* ============ KPI CARD ============ */
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

        /* ============ SECTION / CARD TITLE ============ */
        .dse-card-title {{
            font-size: 20px;
            font-weight: 700;
            color: #993556;
            margin-bottom: 10px;
        }}
        </style>

        <div class="dse-header">
            <div class="dse-title-row">
                <img src="data:image/png;base64,{logo_b64}" class="dse-logo-img" />
                <span class="dse-title-text">Dashboard NP</span>
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

            return username

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
    # FILTER TANGGAL
    # =====================================================

    df["Tanggal"] = pd.to_datetime(

        df["Tanggal"],

        errors="coerce"

    ).dt.date

    st.divider()

    # =====================================================
    # FILTER ROLE
    # =====================================================

    if role == "NP":

        df = df[
            df["Input By"] == user
        ]

    elif role in [

        "CSE",
        "RSE"

    ]:

        daftar_promotor = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "NP")

        ]["USER"].tolist()

        df = df[
            df["Input By"]
            .isin(daftar_promotor)
        ]

    elif role == "BSM":

        daftar_cse = df_user[
            df_user["ATASAN"] == user
        ]["USER"].tolist()

        daftar_promotor = df_user[

            (df_user["ATASAN"]
            .isin(daftar_cse))

            &

            (df_user["ROLE"] == "NP")

        ]["USER"].tolist()

        df = df[
            df["Input By"]
            .isin(daftar_promotor)
        ]

    elif role == "HOS":

        daftar_bsm = df_user[
            df_user["ATASAN"] == user
        ]["USER"].tolist()

        daftar_cse = df_user[
            df_user["ATASAN"]
            .isin(daftar_bsm)
        ]["USER"].tolist()

        daftar_promotor = df_user[

            (df_user["ATASAN"]
            .isin(daftar_cse))

            &

            (df_user["ROLE"] == "NP")

        ]["USER"].tolist()

        df = df[
            df["Input By"]
            .isin(daftar_promotor)
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

    # =====================================================
    # KPI FILTER SESUAI ROLE
    # =====================================================

    if role == "NP":

        promotor_all = [user]

    elif role in ["CSE", "RSE"]:

        promotor_all = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "NP")

        ]["USER"].tolist()

    elif role == "BSM":

        daftar_cse = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"].isin([
                "CSE",
                "RSE"
            ]))

        ]["USER"].tolist()

        promotor_all = df_user[

            (df_user["ATASAN"].isin(
                daftar_cse
            ))

            &

            (df_user["ROLE"] == "NP")

        ]["USER"].tolist()

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

        promotor_all = df_user[

            (df_user["ATASAN"].isin(
                daftar_cse
            ))

            &

            (df_user["ROLE"] == "NP")

        ]["USER"].tolist()

    else:

        promotor_all = df_user[
            df_user["ROLE"] == "NP"
        ]["USER"].tolist()

    # =====================================================
    # FILTER BRAND KPI
    # =====================================================

    if brand != "Semua":

        promotor_all = df_user[

            (df_user["ROLE"] == "NP")

            &

            (
                df_user["ATASAN"]
                .astype(str)
                .str.contains(
                    brand,
                    case=False,
                    na=False
                )
            )

        ]["USER"].tolist()

    total_promotor = len(
        promotor_all
    )

    # =====================================================
    # JUMLAH VACANT
    # =====================================================

    user_master = (
        df_user[
            df_user["USER"].isin(promotor_all)
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

    df_promotor = df[

        df["Input By"].isin(
            promotor_all
        )

    ]

    promotor_aktif = (
        df_promotor["Input By"]
        .nunique()
    )

    jumlah_outlet = (
        df_promotor["ID Outlet"]
        .nunique()
    )

    jumlah_msisdn = len(
        df_promotor
    )

    jumlah_biometrik = (
        df_promotor["Biometrik"]
        .sum()
    )

    persen_aktif = round(

        (
            promotor_aktif
            / total_promotor
        ) * 100,

        2

    ) if total_promotor > 0 else 0

    persen_bio = round(

        (
            jumlah_biometrik
            / jumlah_msisdn
        ) * 100,

        2

    ) if jumlah_msisdn > 0 else 0

    # =====================================================
    # KPI UI
    # =====================================================

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        kpi_card("group", "NP", total_promotor, "#F5B400")

    with col2:
        kpi_card("person_off", "Vacant", jumlah_vacant, "#E8A33D")

    with col3:
        kpi_card("bolt", "NP Aktif", promotor_aktif, "#F0997B")

    with col4:
        kpi_card("trending_up", "% NP Aktif", f"{persen_aktif}%", "#D4537E")

    with col5:
        kpi_card("smartphone", "MSISDN", jumlah_msisdn, "#993556")

    st.divider()
    # =========================================================
    # HIERARCHY SESSION
    # =========================================================

    if "selected_hos_pm" not in st.session_state:

        st.session_state.selected_hos_pm = None

    if "selected_bsm_pm" not in st.session_state:

        st.session_state.selected_bsm_pm = None

    if "selected_cse_pm" not in st.session_state:

        st.session_state.selected_cse_pm = None

    # =========================================================
    # HEADER + RESET
    # =========================================================

    col_title, col_reset = st.columns([5, 1])

    with col_title:

        if role == "ADMIN":

            section_title("Rekap HOS", icon="list_alt")

        elif role == "HOS":

            section_title("Rekap BSM", icon="list_alt")

        elif role == "BSM":

            section_title("Rekap CSE/RSE", icon="list_alt")

        else:

            section_title("Rekap NP", icon="list_alt")

    with col_reset:

        if st.button(
            "Reset",
            icon=":material/refresh:",
            use_container_width=True,
            key="reset_pm"
        ):

            st.session_state.selected_hos_pm = None
            st.session_state.selected_bsm_pm = None
            st.session_state.selected_cse_pm = None

            st.rerun()

    # =========================================================
    # REKAP HOS
    # =========================================================

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

                (df_user["ATASAN"].isin(
                    daftar_bsm
                ))

                &

                (df_user["ROLE"].isin([
                    "CSE",
                    "RSE"
                ]))

            ]["USER"].tolist()

            daftar_promotor = df_user[

                (df_user["ATASAN"].isin(
                    daftar_cse
                ))

                &

                (df_user["ROLE"] == "NP")

            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(
                    daftar_promotor
                )
            ]

            total_promotor = len(
                daftar_promotor
            )

            promotor_aktif = (
                temp["Input By"]
                .nunique()
            )

            total_msisdn = len(temp)

            total_bio = (
                temp["Biometrik"]
                .sum()
            )

            persen_aktif = round(
                (
                    promotor_aktif
                    / total_promotor
                ) * 100,
                2
            ) if total_promotor > 0 else 0

            persen_bio = round(
                (
                    total_bio
                    / total_msisdn
                ) * 100,
                2
            ) if total_msisdn > 0 else 0

            rekap_hos.append({

                "HOS": nama_hos,

                "Nama":
                    get_real_name(nama_hos),

                "NP": total_promotor,

                "NP Aktif": promotor_aktif,

                "% NP Aktif": f"{persen_aktif}%",

                "MSISDN": total_msisdn,

                "Biometrik": total_bio,

                "% Biometrik": f"{persen_bio}%"

            })

        summary_hos = pd.DataFrame(rekap_hos)

        # =====================================================
        # FILTER BRAND
        # =====================================================

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

            summary_hos = summary_hos.sort_values(
                "MSISDN",
                ascending=False
            )

        st.download_button(

            label=":material/download: Download Rekap HOS",
            data=to_excel(summary_hos),

            file_name="rekap_hos.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key="download_hos"

        )

        hos_grid = show_grid(

            summary_hos,

            selectable=True,

            key="hos",
            col_align={
                "Nama": "left"
            }

        )

        selected_hos = get_selected_value(

            hos_grid,

            "HOS"

        )

        if selected_hos:

            if st.session_state.selected_hos_pm != selected_hos:

                st.session_state.selected_hos_pm = selected_hos
                st.session_state.selected_bsm_pm = None
                st.session_state.selected_cse_pm = None

                st.rerun()

        st.divider()

    # =========================================================
    # REKAP BSM
    # =========================================================

    if role in ["ADMIN", "HOS"]:

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

            if (
                st.session_state.selected_hos_pm
            ):

                if (
                    row["ATASAN"]
                    !=
                    st.session_state.selected_hos_pm
                ):

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

            daftar_promotor = df_user[

                (df_user["ATASAN"].isin(
                    daftar_cse
                ))

                &

                (df_user["ROLE"] == "NP")

            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(
                    daftar_promotor
                )
            ]

            total_promotor = len(
                daftar_promotor
            )

            promotor_aktif = (
                temp["Input By"]
                .nunique()
            )

            total_msisdn = len(temp)

            total_bio = (
                temp["Biometrik"]
                .sum()
            )

            persen_aktif = round(
                (
                    promotor_aktif
                    / total_promotor
                ) * 100,
                2
            ) if total_promotor > 0 else 0

            persen_bio = round(
                (
                    total_bio
                    / total_msisdn
                ) * 100,
                2
            ) if total_msisdn > 0 else 0

            rekap_bsm.append({

                "BSM":
                    nama_bsm,

                "Nama":
                    get_real_name(nama_bsm),

                "NP":
                    total_promotor,

                "NP Aktif":
                    promotor_aktif,

                "% NP Aktif":
                    f"{persen_aktif}%",

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

        st.download_button(

            label=":material/download: Download Rekap BSM",

            data=to_excel(summary_bsm),

            file_name="rekap_bsm.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key="download_bsm"

        )

        bsm_grid = show_grid(

            summary_bsm,

            selectable=True,

            key="bsm",
            col_align={
                "Nama": "left"
            }

        )

        selected_bsm = get_selected_value(

            bsm_grid,

            "BSM"

        )

        if selected_bsm:

            if (
                st.session_state.selected_bsm_pm
                != selected_bsm
            ):

                st.session_state.selected_bsm_pm = (
                    selected_bsm
                )

                st.session_state.selected_cse_pm = None

                st.rerun()

        st.divider()
    # =========================================================
    # REKAP CSE / RSE
    # =========================================================

    if role in ["ADMIN", "HOS", "BSM"]:

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

            if (

                st.session_state.selected_bsm_pm

            ):

                if (

                    row["ATASAN"]

                    !=

                    st.session_state.selected_bsm_pm

                ):

                    continue

            elif (

                st.session_state.selected_hos_pm

            ):

                daftar_bsm_hos = df_user[

                    (df_user["ATASAN"]

                    == st.session_state.selected_hos_pm)

                    &

                    (df_user["ROLE"] == "BSM")

                ]["USER"].tolist()

                if row["ATASAN"] not in daftar_bsm_hos:

                    continue

            nama_cse = row["USER"]

            daftar_promotor = df_user[

                (df_user["ATASAN"] == nama_cse)

                &

                (df_user["ROLE"] == "NP")

            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(
                    daftar_promotor
                )
            ]

            total_promotor = len(
                daftar_promotor
            )

            promotor_aktif = (
                temp["Input By"]
                .nunique()
            )

            total_msisdn = len(temp)

            total_bio = (
                temp["Biometrik"]
                .sum()
            )

            persen_aktif = round(
                (
                    promotor_aktif
                    / total_promotor
                ) * 100,
                2
            ) if total_promotor > 0 else 0

            persen_bio = round(
                (
                    total_bio
                    / total_msisdn
                ) * 100,
                2
            ) if total_msisdn > 0 else 0

            rekap_cse.append({

                "CSE/RSE":
                    nama_cse,

                "Nama":
                    get_real_name(nama_cse),

                "NP":
                    total_promotor,

                "NP Aktif":
                    promotor_aktif,

                "% NP Aktif":
                    f"{persen_aktif}%",

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
        if not summary_cse.empty:

            summary_cse = (
                summary_cse
                .sort_values(
                    "MSISDN",
                    ascending=False
                )
            )

        st.download_button(

            label=":material/download: Download Rekap CSE/RSE",

            data=to_excel(summary_cse),

            file_name="rekap_cse.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key="download_cse"

        )

        cse_grid = show_grid(

            summary_cse,

            selectable=True,

            key="cse",
            col_align={
                "Nama": "left"
            }

        )

        selected_cse = get_selected_value(

            cse_grid,

            "CSE/RSE"

        )

        if selected_cse:

            if (
                st.session_state.selected_cse_pm
                != selected_cse
            ):

                st.session_state.selected_cse_pm = (
                    selected_cse
                )

                st.rerun()

        st.divider()

    # =========================================================
    # REKAP PROMOTOR
    # =========================================================

    if role not in ["CSE", "RSE"]:

        section_title("Rekap NP", icon="list_alt")

    rekap_promotor = []

    promotor_user = df_user[

        df_user["ROLE"] == "NP"

    ]

    for _, row in promotor_user.iterrows():

        # =============================================
        # FILTER ADMIN
        # =============================================

        if role == "ADMIN":

            if st.session_state.selected_cse_pm:

                if (
                    row["ATASAN"]
                    !=
                    st.session_state.selected_cse_pm
                ):

                    continue

            elif st.session_state.selected_bsm_pm:

                daftar_cse = df_user[

                    (df_user["ATASAN"]
                    == st.session_state.selected_bsm_pm)

                    &

                    (df_user["ROLE"].isin([
                        "CSE",
                        "RSE"
                    ]))

                ]["USER"].tolist()

                if row["ATASAN"] not in daftar_cse:

                    continue

            elif st.session_state.selected_hos_pm:

                daftar_bsm = df_user[

                    df_user["ATASAN"]
                    == st.session_state.selected_hos_pm

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

        # =============================================
        # FILTER HOS
        # =============================================

        elif role == "HOS":

            if st.session_state.selected_bsm_pm:

                daftar_cse = df_user[

                    (df_user["ATASAN"]
                    == st.session_state.selected_bsm_pm)

                    &

                    (df_user["ROLE"].isin([
                        "CSE",
                        "RSE"
                    ]))

                ]["USER"].tolist()

                if row["ATASAN"] not in daftar_cse:

                    continue

            else:

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

        # =============================================
        # FILTER BSM
        # =============================================

        elif role == "BSM":

            if st.session_state.selected_cse_pm:

                if (
                    row["ATASAN"]
                    !=
                    st.session_state.selected_cse_pm
                ):

                    continue

            else:

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

        # =============================================
        # FILTER CSE/RSE
        # =============================================

        elif role in ["CSE", "RSE"]:

            if row["ATASAN"] != user:

                continue

        nama_promotor = row["USER"]

        temp = df[
            df["Input By"] == nama_promotor
        ]

        total_msisdn = len(temp)

        total_bio = (
            temp["Biometrik"]
            .sum()
        )

        persen_bio = round(
            (
                total_bio
                / total_msisdn
            ) * 100,
            2
        ) if total_msisdn > 0 else 0

        rekap_promotor.append({

            "NP":
                nama_promotor,

             "Nama":
                get_real_name(nama_promotor),

            "Upline":
                row["ATASAN"],

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

    summary_promotor = pd.DataFrame(
        rekap_promotor
    )

    # =====================================================
    # FILTER BRAND
    # =====================================================

    if brand != "Semua":

        summary_promotor = summary_promotor[

            summary_promotor["Upline"]
            .astype(str)
            .str.contains(
                brand,
                case=False,
                na=False
            )

        ]

    if not summary_promotor.empty:

        summary_promotor = (
            summary_promotor
            .sort_values(
                "MSISDN",
                ascending=False
            )
        )

        st.download_button(

            label=":material/download: Download Rekap NP",

            data=to_excel(summary_promotor),

            file_name="rekap_promotor.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key="download_promotor"

        )

        show_grid(

            summary_promotor,

            selectable=False,

            key="NP",
            col_align={
                "Nama": "left"
            }

        )