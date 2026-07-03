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
    tampil_data,
    tampil_user
)

# ==========================================================
# LOAD BIOMETRIK
# ==========================================================

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
    key=None
):

    if df.empty:

        st.info("Tidak ada data.")
        return None

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

    gb.configure_default_column(

        resizable=True,
        sortable=True,
        filter=True

    )

    # ======================================================
    # SELECTABLE
    # ======================================================

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

    # ======================================================
    # TOTAL ROW
    # ======================================================

    total_row = {}

    for col in df.columns:

        if pd.api.types.is_numeric_dtype(df[col]):

            total_row[col] = int(df[col].sum())

        else:

            if col in [

                "HOS",
                "BSM",
                "Branch",
                "CSE/RSE"

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

        fit_columns_on_grid_load=True,

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

    st.title("📊 Dashboard CSE/RSE")

    # ======================================================
    # LOAD DATA
    # ======================================================

    data = tampil_data()

    # ======================================================
    # USER DATAFRAME
    # ======================================================

    users = tampil_user()

    df_user = pd.DataFrame(

        [dict(row) for row in users]

    )

    df_user.columns = df_user.columns.str.upper()

    # ======================================================
    # EMPTY
    # ======================================================

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
            "Tanggal"

        ]

    )

    # ======================================================
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
    ).dt.date

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
            df["Tanggal"] ==
            df["tanggal_biometrik"]
        )
        .fillna(False)
        .astype(int)
    )

    # ======================================================
    # USER DATAFRAME
    # ======================================================

    df_user = pd.DataFrame(

        users,

        columns=[

            "USER",
            "ROLE",
            "ATASAN"

        ]

    )

    # ======================================================
    # SESSION
    # ======================================================

    role = st.session_state.outlet_role

    user = st.session_state.outlet_user

    # ======================================================
    # FILTER TANGGAL
    # ======================================================

    df["Tanggal"] = pd.to_datetime(

        df["Tanggal"],

        errors="coerce"

    )

    tanggal = st.date_input(

        "📅 Filter Tanggal",

        value=None,

        key="dashboard_tanggal"

    )

    if tanggal:

        df = df[

            df["Tanggal"].dt.date
            == tanggal

        ]

    st.divider()

    # ======================================================
    # FILTER ROLE
    # ======================================================

    if role in [

        "CSE",
        "RSE",
        "DSE",
        "FRONTLINER",
        "PROMOTOR"

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

            df_user["ATASAN"] == user

        ]["USER"].tolist()

        bawahan = df_user[

            df_user["ATASAN"]
            .isin(daftar_bsm)

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(bawahan)
        ]

    # ======================================================
    # KPI KHUSUS INPUT CSE/RSE
    # ======================================================

    cse_user = df_user[

        df_user["ROLE"]
        .isin([
            "CSE",
            "RSE"
        ])

    ]["USER"].tolist()

    # ======================================================
    # DATA INPUT CSE/RSE
    # ======================================================

    df_cse = df[

        df["Input By"]
        .isin(cse_user)

    ]

    # ======================================================
    # KPI CSE/RSE
    # ======================================================

    df_cse_all = df_user[df_user["ROLE"].isin(["CSE", "RSE"])]

    # hitung total user CSE/RSE (global, bukan hasil filter df)
    total_user_cse = len(df_cse_all)

    # data aktivitas (sudah ter-filter sesuai role sebelumnya)
    jumlah_user = df_cse["Input By"].nunique()
    jumlah_outlet = df_cse["ID Outlet"].nunique()
    jumlah_msisdn = len(df_cse)
    jumlah_biometrik = df_cse["Biometrik"].sum()

    # ======================================================
    # PERSENTASE
    # ======================================================

    persen_user_aktif = (
        round((jumlah_user / total_user_cse) * 100, 2)
        if total_user_cse > 0 else 0
    )

    persen_bio = (
        round((jumlah_biometrik / jumlah_msisdn) * 100, 2)
        if jumlah_msisdn > 0 else 0
    )

    # ======================================================
    # UI KPI
    # ======================================================

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("🏪 Outlet", jumlah_outlet)
    col2.metric("👤 CSE/RSE Aktif", jumlah_user)
    col3.metric("% User Aktif", f"{persen_user_aktif}%")
    col4.metric("📱 MSISDN", jumlah_msisdn)
    col5.metric("✅ Biometrik", jumlah_biometrik)
    col6.metric("% Biometrik", f"{persen_bio}%")

    st.divider()
    # ======================================================
    # CSE / RSE
    # ======================================================

    if role in [

        "CSE",
        "RSE",
        "DSE",
        "FRONTLINER",
        "PROMOTOR"

    ]:

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

        show_grid(detail_df)

    # ======================================================
    # BSM
    # ======================================================

    elif role == "BSM":

        st.subheader(
            "📋 Rekap CSE/RSE"
        )

        summary = (

            df

            .groupby("Input By")

            .agg(

                Outlet=(
                    "ID Outlet",
                    "nunique"
                ),

                MSISDN=(
                    "MSISDN",
                    "count"
                ),

                Biometrik=(
                    "Biometrik",
                    "sum"
                )

            )

            .reset_index()

            .rename(

                columns={
                    "Input By": "CSE/RSE"
                }

            )

            .sort_values(

                "MSISDN",

                ascending=False

            )

        )

        show_grid(
            summary_cse.copy(),
            selectable=True,
    key=f"cse_{selected_bsm}_{selected_hos}"
)

    # ======================================================
    # HOS
    # ======================================================

    elif role == "HOS":

        # ==================================================
        # REKAP BSM
        # ==================================================

        st.subheader(
            "📋 Rekap BSM"
        )

        daftar = []

        daftar_bsm = df_user[

            df_user["ATASAN"] == user

        ]["USER"].tolist()

        for bsm in daftar_bsm:

            bawahan = df_user[

                (df_user["ATASAN"] == bsm)

                &

                (df_user["ROLE"].isin([

                    "CSE",
                    "RSE"

                ]))

            ]["USER"].tolist()

            temp = df[

                df["Input By"]
                .isin(bawahan)

            ]

            daftar.append({

                "BSM": bsm,

                "CSE/RSE":
                    temp["Input By"]
                    .nunique(),

                "CSE/RSE Aktif":
                    temp["Input By"]
                    .nunique(),

                "Outlet":
                    temp["ID Outlet"]
                    .nunique(),

                "MSISDN":
                    len(temp),

                "Biometrik":
                    temp["Biometrik"]
                    .sum()

            })

        summary_bsm = pd.DataFrame(
            daftar
        )

        if not summary_bsm.empty:

            summary_bsm = (

                summary_bsm

                .sort_values(

                    "MSISDN",

                    ascending=False

                )

            )

        show_grid(summary_bsm)

        st.divider()

        # ==================================================
        # REKAP CSE
        # ==================================================

        st.subheader(
            "📋 Rekap CSE/RSE"
        )

        rekap_cse = []

        for bsm in daftar_bsm:

            bawahan = df_user[

                df_user["ATASAN"] == bsm

            ]

            for _, row in bawahan.iterrows():

                user_cse = row["USER"]

                temp = df[

                    df["Input By"]
                    == user_cse

                ]

                rekap_cse.append({

                    "CSE/RSE":
                        user_cse,

                    "Branch":
                        bsm,

                    "Outlet":
                        temp["ID Outlet"]
                        .nunique(),

                    "MSISDN":
                        len(temp),

                    "Biometrik":
                        temp["Biometrik"]
                        .sum()

                })

        summary_cse = pd.DataFrame(
            rekap_cse
        )

        if not summary_cse.empty:

            summary_cse = (

                summary_cse

                .sort_values(

                    ["MSISDN"],

                    ascending=False

                )

            )

        show_grid(summary_cse)

    # ======================================================
    # ADMIN
    # ======================================================

    else:

        selected_hos = None
        selected_bsm = None
        selected_cse = None

        # ======================================================
        # HEADER + RESET (SEJAJAR)
        # ======================================================

        header_col, reset_col = st.columns([5, 1])

        with header_col:
            st.subheader("📋 Rekap HOS")

        with reset_col:
            if st.button(
                "🔄 Reset",
                use_container_width=True
            ):
                st.session_state.selected_hos = None
                st.session_state.selected_bsm = None
                st.session_state.selected_cse = None
                st.rerun()

        # ==================================================
        # REKAP HOS
        # ==================================================

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
                (df_user["ROLE"].isin(["CSE", "RSE"]))
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_cse)
            ]

            total_cse = len(daftar_cse)
            cse_aktif = temp["Input By"].nunique()

            total_msisdn = len(temp)
            total_bio = temp["Biometrik"].sum()

            persen_aktif = round(
                (cse_aktif / total_cse) * 100,
                2
            ) if total_cse > 0 else 0

            persen_bio = round(
                (total_bio / total_msisdn) * 100,
                2
            ) if total_msisdn > 0 else 0

            rekap_hos.append({

                "HOS": nama_hos,
                "BSM": len(daftar_bsm),
                "CSE/RSE": total_cse,
                "CSE/RSE Aktif": cse_aktif,
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

        st.download_button(
            "⬇️ Download HOS",
            to_excel(summary_hos),
            file_name="rekap_hos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_hos"
        )

        hos_grid = show_grid(
            summary_hos,
            selectable=True,
            key="hos"
        )

        selected_hos = get_selected_value(hos_grid, "HOS")

        st.divider()

        # ==================================================
        # REKAP BSM
        # ==================================================

        st.subheader("📋 Rekap BSM")

        rekap_bsm = []

        bsm_list = df_user[
            df_user["ROLE"] == "BSM"
        ]

        for _, row in bsm_list.iterrows():

            if selected_hos and row["ATASAN"] != selected_hos:
                continue

            nama_bsm = row["USER"]

            daftar_cse = df_user[
                (df_user["ATASAN"] == nama_bsm)
                &
                (df_user["ROLE"].isin(["CSE", "RSE"]))
            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_cse)
            ]

            total_cse = len(daftar_cse)
            cse_aktif = temp["Input By"].nunique()

            total_msisdn = len(temp)
            total_bio = temp["Biometrik"].sum()

            persen_aktif = round(
                (cse_aktif / total_cse) * 100,
                2
            ) if total_cse > 0 else 0

            persen_bio = round(
                (total_bio / total_msisdn) * 100,
                2
            ) if total_msisdn > 0 else 0

            rekap_bsm.append({

                "BSM": nama_bsm,
                "CSE/RSE": total_cse,
                "CSE/RSE Aktif": cse_aktif,
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

        st.download_button(
            "⬇️ Download BSM",
            to_excel(summary_bsm),
            file_name="rekap_bsm.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_bsm"
        )

        bsm_grid = show_grid(
            summary_bsm,
            selectable=True,
            key="bsm"
        )

        selected_bsm = get_selected_value(bsm_grid, "BSM")

        st.divider()

        # ==================================================
        # REKAP CSE/RSE
        # ==================================================

        st.subheader("📋 Rekap CSE/RSE")

        rekap_cse = []

        cse_list = df_user[
            df_user["ROLE"].isin(["CSE", "RSE"])
        ]

        for _, row in cse_list.iterrows():

            if selected_bsm and row["ATASAN"] != selected_bsm:
                continue

            nama_cse = row["USER"]

            temp = df[
                df["Input By"] == nama_cse
            ]

            total_msisdn = len(temp)
            total_bio = temp["Biometrik"].sum()

            persen_bio = round(
                (total_bio / total_msisdn) * 100,
                2
            ) if total_msisdn > 0 else 0

            rekap_cse.append({

                "CSE/RSE": nama_cse,
                "Branch": row["ATASAN"],
                "Status": "Aktif" if total_msisdn > 0 else "Belum Input",
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

        st.download_button(
            "⬇️ Download CSE",
            to_excel(summary_cse),
            file_name="rekap_cse.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_cse"
        )

        show_grid(
            summary_cse,
            selectable=True,
            key="cse"
        )