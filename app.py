import streamlit as st


st.set_page_config(
    page_title="Job Hunt Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)


if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False


if not st.session_state.setup_complete:
    st.switch_page("pages/0_Setup.py")
else:
    st.switch_page("pages/1_Home.py")

