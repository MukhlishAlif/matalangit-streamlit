
import streamlit as st
from database import login
from html import escape

def mat_icon(name, size=20, valign=-2):
    return f"""
    <span class="material-icons"
          style="
              font-size:{size}px;
              vertical-align:{valign}px;
              line-height:1;
          ">
        {escape(name)}
    </span>
    """

st.markdown("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
""", unsafe_allow_html=True)


# =====================================
# LOGIN PAGE
# =====================================

def login_page():

    # =====================================
    # SESSION INIT
    # =====================================

    if "outlet_login" not in st.session_state:
        st.session_state.outlet_login = False

    if "outlet_user" not in st.session_state:
        st.session_state.outlet_user = ""

    if "outlet_role" not in st.session_state:
        st.session_state.outlet_role = ""

    if "outlet_atasan" not in st.session_state:
        st.session_state.outlet_atasan = ""

    # =====================================
    # SUDAH LOGIN
    # =====================================

    if st.session_state.outlet_login:
        return

    # =====================================
    # CSS
    # =====================================

    st.markdown(
        """
        <style>

            .block-container {
                padding-top: 0.2rem;
            }

        </style>
        """,
        unsafe_allow_html=True
    )

    # =====================================
    # LOGO
    # =====================================

    _, logo_col, _ = st.columns([1, 0.8, 1])

    with logo_col:

        st.image(
            "icon.png",
            width=600
        )

    st.markdown(
        """
        <style>

            div[data-testid="stImage"]{
                margin-bottom:-20px;
            }

        </style>
        """,
        unsafe_allow_html=True
    )

    # =====================================
    # TITLE
    # =====================================

    st.markdown(
        f"""
        <h2 style="
            text-align:center;
        ">
         Login
        </h2>
        """,
        unsafe_allow_html=True
    )
    # =====================================
    # FORM LOGIN
    # =====================================

    left, center, right = st.columns([1.3, 1, 1.3])

    with center:

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            hasil = login(
                username.strip(),
                password.strip()
            )

            if hasil:

                st.session_state.outlet_login = True
                st.session_state.outlet_user = hasil["user"]
                st.session_state.outlet_role = hasil["role"]
                st.session_state.outlet_atasan = hasil["atasan"]
                st.session_state.outlet_token = hasil["token"] 

                st.rerun()

            else:

                st.error(
                    "Username atau Password salah."
                )

    st.stop()

# =====================================
# SIDEBAR
# =====================================

def sidebar():

    with st.sidebar:

        st.success(
            f":material/account_circle: **{st.session_state.outlet_user}**"
        )

        col_role, col_bell = st.columns(
            [4, 1], gap="small", vertical_alignment="center"
        )

        with col_role:
            st.caption(
                f":material/badge: {st.session_state.outlet_role}"
            )

        with col_bell:
            if st.button(
                "",
                icon=":material/notifications_active:",
                key="btn_bell_summary",
                help="Lihat ringkasan tim yang belum submit"
            ):
                st.session_state["force_show_summary_popup"] = True
                st.rerun()

        st.divider()
        # =====================================
        # LOGOUT
        # =====================================

        if st.button(
            "Logout",
            icon=":material/logout:",
            use_container_width=True
        ):

            st.session_state.clear()

            st.rerun()