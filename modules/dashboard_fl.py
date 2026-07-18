# =========================================================
# dashboard_frontliner.py
# DASHBOARD FRONTLINER
# HOS (region_name) -> BSM (branch) -> CSE/RSE (micro_cluster_name) -> FRONTLINER (fl_id)
#
# SUMBER DATA: endpoint /bio/fetch-all-fl + /bio/fetch-all-bio
# (via database.load_outlet_bio_summary), BUKAN dari outlet.db /
# tampil_data_by_date lagi.
#
# ASUMSI (tolong dikonfirmasi kalau meleset):
#   - fl_id di data FL == username Frontliner di df_user (USER, ROLE=FRONTLINER)
#   - region_name (FL) <-> REGION (user)
#   - branch      (FL) <-> BRANCH (user)
#   - micro_cluster_name (FL) <-> MICRO_CLUSTER (user)
# =========================================================
import requests
import streamlit as st
import pandas as pd
from io import BytesIO
import base64
from datetime import date

from st_aggrid import (
    AgGrid,
    GridOptionsBuilder,
    GridUpdateMode
)

from database import (
    load_fl_summary,
    load_user_hierarchy
)


# =========================================================
# HELPER TAMPILAN (tidak berubah)
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
# GET SELECTED VALUE (tidak berubah)
# =========================================================

def get_selected_value(grid, column_name):

    if not grid:
        return None

    selected = grid.get("selected_rows")

    if selected is None:
        return None

    if isinstance(selected, pd.DataFrame):
        if not selected.empty:
            return selected.iloc[0][column_name]

    elif isinstance(selected, list):
        if len(selected) > 0:
            return selected[0][column_name]

    return None

# =========================================================
# GRID TABLE (tidak berubah dari versi sebelumnya)
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

    gb.configure_default_column(
        resizable=False,
        sortable=True,
        filter=False,
        suppressMenu=True,
        floatingFilter=False
    )

    if selectable:
        gb.configure_selection(
            selection_mode="single",
            use_checkbox=False
        )

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

    id_cols_for_nunique = [
        "HOS", "BSM", "Branch", "CSE/RSE", "AE", "Atasan",
        "Region (HOS)", "Branch (BSM)", "Micro Cluster (CSE/RSE)",
        "Frontliner"
    ]

    for col in df.columns:

        if pd.api.types.is_numeric_dtype(df[col]):

            if col in ("Outlet", "Jumlah FL"):
                total_row[col] = (
                    total_outlet
                    if total_outlet is not None
                    else int(df[col].sum())
                )
            else:
                total_row[col] = int(df[col].sum())

        else:

            if col in id_cols_for_nunique:
                total_row[col] = df[col].nunique()
            else:
                total_row[col] = ""

    grid_options = gb.build()

    def get_justify(align_value):
        mapping = {"left": "flex-start", "center": "center", "right": "flex-end"}
        return mapping.get(align_value, "center")

    def get_text_align(align_value):
        return align_value if align_value in ["left", "center", "right"] else "center"

    first_col = df.columns[0]

    for col in grid_options["columnDefs"]:

        field = col["field"]

        max_len = max(
            len(str(field)),
            df[field].astype(str).str.len().max()
        )

        width = min(max(max_len * 10 + 30, 120), 450)

        col["width"] = int(width)
        col["minWidth"] = int(width)
        col["maxWidth"] = int(width)

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

            col["width"] = 220
            col["minWidth"] = 220
            col["maxWidth"] = 220

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

    for col in grid_options["columnDefs"]:
        col["filter"] = False
        col["floatingFilter"] = False
        col["suppressMenu"] = True

    grid_options["pinnedBottomRowData"] = [total_row]

    header_height = 45
    row_height = 42
    footer_height = 45

    table_height = min(
        header_height + (len(df) * row_height) + footer_height + 10,
        560
    )

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
                "border": "1px solid #f0dce2",
                "border-radius": "14px"
            },

            ".ag-header": {
                "background": "linear-gradient(120deg, #FCEFE1 0%, #FBE3E0 60%, #F8DDE6 100%)"
            },

            ".ag-header-cell-label": {
                "justify-content": "center",
                "font-weight": "700",
                "color": "#7A2C46"
            },

            ".ag-pinned-left-header .ag-header-cell-label": {
                "justify-content": "flex-start !important",
                "padding-left": "12px"
            },

            ".ag-row": {"font-size": "14px"},

            ".ag-row-hover": {"background-color": "#FFF5F7 !important"},

            ".ag-pinned-bottom": {
                "background-color": "#FDF1F5",
                "font-weight": "700",
                "border-top": "2px solid #D4537E",
                "min-height": "42px"
            }
        }
    )

    return grid_response


# =========================================================
# HELPER: AGREGASI PER LEVEL (region / branch / micro_cluster)
# =========================================================

def build_rekap(df_source, group_col, id_label):
    """
    Agregasi df hasil load_outlet_bio_summary() per level geografis
    (region_name / branch / micro_cluster_name). Metrik: jumlah FL,
    total target, total biometrik, jumlah eligible, % capaian, % eligible.
    """

    if df_source.empty or group_col not in df_source.columns:
        return pd.DataFrame()

    grp = (
        df_source
        .groupby(group_col, dropna=False)
        .agg(
            **{
                "Jumlah FL": ("fl_id", "nunique"),
                "Target": ("fl_target", "sum"),
                "Biometrik": ("Biometrik", "sum"),
                "Eligible_n": ("Eligible", "sum"),
            }
        )
        .reset_index()
        .rename(columns={group_col: id_label})
    )

    grp["Target"] = grp["Target"].astype(int)
    grp["Biometrik"] = grp["Biometrik"].astype(int)

    grp["% Capaian"] = grp.apply(
        lambda r: round(r["Biometrik"] / r["Target"] * 100, 2) if r["Target"] > 0 else 0,
        axis=1
    )

    grp["% Eligible"] = grp.apply(
        lambda r: round(r["Eligible_n"] / r["Jumlah FL"] * 100, 2) if r["Jumlah FL"] > 0 else 0,
        axis=1
    )

    grp = grp.rename(columns={"Eligible_n": "FL Eligible"})

    grp["% Capaian"] = grp["% Capaian"].astype(str) + "%"
    grp["% Eligible"] = grp["% Eligible"].astype(str) + "%"

    grp[id_label] = grp[id_label].fillna("-").replace("", "-")

    return grp[[id_label, "Jumlah FL", "Target", "Biometrik", "FL Eligible", "% Capaian", "% Eligible"]]


def download_button_df(dfr, label, filename, key):

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dfr.to_excel(writer, index=False)

    st.download_button(
        label=label,
        data=buffer.getvalue(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=key
    )


# =========================================================
# DASHBOARD
# =========================================================
@st.cache_data(ttl=300)
def load_fl_api():

    url = "https://api.matalangit.cloud/bio/fetch-all-fl"

    try:

        response = requests.get(
            url,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        df = pd.DataFrame(result["data"])

        # convert numeric
        df["fl_target"] = pd.to_numeric(
            df["fl_target"],
            errors="coerce"
        ).fillna(0).astype(int)

        df["ga_mtd"] = pd.to_numeric(
            df["ga_mtd"],
            errors="coerce"
        ).fillna(0).astype(int)

        # supaya sama seperti dashboard lama
        df["Biometrik"] = df["ga_mtd"]

        # Eligible = target tercapai
        df["Eligible"] = (
            df["Biometrik"] >= df["fl_target"]
        ).astype(int)

        return df

    except Exception as e:

        st.error(f"Gagal mengambil data FL : {e}")

        return pd.DataFrame()
        
def show():

    st.markdown(
        """
        <link rel="stylesheet"
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" />
        """,
        unsafe_allow_html=True
    )

    # =====================================================
    # USER HIERARCHY (dari load_user_hierarchy, PUNYA field
    # REGION/AREA/BRANCH/MICRO_CLUSTER per user -- dipakai untuk
    # scoping & nama asli, BUKAN untuk data submission lagi)
    # =====================================================

    (
        df_user,
        role_map,
        atasan_map,
        brand_map,
        children_map
    ) = load_user_hierarchy()

    role = st.session_state.outlet_role
    user = st.session_state.outlet_user

    real_name_map = (
        df_user
        .drop_duplicates(subset="USER")
        .assign(USER=lambda x: x["USER"].astype(str).str.strip().str.upper())
        .set_index("USER")["REAL_NAME"]
        .to_dict()
    )

    def get_real_name(username):
        key = str(username).strip().upper()
        nama = real_name_map.get(key)
        return nama if nama else username

    my_row = df_user[df_user["USER"] == user]

    my_region = my_row["REGION"].iloc[0] if not my_row.empty and "REGION" in df_user.columns else None
    my_branch = my_row["BRANCH"].iloc[0] if not my_row.empty and "BRANCH" in df_user.columns else None
    my_mc = my_row["MICRO_CLUSTER"].iloc[0] if not my_row.empty and "MICRO_CLUSTER" in df_user.columns else None

    # =====================================================
    # HEADER
    # =====================================================

    logo_b64 = get_base64_image("icon.png")

    display_name = real_name_map.get(str(user).strip().upper(), user)

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
        .dse-kpi-card {{
            background: #fff;
            border-radius: 14px;
            padding: 16px 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(153, 53, 86, 0.08);
            border: 1px solid #f3e3e8;
        }}
        .dse-kpi-icon {{ font-size: 22px; margin-bottom: 4px; }}
        .dse-kpi-value {{ font-size: 22px; font-weight: 700; color: #3d2230; }}
        .dse-kpi-label {{ font-size: 12px; color: #9a7a86; margin-top: 2px; }}
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
                        <span class="dse-title-text">Dashboard Frontliner</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =====================================================
    # FILTER
    # =====================================================

    with st.container(border=True):

        st.caption(
            ":material/info: Biometrik (ga_mtd) adalah akumulasi bulan "
            "berjalan langsung dari sistem -- tidak ada filter tanggal."
        )

        brand = st.selectbox(
            ":material/sim_card: Filter Brand",
            options=["Semua", "IM3", "3ID"],
            index=0
        )

    # =====================================================
    # AMBIL DATA DARI ENDPOINT FL (ga_mtd = Biometrik tercapai,
    # sudah termasuk target & capaian langsung dari API)
    # =====================================================

    df = load_fl_api()

    if brand != "Semua":

        if brand == "IM3":

            df = df[
                df["fl_id"]
                .astype(str)
                .str.upper()
                .str.endswith("IM3")
            ]

        elif brand == "3ID":

            df = df[
                df["fl_id"]
                .astype(str)
                .str.upper()
                .str.endswith("3ID")
            ]

    if df.empty:
        st.info("Belum ada data Frontliner / Biometrik untuk filter ini.")
        return

    # =====================================================
    # SCOPE SESUAI ROLE YANG LOGIN
    # (pengganti filter ATASAN chain yang dulu dari outlet.db)
    # =====================================================

    if role == "FRONTLINER":

        df = df[
            df["fl_id"].astype(str).str.strip().str.upper()
            == str(user).strip().upper()
        ]

    elif role in ["CSE", "RSE"]:

        df = df[df["micro_cluster_name"] == my_mc]

    elif role == "BSM":

        df = df[df["branch"] == my_branch]

    elif role == "HOS":

        df = df[df["region_name"] == my_region]

    # ADMIN / HOR -> tanpa filter scope, lihat semua

    if df.empty:
        st.info("Tidak ada data Frontliner pada scope kamu untuk filter ini.")
        return

    # =====================================================
    # KPI
    # =====================================================

    total_fl = df["fl_id"].nunique()
    total_target = int(df["fl_target"].sum())
    total_bio = int(df["Biometrik"].sum())
    total_eligible = int(df["Eligible"].sum())

    persen_eligible = round(total_eligible / total_fl * 100, 2) if total_fl > 0 else 0
    persen_capaian = round(total_bio / total_target * 100, 2) if total_target > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        kpi_card("store", "Jumlah Frontliner", total_fl, "#F5B400")

    with col2:
        kpi_card("flag", "Target Biometrik", total_target, "#F0997B")

    with col3:
        kpi_card("fingerprint", "Biometrik Tercapai", total_bio, "#D4537E")

    with col4:
        kpi_card("verified", "FL Eligible", f"{total_eligible} ({persen_eligible}%)", "#993556")

    with col5:
        kpi_card("trending_up", "% Capaian Target", f"{persen_capaian}%", "#7A2C46")

    st.divider()

    # =====================================================
    # SESSION STATE UNTUK DRILL-DOWN
    # =====================================================

    for k in ["selected_region_fl", "selected_branch_fl", "selected_mc_fl"]:
        if k not in st.session_state:
            st.session_state[k] = None

    header_col, reset_col = st.columns([5, 1])

    with header_col:
        if role == "ADMIN" or role == "HOR":
            section_title("Rekap Region (HOS)", icon="list_alt")
        elif role == "HOS":
            section_title("Rekap Branch (BSM)", icon="list_alt")
        elif role == "BSM":
            section_title("Rekap Micro Cluster (CSE/RSE)", icon="list_alt")
        else:
            section_title("Rekap Frontliner", icon="list_alt")

    with reset_col:

        if st.button(
            "Reset",
            icon=":material/refresh:",
            use_container_width=True,
            key="reset_fl"
        ):

            st.session_state.selected_region_fl = None
            st.session_state.selected_branch_fl = None
            st.session_state.selected_mc_fl = None

            st.rerun()

    # =====================================================
    # REKAP REGION (level "HOS")
    # =====================================================

    if role in ["ADMIN", "HOR"]:

        rekap_region = (
            df.groupby(
                "region_name",
                as_index=False
            )
            .agg(
                **{
                    "Jumlah FL": ("fl_id", "nunique"),
                    "Target": ("fl_target", "sum"),
                    "Biometrik": ("Biometrik", "sum"),
                    "FL Eligible": ("Eligible", "sum"),
                }
            )
        )

        rekap_region.rename(
            columns={
                "region_name": "Region (HOS)"
            },
            inplace=True
        )

        rekap_region["% Capaian"] = (
            rekap_region["Biometrik"]
            / rekap_region["Target"]
            * 100
        ).round(2)

        rekap_region["% Eligible"] = (
            rekap_region["FL Eligible"]
            / rekap_region["Jumlah FL"]
            * 100
        ).round(2)

        rekap_region["% Capaian"] = (
            rekap_region["% Capaian"].astype(str)
            + "%"
        )

        rekap_region["% Eligible"] = (
            rekap_region["% Eligible"].astype(str)
            + "%"
        )

        with st.container(border=True):

            download_button_df(
                rekap_region,
                ":material/download: Download Region",
                "rekap_region_fl.xlsx",
                "download_region_fl"
            )

            region_grid = show_grid(
                rekap_region,
                selectable=True,
                key=f"region_{brand}_{role}_{user}",
                col_align={
                    "Region (HOS)": "left"
                },
                total_outlet=df["fl_id"].nunique()
            )

        selected_region = get_selected_value(
            region_grid,
            "Region (HOS)"
        )

        if selected_region:

            st.session_state.selected_region_fl = selected_region
            st.session_state.selected_branch_fl = None
            st.session_state.selected_mc_fl = None
    st.divider()
    # =====================================================
    # REKAP BRANCH (level "BSM")
    # =====================================================

    if role in ["ADMIN", "HOR", "HOS"]:

        if role in ["ADMIN", "HOR"]:
            section_title("Rekap Branch (BSM)", icon="list_alt")

        df_branch_scope = df.copy()

        if role in ["ADMIN", "HOR"] and st.session_state.selected_region_fl:
            df_branch_scope = df_branch_scope[
                df_branch_scope["region_name"] == st.session_state.selected_region_fl
            ]

        rekap_branch = build_rekap(df_branch_scope, "branch", "Branch (BSM)")

        with st.container(border=True):

            download_button_df(
                rekap_branch,
                ":material/download: Download Branch",
                "rekap_branch_fl.xlsx",
                "download_branch_fl"
            )

            branch_grid = show_grid(
                rekap_branch,
                selectable=True,
                key=f"branch_{brand}_{role}_{user}",
                col_align={"Branch (BSM)": "left"},
                total_outlet=df_branch_scope["fl_id"].nunique()
            )

        selected_branch = get_selected_value(branch_grid, "Branch (BSM)")

        if selected_branch:
            st.session_state.selected_branch_fl = selected_branch
            st.session_state.selected_mc_fl = None

        st.divider()

    # =====================================================
    # REKAP MICRO CLUSTER (level "CSE/RSE")
    # =====================================================

    if role in ["ADMIN", "HOR", "HOS", "BSM"]:

        if role in ["ADMIN", "HOR", "HOS"]:
            section_title("Rekap Micro Cluster (CSE/RSE)", icon="list_alt")

        df_mc_scope = df.copy()

        if role in ["ADMIN", "HOR", "HOS"] and st.session_state.selected_branch_fl:
            df_mc_scope = df_mc_scope[
                df_mc_scope["branch"] == st.session_state.selected_branch_fl
            ]
        elif role in ["ADMIN", "HOR"] and st.session_state.selected_region_fl and not st.session_state.selected_branch_fl:
            df_mc_scope = df_mc_scope[
                df_mc_scope["region_name"] == st.session_state.selected_region_fl
            ]

        rekap_mc = build_rekap(df_mc_scope, "micro_cluster_name", "Micro Cluster (CSE/RSE)")

        with st.container(border=True):

            download_button_df(
                rekap_mc,
                ":material/download: Download Micro Cluster",
                "rekap_mc_fl.xlsx",
                "download_mc_fl"
            )

            mc_grid = show_grid(
                rekap_mc,
                selectable=True,
                key=f"mc_{brand}_{role}_{user}",
                col_align={"Micro Cluster (CSE/RSE)": "left"},
                total_outlet=df_mc_scope["fl_id"].nunique()
            )

        selected_mc = get_selected_value(mc_grid, "Micro Cluster (CSE/RSE)")

        if selected_mc:
            st.session_state.selected_mc_fl = selected_mc

        st.divider()

    # =====================================================
    # REKAP FRONTLINER (leaf level)
    # =====================================================

    if role not in ["CSE", "RSE"]:
        section_title("Rekap Frontliner", icon="list_alt")

    df_fl_scope = df.copy()

    if role in ["ADMIN", "HOR", "HOS", "BSM"] and st.session_state.selected_mc_fl:
        df_fl_scope = df_fl_scope[
            df_fl_scope["micro_cluster_name"] == st.session_state.selected_mc_fl
        ]
    elif role in ["ADMIN", "HOR", "HOS"] and st.session_state.selected_branch_fl and not st.session_state.selected_mc_fl:
        df_fl_scope = df_fl_scope[
            df_fl_scope["branch"] == st.session_state.selected_branch_fl
        ]
    elif role in ["ADMIN", "HOR"] and st.session_state.selected_region_fl and not st.session_state.selected_branch_fl:
        df_fl_scope = df_fl_scope[
            df_fl_scope["region_name"] == st.session_state.selected_region_fl
        ]

    summary_fl = df_fl_scope.copy()

    summary_fl["Status"] = summary_fl["Eligible"].apply(
        lambda e: "Eligible" if e else "Belum Capai Target"
    )

    summary_fl["% Capaian"] = summary_fl.apply(
        lambda r: f"{round(r['Biometrik'] / r['fl_target'] * 100, 2)}%" if r["fl_target"] > 0 else "0%",
        axis=1
    )

    summary_fl = summary_fl.rename(columns={
        "organization_id": "Organization ID",
        "fl_id": "Frontliner",
        "brand": "Nama",
        "sub_area_name": "Sub Area",
        "branch": "Branch",
        "micro_cluster_name": "Micro Cluster",
        "fl_target": "Target",
        "Biometrik": "Biometrik",
    })[[
        "Organization ID", "Frontliner", "Nama",
        "Sub Area", "Branch", "Micro Cluster",
        "Target", "Biometrik", "Status", "% Capaian"
    ]]

    with st.container(border=True):

        download_button_df(
            summary_fl,
            ":material/download: Download Frontliner",
            "rekap_frontliner.xlsx",
            "download_frontliner"
        )

        show_grid(
            summary_fl,
            selectable=False,
            key="frontliner_leaf",
            col_align={"Nama": "left"},
            total_outlet=summary_fl["Frontliner"].nunique()
        )