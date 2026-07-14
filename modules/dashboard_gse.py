# ==========================================================
# IMPORT
# ==========================================================

import streamlit as st
import pandas as pd

from st_aggrid import (
    AgGrid,
    GridOptionsBuilder
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

    st.title("📊 Dashboard GSE")

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
            "Tanggal"

        ]

    )
    # ======================================================
    #     # ======================================================
    # BIOMETRIK
    # ======================================================

    biometrik = load_biometrik()

    df["MSISDN"] = (
        df["MSISDN"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["Tanggal"] = pd.to_datetime(
        df["Tanggal"],
        errors="coerce"
    )

    df = df.merge(
        biometrik,
        left_on="MSISDN",
        right_on="msisdn",
        how="left"
    )

    df.drop(
        columns=["msisdn"],
        inplace=True
    )

    df["Biometrik"] = (

        (

            df["Tanggal"]

            .dt.date

            ==

            pd.to_datetime(

                df["tanggal_biometrik"],

                errors="coerce"

            )

            .dt.date

        )

        .fillna(False)

        .astype(int)

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

        df_user["ROLE"].isin([

            "GSE"

        ])

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

            df_user["ROLE"].isin([

                "GSE"

            ])

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

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "👤 GSE",
        total_user
    )

    col2.metric(
        "🔥 GSE Aktif",
        user_aktif
    )

    col3.metric(
        "% GSE Aktif",
        f"{persen_user_aktif}%"
    )

    col4.metric(
        "📱 MSISDN",
        total_msisdn
    )


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

            "⬇️ Download Detail Input",

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

            st.subheader(
                "📋 Rekap GSE"
            )

        with reset_col:

            if st.button(

                "🔄 Reset",

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

            "⬇️ Download Rekap GSE",

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

            st.subheader(
                "📋 Rekap BSM"
            )

        with reset_col:

            if st.button(

                "🔄 Reset",

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
        ]["USER"].tolist()

        for bsm in daftar_bsm:

            bawahan = df_user[

                (df_user["ATASAN"] == bsm)

                &

                (df_user["ROLE"].isin([

                    "GSE"

                ]))

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
                    get_real_name(nama_bsm), 

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

            "⬇️ Download Rekap BSM",

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

        st.subheader(
            "📋 Rekap GSE"
        )

        rekap_cse = []

        for bsm in daftar_bsm:

            bawahan = df_user[
                (df_user["ATASAN"] == bsm)
                &
                (df_user["ROLE"].isin([
                    "GSE"
                ]))
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

            "⬇️ Download Rekap GSE",

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

            st.subheader(
                "📋 Rekap HOS"
            )

        with reset_col:

            if st.button(

                "🔄 Reset",

                use_container_width=True,

                key="reset_admin"

            ):

                st.session_state.selected_hos = None
                st.session_state.selected_bsm = None
                st.session_state.selected_cse = None

                st.rerun()

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

                (df_user["ATASAN"]
                .isin(daftar_bsm))

                &

                (df_user["ROLE"].isin([

                    "GSE"

                ]))

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

            "⬇️ Download Rekap HOS",

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

        st.subheader(
            "📋 Rekap BSM"
        )

        rekap_bsm = []

        bsm_list = df_user[
            df_user["ROLE"] == "BSM"
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

            "⬇️ Download Rekap BSM",

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

        st.subheader(
            "📋 Rekap GSE"
        )

        rekap_cse = []

        cse_list = df_user[

            df_user["ROLE"].isin([

                "GSE"

            ])

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

            "⬇️ Download Rekap GSE",

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