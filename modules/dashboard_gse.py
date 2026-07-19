# ==========================================================
# IMPORT
# ==========================================================

import streamlit as st
import pandas as pd
import base64

from st_aggrid import (
    AgGrid,
    GridOptionsBuilder
)

from io import BytesIO

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

# ==========================================================
# GRID TABLE
# ==========================================================

from st_aggrid import (
    AgGrid,
    GridOptionsBuilder,
    GridUpdateMode
)

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

        </style>
        """,
        unsafe_allow_html=True
    )

    gb = GridOptionsBuilder.from_dataframe(df)

    # =====================================================
    # DEFAULT COLUMN
    # =====================================================

    gb.configure_default_column(

        resizable=True,
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

            total_row[col] = int(
                df[col].sum()
            )

        else:

            if col in [

                "HOS",
                "BSM",
                "Branch",
                "Promotor",
                "AE",
                "RGE",
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
    # FIX WIDTH + FREEZE FIRST COLUMN + ALIGNMENT
    # =====================================================

    first_col = df.columns[0]

    for col in grid_options["columnDefs"]:

        field = col["field"]

        # Hitung panjang isi terpanjang
        max_len = max(
            len(str(field)),
            df[field].fillna("").astype(str).str.len().max()
        )

        # Estimasi lebar (±9 px per karakter)
        width = max(120, min(max_len * 9 + 30, 450))

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

        # Freeze kolom pertama
        if field == first_col:

            col["pinned"] = "left"
            col["lockPinned"] = True
            col["lockPosition"] = True
            col["suppressMovable"] = True

            col["width"] = max(260, int(width))
            col["minWidth"] = max(260, int(width))
            col["maxWidth"] = max(260, int(width))

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

    # ======================================================
    # HEIGHT
    # ======================================================

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

                "border": "1px solid #e5e7eb",
                "border-radius": "14px"

            },

            ".ag-header": {

                "background": "linear-gradient(120deg, #FCEFE1 0%, #FBE3E0 60%, #F8DDE6 100%)",
                "font-weight": "700",
                "color": "#7A2C46"

            },

            # Header semua kolom center
            ".ag-header-cell-label": {

                "display": "flex",
                "justify-content": "center",
                "align-items": "center",
                "width": "100%",
                "text-align": "center"

            },

            # Khusus kolom pertama rata kiri
            ".ag-pinned-left-cols-container .ag-cell": {

                "justify-content": "flex-start !important",
                "text-align": "left !important",
                "padding-left": "12px"

            },

            # Khusus header kolom pertama rata kiri
            ".ag-pinned-left-header .ag-header-cell-label": {

                "justify-content": "flex-start !important",
                "padding-left": "12px"

            },

            ".ag-row": {

                "font-size": "14px"

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

    # ======================================================
    # DATAFRAME
    # ======================================================

    if isinstance(
        selected,
        pd.DataFrame
    ):

        if not selected.empty:

            return selected.iloc[0][column_name]

    # ======================================================
    # LIST
    # ======================================================

    elif isinstance(
        selected,
        list
    ):

        if len(selected) > 0:

            return selected[0][column_name]

    return None

# =========================================================
# EXPORT EXCEL
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

            sheet_name="Dashboard"

        )

    return output.getvalue()
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
                <span class="dse-title-text">Dashboard GSE</span>
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

                    "📅 Filter Tanggal",

                    value=(

                        latest_date,

                        latest_date

                    ),

                    key="pm_tanggal"

                )

        with col_brand:

                brand = st.selectbox(

                    "📶 Filter Brand",

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

    # ======================================================
    # USER DATAFRAME
    # ======================================================

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
    # SESSION
    # ======================================================

    role = st.session_state.outlet_role

    user = st.session_state.outlet_user

    # =====================================================
    # FILTER
    # =====================================================

    df["Tanggal"] = pd.to_datetime(

        df["Tanggal"],

        errors="coerce"

    ).dt.date

    # ======================================================
    # FILTER: HANYA SUBMISSION DARI USER AKTIF.
    # User non-aktif tidak boleh muncul/dihitung di manapun
    # (dashboard maupun rekap) -- cukup dihitung di Vacant.
    # ======================================================

    df = df[
        df["Input By"]
        .astype(str)
        .str.strip()
        .isin(active_users_set)
    ]

    st.divider()

    # ======================================================
    # FILTER ROLE
    # ======================================================

    if role in [

        "GSE"

    ]:

        df = df[
            df["Input By"] == user
        ]

    elif role == "BSM":

        bawahan = df_user[

            df_user["ATASAN"] == user

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(bawahan)
        ]

    elif role == "HOS":

        daftar_bsm = df_user[
            (df_user["ATASAN"] == user)
            &
            (df_user["ROLE"] == "BSM")
        ]["USER"].tolist()

        bawahan = df_user[

            df_user["ATASAN"]
            .isin(daftar_bsm)

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(bawahan)
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
    # DATA KHUSUS INPUT CSE/RSE
    # =====================================================

    daftar_cse_rse = df_user[

        (df_user["ROLE"].isin([

            "GSE"

        ]))

        &

        (df_user["FLAG_ACTIVE"] == True)

    ]["USER"].tolist()

    df_cse = df[

        df["Input By"].isin(
            daftar_cse_rse
        )

    ]

    # =====================================================
    # KPI ROLE AWARE
    # =====================================================

    if role in [

        "GSE"

    ]:

        total_user = 1

        user_aktif = (

            1

            if len(df_cse) > 0

            else 0

        )

    elif role == "BSM":

        daftar_user = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"].isin([

                "GSE"

            ]))

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]["USER"].tolist()

        total_user = len(
            daftar_user
        )

        user_aktif = df_cse[

            df_cse["Input By"].isin(
                daftar_user
            )

        ]["Input By"].nunique()

    elif role == "HOS":

        daftar_bsm = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "BSM")

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]["USER"].tolist()

        daftar_user = df_user[

            (df_user["ATASAN"].isin(
                daftar_bsm
            ))

            &

            (df_user["ROLE"].isin([

                "GSE"

            ]))

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]["USER"].tolist()

        daftar_user = df_user[

            (df_user["ATASAN"].isin(
                daftar_bsm
            ))

            &

            (df_user["ROLE"].isin([

                "GSE"

            ]))

        ]["USER"].tolist()

        total_user = len(
            daftar_user
        )

        user_aktif = df_cse[

            df_cse["Input By"].isin(
                daftar_user
            )

        ]["Input By"].nunique()

    else:

        daftar_user = df_user[

            (df_user["ROLE"].isin([

                "GSE"

            ]))

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]["USER"].tolist()

        total_user = len(
            daftar_user
        )

        user_aktif = df_cse[

            df_cse["Input By"].isin(
                daftar_user
            )

        ]["Input By"].nunique()

    
    
    # =====================================================
    # JUMLAH VACANT = GSE dalam scope role login yang
    # STATUS-nya Non Aktif -> FLAG_ACTIVE == False
    # =====================================================

    if role == "GSE":

        scope_vacant = df_user[

            df_user["USER"] == user

        ]

    elif role == "BSM":

        scope_vacant = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "GSE")

        ]

    elif role == "HOS":

        daftar_bsm_vacant = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "BSM")

        ]["USER"].tolist()

        scope_vacant = df_user[

            (df_user["ATASAN"].isin(daftar_bsm_vacant))

            &

            (df_user["ROLE"] == "GSE")

        ]

    else:

        scope_vacant = df_user[

            df_user["ROLE"] == "GSE"

        ]

    jumlah_vacant = int(

        scope_vacant[

            scope_vacant["FLAG_ACTIVE"] == False

        ]["USER"].nunique()

    )


    # =====================================================
    # KPI TOTAL
    # =====================================================

    total_outlet = df_cse["ID Outlet"].nunique()

    total_msisdn = len(df_cse)

    total_bio = df_cse["Biometrik"].sum()

    # =====================================================
    # PERSENTASE
    # =====================================================

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
    # UI KPI
    # =====================================================

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        kpi_card("group", "GSE", total_user, "#F5B400")

    with col2:
        kpi_card("person_off", "Vacant", jumlah_vacant, "#E8A33D")

    with col3:
        kpi_card("bolt", "GSE Aktif", user_aktif, "#F0997B")

    with col4:
        kpi_card("trending_up", "% GSE Aktif", f"{persen_user_aktif}%", "#D4537E")

    with col5:
        kpi_card("smartphone", "MSISDN", total_msisdn, "#993556")

    st.divider()

    # ======================================================
    # CSE / RSE
    # ======================================================

    if role in [

        "GSE"

    ]:

        st.subheader(
            "📋 Detail Input"
        )

        detail_df = df[[

            "MSISDN",
            "Biometrik",
            "Tanggal"

        ]]

        st.download_button(

            label=":material/download: Download Detail Input",

            data=to_excel(detail_df),

            file_name="detail_input.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key="download_detail"

        )

        show_grid(detail_df)

    # ======================================================
    # BSM
    # ======================================================

    elif role == "BSM":

        header_col, reset_col = st.columns([5, 1])

        with header_col:

            section_title("Rekap GSE", icon="list_alt")

        with reset_col:

            if st.button(

                "Reset",
                icon=":material/refresh:",

                use_container_width=True,

                key="reset_bsm"

            ):

                st.rerun()

        rekap_cse = []

        daftar_cse = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"].isin([

                "GSE"

            ]))

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]


        for _, row in daftar_cse.iterrows():

            nama_cse = row["USER"]

            temp = df[

                df["Input By"] == nama_cse

            ]

            total_msisdn = len(temp)

            total_bio = temp["Biometrik"].sum()

            persen_bio = round(

                (
                    total_bio / total_msisdn
                ) * 100,

                2

            ) if total_msisdn > 0 else 0

            rekap_cse.append({

                "GSE":
                    nama_cse,

                "Nama":
                    get_real_name(nama_cse), 

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

        summary_cse = pd.DataFrame(
            rekap_cse
        )

        # ======================================================
        # FILTER BRAND
        # ======================================================

        if brand != "Semua":

            summary_cse = summary_cse[

                summary_cse["GSE"]
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

            label=":material/download: Download Rekap GSE",

            data=to_excel(summary_cse),

            file_name="rekap_gse.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key="download_pm"

        )

        show_grid(

            summary_cse,

            selectable=False,

            key="cse_bsm",
            col_align={
                "Nama": "left"
            }

        )

    # ======================================================
    # HOS
    # ======================================================

    elif role == "HOS":

        selected_bsm = None

        # ==================================================
        # REKAP BSM
        # ==================================================

        header_col, reset_col = st.columns([5, 1])

        with header_col:

            section_title("Rekap BSM", icon="list_alt")

        with reset_col:

            if st.button(

                "Reset",
                icon=":material/refresh:",

                use_container_width=True,

                key="reset_hos"

            ):

                st.session_state.selected_bsm = None
                st.rerun()

        daftar = []

        daftar_bsm = df_user[
            (df_user["ATASAN"] == user)
            &
            (df_user["ROLE"] == "BSM")
            &
            (df_user["FLAG_ACTIVE"] == True)
        ]["USER"].tolist()

        for bsm in daftar_bsm:

            bawahan = df_user[

                (df_user["ATASAN"] == bsm)

                &

                (df_user["ROLE"].isin([

                    "GSE"

                ]))

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]["USER"].tolist()

            temp = df[

                df["Input By"]
                .isin(bawahan)

            ]

            total_cse = len(bawahan)

            cse_aktif = temp[
                temp["Input By"].isin(bawahan)
            ]["Input By"].nunique()

            total_msisdn = len(temp)

            total_bio = temp["Biometrik"].sum()

            persen_aktif = round(
                (cse_aktif / total_cse) * 100,
                2
            ) if total_cse > 0 else 0

            persen_bio = round(

                (
                    total_bio / total_msisdn
                ) * 100,

                2

            ) if total_msisdn > 0 else 0

            daftar.append({

                "BSM":
                    bsm,

                "Nama":
                    get_real_name(bsm), 

                "GSE":
                    total_cse,

                "GSE Aktif":
                    cse_aktif,

                "% User Aktif":
                    f"{persen_aktif}%",

                "MSISDN":
                    total_msisdn,

                "Biometrik":
                    total_bio,

                "% Biometrik":
                    f"{persen_bio}%"

            })

        summary_bsm = pd.DataFrame(
            daftar
        )

        # ======================================================
        # FILTER BRAND
        # ======================================================

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

            key="hos_bsm",
            col_align={
                "Nama": "left"
            }

        )

        selected_bsm = get_selected_value(
            bsm_grid,
            "BSM"
        )

        st.session_state.selected_bsm = selected_bsm

        st.divider()

        # ==================================================
        # REKAP CSE/RSE
        # ==================================================

        section_title("Rekap GSE", icon="list_alt")

        rekap_cse = []

        for bsm in daftar_bsm:

            bawahan = df_user[
                (df_user["ATASAN"] == bsm)
                &
                (df_user["ROLE"].isin([
                    "GSE"
                ]))
                &
                (df_user["FLAG_ACTIVE"] == True)
            ]

            for _, row in bawahan.iterrows():

                if st.session_state.selected_bsm:

                    if row["ATASAN"] != st.session_state.selected_bsm:
                        continue

                user_cse = row["USER"]

                temp = df[

                    df["Input By"]
                    == user_cse

                ]

                total_msisdn = len(temp)

                total_bio = temp["Biometrik"].sum()

                persen_bio = round(

                    (
                        total_bio / total_msisdn
                    ) * 100,

                    2

                ) if total_msisdn > 0 else 0

                rekap_cse.append({

                    "GSE":
                        user_cse,

                    "Nama":
                        get_real_name(user_cse), 

                    "Branch":
                        bsm,

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

        # ======================================================
        # FILTER BRAND
        # ======================================================

        if brand != "Semua":

            summary_cse = summary_cse[

                summary_cse["GSE"]
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

                    ["MSISDN"],

                    ascending=False

                )

            )

        st.download_button(

            label=":material/download: Download Rekap GSE",

            data=to_excel(summary_cse),

            file_name="rekap_cse.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key="download_hos_pm"

        )

        show_grid(summary_cse)

    # ======================================================
    # ADMIN
    # ======================================================

    else:

        selected_hos = None
        selected_bsm = None

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

                key="reset_admin"

            ):

                st.session_state.selected_hos = None
                st.session_state.selected_bsm = None
                st.session_state.selected_cse = None

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
                (df_user["FLAG_ACTIVE"] == True)
            ]["USER"].tolist()

            daftar_cse = df_user[

                (df_user["ATASAN"]
                .isin(daftar_bsm))

                &

                (df_user["ROLE"].isin([

                    "GSE"

                ]))

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]["USER"].tolist()

            temp = df[
                df["Input By"]
                .isin(daftar_cse)
            ]

            total_cse = len(daftar_cse)

            total_aktif = temp["Input By"].nunique()

            total_msisdn = len(temp)

            total_bio = temp["Biometrik"].sum()

            persen_aktif = round(

                (
                    total_aktif / total_cse
                ) * 100,

                2

            ) if total_cse > 0 else 0

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

                "GSE":
                    total_cse,

                "GSE Aktif":
                    total_aktif,

                "% GSE Aktif":
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

        # ======================================================
        # FILTER BRAND REKAP
        # ======================================================

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

        st.session_state.selected_hos = selected_hos

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

            if selected_hos:

                if row["ATASAN"] != selected_hos:
                    continue

            nama_bsm = row["USER"]

            daftar_cse = df_user[

                (df_user["ATASAN"] == nama_bsm)

                &

                (df_user["ROLE"].isin([

                    "GSE"

                ]))

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]["USER"].tolist()

            temp = df[
                df["Input By"]
                .isin(daftar_cse)
            ]

            total_cse = len(daftar_cse)

            total_aktif = temp["Input By"].nunique()

            total_msisdn = len(temp)

            total_bio = temp["Biometrik"].sum()

            persen_aktif = round(

                (
                    total_aktif / total_cse
                ) * 100,

                2

            ) if total_cse > 0 else 0

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

                "GSE":
                    total_cse,

                "GSE Aktif":
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

        summary_bsm = pd.DataFrame(
            rekap_bsm
        )

        # ======================================================
        # FILTER BRAND
        # ======================================================

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

            key="download_admin_pm"

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

        st.session_state.selected_bsm = selected_bsm

        st.divider()

        # ==================================================
        # REKAP CSE/RSE
        # ==================================================

        section_title("Rekap GSE", icon="list_alt")

        rekap_cse = []

        cse_list = df_user[

            (df_user["ROLE"].isin([

                "GSE"

            ]))

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]

        # ================================================
        # FILTER HOS
        # ================================================

        if selected_hos:

            daftar_bsm_hos = df_user[

                df_user["ATASAN"]
                == selected_hos

            ]["USER"].tolist()

            cse_list = cse_list[

                cse_list["ATASAN"]
                .isin(daftar_bsm_hos)

            ]

        # ================================================
        # FILTER BSM
        # ================================================

        if selected_bsm:

            cse_list = cse_list[

                cse_list["ATASAN"]
                == selected_bsm

            ]

        # ================================================
        # LOOP
        # ================================================

        for _, row in cse_list.iterrows():

            nama_cse = row["USER"]

            # ============================================
            # PENJUALAN CSE ITU SENDIRI
            # ============================================

            temp = df[

                df["Input By"]
                == nama_cse

            ]

            total_msisdn = len(temp)

            total_bio = temp[
                "Biometrik"
            ].sum()

            persen_bio = round(

                (
                    total_bio
                    / total_msisdn
                ) * 100,

                2

            ) if total_msisdn > 0 else 0

            # ============================================
            # STATUS
            # ============================================

            status_user = (

                "Aktif"

                if total_msisdn > 0

                else

                "Belum Input"

            )

            rekap_cse.append({

                "GSE":
                    nama_cse,

                "Nama":
                    get_real_name(nama_cse), 

                "Branch":
                    row["ATASAN"],

                "Status":
                    status_user,

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

        # ======================================================
        # FILTER BRAND
        # ======================================================

        if brand != "Semua":

            summary_cse = summary_cse[

                summary_cse["Branch"]
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

            label=":material/download: Download Rekap GSE",

            data=to_excel(summary_cse),

            file_name="rekap_pm.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key="download_admin_bsm"

        )

        cse_grid = show_grid(

            summary_cse,

            selectable=True,

            key="pm_admin",
            col_align={
                "Nama": "left"
            }

        )

        selected_cse = get_selected_value(

            cse_grid,
            "GSE"

        )

        st.session_state.selected_cse = (
            selected_cse
        )