# =========================================================
# dashboard_frontliner.py
# DASHBOARD FRONTLINER
# HOS -> BSM -> CSE/RSE -> FRONTLINER
# =========================================================

import streamlit as st
import pandas as pd
from io import BytesIO

from st_aggrid import (
    AgGrid,
    GridOptionsBuilder,
    GridUpdateMode
)

from database import (
    tampil_data_by_date,
    get_latest_data_date,
    tampil_user,
    load_biometrik
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

                "border": "1px solid #e5e7eb",
                "border-radius": "14px"

            },

            ".ag-header": {

                "background-color": "#f8fafc",
                "font-weight": "700"

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
            ".ag-cell:first-child": {

                "justify-content": "flex-start !important",
                "text-align": "left !important",
                "padding-left": "12px"

            },

            # Khusus header kolom pertama rata kiri
            ".ag-header-cell:first-child .ag-header-cell-label": {

                "justify-content": "flex-start !important",
                "padding-left": "12px"

            },

            ".ag-row": {

                "font-size": "14px"

            },

            ".ag-pinned-bottom": {

                "background-color": "#eef2ff",
                "font-weight": "700",
                "border-top": "2px solid #6366f1",
                "min-height": "42px"

            }

        }

    )
    return grid_response
# =========================================================
# DASHBOARD
# =========================================================

def show():

    st.title("📊 Dashboard Frontliner")

    # =====================================================
    # TENTUKAN TANGGAL & BRAND DULU, SEBELUM LOAD DATA
    # =====================================================

    col_tgl, col_brand = st.columns(2)

    with col_tgl:

        tanggal = st.date_input(
            "📅 Filter Tanggal",
            value=None,
            key="fl_tanggal"
        )

    if tanggal is None:
        tanggal = get_latest_data_date()

    with col_brand:

        brand = st.selectbox(
            "📶 Filter Brand",
            options=["Semua", "IM3", "3ID"],
            index=0
        )

    # =====================================================
    # LOAD DATA HANYA UNTUK TANGGAL TERPILIH
    # =====================================================

    data = tampil_data_by_date(tanggal, tanggal)
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
            "flag_bio"
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
    # KPI UI (6 COL DSE STYLE)
    # =========================

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "🏪 Outlet",
        jumlah_outlet
    )

    col2.metric(
        "👤 Frontliner",
        total_fl
    )

    col3.metric(
        "🔥 FL Aktif",
        fl_aktif
    )

    col4.metric(
        "📱 MSISDN",
        jumlah_msisdn
    )

    col5.metric(
        "📊 % FL Aktif",
        f"{persen_fl_aktif}%"
    )

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

    if role == "ADMIN":

        title_rekap = "📋 Rekap HOS"

    elif role == "HOS":

        title_rekap = "📋 Rekap BSM"

    elif role == "BSM":

        title_rekap = "📋 Rekap CSE/RSE"

    else:

        title_rekap = "📋 Rekap Frontliner"

    header_col, reset_col = st.columns([5, 1])

    with header_col:

        st.subheader(title_rekap)

    with reset_col:

        if st.button(
            "🔄 Reset",
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
                .str.contains(
                    brand,
                    case=False,
                    na=False
                )

            ]


        hos_grid = show_grid(

            summary_hos,

            selectable=True,

            key=f"hos_{tanggal}_{role}_{user}",
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

        selected_hos = get_selected_value(
            hos_grid,
            "HOS"
        )

        if selected_hos:

            st.session_state.selected_hos_fl = (
                selected_hos
            )

            st.session_state.selected_bsm_fl = None
            st.session_state.selected_cse_fl = None

        buffer = BytesIO()

        with pd.ExcelWriter(
            buffer,
            engine="openpyxl"
        ) as writer:

            summary_hos.to_excel(
                writer,
                index=False
            )

        st.download_button(

            "📥 Download HOS",

            buffer.getvalue(),

            file_name="rekap_hos.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        )

        st.divider()

    # =====================================================
    # REKAP BSM
    # =====================================================

    if role in ["HOS", "ADMIN"]:

        if role == "ADMIN":

            st.markdown("### 📋 Rekap BSM")

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

            "📥 Download BSM",

            buffer.getvalue(),

            file_name="rekap_bsm.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        )

        st.divider()

    # =====================================================
    # REKAP CSE/RSE
    # =====================================================

    if role in ["BSM", "HOS", "ADMIN"]:

        if role in ["ADMIN", "HOS"]:

            st.subheader("📋 Rekap CSE/RSE")

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

            "📥 Download CSE/RSE",

            buffer.getvalue(),

            file_name="rekap_cse.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        )

        st.divider()

    # =====================================================
    # REKAP FRONTLINER
    # =====================================================
    if role not in ["CSE", "RSE"]:
       st.subheader("📋 Rekap Frontliner")

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

    # =====================================================
    # FILTER BRAND
    # =====================================================

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

        "📥 Download Frontliner",

        buffer.getvalue(),

        file_name="rekap_frontliner.xlsx",

        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )