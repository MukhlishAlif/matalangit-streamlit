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

    # =====================================================
    # SELECTABLE
    # =====================================================

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
                "Frontliner",
                "Frontliner Inaktif",
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

    # =====================================================
    # GRID
    # =====================================================

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

    st.title("📊 Dashboard Frontliner")

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

    tanggal = st.date_input(

        "📅 Filter Tanggal",

        value=None,

        key="fl_tanggal"

    )

    if tanggal:

        df = df[
            df["Tanggal"] == tanggal
        ]

    st.divider()

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

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col2.metric(
        "👤 FL Aktif",
        fl_aktif
    )

    col1.metric(
        "🏪 Outlet",
        jumlah_outlet
    )

    col4.metric(
        "📱 MSISDN",
        jumlah_msisdn
    )

    col3.metric(
        "📊 % FL Aktif",
        f"{persen_fl_aktif}%"
    )

    col5.metric(
        "✅ Biometrik",
        jumlah_biometrik
    )

    col6.metric(
        "📈 % Biometrik",
        f"{persen_biometrik}%"
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

            # Dynamic Inactive Calculation
            fl_inaktif = total_fl - fl_aktif

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

                "BSM":
                    len(daftar_bsm),

                "CSE/RSE":
                    len(daftar_cse),

                "Frontliner":
                    total_fl,

                "Frontliner Aktif":
                    fl_aktif,

                "Frontliner Inaktif":
                    fl_inaktif,

                "% Active":
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

        hos_grid = show_grid(

            summary_hos,

            selectable=True,

            key="hos_fl"

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

            # Dynamic Inactive Calculation
            fl_inaktif = total_fl - fl_aktif

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

            print(fl_aktif, total_fl)
            persen_bio = round(
                (
                    total_bio / total_msisdn
                ) * 100,
                2
            ) if jumlah_msisdn > 0 else 0

            rekap_bsm.append({

                "BSM":
                    nama_bsm,

                "CSE/RSE":
                    len(daftar_cse),

                "Frontliner":
                    total_fl,

                "Frontliner Aktif":
                    fl_aktif,

                "Frontliner Inaktif":
                    fl_inaktif,

                "% Active":
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

        bsm_grid = show_grid(

            summary_bsm,

            selectable=True,

            key="bsm_fl"

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

            # Dynamic Inactive Calculation
            fl_inaktif = total_fl - fl_aktif

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

                "Branch":
                    row["ATASAN"],

                "Frontliner":
                    total_fl,

                "Frontliner Aktif":
                    fl_aktif,

                "Frontliner Inaktif":
                    fl_inaktif,

                "% Active":
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

        cse_grid = show_grid(

            summary_cse,

            selectable=True,

            key="cse_fl"

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

    show_grid(

        summary_fl,

        selectable=False,

        key="frontliner"

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