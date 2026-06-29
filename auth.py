import streamlit as st
from database import login


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

    if st.session_state.outlet_login:
        return

    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):

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

            st.rerun()