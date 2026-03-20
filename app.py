import streamlit as st


st.set_page_config(
    page_title="Job Hunt Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)


if not st.session_state.get("logged_in"):
    st.switch_page("pages/landing.py")
elif not st.session_state.get("setup_complete"):
    st.switch_page("pages/0_Setup.py")
else:
    st.switch_page("pages/1_Home.py")
