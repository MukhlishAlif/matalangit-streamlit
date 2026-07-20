# =========================================================
# dashboard_dse.py
# DASHBOARD HIERARCHY DSE
# Hierarki: HOS -> BSM -> GEMINI (CSE/RSE dihilangkan)
# =========================================================

import streamlit as st
import pandas as pd
from io import BytesIO
import requests
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
        "Branch": 170,
        "Atasan": 170,
        "Nama": 200,
        "Role": 120,
        "Upline": 180,
        "Status": 140,

        "GEMPI": 200,
        "GEMPI Aktif": 120,
        "Outlet": 100,
        "MSISDN": 110,
        "Biometrik": 110,
        "% GEMPI Aktif": 130,
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

        elif field == "Nama":

            # Paksa rata tengah, override cellStyle apapun yang mungkin
            # sudah di-set sebelumnya di gb.configure_column().
            col["cellStyle"] = {

                "textAlign": "Left",
                "display": "flex",
                "justifyContent": "Left",
                "alignItems": "Left"

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
                <span class="dse-title-text">Dashboard GEMPI</span>
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
    # NOTE: tampil_user() sekarang mengembalikan juga kolom
    # "status" dan "flag_active" (sama seperti di dashboard
    # DSE Promotor), sehingga user non-aktif bisa dibedakan
    # dari user aktif.
    # =====================================================

    df_user = pd.DataFrame(

        users,

        columns=[

            "user",
            "role",
            "atasan",
            "real_name",
            "status",
            "flag_active",
            "join_date"

        ]

    )

    df_user.columns = (
        df_user.columns.str.upper()
    )

    # =====================================================
    # FLAG_ACTIVE: True = Aktif (tampil di rekap & dashboard),
    # False = Non Aktif (HANYA dihitung di KPI Vacant)
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

            return username

        return nama

    join_date_map = (
        df_user
        .drop_duplicates(subset="USER")
        .assign(
            USER=lambda x: x["USER"]
            .astype(str)
            .str.strip()
            .str.upper()
        )
        .set_index("USER")["JOIN_DATE"]
        .to_dict()
    )

    def get_join_date(username):

        key = str(username).strip().upper()

        tgl = join_date_map.get(key)

        if pd.isna(tgl) or str(tgl).strip() == "":

            return "-"

        return tgl


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
    # FILTER
    # =====================================================

    df["Tanggal"] = pd.to_datetime(

        df["Tanggal"],

        errors="coerce"

    ).dt.date

    # =====================================================
    # MASTER DATA
    # =====================================================

    df_master = df.copy()

    st.divider()

    # =====================================================
    # FILTER ROLE
    # Hierarki: HOS -> BSM -> GEMINI (CSE/RSE dihilangkan)
    # Hanya GEMINI yang FLAG_ACTIVE == True yang dimasukkan
    # ke dalam scope perhitungan dashboard.
    # =====================================================

    if role in [

        "GEMINI"

    ]:

        df = df[
            df["Input By"] == user
        ]

    elif role == "BSM":

        daftar_dse = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"].isin([

                "GEMINI"
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

        ]["USER"].tolist()

        daftar_dse = df_user[

            (df_user["ATASAN"].isin(
                daftar_bsm
            ))

            &

            (df_user["ROLE"].isin([

                "GEMINI"

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

            (df_user["ROLE"].isin([

                "GEMINI"

            ]))

            &

            (df_user["FLAG_ACTIVE"] == True)

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(
                daftar_dse
            )
        ]

    # =====================================================
    # FILTER: HANYA SUBMISSION DARI USER AKTIF.
    # Jaring pengaman tambahan (sama seperti di dashboard
    # DSE Promotor) supaya user non-aktif tidak pernah
    # muncul/terhitung di manapun selain KPI Vacant, walau
    # ada role/cabang baru yang lupa difilter di atas.
    # =====================================================

    df = df[
        df["Input By"]
        .astype(str)
        .str.strip()
        .isin(active_users_set)
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
    # daftar_dse_scope = SEMUA GEMPI dalam scope (termasuk
    # non-aktif) -- dipakai HANYA untuk hitung Vacant.
    # daftar_dse       = GEMPI AKTIF saja -- dipakai untuk
    # total_dse & dse_aktif (KPI selain Vacant).
    # =====================================================

    if role in [

        "GEMINI"

    ]:

        daftar_dse_scope = [user]

        daftar_dse = [
            u for u in daftar_dse_scope
            if str(u).strip() in active_users_set
        ]

        total_dse = len(daftar_dse)

        dse_aktif = (

            1

            if len(df[
                df["Input By"] == user
            ]) > 0

            else 0

        )

    elif role == "BSM":

        daftar_dse_scope = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"].isin([

                "GEMINI"

            ]))

        ]["USER"].tolist()

        daftar_dse = [
            u for u in daftar_dse_scope
            if str(u).strip() in active_users_set
        ]

        total_dse = len(
            daftar_dse
        )

        dse_aktif = df[
            df["Input By"].isin(
                daftar_dse
            )
        ]["Input By"].nunique()

    elif role == "HOS":

        daftar_bsm = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "BSM")

        ]["USER"].tolist()

        daftar_dse_scope = df_user[

            (df_user["ATASAN"].isin(
                daftar_bsm
            ))

            &

            (df_user["ROLE"].isin([

                "GEMINI"
            ]))

        ]["USER"].tolist()

        daftar_dse = [
            u for u in daftar_dse_scope
            if str(u).strip() in active_users_set
        ]

        total_dse = len(
            daftar_dse
        )

        dse_aktif = df[
            df["Input By"].isin(
                daftar_dse
            )
        ]["Input By"].nunique()

    else:

        daftar_dse_scope = df_user[

            df_user["ROLE"].isin([

                "GEMINI"
            ])

        ]["USER"].tolist()

        daftar_dse = [
            u for u in daftar_dse_scope
            if str(u).strip() in active_users_set
        ]

        total_dse = len(
            daftar_dse
        )

        dse_aktif = df[
            df["Input By"].isin(
                daftar_dse
            )
        ]["Input By"].nunique()

    # =====================================================
    # JUMLAH VACANT = GEMPI dalam scope yang STATUS-nya
    # Non Aktif -> FLAG_ACTIVE == False
    # =====================================================

    user_master = (
        df_user[
            df_user["USER"].isin(daftar_dse_scope)
        ]
        .drop_duplicates(subset="USER")
    )

    jumlah_vacant = int(

        user_master[

            user_master["FLAG_ACTIVE"] == False

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

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        kpi_card("group", "GEMPI", total_dse, "#F5B400")

    with col2:
        kpi_card("person_off", "Vacant", jumlah_vacant, "#E8A33D")

    with col3:
        kpi_card("bolt", "GEMPI Aktif", dse_aktif, "#F0997B")

    with col4:
        kpi_card("trending_up", "% GEMPI Aktif", f"{persen_dse_aktif}%", "#D4537E")

    with col5:
        kpi_card("smartphone", "MSISDN", total_msisdn, "#993556")

    st.divider()

    # =====================================================
    # HEADER
    # =====================================================

    header_col, reset_col = st.columns([5, 1])

    with header_col:

        if role == "ADMIN":

            section_title("Rekap HOS", icon="list_alt")

        elif role == "HOS":

            section_title("Rekap BSM", icon="list_alt")

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

            st.rerun()

    # =====================================================
    # DEFAULT SESSION
    # =====================================================

    if "selected_hos" not in st.session_state:

        st.session_state.selected_hos = None

    if "selected_bsm" not in st.session_state:

        st.session_state.selected_bsm = None

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

            daftar_bsm = df_user[

                (df_user["ATASAN"] == nama_hos)

                &

                (df_user["ROLE"] == "BSM")

            ]["USER"].unique().tolist()

            # =========================================
            # GEMINI = langsung ATASAN-nya BSM
            # Hanya yang FLAG_ACTIVE == True
            # =========================================

            daftar_dse = df_user[

                (df_user["ROLE"] == "GEMINI")

                &

                (df_user["ATASAN"].isin(
                    daftar_bsm
                ))

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

            # =============================================
            # APPEND
            # =============================================
            rekap_hos.append({
                "HOS":
                    nama_hos,

                "Nama":
                    get_real_name(nama_hos),

                "GEMPI":
                    total_dse,
                "GEMPI Aktif":
                    dse_aktif,
                "% GEMPI Aktif":
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
            # GEMINI = langsung ATASAN-nya BSM ini
            # Hanya yang FLAG_ACTIVE == True
            # =============================================

            daftar_dse = df_user[

                (df_user["ROLE"] == "GEMINI")

                &

                (df_user["ATASAN"] == nama_bsm)

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
                "GEMPI":
                    total_dse,
                "GEMPI Aktif":
                    dse_aktif,
                "% GEMPI Aktif":
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

            st.rerun()

        st.divider()

    # =====================================================
    # REKAP DSE / GEMINI
    # =====================================================

    if role in [

        "ADMIN",
        "HOS",
        "BSM"

    ]:

        section_title("Rekap GEMPI", icon="list_alt")

        rekap_dse = []

        # =================================================
        # BASE USER
        # Hanya GEMINI dengan FLAG_ACTIVE == True yang
        # ditampilkan di rekap.
        # =================================================

        user_bawahan = df_user[

            (df_user["ROLE"].isin([

                "GEMINI"

            ]))

            &

            (df_user["FLAG_ACTIVE"] == True)

        ].copy()

        # =================================================
        # FILTER HIERARKI USER
        # =================================================

        if role == "BSM":

            filtered_user = user_bawahan[

                user_bawahan["ATASAN"] == user

            ]

        elif role == "HOS":

            daftar_bsm = df_user[

                (df_user["ATASAN"] == user)

                &

                (df_user["ROLE"] == "BSM")

            ]["USER"].tolist()

            filtered_user = user_bawahan[

                user_bawahan["ATASAN"]
                .isin(daftar_bsm)

            ]

            # CLICK BSM
            if st.session_state.selected_bsm:

                filtered_user = filtered_user[

                    filtered_user["ATASAN"]
                    == st.session_state.selected_bsm

                ]

        else:

            filtered_user = user_bawahan.copy()

            # CLICK HOS
            if st.session_state.selected_hos:

                daftar_bsm = df_user[

                    df_user["ATASAN"]
                    == st.session_state.selected_hos

                ]["USER"].tolist()

                filtered_user = filtered_user[

                    filtered_user["ATASAN"]
                    .isin(daftar_bsm)

                ]

            # CLICK BSM
            if st.session_state.selected_bsm:

                filtered_user = filtered_user[

                    filtered_user["ATASAN"]
                    == st.session_state.selected_bsm

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

                "GEMPI":
                    nama_user,

                "Nama":
                    get_real_name(nama_user),

                "Join Date":
                    get_join_date(nama_user),

                "Role":
                    row["ROLE"],

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

        st.download_button(

            label=":material/download: Download Rekap",

            data=to_excel(summary_dse),

            file_name="rekap_dse_pm_fl.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key="download_gemini"

        )

        show_grid(

            summary_dse,

            selectable=False,

            key="GEMINI"

        )