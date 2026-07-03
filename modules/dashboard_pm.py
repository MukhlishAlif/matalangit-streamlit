
# =========================================================
# dashboard_promotor.py
# DASHBOARD PROMOTOR
# HOS -> BSM -> CSE/RSE -> PROMOTOR
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
    tampil_data,
    tampil_user
)

# =========================================================
# LOAD BIOMETRIK
# =========================================================

@st.cache_data
def load_biometrik():

    biometrik = pd.read_csv(
        "ga_biometrics_cj.csv",
        dtype=str,
        low_memory=False
    )

    biometrik.columns = (
        biometrik.columns
        .str.strip()
        .str.lower()
    )

    biometrik["msisdn"] = (
        biometrik["msisdn"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    biometrik["tanggal_biometrik"] = pd.to_datetime(
        biometrik["ga_dt"],
        errors="coerce"
    ).dt.date

    return biometrik[
        [
            "msisdn",
            "tanggal_biometrik"
        ]
    ].drop_duplicates()

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
    key=None
):

    if df.empty:

        st.info("Tidak ada data.")
        return None

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

    gb.configure_default_column(

        resizable=True,
        sortable=True,
        filter=True

    )

    if selectable:

        gb.configure_selection(

            selection_mode="single",
            use_checkbox=False

        )

    gb.configure_grid_options(

        headerHeight=45,
        rowHeight=42,
        domLayout="normal"

    )

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
                "Promotor",
                "Atasan"

            ]:

                total_row[col] = (
                    df[col].nunique()
                )

            else:

                total_row[col] = ""

    grid_options = gb.build()

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

        fit_columns_on_grid_load=True,

        update_mode=GridUpdateMode.SELECTION_CHANGED,

        height=table_height,

        theme="balham",

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

    st.title("📊 Dashboard Promotor")

    # =====================================================
    # LOAD DATA
    # =====================================================

    data = tampil_data()

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
            "Tanggal"

        ]

    )

    # =====================================================
    # BIOMETRIK
    # =====================================================

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

    ).dt.date

    df = df.merge(

        biometrik,

        left_on="MSISDN",

        right_on="msisdn",

        how="left"

    )

    df["Biometrik"] = (

        df["Tanggal"]

        ==

        df["tanggal_biometrik"]

    )

    df.drop(

        columns=[

            "msisdn",
            "tanggal_biometrik"

        ],

        inplace=True

    )

    # =====================================================
    # USER DF
    # =====================================================

    df_user = pd.DataFrame(

        users,

        columns=[

            "USER",
            "ROLE",
            "ATASAN"

        ]

    )

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

    tanggal = st.date_input(

        "📅 Filter Tanggal",

        value=None,

        key="pm_tanggal"

    )

    if tanggal:

        df = df[
            df["Tanggal"] == tanggal
        ]

    st.divider()

    # =====================================================
    # FILTER ROLE
    # =====================================================

    if role == "PROMOTOR":

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

            (df_user["ROLE"] == "PROMOTOR")

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

            (df_user["ROLE"] == "PROMOTOR")

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

            (df_user["ROLE"] == "PROMOTOR")

        ]["USER"].tolist()

        df = df[
            df["Input By"]
            .isin(daftar_promotor)
        ]

    # =====================================================
    # KPI PROMOTOR (STYLE DSE)
    # =====================================================

    promotor_all = df_user[
        df_user["ROLE"] == "PROMOTOR"
    ]["USER"].tolist()

    df_promotor = df[
        df["Input By"].isin(promotor_all)
    ]

    total_promotor = len(promotor_all)

    promotor_aktif = df_promotor["Input By"].nunique()

    jumlah_outlet = df_promotor["ID Outlet"].nunique()

    jumlah_msisdn = len(df_promotor)

    jumlah_biometrik = df_promotor["Biometrik"].sum()

    persen_aktif = round(
        (promotor_aktif / total_promotor) * 100,
        2
    ) if total_promotor > 0 else 0

    persen_bio = round(
        (jumlah_biometrik / jumlah_msisdn) * 100,
        2
    ) if jumlah_msisdn > 0 else 0

    # =====================================================
    # UI KPI (DSE STYLE)
    # =====================================================

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("👤 Total Promotor", total_promotor)
    col2.metric("🔥 Promotor Aktif", promotor_aktif)
    col3.metric("% User Aktif", f"{persen_aktif}%")
    col4.metric("🏪 Outlet", jumlah_outlet)
    col5.metric("📱 MSISDN", jumlah_msisdn)
    col6.metric("% Biometrik", f"{persen_bio}%")

    st.divider()

    # =========================================================
    # HIERARCHY FILTER
    # =========================================================

    selected_hos = None
    selected_bsm = None
    selected_cse = None

    # =========================================================
    # REKAP HOS
    # =========================================================

    if role == "ADMIN":

        st.subheader("📋 Rekap HOS")

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

            daftar_promotor = df_user[
                (df_user["ATASAN"].isin(daftar_cse))
                &
                (df_user["ROLE"] == "PROMOTOR")
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_promotor)
            ]

            total_promotor = len(daftar_promotor)
            promotor_aktif = temp["Input By"].nunique()
            total_msisdn = len(temp)
            total_bio = temp["Biometrik"].sum()

            persen_aktif = round(
                (promotor_aktif / total_promotor) * 100,
                2
            ) if total_promotor > 0 else 0

            persen_bio = round(
                (total_bio / total_msisdn) * 100,
                2
            ) if total_msisdn > 0 else 0

            rekap_hos.append({
                "HOS": nama_hos,
                "BSM": len(daftar_bsm),
                "CSE/RSE": len(daftar_cse),
                "Promotor": total_promotor,
                "Promotor Aktif": promotor_aktif,
                "% User Aktif": f"{persen_aktif}%",
                "Outlet": temp["ID Outlet"].nunique(),
                "MSISDN": total_msisdn,
                "Biometrik": total_bio,
                "% Biometrik": f"{persen_bio}%"
            })

        summary_hos = pd.DataFrame(rekap_hos)

        if not summary_hos.empty:
            summary_hos = summary_hos.sort_values(
                "MSISDN",
                ascending=False
            )

        hos_grid = show_grid(
            summary_hos,
            selectable=True,
            key="hos"
        )

        selected_hos = get_selected_value(
            hos_grid,
            "HOS"
        )

        st.divider()

    # =========================================================
    # REKAP BSM
    # =========================================================

    if role in ["HOS", "ADMIN"]:

        st.subheader("📋 Rekap BSM")

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
                    "CSE",
                    "RSE"
                ]))
            ]["USER"].tolist()

            daftar_promotor = df_user[
                (df_user["ATASAN"].isin(daftar_cse))
                &
                (df_user["ROLE"] == "PROMOTOR")
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_promotor)
            ]

            total_promotor = len(daftar_promotor)
            promotor_aktif = temp["Input By"].nunique()
            total_msisdn = len(temp)
            total_bio = temp["Biometrik"].sum()

            persen_aktif = round(
                (promotor_aktif / total_promotor) * 100,
                2
            ) if total_promotor > 0 else 0

            persen_bio = round(
                (total_bio / total_msisdn) * 100,
                2
            ) if total_msisdn > 0 else 0

            rekap_bsm.append({
                "BSM": nama_bsm,
                "CSE/RSE": len(daftar_cse),
                "Promotor": total_promotor,
                "Promotor Aktif": promotor_aktif,
                "% User Aktif": f"{persen_aktif}%",
                "Outlet": temp["ID Outlet"].nunique(),
                "MSISDN": total_msisdn,
                "Biometrik": total_bio,
                "% Biometrik": f"{persen_bio}%"
            })

        summary_bsm = pd.DataFrame(rekap_bsm)

        if not summary_bsm.empty:
            summary_bsm = summary_bsm.sort_values(
                "MSISDN",
                ascending=False
            )

        bsm_grid = show_grid(
            summary_bsm,
            selectable=True,
            key="bsm"
        )

        selected_bsm = get_selected_value(
            bsm_grid,
            "BSM"
        )

        st.divider()

    # =========================================================
    # REKAP CSE / RSE
    # =========================================================

    if role in ["BSM", "HOS", "ADMIN"]:

        st.subheader("📋 Rekap CSE/RSE")

        rekap_cse = []

        cse_list = df_user[
            df_user["ROLE"].isin([
                "CSE",
                "RSE"
            ])
        ]

        for _, row in cse_list.iterrows():

            if selected_bsm:
                if row["ATASAN"] != selected_bsm:
                    continue

            nama_cse = row["USER"]

            daftar_promotor = df_user[
                (df_user["ATASAN"] == nama_cse)
                &
                (df_user["ROLE"] == "PROMOTOR")
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_promotor)
            ]

            total_promotor = len(daftar_promotor)
            promotor_aktif = temp["Input By"].nunique()
            total_msisdn = len(temp)
            total_bio = temp["Biometrik"].sum()

            persen_aktif = round(
                (promotor_aktif / total_promotor) * 100,
                2
            ) if total_promotor > 0 else 0

            persen_bio = round(
                (total_bio / total_msisdn) * 100,
                2
            ) if total_msisdn > 0 else 0

            rekap_cse.append({
                "CSE/RSE": nama_cse,
                "Branch": row["ATASAN"],
                "Promotor": total_promotor,
                "Promotor Aktif": promotor_aktif,
                "% User Aktif": f"{persen_aktif}%",
                "Outlet": temp["ID Outlet"].nunique(),
                "MSISDN": total_msisdn,
                "Biometrik": total_bio,
                "% Biometrik": f"{persen_bio}%"
            })

        summary_cse = pd.DataFrame(rekap_cse)

        if not summary_cse.empty:
            summary_cse = summary_cse.sort_values(
                "MSISDN",
                ascending=False
            )

        cse_grid = show_grid(
            summary_cse,
            selectable=True,
            key="cse"
        )

        selected_cse = get_selected_value(
            cse_grid,
            "CSE/RSE"
        )

        st.divider()

    # =========================================================
    # REKAP PROMOTOR
    # =========================================================

    st.subheader("📋 Rekap Promotor")

    rekap_promotor = []

    promotor_user = df_user[
        df_user["ROLE"] == "PROMOTOR"
    ]

    for _, row in promotor_user.iterrows():

        if selected_cse:
            if row["ATASAN"] != selected_cse:
                continue

        nama_promotor = row["USER"]

        temp = df[
            df["Input By"] == nama_promotor
        ]

        total_msisdn = len(temp)
        total_bio = temp["Biometrik"].sum()

        persen_bio = round(
            (total_bio / total_msisdn) * 100,
            2
        ) if total_msisdn > 0 else 0

        rekap_promotor.append({
            "Promotor": nama_promotor,
            "Upline": row["ATASAN"],
            "Status": "Aktif" if total_msisdn > 0 else "Belum Input",
            "Outlet": temp["ID Outlet"].nunique(),
            "MSISDN": total_msisdn,
            "Biometrik": total_bio,
            "% Biometrik": f"{persen_bio}%"
        })

    summary_promotor = pd.DataFrame(rekap_promotor)

    if not summary_promotor.empty:
        summary_promotor = summary_promotor.sort_values(
            "MSISDN",
            ascending=False
        )

    show_grid(
        summary_promotor,
        selectable=True,
        key="promotor"
    )