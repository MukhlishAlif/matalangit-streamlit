# ==========================================================
# IMPORT
# ==========================================================

import streamlit as st
import pandas as pd

from st_aggrid import (
    AgGrid,
    GridOptionsBuilder,
    GridUpdateMode
)

from io import BytesIO

from database import (
    tampil_data_by_date,
    get_latest_data_date,
    tampil_user,
    load_biometrik
)


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
    # FIX WIDTH + FREEZE FIRST COLUMN + ALIGNMENT
    # =====================================================

    first_col = df.columns[0]

    for col in grid_options["columnDefs"]:

        field = col["field"]

        max_len = max(
            len(str(field)),
            df[field].fillna("").astype(str).str.len().max()
        )

        width = max(140, min(max_len * 12 + 50, 500))

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

        # Freeze kolom pertama (tetap seperti semula)
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

                "background-color": "#f8fafc",
                "font-weight": "700"

            },

            ".ag-header-cell-label": {

                "display": "flex",
                "justify-content": "center",
                "align-items": "center",
                "width": "100%",
                "text-align": "center"

            },

            ".ag-cell": {

                "display": "flex",
                "justify-content": "center",
                "align-items": "center",
                "text-align": "center"

            },

            ".ag-pinned-left-cols-container .ag-cell": {

                "justify-content": "flex-start !important",
                "text-align": "left !important",
                "padding-left": "12px"

            },

            ".ag-pinned-left-header .ag-header-cell-label": {

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

    st.title("📊 Dashboard BSM")

    # ======================================================
    # TENTUKAN TANGGAL DULU, SEBELUM LOAD DATA APAPUN
    # ======================================================

    col_tgl, col_brand = st.columns(2)

    with col_tgl:

        tanggal = st.date_input(
            "📅 Filter Tanggal",
            value=None,
            key="bsm_tanggal"
        )

    if tanggal is None:
        tanggal = get_latest_data_date()

    with col_brand:

        brand = st.selectbox(
            "📶 Filter Brand",
            options=["Semua", "IM3", "3ID"],
            index=0
        )

    # ======================================================
    # LOAD DATA HANYA UNTUK TANGGAL TERPILIH
    # ======================================================

    data = tampil_data_by_date(tanggal, tanggal)
    users = tampil_user()

    # ======================================================
    # USER DATAFRAME
    # ======================================================

    df_user = pd.DataFrame(
        [dict(row) for row in users]
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

        nama_str = str(nama).strip().upper()

        if (
            pd.isna(nama)
            or nama_str in ["", "VACANT", "NAN", "NONE"]
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

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(bawahan)
        ]

    # role == "ADMIN" -> tidak difilter, lihat semua

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

        df_user["ROLE"] == "BSM"

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

    elif role == "HOS":

        daftar_user = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "BSM")

        ]["USER"].tolist()

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
    # UI KPI
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "👤 BSM",
        total_user
    )

    col2.metric(
        "🔥 BSM Aktif",
        user_aktif
    )

    col3.metric(
        "% BSM Aktif",
        f"{persen_user_aktif}%"
    )

    col4.metric(
        "📱 MSISDN",
        total_msisdn
    )

    st.divider()

    # ======================================================
    # BSM (LEAF - INPUT SENDIRI)
    # ======================================================

    if role == "BSM":

        st.subheader(
            "📋 Detail Input"
        )

        detail_df = df[[

            "Nama Outlet",
            "ID Outlet",
            "MSISDN",
            "Biometrik",
            "Tanggal"

        ]]

        st.download_button(

            "⬇️ Download Detail Input",

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

            st.subheader(
                "📋 Rekap BSM"
            )

        with reset_col:

            if st.button(

                "🔄 Reset",

                use_container_width=True,

                key="reset_hos_bsm"

            ):

                st.rerun()

        rekap_bsm = []

        daftar_bsm = df_user[

            (df_user["ATASAN"] == user)

            &

            (df_user["ROLE"] == "BSM")

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

        st.download_button(

            "⬇️ Download Rekap BSM",

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

        selected_hos = None

        # ==================================================
        # REKAP HOS
        # ==================================================

        header_col, reset_col = st.columns([5, 1])

        with header_col:

            st.subheader(
                "📋 Rekap HOS"
            )

        with reset_col:

            if st.button(

                "🔄 Reset",

                use_container_width=True,

                key="reset_admin_bsm"

            ):

                st.session_state.selected_hos_bsm = None
                st.rerun()

        rekap_hos = []

        hos_list = df_user[
            df_user["ROLE"] == "HOS"
        ]

        for _, row in hos_list.iterrows():

            nama_hos = row["USER"]

            daftar_bsm = df_user[

                (df_user["ATASAN"] == nama_hos)

                &

                (df_user["ROLE"] == "BSM")

            ]["USER"].tolist()

            temp = df[
                df["Input By"]
                .isin(daftar_bsm)
            ]

            total_bsm = len(daftar_bsm)

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

        st.download_button(

            "⬇️ Download Rekap HOS",

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

        st.session_state.selected_hos_bsm = selected_hos

        st.divider()

        # ==================================================
        # REKAP BSM
        # ==================================================

        st.subheader(
            "📋 Rekap BSM"
        )

        rekap_bsm = []

        bsm_list = df_user[
            df_user["ROLE"] == "BSM"
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

        st.download_button(

            "⬇️ Download Rekap BSM",

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