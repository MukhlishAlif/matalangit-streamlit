# =========================================================
# dashboard_dse.py
# DASHBOARD HIERARCHY DSE
# =========================================================

import streamlit as st
import pandas as pd
from io import BytesIO
import requests

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

import base64

# Tambah fungsi ini setelah imports:
def get_base64_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

# =========================================================
# GRID
# =========================================================

def show_grid(
    df,
    selectable=False,
    key=None
):

    if df.empty:
        st.info("Tidak ada data.")
        return None

    gb = GridOptionsBuilder.from_dataframe(df)

    # =========================
    # DEFAULT COLUMN
    # =========================

    gb.configure_default_column(

        resizable=False,
        sortable=True,
        filter=False,
        suppressMenu=True,
        floatingFilter=False,

        width=140,

        cellStyle={
            "textAlign": "center"
        }

    )

    # =========================
    # FIRST COLUMN
    # =========================

    first_col = df.columns[0]

    gb.configure_column(

        first_col,

        width=700,

        cellStyle={
            "textAlign": "left"
        },

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
    # TOTAL ROW
    # =====================================================

    total_row = {}

    for col in df.columns:

        if pd.api.types.is_numeric_dtype(df[col]):

            total_row[col] = int(
                df[col].sum()
            )

        elif col in [

            "HOS",
            "BSM",
            "Branch",
            "CSE/RSE",
            "Atasan",
            "Nama"

        ]:

            total_row[col] = df[col].nunique()

        else:

            total_row[col] = ""

    # =====================================================
    # GRID OPTIONS
    # =====================================================

    gb.configure_grid_options(

        pinnedBottomRowData=[total_row],

        headerHeight=45,
        rowHeight=42,
        domLayout="normal"

    )

    # =====================================================
    # BUILD GRID
    # =====================================================

    grid_options = gb.build()

    # =====================================================
    # AUTO COLUMN WIDTH
    # =====================================================

    column_widths = {

        first_col: 260,

        "HOS": 180,
        "BSM": 180,
        "CSE/RSE": 260,
        "Branch": 170,
        "Atasan": 170,
        "DSE": 180,
        "Role": 120,
        "Upline": 180,
        "Status": 140,

        "Nama": 230,
        "DSE Aktif": 120,
        "Outlet": 100,
        "MSISDN": 110,
        "Biometrik": 110,
        "% DSE Aktif": 130,
        "% Biometrik": 120

    }

    for col in grid_options["columnDefs"]:

        field = col["field"]

        width = column_widths.get(field, 140)

        col["width"] = width
        col["minWidth"] = width
        col["maxWidth"] = width

        if field == first_col:

            col["pinned"] = "left"

            col["cellStyle"] = {

                "textAlign": "left",
                "display": "flex",
                "justifyContent": "flex-start",
                "alignItems": "center",
                "paddingLeft": "12px",
                "fontWeight": "600"

            }
    # =====================================================
    # HILANGKAN CORONG
    # =====================================================

    for col in grid_options["columnDefs"]:

        col["filter"] = False
        col["floatingFilter"] = False
        col["suppressMenu"] = True


    # =====================================================
    # AUTO HEIGHT
    # =====================================================

    table_height = min(

        520,
        (len(df) + 2) * 42

    )

    # =====================================================
    # GRID CSS
    # =====================================================

    custom_css = {

        # Wrapper
        ".ag-root-wrapper": {
            "border": "1px solid #f0dce2",
            "border-radius": "14px"
        },

        # Header background
        ".ag-header": {
            "background": "linear-gradient(120deg, #FCEFE1 0%, #FBE3E0 60%, #F8DDE6 100%)"
        },

        # =================================================
        # HEADER
        # =================================================

        ".ag-header-cell-label": {
            "display": "flex",
            "justify-content": "center",
            "align-items": "center",
            "width": "100%",
            "font-weight": "700",
            "text-align": "center",
            "color": "#7A2C46"
        },

        ".ag-header-cell[col-id='nama_outlet'] .ag-header-cell-label": {
            "justify-content": "flex-start !important",
            "padding-left": "1px"
        },

        # =================================================
        # CELL
        # =================================================

        ".ag-row": {
            "font-size": "14px"
        },

        ".ag-row-hover": {
            "background-color": "#FFF5F7 !important"
        },

        ".ag-cell": {
            "display": "flex",
            "justify-content": "center",
            "align-items": "center",
            "text-align": "center"
        },

        ".ag-cell[col-id='nama_outlet']": {
            "justify-content": "flex-start !important",
            "text-align": "left !important",
            "padding-left": "12px"
        },

        # =================================================
        # PINNED BOTTOM ROW
        # =================================================

        ".ag-pinned-bottom-row": {
            "background-color": "#FDF1F5",
            "font-weight": "700",
            "border-top": "2px solid #D4537E"
        }

    }
    # =====================================================
    # GRID RENDER
    # =====================================================

    grid_response = AgGrid(

        df,

        key=key,

        gridOptions=grid_options,

        fit_columns_on_grid_load=False,

        height=table_height,

        theme="balham",

        update_mode=GridUpdateMode.SELECTION_CHANGED,

        allow_unsafe_jscode=True,

        custom_css=custom_css

    )

    return grid_response

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

        f"<div class='DSE-card-title'>{icon_html}{text}</div>",

        unsafe_allow_html=True

    )
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
        st.info("Belum ada data.")
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
            "real_name",
            "status",
            "flag_active"
        ]
    )

    df_user.columns = df_user.columns.str.upper()

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
        .str.contains("_im3"),
        "BRAND"
    ] = "IM3"

    df_user.loc[
        df_user["ATASAN"]
        .astype(str)
        .str.lower()
        .str.contains("_3id"),
        "BRAND"
    ] = "3ID"

    # =====================================================
    # SESSION
    # =====================================================

    role = st.session_state.outlet_role
    user = st.session_state.outlet_user

    # =====================================================
    # ⭐ HEADER (tampil duluan, sebelum filter)
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
                        <span class="dse-title-text">Dashboard DSE</span>
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
    # RELOAD DATA SESUAI RENTANG TANGGAL HASIL FILTER
    # =====================================================

    data = tampil_data_by_date(
        start_date,
        end_date
    )

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
            "flag_bio",
            "ga_dt"
        ]
    )

    df["Biometrik"] = (
        df["flag_bio"]
        .fillna(False)
        .astype(bool)
    )

    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"],
        errors="coerce"
    ).dt.date

    # =====================================================
    # FILTER: HANYA SUBMISSION DARI USER AKTIF.
    # User non-aktif tidak boleh muncul/dihitung di manapun
    # (dashboard maupun rekap) -- cukup dihitung di Vacant.
    # =====================================================

    df = df[
        df["Input By"]
        .astype(str)
        .str.strip()
        .isin(active_users_set)
    ]


    # =====================================================
    # MASTER DATA
    # =====================================================

    df_master = df.copy()

    st.divider()

    # =====================================================
    # FILTER ROLE
    # =====================================================

    if role in [

        "DSE",
        "PROMOTOR",
        "FRONTLINER"

    ]:

        df = df[
            df["Input By"] == user
        ]

    elif role in [

        "CSE",
        "RSE"

    ]:

        daftar_dse = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"].isin([

                "DSE"
            ]))

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(
                daftar_dse
            )
        ]

    elif role == "BSM":

        daftar_cse = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"].isin([

                "CSE",
                "RSE"

            ]))

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]["USER"].tolist()

        daftar_dse = df_user[

            (df_user["ATASAN"].isin(
                daftar_cse
            ))

            &

            (df_user["ROLE"].isin([

                "DSE"

            ]))

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(
                daftar_dse
            )
        ]

    elif role == "HOS":

        daftar_bsm = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "BSM")

            &

            (df_user["FLAG_ACTIVE"] == True)

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

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]["USER"].tolist()

        daftar_dse = df_user[

            (df_user["ATASAN"].isin(
                daftar_cse
            ))

            &

            (df_user["ROLE"].isin([

                "DSE"

            ]))

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(
                daftar_dse
            )
        ]

    else:

        daftar_dse = df_user[

            df_user["ROLE"].isin([

                "DSE"

            ])

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(
                daftar_dse
            )
        ]

    # =====================================================
    # FILTER BRAND DATA
    # =====================================================

    if brand != "Semua":

        user_brand = df_user[

            df_user["BRAND"] == brand

        ]["USER"].tolist()

        df = df[

            df["Input By"].isin(
                user_brand
            )

        ]

    # =====================================================
    # FILTER BRAND FUNCTION
    # =====================================================

    def filter_brand_df(dataframe):

        if brand == "IM3":

            return dataframe[

                dataframe["USER"]
                .astype(str)
                .str.upper()
                .str.contains("_IM3")

            ]

        elif brand == "3ID":

            return dataframe[

                dataframe["USER"]
                .astype(str)
                .str.upper()
                .str.contains("_3ID")

            ]

        return dataframe

# =====================================================
    # KPI ROLE AWARE
    # =====================================================

    if role in [

        "DSE",
        "PROMOTOR",
        "FRONTLINER"

    ]:

        total_dse = 1

        dse_aktif = (

            1

            if len(df[
                df["Input By"] == user
            ]) > 0

            else 0

        )

        daftar_user = [user]

    elif role in [

        "CSE",
        "RSE"

    ]:

        daftar_dse = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"].isin([

                "DSE"

            ]))

        ]["USER"].tolist()

        total_dse = len(
            daftar_dse
        )

        dse_aktif = df[
            df["Input By"].isin(
                daftar_dse
            )
        ]["Input By"].nunique()

        daftar_user = daftar_dse

    elif role == "BSM":

        daftar_cse = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"].isin([

                "CSE",
                "RSE"

            ]))

        ]["USER"].tolist()

        daftar_dse = df_user[

            (df_user["ATASAN"].isin(
                daftar_cse
            ))

            &

            (df_user["ROLE"].isin([

                "DSE"

            ]))

        ]["USER"].tolist()

        total_dse = len(
            daftar_dse
        )

        dse_aktif = df[
            df["Input By"].isin(
                daftar_dse
            )
        ]["Input By"].nunique()

        daftar_user = daftar_dse

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

        daftar_dse = df_user[

            (df_user["ATASAN"].isin(
                daftar_cse
            ))

            &

            (df_user["ROLE"].isin([

                "DSE"
            ]))

        ]["USER"].tolist()

        total_dse = len(
            daftar_dse
        )

        dse_aktif = df[
            df["Input By"].isin(
                daftar_dse
            )
        ]["Input By"].nunique()

        daftar_user = daftar_dse

    else:

        daftar_dse = df_user[

            df_user["ROLE"].isin([

                "DSE"
            ])

        ]["USER"].tolist()

        total_dse = len(
            daftar_dse
        )

        dse_aktif = df[
            df["Input By"].isin(
                daftar_dse
            )
        ]["Input By"].nunique()

        daftar_user = daftar_dse

    # =====================================================
    # JUMLAH VACANT = DSE dalam scope yang STATUS-nya
    # Non Aktif -> FLAG_ACTIVE == False
    #
    # daftar_user (daftar_dse) di atas HANYA berisi user
    # AKTIF (sudah difilter FLAG_ACTIVE == True di KPI ROLE
    # AWARE), jadi scope penuh (termasuk non-aktif) harus
    # diambil ulang di sini untuk hitung vacant.
    # =====================================================

    if role in ["DSE", "PROMOTOR", "FRONTLINER"]:

        daftar_dse_all = [user]

    elif role in ["CSE", "RSE"]:

        daftar_dse_all = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "DSE")

        ]["USER"].tolist()

    elif role == "BSM":

        daftar_cse_all = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"].isin(["CSE", "RSE"]))

        ]["USER"].tolist()

        daftar_dse_all = df_user[

            (df_user["ATASAN"].isin(daftar_cse_all))

            &

            (df_user["ROLE"] == "DSE")

        ]["USER"].tolist()

    elif role == "HOS":

        daftar_bsm_all = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "BSM")

        ]["USER"].tolist()

        daftar_cse_all = df_user[

            (df_user["ATASAN"].isin(daftar_bsm_all))

            &

            (df_user["ROLE"].isin(["CSE", "RSE"]))

        ]["USER"].tolist()

        daftar_dse_all = df_user[

            (df_user["ATASAN"].isin(daftar_cse_all))

            &

            (df_user["ROLE"] == "DSE")

        ]["USER"].tolist()

    else:

        daftar_dse_all = df_user[

            df_user["ROLE"] == "DSE"

        ]["USER"].tolist()

    user_master_all = df_user[

        df_user["USER"].isin(daftar_dse_all)

    ]

    jumlah_vacant = int(

        user_master_all[

            user_master_all["FLAG_ACTIVE"] == False

        ]["USER"].nunique()

    )

    # =====================================================
    # KPI TOTAL
    # =====================================================

    total_outlet = int(
        df["ID Outlet"]
        .dropna()
        .nunique()
    )

    total_msisdn = int(
        len(df.index)
    )

    total_bio = int(
        df["Biometrik"]
        .fillna(False)
        .sum()
    )

    # =====================================================
    # PERSENTASE
    # =====================================================

    persen_dse_aktif = round(

        (
            dse_aktif / total_dse
        ) * 100,

        2

    ) if total_dse > 0 else 0

    persen_bio = round(

        (
            total_bio / total_msisdn
        ) * 100,

        2

    ) if total_msisdn > 0 else 0

    # =====================================================
    # UI KPI
    # =====================================================

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        kpi_card("store", "Outlet", total_outlet, "#F5B400")

    with col2:
        kpi_card("groups", "DSE", total_dse, "#F0997B")

    with col3:
        kpi_card("person_off", "Vacant", jumlah_vacant, "#E8A33D")

    with col4:
        kpi_card("bolt", "DSE Aktif", dse_aktif, "#D4537E")

    with col5:
        kpi_card("trending_up", "% Aktif", f"{persen_dse_aktif}%", "#993556")

    with col6:
        kpi_card("smartphone", "MSISDN", total_msisdn, "#7A2C46")

    st.divider()
    # =====================================================
    # RESET SESSION KHUSUS CSE/RSE
    # =====================================================

    if role in [

        "CSE",
        "RSE"

    ]:

        st.session_state.selected_hos = None
        st.session_state.selected_bsm = None

    # =====================================================
    # HEADER
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

            section_title("", icon="list_alt")

    with reset_col:

        if st.button(

            "Reset",
            icon=":material/refresh:",

            use_container_width=True

        ):

            st.session_state.selected_hos = None
            st.session_state.selected_bsm = None
            st.session_state.selected_cse = None

            st.rerun()

    # =====================================================
    # DEFAULT SESSION
    # =====================================================

    if "selected_hos" not in st.session_state:

        st.session_state.selected_hos = None

    if "selected_bsm" not in st.session_state:

        st.session_state.selected_bsm = None

    if "selected_cse" not in st.session_state:

        st.session_state.selected_cse = None

    # =====================================================
    # GET SELECTED VALUE
    # =====================================================

    def get_selected_value(

        grid_response,
        column_name

    ):

        if grid_response is None:

            return None

        selected = grid_response.get(
            "selected_rows"
        )

        if selected is None:

            return None

        # ==========================================
        # DATAFRAME
        # ==========================================

        if isinstance(selected, pd.DataFrame):

            if selected.empty:

                return None

            if column_name not in selected.columns:

                return None

            return selected.iloc[0][
                column_name
            ]

        # ==========================================
        # LIST
        # ==========================================

        elif isinstance(selected, list):

            if len(selected) == 0:

                return None

            if column_name not in selected[0]:

                return None

            return selected[0][
                column_name
            ]

        return None
    # =====================================================
    # REKAP HOS
    # =====================================================

    if role == "ADMIN":

        rekap_hos = []

        hos_list = filter_brand_df(

            df_user[

                (df_user["ROLE"] == "HOS")

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]

        )

        for _, row in hos_list.iterrows():

            nama_hos = row["USER"]

            bsm_hos = df_user[

                (df_user["ATASAN"] == nama_hos)

                &

                (df_user["ROLE"] == "BSM")

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]
            daftar_bsm = bsm_hos["USER"].unique().tolist()


            daftar_cse = df_user[

                (df_user["ATASAN"].isin(
                    daftar_bsm
                ))

                &

                (df_user["ROLE"].isin([
                    "CSE",
                    "RSE"
                ]))

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]["USER"].unique().tolist()

            daftar_dse = df_user[

                (df_user["ATASAN"].isin(
                    daftar_cse
                ))

                &

                (df_user["ROLE"] == "DSE")

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]["USER"].drop_duplicates().tolist()

            temp = df[
                df["Input By"].isin(
                    daftar_dse
                )
            ]

            # =============================================
            # KPI
            # =============================================

            total_dse = len(daftar_dse)

            dse_aktif = temp[
                "Input By"
            ].nunique()

            total_msisdn = len(temp)

            total_bio = temp[
                "Biometrik"
            ].sum()

            persen_aktif = round(

                (
                    dse_aktif / total_dse
                ) * 100,

                2

            ) if total_dse > 0 else 0

            persen_bio = round(

                (
                    total_bio / total_msisdn
                ) * 100,

                2

            ) if total_msisdn > 0 else 0
            # =============================================
            # APPEND
            # =============================================

            rekap_hos.append({

                "HOS":
                    nama_hos,

                "Nama":
                    get_real_name(nama_hos), 

                "DSE":
                    total_dse,

                "DSE Aktif":
                    dse_aktif,

                "% DSE Aktif":
                    f"{persen_aktif}%",

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

        summary_hos = pd.DataFrame(
            rekap_hos
        )

        # ======================================================
        # FILTER BRAND
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

            summary_hos = summary_hos.sort_values(
                "MSISDN",
                ascending=False
            )

        with st.container(border=True):

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
                key=f"hos_{tanggal}_{role}_{user}"
            )

        selected_hos = get_selected_value(
            hos_grid,
            "HOS"
        )

        if selected_hos != st.session_state.selected_hos:

            st.session_state.selected_hos = (
                selected_hos
            )

            st.session_state.selected_bsm = None
            st.session_state.selected_cse = None

            st.rerun()

        st.divider()
    # =====================================================
    # REKAP BSM
    # =====================================================

    if role in ["ADMIN", "HOS"]:

        # =============================================
        # TITLE TABLE
        # =============================================

        if role == "ADMIN":

            section_title("Rekap BSM", icon="list_alt")

        rekap_bsm = []

        if role == "HOS":

            bsm_list = df_user[

                (df_user["ROLE"] == "BSM")

                &

                (df_user["ATASAN"] == user)

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]

        else:

            bsm_list = filter_brand_df(

               df_user[

                  (df_user["ROLE"] == "BSM")

                  &

                  (df_user["FLAG_ACTIVE"] == True)

               ]

            )

        for _, row in bsm_list.iterrows():

            if role == "ADMIN":

                if st.session_state.selected_hos:

                    if row["ATASAN"] != st.session_state.selected_hos:

                        continue


            nama_bsm = row["USER"]

            # =============================================
            # DOWNLINE
            # =============================================

            daftar_cse = df_user[

                (df_user["ATASAN"] == nama_bsm)

                &

                (df_user["ROLE"].isin([

                    "CSE",
                    "RSE"

                ]))

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]["USER"].drop_duplicates().tolist()

            daftar_dse = df_user[

                (df_user["ATASAN"].isin(
                    daftar_cse
                ))

                &

                (df_user["ROLE"] == "DSE")

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]["USER"].drop_duplicates().tolist()

            temp = df[

                df["Input By"].isin(
                    daftar_dse
                )

            ]
            total_dse = len(daftar_dse)

            dse_aktif = temp["Input By"].nunique()

            total_msisdn = len(temp)

            total_bio = temp["Biometrik"].sum()

            persen_aktif = round(
                (
                    dse_aktif / total_dse
                ) * 100,
                2
            ) if total_dse > 0 else 0

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

                "DSE":
                    total_dse,

                "DSE Aktif":
                    dse_aktif,

                "% DSE Aktif":
                    f"{persen_aktif}%",

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

            summary_bsm = summary_bsm.sort_values(
                "MSISDN",
                ascending=False
            )

        with st.container(border=True):

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
                key=f"bsm_{tanggal}_{role}_{user}"
            )

        selected_bsm = get_selected_value(
            bsm_grid,
            "BSM"
        )

        if selected_bsm != st.session_state.selected_bsm:

            st.session_state.selected_bsm = (
                selected_bsm
            )

            st.session_state.selected_cse = None

            st.rerun()

        st.divider()

    # =====================================================
    # REKAP CSE/RSE
    # =====================================================

    if role in ["ADMIN", "HOS", "BSM"]:

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

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]

        elif role == "HOS":

            daftar_bsm = df_user[

                (df_user["ATASAN"] == user)

                &

                (df_user["ROLE"] == "BSM")

                &

                (df_user["FLAG_ACTIVE"] == True)

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

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]

        else:

            cse_list = df_user[

                (df_user["ROLE"].isin([
                    "CSE",
                    "RSE"
                ]))

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]

            # ==========================================
            # FILTER HOS
            # ==========================================

            if st.session_state.selected_hos:

                daftar_bsm_hos = df_user[

                    df_user["ATASAN"]
                    == st.session_state.selected_hos

                ]["USER"].tolist()

                cse_list = cse_list[

                    cse_list["ATASAN"]
                    .isin(daftar_bsm_hos)

                ]

        for _, row in cse_list.iterrows():

            if role in ["ADMIN", "HOS"]:

                if st.session_state.selected_bsm:

                    if row["ATASAN"] != st.session_state.selected_bsm:

                        continue

            nama_cse = row["USER"]

            daftar_dse = df_user[

                (df_user["ATASAN"] == nama_cse)

                &

                (df_user["ROLE"] == "DSE")

                &

                (df_user["FLAG_ACTIVE"] == True)

            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(
                    daftar_dse
                )
            ]

            total_dse = len(daftar_dse)

            dse_aktif = temp["Input By"].nunique()

            total_msisdn = len(temp)

            total_bio = temp["Biometrik"].sum()

            persen_aktif = round(
                (
                    dse_aktif / total_dse
                ) * 100,
                2
            ) if total_dse > 0 else 0

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

                "DSE":
                    total_dse,

                "DSE Aktif":
                    dse_aktif,

                "% DSE Aktif":
                    f"{persen_aktif}%",

                "Outlet":
                    temp["ID Outlet"].nunique(),

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

                summary_cse["CSE/RSE"]
                .astype(str)
                .str.contains(
                    brand,
                    case=False,
                    na=False
                )

            ]

        if not summary_cse.empty:

            summary_cse = summary_cse.sort_values(
                "MSISDN",
                ascending=False
            )


        with st.container(border=True):

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
                key=f"cse_{tanggal}_{role}_{user}"
            )


        selected_cse = get_selected_value(
            cse_grid,
            "CSE/RSE"
        )

        if selected_cse:

            if st.session_state.selected_cse != selected_cse:

                st.session_state.selected_cse = (
                    selected_cse
                )

                st.rerun()

        st.divider()

    # =====================================================
    # REKAP DSE / PM / FL
    # =====================================================

    if role in [

        "ADMIN",
        "HOS",
        "BSM",
        "CSE",
        "RSE"

    ]:

        section_title("Rekap DSE", icon="list_alt")

        rekap_dse = []

        # =================================================
        # BASE USER
        # =================================================

        user_bawahan = df_user[

            (df_user["ROLE"].isin([

                "DSE"

            ]))

            &

            (df_user["FLAG_ACTIVE"] == True)

        ].copy()

        # =================================================
        # FILTER HIERARKI USER
        # =================================================

        if role in ["CSE", "RSE"]:

            filtered_user = user_bawahan[

                user_bawahan["ATASAN"] == user

            ]

        elif role == "BSM":

            daftar_cse = df_user[

                (df_user["ATASAN"] == user)

                &

                (df_user["ROLE"].isin([

                    "CSE",
                    "RSE"

                ]))

            ]["USER"].tolist()

            filtered_user = user_bawahan[

                user_bawahan["ATASAN"]
                .isin(daftar_cse)

            ]

            # CLICK CSE
            if st.session_state.selected_cse:

                filtered_user = filtered_user[

                    filtered_user["ATASAN"]
                    == st.session_state.selected_cse

                ]

        elif role == "HOS":

            daftar_bsm = df_user[

                (df_user["ATASAN"] == user)

                &

                (df_user["ROLE"] == "BSM")

            ]["USER"].tolist()

            daftar_cse = df_user[

                (df_user["ATASAN"]
                .isin(daftar_bsm))

                &

                (df_user["ROLE"].isin([

                    "CSE",
                    "RSE"

                ]))

            ]["USER"].tolist()

            filtered_user = user_bawahan[

                user_bawahan["ATASAN"]
                .isin(daftar_cse)

            ]

            # CLICK BSM
            if st.session_state.selected_bsm:

                daftar_cse_bsm = df_user[

                    (df_user["ATASAN"]
                    == st.session_state.selected_bsm)

                    &

                    (df_user["ROLE"].isin([

                        "CSE",
                        "RSE"

                    ]))

                ]["USER"].tolist()

                filtered_user = filtered_user[

                    filtered_user["ATASAN"]
                    .isin(daftar_cse_bsm)

                ]

            # CLICK CSE
            if st.session_state.selected_cse:

                filtered_user = filtered_user[

                    filtered_user["ATASAN"]
                    == st.session_state.selected_cse

                ]

        else:

            filtered_user = user_bawahan.copy()

            # CLICK HOS
            if st.session_state.selected_hos:

                daftar_bsm = df_user[

                    df_user["ATASAN"]
                    == st.session_state.selected_hos

                ]["USER"].tolist()

                daftar_cse = df_user[

                    (df_user["ATASAN"]
                    .isin(daftar_bsm))

                    &

                    (df_user["ROLE"].isin([

                        "CSE",
                        "RSE"

                    ]))

                ]["USER"].tolist()

                filtered_user = filtered_user[

                    filtered_user["ATASAN"]
                    .isin(daftar_cse)

                ]

            # CLICK BSM
            if st.session_state.selected_bsm:

                daftar_cse = df_user[

                    (df_user["ATASAN"]
                    == st.session_state.selected_bsm)

                    &

                    (df_user["ROLE"].isin([

                        "CSE",
                        "RSE"

                    ]))

                ]["USER"].tolist()

                filtered_user = filtered_user[

                    filtered_user["ATASAN"]
                    .isin(daftar_cse)

                ]

            # CLICK CSE
            if st.session_state.selected_cse:

                filtered_user = filtered_user[

                    filtered_user["ATASAN"]
                    == st.session_state.selected_cse

                ]

        # =================================================
        # LOOP FINAL
        # =================================================

        for _, row in filtered_user.iterrows():

            nama_user = row["USER"]

            # =============================================
            # PAKAI DF YANG SUDAH FILTER TANGGAL
            # =============================================

            temp = df[

                df["Input By"] == nama_user

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

            rekap_dse.append({

                "DSE":
                    nama_user,

                "Nama":
                    get_real_name(nama_user),

                "Upline":
                    row["ATASAN"],

                "Status":
                    status_user,

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

        summary_dse = pd.DataFrame(
            rekap_dse
        )

        # ======================================================
        # FILTER BRAND
        # ======================================================

        if brand != "Semua":

            summary_dse = summary_dse[

                summary_dse["Upline"]
                .astype(str)
                .str.contains(
                    brand,
                    case=False,
                    na=False
                )

            ]
        if not summary_dse.empty:

            summary_dse = summary_dse.sort_values(

                "MSISDN",

                ascending=False

            )


        with st.container(border=True):

            st.download_button(
                label=":material/download: Download Rekap DSE",
                data=to_excel(summary_dse),
                file_name="rekap_dse_pm_fl.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_dse"
            )

            show_grid(
                summary_dse,
                selectable=False,
                key=f"dse"
            )