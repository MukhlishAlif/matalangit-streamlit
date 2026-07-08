import streamlit as st

from streamlit_cookies_controller import CookieController

from database import (

    login,
    buat_session,
    cek_session,
    hapus_session

)
# =====================================
# COOKIE
# =====================================

cookies = CookieController()

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
    # RESTORE SESSION
    # =====================================

    if not st.session_state.outlet_login:

        session_id = cookies.get(
            "session_id"
        )

        if session_id:

            session = cek_session(
                session_id
            )

            if session:

                st.session_state.outlet_login = True
                st.session_state.outlet_user = session["username"]
                st.session_state.outlet_role = session["role"]
                st.session_state.outlet_atasan = session["atasan"]

                st.rerun()
    session_id = cookies.get("session_id")
    st.write("COOKIE:", session_id)

    session = cek_session(session_id)

    st.write("SESSION DB:", dict(session) if session else None)

    # =====================================
    # SUDAH LOGIN
    # =====================================

    if st.session_state.outlet_login:
        return
    st.write("SESSION BARU:", session_id)

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

                session_id = buat_session(

                    hasil["user"],
                    hasil["role"],
                    hasil["atasan"]

                )

                cookies.set(
                    "session_id",
                    session_id,
                    max_age=60 * 60 * 8   # 8 jam
                )

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

            session_id = cookies.get(
                "session_id"
            )

            if session_id:

                hapus_session(
                    session_id
                )

            cookies.remove("session_id")

            st.session_state.clear()

            st.rerun()
