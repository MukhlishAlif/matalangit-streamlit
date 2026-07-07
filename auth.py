
import streamlit as st
from database import login

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

    _, logo_col, _ = st.columns([1, 1.35, 1])

    with logo_col:

        st.image(
            "logo.png",
            width=600
        )

    st.markdown(
        """
        <style>

            div[data-testid="stImage"]{
                margin-bottom:-130px;
            }

        </style>
        """,
        unsafe_allow_html=True
    )

    # =====================================
    # TITLE
    # =====================================

    st.markdown(
        """
        <h2 style="
            text-align:center;
            margin-top:0px;
            margin-bottom:2px;
        ">
            🔐 Login
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
            f"👤 {st.session_state.outlet_user}"
        )

        st.caption(
            f"Role : {st.session_state.outlet_role}"
        )

        st.divider()

        # =====================================
        # LOGOUT
        # =====================================

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.clear()

            st.rerun()
