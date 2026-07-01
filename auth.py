import streamlit as st
from database import login
from streamlit_cookies_manager import EncryptedCookieManager

# =====================================
# COOKIE MANAGER
# =====================================

cookies = EncryptedCookieManager(
    prefix="matalangit/",
    password="MATALANGIT_SECRET_2026"
)

if not cookies.ready():
    st.stop()


# =====================================
# LOGIN
# =====================================

def login_page():

    if "outlet_login" not in st.session_state:
        st.session_state.outlet_login = False

    if "outlet_user" not in st.session_state:
        st.session_state.outlet_user = ""

    if "outlet_role" not in st.session_state:
        st.session_state.outlet_role = ""

    if "outlet_atasan" not in st.session_state:
        st.session_state.outlet_atasan = ""

    # =====================================
    # AUTO LOGIN DARI COOKIE
    # =====================================

    if (
        not st.session_state.outlet_login
        and cookies.get("outlet_login") == "true"
    ):

        st.session_state.outlet_login = True
        st.session_state.outlet_user = cookies.get("outlet_user", "")
        st.session_state.outlet_role = cookies.get("outlet_role", "")
        st.session_state.outlet_atasan = cookies.get("outlet_atasan", "")

    if st.session_state.outlet_login:
        return

    # =====================================
    # KURANGI PADDING ATAS
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
    # JUDUL
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

                # =====================================
                # SIMPAN COOKIE
                # =====================================

                cookies["outlet_login"] = "true"
                cookies["outlet_user"] = hasil["user"]
                cookies["outlet_role"] = hasil["role"]
                cookies["outlet_atasan"] = hasil["atasan"]
                cookies.save()

                st.rerun()

            else:

                st.error("Username atau Password salah.")

    st.stop()


# =====================================
# SIDEBAR
# =====================================

def sidebar():

    with st.sidebar:

        st.success(f"👤 {st.session_state.outlet_user}")

        st.caption(
            f"Role : {st.session_state.outlet_role}"
        )

        st.divider()

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):

            st.session_state.outlet_login = False
            st.session_state.outlet_user = ""
            st.session_state.outlet_role = ""
            st.session_state.outlet_atasan = ""

            # =====================================
            # HAPUS COOKIE
            # =====================================

            cookies["outlet_login"] = ""
            cookies["outlet_user"] = ""
            cookies["outlet_role"] = ""
            cookies["outlet_atasan"] = ""
            cookies.save()

            st.rerun()