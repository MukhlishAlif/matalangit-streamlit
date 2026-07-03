# =========================================================
# dashboard_dse.py
# DASHBOARD HIERARCHY DSE
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

    # =====================================================
    # DEFAULT COLUMN STYLE (CENTER ALL + WRAP SAFE)
    # =====================================================

    gb.configure_default_column(

        resizable=True,
        sortable=True,
        filter=True,

        minWidth=90,

        wrapText=False,

        cellStyle={

            "textAlign": "center",
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center",
            "fontSize": "13px"

        }

    )

    # =====================================================
    # PIN FIRST COLUMN (BIAR RAPI TABLE BESAR)
    # =====================================================

    first_col = df.columns[0]

    gb.configure_column(

        first_col,

        pinned="left",

        cellStyle={

            "fontWeight": "600",
            "textAlign": "center",
            "display": "flex",
            "justifyContent": "center",
            "alignItems": "center"

        }

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
    # TOTAL ROW (PINNED BOTTOM)
    # =====================================================

    total_row = {}

    for col in df.columns:

        if pd.api.types.is_numeric_dtype(df[col]):

            total_row[col] = int(df[col].sum())

        else:

            if col in [

                "HOS",
                "BSM",
                "Branch",
                "CSE/RSE",
                "DSE",
                "Atasan"

            ]:

                total_row[col] = df[col].nunique()

            else:

                total_row[col] = ""

    gb.configure_grid_options(

        pinnedBottomRowData=[total_row],

        headerHeight=45,
        rowHeight=42,
        domLayout="normal"

    )

    grid_options = gb.build()

    # =====================================================
    # AUTO HEIGHT (BIAR 1 VIEW TANPA SCROLL KE BAWAH PANJANG)
    # =====================================================

    table_height = min(

        520,
        (len(df) + 2) * 42

    )

    # =====================================================
    # GRID CSS (FULL CENTER CLEAN UI)
    # =====================================================

    custom_css = {

        ".ag-theme-balham": {

            "font-family": "Poppins",
            "font-size": "13px"

        },

        ".ag-header-cell-label": {

            "justify-content": "center",
            "font-weight": "700"

        },

        ".ag-cell": {

            "display": "flex",
            "justify-content": "center",
            "align-items": "center",
            "text-align": "center"

        },

        ".ag-pinned-bottom-row": {

            "background-color": "#eef2ff",
            "font-weight": "700"

        }

    }

    # =====================================================
    # GRID RENDER
    # =====================================================

    grid_response = AgGrid(

        df,

        key=key,

        gridOptions=grid_options,

        fit_columns_on_grid_load=True,

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

    st.title("📊 Dashboard DSE")

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

    df["Tanggal"] = (

        pd.to_datetime(
            df["Tanggal"],
            errors="coerce"
        ).dt.date

    )

    df = df.merge(

        biometrik,

        left_on=[
            "MSISDN",
            "Tanggal"
        ],

        right_on=[
            "msisdn",
            "tanggal_biometrik"
        ],

        how="left"

    )

    df["Biometrik"] = (
        df["tanggal_biometrik"].notna()
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

    tanggal = st.date_input(

        "📅 Filter Tanggal",

        value=None,

        key="dse_tanggal"

    )

    if tanggal:

        df = df[
            df["Tanggal"] == tanggal
        ]

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

            (df_user["ROLE"] == "DSE")

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(daftar_dse)
        ]

    elif role == "BSM":

        daftar_cse = df_user[
            df_user["ATASAN"] == user
        ]["USER"].tolist()

        daftar_dse = df_user[

            (df_user["ATASAN"].isin(daftar_cse))

            &

            (df_user["ROLE"] == "DSE")

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(daftar_dse)
        ]

    elif role == "HOS":

        daftar_bsm = df_user[
            df_user["ATASAN"] == user
        ]["USER"].tolist()

        daftar_cse = df_user[

            (df_user["ATASAN"].isin(daftar_bsm))

            &

            (df_user["ROLE"].isin(["CSE", "RSE"]))

        ]["USER"].tolist()

        daftar_dse = df_user[

            (df_user["ATASAN"].isin(daftar_cse))

            &

            (df_user["ROLE"] == "DSE")

        ]["USER"].tolist()

        df = df[
            df["Input By"].isin(daftar_dse)
        ]
    # =====================================================
    # KPI (ROLE AWARE - FIXED)
    # =====================================================

    df_dse = df.copy()

    # semua DSE yang ADA DI DATA YANG SUDAH DIFILTER
    list_dse_in_view = df_user[
    df_user["ROLE"] == "DSE"
    ]["USER"].tolist()

    df_dse = df_dse[df_dse["Input By"].isin(list_dse_in_view)]

    # =====================================================
    # TOTAL METRICS
    # =====================================================

    total_dse = len(list_dse_in_view)

    dse_aktif = df_dse["Input By"].nunique()
    total_outlet = df_dse["ID Outlet"].nunique()
    total_msisdn = len(df_dse)
    total_bio = df_dse["Biometrik"].sum()

    # =====================================================
    # PERSENTASE
    # =====================================================

    persen_dse_aktif = round(
        (dse_aktif / total_dse) * 100,
        2
    ) if total_dse > 0 else 0

    persen_bio = round(
        (total_bio / total_msisdn) * 100,
        2
    ) if total_msisdn > 0 else 0


    # =====================================================
    # UI KPI
    # =====================================================

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric(
        "🏪 Outlet",
        total_outlet
    )

    col2.metric(
        "👤 DSE Aktif",
        dse_aktif
    )

    col3.metric(
        "% DSE Aktif",
        f"{persen_dse_aktif}%"
    )

    col4.metric(
        "📱 MSISDN",
        total_msisdn
    )

    col5.metric(
        "✅ Biometrik",
        total_bio
    )

    col6.metric(
        "% Biometrik",
        f"{persen_bio}%"
    )

    st.divider()
    # =====================================================
    # RESET FILTER BUTTON (KANAN SEJAJAR TITLE)
    # =====================================================

    header_col, reset_col = st.columns([5, 1])

    with header_col:
        st.subheader("📋 Rekap")

    with reset_col:
        if st.button(
            "🔄 Reset",
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

            daftar_dse = df_user[

                (df_user["ATASAN"].isin(daftar_cse))

                &

                (df_user["ROLE"] == "DSE")

            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_dse)
            ]

            dse_aktif = temp["Input By"].nunique()

            total_dse = len(daftar_dse)

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

            rekap_hos.append({

                "HOS":
                    nama_hos,

                "BSM":
                    len(daftar_bsm),

                "CSE/RSE":
                    len(daftar_cse),

                "DSE":
                    total_dse,

                "DSE Aktif":
                    dse_aktif,

                "% User Aktif":
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

        summary_hos = pd.DataFrame(
            rekap_hos
        )

        st.download_button(

            label="⬇️ Download Rekap HOS",

            data=to_excel(summary_hos),

            file_name="rekap_hos.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key="download_hos"

        )

        hos_grid = show_grid(

            summary_hos,

            selectable=True,

            key="hos"

        )

        if hos_grid:

            selected = hos_grid.get(
                "selected_rows"
            )

            if selected is not None:

                if isinstance(
                    selected,
                    pd.DataFrame
                ):

                    if not selected.empty:

                        st.session_state.selected_hos = (
                            selected.iloc[0]["HOS"]
                        )

                        st.session_state.selected_bsm = None
                        st.session_state.selected_cse = None

                elif isinstance(
                    selected,
                    list
                ):

                    if len(selected) > 0:

                        st.session_state.selected_hos = (
                            selected[0]["HOS"]
                        )

                        st.session_state.selected_bsm = None
                        st.session_state.selected_cse = None

        st.divider()

    # =====================================================
    # REKAP BSM
    # =====================================================

    if role in ["ADMIN", "HOS"]:

        st.subheader("📋 Rekap BSM")

        rekap_bsm = []

        bsm_list = df_user[
            df_user["ROLE"] == "BSM"
        ]

        for _, row in bsm_list.iterrows():

            if st.session_state.selected_hos:

                if row["ATASAN"] != st.session_state.selected_hos:

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

            daftar_dse = df_user[

                (df_user["ATASAN"].isin(daftar_cse))

                &

                (df_user["ROLE"] == "DSE")

            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_dse)
            ]

            dse_aktif = temp["Input By"].nunique()

            total_dse = len(daftar_dse)

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

                "CSE/RSE":
                    len(daftar_cse),

                "DSE":
                    total_dse,

                "DSE Aktif":
                    dse_aktif,

                "% User Aktif":
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

        st.download_button(

            label="⬇️ Download Rekap BSM",

            data=to_excel(summary_bsm),

            file_name="rekap_bsm.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key="download_bsm"

        )

        bsm_grid = show_grid(

            summary_bsm,

            selectable=True,

            key="bsm"

        )

        if bsm_grid:

            selected = bsm_grid.get(
                "selected_rows"
            )

            if selected is not None:

                if isinstance(
                    selected,
                    pd.DataFrame
                ):

                    if not selected.empty:

                        st.session_state.selected_bsm = (
                            selected.iloc[0]["BSM"]
                        )

                        st.session_state.selected_cse = None

                elif isinstance(
                    selected,
                    list
                ):

                    if len(selected) > 0:

                        st.session_state.selected_bsm = (
                            selected[0]["BSM"]
                        )

                        st.session_state.selected_cse = None

        st.divider()

    # =====================================================
    # REKAP CSE/RSE
    # =====================================================

    if role in ["ADMIN", "HOS", "BSM"]:

        st.subheader("📋 Rekap CSE/RSE")

        rekap_cse = []

        cse_list = df_user[

            df_user["ROLE"].isin([
                "CSE",
                "RSE"
            ])

        ]

        for _, row in cse_list.iterrows():

            if st.session_state.selected_bsm:

                if row["ATASAN"] != st.session_state.selected_bsm:

                    continue

            nama_cse = row["USER"]

            daftar_dse = df_user[

                (df_user["ATASAN"] == nama_cse)

                &

                (df_user["ROLE"] == "DSE")

            ]["USER"].tolist()

            temp = df[
                df["Input By"].isin(daftar_dse)
            ]

            dse_aktif = temp["Input By"].nunique()

            total_dse = len(daftar_dse)

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

                "Branch":
                    row["ATASAN"],

                "DSE":
                    total_dse,

                "DSE Aktif":
                    dse_aktif,

                "% User Aktif":
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

        st.download_button(

            label="⬇️ Download Rekap CSE",

            data=to_excel(summary_cse),

            file_name="rekap_cse.xlsx",

            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            key="download_cse"

        )

        cse_grid = show_grid(

            summary_cse,

            selectable=True,

            key="cse"

        )

        if cse_grid:

            selected = cse_grid.get(
                "selected_rows"
            )

            if selected is not None:

                if isinstance(
                    selected,
                    pd.DataFrame
                ):

                    if not selected.empty:

                        st.session_state.selected_cse = (
                            selected.iloc[0]["CSE/RSE"]
                        )

                elif isinstance(
                    selected,
                    list
                ):

                    if len(selected) > 0:

                        st.session_state.selected_cse = (
                            selected[0]["CSE/RSE"]
                        )

        st.divider()

    # =====================================================
    # REKAP DSE
    # =====================================================

    st.subheader("📋 Rekap DSE")

    rekap_dse = []

    dse_user = df_user[
        df_user["ROLE"] == "DSE"
    ]

    for _, row in dse_user.iterrows():

        if st.session_state.selected_cse:

            if row["ATASAN"] != st.session_state.selected_cse:

                continue

        nama_dse = row["USER"]

        temp = df[
            df["Input By"] == nama_dse
        ]

        total_msisdn = len(temp)

        total_bio = temp["Biometrik"].sum()

        persen_bio = round(

            (
                total_bio / total_msisdn
            ) * 100,

            2

        ) if total_msisdn > 0 else 0

        rekap_dse.append({

            "DSE":
                nama_dse,

            "Upline":
                row["ATASAN"],

            "Status":

                "Aktif"

                if len(temp) > 0

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

    summary_dse = pd.DataFrame(
        rekap_dse
    )

    if not summary_dse.empty:

        summary_dse = (

            summary_dse

            .sort_values(

                "MSISDN",

                ascending=False

            )

        )

    st.download_button(

        label="⬇️ Download Rekap DSE",

        data=to_excel(summary_dse),

        file_name="rekap_dse.xlsx",

        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

        key="download_dse"

    )

    show_grid(

        summary_dse,

        selectable=False,

        key="dse"

    )